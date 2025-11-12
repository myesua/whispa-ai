import mimetypes
from app.services.supabase_client import supabase
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import Response
from typing import Union

router = APIRouter(prefix="/attachments", tags=["attachments"])

@router.api_route('/proxy', methods=["GET", "HEAD"], summary="Securely proxies private Supabase images for Linear ingestion.")
async def linear_image_proxy(file_path: str = Query(..., description="The internal path to the private Supabase file.")):
    
    if not file_path.startswith("private/"):
        raise HTTPException(status_code=403, detail="Invalid file path format.")

    try:
        res: Union[bytes, dict] = supabase.storage.from_("whis").download(file_path)

        if isinstance(res, dict) and res.get('error'):
            error_message = res['error'].get('message') or str(res['error'])
            status_code = res.get('status_code', 500)
            
            if status_code == 404:
                raise HTTPException(status_code=404, detail=f"File not found on Supabase: {error_message}")
            if status_code == 403:
                raise HTTPException(status_code=403, detail=f"Supabase Access Denied: {error_message}")
            
            raise HTTPException(status_code=status_code, detail=f"Supabase Storage error: {error_message}")
            
        elif isinstance(res, bytes):
            image_bytes = res
        
        else: 
            raise HTTPException(status_code=500, detail="Supabase download failed with unexpected response type.")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith('image/'):
            mime_type = 'image/png'

        return Response(content=image_bytes, media_type=mime_type)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy internal error: {str(e)}")