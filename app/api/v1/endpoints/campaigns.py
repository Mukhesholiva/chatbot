from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....services.campaign_service import CampaignService
from ....schemas.campaign import CampaignCreate, CampaignResponse
from ....core.auth import get_current_active_user
from ....models.user import User

router = APIRouter()

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: CampaignCreate,
    current_user: User = Depends(get_current_active_user)
) -> CampaignResponse:
    """
    Create a new campaign.
    """
    try:
        campaign = await CampaignService.create_campaign_with_external(db, campaign=campaign_in)
        return campaign
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: str,
    current_user: User = Depends(get_current_active_user)
) -> CampaignResponse:
    """
    Get campaign details by campaign ID.
    """
    campaign = await CampaignService.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> List[CampaignResponse]:
    """
    Get all campaigns with pagination.
    """
    campaigns = await CampaignService.get_campaigns(db, skip=skip, limit=limit)
    return list(campaigns) 