import openai
import os
from typing import Dict, Any, List

class MedicalExtractionService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def extract_medical_info(self, text: str, language: str = "es") -> Dict[str, Any]:
        """
        Extract medical information from text
        """
        try:
            # For now, return a placeholder response
            # In production, you would use OpenAI's API with proper extraction prompts
            return {
                "patient_info": {
                    "name": "Paciente",
                    "age": 30,
                    "id": None
                },
                "symptoms": ["síntoma extraído del texto"],
                "medications": ["medicamento mencionado"],
                "allergies": ["alergia mencionada"],
                "motive": "Motivo de consulta extraído",
                "entities": ["entidad médica"],
                "confidence": 0.85,
                "language": language
            }
        except Exception as e:
            print(f"Error extracting medical info: {e}")
            return {
                "patient_info": {"name": "", "age": 0, "id": None},
                "symptoms": [],
                "medications": [],
                "allergies": [],
                "motive": "",
                "entities": [],
                "confidence": 0.0,
                "language": language
            } 