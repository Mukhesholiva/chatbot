from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ....db.session import get_db
from ....services.campaign_service import CampaignService
from ....schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from ....core.auth import get_current_active_user
from ....models.user import User
from ....schemas.voice import VoiceResponse

router = APIRouter()

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks
):
    """
    Create a new campaign in our database and sync with external API
    """
    try:
        result = await CampaignService.create_campaign(
            db=db,
            campaign=campaign_in,
            current_user_id=current_user.id,
            is_superuser=current_user.is_superuser,
            sync_with_external=True
        )
        
        # Return the created campaign (already CampaignResponse)
        return result["campaign"]
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create campaign: {str(e)}"
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
    
    result = await CampaignService.update_campaign(db, campaign_id, campaign_update.model_dump(), current_user=current_user)
    if not result or not result.get("campaign"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return result["campaign"]

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

@router.get("/voices", response_model=List[VoiceResponse])
async def get_voices(
    *, 
    db: Session = Depends(get_db),
    voice_ids: str = None,
    current_user: User = Depends(get_current_active_user)
) -> List[VoiceResponse]:
    """
    Get voice details by voice IDs (comma-separated).
    If no IDs provided, returns all voices.
    """
    try:
        if voice_ids:
            voice_id_list = voice_ids.split(',')
            query = f"""
                SELECT 
                    id, voice_id, name, main_accent, description, age, gender, 
                    use_case, main_preview_url, next_page_token, language,
                    model_id, lang_accent, locale, lang_preview_url
                FROM [voicebot].[dbo].[ElevenLabsVoices]
                WHERE voice_id IN :voice_ids
            """
            result = await db.execute(query, {'voice_ids': tuple(voice_id_list)})
        else:
            query = """
                SELECT 
                    id, voice_id, name, main_accent, description, age, gender, 
                    use_case, main_preview_url, next_page_token, language,
                    model_id, lang_accent, locale, lang_preview_url
                FROM [voicebot].[dbo].[ElevenLabsVoices]
            """
            result = await db.execute(query)
        
        voices = result.all()
        if not voices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No voices found"
            )
        return voices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )