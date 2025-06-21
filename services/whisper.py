import whisper
import httpx
import tempfile
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_name: str = "base"):
        """Initialize Whisper service with specified model."""
        self.model = whisper.load_model(model_name)
        logger.info(f"Whisper model {model_name} loaded successfully")
    
    async def transcribe(self, audio_url: str) -> str:
        """
        Transcribe audio from URL using Whisper.
        
        Args:
            audio_url: URL to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                
                try:
                    # Transcribe using Whisper
                    result = self.model.transcribe(temp_file_path)
                    transcription = result["text"].strip()
                    
                    logger.info(f"Successfully transcribed audio from {audio_url}")
                    logger.info(f"Transcription length: {len(transcription)} characters")
                    
                    return transcription
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
        except Exception as e:
            logger.error(f"Error transcribing audio from {audio_url}: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe audio from local file path.
        
        Args:
            file_path: Path to local audio file
            
        Returns:
            Transcribed text
        """
        try:
            result = self.model.transcribe(file_path)
            transcription = result["text"].strip()
            
            logger.info(f"Successfully transcribed audio file: {file_path}")
            logger.info(f"Transcription length: {len(transcription)} characters")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio file {file_path}: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}") 