import os
from typing import Dict, Any, List, Optional
import json

class CogneeMemoryService:
    def __init__(self):
        # For now, use a simple in-memory storage
        # In production, you would use a proper vector database
        self.memory_store = {}
    
    async def save_memory(self, patient_id: str, content: str, content_type: str = "symptom") -> Dict[str, Any]:
        """
        Save information to patient memory
        """
        try:
            if patient_id not in self.memory_store:
                self.memory_store[patient_id] = []
            
            memory_entry = {
                "id": f"mem_{len(self.memory_store[patient_id])}",
                "content": content,
                "content_type": content_type,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            self.memory_store[patient_id].append(memory_entry)
            
            return {
                "memory_id": memory_entry["id"],
                "status": "saved",
                "patient_id": patient_id
            }
        except Exception as e:
            print(f"Error saving memory: {e}")
            return {"memory_id": None, "status": "error", "patient_id": patient_id}
    
    async def query_memory(self, patient_id: str, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query patient memory
        """
        try:
            if patient_id not in self.memory_store:
                return {
                    "patient_id": patient_id,
                    "query": query,
                    "results": [],
                    "count": 0
                }
            
            # Simple text matching for now
            # In production, you would use vector similarity search
            results = []
            for memory in self.memory_store[patient_id]:
                if query.lower() in memory["content"].lower():
                    results.append(memory)
                    if len(results) >= limit:
                        break
            
            return {
                "patient_id": patient_id,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            print(f"Error querying memory: {e}")
            return {
                "patient_id": patient_id,
                "query": query,
                "results": [],
                "count": 0
            } 