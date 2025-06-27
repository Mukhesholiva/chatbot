from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....services.user_campaign_service import UserCampaignService
from ....schemas.user_campaign import UserCampaignCreate, UserCampaignResponse, UserCampaignUpdate
from ....core.auth import get_current_active_user
from ....models.user import User

router = APIRouter()

@router.post("/users/{user_id}/campaigns", response_model=UserCampaignResponse)
async def assign_campaign_to_user(
    user_id: str,
    campaign_in: UserCampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserCampaignResponse:
    """
    Assign a campaign to a user.
    """
    try:
        return await UserCampaignService.create_user_campaign(
            db=db,
            user_campaign=campaign_in,
            current_user_email=current_user.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/users/{user_id}/campaigns", response_model=List[UserCampaignResponse])
async def get_user_campaigns(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[UserCampaignResponse]:
    """
    Get all campaigns assigned to a user.
    """
    try:
        return await UserCampaignService.get_user_campaigns(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/campaigns/{campaign_id}/users", response_model=List[UserCampaignResponse])
async def get_campaign_users(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[UserCampaignResponse]:
    """
    Get all users assigned to a campaign.
    """
    try:
        return await UserCampaignService.get_campaign_users(db=db, campaign_id=campaign_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/users/{user_id}/campaigns", response_model=List[UserCampaignResponse])
async def update_user_campaigns(
    user_id: str,
    campaign_update: UserCampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[UserCampaignResponse]:
    """
    Update the list of campaigns assigned to a user.
    """
    try:
        return await UserCampaignService.update_user_campaigns(
            db=db,
            user_id=user_id,
            campaign_ids=campaign_update.campaign_ids,
            current_user_email=current_user.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/users/{user_id}/campaigns/{campaign_id}")
async def remove_campaign_from_user(
    user_id: str,
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Remove a campaign assignment from a user.
    """
    try:
        success = await UserCampaignService.delete_user_campaign(
            db=db,
            user_id=user_id,
            campaign_id=campaign_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User-Campaign association not found"
            )
        return {"message": "Campaign assignment removed successfully"} 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )