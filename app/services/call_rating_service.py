from sqlalchemy.orm import Session
from typing import Optional
from ..models.call_rating import CallRating
from ..schemas.call_rating import CallRatingCreate
import uuid
from datetime import datetime

class CallRatingService:
    @staticmethod
    async def create_call_rating(db: Session, *, rating_in: CallRatingCreate) -> CallRating:
        """Create a new call rating."""
        db_obj = CallRating(
            id=str(uuid.uuid4()),
            call_id=rating_in.call_id,
            rating=rating_in.rating,
            submitted_by=rating_in.submitted_by,
            submitted_at=rating_in.submitted_at or datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_call_rating(db: Session, *, call_id: str) -> Optional[CallRating]:
        """Get rating for a specific call."""
        return db.query(CallRating).filter(CallRating.call_id == call_id).first() 