from app.utils.transcribe_audio import transcribe_base64_audio

class AudioService:
    def __init__(self):
        self.transcribe_base64_audio = transcribe_base64_audio

    def process_audio(self, audio_base64: str) -> str:
        try:
            text = self.transcribe_base64_audio(audio_base64)
            return text
        except Exception as e:
            return f"Invalid audio string: {str(e)}"