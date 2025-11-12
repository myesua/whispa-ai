import base64
import tempfile
from app.dependencies import get_whisper_model 

def transcribe_file_path(audio_path: str) -> str:
    try:
        model = get_whisper_model()
        
        segments, info = model.transcribe(audio_path, language="en",
            task="translate")
            
        text = " ".join([seg.text for seg in segments]).strip()

        return text or "No speech detected"

    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def transcribe_base64_audio(audio_base64: str, file_suffix: str) -> str:
    """
    Decode base64 audio (MP3, WAV, etc.) and transcribe using local Faster-Whisper.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()

            model = get_whisper_model()
            segments, info = model.transcribe(tmp.name, language="en",
                task="translate")
            text = " ".join([seg.text for seg in segments]).strip()

            return text or "No speech detected"

    except Exception as e:
        return f"Error transcribing audio: {str(e)}"
