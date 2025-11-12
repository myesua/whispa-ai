import base64
import uuid
from app.services.supabase_client import supabase
from fastapi import HTTPException

async def base64_to_temp_url(base64_str: str, expires_in: int = 300) -> str:
    """
    Convert base64 image string to a short-lived Supabase signed URL.

    Args:
        base64_str: Image in base64 (without 'data:image/png;base64,' prefix)
        expires_in: Expiration in seconds (default 180s)
    Returns:
        Temporary signed URL
    """
    try:
        image_bytes = base64.b64decode(base64_str)
        file_id = str(uuid.uuid4()) + ".jpg"
        path = f"private/{file_id}"

        upload_res = supabase.storage.from_("temp").upload(path, image_bytes)

        if not upload_res or getattr(upload_res, "error", None):
            raise HTTPException(status_code=500, detail=f"Upload failed: {getattr(upload_res, 'error', 'Unknown error')}")

        # Create short-lived signed URL
        signed = supabase.storage.from_("temp").create_signed_url(path, expires_in)
        if not signed or not signed.get("signedURL"):
            raise HTTPException(status_code=500, detail="Failed to generate signed URL")
        return signed["signedURL"]

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process base64: {str(e)}")
        
async def delete_temp_file(file_path: str):
    """
    Delete a temporary file from Supabase storage.

    Args:
        file_path: Path of the file to delete
    """
    try:
        res = supabase.storage.from_("temp").remove([file_path])
        if res.get("error"):
            raise HTTPException(status_code=500, detail=f"Failed to delete temp file: {res['error']}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting temp file: {str(e)}")