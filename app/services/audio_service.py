import asyncio
from fastapi import UploadFile, HTTPException
from google.genai import Client
from google.genai.errors import APIError 
from typing import Optional
from app.config import settings
from app.utils.transcribe_audio import transcribe_base64_audio
import aiofiles
import os
import tempfile
class AudioService:
    def __init__(self):
        self.client = Client(api_key=settings.gemini_api_key) 
        self.aclient = self.client.aio
        self.model_name = "gemini-2.5-flash"
        self.transcribe_base64_audio = transcribe_base64_audio
        self.gemini_key = settings.gemini_api_key
    def process_audio(self, audio_base64: str, file_suffix: str) -> str:
        try:
            text = self.transcribe_base64_audio(audio_base64, file_suffix)
            return text
        except Exception as e:
            return f"Invalid audio string: {str(e)}"

    async def transcribe_audio_with_gemini(self, audio_file: UploadFile) -> str:
        """
        Reads audio bytes, writes them to a temp file, uploads the file 
        using the path, transcribes, and ensures cleanup of both the 
        Gemini file and the local temp file.
        """
    
        audio_bytes = await audio_file.read()
        mime_type = audio_file.content_type
    
        if not audio_bytes or not mime_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid or empty audio file provided.")

        audio_file_upload = None
        temp_file_path = None

        try:
            suffix = "." + mime_type.split("/")[-1] if "/" in mime_type else ".tmp"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                temp_file_path = tmp.name

            async with aiofiles.open(temp_file_path, 'wb') as f:
                await f.write(audio_bytes)

            config = {
                'mime_type': mime_type
            }
                
            audio_file_upload = await self.aclient.files.upload(
                file=temp_file_path, 
                config=config  
            )
        
            prompt = [
                "Transcribe this audio file accurately. Include all punctuation and capitalization.",
                audio_file_upload 
            ]
        
            response = await self.aclient.models.generate_content(
                model=self.model_name, 
                contents=prompt
            )
            transcribed_text = response.text.replace('\n', ' ')
        
            return ' '.join(transcribed_text.split()).strip()

        except HTTPException:
            raise
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"Gemini API error during transcription: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error during transcription: {str(e)}")

        finally:
            if audio_file_upload:
                await self.aclient.files.delete(
                    name=audio_file_upload.name 
                )
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path) #