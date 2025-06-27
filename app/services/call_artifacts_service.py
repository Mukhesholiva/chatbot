import httpx
import json
from typing import Optional, Dict, Any
from ..schemas.call_artifacts import CallArtifacts, DataExtractionResponse, TranscriptionResponse

class CallArtifactsService:
    @staticmethod
    async def get_artifacts(call_id: str, auth_token: str) -> CallArtifacts:
        """Get all artifacts for a specific call."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://platform.voicelabs.in/api/v1/get-artifacts",
                json={"call_id": call_id},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            return CallArtifacts(**data)

    @staticmethod
    async def get_data_extraction(call_id: str, auth_token: str) -> DataExtractionResponse:
        """Get only the data extraction part of the artifacts."""
        artifacts = await CallArtifactsService.get_artifacts(call_id, auth_token)
        return DataExtractionResponse(
            category=artifacts.category,
            summary=artifacts.summary,
            **{"extracted-data": artifacts.extracted_data}
        )

    @staticmethod
    async def get_transcription(call_id: str, auth_token: str) -> TranscriptionResponse:
        """Get only the transcription part of the artifacts."""
        artifacts = await CallArtifactsService.get_artifacts(call_id, auth_token)
        return TranscriptionResponse(transcription=artifacts.transcription) 