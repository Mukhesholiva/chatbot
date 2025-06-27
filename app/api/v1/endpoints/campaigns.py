from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ....db.session import get_db
from ....services.campaign_service import CampaignService
from ....schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
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
    Create a new campaign. For non-superusers, the campaign will be automatically
    associated with the current user.
    """
    try:
        campaign = await CampaignService.create_campaign_with_external(
            db=db,
            campaign=campaign_in,
            current_user_id=current_user.id,
            is_superuser=current_user.is_superuser
        )
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
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[CampaignResponse]:
    """
    Get all campaigns. For superusers, returns all campaigns.
    For regular users, returns only their associated campaigns.
    """
    try:
        return await CampaignService.get_user_campaigns(
            db=db,
            user_id=current_user.id,
            is_superuser=current_user.is_superuser,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_active_user)
) -> CampaignResponse:
    """
    Update a campaign by ID. Requires all campaign fields.
    """
    if campaign_id != campaign_update.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in path does not match ID in update data"
        )
    
    updated_campaign = await CampaignService.update_campaign(db, campaign_id, campaign_update.model_dump())
    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return updated_campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a campaign by ID.
    """
    deleted = await CampaignService.delete_campaign(db, campaign_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return None 