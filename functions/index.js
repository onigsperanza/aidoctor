const functions = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({ origin: true });
const OpenAI = require('openai');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { ChatOpenAI } = require('langchain/chat_models/openai');
const { ChatGoogleGenerativeAI } = require('@langchain/google-genai');
const { HumanMessage, SystemMessage } = require('langchain/schema');
const { StateGraph, END } = require('langgraph/graphs');
const { Cognee } = require('cognee');
const mlflow = require('mlflow');
const axios = require('axios');
const multer = require('multer');
const fs = require('fs');
const os = require('os');
const path = require('path');
require('dotenv').config();

// Initialize Firebase Admin
admin.initializeApp();

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

// Initialize Cognee for patient knowledge graphs
const cognee = new Cognee();

// Initialize MLflow
mlflow.setTrackingUri(process.env.MLFLOW_TRACKING_URI || 'http://localhost:5000');
const experimentName = 'ai-doctor-assistant';

// Ensure experiment exists
try {
  mlflow.getExperimentByName(experimentName);
} catch (error) {
  mlflow.createExperiment(experimentName);
}
mlflow.setExperiment(experimentName);

// Use Firestore for basic patient metadata backup
const db = admin.firestore();

// Prompt versions
const PROMPT_VERSIONS = {
  EXTRACT: 'extract_v2',
  DIAGNOSIS: 'diagnosis_v3'
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
        errors.push(`symptom[${index}] must be string`);
      }
    });
  }
  
  // Check motive
  if (typeof data.motive !== 'string') {
    errors.push('motive must be string');
  }
  
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

// Drift detection
const detectDrift = (extractionResult, previousResults = []) => {
  const driftFlags = [];
  
  // Schema field check
  const schemaValidation = validateExtractionSchema(extractionResult);
  if (!schemaValidation.isValid) {
    driftFlags.push(`Schema validation failed: ${schemaValidation.errors.join(', ')}`);
  }
  
  // Symptom count variance
  const currentSymptomCount = extractionResult.symptoms?.length || 0;
  if (previousResults.length > 0) {
    const avgSymptomCount = previousResults.reduce((sum, result) => 
      sum + (result.symptoms?.length || 0), 0) / previousResults.length;
    const variance = Math.abs(currentSymptomCount - avgSymptomCount);
    if (variance > 3) { // Threshold of 3 symptoms
      driftFlags.push(`Symptom count variance detected: current=${currentSymptomCount}, avg=${avgSymptomCount.toFixed(1)}`);
    }
  }
  
  return {
    hasDrift: driftFlags.length > 0,
    flags: driftFlags
  };
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
  drift_flags: []
});

// Initialize patient knowledge graph in Cognee
const initializePatientGraph = async (patientId) => {
  try {
    // Create a unique graph ID for this patient
    const graphId = `patient-${patientId}`;
    
    // Check if graph already exists
    const existingGraph = await cognee.getGraph(graphId);
    if (!existingGraph) {
      // Initialize new patient knowledge graph
      await cognee.createGraph({
        id: graphId,
        name: `Patient ${patientId} Medical History`,
        description: `Knowledge graph for patient ${patientId} containing medical history, symptoms, diagnoses, and treatments`
      });
    }
    
    return graphId;
  } catch (error) {
    console.error('Error initializing patient graph:', error);
    return null;
  }
};

// Add medical data to patient's knowledge graph
const addToPatientGraph = async (patientId, data) => {
  try {
    const graphId = `patient-${patientId}`;
    
    // Create structured medical nodes
    const medicalData = {
      timestamp: new Date().toISOString(),
      symptoms: data.extracted_data?.symptoms || [],
      medications: data.extracted_data?.medications || [],
      allergies: data.extracted_data?.allergies || [],
      diagnosis: data.diagnosis?.diagnosis || '',
      treatment: data.diagnosis?.treatment || '',
      recommendations: data.diagnosis?.recommendations || '',
      raw_text: data.messages?.[data.messages.length - 1]?.content || ''
    };
    
    // Add to Cognee knowledge graph
    await cognee.addNode(graphId, {
      id: `consultation-${Date.now()}`,
      type: 'medical_consultation',
      data: medicalData,
      metadata: {
        patient_id: patientId,
        consultation_date: new Date().toISOString()
      }
    });
    
    // Also store in Firestore for backup
    await db.collection('patients').doc(patientId).collection('history').add(medicalData);
    
  } catch (error) {
    console.error('Error adding to patient graph:', error);
  }
};

