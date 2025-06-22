class MedicalExtractionService:
    async def extract_medical_info(self, text: str, language: str = "es"):
        # TODO: Implement extraction logic using MedCAT, SNOMED, etc.
        return {"entities": ["Entidad simulada"]} 