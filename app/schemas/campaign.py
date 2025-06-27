from pydantic import BaseModel
from typing import Optional, Dict, Any
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

class CampaignBase(BaseModel):
    name: str
    direction: str
    inbound_number: Optional[str] = ""
    caller_id_number: Optional[str] = ""
    state: str
    version: int = 0
    llm: LLMConfig
    tts: TTSConfig
    stt: Dict[str, Any] = {}
    timezone: str
    post_call_actions: Dict[str, Any]
    live_actions: list = []
    callback_endpoint: str = ""
    retry: Dict[str, Any] = {}
    account_id: str
    org_id: Optional[str] = None
    created_by: int
    is_active: bool = True
    telephonic_provider: str
    knowledge_base: KnowledgeBase

class CampaignCreate(CampaignBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    username: Optional[str] = None
    password: Optional[str] = None
    allow_interruption: Optional[bool] = True
class CampaignUpdate(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime
    allow_interruption: Optional[bool] = True

class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 