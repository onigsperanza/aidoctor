class CogneeMemoryService:
    async def save_memory(self, patient_id: str, content: str, content_type: str = "symptom"):
        # TODO: Implement memory saving logic
        return {"memory_id": "simulated_id"}

    async def query_memory(self, patient_id: str, query: str, limit: int = 5):
        # TODO: Implement memory query logic
        return ["Simulated memory result"] 