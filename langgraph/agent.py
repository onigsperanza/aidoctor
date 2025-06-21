from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the LangGraph agent."""
    input_text: str
    audio_url: str
    patient_info: Dict[str, Any]
    symptoms: List[str]
    motive: str
    retrieved_history: List[str]
    diagnosis: str
    treatment: str
    recommendations: str
    metadata: Dict[str, Any]

class LangGraphAgent:
    def __init__(self):
        """Initialize LangGraph agent with workflow definition."""
        self.graph = self._create_workflow()
        
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("transcribe", self._transcribe_node)
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("diagnose", self._diagnose_node)
        
        # Define edges
        workflow.set_entry_point("transcribe")
        workflow.add_edge("transcribe", "extract")
        workflow.add_edge("extract", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "diagnose")
        workflow.add_edge("diagnose", END)
        
        return workflow.compile()
    
    async def _transcribe_node(self, state: AgentState) -> AgentState:
        """Transcribe audio if provided."""
        if state["audio_url"]:
            from services.whisper import WhisperService
            whisper_service = WhisperService()
            state["input_text"] = await whisper_service.transcribe(state["audio_url"])
        return state
    
    async def _extract_node(self, state: AgentState) -> AgentState:
        """Extract medical information from text."""
        from services.extract import ExtractService
        extract_service = ExtractService()
        
        extraction_result = await extract_service.extract_medical_info(
            state["input_text"],
            model=state.get("metadata", {}).get("model", "gpt-4")
        )
        
        state["patient_info"] = extraction_result["patient_info"]
        state["symptoms"] = extraction_result["symptoms"]
        state["motive"] = extraction_result["motive"]
        
        return state
    
    async def _retrieve_memory_node(self, state: AgentState) -> AgentState:
        """Retrieve patient history from memory."""
        from memory.cognee import CogneeMemory
        from utils.id_utils import generate_patient_id
        
        memory_service = CogneeMemory()
        patient_id = generate_patient_id(state["patient_info"])
        
        state["retrieved_history"] = await memory_service.retrieve_patient_history(
            patient_id,
            state["symptoms"]
        )
        
        return state
    
    async def _diagnose_node(self, state: AgentState) -> AgentState:
        """Generate diagnosis using LLM."""
        from services.diagnose import DiagnoseService
        
        diagnose_service = DiagnoseService()
        
        diagnosis_result = await diagnose_service.generate_diagnosis(
            {
                "patient_info": state["patient_info"],
                "symptoms": state["symptoms"],
                "motive": state["motive"]
            },
            state["retrieved_history"],
            model=state.get("metadata", {}).get("model", "gpt-4")
        )
        
        state["diagnosis"] = diagnosis_result["diagnosis"]
        state["treatment"] = diagnosis_result["treatment"]
        state["recommendations"] = diagnosis_result["recommendations"]
        
        return state
    
    async def run(self, initial_state: Dict[str, Any]) -> AgentState:
        """Run the complete workflow."""
        try:
            result = await self.graph.ainvoke(initial_state)
            logger.info("LangGraph workflow completed successfully")
            return result
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {str(e)}")
            raise Exception(f"Workflow execution failed: {str(e)}") 