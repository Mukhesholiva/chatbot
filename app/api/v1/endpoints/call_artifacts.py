from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....db.session import get_db
from ....services.call_artifacts_service import CallArtifactsService
from ....schemas.call_artifacts import CallArtifacts, DataExtractionResponse, TranscriptionResponse
from ....core.auth import get_current_active_user
from ....models.user import User
import httpx

router = APIRouter()

async def get_external_token() -> str:
    """Get access token from external API."""
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            "https://platform.voicelabs.in/api/v1/login",
            json={
                "username": "rakeshVoxiflow",
                "password": "Rakesh@voxi123"
            }
        )
        login_response.raise_for_status()
        return login_response.json()["access_token"]

@router.get("/{call_id}/artifacts", response_model=CallArtifacts)
async def get_call_artifacts(
    *,
    call_id: str,
    current_user: User = Depends(get_current_active_user)
) -> CallArtifacts:
    """
    Get all artifacts for a specific call.
    """
    try:
        auth_token = await get_external_token()
        return await CallArtifactsService.get_artifacts(call_id=call_id, auth_token=auth_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{call_id}/data-extraction", response_model=DataExtractionResponse)
async def get_call_data_extraction(
    *,
    call_id: str,
    current_user: User = Depends(get_current_active_user)
) -> DataExtractionResponse:
    """
    Get data extraction for a specific call.
    """
    try:
        auth_token = await get_external_token()
        return await CallArtifactsService.get_data_extraction(call_id=call_id, auth_token=auth_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{call_id}/transcription", response_model=TranscriptionResponse)
async def get_call_transcription(
    *,
    call_id: str,
    current_user: User = Depends(get_current_active_user)
) -> TranscriptionResponse:
    """
    Get transcription for a specific call.
    """
    try:
        auth_token = await get_external_token()
        return await CallArtifactsService.get_transcription(call_id=call_id, auth_token=auth_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 