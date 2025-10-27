from fastapi import APIRouter, HTTPException, Request
from app.services.audio_service import AudioService

router = APIRouter()

@router.post("/transcribe", summary="Process base64 audio payload")
async def process_audio(request: Request = None):
    try:
        service = AudioService()
        req_data = await request.json()
        b64 = req_data.get('audio') or req_data.get('audio_data')
        b64 = b64.split(',')[1] if ',' in b64 else b64
        if not b64:
            raise HTTPException(status_code=400, detail="No audio provided")
        text = service.process_audio(b64)
        low = text.lower() if isinstance(text, str) else ""
        if any(k in low for k in ("could not", "audio could not", "invalid audio", "invalid audio file", "audio could not be understood", "invalid")):
            raise HTTPException(status_code=400, detail=text)
        return {"success": True, "audio_text": text}  

    except HTTPException:
        # Preserve HTTPExceptions raised intentionally above
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

