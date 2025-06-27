from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from ....db.session import get_db
from ....services.role_service import RoleService
from ....schemas.role import RoleCreate, RoleUpdate, RoleResponse, UserRoleCreate, UserRoleResponse
from ....core.auth import get_current_user
from ....models.user import User
from ....models.role import Role

router = APIRouter()

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new role.
    """
    # Check if role with same name exists in the organization
    existing_role = RoleService.get_role_by_name(db, name=role_in.name, org_id=role_in.org_id)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists in the organization",
        )
    role = RoleService.create_role(db, role=role_in, current_user_id=current_user.id)
    return role

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: str,
    role_in: RoleUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a role.
    """
    role = RoleService.get_role_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Check if new name conflicts with existing role
    if role_in.name and role_in.name != role.name:
        existing_role = RoleService.get_role_by_name(db, name=role_in.name, org_id=role.org_id)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists in the organization",
            )
    
    role = RoleService.update_role(db, role_id=role_id, role_update=role_in, current_user_id=current_user.id)
    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a role.
    """
    role = RoleService.get_role_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    success = RoleService.delete_role(db, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role",
        )

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    *,
    db: Session = Depends(get_db),
    role_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get role by ID.
    """
    role = RoleService.get_role_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role

@router.get("/", response_model=List[RoleResponse])
def get_roles(
    *,
    db: Session = Depends(get_db),
    org_id: str = None,
    current_user: User = Depends(get_current_user)
) -> List[RoleResponse]:
    """
    Get all roles, optionally filtered by organization.
    """
    if org_id:
        roles = RoleService.get_roles_by_org(db, org_id=org_id)
    else:
        # Get all roles instead of just global roles
        roles = db.query(Role).all()
    return roles

@router.post("/assign", response_model=UserRoleResponse)
def assign_role(
    *,
    db: Session = Depends(get_db),
    user_role: UserRoleCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Assign a role to a user.
    """
    # Check if role exists
    role = RoleService.get_role_by_id(db, role_id=user_role.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Check if user already has this role
    existing_assignments = RoleService.get_user_roles(db, user_id=user_role.user_id)
    if any(assignment.role_id == user_role.role_id for assignment in existing_assignments):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role",
        )
    
    user_role = RoleService.assign_role_to_user(
        db, 
        user_role=user_role,
        assigned_by=current_user.id
    )
    return user_role

@router.delete("/assign/{user_id}/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    role_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Remove a role from a user.
    """
    success = RoleService.remove_role_from_user(db, user_id=user_id, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found",
        )

@router.get("/user/{user_id}", response_model=List[UserRoleResponse])
def get_user_roles(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> List[UserRoleResponse]:
    """
    Get all roles assigned to a user.
    """
    return RoleService.get_user_roles(db, user_id=user_id)

@router.get("/{role_id}/users", response_model=List[UserRoleResponse])
def get_role_users(
    *,
    db: Session = Depends(get_db),
    role_id: str,
    current_user: User = Depends(get_current_user)
) -> List[UserRoleResponse]:
    """
    Get all users assigned to a role.
    """
    role = RoleService.get_role_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return RoleService.get_role_users(db, role_id=role_id) 