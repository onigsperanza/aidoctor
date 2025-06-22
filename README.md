# AI Doctor Assistant

A full-stack AI medical assistant web application that transcribes patient speech, extracts structured EMR data, leverages personalized patient knowledge graphs with local RAG capabilities, and generates personalized diagnostic reasoning using LLMs on Firebase.

## 🏥 Features

- **Speech Transcription**: Convert patient audio to text using OpenAI Whisper.
- **Medical Information Extraction**: Extract structured patient data using Google Gemini.
- **Patient Knowledge Graphs**: Advanced patient memory using local Firestore-based knowledge graphs with similarity search.
- **RAG-Powered Reasoning**: Retrieval-Augmented Generation over patient-specific context for personalized medical insights.
- **Diagnostic Suggestions**: AI-powered medical assessments with GPT-4 enhanced by patient history.
- **Serverless Backend**: Scalable and managed backend using Firebase Cloud Functions.
- **Modern UI**: React frontend with TypeScript and Vite.
- **Local Emulation**: Full local development environment with Firebase Emulators.

## 🏗️ Architecture

### Backend (Firebase)
- **Firebase Cloud Functions**: Serverless functions for all backend logic (processing, transcription, history).
- **Local Knowledge Graphs**: Patient memory system using Firestore with similarity-based RAG capabilities.
- **Firebase Firestore**: NoSQL database for storing patient knowledge graphs and metadata.
- **LangGraph**: AI workflow orchestration running within a Node.js environment.
- **OpenAI & Google AI**: Integration with Whisper, GPT-4, and Gemini models.

### Frontend (React)
- **React 18**: Modern UI framework.
- **TypeScript**: Type-safe development.
- **Vite**: Fast development server and build tool.
- **Tailwind CSS**: Utility-first styling (or your preferred choice).

### Infrastructure
- **Firebase Hosting**: Frontend deployment.
- **Firebase**: Backend infrastructure (Functions, Firestore).

## 🧠 AI Agent Workflow

The AI agent follows a sophisticated workflow that combines multiple AI capabilities:

1. **Speech Recognition**: Patient audio is transcribed using OpenAI Whisper
2. **Structured EMR Extraction**: Medical information is extracted and structured using Google Gemini
3. **Patient-Specific RAG**: Local knowledge graph searches patient history for relevant medical context
4. **Personalized Reasoning**: GPT-4 generates diagnostic suggestions enhanced by patient context

### Local Knowledge Graph Benefits

- **Knowledge Graphs**: Each patient gets a personalized knowledge graph stored in Firestore
- **Similarity Search**: Jaccard similarity algorithm for finding relevant medical history
- **Improved Accuracy**: RAG over patient-specific data reduces AI hallucinations and improves diagnostic relevance
- **Temporal Awareness**: The system understands how patient conditions evolve over time
- **No External Dependencies**: Self-contained system without requiring additional API keys

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Node.js**: v18 or newer.
- **Firebase CLI**: `npm install -g firebase-tools`
- **OpenAI API Key**
- **Google API Key**

### Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/onigsperanza/aidoctor.git
    cd aidoctor
    ```

2.  **Configure Backend Environment**

    You need to provide your API keys for the backend functions to work.

    -   Navigate to the `functions` directory: `cd functions`
    -   Create a `.env` file. You can copy the example: `cp env.example .env`
    -   Edit the `functions/.env` file and add your actual API keys:
        ```env
        OPENAI_API_KEY=your_openai_api_key_here
        GOOGLE_API_KEY=your_google_api_key_here
        ```
    -   Go back to the root directory: `cd ..`

3.  **Run the Application**

    The `run_local.sh` script handles everything: it installs dependencies for both frontend and backend, and starts the Firebase emulators and the frontend development server.

    ```bash
    chmod +x run_local.sh
    ./run_local.sh
    ```

### Accessing the Local Services

-   **Frontend App**: http://localhost:5173
-   **Firebase Emulator Suite**: http://127.0.0.1:4000
-   **Cloud Functions Emulator**:
    -   The functions are exposed under the project ID `aidoctor-dev`.
    -   Base URL: `http://127.0.0.1:5001/aidoctor-dev/us-central1`
    -   Example `process` endpoint: `http://127.0.0.1:5001/aidoctor-dev/us-central1/process`
-   **Firestore Emulator**: View and manage your local database via the Emulator Suite UI.

## 📋 API Usage

You can interact with the local functions using `curl` or any API client.

### Process Medical Text with RAG

-   **Endpoint**: `POST /process`
-   **URL**: `http://127.0.0.1:5001/aidoctor-dev/us-central1/process`
-   **Body**:
    ```json
    {
      "text": "El paciente se queja de un fuerte dolor de cabeza y fiebre desde hace dos días.",
      "patient_id": "test-patient-123"
    }
    ```
-   **Response**:
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

### Transcribe Audio

-   **Endpoint**: `POST /transcribe`
-   **URL**: `http://127.0.0.1:5001/aidoctor-dev/us-central1/transcribe`
-   **Body**: `multipart/form-data` with a single field `audio` containing the audio file.

```bash
curl -X POST http://127.0.0.1:5001/aidoctor-dev/us-central1/transcribe \
  -F "audio=@/path/to/your/audio.mp3"
```

### Get Patient History from Knowledge Graph

-   **Endpoint**: `GET /getHistory`
-   **URL**: `http://127.0.0.1:5001/aidoctor-dev/us-central1/getHistory?patient_id=test-patient-123`

### Search Patient Knowledge Graph

-   **Endpoint**: `POST /searchPatient`
-   **URL**: `http://127.0.0.1:5001/aidoctor-dev/us-central1/searchPatient`
-   **Body**:
    ```json
    {
      "patient_id": "test-patient-123",
      "query": "dolor de cabeza migraña"
    }
    ```

## 部署

### 1. Deploy Frontend
```bash
firebase deploy --only hosting
```

### 2. Deploy Backend Functions
```bash
# Make sure to set your production environment variables
# firebase functions:config:set openai.key="YOUR_KEY" google.key="YOUR_KEY"
firebase deploy --only functions
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

## 🔧 Local Development

Run the full stack locally in minutes using Docker and Vite.

### Requirements
- Docker
- Node.js + npm
- Firebase CLI (optional)
- `.env.local` in `frontend/`
- `dev.env` in project root

---

### 🧠 One Command to Start All

```bash
chmod +x run_local.sh && ./run_local.sh
```

---

### Manual Start (If Needed)

#### Backend

```bash
docker build -t ai-backend .
docker run -p 8000:8000 --env-file dev.env ai-backend
```

- Swagger UI: http://localhost:8000/docs

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

`.env.local` content:

```env
VITE_API_URL=http://localhost:8000
```

#### Firebase Emulator (Optional)

```bash
firebase emulators:start --only functions
```

---

### Folder Structure

```
├── backend/
│   ├── main.py
│   ├── services/
│   ├── langgraph/
│   └── memory/
├── frontend/
│   └── src/
├── run_local.sh
├── dev.env
└── frontend/.env.local
```

---

### ✅ Test Flow

1. Open http://localhost:5173  
2. Submit audio or text  
3. Backend returns structured EMR, diagnosis, and recommendations  
4. Inspect logs or Swagger: http://localhost:8000/docs

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