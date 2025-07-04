const functions = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({ origin: true });
const axios = require('axios');
const multer = require('multer');
const fs = require('fs');
const os = require('os');
const path = require('path');
require('dotenv').config();

// Initialize Firebase Admin
admin.initializeApp();

// Python Microservice URL
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

// Setup multer for file uploads
const upload = multer({ 
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      const uploadPath = path.join(os.tmpdir(), 'uploads');
      fs.mkdirSync(uploadPath, { recursive: true });
      cb(null, uploadPath);
    },
    filename: (req, file, cb) => {
      cb(null, `${Date.now()}-${file.originalname}`);
    }
  }),
  limits: { fileSize: 10 * 1024 * 1024 } // 10 MB limit
});

// Use Firestore for basic patient metadata backup
const db = admin.firestore();

// Python Microservice API calls
const pythonService = {
  // Call Python service for complete processing (LangGraph workflow)
  async processComplete(text, patientId, language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/process`, {
        text,
        patient_id: patientId,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python complete processing service:', error.message);
      throw error;
    }
  },

  // Call Python service for audio processing
  async processAudio(audioUrl, patientId, language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/process-audio`, {
        audio_url: audioUrl,
        patient_id: patientId,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python audio processing service:', error.message);
      throw error;
    }
  },

  // Call Python service for diagnosis
  async getDiagnosis(symptoms, patientId, model = 'gpt-4', language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/diagnose`, {
        symptoms,
        patient_id: patientId,
        model,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python diagnosis service:', error.message);
      throw error;
    }
  },

  // Call Python service for extraction
  async extractMedicalInfo(text, patientId, language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/extract`, {
        text,
        patient_id: patientId,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python extraction service:', error.message);
      throw error;
    }
  },

  // Call Python service for transcription
  async transcribeAudio(audioUrl, patientId, language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/transcribe`, {
        audio_url: audioUrl,
        patient_id: patientId,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python transcription service:', error.message);
      throw error;
    }
  },

  // Call Python service for memory operations
  async saveToMemory(patientId, content, contentType = 'symptom') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/memory/save`, {
        patient_id: patientId,
        content,
        content_type: contentType
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python memory save service:', error.message);
      throw error;
    }
  },

  async queryMemory(patientId, query, limit = 5) {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/memory/query`, {
        patient_id: patientId,
        query,
        limit
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python memory query service:', error.message);
      throw error;
    }
  },

  // Call Python service for MLops
  async logToMLflow(data) {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/mlops/log`, data);
      return response.data;
    } catch (error) {
      console.error('Error calling Python MLflow service:', error.message);
      throw error;
    }
  },

  async checkDrift(data) {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/mlops/drift`, data);
      return response.data;
    } catch (error) {
      console.error('Error calling Python drift detection service:', error.message);
      throw error;
    }
  }
};

// Main processing function - delegates to Python microservice
const processMessage = async (text, patientId = null) => {
  try {
    // Delegate all processing to Python microservice with LangGraph workflow
    const result = await pythonService.processComplete(text, patientId, 'es');
    return result;
  } catch (error) {
    console.error('Error in processMessage:', error);
    return {
      response: 'Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.',
      success: false,
      error: error.message
    };
  }
};

// Cloud Functions

// Main processing endpoint - delegates to Python microservice
exports.process = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { text, patient_id } = req.body;
      
      if (!text) {
        return res.status(400).json({ error: 'Se requiere texto para procesar' });
      }

      const result = await processMessage(text, patient_id);
      res.json(result);
    } catch (error) {
      console.error('Error in /process:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

// Audio processing endpoint - delegates to Python microservice
exports.processAudio = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { audio_url, patient_id } = req.body;
      
      if (!audio_url) {
        return res.status(400).json({ error: 'Se requiere URL de audio para procesar' });
      }

      const result = await pythonService.processAudio(audio_url, patient_id, 'es');
      res.json(result);
    } catch (error) {
      console.error('Error in /processAudio:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

// File upload endpoint
exports.uploadAudio = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    upload.single('audio')(req, res, async (err) => {
      if (err) {
        return res.status(400).json({ error: 'Error al subir archivo' });
      }

      if (!req.file) {
        return res.status(400).json({ error: 'No se proporcionó archivo de audio' });
      }

      try {
        // For now, just return file info
        // In production, you'd upload to cloud storage and get a URL
        res.json({
          message: 'Archivo subido exitosamente',
          filename: req.file.filename,
          size: req.file.size,
          mimetype: req.file.mimetype
        });
      } catch (error) {
        console.error('Error in /uploadAudio:', error);
        res.status(500).json({ 
          error: 'Error interno del servidor',
          details: error.message 
        });
      }
    });
  });
});

// Health check endpoint
exports.health = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    try {
      // Check Python microservice health
      const pythonHealth = await axios.get(`${PYTHON_SERVICE_URL}/health`);
      
      res.json({
        status: 'healthy',
        firebase_functions: 'running',
        python_microservice: pythonHealth.data.status,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Health check failed:', error);
      res.status(500).json({
        status: 'unhealthy',
        firebase_functions: 'running',
        python_microservice: 'unreachable',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });
});

// Individual service endpoints - direct proxies to Python microservice

exports.diagnose = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { symptoms, patient_id, model, language } = req.body;
      
      if (!symptoms) {
        return res.status(400).json({ error: 'Se requieren síntomas para diagnosticar' });
      }

      const result = await pythonService.getDiagnosis(symptoms, patient_id, model, language);
      res.json(result);
    } catch (error) {
      console.error('Error in /diagnose:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

exports.extract = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { text, patient_id, language } = req.body;
      
      if (!text) {
        return res.status(400).json({ error: 'Se requiere texto para extraer información' });
      }

      const result = await pythonService.extractMedicalInfo(text, patient_id, language);
      res.json(result);
    } catch (error) {
      console.error('Error in /extract:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

exports.transcribe = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { audio_url, patient_id, language } = req.body;
      
      if (!audio_url) {
        return res.status(400).json({ error: 'Se requiere URL de audio para transcribir' });
      }

      const result = await pythonService.transcribeAudio(audio_url, patient_id, language);
      res.json(result);
    } catch (error) {
      console.error('Error in /transcribe:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

// Memory endpoints
exports.saveMemory = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { patient_id, content, content_type } = req.body;
      
      if (!patient_id || !content) {
        return res.status(400).json({ error: 'Se requiere patient_id y content' });
      }

      const result = await pythonService.saveToMemory(patient_id, content, content_type);
      res.json(result);
    } catch (error) {
      console.error('Error in /saveMemory:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

exports.queryMemory = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { patient_id, query, limit } = req.body;
      
      if (!patient_id || !query) {
        return res.status(400).json({ error: 'Se requiere patient_id y query' });
      }

      const result = await pythonService.queryMemory(patient_id, query, limit);
      res.json(result);
    } catch (error) {
      console.error('Error in /queryMemory:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

// MLops endpoints
exports.logMLflow = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const result = await pythonService.logToMLflow(req.body);
      res.json(result);
    } catch (error) {
      console.error('Error in /logMLflow:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

exports.checkDrift = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const result = await pythonService.checkDrift(req.body);
      res.json(result);
    } catch (error) {
      console.error('Error in /checkDrift:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});
