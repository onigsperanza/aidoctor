const functions = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({ origin: true });
const OpenAI = require('openai');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { ChatOpenAI } = require('langchain/chat_models/openai');
const { ChatGoogleGenerativeAI } = require('@langchain/google-genai');
const { HumanMessage, SystemMessage } = require('langchain/schema');
const { StateGraph, END } = require('langgraph/graphs');
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

// Initialize AI clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// Initialize LangChain models
const openaiModel = new ChatOpenAI({
  openAIApiKey: process.env.OPENAI_API_KEY,
  modelName: 'gpt-4',
  temperature: 0.7,
});

const geminiModel = new ChatGoogleGenerativeAI({
  model: 'gemini-pro',
  maxOutputTokens: 2048,
  temperature: 0.7,
});

// Use Firestore for basic patient metadata backup
const db = admin.firestore();

// Prompt versions
const PROMPT_VERSIONS = {
  EXTRACT: 'extract_v2',
  DIAGNOSIS: 'diagnosis_v3'
};

// Python Microservice API calls
const pythonService = {
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
  },

  // Call Python service for complete audio processing
  async processAudioComplete(audioUrl, patientId, language = 'es') {
    try {
      const response = await axios.post(`${PYTHON_SERVICE_URL}/process-audio`, {
        audio_url: audioUrl,
        patient_id: patientId,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Error calling Python complete audio processing service:', error.message);
      throw error;
    }
  }
};

// Schema validation functions
const validateExtractionSchema = (data) => {
  const errors = [];
  
  // Check patient_info
  if (!data.patient_info) {
    errors.push('Missing patient_info');
  } else {
    if (typeof data.patient_info.name !== 'string') errors.push('patient_info.name must be string');
    if (typeof data.patient_info.age !== 'number') errors.push('patient_info.age must be number');
    if (data.patient_info.id !== null && typeof data.patient_info.id !== 'string') {
      errors.push('patient_info.id must be string or null');
    }
  }
  
  // Check symptoms
  if (!Array.isArray(data.symptoms)) {
    errors.push('symptoms must be array');
  } else {
    data.symptoms.forEach((symptom, index) => {
      if (typeof symptom !== 'string') {
        errors.push(`symptoms[${index}] must be string`);
      }
    });
  }
  
  // Check medications
  if (!Array.isArray(data.medications)) {
    errors.push('medications must be array');
  } else {
    data.medications.forEach((medication, index) => {
      if (typeof medication !== 'string') {
        errors.push(`medications[${index}] must be string`);
      }
    });
  }
  
  // Check allergies
  if (!Array.isArray(data.allergies)) {
    errors.push('allergies must be array');
  } else {
    data.allergies.forEach((allergy, index) => {
      if (typeof allergy !== 'string') {
        errors.push(`allergies[${index}] must be string`);
      }
    });
  }
  
  // Check motive
  if (typeof data.motive !== 'string') errors.push('motive must be string');
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

const validateDiagnosisSchema = (data) => {
  const errors = [];
  
  if (typeof data.diagnosis !== 'string') errors.push('diagnosis must be string');
  if (typeof data.treatment !== 'string') errors.push('treatment must be string');
  if (typeof data.recommendations !== 'string') errors.push('recommendations must be string');
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Drift detection (simplified for Node.js)
const detectDrift = (extractionResult, previousResults = []) => {
  const flags = [];
  
  // Simple drift detection based on symptom patterns
  if (previousResults.length > 0) {
    const currentSymptoms = extractionResult.symptoms || [];
    const previousSymptoms = previousResults.flatMap(r => r.symptoms || []);
    
    // Check for unusual symptom combinations
    const symptomFrequency = {};
    previousSymptoms.forEach(symptom => {
      symptomFrequency[symptom] = (symptomFrequency[symptom] || 0) + 1;
    });
    
    currentSymptoms.forEach(symptom => {
      if (!symptomFrequency[symptom]) {
        flags.push(`Unusual symptom detected: ${symptom}`);
      }
    });
  }
  
  return { flags };
};

// Load prompts
const loadPrompt = (version, type) => {
  try {
    if (type === 'extract') {
      const promptPath = path.join(__dirname, '..', 'prompts', 'extract_v2.json');
      const promptData = JSON.parse(fs.readFileSync(promptPath, 'utf8'));
      return promptData.prompt;
    } else if (type === 'diagnosis') {
      const promptPath = path.join(__dirname, '..', 'prompts', 'diagnosis_v3.txt');
      return fs.readFileSync(promptPath, 'utf8');
    }
  } catch (error) {
    console.error(`Error loading prompt ${version}:`, error);
    return null;
  }
};

// State for LangGraph
const createState = () => ({
  messages: [],
  extracted_data: {},
  diagnosis: {},
  patient_id: null,
  cognee_context: '',
  transcription: '',
  drift_flags: [],
  ner_results: {}
});

// LangGraph workflow (simplified to use Python microservice)
const createWorkflow = () => {
  const workflow = new StateGraph({
    channels: createState()
  });

  // Extract medical data using Python microservice
  workflow.addNode('extract', async (state) => {
    const lastMessage = state.messages[state.messages.length - 1];
    
    try {
      const extractionResult = await pythonService.extractMedicalInfo(
        lastMessage.content,
        state.patient_id,
        'es'
      );
      
      return { extracted_data: extractionResult.extraction };
    } catch (error) {
      console.error('Error in extraction:', error);
      return { extracted_data: { error: 'No se pudo extraer datos estructurados' } };
    }
  });

  // Get patient context using Python microservice
  workflow.addNode('get_context', async (state) => {
    if (!state.patient_id) {
      return { cognee_context: '' };
    }
    
    try {
      const currentSymptoms = state.extracted_data?.symptoms?.join(' ') || '';
      const memoryResults = await pythonService.queryMemory(state.patient_id, currentSymptoms, 5);
      
      const context = memoryResults.results?.map(result => 
        `Consulta anterior: ${result.content}`
      ).join('\n') || '';
      
      return { cognee_context: context };
    } catch (error) {
      console.error('Error getting patient context:', error);
      return { cognee_context: '' };
    }
  });

  // Generate diagnosis using Python microservice
  workflow.addNode('diagnose', async (state) => {
    const lastMessage = state.messages[state.messages.length - 1];
    const symptoms = lastMessage.content;
    
    try {
      const diagnosisResult = await pythonService.getDiagnosis(
        symptoms,
        state.patient_id,
        'gpt-4',
        'es'
      );
      
      return { diagnosis: diagnosisResult.diagnosis };
    } catch (error) {
      console.error('Error in diagnosis:', error);
      return { diagnosis: { error: 'No se pudo generar diagnóstico estructurado' } };
    }
  });

  // Detect drift using Python microservice
  workflow.addNode('detect_drift', async (state) => {
    try {
      const driftResult = await pythonService.checkDrift({
        current_data: state.extracted_data,
        reference_data: [],
        threshold: 0.05
      });
      
      return { drift_flags: driftResult.drift_detected ? ['Data drift detected'] : [] };
    } catch (error) {
      console.error('Error in drift detection:', error);
      return { drift_flags: [] };
    }
  });

  // Save to memory using Python microservice
  workflow.addNode('save_to_memory', async (state) => {
    if (!state.patient_id) {
      return {};
    }
    
    try {
      const lastMessage = state.messages[state.messages.length - 1];
      await pythonService.saveToMemory(
        state.patient_id,
        lastMessage.content,
        'consultation'
      );
    } catch (error) {
      console.error('Error saving to memory:', error);
    }
    
    return {};
  });

  // Define workflow edges
  workflow.setEntryPoint('extract');
  workflow.addEdge('extract', 'get_context');
  workflow.addEdge('get_context', 'diagnose');
  workflow.addEdge('diagnose', 'detect_drift');
  workflow.addEdge('detect_drift', 'save_to_memory');
  workflow.addEdge('save_to_memory', END);

  return workflow.compile();
};

// Main processing function
const processMessage = async (text, patientId = null) => {
  const startTime = Date.now();
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  try {
    const workflow = createWorkflow();
    
    const initialState = createState();
    initialState.messages = [{ role: 'user', content: text }];
    initialState.patient_id = patientId;
    
    const result = await workflow.invoke(initialState);
    
    const latencyMs = Date.now() - startTime;
    
    // Log to MLflow using Python microservice
    await pythonService.logToMLflow({
      metric_name: 'request_latency',
      value: latencyMs,
      step: Date.now(),
      tags: {
        request_id: requestId,
        patient_id: patientId,
        input_type: 'text'
      }
    });
    
    return {
      patient_info: result.extracted_data?.patient_info || {},
      symptoms: result.extracted_data?.symptoms || [],
      motive: result.extracted_data?.motive || '',
      diagnosis: result.diagnosis?.diagnosis || '',
      treatment: result.diagnosis?.treatment || '',
      recommendations: result.diagnosis?.recommendations || [],
      metadata: {
        request_id: requestId,
        model_version: 'gpt-4',
        prompt_version: `${PROMPT_VERSIONS.EXTRACT},${PROMPT_VERSIONS.DIAGNOSIS}`,
        latency_ms: latencyMs,
        timestamp: new Date().toISOString(),
        input_type: 'text',
        drift_detected: result.drift_flags.length > 0,
        drift_flags: result.drift_flags
      },
      success: true
    };
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

// Main processing endpoint
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

// Health check endpoint
exports.health = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    res.json({ 
      status: 'OK', 
      service: 'AI Doctor Assistant - Firebase Functions',
      python_service_url: PYTHON_SERVICE_URL,
      language: 'Spanish',
      features: [
        'speech_recognition', 
        'emr_extraction', 
        'memory_management', 
        'mlops_observability', 
        'drift_detection', 
        'schema_validation',
        'personalized_reasoning'
      ],
      prompt_versions: PROMPT_VERSIONS,
      timestamp: new Date().toISOString()
    });
  });
});

// Transcribe audio using Python microservice
exports.transcribe = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    upload.single('audio')(req, res, async (err) => {
      if (err) {
        return res.status(400).json({ error: 'Error al subir el archivo.', details: err.message });
      }

      if (!req.file) {
        return res.status(400).json({ error: 'No se encontró ningún archivo de audio.' });
      }

      try {
        // For now, we'll use OpenAI directly for transcription
        // In the future, this can be moved to Python microservice
        const transcription = await openai.audio.transcriptions.create({
          file: fs.createReadStream(req.file.path),
          model: 'whisper-1',
          language: 'es'
        });

        // Clean up the uploaded file
        fs.unlinkSync(req.file.path);

        res.json({ transcription: transcription.text });
      } catch (error) {
        console.error('Error in /transcribe:', error);
        // Clean up the uploaded file in case of an error
        if (req.file && fs.existsSync(req.file.path)) {
          fs.unlinkSync(req.file.path);
        }
        res.status(500).json({ 
          error: 'Error al transcribir el audio.', 
          details: error.message 
        });
      }
    });
  });
});

// Process audio completely using Python microservice
exports.processAudio = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { audio_url, patient_id, language = 'es' } = req.body;

      if (!audio_url) {
        return res.status(400).json({ error: 'Se requiere audio_url' });
      }

      const result = await pythonService.processAudioComplete(audio_url, patient_id, language);
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

// Memory operations using Python microservice
exports.saveMemory = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { patient_id, content, content_type = 'symptom' } = req.body;

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
      const { patient_id, query, limit = 5 } = req.body;

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

module.exports = {
  processMessage,
  createWorkflow,
  pythonService
}; 