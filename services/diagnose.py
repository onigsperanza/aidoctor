import json
import logging
from typing import Dict, Any, List
import openai
import os

logger = logging.getLogger(__name__)

class DiagnoseService:
    def __init__(self):
        """Initialize diagnosis service with API keys."""
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_diagnosis(
        self,
        extraction_result: Dict[str, Any],
        retrieved_history: List[str],
        model: str = "gpt-4",
        prompt_version: str = "diagnosis_v3"
    ) -> Dict[str, str]:
        """
        Generate medical diagnosis using LLM with patient history.
        
        Args:
            extraction_result: Structured medical information from extraction
            retrieved_history: List of relevant patient history
            model: LLM to use (gpt-4 only)
            prompt_version: Version of prompt to use
            
        Returns:
            Diagnosis, treatment, and recommendations
        """
        try:
            # Load prompt template
            prompt = self._load_prompt(prompt_version)
            
            # Prepare context
            context = self._prepare_context(extraction_result, retrieved_history)
            
            # Format prompt with context
            formatted_prompt = prompt.format(context=context)
            
            # Get LLM response (OpenAI only)
            response = await self._call_openai(formatted_prompt)
            
            # Parse response
            diagnosis_result = self._parse_diagnosis_response(response)
            
            logger.info(f"Successfully generated diagnosis using OpenAI GPT-4")
            
            return diagnosis_result
            
        except Exception as e:
            logger.error(f"Error generating diagnosis: {str(e)}")
            raise Exception(f"Diagnosis generation failed: {str(e)}")
    
    def _load_prompt(self, version: str) -> str:
        """Load prompt template from file."""
        try:
            prompt_path = f"prompts/{version}.txt"
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to default prompt
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt for diagnosis generation."""
        return """
You are a medical AI assistant. Based on the following patient information and medical history, provide a comprehensive medical assessment.

Patient Information and Context:
{context}

Please provide your assessment in the following JSON format:
{{
  "diagnosis": "Your primary diagnosis or assessment",
  "treatment": "Recommended treatment plan",
  "recommendations": "Additional recommendations, follow-up instructions, or warnings"
}}

Important guidelines:
- Be thorough but concise
- Consider the patient's history when available
- Provide actionable treatment recommendations
- Include any red flags or urgent concerns
- Remember this is for informational purposes only

Return ONLY the JSON object, no additional text.
"""
    
    def _prepare_context(self, extraction_result: Dict[str, Any], history: List[str]) -> str:
        """Prepare context for diagnosis prompt."""
        patient_info = extraction_result["patient_info"]
        symptoms = extraction_result["symptoms"]
        motive = extraction_result["motive"]
        
        context = f"""
Patient Information:
- Name: {patient_info['name']}
- Age: {patient_info['age']}
- ID: {patient_info.get('id', 'Not provided')}

Current Symptoms: {', '.join(symptoms)}
Reason for Visit: {motive}
"""
        
        if history:
            context += f"\nRelevant Medical History:\n" + "\n".join([f"- {h}" for h in history])
        else:
            context += "\nNo relevant medical history found."
        
        return context
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant that provides diagnostic assessments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    
    def _parse_diagnosis_response(self, response: str) -> Dict[str, str]:
        """Parse diagnosis response from LLM."""
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            parsed = json.loads(response.strip())
            
            # Validate required fields
            required_fields = ["diagnosis", "treatment", "recommendations"]
            for field in required_fields:
                if field not in parsed or not isinstance(parsed[field], str):
                    raise ValueError(f"Missing or invalid field: {field}")
            
            return {
                "diagnosis": parsed["diagnosis"],
                "treatment": parsed["treatment"],
                "recommendations": parsed["recommendations"]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse diagnosis response: {response}")
            # Fallback to structured text parsing
            return self._fallback_parse(response)
        except Exception as e:
            logger.error(f"Error parsing diagnosis response: {str(e)}")
            raise Exception(f"Failed to parse diagnosis: {str(e)}")
    
    def _fallback_parse(self, response: str) -> Dict[str, str]:
        """Fallback parsing for non-JSON responses."""
        lines = response.split('\n')
        diagnosis = ""
        treatment = ""
        recommendations = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "diagnosis" in line.lower():
                current_section = "diagnosis"
                diagnosis = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "treatment" in line.lower():
                current_section = "treatment"
                treatment = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "recommendation" in line.lower():
                current_section = "recommendations"
                recommendations = line.split(":", 1)[1].strip() if ":" in line else ""
            elif current_section:
                if current_section == "diagnosis":
                    diagnosis += " " + line
                elif current_section == "treatment":
                    treatment += " " + line
                elif current_section == "recommendations":
                    recommendations += " " + line
        
        return {
            "diagnosis": diagnosis.strip(),
            "treatment": treatment.strip(),
            "recommendations": recommendations.strip()
        } 