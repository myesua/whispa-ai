from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import base64
import io
import uuid
from PIL import Image
import pytesseract
from app.services.ocr_service import OCRService

router = APIRouter()

class OCRRequest(BaseModel):
    image: str
    session_id: Optional[str] = None

@router.post("/ocr")
async def process_ocr(request: Request):
    """Process an image with OCR and Gemini Vision."""
    try:
        # Get request data
        request_data = await request.json()
        # Extract image data from base64 string
        image_data = request_data.get("image")

        return OCRService.process_image(image_data)
    
    except HTTPException:
        # Preserve HTTPExceptions raised above (bad request, etc.)
        raise
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))