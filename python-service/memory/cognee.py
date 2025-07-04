import os
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Cognee, with fallback
try:
    from cognee import Cognee
    COGNEE_AVAILABLE = True
except ImportError:
    try:
        import cognee
        COGNEE_AVAILABLE = True
    except ImportError:
        COGNEE_AVAILABLE = False
        logger.warning("Cognee library not available, using fallback storage")

class CogneeMemoryService:
    def __init__(self):
        """Initialize Cognee memory service with actual Cognee library."""
        self.initialized = False
        self.cognee = None
        self.memory_store = {}
        
        if COGNEE_AVAILABLE:
            try:
                # Try different initialization approaches
                try:
                    self.cognee = Cognee()
                    self.initialized = True
                except:
                    # Try alternative initialization
                    import cognee
                    self.cognee = cognee.Cognee()
                    self.initialized = True
                
                logger.info("Cognee memory service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cognee: {e}")
                self.cognee = None
                self.initialized = False
        else:
            logger.info("Using fallback memory storage (Cognee not available)")
    
    async def save_memory(self, patient_id: str, content: str, content_type: str = "symptom") -> Dict[str, Any]:
        """
        Save information to patient memory using Cognee
        """
        try:
            if not self.initialized or not self.cognee:
                # Fallback to simple storage
                return await self._save_memory_fallback(patient_id, content, content_type)
            
            # Create a unique identifier for this memory entry
            memory_id = f"{patient_id}_{content_type}_{datetime.now().timestamp()}"
            
            # Store in Cognee with metadata
            await self.cognee.add(
                content=content,
                metadata={
                    "patient_id": patient_id,
                    "content_type": content_type,
                    "timestamp": datetime.now().isoformat(),
                    "memory_id": memory_id
                }
            )
            
            logger.info(f"Saved memory to Cognee for patient {patient_id}")
            
            return {
                "memory_id": memory_id,
                "status": "saved",
                "patient_id": patient_id,
                "storage": "cognee"
            }
            
        except Exception as e:
            logger.error(f"Error saving memory to Cognee: {e}")
            # Fallback to simple storage
            return await self._save_memory_fallback(patient_id, content, content_type)
    
    async def query_memory(self, patient_id: str, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query patient memory using Cognee vector search
        """
        try:
            if not self.initialized or not self.cognee:
                # Fallback to simple search
                return await self._query_memory_fallback(patient_id, query, limit)
            
            # Search in Cognee with patient filter
            search_results = await self.cognee.search(
                query=query,
                metadata_filter={"patient_id": patient_id},
                limit=limit
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.metadata.get("memory_id", "unknown"),
                    "content": result.content,
                    "content_type": result.metadata.get("content_type", "unknown"),
                    "timestamp": result.metadata.get("timestamp", ""),
                    "similarity_score": result.similarity if hasattr(result, 'similarity') else 0.0
                })
            
            logger.info(f"Queried Cognee memory for patient {patient_id}, found {len(results)} results")
            
            return {
                "patient_id": patient_id,
                "query": query,
                "results": results,
                "count": len(results),
                "storage": "cognee"
            }
            
        except Exception as e:
            logger.error(f"Error querying Cognee memory: {e}")
            # Fallback to simple search
            return await self._query_memory_fallback(patient_id, query, limit)
    
    async def get_patient_history(self, patient_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get complete patient history from Cognee
        """
        try:
            if not self.initialized or not self.cognee:
                # Fallback to simple retrieval
                return await self._get_patient_history_fallback(patient_id, limit)
            
            # Get all memories for this patient
            all_memories = await self.cognee.search(
                query="",  # Empty query to get all
                metadata_filter={"patient_id": patient_id},
                limit=limit
            )
            
            # Group by content type
            history = {
                "consultations": [],
                "symptoms": [],
                "diagnoses": [],
                "other": []
            }
            
            for memory in all_memories:
                content_type = memory.metadata.get("content_type", "other")
                memory_entry = {
                    "id": memory.metadata.get("memory_id", "unknown"),
                    "content": memory.content,
                    "timestamp": memory.metadata.get("timestamp", ""),
                    "similarity_score": memory.similarity if hasattr(memory, 'similarity') else 0.0
                }
                
                if content_type == "consultation":
                    history["consultations"].append(memory_entry)
                elif content_type == "symptom":
                    history["symptoms"].append(memory_entry)
                elif content_type == "diagnosis":
                    history["diagnoses"].append(memory_entry)
                else:
                    history["other"].append(memory_entry)
            
            logger.info(f"Retrieved complete history for patient {patient_id}")
            
            return {
                "patient_id": patient_id,
                "history": history,
                "total_entries": len(all_memories),
                "storage": "cognee"
            }
            
        except Exception as e:
            logger.error(f"Error getting patient history from Cognee: {e}")
            # Fallback to simple retrieval
            return await self._get_patient_history_fallback(patient_id, limit)
    
    async def delete_patient_memory(self, patient_id: str) -> Dict[str, Any]:
        """
        Delete all memories for a patient
        """
        try:
            if not self.initialized or not self.cognee:
                # Fallback to simple deletion
                return await self._delete_patient_memory_fallback(patient_id)
            
            # Get all memories for this patient first
            all_memories = await self.cognee.search(
                query="",
                metadata_filter={"patient_id": patient_id},
                limit=1000  # Large limit to get all
            )
            
            # Delete each memory
            deleted_count = 0
            for memory in all_memories:
                memory_id = memory.metadata.get("memory_id")
                if memory_id:
                    try:
                        await self.cognee.delete(memory_id)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting memory {memory_id}: {e}")
            
            logger.info(f"Deleted {deleted_count} memories for patient {patient_id}")
            
            return {
                "patient_id": patient_id,
                "deleted_count": deleted_count,
                "status": "deleted",
                "storage": "cognee"
            }
            
        except Exception as e:
            logger.error(f"Error deleting patient memory from Cognee: {e}")
            # Fallback to simple deletion
            return await self._delete_patient_memory_fallback(patient_id)
    
    # Fallback methods for when Cognee is not available
    async def _save_memory_fallback(self, patient_id: str, content: str, content_type: str = "symptom") -> Dict[str, Any]:
        """Fallback save method using simple in-memory storage."""
        try:
            if patient_id not in self.memory_store:
                self.memory_store[patient_id] = []
            
            memory_entry = {
                "id": f"mem_{len(self.memory_store[patient_id])}",
                "content": content,
                "content_type": content_type,
                "timestamp": datetime.now().isoformat()
            }
            
            self.memory_store[patient_id].append(memory_entry)
            
            logger.info(f"Saved memory using fallback storage for patient {patient_id}")
            
            return {
                "memory_id": memory_entry["id"],
                "status": "saved",
                "patient_id": patient_id,
                "storage": "fallback"
            }
        except Exception as e:
            logger.error(f"Error in fallback save: {e}")
            return {"memory_id": None, "status": "error", "patient_id": patient_id, "storage": "fallback"}
    
    async def _query_memory_fallback(self, patient_id: str, query: str, limit: int = 5) -> Dict[str, Any]:
        """Fallback query method using simple text matching."""
        try:
            if patient_id not in self.memory_store:
                return {
                    "patient_id": patient_id,
                    "query": query,
                    "results": [],
                    "count": 0,
                    "storage": "fallback"
                }
            
            # Simple text matching
            results = []
            for memory in self.memory_store[patient_id]:
                if query.lower() in memory["content"].lower():
                    results.append(memory)
                    if len(results) >= limit:
                        break
            
            logger.info(f"Queried memory using fallback storage for patient {patient_id}")
            
            return {
                "patient_id": patient_id,
                "query": query,
                "results": results,
                "count": len(results),
                "storage": "fallback"
            }
        except Exception as e:
            logger.error(f"Error in fallback query: {e}")
            return {
                "patient_id": patient_id,
                "query": query,
                "results": [],
                "count": 0,
                "storage": "fallback"
            }
    
    async def _get_patient_history_fallback(self, patient_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fallback method to get patient history."""
        try:
            if patient_id not in self.memory_store:
                return {
                    "patient_id": patient_id,
                    "history": {"consultations": [], "symptoms": [], "diagnoses": [], "other": []},
                    "total_entries": 0,
                    "storage": "fallback"
                }
            
            memories = self.memory_store[patient_id][:limit]
            
            history = {
                "consultations": [],
                "symptoms": [],
                "diagnoses": [],
                "other": []
            }
            
            for memory in memories:
                content_type = memory.get("content_type", "other")
                if content_type == "consultation":
                    history["consultations"].append(memory)
                elif content_type == "symptom":
                    history["symptoms"].append(memory)
                elif content_type == "diagnosis":
                    history["diagnoses"].append(memory)
                else:
                    history["other"].append(memory)
            
            return {
                "patient_id": patient_id,
                "history": history,
                "total_entries": len(memories),
                "storage": "fallback"
            }
        except Exception as e:
            logger.error(f"Error in fallback history retrieval: {e}")
            return {
                "patient_id": patient_id,
                "history": {"consultations": [], "symptoms": [], "diagnoses": [], "other": []},
                "total_entries": 0,
                "storage": "fallback"
            }
    
    async def _delete_patient_memory_fallback(self, patient_id: str) -> Dict[str, Any]:
        """Fallback method to delete patient memory."""
        try:
            if patient_id in self.memory_store:
                deleted_count = len(self.memory_store[patient_id])
                del self.memory_store[patient_id]
                
                logger.info(f"Deleted {deleted_count} memories using fallback storage for patient {patient_id}")
                
                return {
                    "patient_id": patient_id,
                    "deleted_count": deleted_count,
                    "status": "deleted",
                    "storage": "fallback"
                }
            else:
                return {
                    "patient_id": patient_id,
                    "deleted_count": 0,
                    "status": "not_found",
                    "storage": "fallback"
                }
        except Exception as e:
            logger.error(f"Error in fallback deletion: {e}")
            return {
                "patient_id": patient_id,
                "deleted_count": 0,
                "status": "error",
                "storage": "fallback"
            }