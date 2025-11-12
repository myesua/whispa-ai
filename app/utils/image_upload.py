import base64
import uuid
import os
from app.services.supabase_client import supabase
from app.config import settings
from fastapi import HTTPException
from typing import Tuple

async def base64_to_proxy_url(base64_str: str) -> Tuple[str, str]:
    try:
        image_bytes = base64.b64decode(base64_str)
        file_id = str(uuid.uuid4()) + ".png" 
        file_path = f"private/{file_id}"

        upload_res = supabase.storage.from_("whis").upload(file_path, image_bytes)

        if not upload_res or getattr(upload_res, "error", None):
            error_message = getattr(upload_res, 'error', 'Unknown error')
            raise HTTPException(status_code=500, detail=f"Upload failed: {error_message}")

        proxy_url = os.path.join(
            settings.api_base_url.rstrip("/"),
            f"v1/attachments/proxy?file_path={file_path}"
        )
        
        return proxy_url, file_path

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process base64: {str(e)}")
        
async def delete_temp_file(file_path: str):
    try:
        res = supabase.storage.from_("whis").remove([file_path])
        if isinstance(res, list) and any(item.get('error') for item in res):
            error_details = ", ".join([item.get('error') for item in res if item.get('error')])
            raise HTTPException(status_code=500, detail=f"Failed to delete temp file: {error_details}")
    except Exception as e:
        print(f"Error deleting temp file {file_path}: {str(e)}")