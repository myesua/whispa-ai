import base64
import tempfile
from faster_whisper import WhisperModel

# ✅ Global model cache (loaded once)
_whisper_model = None

def get_whisper_model():
    """Lazy-load the Faster-Whisper model once and reuse it."""
    global _whisper_model
    if _whisper_model is None:
        # model size: tiny, base, small, medium, large-v2
        _whisper_model = WhisperModel("small", device="cpu")  # or "cuda" for GPU
    return _whisper_model


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
            segments, info = model.transcribe(tmp.name, language="en", # Assuming you are speaking English
                task="transcribe")
            text = " ".join([seg.text for seg in segments]).strip()

            return text or "No speech detected"

    except Exception as e:
        return f"Error transcribing audio: {str(e)}"
