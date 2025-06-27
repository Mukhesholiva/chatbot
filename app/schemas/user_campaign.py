from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCampaignBase(BaseModel):
    user_id: str
    campaign_id: str

class UserCampaignCreate(UserCampaignBase):
    pass

class UserCampaignUpdate(BaseModel):
    campaign_ids: List[str]

class UserCampaignResponse(UserCampaignBase):
    id: str
    created_at: datetime
    created_by: str
    modified_at: datetime
    modified_by: str
    campaign_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True 