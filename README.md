# AI Doctor Assistant

A full-stack AI medical assistant web application that transcribes patient speech, extracts structured EMR data, leverages personalized vector memory, and generates diagnostic suggestions using LLMs.

## 🏥 Features

- **Speech Transcription**: Convert patient audio to text using Whisper
- **Medical Information Extraction**: Extract structured patient data using LLMs
- **Patient Memory**: Vector-based patient history retrieval using Cognee
- **Diagnostic Suggestions**: AI-powered medical assessments with GPT-4/Gemini
- **Observability**: MLflow integration for experiment tracking and drift detection
- **Production-Ready**: Prompt versioning, retry logic, and comprehensive logging
- **Modern UI**: React frontend with TypeScript and beautiful design

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: High-performance web framework
- **LangGraph**: AI workflow orchestration
- **Whisper**: Speech-to-text transcription
- **OpenAI/Gemini**: LLM integration for medical reasoning
- **Cognee**: Vector-based patient memory
- **MLflow**: Experiment tracking and observability

### Frontend (React)
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Beautiful component library

### Infrastructure
- **Firebase Hosting**: Frontend deployment
- **Firebase Cloud Functions**: API gateway
- **Firestore/BigQuery**: Data storage and analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key
- Google API key (for Gemini)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd aidoctor
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp env.example .env
# Edit .env with your API keys
```

4. **Start the backend**
```bash
python main.py
```

5. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 API Usage

### Process Medical Information

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient John Doe, age 35, experiencing severe headaches and fever for 3 days",
    "model": "gpt-4"
  }'
```

### Response Format

```json
{
  "patient_info": {
    "name": "John Doe",
    "age": 35,
    "id": "P12345"
  },
  "symptoms": ["headache", "fever", "fatigue"],
  "motive": "Patient experiencing severe headaches and fever for 3 days",
  "diagnosis": "Likely viral infection with secondary headache",
  "treatment": "Rest, hydration, acetaminophen for fever and pain",
  "recommendations": "Monitor symptoms, seek medical attention if fever persists >3 days",
  "metadata": {
    "request_id": "uuid",
    "model_version": "gpt-4",
    "prompt_version": "extract_v2,diagnosis_v3",
    "latency_ms": 1250,
    "timestamp": "2024-01-01T00:00:00Z",
    "input_type": "text"
  }
}
```

## 🧠 Technical Design Decisions

### LangGraph Workflow
- **Step 1**: Audio transcription (if provided)
- **Step 2**: Medical information extraction with JSON schema
- **Step 3**: Patient history retrieval using vector similarity
- **Step 4**: Diagnosis generation with context

### Patient Memory System
- **Cognee Integration**: Vector-based storage and retrieval
- **Patient Namespacing**: Unique IDs based on name + age hash
- **Similarity Search**: Cosine similarity for relevant history
- **Metadata Storage**: Symptoms, diagnosis, timestamps

### Prompt Versioning
- **extract_v2.json**: Medical information extraction
- **diagnosis_v3.txt**: Diagnosis generation
- **Version Tracking**: All prompts logged with request metadata

### Drift Detection
- **Schema Validation**: Check for missing fields
- **Symptom Count Variance**: Statistical anomaly detection
- **Content Similarity**: Cosine similarity with baseline
- **Alerting**: Automatic flagging of abnormal results

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `GOOGLE_API_KEY` | Google API key for Gemini | Yes |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URL | No |
| `FIREBASE_PROJECT_ID` | Firebase project ID | No |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | No |

### Model Configuration

The system supports multiple LLM providers:
- **GPT-4**: OpenAI's latest model (default)
- **Gemini**: Google's multimodal model

## 📊 Observability

### MLflow Integration
- **Experiment Tracking**: All requests logged as MLflow runs
- **Metrics**: Latency, success rate, symptom count
- **Artifacts**: Extraction and diagnosis results
- **Parameters**: Model version, prompt version, input type

### Drift Detection
- **Real-time Monitoring**: Automatic drift detection on each request
- **Baseline Management**: Rolling window of recent results
- **Alerting**: Configurable thresholds for anomalies

### Logging
- **Structured Logs**: JSON format for easy parsing
- **Request Tracing**: Unique IDs for end-to-end tracking
- **Error Handling**: Comprehensive error logging and recovery

## 🚀 Deployment

### Development
```bash
# Backend
python main.py

# Frontend
cd frontend && npm run dev
```

### Production (Firebase)
```bash
# Deploy frontend
firebase deploy --only hosting

# Deploy Cloud Functions
firebase deploy --only functions
```

### Docker
```bash
# Build and run
docker-compose up --build
```

## 🔒 Security & Compliance

### HIPAA Compliance
- **Data Encryption**: All data encrypted in transit and at rest
- **Access Controls**: Role-based access to patient data
- **Audit Logging**: Comprehensive audit trails
- **Data Retention**: Configurable data retention policies

### Privacy Features
- **Patient Anonymization**: Optional patient ID generation
- **Secure Storage**: Encrypted vector embeddings
- **Access Logging**: All data access logged and monitored

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This AI assistant is for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical decisions.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the MLflow dashboard for system metrics 