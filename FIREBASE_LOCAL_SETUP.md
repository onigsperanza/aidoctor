# AI Doctor Assistant - Firebase Local Development Guide

This guide will help you set up and run the AI Doctor Assistant locally using Firebase emulator, just like an evaluator would.

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Python** (3.8 or higher)
   - Verify installation: `python --version`

3. **API Keys**
   - OpenAI API Key (required)
   - Google API Key (optional, for Gemini features)

### Step 1: Install Dependencies

#### Option A: Using the Setup Script (Recommended)

**Windows (PowerShell):**
```powershell
.\setup_firebase_local.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_firebase_local.sh
./setup_firebase_local.sh
```

#### Option B: Manual Setup

1. **Install Firebase CLI globally:**
   ```bash
   npm install -g firebase-tools
   ```

2. **Install function dependencies:**
   ```bash
   cd functions
   npm install
   cd ..
   ```

3. **Set up environment variables:**
   ```bash
   cp functions/env.example functions/.env
   ```

4. **Edit `functions/.env` and add your API keys:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Step 2: Start Firebase Emulator

```bash
firebase emulators:start
```

This will start:
- **Functions Emulator**: http://localhost:5001
- **Emulator UI**: http://localhost:4000
- **Hosting Emulator**: http://localhost:5000

### Step 3: Test the Application

Run the comprehensive test suite:

```bash
python test_firebase_emulator.py
```

## 📋 Available Endpoints

When the emulator is running, you can access these endpoints:

| Endpoint | URL | Description |
|----------|-----|-------------|
| Extract | `http://localhost:5001/demo-aidoctor/us-central1/extract` | Extract structured data from text |
| Diagnose | `http://localhost:5001/demo-aidoctor/us-central1/diagnose` | Generate diagnostic suggestions |
| Transcribe | `http://localhost:5001/demo-aidoctor/us-central1/transcribe` | Transcribe audio files |
| Process | `http://localhost:5001/demo-aidoctor/us-central1/process` | Full workflow (extract + diagnose) |

## 🧪 Testing Examples

### Test Spanish Extraction

```bash
curl -X POST http://localhost:5001/demo-aidoctor/us-central1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paciente: María González, 35 años. Síntomas: dolor de cabeza intenso, náuseas, sensibilidad a la luz. Duración: 3 días.",
    "patient_id": "test_patient_001"
  }'
```

### Test English Diagnosis

```bash
curl -X POST http://localhost:5001/demo-aidoctor/us-central1/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["chest pain", "shortness of breath", "fatigue"],
    "patient_info": {
      "name": "John Smith",
      "age": 45,
      "gender": "M"
    },
    "patient_id": "test_patient_002"
  }'
```

## 🔧 Configuration

### Environment Variables

Edit `functions/.env` to configure:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
GOOGLE_API_KEY=your_google_api_key_here
MLFLOW_TRACKING_URI=http://localhost:5000

# MedCAT Configuration (optional)
MEDCAT_MODEL_PATH=/path/to/medcat/model
MEDCAT_VOCAB_PATH=/path/to/medcat/vocab

# SNOMED Configuration
SNOMED_CONFIDENCE_THRESHOLD=0.85
SNOMED_ENABLE_GRAPH_TRAVERSAL=true
SNOMED_LOG_CONCEPT_DETAILS=true
```

### Firebase Configuration

The `firebase.json` file is already configured for local development:

```json
{
  "functions": {
    "source": "functions",
    "runtime": "nodejs18"
  },
  "emulators": {
    "functions": {
      "port": 5001
    },
    "ui": {
      "enabled": true,
      "port": 4000
    },
    "hosting": {
      "port": 5000
    }
  }
}
```

## 🏥 Features Tested

### ✅ Spanish Language Support
- **Prompts**: All system messages and prompts are in Spanish
- **Whisper Transcription**: Configured for Spanish audio
- **LLM Responses**: Generated in Spanish
- **EMR Extraction**: Handles Spanish medical terminology

### ✅ AI Capabilities
- **Speech-to-Text**: Whisper transcription
- **EMR Data Extraction**: Structured medical data extraction
- **Diagnostic Suggestions**: AI-powered diagnosis
- **Patient Memory**: Cognee knowledge graphs
- **Medical NER**: MedCAT entity recognition
- **SNOMED Validation**: Medical concept validation

### ✅ Observability
- **MLflow Integration**: Experiment tracking
- **Drift Detection**: Data drift monitoring
- **Logging**: Comprehensive logging
- **Metrics**: Performance monitoring

## 🐛 Troubleshooting

### Common Issues

1. **"Node.js is not installed"**
   - Download and install Node.js from https://nodejs.org/
   - Restart your terminal after installation

2. **"Firebase emulator not accessible"**
   - Make sure you're running `firebase emulators:start`
   - Check if ports 5001, 4000, 5000 are available

3. **"API key errors"**
   - Verify your API keys in `functions/.env`
   - Make sure the keys are valid and have sufficient credits

4. **"Function deployment errors"**
   - Check the Firebase Emulator UI for detailed logs
   - Verify all dependencies are installed in `functions/`

### Debug Mode

Run the emulator with debug logging:

```bash
firebase emulators:start --debug
```

### View Logs

Access the Firebase Emulator UI at http://localhost:4000 to:
- View function logs
- Monitor requests
- Debug issues
- Test functions interactively

## 📊 Performance Monitoring

### MLflow Dashboard

If MLflow is running, access the dashboard at http://localhost:5000 to view:
- Experiment tracking
- Model performance metrics
- Data drift alerts
- Training runs

### Function Metrics

Monitor function performance in the Firebase Emulator UI:
- Execution time
- Memory usage
- Error rates
- Request volume

## 🔄 Development Workflow

1. **Start emulator**: `firebase emulators:start`
2. **Make changes**: Edit code in `functions/`
3. **Test changes**: `python test_firebase_emulator.py`
4. **View logs**: http://localhost:4000
5. **Iterate**: Repeat steps 2-4

## 🚀 Production Deployment

When ready for production:

1. **Deploy to Firebase:**
   ```bash
   firebase deploy --only functions
   ```

2. **Update environment variables** in Firebase Console

3. **Configure custom domain** (optional)

## 📚 Additional Resources

- [Firebase Functions Documentation](https://firebase.google.com/docs/functions)
- [Firebase Emulator Documentation](https://firebase.google.com/docs/emulator-suite)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google AI Documentation](https://ai.google.dev/)

## 🤝 Support

If you encounter issues:

1. Check the Firebase Emulator UI logs
2. Review the troubleshooting section above
3. Check the GitHub repository for updates
4. Open an issue with detailed error information

---

**Happy Testing! 🎉** 