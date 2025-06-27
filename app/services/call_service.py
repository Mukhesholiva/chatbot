from sqlalchemy.orm import Session
from ..models.call import Call
from ..schemas.call import CallCreate, CallResponse, ExternalCallListResponse, CallRecordingResponse
import httpx
from typing import Optional, Dict, Any
import json
from datetime import datetime
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class CallService:
    # Hardcoded credentials for external API
    EXTERNAL_API_USERNAME = "rakeshVoxiflow"
    EXTERNAL_API_PASSWORD = "Rakesh@voxi123"
    EXTERNAL_API_BASE_URL = "https://platform.voicelabs.in/api/v1"

    @staticmethod
    async def get_access_token() -> str:
        """Get access token from external API using hardcoded credentials."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CallService.EXTERNAL_API_BASE_URL}/login",
                json={
                    "username": CallService.EXTERNAL_API_USERNAME,
                    "password": CallService.EXTERNAL_API_PASSWORD
                }
            )
            response.raise_for_status()
            return response.json()["access_token"]

    @staticmethod
    async def create_call(db: Session, call_data: CallCreate, auth_token: str) -> Call:
        # First, make the API call to create the call
        async with httpx.AsyncClient() as client:
            # Convert the data to dict and ensure metadata is used in the API call
            api_data = call_data.model_dump(by_alias=False)
            # print("API Request Data:", api_data)
            
            # Ensure campaign_id is included in the request
            request_data = {
                "to_number": api_data["to_number"],
                "dynamic_variables": api_data["dynamic_variables"],
                "metadata": api_data["metadata"],
                "campaign_id": api_data["campaign_id"]  # Explicitly include campaign_id
            }
            # print("Request Data with Campaign ID:", request_data)
            
            response = await client.post(
                "https://platform.voicelabs.in/api/v1/create-call",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                },
                json=request_data
            )
            # print("Auth Token:", auth_token)
            # print("API Response:", response.text)
            
            response.raise_for_status()
            api_response = response.json()

        # Parse the created_at string into a datetime object
        created_at = datetime.strptime(api_response["created_at"].replace('Z', '+0000'), "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)

        # Create the call record in our database
        db_call = Call(
            call_id=api_response["call_id"],
            to_number=call_data.to_number,
            dynamic_variables=call_data.dynamic_variables,
            call_metadata=call_data.metadata,  # Use call_metadata for the database model
            campaign_id=call_data.campaign_id,
            created_at=created_at,
            updated_at=created_at  # Set updated_at to the same value initially
        )
        
        db.add(db_call)
        db.commit()
        db.refresh(db_call)
        return db_call

    @staticmethod
    async def get_call(db: Session, call_id: str) -> Optional[Call]:
        return db.query(Call).filter(Call.call_id == call_id).first()

    @staticmethod
    async def get_calls_by_campaign(db: Session, campaign_id: str, skip: int = 0, limit: int = 100):
        return db.query(Call).filter(Call.campaign_id == campaign_id).offset(skip).limit(limit).all()

    @staticmethod
    async def get_external_calls(
        campaign_id: str, 
        start_date: str, 
        end_date: str, 
        auth_token: str,
        page_size: int = 10,
        cursor: str = None
    ) -> ExternalCallListResponse:
        """
        Get list of calls from external API for a specific campaign and date range.
        """
        async with httpx.AsyncClient() as client:
            params = {
                "campaign_id": campaign_id,
                "start": start_date,
                "end": end_date,
                "page_size": page_size
            }
            if cursor:
                params["cursor"] = cursor

            response = await client.get(
                "https://platform.voicelabs.in/api/v1/list-calls",
                params=params,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return ExternalCallListResponse(
                items=data.get("items", []),
                page_size=data.get("page_size", 10),
                has_more=data.get("has_more", False),
                next_cursor=data.get("next_cursor")
            )

    @staticmethod
    async def get_call_recording(campaign_id: str, call_id: str) -> CallRecordingResponse:
        """
        Get call recording URL from external API.
        Returns the URL and expiration time.
        """
        try:
            # First get the access token
            access_token = await CallService.get_access_token()
            
            # Get the recording URL
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CallService.EXTERNAL_API_BASE_URL}/call-recordings",
                    params={"campaign_id": campaign_id, "call_id": call_id},
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                recording_data = response.json()
                
                # The API returns the URL in the 'url' field
                if not recording_data.get("url"):
                    raise HTTPException(status_code=404, detail="Recording URL not found")
                
                return CallRecordingResponse(
                    url=recording_data["url"],
                    expiresAt=recording_data.get("expiresAt")
                )
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching recording URL: {str(e)}")
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching recording URL: {str(e)}")
