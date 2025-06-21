import json
import logging
from typing import Dict, Any, List
import openai
from pydantic import BaseModel, ValidationError
import os

logger = logging.getLogger(__name__)

class PatientInfo(BaseModel):
    name: str
    age: int
    id: str = None

class ExtractionResult(BaseModel):
    patient_info: PatientInfo
    symptoms: List[str]
    motive: str

class ExtractService:
    def __init__(self):
        """Initialize extraction service with API keys."""
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def extract_medical_info(
        self, 
        text: str, 
        model: str = "gpt-4",
        prompt_version: str = "extract_v2"
    ) -> Dict[str, Any]:
        """
        Extract structured medical information from text using LLM.
        
        Args:
            text: Input text to extract from
            model: LLM to use (gpt-4 only)
            prompt_version: Version of prompt to use
            
        Returns:
            Structured medical information
        """
        try:
            # Load prompt template
            prompt = self._load_prompt(prompt_version)
            
            # Format prompt with input text
            formatted_prompt = prompt.format(text=text)
            
            # Get LLM response (OpenAI only)
            response = await self._call_openai(formatted_prompt)
            
            # Parse and validate JSON response
            extraction_data = self._parse_json_response(response)
            validated_result = self._validate_extraction(extraction_data)
            
            logger.info(f"Successfully extracted medical info using OpenAI GPT-4")
            logger.info(f"Extracted {len(validated_result['symptoms'])} symptoms")
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error extracting medical info: {str(e)}")
            raise Exception(f"Extraction failed: {str(e)}")
    
    def _load_prompt(self, version: str) -> str:
        """Load prompt template from file."""
        try:
            prompt_path = f"prompts/{version}.json"
            with open(prompt_path, 'r') as f:
                prompt_data = json.load(f)
            return prompt_data["prompt"]
        except FileNotFoundError:
            # Fallback to default prompt
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt for medical information extraction."""
        return """
You are a medical AI assistant. Extract structured medical information from the following text.

Input text: {text}

Extract the following information and return it as a valid JSON object:
- patient_info: object with name (string), age (integer), and id (string or null)
- symptoms: array of symptom strings
- motive: short description of why the patient is seeking care

Return ONLY the JSON object, no additional text or explanation.

Example output format:
{{
  "patient_info": {{
    "name": "John Doe",
    "age": 35,
    "id": "P12345"
  }},
  "symptoms": ["headache", "fever", "fatigue"],
  "motive": "Patient experiencing severe headaches and fever for 3 days"
}}
"""
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant that extracts structured information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against schema."""
        try:
            # Validate patient_info
            if "patient_info" not in data:
                raise ValidationError("Missing patient_info")
            
            patient_info = data["patient_info"]
            if not isinstance(patient_info.get("name"), str):
                raise ValidationError("Patient name must be string")
            if not isinstance(patient_info.get("age"), int):
                raise ValidationError("Patient age must be integer")
            
            # Validate symptoms
            if "symptoms" not in data or not isinstance(data["symptoms"], list):
                raise ValidationError("Symptoms must be a list")
            
            # Validate motive
            if "motive" not in data or not isinstance(data["motive"], str):
                raise ValidationError("Motive must be a string")
            
            return data
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise Exception(f"Data validation failed: {str(e)}") 