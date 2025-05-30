from sqlalchemy.orm import Session
from ..models.campaign import Campaign
from ..schemas.campaign import CampaignCreate, CampaignResponse
import httpx
import json
from datetime import datetime
import uuid

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
        username: str = None,  # These parameters are kept for backward compatibility
        password: str = None   # but will be ignored as we use hardcoded credentials
    ) -> Campaign:
        """
        Create campaign both in external system and database.
        Uses hardcoded credentials for external API authentication.
        """
        try:
            # Get access token using hardcoded credentials
            access_token = await CampaignService.get_access_token()

            # Prepare campaign data for external API
            campaign_data = campaign.model_dump()
            
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
                campaign_data["created_at"] = current_time.isoformat()
            if "updated_at" not in campaign_data:
                campaign_data["updated_at"] = current_time.isoformat()

            # Convert any datetime objects to ISO format strings
            campaign_data = json.loads(
                json.dumps(
                    campaign_data,
                    default=CampaignService._serialize_datetime
                )
            )

            # Create campaign in external system
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CampaignService.EXTERNAL_API_BASE_URL}/create-campaign",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=campaign_data
                )
                response.raise_for_status()
                external_campaign = response.json()

            # Create campaign in database
            db_campaign = Campaign(
                id=campaign_data["id"],  # Use the ID from campaign_data
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
                created_by=campaign.created_by,
                is_active=campaign.is_active,
                telephonic_provider=campaign.telephonic_provider,
                knowledge_base=campaign.knowledge_base.model_dump()
            )
            db.add(db_campaign)
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
            response_data.pop("_sa_instance_state", None)  # Remove SQLAlchemy internal state

            return CampaignResponse(**response_data)

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create campaign: {str(e)}")

    @staticmethod
    async def get_campaign(db: Session, campaign_id: str) -> Campaign:
        """Get campaign by ID."""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    @staticmethod
    async def get_all_campaigns(db: Session, skip: int = 0, limit: int = 100):
        """Get all campaigns with pagination."""
        return db.query(Campaign).offset(skip).limit(limit).all() 