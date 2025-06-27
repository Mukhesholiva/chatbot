from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class CallBase(BaseModel):
    to_number: str
    dynamic_variables: Dict[str, Any]
    metadata: Dict[str, str] = Field(alias="call_metadata")
    campaign_id: str

    class Config:
        populate_by_name = True

class CallCreate(CallBase):
    pass

class CallResponse(CallBase):
    id: str
    call_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExternalCallDetail(BaseModel):
    From: str
    Direction: str
    CallerName: Optional[str] = None
    RecordingUrl: Optional[str] = None
    ParentCallSid: Optional[str] = None
    EndTime: str
    Uri: str
    Status: str
    campaign_id: str
    PhoneNumberSid: str
    call_id: str
    DateUpdated: str
    Duration: Optional[int] = None
    AccountSid: str
    Price: Optional[float] = None
    AnsweredBy: Optional[str] = None
    To: str
    DateCreated: str
    StartTime: str
    ForwardedFrom: Optional[str] = None

    class Config:
        from_attributes = True

class ExternalCallListResponse(BaseModel):
    items: List[ExternalCallDetail]
    page_size: int
    has_more: bool
    next_cursor: Optional[str] = None

    class Config:
        from_attributes = True

class CallRecordingResponse(BaseModel):
    url: str
    expiresAt: str

    class Config:
        from_attributes = True 