from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.audio_service import AudioService 
from prometheus_client import Counter, Histogram
import time

router = APIRouter()

TRANSCRIPTION_ENDPOINT_COUNT = Counter(
    'transcription_endpoint_total', 'Total transcription attempts processed',
    ['status', 'provider']
)

TRANSCRIPTION_LATENCY_SECONDS = Histogram(
    'transcription_latency_seconds', 'Transcription endpoint latency (seconds)',
    ['provider']
)

@router.post("/transcribe/old", summary="Upload and transcribe audio file using Gemini")
async def process_audio(audio_file: UploadFile = File(...)):
    PROVIDER_LABEL = 'gemini' 
    start_time = time.time()
    
    try:
        service = AudioService()
        text = await service.transcribe_audio_with_gemini(audio_file) 
        
        low = text.lower() if isinstance(text, str) else ""
        
        if "error" in low or "fail" in low or not text:
            TRANSCRIPTION_ENDPOINT_COUNT.labels(status='fail', provider=PROVIDER_LABEL).inc()
            raise HTTPException(status_code=400, detail=f"Transcription failed or was empty: {text}")
            
        TRANSCRIPTION_ENDPOINT_COUNT.labels(status='success', provider=PROVIDER_LABEL).inc()
        return {"success": True, "audio_text": text}  

    except HTTPException:
        raise
    except Exception as e:
        TRANSCRIPTION_ENDPOINT_COUNT.labels(status='error', provider=PROVIDER_LABEL).inc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error during transcription: {str(e)}")

    finally:
        end_time = time.time()
        process_time = end_time - start_time
        TRANSCRIPTION_LATENCY_SECONDS.labels(provider=PROVIDER_LABEL).observe(process_time)


@router.post("/transcribe", summary="Upload and transcribe audio file using Faster-Whisper")
async def process_audio_faster_whisper(audio_file: UploadFile = File(...)):
    PROVIDER_LABEL = 'faster_whisper' 
    start_time = time.time()
    
    try:
        service = AudioService()
        text = await service.transcribe_audio_with_faster_whisper(audio_file) 
        
        if not text or text.lower().startswith("error transcribing audio"):
            TRANSCRIPTION_ENDPOINT_COUNT.labels(status='fail', provider=PROVIDER_LABEL).inc()
            raise HTTPException(status_code=400, detail=f"Transcription failed or was empty: {text}")
            
        TRANSCRIPTION_ENDPOINT_COUNT.labels(status='success', provider=PROVIDER_LABEL).inc()
        return {"success": True, "audio_text": text}  

    except HTTPException:
        raise
    except Exception as e:
        TRANSCRIPTION_ENDPOINT_COUNT.labels(status='error', provider=PROVIDER_LABEL).inc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error during transcription: {str(e)}")

    finally:
        end_time = time.time()
        process_time = end_time - start_time
        TRANSCRIPTION_LATENCY_SECONDS.labels(provider=PROVIDER_LABEL).observe(process_time)