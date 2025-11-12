from app.services.usage_service import UsageService
from faster_whisper import WhisperModel

def get_usage_service() -> UsageService:
    """Dependency to provide the UsageService instance."""
    return UsageService()

_whisper_model = None

def get_whisper_model():
    """Lazy-load the Faster-Whisper model once and reuse it."""
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("small", device="cpu") 
    return _whisper_model