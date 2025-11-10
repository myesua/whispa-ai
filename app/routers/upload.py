from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.linear_service import LinearService
import uuid

router = APIRouter()

class ImageUploadPayload(BaseModel):
    image_base64: str
    file_name: str 

@router.post("/upload_image_to_linear", summary="Uploads one Base64 image directly to Linear as an attachment")
async def upload_image_to_linear(
    payload: ImageUploadPayload, 
    user: dict = Depends(get_current_user)
):
    linear_service = LinearService()
    
    try:
        upload_result = linear_service.upload_attachment(
            file_name=payload.file_name,
            image_base64=payload.image_base64
        )
        return {
            "success": True, 
            "attachment_url": upload_result.get("url"),
            "attachment_id": upload_result.get("attachmentId"),
            "user_id": user.get("id")
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error during Linear attachment upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload attachment to Linear.")