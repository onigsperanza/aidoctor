from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import logging
from datetime import datetime

# Import our custom modules
from services.diagnose import MedicalDiagnosisService
from services.extract import MedicalExtractionService
from services.whisper import WhisperService
from memory.cognee import CogneeMemoryService
from mlops.logger import MLflowLogger
from mlops.drift import DriftDetector
from utils.id_utils import generate_patient_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Doctor Python Microservice",
    description="Handles medical AI operations: diagnosis, extraction, memory, and MLops",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
diagnosis_service = MedicalDiagnosisService()
extraction_service = MedicalExtractionService()
whisper_service = WhisperService()
memory_service = CogneeMemoryService()
mlflow_logger = MLflowLogger()
drift_detector = DriftDetector()

# Pydantic models
class AudioRequest(BaseModel):
    audio_url: str
    patient_id: Optional[str] = None
    language: str = "es"

class TextRequest(BaseModel):
    text: str
    patient_id: Optional[str] = None
    language: str = "es"

class DiagnosisRequest(BaseModel):
    symptoms: str
    patient_id: Optional[str] = None
    model: str = "gpt-4"
    language: str = "es"

class MemoryRequest(BaseModel):
    patient_id: str
    content: str
    content_type: str = "symptom"

class MemoryQueryRequest(BaseModel):
    patient_id: str
    query: str
    limit: int = 5

@app.get("/")
async def root():
    return {"message": "AI Doctor Python Microservice", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test basic functionality
        services_status = {
            "diagnosis_service": True,
            "extraction_service": True,
            "whisper_service": True,
            "memory_service": True,
            "mlflow_logger": True,
            "drift_detector": True
        }
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": services_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(request: AudioRequest):
    """Transcribe audio to text using Whisper"""
    try:
        logger.info(f"Transcribing audio from: {request.audio_url}")
        
        # Generate patient ID if not provided
        patient_id = request.patient_id or generate_patient_id()
        
        # Transcribe audio
        transcription = await whisper_service.transcribe_audio(
            audio_url=request.audio_url,
            language=request.language
        )
        
        # Log to MLflow
        mlflow_logger.log_transcription(
            patient_id=patient_id,
            audio_url=request.audio_url,
            transcription=transcription,
            language=request.language
        )
        
        return {
            "patient_id": patient_id,
            "transcription": transcription,
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract")
async def extract_medical_info(request: TextRequest):
    """Extract medical information from text"""
    try:
        logger.info(f"Extracting medical info for patient: {request.patient_id}")
        
        # Generate patient ID if not provided
        patient_id = request.patient_id or generate_patient_id()
        
        # Extract medical information
        extraction_result = await extraction_service.extract_medical_info(
            text=request.text,
            language=request.language
        )
        
        # Log to MLflow
        mlflow_logger.log_extraction(
            patient_id=patient_id,
            text=request.text,
            extraction=extraction_result,
            language=request.language
        )
        
        return {
            "patient_id": patient_id,
            "extraction": extraction_result,
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnose")
async def generate_diagnosis(request: DiagnosisRequest):
    """Generate medical diagnosis"""
    try:
        logger.info(f"Generating diagnosis for patient: {request.patient_id}")
        
        # Generate patient ID if not provided
        patient_id = request.patient_id or generate_patient_id()
        
        # Generate diagnosis
        diagnosis_result = await diagnosis_service.generate_diagnosis(
            symptoms=request.symptoms,
            model=request.model,
            language=request.language
        )
        
        # Log to MLflow
        mlflow_logger.log_diagnosis(
            patient_id=patient_id,
            symptoms=request.symptoms,
            diagnosis=diagnosis_result,
            model=request.model,
            language=request.language
        )
        
        return {
            "patient_id": patient_id,
            "diagnosis": diagnosis_result,
            "model": request.model,
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/save")
async def save_to_memory(request: MemoryRequest):
    """Save information to patient memory"""
    try:
        logger.info(f"Saving to memory for patient: {request.patient_id}")
        
        # Save to memory
        memory_result = await memory_service.save_memory(
            patient_id=request.patient_id,
            content=request.content,
            content_type=request.content_type
        )
        
        return {
            "patient_id": request.patient_id,
            "memory_id": memory_result.get("memory_id"),
            "status": "saved",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Memory save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/query")
async def query_memory(request: MemoryQueryRequest):
    """Query patient memory"""
    try:
        logger.info(f"Querying memory for patient: {request.patient_id}")
        
        # Query memory
        memory_results = await memory_service.query_memory(
            patient_id=request.patient_id,
            query=request.query,
            limit=request.limit
        )
        
        return {
            "patient_id": request.patient_id,
            "query": request.query,
            "results": memory_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Memory query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mlops/log")
async def log_to_mlflow(data: Dict[str, Any]):
    """Log data to MLflow"""
    try:
        logger.info("Logging to MLflow")
        
        # Log to MLflow
        mlflow_logger.log_custom_metric(
            metric_name=data.get("metric_name"),
            value=data.get("value"),
            step=data.get("step"),
            tags=data.get("tags", {})
        )
        
        return {
            "status": "logged",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"MLflow logging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mlops/drift")
async def check_drift(data: Dict[str, Any]):
    """Check for data drift"""
    try:
        logger.info("Checking for data drift")
        
        # Check drift
        drift_result = drift_detector.detect_drift(
            current_data=data.get("current_data"),
            reference_data=data.get("reference_data"),
            threshold=data.get("threshold", 0.05)
        )
        
        return {
            "drift_detected": drift_result.get("drift_detected"),
            "drift_score": drift_result.get("drift_score"),
            "details": drift_result.get("details"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Drift detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-audio")
async def process_audio_complete(request: AudioRequest):
    """Complete audio processing pipeline: transcribe -> extract -> diagnose"""
    try:
        logger.info(f"Processing complete audio pipeline for: {request.audio_url}")
        
        # Generate patient ID if not provided
        patient_id = request.patient_id or generate_patient_id()
        
        # Step 1: Transcribe
        transcription_result = await transcribe_audio(request)
        transcription = transcription_result["transcription"]
        
        # Step 2: Extract medical info
        extraction_result = await extract_medical_info(TextRequest(
            text=transcription,
            patient_id=patient_id,
            language=request.language
        ))
        
        # Step 3: Generate diagnosis
        diagnosis_result = await generate_diagnosis(DiagnosisRequest(
            symptoms=transcription,
            patient_id=patient_id,
            language=request.language
        ))
        
        # Step 4: Save to memory
        await save_to_memory(MemoryRequest(
            patient_id=patient_id,
            content=f"Audio consultation: {transcription}",
            content_type="consultation"
        ))
        
        return {
            "patient_id": patient_id,
            "transcription": transcription,
            "extraction": extraction_result["extraction"],
            "diagnosis": diagnosis_result["diagnosis"],
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Complete audio processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 