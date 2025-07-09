from sqlalchemy.orm import Session
from ..models.campaign import Campaign
from ..models.user_campaign import UserCampaign
from ..schemas.campaign import CampaignCreate, CampaignResponse
import uuid
from sqlalchemy import select, text
from typing import Any, Dict, List, Optional, Set, Union
from fastapi import HTTPException, status
import logging
from .external.api_client import external_api

logger = logging.getLogger(__name__)

class CampaignService:
    @staticmethod
    def _to_dict(obj):
        """Convert various object types to a plain dictionary.
        Supports Pydantic models, SQLAlchemy models, and plain dicts."""
        if obj is None:
            return None
        # Pydantic model
        if hasattr(obj, 'dict'):
            return obj.dict()
        # SQLAlchemy model instance
        if hasattr(obj, '__table__'):
            return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
        # Already a dict
        if isinstance(obj, dict):
            return dict(obj)
        return obj
        
    @staticmethod
    def _get_valid_campaign_fields():
        """Get the list of valid field names for the Campaign model"""
        return {
            'id', 'name', 'direction', 'inbound_number', 'caller_id_number',
            'state', 'version', 'llm_config', 'tts_config', 'stt_config',
            'timezone', 'post_call_actions', 'live_actions', 'callback_endpoint',
            'retry_config', 'account_id', 'org_id', 'created_by', 'created_at',
            'updated_at', 'is_active', 'telephonic_provider', 'knowledge_base',
            'allow_interruption', 'speech_setting', 'external_id'
        }
        
    @staticmethod
    def _prepare_external_payload(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for external API"""
        # Ensure we are working with a dict
        campaign_data = CampaignService._to_dict(campaign_data)
        # Map fields to external API format
        payload = {
            "id": campaign_data.get("id") or campaign_data.get("id", None),
            "name": campaign_data.get("name"),
            "direction": campaign_data.get("direction", "OUTBOUND"),
            "state": campaign_data.get("state", "TRIAL"),
            "version": str(campaign_data.get("version", "0")),  # Ensure version is string
            "account_id": campaign_data.get("account_id"),
            "telephonic_provider": campaign_data.get("telephonic_provider", "exotel"),
            "allow_interruption": campaign_data.get("allow_interruption", True),
            "llm": campaign_data.get("llm", campaign_data.get("llm_config", {})),
            "tts": campaign_data.get("tts", campaign_data.get("tts_config", {})),
            "stt": campaign_data.get("stt", campaign_data.get("stt_config", {})),
            "speech_setting": campaign_data.get("speech_setting", {}),
            "retry": campaign_data.get("retry", campaign_data.get("retry_config", {})),
            "post_call_actions": campaign_data.get("post_call_actions", {}),
            "live_actions": campaign_data.get("live_actions", []),
            "timezone": campaign_data.get("timezone", "UTC"),
            "knowledge_base": campaign_data.get("knowledge_base", {})
        }
        
        # Remove None values
        return {k: v for k, v in payload.items() if v is not None}

    @staticmethod
    def _get_nested(data, *keys, default=None):
        """Safely get nested dictionary keys"""
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            elif hasattr(data, key):
                data = getattr(data, key, default)
            else:
                return default
        return data

    @staticmethod
    def _filter_valid_fields(data: dict, exclude_fields: set = None) -> dict:
        """Filter out any fields that aren't valid for the Campaign model"""
        if exclude_fields is None:
            exclude_fields = set()
            
        valid_fields = CampaignService._get_valid_campaign_fields()
        return {
            k: v for k, v in data.items() 
            if k in valid_fields and k not in exclude_fields
        }

    @staticmethod
    async def create_campaign(
        db: Session,
        campaign,
        current_user_id: str,  # Changed to str to match database type
        is_superuser: bool = False,
        sync_with_external: bool = True
    ) -> Dict[str, Any]:
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(campaign, 'dict'):
                campaign_data = campaign.dict(exclude_unset=True)
            else:
                campaign_data = dict(campaign)
            
            # Filter out any invalid fields and excluded fields
            exclude_fields = {"speech_setting", "llm", "tts", "stt", "retry"}
            campaign_data = CampaignService._filter_valid_fields(campaign_data, exclude_fields)
            
            # Set required fields
            campaign_data["created_by"] = current_user_id
            
            # Set default values for required fields if not provided
            if "state" not in campaign_data:
                campaign_data["state"] = "DRAFT"
            if "direction" not in campaign_data:
                campaign_data["direction"] = "OUTBOUND"
            if "version" not in campaign_data:
                campaign_data["version"] = "0"
            if "is_active" not in campaign_data:
                campaign_data["is_active"] = True
                
            # Ensure required fields have proper defaults
            if "knowledge_base" not in campaign_data or not campaign_data["knowledge_base"]:
                campaign_data["knowledge_base"] = {}
                
            # Set created_by as string (UUID)
            campaign_data["created_by"] = str(current_user_id)

            # Safely get and convert nested objects with proper error handling
            def safe_get_nested(key):
                try:
                    return CampaignService._to_dict(CampaignService._get_nested(campaign, key))
                except Exception as e:
                    logger.warning(f"Failed to process {key}: {str(e)}")
                    return None
            
            speech_setting = safe_get_nested("speech_setting")
            llm = safe_get_nested("llm")
            tts = safe_get_nested("tts")
            stt = safe_get_nested("stt")
            retry = safe_get_nested("retry")

            # Prepare the campaign data for database
            db_campaign_data = {
                **campaign_data,
                "speech_setting": speech_setting or {},
                "llm_config": llm or {},
                "tts_config": tts or {},
                "stt_config": stt or {},
                "retry_config": retry or {},
                "knowledge_base": campaign_data.get("knowledge_base", {})
            }
            
            # Create the campaign in the database
            db_campaign = Campaign(**db_campaign_data)

            db.add(db_campaign)
            
            # First save to our database
            db.commit()
            db.refresh(db_campaign)
            
            # Then sync with external API if needed
            if sync_with_external:
                try:
                    logger.info("Syncing campaign with external API …")
                    external_response = await external_api.create_campaign(
                        CampaignService._prepare_external_payload(db_campaign)
                    )
                    logger.info(f"External API response: {external_response}")

                    # Persist external campaign ID if returned
                    if external_response and 'id' in external_response:
                        db_campaign.external_id = external_response['id']
                        db.commit()
                        db.refresh(db_campaign)

                except Exception as e:
                    db.rollback()
                    logger.error(f"External API sync failed: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"External API sync failed: {str(e)}"
                    )
            
            # Build response object
            from app.schemas.campaign import CampaignResponse
            response_dict = {
                **db_campaign.__dict__,
                "created_at": db_campaign.created_at,
                "updated_at": db_campaign.updated_at,
                "llm": db_campaign.llm_config or {},
                "tts": db_campaign.tts_config or {},
                "stt": db_campaign.stt_config or {},
                "retry": db_campaign.retry_config or {},
            }
            response = CampaignResponse(**response_dict)
            return {
                "campaign": response,
                "external_campaign": external_response if sync_with_external else None,
                "external_sync_success": True if sync_with_external else False
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create campaign: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create campaign: {str(e)}"
            )

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
            "version": str(campaign.version) if campaign.version is not None else "0",
            "llm": campaign.llm_config or {},
            "tts": campaign.tts_config or {},
            "stt": campaign.stt_config or {},
            "retry": campaign.retry_config or {},
            "timezone": campaign.timezone,
            "post_call_actions": campaign.post_call_actions,
            "live_actions": campaign.live_actions,
            "callback_endpoint": campaign.callback_endpoint,
            "account_id": campaign.account_id,
            "created_by": campaign.created_by,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "is_active": campaign.is_active,
            "telephonic_provider": campaign.telephonic_provider,
            "knowledge_base": campaign.knowledge_base,
            "org_id": campaign.org_id,
            "allow_interruption": bool(getattr(campaign, "allow_interruption", True)),
            "speech_setting": campaign.speech_setting or {},
            "external_id": getattr(campaign, "external_id", None)
        }
        return CampaignResponse(**response_data)

    @staticmethod
    async def update_campaign(
        db: Session,
        campaign_id: str,
        campaign_update: dict,
        current_user,
        sync_with_external: bool = True
    ) -> dict:
        """Update campaign by ID in local DB and sync with external API."""
        
        # Fetch from DB
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return None

        # Remove created_by from payload to avoid overwriting
        campaign_update.pop("created_by", None)

        # Update local fields
        for field, value in campaign_update.items():
            if field in ["llm", "tts", "stt", "retry"]:
                setattr(db_campaign, f"{field}_config", value)
            else:
                setattr(db_campaign, field, value)

        # Always set created_by from the current user
        db_campaign.created_by = getattr(current_user, "id", getattr(current_user, "email", None))

        try:
            # Commit the transaction
            db.commit()
            db.refresh(db_campaign)

            external_response = None
            # Sync with external API if requested
            if sync_with_external:
                try:
                    logger.info("Syncing campaign update with external API …")
                    payload = CampaignService._prepare_external_payload(db_campaign)
                    external_response = await external_api.update_campaign(str(db_campaign.external_id or db_campaign.id), payload)
                    logger.info(f"External API update response: {external_response}")
                except Exception as e:
                    db.rollback()
                    logger.error(f"External API update failed: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"External API update failed: {str(e)}"
                    )

            from app.schemas.campaign import CampaignResponse
            campaign_dict = {
                **db_campaign.__dict__,
                "created_at": db_campaign.created_at,
                "updated_at": db_campaign.updated_at,
                "external_id": db_campaign.external_id,
                "post_call_actions": db_campaign.post_call_actions or {},
                "live_actions": db_campaign.live_actions or [],
                "callback_endpoint": db_campaign.callback_endpoint or "",
                "llm": db_campaign.llm_config or {},
                "tts": db_campaign.tts_config or {},
                "stt": db_campaign.stt_config or {},
                "retry": db_campaign.retry_config or {},
                "speech_setting": db_campaign.speech_setting or {},
                "knowledge_base": db_campaign.knowledge_base or {},
                "version": str(db_campaign.version) if db_campaign.version is not None else "0"
            }
            response = CampaignResponse(**campaign_dict)
            return {
                "campaign": response,
                "external_campaign": external_response if sync_with_external else None,
                "external_sync_success": True if sync_with_external else False
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Update failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Update failed: {str(e)}"
            )

    @staticmethod
    async def delete_campaign(db: Session, campaign_id: str) -> bool:
        """Delete campaign by ID."""
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return False
            campaign.is_active = 0
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"Database error during soft deletion: {str(e)}")

    @staticmethod
    async def get_user_campaigns(
        db: Session,
        user_id: str,
        is_superuser: bool = False,
        skip: int = 0,
        limit: int = 1000
    ):
        from sqlalchemy import select
        if is_superuser:
            query = select(Campaign).where(Campaign.is_active == 1).order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
            result = db.execute(query)
            campaigns = result.scalars().all()
        else:
            query = select(Campaign).join(UserCampaign, Campaign.id == UserCampaign.campaign_id).where(
                UserCampaign.user_id == user_id,
                Campaign.is_active == 1
            ).order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
            result = db.execute(query)
            campaigns = result.scalars().all()
        campaign_list = []
        for campaign in campaigns:
            campaign_dict = {
                "id": campaign.id,
                "name": campaign.name,
                "direction": campaign.direction,
                "inbound_number": campaign.inbound_number,
                "caller_id_number": campaign.caller_id_number,
                "state": campaign.state,
                "version": str(campaign.version) if campaign.version is not None else "0",
                "llm": campaign.llm_config or {},
                "tts": campaign.tts_config or {},
                "stt": campaign.stt_config or {},
                "retry": campaign.retry_config or {},
                "timezone": campaign.timezone,
                "post_call_actions": campaign.post_call_actions,
                "live_actions": campaign.live_actions,
                "callback_endpoint": campaign.callback_endpoint,
                "account_id": campaign.account_id,
                "created_by": campaign.created_by,
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at,
                "is_active": campaign.is_active,
                "telephonic_provider": campaign.telephonic_provider,
                "knowledge_base": campaign.knowledge_base,
                "org_id": campaign.org_id,
                "allow_interruption": bool(getattr(campaign, "allow_interruption", True)),
                "speech_setting": campaign.speech_setting or {},
                "external_id": getattr(campaign, "external_id", None)
            }
            campaign_list.append(CampaignResponse(**campaign_dict))
        return campaign_list