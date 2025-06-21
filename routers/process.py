from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import uuid
from datetime import datetime

from services.whisper import WhisperService
from services.extract import ExtractService
from services.diagnose import DiagnoseService
from langgraph.agent import LangGraphAgent
from memory.cognee import CogneeMemory
from mlops.logger import MLOpsLogger
from mlops.drift import DriftDetector
from utils.id_utils import generate_patient_id

router = APIRouter()

class ProcessRequest(BaseModel):
    audio_url: Optional[str] = None
    text: Optional[str] = None
    model: str = "gpt-4"  # Only gpt-4 is supported

class ProcessResponse(BaseModel):
    patient_info: Dict[str, Any]
    symptoms: List[str]
    motive: str
    diagnosis: str
    treatment: str
    recommendations: str
    metadata: Dict[str, Any]

@router.post("/process", response_model=ProcessResponse)
async def process_medical_input(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Validate input
    if not request.audio_url and not request.text:
        raise HTTPException(status_code=400, detail="Either audio_url or text must be provided")
    
    try:
        # Initialize services
        whisper_service = WhisperService()
        extract_service = ExtractService()
        diagnose_service = DiagnoseService()
        memory_service = CogneeMemory()
        logger = MLOpsLogger()
        drift_detector = DriftDetector()
        
        # Step 1: Transcription (if audio provided)
        input_text = request.text
        if request.audio_url:
            input_text = await whisper_service.transcribe(request.audio_url)
        
        # Step 2: EMR Extraction
        extraction_result = await extract_service.extract_medical_info(
            input_text, 
            model="gpt-4",
            prompt_version="extract_v2"
        )
        
        # Step 3: Patient Memory Retrieval
        patient_id = generate_patient_id(extraction_result["patient_info"])
        retrieved_history = await memory_service.retrieve_patient_history(
            patient_id, 
            extraction_result["symptoms"]
        )
        
        # Step 4: Diagnosis Generation
        diagnosis_result = await diagnose_service.generate_diagnosis(
            extraction_result,
            retrieved_history,
            model="gpt-4",
            prompt_version="diagnosis_v3"
        )
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Prepare response
        response = ProcessResponse(
            patient_info=extraction_result["patient_info"],
            symptoms=extraction_result["symptoms"],
            motive=extraction_result["motive"],
            diagnosis=diagnosis_result["diagnosis"],
            treatment=diagnosis_result["treatment"],
            recommendations=diagnosis_result["recommendations"],
            metadata={
                "request_id": request_id,
                "model_version": "gpt-4",
                "prompt_version": "extract_v2,diagnosis_v3",
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "input_type": "audio" if request.audio_url else "text"
            }
        )
        
        # Background tasks for logging and drift detection
        background_tasks.add_task(
            logger.log_request,
            request_id=request_id,
            input_type="audio" if request.audio_url else "text",
            model="gpt-4",
            prompt_version="extract_v2,diagnosis_v3",
            latency_ms=latency_ms,
            extraction_result=extraction_result,
            diagnosis_result=diagnosis_result
        )
        
        background_tasks.add_task(
            drift_detector.check_drift,
            extraction_result=extraction_result,
            diagnosis_result=diagnosis_result
        )
        
        # Store in patient memory
        background_tasks.add_task(
            memory_service.store_consultation,
            patient_id=patient_id,
            symptoms=extraction_result["symptoms"],
            diagnosis=diagnosis_result["diagnosis"],
            timestamp=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        # Log error
        logger.log_error(request_id, str(e), latency_ms=int((time.time() - start_time) * 1000))
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") 