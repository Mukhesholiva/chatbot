from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user_campaign import UserCampaign
from ..models.campaign import Campaign
from ..models.user import User
from ..schemas.user_campaign import UserCampaignCreate, UserCampaignResponse
from datetime import datetime

class UserCampaignService:
    @staticmethod
    async def create_user_campaign(
        db: Session,
        user_campaign: UserCampaignCreate,
        current_user_email: str
    ) -> UserCampaignResponse:
        db_user_campaign = UserCampaign(
            user_id=user_campaign.user_id,
            campaign_id=user_campaign.campaign_id,
            created_by=current_user_email,
            modified_by=current_user_email
        )
        db.add(db_user_campaign)
        db.commit()
        db.refresh(db_user_campaign)
        return await UserCampaignService._to_response(db, db_user_campaign)

    @staticmethod
    async def get_user_campaigns(
        db: Session,
        user_id: str
    ) -> List[UserCampaignResponse]:
        user_campaigns = db.query(UserCampaign).filter(
            UserCampaign.user_id == user_id
        ).all()
        return [await UserCampaignService._to_response(db, uc) for uc in user_campaigns]

    @staticmethod
    async def get_campaign_users(
        db: Session,
        campaign_id: str
    ) -> List[UserCampaignResponse]:
        campaign_users = db.query(UserCampaign).filter(
            UserCampaign.campaign_id == campaign_id
        ).all()
        return [await UserCampaignService._to_response(db, cu) for cu in campaign_users]

    @staticmethod
    async def update_user_campaigns(
        db: Session,
        user_id: str,
        campaign_ids: List[str],
        current_user_email: str
    ) -> List[UserCampaignResponse]:
        # Delete existing associations
        db.query(UserCampaign).filter(UserCampaign.user_id == user_id).delete()
        
        # Create new associations
        new_associations = []
        for campaign_id in campaign_ids:
            association = UserCampaign(
                user_id=user_id,
                campaign_id=campaign_id,
                created_by=current_user_email,
                modified_by=current_user_email
            )
            db.add(association)
            new_associations.append(association)
        
        db.commit()
        for assoc in new_associations:
            db.refresh(assoc)
        
        return [await UserCampaignService._to_response(db, na) for na in new_associations]

    @staticmethod
    async def delete_user_campaign(
        db: Session,
        user_id: str,
        campaign_id: str
    ) -> bool:
        result = db.query(UserCampaign).filter(
            UserCampaign.user_id == user_id,
            UserCampaign.campaign_id == campaign_id
        ).delete()
        db.commit()
        return result > 0

    @staticmethod
    async def _to_response(
        db: Session,
        user_campaign: UserCampaign
    ) -> UserCampaignResponse:
        # Get campaign name
        campaign = db.query(Campaign).filter(
            Campaign.id == user_campaign.campaign_id
        ).first()
        campaign_name = campaign.name if campaign else None

        # Get user email
        user = db.query(User).filter(
            User.id == user_campaign.user_id
        ).first()
        user_email = user.email if user else None

        return UserCampaignResponse(
            id=user_campaign.id,
            user_id=user_campaign.user_id,
            campaign_id=user_campaign.campaign_id,
            created_at=user_campaign.created_at,
            created_by=user_campaign.created_by,
            modified_at=user_campaign.modified_at,
            modified_by=user_campaign.modified_by,
            campaign_name=campaign_name,
            user_email=user_email
        ) 