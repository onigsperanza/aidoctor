import uuid
from typing import str

def generate_patient_id() -> str:
    """
    Generate a unique patient ID
    """
    return str(uuid.uuid4()) 