// Retrieve relevant patient context using Cognee RAG
const getPatientContext = async (patientId, currentSymptoms) => {
  try {
    const graphId = `patient-${patientId}`;
    
    // Search the patient's knowledge graph for relevant medical history
    const searchResults = await cognee.search(graphId, {
      query: currentSymptoms,
      limit: 5,
      include_metadata: true
    });
    
    if (searchResults && searchResults.length > 0) {
      // Format the relevant context
      const context = searchResults.map(result => {
        const data = result.data;
        return `Consulta anterior (${data.timestamp}): Síntomas: ${data.symptoms.join(', ')}, Diagnóstico: ${data.diagnosis}`;
      }).join('\n');
      
      return context;
    }
    
    return '';
  } catch (error) {
    console.error('Error retrieving patient context:', error);
    return '';
  }
};

// MLflow logging function with drift detection
const logToMLflow = async (requestId, inputType, model, promptVersion, latencyMs, extractionResult, diagnosisResult, driftFlags = []) => {
  try {
    await mlflow.startRun();
    
    // Log parameters
    mlflow.logParam('request_id', requestId);
    mlflow.logParam('input_type', inputType);
    mlflow.logParam('model', model);
    mlflow.logParam('prompt_version', promptVersion);
    
    // Log metrics
    mlflow.logMetric('latency_ms', latencyMs);
    mlflow.logMetric('symptoms_count', extractionResult?.symptoms?.length || 0);
    mlflow.logMetric('extraction_success', extractionResult ? 1 : 0);
    mlflow.logMetric('diagnosis_success', diagnosisResult ? 1 : 0);
    mlflow.logMetric('drift_detected', driftFlags.length > 0 ? 1 : 0);
    
    // Log artifacts
    mlflow.logArtifact(JSON.stringify(extractionResult, null, 2), 'extraction_result.json');
    mlflow.logArtifact(JSON.stringify(diagnosisResult, null, 2), 'diagnosis_result.json');
    
    if (driftFlags.length > 0) {
      mlflow.logArtifact(JSON.stringify({ drift_flags: driftFlags }, null, 2), 'drift_flags.json');
    }
    
    await mlflow.endRun();
  } catch (error) {
    console.error('Error logging to MLflow:', error);
  }
};

