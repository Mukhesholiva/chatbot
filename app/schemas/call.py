from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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
    is_active: bool = True

    class Config:
        from_attributes = True 