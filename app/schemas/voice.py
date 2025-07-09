from pydantic import BaseModel
from typing import Optional

class VoiceResponse(BaseModel):
    source: str = None
    id: int
    voice_id: str
    name: str
    main_accent: Optional[str] = None
    description: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    use_case: Optional[str] = None
    main_preview_url: Optional[str] = None
    next_page_token: Optional[str] = None
    language: Optional[str] = None
    model_id: Optional[str] = None
    lang_accent: Optional[str] = None
    locale: Optional[str] = None
    lang_preview_url: Optional[str] = None

    class Config:
        orm_mode = True
