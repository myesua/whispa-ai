from typing import Optional
from app.services.llm_client import LLMClient
from app.services.supabase_client import supabase
from app.utils.extract_title_body import extract_title_and_body
import uuid

llm = LLMClient()

async def persist_note_if_allowed(
    user_id: str,
    voice_text: Optional[str],
    title: Optional[str],
    body: Optional[str],
    privacy_mode: bool
):
    """
    Persist note to DB only when privacy_mode is False.
    Returns inserted row metadata or None if not stored.
    """
    if privacy_mode:
        # Do not persist user content
        return None

    payload = {
        "user_id": user_id,
        "voice_text": voice_text,
        "title": title,
        "body": body,
        "privacy_mode": False
    }

    res = supabase.table("notes").insert(payload).execute()
    # supabase-py can return dict with 'data' and 'error'
    if isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Supabase error: {res['error']}")
    return res.get("data") if isinstance(res, dict) else getattr(res, "data", None)


class NotesService:
    def __init__(self):
        self.llm = llm
    async def generate_notes(
        self,
        image_base64: Optional[str] = None,
        voice_text: Optional[str] = None,
        provided_text: Optional[str] = None,
        session_id: Optional[str] = None,
        privacy_mode: bool = True,
        user_id: Optional[str] = None
    ):
        if image_base64 and image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
        llm_resp = await self.llm.analyze_multimodal(image_base64=image_base64, transcription=voice_text, text=provided_text)
        markdown = llm_resp["response"]
        title, body = extract_title_and_body(markdown)
       
        saved = None
        if user_id and not privacy_mode:
            saved = await persist_note_if_allowed(user_id=user_id, voice_text=voice_text, title=title, body=body, privacy_mode=privacy_mode)
        return {"title": title, "content": body, "stored": bool(saved), "session_id": session_id or str(uuid.uuid4())}