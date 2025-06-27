from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExtractedData(BaseModel):
    cost_rating: Optional[float] = None
    Service_and_repair_time_rating: Optional[float] = None
    time_rating: Optional[float] = None
    Service_and_repair_rating: Optional[float] = None

class Message(BaseModel):
    content: str
    timestamp: str
    role: str

class Transcription(BaseModel):
    messages: List[Message]
    call_id: str

class CallArtifacts(BaseModel):
    category: str
    summary: str
    extracted_data: Optional[str] = Field(None, alias="extracted-data")
    campaign_id: Optional[str] = None
    transcription: Optional[Transcription] = None
    call_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DataExtractionResponse(BaseModel):
    category: str
    summary: str
    extracted_data: str = Field(alias="extracted-data")

    class Config:
        populate_by_name = True

class TranscriptionResponse(BaseModel):
    transcription: Transcription 