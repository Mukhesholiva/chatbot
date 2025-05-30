from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    name = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(50), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", lazy="joined") 