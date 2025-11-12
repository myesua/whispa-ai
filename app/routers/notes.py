from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from app.services.notes_service import NotesService, persist_note_if_allowed
# from app.services.supabase_client import supabase
from pydantic import BaseModel
from app.middleware.auth import get_current_user
import uuid
from fastapi.responses import StreamingResponse
from app.dependencies import get_usage_service
from app.services.usage_service import UsageService

router = APIRouter()
security = HTTPBearer()


# async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     # Use server supabase client to validate token and return user id
#     token = credentials.credentials
#     user_resp = supabase.auth.get_user(token)
#     if user_resp.error or not getattr(user_resp, "user", None):
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return user_resp.data.user.id


class NotePersistPayload(BaseModel):
    ocr_text: Optional[str] = None
    voice_text: Optional[str] = None
    generated_notes: Optional[str] = None
    privacy_mode: Optional[bool] = True


@router.post("/generate/stream", summary="Generate notes from image/audio and stream response")
async def generate_notes_stream(request: Request, user: dict = Depends(get_current_user), usage_service: UsageService = Depends(get_usage_service)):
    await usage_service.check_and_increment_note_count(user_id=user.get("id"))
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body provided.")
    
    images_b64 = data.get("images_b64")
    voice_text = data.get("voice_text")
    provided_text = data.get("provided_text")
    qa_type = data.get("qa_type")
    
    service = NotesService()
    
    try:
        stream_generator = service.generate_notes_stream(
            images_base64=images_b64, 
            voice_text=voice_text, 
            provided_text=provided_text,
            qa_type=qa_type
        )
    except HTTPException as e:
        raise e
    return StreamingResponse(
        stream_generator, 
        media_type="text/markdown"
)

@router.post("/save_notes", summary="Persist the final generated notes")
async def save_final_notes(request: Request, user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body provided.")
        
    # Client sends the assembled markdown back to be saved
    final_markdown = data.get("final_markdown")
    voice_text = data.get("voice_text") # Original transcription text
    session_id = data.get("session_id") or str(uuid.uuid4())
    privacy_mode = data.get("privacy_mode", True)
    
    if not final_markdown:
        raise HTTPException(status_code=400, detail="Final markdown content is required for saving.")

    service = NotesService()
    result = await service.process_final_notes(
        markdown_text=final_markdown,
        voice_text=voice_text,
        user_id=user.get("id"),
        privacy_mode=privacy_mode,
        session_id=session_id
    )
    
    return {"success": True, "notes": result}


# @router.post("/generate", summary="Generate notes from image and optional audio")
# async def generate_notes(request: Request, user: dict = Depends(get_current_user), usage_service: UsageService = Depends(get_usage_service)):
#     await usage_service.check_and_increment_note_count(user_id=user.get("id"))
#     try:
#         try:
#             data = await request.json()
#         except Exception:
#             data = {}
#         images_b64 = data.get("images_b64")
#         voice_text = data.get("voice_text")
#         session_id = data.get("session_id") or str(uuid.uuid4())
#         provided_text = data.get("provided_text")
#         privacy_mode = data.get("privacy_mode", True)

#         service = NotesService()
    
#         result = await service.generate_notes(images_base64=images_b64,voice_text=voice_text, provided_text=provided_text, session_id=session_id, privacy_mode=privacy_mode, user_id=user.get("id"))
#         return {"success": True, "notes": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# renamed route to avoid duplicate path
@router.post("/store", summary="Persist a generated note (honors privacy_mode)")
async def store_note(payload: NotePersistPayload, user: dict = Depends(get_current_user)):
    """Persist note to Supabase when the user's privacy_mode is False.
    Returns whether the note was stored and the stored row (or None).
    """
    privacy_mode = payload.privacy_mode if payload.privacy_mode is not None else True
    saved = await persist_note_if_allowed(
        user_id=user.get("id"),
        ocr_text=payload.ocr_text,
        voice_text=payload.voice_text,
        generated_notes=payload.generated_notes,
        privacy_mode=privacy_mode
    )
    return {"stored": bool(saved), "note": saved}