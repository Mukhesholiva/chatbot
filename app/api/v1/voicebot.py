from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from .auth import get_current_active_user

router = APIRouter(prefix="/voicebot", tags=["Voice Bot"])

@router.post("/call")
async def initiate_call(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # TODO: Implement voice bot call initiation
    return {"message": "Voice bot call initiation to be implemented"} 