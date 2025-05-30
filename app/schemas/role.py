from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    org_id: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    status: Optional[str] = "active"

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_id: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class RoleInDB(RoleBase):
    id: str
    created_at: datetime
    created_by: str
    modified_at: datetime
    modified_by: str

    class Config:
        from_attributes = True

class RoleResponse(RoleInDB):
    organization_name: Optional[str] = None

class UserRoleBase(BaseModel):
    user_id: str
    role_id: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleResponse(UserRoleBase):
    id: str
    assigned_by: str
    assigned_at: datetime
    created_at: datetime
    modified_at: datetime
    role_name: str
    assigner_name: str

    class Config:
        from_attributes = True 