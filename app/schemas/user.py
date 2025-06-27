from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    mobile_number: str
    role_id: Optional[str] = None
    status: str = "active"
    organization_id: Optional[str] = None
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str
    created_by: Optional[str] = "system"
    modified_by: Optional[str] = "system"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    status: Optional[str] = None
    organization_id: Optional[str] = None
    is_superuser: Optional[bool] = None

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_by: str
    created_at: datetime
    modified_by: str
    modified_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    organization_name: Optional[str] = None

class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int 