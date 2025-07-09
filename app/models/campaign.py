from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    direction = Column(String(20), nullable=False)
    inbound_number = Column(String(20))
    caller_id_number = Column(String(20))
    state = Column(String(20), nullable=False)
    version = Column(String(10), default="0")
    llm_config = Column(JSON)
    tts_config = Column(JSON)
    stt_config = Column(JSON)
    timezone = Column(String(50))
    post_call_actions = Column(JSON)
    live_actions = Column(JSON)
    callback_endpoint = Column(String(255))
    retry_config = Column(JSON)
    account_id = Column(String(50))
    org_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    telephonic_provider = Column(String(50))
    knowledge_base = Column(JSON)
    allow_interruption = Column(Boolean, default=True)
    speech_setting = Column(JSON)
    external_id = Column(String(50))

    # Relationship with Call
    calls = relationship("Call", back_populates="campaign")
    # Relationship with Organization
    organization = relationship("Organization")
    # Relationship with UserCampaign
    users = relationship("UserCampaign", back_populates="campaign") 