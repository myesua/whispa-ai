from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.audio import router as audio_router

app = FastAPI()
app.include_router(audio_router)

client = TestClient(app)

def test_audio_processing():
    audio_file_path = "tests/test_audio.wav"  # Path to a sample audio file for testing
    with open(audio_file_path, "rb") as audio_file:
        response = client.post("/audio/", files={"file": audio_file})
    
    assert response.status_code == 200
    assert "text" in response.json()  # Ensure the response contains the expected text field
    assert isinstance(response.json()["text"], str)  # Ensure the text is a string

def test_audio_processing_invalid_file():
    response = client.post("/audio/", files={"file": ("invalid.txt", b"not audio data")})
    
    assert response.status_code == 400  # Expect a bad request for invalid audio file
    assert "detail" in response.json()  # Ensure the response contains an error detail