from fastapi import HTTPException, UploadFile
from pydub import AudioSegment
import base64
import io

def base64_to_wav_uploadfile(b64_data: str) -> UploadFile:
    """
    Converts any base64-encoded audio (mp3, m4a, webm, wav, etc.)
    into a WAV UploadFile for processing.
    """
    try:
        # Decode the base64 string
        audio_bytes = base64.b64decode(b64_data)

        # Try reading the file with pydub (auto-detects format)
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Convert/export to WAV
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Wrap it as an UploadFile (like a real file upload)
        return UploadFile(filename="converted_audio.wav", file=wav_io)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Audio conversion failed: {str(e)}")



