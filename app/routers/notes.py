from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from app.services.notes_service import NotesService, persist_note_if_allowed
from app.services.supabase_client import supabase
from pydantic import BaseModel
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Use server supabase client to validate token and return user id
    token = credentials.credentials
    user_resp = supabase.auth.get_user(token)
    if user_resp.error or not getattr(user_resp, "user", None):
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_resp.data.user.id


class NotePersistPayload(BaseModel):
    ocr_text: Optional[str] = None
    voice_text: Optional[str] = None
    generated_notes: Optional[str] = None
    privacy_mode: Optional[bool] = True


@router.post("/", summary="Generate notes from image and optional audio")
async def generate_notes(request: Request, user: dict = Depends(get_current_user)):
    try:
        try:
            data = await request.json()
        except Exception:
            data = {}
        image_b64 = data.get("image_b64")
        voice_text = data.get("voice_text")
        session_id = data.get("session_id")
        provided_text = data.get("provided_text")
        privacy_mode = data.get("privacy_mode", True)

        service = NotesService()
    
        result = await service.generate_notes(image_base64=image_b64,voice_text=voice_text, provided_text=provided_text, session_id=session_id, privacy_mode=privacy_mode, user_id=user.get("id"))
        return {"success": True, "notes": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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