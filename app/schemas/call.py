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
    Sid: str
    ParentCallSid: Optional[str] = ""
    DateCreated: str
    DateUpdated: str
    AccountSid: str
    To: str
    From: str
    PhoneNumber: str
    PhoneNumberSid: str
    Status: str
    StartTime: str
    EndTime: Optional[str] = None
    Duration: Optional[int] = 0
    Price: Optional[float] = 0.0
    Direction: str
    AnsweredBy: Optional[str] = None
    ForwardedFrom: Optional[str] = ""
    CallerName: Optional[str] = ""
    Uri: str
    CustomField: Optional[str] = "N/A"
    RecordingUrl: Optional[str] = ""

    class Config:
        from_attributes = True

class ExternalCallListResponse(BaseModel):
    total: int
    calls: List[ExternalCallDetail]

    class Config:
        from_attributes = True 