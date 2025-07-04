# AI Doctor Assistant - Integrated Architecture

## Overview

The AI Doctor Assistant has been restructured to use a **hybrid architecture** where:
- **Firebase Functions (JavaScript)** acts as a lightweight proxy/coordinator
- **Python Microservice** handles all AI/ML operations including LangGraph workflows
- **Frontend (React)** remains unchanged

## Architecture Diagram

```
┌─────────────────┐    HTTP Requests    ┌─────────────────────┐
│   React Frontend │ ──────────────────► │  Firebase Functions │
│   (Port 5173)    │                     │   (Port 5001)       │
└─────────────────┘                     └─────────────────────┘
                                                │
                                                │ HTTP Proxy
                                                ▼
                                       ┌─────────────────────┐
                                       │ Python Microservice │
                                       │   (Port 8000)       │
                                       │                     │
                                       │ ┌─────────────────┐ │
                                       │ │   LangGraph     │ │
                                       │ │   Workflow      │ │
                                       │ └─────────────────┘ │
                                       │                     │
                                       │ ┌─────────────────┐ │
                                       │ │   Services      │ │
                                       │ │ - Diagnosis     │ │
                                       │ │ - Extraction    │ │
                                       │ │ - Whisper       │ │
                                       │ │ - Memory        │ │
                                       │ │ - MLops         │ │
                                       │ └─────────────────┘ │
                                       └─────────────────────┘
```

## Key Changes

### 1. Firebase Functions (JavaScript) - Simplified Proxy

**Removed:**
- ❌ LangChain dependencies
- ❌ LangGraph dependencies  
- ❌ OpenAI direct integration
- ❌ Complex workflow logic

**Added:**
- ✅ Simple HTTP proxy to Python microservice
- ✅ Request/response forwarding
- ✅ Basic error handling
- ✅ Health check coordination

**New Endpoints:**
- `POST /process` - Complete workflow (delegates to Python `/process`)
- `POST /processAudio` - Audio processing (delegates to Python `/process-audio`)
- `POST /diagnose` - Diagnosis (delegates to Python `/diagnose`)
- `POST /extract` - Extraction (delegates to Python `/extract`)
- `POST /transcribe` - Transcription (delegates to Python `/transcribe`)
- `POST /saveMemory` - Memory save (delegates to Python `/memory/save`)
- `POST /queryMemory` - Memory query (delegates to Python `/memory/query`)
- `POST /logMLflow` - MLops logging (delegates to Python `/mlops/log`)
- `POST /checkDrift` - Drift detection (delegates to Python `/mlops/drift`)
- `GET /health` - Health check (checks both services)

### 2. Python Microservice - Enhanced with LangGraph

**Enhanced:**
- ✅ Complete LangGraph workflow orchestration
- ✅ All AI/ML operations centralized
- ✅ Comprehensive state management
- ✅ Memory integration
- ✅ MLops integration

**New Endpoint:**
- `POST /process` - Complete LangGraph workflow

**LangGraph Workflow:**
```
1. Transcribe (if audio provided)
2. Extract medical information
3. Retrieve patient memory
4. Generate diagnosis
5. Detect data drift
6. Save to memory
```

### 3. Dependencies Updated

**Firebase Functions (`functions/package.json`):**
```json
{
  "dependencies": {
    "firebase-admin": "^11.8.0",
    "firebase-functions": "^4.3.1",
    "axios": "^1.6.0",
    "multer": "^1.4.5-lts.1",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1"
  }
}
```

**Python Microservice (`python-service/requirements.txt`):**
```txt
# LangChain and LangGraph
langchain==0.1.0
langchain-openai==0.0.5
langchain-google-genai==0.0.6
langgraph==0.0.20

# Vector Database and Memory
chromadb==0.4.22
sentence-transformers==2.2.2

# MLops
mlflow==2.8.1
scikit-learn==1.3.2

# Audio Processing
openai-whisper==20231117
```

## Benefits of New Architecture

### 1. **Better Language Support**
- LangGraph and LangChain work natively in Python
- No more compatibility issues with JavaScript versions
- Full access to Python ML ecosystem

### 2. **Simplified Maintenance**
- Firebase Functions: Simple proxy logic
- Python Microservice: All complex logic centralized
- Clear separation of concerns

### 3. **Enhanced Capabilities**
- Complete workflow orchestration
- Better state management
- Comprehensive error handling
- Full MLops integration

### 4. **Scalability**
- Python microservice can be scaled independently
- Firebase Functions remain lightweight
- Easy to add new AI/ML capabilities

## API Flow Examples

### Complete Text Processing
```javascript
// Frontend → Firebase Functions
POST /process
{
  "text": "Tengo dolor de cabeza...",
  "patient_id": "patient_123",
  "language": "es"
}

// Firebase Functions → Python Microservice
POST /process
{
  "text": "Tengo dolor de cabeza...",
  "patient_id": "patient_123", 
  "language": "es"
}

// Python Microservice → LangGraph Workflow
// 1. Extract symptoms and patient info
// 2. Query patient memory
// 3. Generate diagnosis
// 4. Check for data drift
// 5. Save consultation to memory

// Response flows back through the chain
```

### Individual Service Calls
```javascript
// Direct service calls still work
POST /diagnose
POST /extract
POST /transcribe
// etc.
```

## Environment Variables

**Firebase Functions:**
```bash
PYTHON_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

**Python Microservice:**
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
MLFLOW_TRACKING_URI=http://localhost:5000
```

## Running the System

### 1. Start Python Microservice
```bash
cd python-service
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

### 2. Start Firebase Functions
```bash
cd functions
npm install
firebase emulators:start --only functions
# Runs on http://localhost:5001
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 4. Test the System
```bash
python test_api.py
```

## Migration Notes

### For Existing Users
1. **No frontend changes required** - API endpoints remain the same
2. **Enhanced functionality** - Better workflow orchestration
3. **Improved reliability** - Better error handling and state management

### For Developers
1. **Firebase Functions** - Now simple proxy, easy to maintain
2. **Python Microservice** - All AI/ML logic centralized here
3. **LangGraph** - Complete workflow orchestration available

## Future Enhancements

1. **Additional AI Models** - Easy to add new models in Python
2. **Advanced Workflows** - Complex multi-step workflows with LangGraph
3. **Enhanced MLops** - Better monitoring and drift detection
4. **Microservice Scaling** - Independent scaling of AI services
5. **API Gateway** - Optional API gateway for better routing

## Troubleshooting

### Common Issues

1. **Python Service Not Reachable**
   - Check if Python service is running on port 8000
   - Verify PYTHON_SERVICE_URL in Firebase Functions

2. **LangGraph Import Errors**
   - Ensure all Python dependencies are installed
   - Check Python version compatibility

3. **Memory Service Issues**
   - Verify ChromaDB is properly configured
   - Check memory service initialization

4. **MLops Integration**
   - Ensure MLflow is running
   - Check MLFLOW_TRACKING_URI configuration

### Debug Mode

Enable debug logging in Python service:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

This new architecture provides:
- ✅ **Better maintainability** - Clear separation of concerns
- ✅ **Enhanced capabilities** - Full LangGraph workflow orchestration
- ✅ **Improved reliability** - Better error handling and state management
- ✅ **Future-proof design** - Easy to extend and scale

The system now leverages the best of both worlds: Firebase's serverless capabilities for simple operations and Python's rich AI/ML ecosystem for complex workflows.
