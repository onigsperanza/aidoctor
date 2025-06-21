from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import process
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Doctor Assistant",
    description="Full-stack AI medical assistant with speech transcription, EMR extraction, and diagnostic suggestions",
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
    return {"message": "AI Doctor Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 