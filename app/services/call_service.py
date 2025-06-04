from sqlalchemy.orm import Session
from ..models.call import Call
from ..schemas.call import CallCreate, CallResponse, ExternalCallListResponse
import httpx
from typing import Optional, Dict, Any
import json
from datetime import datetime

class CallService:
    @staticmethod
    async def create_call(db: Session, call_data: CallCreate, auth_token: str) -> Call:
        # First, make the API call to create the call
        async with httpx.AsyncClient() as client:
            # Convert the data to dict and ensure metadata is used in the API call
            api_data = call_data.model_dump(by_alias=False)
            print("API Request Data:", api_data)
            
            # Ensure campaign_id is included in the request
            request_data = {
                "to_number": api_data["to_number"],
                "dynamic_variables": api_data["dynamic_variables"],
                "metadata": api_data["metadata"],
                "campaign_id": api_data["campaign_id"]  # Explicitly include campaign_id
            }
            print("Request Data with Campaign ID:", request_data)
            
            response = await client.post(
                "https://platform.voicelabs.in/api/v1/create-call",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                },
                json=request_data
            )
            print("Auth Token:", auth_token)
            print("API Response:", response.text)
            
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
    async def get_external_calls(campaign_id: str, start_date: str, end_date: str, auth_token: str) -> ExternalCallListResponse:
        """
        Get list of calls from external API for a specific campaign and date range.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://platform.voicelabs.in/api/v1/list-calls",
                params={
                    "campaign_id": campaign_id,
                    "start": start_date,
                    "end": end_date
                },
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            return ExternalCallListResponse(
                total=len(data.get("call_details", [])),
                calls=data.get("call_details", [])
            )
