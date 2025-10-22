from pydantic import BaseModel
from typing import Optional, List

class OCRResponse(BaseModel):
    success: bool
    text: Optional[str] = None
    image_data: Optional[str] = None

class AudioRequest(BaseModel):
    audio_data: str
    session_id: Optional[str] = None

class AudioResponse(BaseModel):
    success: bool
    text: Optional[str] = None

class NotesRequest(BaseModel):
    ocr_text: str
    audio_text: str
    session_id: Optional[str] = None

class NotesResponse(BaseModel):
    success: bool
    notes: str
    session_id: Optional[str] = None

class CombinedNotesResponse(BaseModel):
    success: bool
    notes: List[str]
    session_id: Optional[str] = None