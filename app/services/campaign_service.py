from sqlalchemy.orm import Session
from ..models.campaign import Campaign
from ..models.user_campaign import UserCampaign
from ..schemas.campaign import CampaignCreate, CampaignResponse
import httpx
import json
from datetime import datetime
import uuid
from sqlalchemy import select
from sqlalchemy import text

class CampaignService:
    # Hardcoded credentials for external API
    EXTERNAL_API_USERNAME = "rakeshVoxiflow"
    EXTERNAL_API_PASSWORD = "Rakesh@voxi123"
    EXTERNAL_API_BASE_URL = "https://platform.voicelabs.in/api/v1"

    @staticmethod
    async def get_access_token() -> str:
        """Get access token from external API using hardcoded credentials."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CampaignService.EXTERNAL_API_BASE_URL}/login",
                json={
                    "username": CampaignService.EXTERNAL_API_USERNAME,
                    "password": CampaignService.EXTERNAL_API_PASSWORD
                }
            )
            response.raise_for_status()
            return response.json()["access_token"]

    @staticmethod
    def _serialize_datetime(obj):
        """Helper function to serialize datetime objects to ISO format strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    @staticmethod
    async def create_campaign_with_external(
        db: Session,
        campaign: CampaignCreate,
        current_user_id: str = None,
        is_superuser: bool = False,
        username: str = None,
        password: str = None
    ) -> Campaign:
        """
        Create campaign both in external system and database.
        Uses hardcoded credentials for external API authentication.
        For non-superusers, also creates a user-campaign association.
        """
        try:
            # Get access token using hardcoded credentials
            access_token = await CampaignService.get_access_token()

            # Prepare campaign data for external API
            campaign_data = campaign.model_dump()
            
            # Remove fields that shouldn't be sent to external API
            external_campaign_data = {k: v for k, v in campaign_data.items() if k not in ['org_id']}
            
            # Check if campaign with this ID already exists
            if campaign_data.get("id"):
                existing_campaign = await CampaignService.get_campaign(db, campaign_data["id"])
                if existing_campaign:
                    raise Exception(f"Campaign with ID {campaign_data['id']} already exists")
            
            # Generate a new UUID if not provided
            if "id" not in campaign_data:
                campaign_data["id"] = str(uuid.uuid4())
            
            # Set timestamps if not provided
            current_time = datetime.utcnow()
            if "created_at" not in campaign_data:
                campaign_data["created_at"] = current_time
            if "updated_at" not in campaign_data:
                campaign_data["updated_at"] = current_time

            # Create campaign in external system
            # Convert datetime objects to ISO format for JSON serialization
            external_campaign_data = json.loads(
                json.dumps(
                    external_campaign_data,
                    default=CampaignService._serialize_datetime
                )
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CampaignService.EXTERNAL_API_BASE_URL}/create-campaign",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=external_campaign_data
                )
                response.raise_for_status()
                external_campaign = response.json()

            # Create campaign in database
            db_campaign = Campaign(
                id=campaign_data["id"],
                name=campaign.name,
                direction=campaign.direction,
                inbound_number=campaign.inbound_number,
                caller_id_number=campaign.caller_id_number,
                state=campaign.state,
                version=campaign.version,
                llm_config=campaign.llm.model_dump(),
                tts_config=campaign.tts.model_dump(),
                stt_config=campaign.stt,
                timezone=campaign.timezone,
                post_call_actions=campaign.post_call_actions,
                live_actions=campaign.live_actions,
                callback_endpoint=campaign.callback_endpoint,
                retry_config=campaign.retry,
                account_id=campaign.account_id,
                org_id=campaign.org_id,
                created_by=campaign.created_by,
                is_active=campaign.is_active,
                telephonic_provider=campaign.telephonic_provider,
                knowledge_base=campaign.knowledge_base.model_dump()
            )
            db.add(db_campaign)
            
            # If current_user_id is provided and user is not a superuser,
            # create user-campaign association
            if current_user_id and not is_superuser:
                user_campaign = UserCampaign(
                    user_id=current_user_id,
                    campaign_id=db_campaign.id,
                    created_by=str(campaign.created_by),
                    modified_by=str(campaign.created_by)
                )
                db.add(user_campaign)
            
            db.commit()
            db.refresh(db_campaign)

            # Map the config fields to the expected response fields
            response_data = {
                **db_campaign.__dict__,
                "llm": db_campaign.llm_config,
                "tts": db_campaign.tts_config,
                "stt": db_campaign.stt_config,
                "retry": db_campaign.retry_config
            }
            # Remove the config fields
            response_data.pop("llm_config", None)
            response_data.pop("tts_config", None)
            response_data.pop("stt_config", None)
            response_data.pop("retry_config", None)
            response_data.pop("_sa_instance_state", None)

            # Convert datetime objects to ISO format strings in response
            response_data = json.loads(
                json.dumps(response_data, default=CampaignService._serialize_datetime)
            )

            return CampaignResponse(**response_data)

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create campaign: {str(e)}")

    @staticmethod
    async def get_campaign(db: Session, campaign_id: str) -> CampaignResponse:
        """Get campaign by ID."""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None
            
        # Convert to response format
        response_data = {
            "id": campaign.id,
            "name": campaign.name,
            "direction": campaign.direction,
            "inbound_number": campaign.inbound_number,
            "caller_id_number": campaign.caller_id_number,
            "state": campaign.state,
            "version": campaign.version,
            "llm": campaign.llm_config,
            "tts": campaign.tts_config,
            "stt": campaign.stt_config,
            "timezone": campaign.timezone,
            "post_call_actions": campaign.post_call_actions,
            "live_actions": campaign.live_actions,
            "callback_endpoint": campaign.callback_endpoint,
            "retry": campaign.retry_config,
            "account_id": campaign.account_id,
            "created_by": campaign.created_by,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "is_active": campaign.is_active,
            "telephonic_provider": campaign.telephonic_provider,
            "knowledge_base": campaign.knowledge_base,
            "org_id": campaign.org_id
        }
        return CampaignResponse(**response_data)

    @staticmethod
    async def update_campaign(db: Session, campaign_id: str, campaign_update: dict) -> CampaignResponse:
        """Update campaign by ID in local DB and sync with external API."""
        
        # Fetch from DB
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return None

        # Update local fields
        for field, value in campaign_update.items():
            if field in ["llm", "tts", "stt", "retry"]:
                setattr(db_campaign, f"{field}_config", value)
            else:
                setattr(db_campaign, field, value)

        try:
            db.commit()
            db.refresh(db_campaign)

            # External API payload structure
            payload = {
                "id": db_campaign.id,
                "name": db_campaign.name,
                "direction": db_campaign.direction,
                "inbound_number": db_campaign.inbound_number,
                "caller_id_number": db_campaign.caller_id_number,
                "state": db_campaign.state,
                "allow_interruption": getattr(db_campaign, "allow_interruption", False),
                "version": db_campaign.version,
                "llm": db_campaign.llm_config,
                "tts": db_campaign.tts_config,
                "stt": db_campaign.stt_config,
                "timezone": db_campaign.timezone,
                "post_call_actions": db_campaign.post_call_actions,
                "live_actions": db_campaign.live_actions,
                "callback_endpoint": db_campaign.callback_endpoint,
                "retry": db_campaign.retry_config,
                "account_id": db_campaign.account_id,
                "created_by": db_campaign.created_by,
                "created_at": db_campaign.created_at.isoformat() if db_campaign.created_at else None,
                "updated_at": db_campaign.updated_at.isoformat() if db_campaign.updated_at else None,
                "is_active": db_campaign.is_active,
                "telephonic_provider": db_campaign.telephonic_provider,
                "knowledge_base": db_campaign.knowledge_base
            }

            # Get token
            access_token = await CampaignService.get_access_token()

            # Call external API
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    "https://platform.voicelabs.in/api/v1/update-campaign",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()

            return CampaignResponse(**payload)

        except Exception as e:
            db.rollback()
            raise Exception(f"Update failed: {str(e)}")

    @staticmethod
    async def delete_campaign(db: Session, campaign_id: str) -> bool:
        """Delete campaign by ID."""
        try:
            # First, check if campaign exists
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return False

            # Use raw SQL to delete the campaign to avoid SQLAlchemy relationship issues
            
            # Delete any related calls first (if they exist)
            delete_calls_sql = text("""
                IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'calls')
                BEGIN
                    DELETE FROM calls WHERE campaign_id = :campaign_id
                END
            """)
            
            # Delete the campaign
            delete_campaign_sql = text("""
                DELETE FROM campaigns 
                WHERE id = :campaign_id
            """)

            # Execute the deletions in a transaction
            try:
                db.execute(delete_calls_sql, {"campaign_id": campaign_id})
                db.execute(delete_campaign_sql, {"campaign_id": campaign_id})
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise Exception(f"Database error during deletion: {str(e)}")

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete campaign: {str(e)}")

    @staticmethod
    async def get_campaigns(db: Session, skip: int = 0, limit: int = 1000):
        """Get all campaigns with pagination, limited to 1000 records."""
        from sqlalchemy import select
        
        # Create a select statement with specific column order
        query = select(
            Campaign.id,
            Campaign.name,
            Campaign.direction,
            Campaign.inbound_number,
            Campaign.caller_id_number,
            Campaign.state,
            Campaign.version,
            Campaign.llm_config,
            Campaign.tts_config,
            Campaign.stt_config,
            Campaign.timezone,
            Campaign.post_call_actions,
            Campaign.live_actions,
            Campaign.callback_endpoint,
            Campaign.retry_config,
            Campaign.account_id,
            Campaign.created_by,
            Campaign.created_at,
            Campaign.updated_at,
            Campaign.is_active,
            Campaign.telephonic_provider,
            Campaign.knowledge_base,
            Campaign.org_id
        ).select_from(Campaign).order_by(Campaign.created_at.desc()).offset(skip).limit(limit)

        # Execute query
        result = db.execute(query)
        campaigns = result.all()

        # Convert to list of dictionaries with proper field names
        campaign_list = []
        for campaign in campaigns:
            campaign_dict = {
                "id": campaign.id,
                "name": campaign.name,
                "direction": campaign.direction,
                "inbound_number": campaign.inbound_number,
                "caller_id_number": campaign.caller_id_number,
                "state": campaign.state,
                "version": campaign.version,
                "llm": campaign.llm_config,
                "tts": campaign.tts_config,
                "stt": campaign.stt_config,
                "timezone": campaign.timezone,
                "post_call_actions": campaign.post_call_actions,
                "live_actions": campaign.live_actions,
                "callback_endpoint": campaign.callback_endpoint,
                "retry": campaign.retry_config,
                "account_id": campaign.account_id,
                "created_by": campaign.created_by,
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at,
                "is_active": campaign.is_active,
                "telephonic_provider": campaign.telephonic_provider,
                "knowledge_base": campaign.knowledge_base,
                "org_id": campaign.org_id
            }
            campaign_list.append(CampaignResponse(**campaign_dict))

        return campaign_list

    @staticmethod
    async def get_user_campaigns(
        db: Session,
        user_id: str,
        is_superuser: bool = False,
        skip: int = 0,
        limit: int = 1000
    ):
        """Get all campaigns with pagination. For superusers, returns all campaigns.
        For regular users, returns only their associated campaigns."""
        from sqlalchemy import select
        
        # For superusers, return all campaigns
        if is_superuser:
            return await CampaignService.get_campaigns(db, skip=skip, limit=limit)
        
        # For regular users, return only their associated campaigns
        query = select(
            Campaign
        ).join(
            UserCampaign,
            Campaign.id == UserCampaign.campaign_id
        ).where(
            UserCampaign.user_id == user_id
        ).order_by(
            Campaign.created_at.desc()
        ).offset(skip).limit(limit)

        # Execute query
        result = db.execute(query)
        campaigns = result.scalars().all()

        # Convert to response format
        campaign_list = []
        for campaign in campaigns:
            campaign_dict = {
                "id": campaign.id,
                "name": campaign.name,
                "direction": campaign.direction,
                "inbound_number": campaign.inbound_number,
                "caller_id_number": campaign.caller_id_number,
                "state": campaign.state,
                "version": campaign.version,
                "llm": campaign.llm_config,
                "tts": campaign.tts_config,
                "stt": campaign.stt_config,
                "timezone": campaign.timezone,
                "post_call_actions": campaign.post_call_actions,
                "live_actions": campaign.live_actions,
                "callback_endpoint": campaign.callback_endpoint,
                "retry": campaign.retry_config,
                "account_id": campaign.account_id,
                "created_by": campaign.created_by,
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at,
                "is_active": campaign.is_active,
                "telephonic_provider": campaign.telephonic_provider,
                "knowledge_base": campaign.knowledge_base,
                "org_id": campaign.org_id
            }
            campaign_list.append(CampaignResponse(**campaign_dict))

        return campaign_list 