from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....services.call_service import CallService
from ....schemas.call import CallCreate, CallResponse, ExternalCallListResponse
from ....core.auth import get_current_active_user
from ....models.user import User
import httpx
from datetime import datetime, timedelta

router = APIRouter(tags=["calls"])

@router.post("/", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    *,
    db: Session = Depends(get_db),
    call_in: CallCreate,
    current_user: User = Depends(get_current_active_user)
) -> CallResponse:
    """
    Create a new call.
    """
    try:
        # Get access token from external API
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                "https://platform.voicelabs.in/api/v1/login",
                json={
                    "username": "rakeshVoxiflow",
                    "password": "Rakesh@voxi123"
                }
            )
            login_response.raise_for_status()
            auth_token = login_response.json()["access_token"]
        # print(call_in)
        call = await CallService.create_call(db, call_data=call_in, auth_token=auth_token)
        return call
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    *,
    db: Session = Depends(get_db),
    call_id: str,
    current_user: User = Depends(get_current_active_user)
) -> CallResponse:
    """
    Get call details by call ID.
    """
    call = await CallService.get_call(db, call_id=call_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    return call

@router.get("/campaign/{campaign_id}", response_model=List[CallResponse])
async def get_calls_by_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> List[CallResponse]:
    """
    Get all calls for a specific campaign from database.
    """
    calls = await CallService.get_calls_by_campaign(db, campaign_id=campaign_id, skip=skip, limit=limit)
    return list(calls)

@router.get("/external/{campaign_id}/list", response_model=ExternalCallListResponse)
async def list_external_calls(
    *,
    campaign_id: str,
    start_date: str = Query(None, description="Start date in ISO format (YYYY-MM-DDTHH:MM:SSZ)"),
    end_date: str = Query(None, description="End date in ISO format (YYYY-MM-DDTHH:MM:SSZ)"),
    current_user: User = Depends(get_current_active_user)
) -> ExternalCallListResponse:
    """
    Get list of calls from external API for a specific campaign.
    If dates are not provided, defaults to last 30 days.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Get access token from external API
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                "https://platform.voicelabs.in/api/v1/login",
                json={
                    "username": "rakeshVoxiflow",
                    "password": "Rakesh@voxi123"
                }
            )
            login_response.raise_for_status()
            auth_token = login_response.json()["access_token"]

        # Get call list from external API
        return await CallService.get_external_calls(
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date,
            auth_token=auth_token
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 