// LangGraph workflow
const createWorkflow = () => {
  const workflow = new StateGraph({
    channels: createState()
  });

  // Extract medical data with schema validation
  workflow.addNode('extract', async (state) => {
    const lastMessage = state.messages[state.messages.length - 1];
    
    // Load the extraction prompt
    const extractionPrompt = loadPrompt(PROMPT_VERSIONS.EXTRACT, 'extract');
    if (!extractionPrompt) {
      throw new Error('Failed to load extraction prompt');
    }
    
    const formattedPrompt = extractionPrompt.replace('{text}', lastMessage.content);
    
    const response = await geminiModel.invoke([
      new SystemMessage(formattedPrompt)
    ]);
    
    try {
      // Clean the response to ensure it's valid JSON
      const cleanedResponse = response.content.replace(/```json/g, '').replace(/```/g, '').trim();
      const extractedData = JSON.parse(cleanedResponse);
      
      // Validate schema
      const validation = validateExtractionSchema(extractedData);
      if (!validation.isValid) {
        throw new Error(`Schema validation failed: ${validation.errors.join(', ')}`);
      }
      
      return { extracted_data: extractedData };
    } catch (error) {
      console.error('Error parsing extraction response:', error);
      return { extracted_data: { error: 'No se pudo extraer datos estructurados' } };
    }
  });

  // Get patient context using Cognee RAG
  workflow.addNode('get_context', async (state) => {
    if (!state.patient_id) {
      return { cognee_context: '' };
    }
    
    try {
      // Initialize patient graph if needed
      await initializePatientGraph(state.patient_id);
      
      // Get relevant context based on current symptoms
      const currentSymptoms = state.extracted_data?.symptoms?.join(' ') || '';
      const context = await getPatientContext(state.patient_id, currentSymptoms);
      
      return { cognee_context: context };
    } catch (error) {
      console.error('Error getting Cognee context:', error);
      return { cognee_context: '' };
    }
  });

  // Generate structured diagnosis
  workflow.addNode('diagnose', async (state) => {
    const lastMessage = state.messages[state.messages.length - 1];
    const context = state.cognee_context ? `\n\nHistorial relevante del paciente:\n${state.cognee_context}` : '';
    
    // Load the diagnosis prompt
    const diagnosisPrompt = loadPrompt(PROMPT_VERSIONS.DIAGNOSIS, 'diagnosis');
    if (!diagnosisPrompt) {
      throw new Error('Failed to load diagnosis prompt');
    }
    
    const formattedPrompt = diagnosisPrompt.replace('{context}', 
      `Información extraída: ${JSON.stringify(state.extracted_data, null, 2)}${context}\n\nMensaje del paciente: "${lastMessage.content}"`);
    
    const response = await openaiModel.invoke([
      new SystemMessage(formattedPrompt)
    ]);
    
    try {
      // Clean the response to ensure it's valid JSON
      const cleanedResponse = response.content.replace(/```json/g, '').replace(/```/g, '').trim();
      const diagnosisData = JSON.parse(cleanedResponse);
      
      // Validate diagnosis schema
      const validation = validateDiagnosisSchema(diagnosisData);
      if (!validation.isValid) {
        throw new Error(`Diagnosis schema validation failed: ${validation.errors.join(', ')}`);
      }
      
      return { diagnosis: diagnosisData };
    } catch (error) {
      console.error('Error parsing diagnosis response:', error);
      return { diagnosis: { error: 'No se pudo generar diagnóstico estructurado' } };
    }
  });

  // Detect drift
  workflow.addNode('detect_drift', async (state) => {
    try {
      // Get recent results for drift detection
      const recentResults = await db.collection('patients')
        .doc(state.patient_id || 'anonymous')
        .collection('history')
        .orderBy('timestamp', 'desc')
        .limit(10)
        .get();
      
      const previousResults = recentResults.docs.map(doc => doc.data());
      
      // Detect drift
      const driftResult = detectDrift(state.extracted_data, previousResults);
      
      return { drift_flags: driftResult.flags };
    } catch (error) {
      console.error('Error in drift detection:', error);
      return { drift_flags: [] };
    }
  });

  // Save to Cognee knowledge graph
  workflow.addNode('save_to_graph', async (state) => {
    if (!state.patient_id) {
      return {};
    }
    
    try {
      await addToPatientGraph(state.patient_id, {
        extracted_data: state.extracted_data,
        diagnosis: state.diagnosis,
        messages: state.messages
      });
    } catch (error) {
      console.error('Error saving to Cognee graph:', error);
    }
    
    return {};
  });

  // Define workflow edges
  workflow.setEntryPoint('extract');
  workflow.addEdge('extract', 'get_context');
  workflow.addEdge('get_context', 'diagnose');
  workflow.addEdge('diagnose', 'detect_drift');
  workflow.addEdge('detect_drift', 'save_to_graph');
  workflow.addEdge('save_to_graph', END);

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
    
    // Log to MLflow with drift detection
    await logToMLflow(
      requestId,
      'text',
      'gpt-4',
      `${PROMPT_VERSIONS.EXTRACT},${PROMPT_VERSIONS.DIAGNOSIS}`,
      latencyMs,
      result.extracted_data,
      result.diagnosis,
      result.drift_flags
    );
    
    return {
      patient_info: result.extracted_data?.patient_info || {},
      symptoms: result.extracted_data?.symptoms || [],
      motive: result.extracted_data?.motive || '',
      diagnosis: result.diagnosis?.diagnosis || '',
      treatment: result.diagnosis?.treatment || '',
      recommendations: result.diagnosis?.recommendations || '',
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
      service: 'AI Doctor Assistant with Cognee & MLflow',
      language: 'Spanish',
      features: ['speech_recognition', 'emr_extraction', 'cognee_rag', 'mlflow_observability', 'drift_detection', 'schema_validation', 'personalized_reasoning'],
      prompt_versions: PROMPT_VERSIONS,
      timestamp: new Date().toISOString()
    });
  });
});

// Get patient history from Cognee
exports.getHistory = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { patient_id } = req.query;

      if (!patient_id) {
        return res.status(400).json({ error: 'Se requiere patient_id' });
      }

      // Get from Cognee knowledge graph
      const graphId = `patient-${patient_id}`;
      const nodes = await cognee.getNodes(graphId);
      
      if (!nodes || nodes.length === 0) {
        return res.json([]);
      }

      const history = nodes.map(node => ({
        id: node.id,
        type: node.type,
        data: node.data,
        metadata: node.metadata
      }));
      
      res.json(history);

    } catch (error) {
      console.error('Error in /getHistory:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

// Transcribe audio
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

// Search patient knowledge graph
exports.searchPatient = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
      const { patient_id, query } = req.body;

      if (!patient_id || !query) {
        return res.status(400).json({ error: 'Se requiere patient_id y query' });
      }

      const graphId = `patient-${patient_id}`;
      const searchResults = await cognee.search(graphId, {
        query: query,
        limit: 10,
        include_metadata: true
      });

      res.json({ results: searchResults });

    } catch (error) {
      console.error('Error in /searchPatient:', error);
      res.status(500).json({ 
        error: 'Error interno del servidor',
        details: error.message 
      });
    }
  });
});

module.exports = {
  processMessage,
  createWorkflow
}; 