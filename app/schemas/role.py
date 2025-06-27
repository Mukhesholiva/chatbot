from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class PermissionDict(BaseModel):
    read: List[str]
    write: List[str]

    class Config:
        json_encoders = {
            'PermissionDict': lambda v: {'read': v.read, 'write': v.write}
        }

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    org_id: Optional[str] = None
    permissions: Dict[str, List[str]]
    status: Optional[str] = "active"

    @validator('permissions', pre=True)
    def validate_permissions(cls, v):
        if isinstance(v, dict) and 'read' in v and 'write' in v:
            return v
        if isinstance(v, list):
            # Convert old list format to new dict format
            read_perms = []
            write_perms = []
            if '*' in v:
                return {'read': ['*'], 'write': ['*']}
            for perm in v:
                if perm.startswith('read:'):
                    read_perms.append(perm.replace('read:', ''))
                elif perm.startswith('write:'):
                    write_perms.append(perm.replace('write:', ''))
                else:
                    # If no prefix, assume it's both read and write
                    read_perms.append(perm)
                    write_perms.append(perm)
            return {'read': read_perms, 'write': write_perms}
        if isinstance(v, PermissionDict):
            return {'read': v.read, 'write': v.write}
        return {'read': [], 'write': []}

    def __init__(self, **data):
        super().__init__(**data)

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if isinstance(data['permissions'], PermissionDict):
            data['permissions'] = data['permissions'].model_dump()
        return data

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_id: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None
    status: Optional[str] = None

    @validator('permissions', pre=True)
    def validate_permissions(cls, v):
        if v is None:
            return None
        if isinstance(v, dict) and 'read' in v and 'write' in v:
            return v
        if isinstance(v, list):
            # Convert old list format to new dict format
            read_perms = []
            write_perms = []
            if '*' in v:
                return {'read': ['*'], 'write': ['*']}
            for perm in v:
                if perm.startswith('read:'):
                    read_perms.append(perm.replace('read:', ''))
                elif perm.startswith('write:'):
                    write_perms.append(perm.replace('write:', ''))
                else:
                    # If no prefix, assume it's both read and write
                    read_perms.append(perm)
                    write_perms.append(perm)
            return {'read': read_perms, 'write': write_perms}
        if isinstance(v, PermissionDict):
            return {'read': v.read, 'write': v.write}
        return None

    def __init__(self, **data):
        super().__init__(**data)

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