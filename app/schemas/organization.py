from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    code: Optional[str] = None
    name: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime
    created_by: str
    modified_at: datetime = Field(alias="modified_date")
    modified_by: str = Field(alias="last_modified_by")

    class Config:
        from_attributes = True
        populate_by_name = True 