from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext
import uuid
from typing import List, Any

from ...db.session import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from ...services.user_service import UserService
from .auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    db_user = UserService.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return UserService.create_user(db=db, user=user)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user (requires authentication).
    Only authenticated users can create new users with custom roles and organization IDs.
    """
    # Check if user with email already exists
    existing_user = UserService.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Generate unique ID
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Create new user with all fields
    db_user = User(
        id=user_id,
        email=user.email,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        phone=user.mobile_number or "",
        hashed_password=get_password_hash(user.password),
        role=user.role or "user",
        organization_id=user.organization_id,
        status=user.status or "active",
        created_by=current_user.id,  # Set created_by to the current user's ID
        modified_by=current_user.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        if value is not None:  # Only update if value is not None
            setattr(db_user, field, value)
    
    db_user.modified_by = current_user.id
    db_user.modified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by id.
    """
    user = await UserService.get_user(db, user_id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.get("/", response_model=UserListResponse)
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve users.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    users = await UserService.get_all_users(db, skip=skip, limit=limit)
    return {"items": users, "total": len(users)}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a user.
    """
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    
    success = UserService.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get user details by user ID.
    """
    user = await UserService.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    return user

@router.get("/", response_model=List[UserResponse])
async def get_users(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> List[UserResponse]:
    """
    Get all users with pagination.
    Only users with admin role can access this endpoint.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this endpoint"
        )
    users = await UserService.get_all_users(db, skip=skip, limit=limit)
    return list(users)  # Convert to list to ensure proper serialization
