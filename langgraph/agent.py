from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the LangGraph agent."""
    input_text: str
    audio_url: Optional[str]
    patient_id: Optional[str]
    patient_info: Dict[str, Any]
    symptoms: List[str]
    motive: str
    retrieved_history: List[str]
    diagnosis: str
    treatment: str
    recommendations: List[str]
    metadata: Dict[str, Any]
    drift_flags: List[str]
    ner_results: Dict[str, Any]

class LangGraphAgent:
    def __init__(self):
        """Initialize LangGraph agent with workflow definition."""
        self.graph = self._create_workflow()
        
        # Initialize LLM models
        self.openai_model = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.7
        )
        
        self.gemini_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )
        
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("transcribe", self._transcribe_node)
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("diagnose", self._diagnose_node)
        workflow.add_node("detect_drift", self._detect_drift_node)
        workflow.add_node("save_to_memory", self._save_to_memory_node)
        
        # Define edges
        workflow.set_entry_point("transcribe")
        workflow.add_edge("transcribe", "extract")
        workflow.add_edge("extract", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "diagnose")
        workflow.add_edge("diagnose", "detect_drift")
        workflow.add_edge("detect_drift", "save_to_memory")
        workflow.add_edge("save_to_memory", END)
        
        return workflow.compile()
    
    async def _transcribe_node(self, state: AgentState) -> AgentState:
        """Transcribe audio if provided."""
        if state.get("audio_url"):
            try:
                from services.whisper import WhisperService
                whisper_service = WhisperService()
                transcription = await whisper_service.transcribe_audio(
                    audio_url=state["audio_url"],
                    language="es"
                )
                state["input_text"] = transcription
                logger.info(f"Transcribed audio: {transcription[:100]}...")
            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                state["input_text"] = "Error en transcripción de audio"
        return state
    
    async def _extract_node(self, state: AgentState) -> AgentState:
        """Extract medical information from text."""
        try:
            from services.extract import MedicalExtractionService
            extract_service = MedicalExtractionService()
            
            extraction_result = await extract_service.extract_medical_info(
                text=state["input_text"],
                language="es"
            )
            
            state["patient_info"] = extraction_result.get("patient_info", {})
            state["symptoms"] = extraction_result.get("symptoms", [])
            state["motive"] = extraction_result.get("motive", "")
            state["ner_results"] = extraction_result.get("ner_results", {})
            
            logger.info(f"Extracted {len(state['symptoms'])} symptoms")
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            state["patient_info"] = {}
            state["symptoms"] = []
            state["motive"] = ""
            state["ner_results"] = {}
        
        return state
    
    async def _retrieve_memory_node(self, state: AgentState) -> AgentState:
        """Retrieve patient history from memory."""
        if not state.get("patient_id"):
            state["retrieved_history"] = []
            return state
            
        try:
            from memory.cognee import CogneeMemoryService
            memory_service = CogneeMemoryService()
            
            # Query memory with current symptoms
            current_symptoms = " ".join(state["symptoms"])
            memory_results = await memory_service.query_memory(
                patient_id=state["patient_id"],
                query=current_symptoms,
                limit=5
            )
            
            state["retrieved_history"] = memory_results.get("results", [])
            logger.info(f"Retrieved {len(state['retrieved_history'])} memory entries")
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            state["retrieved_history"] = []
        
        return state
    
    async def _diagnose_node(self, state: AgentState) -> AgentState:
        """Generate diagnosis using LLM."""
        try:
            from services.diagnose import MedicalDiagnosisService
            diagnose_service = MedicalDiagnosisService()
            
            # Prepare context from memory
            memory_context = ""
            if state["retrieved_history"]:
                memory_context = "\n".join([
                    f"Consulta anterior: {entry.get('content', '')}"
                    for entry in state["retrieved_history"]
                ])
            
            diagnosis_result = await diagnose_service.generate_diagnosis(
                symptoms=state["input_text"],
                model="gpt-4",
                language="es"
            )
            
            state["diagnosis"] = diagnosis_result.get("diagnosis", "")
            state["treatment"] = diagnosis_result.get("treatment", "")
            state["recommendations"] = diagnosis_result.get("recommendations", [])
            
            logger.info(f"Generated diagnosis: {state['diagnosis'][:100]}...")
        except Exception as e:
            logger.error(f"Diagnosis failed: {e}")
            state["diagnosis"] = "Error en generación de diagnóstico"
            state["treatment"] = ""
            state["recommendations"] = []
        
        return state
    
    async def _detect_drift_node(self, state: AgentState) -> AgentState:
        """Detect data drift using MLops."""
        try:
            from mlops.drift import DriftDetector
            drift_detector = DriftDetector()
            
            drift_result = await drift_detector.detect_drift({
                "current_data": {
                    "symptoms": state["symptoms"],
                    "patient_info": state["patient_info"],
                    "extraction_confidence": state.get("ner_results", {}).get("confidence", 0.0)
                },
                "reference_data": [],
                "threshold": 0.05
            })
            
            state["drift_flags"] = drift_result.get("drift_detected", [])
            logger.info(f"Drift detection: {state['drift_flags']}")
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            state["drift_flags"] = []
        
        return state
    
    async def _save_to_memory_node(self, state: AgentState) -> AgentState:
        """Save consultation to memory."""
        if not state.get("patient_id"):
            return state
            
        try:
            from memory.cognee import CogneeMemoryService
            memory_service = CogneeMemoryService()
            
            # Create consultation summary
            consultation_summary = f"""
            Síntomas: {', '.join(state['symptoms'])}
            Diagnóstico: {state['diagnosis']}
            Tratamiento: {state['treatment']}
            Recomendaciones: {', '.join(state['recommendations'])}
            """
            
            await memory_service.save_to_memory(
                patient_id=state["patient_id"],
                content=consultation_summary,
                content_type="consultation"
            )
            
            logger.info(f"Saved consultation to memory for patient {state['patient_id']}")
        except Exception as e:
            logger.error(f"Memory save failed: {e}")
        
        return state
    
    async def run(self, initial_state: Dict[str, Any]) -> AgentState:
        """Run the complete workflow."""
        try:
            # Ensure all required fields are present
            complete_state = {
                "input_text": "",
                "audio_url": None,
                "patient_id": None,
                "patient_info": {},
                "symptoms": [],
                "motive": "",
                "retrieved_history": [],
                "diagnosis": "",
                "treatment": "",
                "recommendations": [],
                "metadata": {
                    "model_version": "gpt-4",
                    "timestamp": datetime.now().isoformat(),
                    "workflow_version": "1.0"
                },
                "drift_flags": [],
                "ner_results": {}
            }
            
            # Update with provided initial state
            complete_state.update(initial_state)
            
            result = await self.graph.ainvoke(complete_state)
            logger.info("LangGraph workflow completed successfully")
            return result
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {str(e)}")
            raise Exception(f"Workflow execution failed: {str(e)}")
    
    def create_initial_state(self, text: str, patient_id: Optional[str] = None, audio_url: Optional[str] = None) -> Dict[str, Any]:
        """Create initial state for the workflow."""
        return {
            "input_text": text,
            "audio_url": audio_url,
            "patient_id": patient_id,
            "metadata": {
                "model_version": "gpt-4",
                "timestamp": datetime.now().isoformat(),
                "workflow_version": "1.0"
            }
        }
