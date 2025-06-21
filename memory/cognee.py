import logging
from typing import List, Dict, Any
from datetime import datetime
import hashlib
import json
import os

logger = logging.getLogger(__name__)

class CogneeMemory:
    def __init__(self):
        """Initialize Cognee memory service."""
        # In a real implementation, this would connect to Cognee
        # For now, we'll use a simple in-memory storage with vector-like retrieval
        self.memory_store = {}
        self.embeddings = {}
        
    async def store_consultation(
        self,
        patient_id: str,
        symptoms: List[str],
        diagnosis: str,
        timestamp: datetime
    ) -> None:
        """
        Store a consultation in patient memory.
        
        Args:
            patient_id: Unique patient identifier
            symptoms: List of symptoms
            diagnosis: Medical diagnosis
            timestamp: When the consultation occurred
        """
        try:
            if patient_id not in self.memory_store:
                self.memory_store[patient_id] = []
            
            consultation = {
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "timestamp": timestamp.isoformat(),
                "embedding": self._create_simple_embedding(symptoms)
            }
            
            self.memory_store[patient_id].append(consultation)
            self.embeddings[patient_id] = self._create_simple_embedding(symptoms)
            
            logger.info(f"Stored consultation for patient {patient_id}")
            
        except Exception as e:
            logger.error(f"Error storing consultation: {str(e)}")
            raise Exception(f"Failed to store consultation: {str(e)}")
    
    async def retrieve_patient_history(
        self,
        patient_id: str,
        current_symptoms: List[str],
        limit: int = 5
    ) -> List[str]:
        """
        Retrieve relevant patient history based on current symptoms.
        
        Args:
            patient_id: Unique patient identifier
            current_symptoms: Current symptoms to match against
            limit: Maximum number of history items to return
            
        Returns:
            List of relevant historical consultations
        """
        try:
            if patient_id not in self.memory_store:
                return []
            
            current_embedding = self._create_simple_embedding(current_symptoms)
            
            # Calculate similarity scores
            consultations = self.memory_store[patient_id]
            scored_consultations = []
            
            for consultation in consultations:
                similarity = self._calculate_similarity(
                    current_embedding,
                    consultation["embedding"]
                )
                scored_consultations.append((similarity, consultation))
            
            # Sort by similarity and return top matches
            scored_consultations.sort(key=lambda x: x[0], reverse=True)
            
            relevant_history = []
            for _, consultation in scored_consultations[:limit]:
                history_item = f"Previous consultation ({consultation['timestamp']}): Symptoms: {', '.join(consultation['symptoms'])}. Diagnosis: {consultation['diagnosis']}"
                relevant_history.append(history_item)
            
            logger.info(f"Retrieved {len(relevant_history)} history items for patient {patient_id}")
            return relevant_history
            
        except Exception as e:
            logger.error(f"Error retrieving patient history: {str(e)}")
            return []
    
    def _create_simple_embedding(self, symptoms: List[str]) -> Dict[str, int]:
        """
        Create a simple embedding for symptoms.
        In production, this would use a proper embedding model.
        """
        embedding = {}
        for symptom in symptoms:
            # Simple word frequency embedding
            words = symptom.lower().split()
            for word in words:
                embedding[word] = embedding.get(word, 0) + 1
        return embedding
    
    def _calculate_similarity(self, embedding1: Dict[str, int], embedding2: Dict[str, int]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        """
        # Get all unique words
        all_words = set(embedding1.keys()) | set(embedding2.keys())
        
        if not all_words:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = 0
        mag1 = 0
        mag2 = 0
        
        for word in all_words:
            val1 = embedding1.get(word, 0)
            val2 = embedding2.get(word, 0)
            dot_product += val1 * val2
            mag1 += val1 * val1
            mag2 += val2 * val2
        
        mag1 = mag1 ** 0.5
        mag2 = mag2 ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get a summary of patient's medical history.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            Summary of patient history
        """
        if patient_id not in self.memory_store:
            return {"consultations": 0, "last_visit": None}
        
        consultations = self.memory_store[patient_id]
        if not consultations:
            return {"consultations": 0, "last_visit": None}
        
        # Get most recent consultation
        latest = max(consultations, key=lambda x: x["timestamp"])
        
        return {
            "consultations": len(consultations),
            "last_visit": latest["timestamp"],
            "common_symptoms": self._get_common_symptoms(consultations)
        }
    
    def _get_common_symptoms(self, consultations: List[Dict[str, Any]]) -> List[str]:
        """Get most common symptoms across consultations."""
        symptom_counts = {}
        for consultation in consultations:
            for symptom in consultation["symptoms"]:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        # Return top 5 most common symptoms
        sorted_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)
        return [symptom for symptom, count in sorted_symptoms[:5]] 