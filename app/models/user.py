from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile_number = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    role_id = Column(String(50), ForeignKey("roles.id"), nullable=False)
    status = Column(String(20), default="active")
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(50), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", lazy="joined")
    campaigns = relationship("UserCampaign", back_populates="user")
