import openai
import os
from typing import Dict, Any, List, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

logger = logging.getLogger(__name__)

class MedicalExtractionService:
    def __init__(self):
        """Initialize medical extraction service with MedCAT and SNOMED validation."""
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize LangChain model
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.1
        )
        
        # Initialize MedCAT (with fallback)
        self.medcat = None
        self._initialize_medcat()
        
        # SNOMED validation configuration
        self.snomed_config = {
            "confidence_threshold": float(os.getenv("SNOMED_CONFIDENCE_THRESHOLD", "0.85")),
            "enable_graph_traversal": os.getenv("SNOMED_ENABLE_GRAPH_TRAVERSAL", "true").lower() == "true",
            "log_concept_details": os.getenv("SNOMED_LOG_CONCEPT_DETAILS", "true").lower() == "true"
        }
        
        logger.info("Medical extraction service initialized")
    
    def _initialize_medcat(self):
        """Initialize MedCAT with fallback to simple NER."""
        try:
            import medcat
            # Try to load MedCAT model
            model_path = os.getenv("MEDCAT_MODEL_PATH")
            if model_path and os.path.exists(model_path):
                self.medcat = medcat.CAT(model_path=model_path)
                logger.info("MedCAT model loaded successfully")
            else:
                logger.warning("MedCAT model path not found, using fallback NER")
                self.medcat = None
        except ImportError:
            logger.warning("MedCAT not available, using fallback NER")
            self.medcat = None
        except Exception as e:
            logger.error(f"Failed to initialize MedCAT: {e}")
            self.medcat = None
    
    async def extract_medical_info(self, text: str, language: str = "es") -> Dict[str, Any]:
        """
        Extract medical information using MedCAT NER and SNOMED validation
        """
        try:
            # Extract entities using MedCAT or fallback
            ner_results = await self._extract_entities(text, language)
            
            # Validate concepts against SNOMED
            snomed_validation = await self._validate_snomed_concepts(ner_results.get("concepts", []))
            
            # Extract structured information using LangChain
            structured_info = await self._extract_structured_info(text, ner_results, language)
            
            # Combine results
            result = {
                "patient_info": structured_info.get("patient_info", {}),
                "symptoms": structured_info.get("symptoms", []),
                "medications": structured_info.get("medications", []),
                "allergies": structured_info.get("allergies", []),
                "motive": structured_info.get("motive", ""),
                "entities": ner_results.get("entities", []),
                "confidence": ner_results.get("confidence", 0.0),
                "language": language,
                "ner_results": ner_results,
                "snomed_validation": snomed_validation
            }
            
            logger.info(f"Extracted {len(result['symptoms'])} symptoms, {len(result['medications'])} medications")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting medical info: {e}")
            return self._get_fallback_result(language)
    
    async def _extract_entities(self, text: str, language: str) -> Dict[str, Any]:
        """Extract medical entities using MedCAT or fallback."""
        try:
            if self.medcat:
                # Use MedCAT for NER
                doc = self.medcat(text)
                entities = []
                concepts = []
                
                for ent in doc.ents:
                    entity_info = {
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "label": ent.label_,
                        "confidence": ent._.confidence
                    }
                    entities.append(entity_info)
                    
                    # Get concept information
                    if hasattr(ent, '_') and hasattr(ent._, 'cui'):
                        concept_info = {
                            "cui": ent._.cui,
                            "name": ent._.name,
                            "confidence": ent._.confidence,
                            "semantic_types": getattr(ent._, 'semantic_types', []),
                            "is_negated": getattr(ent._, 'is_negated', False)
                        }
                        concepts.append(concept_info)
                
                return {
                    "entities": entities,
                    "concepts": concepts,
                    "confidence": sum([ent["confidence"] for ent in entities]) / len(entities) if entities else 0.0,
                    "method": "medcat"
                }
            else:
                # Fallback to simple keyword extraction
                return await self._fallback_ner(text, language)
                
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return await self._fallback_ner(text, language)
    
    async def _fallback_ner(self, text: str, language: str) -> Dict[str, Any]:
        """Fallback NER using simple keyword matching."""
        # Simple medical keywords for Spanish
        medical_keywords = {
            "symptoms": [
                "dolor", "fiebre", "tos", "dolor de cabeza", "náuseas", "vómitos",
                "fatiga", "disnea", "mareos", "dolor abdominal", "diarrea",
                "estreñimiento", "pérdida de apetito", "insomnio", "ansiedad"
            ],
            "medications": [
                "paracetamol", "ibuprofeno", "aspirina", "antibiótico",
                "antihistamínico", "antidepresivo", "antihipertensivo"
            ],
            "conditions": [
                "hipertensión", "diabetes", "asma", "artritis", "migraña",
                "depresión", "ansiedad", "insomnio", "obesidad"
            ]
        }
        
        entities = []
        concepts = []
        
        for category, keywords in medical_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    entities.append({
                        "text": keyword,
                        "label": category,
                        "confidence": 0.7  # Default confidence for fallback
                    })
                    
                    concepts.append({
                        "cui": f"FALLBACK_{category.upper()}_{keyword.upper()}",
                        "name": keyword,
                        "confidence": 0.7,
                        "semantic_types": [category],
                        "is_negated": False
                    })
        
        return {
            "entities": entities,
            "concepts": concepts,
            "confidence": 0.7 if entities else 0.0,
            "method": "fallback"
        }
    
    async def _validate_snomed_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate medical concepts against SNOMED-CT."""
        validation_results = []
        
        for concept in concepts:
            try:
                # Simulate SNOMED validation
                # In production, you would use actual SNOMED-CT API or database
                is_valid = concept.get("confidence", 0) >= self.snomed_config["confidence_threshold"]
                
                validation_result = {
                    "concept_id": concept.get("cui"),
                    "concept_name": concept.get("name"),
                    "is_valid": is_valid,
                    "confidence": concept.get("confidence", 0),
                    "validation_method": "confidence_threshold",
                    "threshold": self.snomed_config["confidence_threshold"],
                    "semantic_types": concept.get("semantic_types", []),
                    "is_negated": concept.get("is_negated", False)
                }
                
                # Add graph traversal info if enabled
                if self.snomed_config["enable_graph_traversal"]:
                    validation_result["graph_traversal"] = {
                        "parent_concepts": [],
                        "child_concepts": [],
                        "related_concepts": []
                    }
                
                validation_results.append(validation_result)
                
            except Exception as e:
                logger.error(f"Error validating concept {concept.get('cui')}: {e}")
                validation_results.append({
                    "concept_id": concept.get("cui"),
                    "concept_name": concept.get("name"),
                    "is_valid": False,
                    "error": str(e)
                })
        
        return validation_results
    
    async def _extract_structured_info(self, text: str, ner_results: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Extract structured medical information using LangChain."""
        try:
            # Create prompt for structured extraction
            system_prompt = """You are a medical information extraction specialist. Extract structured medical information from the given text. Return the information in JSON format with the following structure:
            {
                "patient_info": {
                    "name": "patient name if mentioned",
                    "age": "age if mentioned",
                    "gender": "gender if mentioned"
                },
                "symptoms": ["list of symptoms mentioned"],
                "medications": ["list of medications mentioned"],
                "allergies": ["list of allergies mentioned"],
                "motive": "reason for consultation"
            }
            
            Focus on medical accuracy and extract only information that is explicitly mentioned in the text."""
            
            human_prompt = f"Extract medical information from this text: {text}"
            
            # Get LLM response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            response_text = response.generations[0][0].text
            
            # Parse JSON response
            try:
                structured_data = json.loads(response_text)
                return structured_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON, using fallback")
                return self._extract_fallback_structured_info(text, ner_results)
                
        except Exception as e:
            logger.error(f"Error in structured extraction: {e}")
            return self._extract_fallback_structured_info(text, ner_results)
    
    def _extract_fallback_structured_info(self, text: str, ner_results: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback structured information extraction."""
        # Extract symptoms from NER results
        symptoms = []
        for entity in ner_results.get("entities", []):
            if entity.get("label") == "symptoms":
                symptoms.append(entity.get("text"))
        
        # Extract medications from NER results
        medications = []
        for entity in ner_results.get("entities", []):
            if entity.get("label") == "medications":
                medications.append(entity.get("text"))
        
        return {
            "patient_info": {
                "name": "Paciente",
                "age": None,
                "gender": None
            },
            "symptoms": symptoms,
            "medications": medications,
            "allergies": [],
            "motive": "Consulta médica"
        }
    
    def _get_fallback_result(self, language: str) -> Dict[str, Any]:
        """Return fallback result when extraction fails."""
        return {
            "patient_info": {"name": "", "age": 0, "id": None},
            "symptoms": [],
            "medications": [],
            "allergies": [],
            "motive": "",
            "entities": [],
            "confidence": 0.0,
            "language": language,
            "ner_results": {"entities": [], "concepts": [], "confidence": 0.0, "method": "fallback"},
            "snomed_validation": []
        }
