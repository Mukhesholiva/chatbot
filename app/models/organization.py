from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(50), nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", lazy="joined")
    roles = relationship("Role", back_populates="organization", lazy="joined") 