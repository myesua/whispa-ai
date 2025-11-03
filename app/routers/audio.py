# from fastapi import APIRouter, HTTPException, Request
# from app.services.audio_service import AudioService

# router = APIRouter()

# @router.post("/transcribe", summary="Process base64 audio payload")
# async def process_audio(request: Request = None):
#     try:
#         service = AudioService()
#         req_data = await request.json()
#         b64 = req_data.get('audio') or req_data.get('audio_data')
#         # b64 = b64.split(',')[1] if ',' in b64 else b64
#         file_suffix = req_data.get('audio_extension') or '.webm'
#         if not b64:
#             raise HTTPException(status_code=400, detail="No audio provided")
#         text = service.process_audio(b64, file_suffix)
#         low = text.lower() if isinstance(text, str) else ""
#         if any(k in low for k in ("could not", "audio could not", "invalid audio", "invalid audio file", "audio could not be understood", "invalid")):
#             raise HTTPException(status_code=400, detail=text)
#         return {"success": True, "audio_text": text}  

#     except HTTPException:
#         # Preserve HTTPExceptions raised intentionally above
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# routers/audio.py

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.audio_service import AudioService # Update the import path if needed

router = APIRouter()

@router.post("/transcribe", summary="Upload and transcribe audio file using Gemini")
async def process_audio(audio_file: UploadFile = File(...)): # Expect a direct file upload
    """
    Accepts a binary audio file upload and returns a transcription using the Gemini API.
    """
    try:
        service = AudioService()
        
        # Call the new service method
        text = await service.transcribe_audio_with_gemini(audio_file)
        
        low = text.lower() if isinstance(text, str) else ""
        
        # Robust check for transcription failure or generic errors
        if "error" in low or "fail" in low or not text:
            raise HTTPException(status_code=400, detail=f"Transcription failed or was empty: {text}")
            
        return {"success": True, "audio_text": text}  

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during transcription: {str(e)}")
