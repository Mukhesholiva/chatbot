from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from ...db.session import get_db
from ...services.campaign_service import CampaignService
from ...schemas.campaign import CampaignCreate, CampaignResponse
from .auth import get_current_active_user
from ...models.user import User

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("/")
async def list_campaigns(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # TODO: Implement campaign listing
    return {"message": "Campaign listing to be implemented"}

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: CampaignCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new campaign both in database and external system.
    """
    campaign = await CampaignService.create_campaign_with_external(
        db=db,
        campaign=campaign_in,
        username=campaign_in.username,
        password=campaign_in.password
    )
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign in external system or database",
        )
    return campaign 