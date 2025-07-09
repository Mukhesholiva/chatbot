from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class LLMConfig(BaseModel):
    model: str
    prompt: str
    provider: str
    promptJson: Dict[str, Any]
    temperature: str
    useProxyLlm: bool
    useEmbeddings: bool
    initialMessage: str
    maxCallDuration: int
    UseStructuredPrompt: bool

class TTSConfig(BaseModel):
    gender: str
    language: str
    voice_id: str

class KnowledgeBase(BaseModel):
    url: str
    file: Optional[str] = None

class SpeechSetting(BaseModel):
    interruption: Dict[str, Any]
    ambient_sound: Dict[str, Any]

class CampaignBase(BaseModel):
    name: str
    direction: str = "OUTBOUND"
    inbound_number: str = ""
    caller_id_number: str = ""
    state: str = "TRIAL"
    version: Union[str, int] = "0"
    llm: Dict[str, Any] = {}
    tts: Dict[str, Any] = {}
    stt: Dict[str, Any] = {}
    timezone: str = "UTC"
    post_call_actions: Dict[str, Any] = {}
    live_actions: List[Dict[str, Any]] = []
    callback_endpoint: str = ""
    retry: Dict[str, Any] = {}
    account_id: str = ""
    telephonic_provider: str = "exotel"
    allow_interruption: bool = True
    speech_setting: Dict[str, Any] = {}
    knowledge_base: Dict[str, Any] = {}
    id: Optional[str] = None
    org_id: Optional[str] = None
    created_by: Optional[str] = None
    is_active: bool = True

class CampaignCreate(CampaignBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    username: Optional[str] = None
    password: Optional[str] = None
    created_by: Optional[int] = None
    knowledge_base: Optional[KnowledgeBase] = None

class CampaignUpdate(CampaignBase):
    created_at: datetime
    updated_at: datetime

class CampaignResponse(CampaignBase):
    created_at: datetime
    updated_at: datetime
    llm: Dict[str, Any] = {}
    tts: Dict[str, Any] = {}
    stt: Dict[str, Any] = {}
    retry: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }