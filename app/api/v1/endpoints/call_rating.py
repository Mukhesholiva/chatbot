from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from ....db.session import get_db
from ....services.call_rating_service import CallRatingService
from ....schemas.call_rating import CallRatingCreate, CallRatingResponse
from ....core.auth import get_current_active_user
from ....models.user import User

router = APIRouter()

@router.post("/{call_id}/rating", response_model=CallRatingResponse)
async def create_call_rating(
    *,
    call_id: str,
    rating_data: dict = Body(..., example={"rating": 4.5}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CallRatingResponse:
    """
    Create a new rating for a call.
    """
    try:
        rating_in = CallRatingCreate(
            call_id=call_id,
            rating=rating_data.get("rating"),
            submitted_by=current_user.email,
            submitted_at=None  # Will use current time
        )
        return await CallRatingService.create_call_rating(db=db, rating_in=rating_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{call_id}/rating", response_model=CallRatingResponse)
async def get_call_rating(
    *,
    call_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CallRatingResponse:
    """
    Get rating for a specific call.
    """
    rating = await CallRatingService.get_call_rating(db=db, call_id=call_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating not found for call {call_id}"
        )
    return rating 