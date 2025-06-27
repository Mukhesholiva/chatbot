from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db.base_class import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    call_id = Column(String(255), unique=True, index=True)
    to_number = Column(String(20))
    dynamic_variables = Column(JSON)  # Stores customer_name, dealer_name, vehicle_no, etc.
    call_metadata = Column('metadata', JSON)  # Stores org_id and user_id
    campaign_id = Column(String(36), ForeignKey("campaigns.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Campaign
    campaign = relationship("Campaign", back_populates="calls") 