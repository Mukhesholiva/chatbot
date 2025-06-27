from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class CallRatingBase(BaseModel):
    call_id: str
    rating: float
    submitted_by: str
    submitted_at: Optional[datetime] = None

    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class CallRatingCreate(CallRatingBase):
    pass

class CallRatingResponse(CallRatingBase):
    id: str
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True 