from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_notes():
    # Test case for generating notes from OCR and audio input
    image_data = "data:image/png;base64,..."  # Replace with valid base64 image data
    audio_data = "base64_audio_data..."  # Replace with valid base64 audio data

    response = client.post("/ocr", json={"image": image_data})
    assert response.status_code == 200
    ocr_result = response.json()
    assert ocr_result['success'] is True
    extracted_text = ocr_result['text']

    response = client.post("/audio", json={"audio": audio_data})
    assert response.status_code == 200
    audio_result = response.json()
    assert audio_result['success'] is True
    voice_text = audio_result['text']

    response = client.post("/notes", json={"ocr_text": extracted_text, "voice_text": voice_text})
    assert response.status_code == 200
    notes_result = response.json()
    assert notes_result['success'] is True
    assert 'notes' in notes_result

def test_invalid_image():
    # Test case for handling invalid image input
    invalid_image_data = "invalid_base64_data"
    response = client.post("/ocr", json={"image": invalid_image_data})
    assert response.status_code == 400

def test_invalid_audio():
    # Test case for handling invalid audio input
    invalid_audio_data = "invalid_base64_data"
    response = client.post("/audio", json={"audio": invalid_audio_data})
    assert response.status_code == 400