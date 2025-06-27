from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.sql import func
from ..db.base_class import Base

class CallRating(Base):
    __tablename__ = "call_ratings"

    id = Column(String, primary_key=True, index=True)
    call_id = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False)
    submitted_by = Column(String, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 