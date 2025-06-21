import hashlib
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_patient_id(patient_info: Dict[str, Any]) -> str:
    """
    Generate a unique patient ID based on patient information.
    
    Args:
        patient_info: Dictionary containing patient information
        
    Returns:
        Unique patient identifier
    """
    try:
        # Extract key identifying information
        name = patient_info.get("name", "").lower().strip()
        age = str(patient_info.get("age", ""))
        patient_id = patient_info.get("id", "")
        
        # Create a hash from the identifying information
        identifier_string = f"{name}_{age}_{patient_id}"
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(identifier_string.encode())
        patient_hash = hash_object.hexdigest()[:16]  # Use first 16 characters
        
        # Format as readable ID
        formatted_id = f"P{patient_hash.upper()}"
        
        logger.info(f"Generated patient ID: {formatted_id} for patient: {name}")
        return formatted_id
        
    except Exception as e:
        logger.error(f"Error generating patient ID: {str(e)}")
        # Fallback to a simple hash
        fallback_string = str(patient_info)
        hash_object = hashlib.sha256(fallback_string.encode())
        return f"P{hash_object.hexdigest()[:16].upper()}" 