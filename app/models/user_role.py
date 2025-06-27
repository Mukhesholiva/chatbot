from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(50), ForeignKey("roles.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(50), nullable=False)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    # Remove direct relationships to avoid circular dependencies 