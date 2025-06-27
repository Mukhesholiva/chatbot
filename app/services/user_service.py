from sqlalchemy.orm import Session
from datetime import datetime
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
import httpx
from typing import List, Optional
import os
from sqlalchemy import text
from ..core.security import get_password_hash
import uuid
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    async def get_organization_name(org_id: str) -> Optional[str]:
        """Fetch organization name from the organization API"""
        if not org_id:
            return None
        try:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/v1/organizations/{org_id}")
                if response.status_code == 200:
                    org_data = response.json()
                    return org_data.get("name")
        except Exception as e:
            print(f"Error fetching organization name: {str(e)}")
            return None
        return None

    @staticmethod
    async def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> List[User]:
        """
        Get all users with pagination support.
        Returns users ordered by created_at descending (newest first).
        """
        users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        for user in users:
            if user.organization_id:
                user.organization_name = await UserService.get_organization_name(user.organization_id)
        return users
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        # Check if organization exists if provided
        if user.organization_id:
            org_exists = db.execute(
                text("SELECT 1 FROM organizations WHERE id = :org_id"),
                {"org_id": user.organization_id}
            ).scalar()
            if not org_exists:
                raise ValueError(f"Organization with ID {user.organization_id} does not exist")
        else:
            # Use default organization if none provided
            user.organization_id = "org_1"

        # Check if role exists
        if user.role_id:
            role_exists = db.execute(
                text("SELECT 1 FROM roles WHERE id = :role_id"),
                {"role_id": user.role_id}
            ).scalar()
            if not role_exists:
                raise ValueError(f"Role with ID {user.role_id} does not exist")
        else:
            # Get default user role ID
            default_role = db.execute(
                text("SELECT id FROM roles WHERE name = 'user' LIMIT 1")
            ).scalar()
            if not default_role:
                raise ValueError("Default user role not found")
            user.role_id = default_role

        db_user = User(
            id=str(uuid.uuid4()),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            mobile_number=user.mobile_number,
            hashed_password=get_password_hash(user.password),
            organization_id=user.organization_id,
            role_id=user.role_id,
            created_by=user.created_by or "system",
            modified_by=user.modified_by or "system"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user(db: Session, user_id: str) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.organization_id:
            user.organization_name = await UserService.get_organization_name(user.organization_id)
        return user

    @staticmethod
    async def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        db_user = await UserService.get_user(db, user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db_user.modified_at = datetime.utcnow()
            db.commit()
            db.refresh(db_user)
            if db_user.organization_id:
                db_user.organization_name = await UserService.get_organization_name(db_user.organization_id)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        db.delete(db_user)
        db.commit()
        return True 