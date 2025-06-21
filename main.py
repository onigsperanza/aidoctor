from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import process
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Doctor Assistant - Servicio Médico en Español",
    description="Asistente médico de IA de pila completa con transcripción de voz, extracción de datos EMR estructurados y sugerencias de diagnóstico usando LLMs",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(process.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "AI Doctor Assistant - Servicio Médico en Español", 
        "version": "1.0.0",
        "language": "es",
        "default_model": "gpt-4"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-01T00:00:00Z",
        "language": "es",
        "services": {
            "openai": "available",
            "whisper": "available",
            "mlflow": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 