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
- **Spanish Language Support**: Full Spanish backend and frontend support
- **Medical AI**: MedCAT for NER and SNOMED-CT concept mapping
- **Drift Detection**: Automated data drift monitoring and alerting

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: Firebase Functions (Node.js) + Python Microservice
- **AI/ML**: OpenAI GPT-4, Google Gemini, Whisper, MedCAT, SNOMED-CT
- **Memory**: Cognee Knowledge Graphs
- **MLops**: MLflow for observability and drift detection
- **Language**: Spanish (es)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │ Firebase Functions│    │   AI/ML Services │
│                 │    │                  │    │                 │
│ • Modern UI     │◄──►│ • LangGraph      │◄──►│ • OpenAI GPT-4  │
│ • Audio Upload  │    │ • Cognee RAG     │    │ • Google Gemini  │
│ • Real-time     │    │ • MLflow Logging │    │ • MedCAT NER     │
│ • Patient Mgmt  │    │ • Drift Detection│    │ • SNOMED Validation│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start - Local Firebase Emulation

### Prerequisites

1. **Node.js 18+** and **npm**
2. **Python 3.9+** and **pip**
3. **Docker** and **Docker Compose**
4. **Firebase CLI**: `npm install -g firebase-tools`

### Step-by-Step Setup
```bash
git clone https://github.com/yourusername/aidoctor.git
cd aidoctor
```

#### 2. Install Dependencies
```bash
# Install frontend dependencies
cd frontend && npm install && cd ..

# Install Firebase Functions dependencies
cd functions && npm install && cd ..

# Install Python microservice dependencies
cd python-service && pip install -r requirements.txt && cd ..
```

#### 3. Configure Environment Variables
```bash
# Copy environment files
cp functions/env.example functions/.env
cp .env.example .env

# Edit the files with your API keys
# functions/.env:
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
PYTHON_SERVICE_URL=http://localhost:8000

# .env (for Docker Compose):
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

#### 4. Start All Services
```bash
# Option A: Using the provided script (Recommended)
chmod +x run_local_firebase.sh
./run_local_firebase.sh start

# Option B: Manual Docker Compose
docker-compose up --build -d
```

#### 5. Verify Services
```bash
# Test all services
./run_local_firebase.sh test
```

### 🌐 Service URLs

- **Frontend**: http://localhost:5173
- **Firebase Functions**: http://localhost:5001
- **Python Microservice**: http://localhost:8000
- **MLflow**: http://localhost:5000
- **Firebase Emulator UI**: http://localhost:4000

## 🧪 Testing the Application

### 1. Health Checks
```bash
# Test Firebase Functions
curl http://localhost:5001/health

# Test Python Microservice
curl http://localhost:8000/health
```

### 2. Process Text
```bash
curl -X POST http://localhost:5001/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tengo dolor de cabeza y fiebre desde hace 2 días",
    "patient_id": "test-patient-123"
  }'
```

### 3. Transcribe Audio
```bash
curl -X POST http://localhost:5001/transcribe \
  -F "audio=@path/to/your/audio.mp3"
```

### 4. Complete Audio Processing
```bash
curl -X POST http://localhost:5001/processAudio \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "patient_id": "test-patient-123",
    "language": "es"
  }'
```

### 5. Memory Operations
```bash
# Save to memory
curl -X POST http://localhost:5001/saveMemory \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-patient-123",
    "content": "Dolor de cabeza y fiebre",
    "content_type": "symptom"
  }'

# Query memory
curl -X POST http://localhost:5001/queryMemory \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-patient-123",
    "query": "dolor de cabeza",
    "limit": 5
  }'
```

## 🔧 Development Commands

### Using the Script
```bash
# Start all services
./run_local_firebase.sh start

# Stop all services
./run_local_firebase.sh stop

# Restart all services
./run_local_firebase.sh restart

# View logs
./run_local_firebase.sh logs

# Test services
./run_local_firebase.sh test
```

### Manual Commands
```bash
# Start services
docker-compose up --build -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose up --build -d backend

# Access service shell
docker-compose exec backend bash
docker-compose exec functions bash
```

## 📁 Project Structure

```
aidoctor/
├── frontend/                 # React frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── functions/               # Firebase Functions (Node.js)
│   ├── index.js            # Main functions
│   ├── package.json
│   ├── .env               # Environment variables
│   └── Dockerfile
├── python-service/         # Python microservice
│   ├── main.py            # FastAPI app
│   ├── services/          # AI services
│   ├── memory/            # Cognee memory
│   ├── mlops/             # MLflow & drift detection
│   ├── requirements.txt
│   └── Dockerfile
├── prompts/               # AI prompts
├── docker-compose.yml     # Local development
├── run_local_firebase.sh  # Setup script
└── README.md
```

## 🔌 API Endpoints

### Firebase Functions (Port 5001)
- `GET /health` - Health check
- `POST /process` - Process text input
- `POST /transcribe` - Transcribe audio file
- `POST /processAudio` - Complete audio processing
- `POST /saveMemory` - Save to patient memory
- `POST /queryMemory` - Query patient memory

### Python Microservice (Port 8000)
- `GET /health` - Health check
- `POST /diagnose` - Generate diagnosis
- `POST /extract` - Extract medical information
- `POST /transcribe` - Transcribe audio
- `POST /memory/save` - Save to memory
- `POST /memory/query` - Query memory
- `POST /mlops/log` - Log to MLflow
- `POST /mlops/drift` - Check for drift
- `POST /process-audio` - Complete audio pipeline

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :5001
   lsof -i :8000
   lsof -i :5173
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Docker not running**
   ```bash
   # Start Docker Desktop
   # On Linux: sudo systemctl start docker
   ```

3. **API keys not working**
   ```bash
   # Check environment variables
   docker-compose exec functions env | grep API_KEY
   docker-compose exec backend env | grep API_KEY
   ```

4. **Services not starting**
   ```bash
   # Check logs
   docker-compose logs -f
   
   # Rebuild services
   docker-compose down
   docker-compose up --build -d
   ```

### Debug Mode
```bash
# Run services in debug mode
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up

# Access service logs
docker-compose logs -f backend
docker-compose logs -f functions
docker-compose logs -f frontend
```

## 🚀 Production Deployment

### Firebase Functions
```bash
cd functions
firebase login
firebase deploy --only functions
```

### Python Microservice (Cloud Run)
```bash
cd python-service
gcloud builds submit --tag gcr.io/PROJECT_ID/aidoctor-python
gcloud run deploy aidoctor-python --image gcr.io/PROJECT_ID/aidoctor-python
```

### Frontend (Firebase Hosting)
```bash
cd frontend
npm run build
firebase deploy --only hosting
```

## 📊 Monitoring & Observability

- **MLflow**: http://localhost:5000 (experiments, metrics, artifacts)
- **Firebase Console**: https://console.firebase.google.com
- **Application Logs**: `docker-compose logs -f`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `./run_local_firebase.sh test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs: `docker-compose logs -f`
3. Open an issue on GitHub
4. Contact the development team

---

**Happy coding! 🏥💻** 