from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
from ....db.session import get_db
from ....services.user_service import UserService
from ....schemas.user import UserCreate, UserUpdate, UserResponse
from ....core.auth import get_current_active_user
from ....models.user import User

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new user.
    """
    user = UserService.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = UserService.create_user(db, user=user_in)
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a user.
    
    Request body format:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "mobile_number": "+1234567890",
        "role": "org_admin",
        "organization_id": "org_id_here",
        "status": "active"
    }
    """
    user = await UserService.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    
    # Check if email is being updated and if it's already taken
    if user_in.email and user_in.email != user.email:
        existing_user = UserService.get_user_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered to another user",
            )
    
    user = await UserService.update_user(
        db, 
        user_id=user_id, 
        user_update=user_in
    )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a user by ID.
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        None with 204 status code on successful deletion
        
    Raises:
        HTTPException: If user is not found or deletion fails
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
    
    return None

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
    Only users with superuser role can access this endpoint.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this endpoint"
        )
    users = await UserService.get_all_users(db, skip=skip, limit=limit)
    return list(users)  # Convert to list to ensure proper serialization 