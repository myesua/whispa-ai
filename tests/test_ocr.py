from fastapi.testclient import TestClient
from app.main import app
import base64
import os

client = TestClient(app)

def test_process_ocr_valid_image():
    # Prepare a valid base64 encoded image
    with open(os.path.join(os.path.dirname(__file__), 'test_image.png'), 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        response = client.post("/", json={"image": f"data:image/png;base64,{encoded_string}"})
    
    assert response.status_code == 200
    assert response.json().get('success') is True
    assert 'image_data' in response.json()

def test_process_ocr_invalid_image():
    # Test with invalid base64 string
    response = client.post("/", json={"image": "invalid_base64_string"})
    
    assert response.status_code == 500
    assert 'detail' in response.json()

def test_process_ocr_no_image():
    # Test with no image provided
    response = client.post("/", json={})
    
    assert response.status_code == 500
    assert 'detail' in response.json()