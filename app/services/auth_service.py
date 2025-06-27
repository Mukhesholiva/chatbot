from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from ..core.security import verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        user = self.db.query(models.User).filter(models.User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, username: str, expires_delta: Optional[timedelta] = None) -> str:
        return create_access_token(
            data={"sub": username},
            expires_delta=expires_delta
        ) 