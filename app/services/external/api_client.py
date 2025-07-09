import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from ...core.config import settings
import logging

logger = logging.getLogger(__name__)

class ExternalAPIClient:
    def __init__(self):
        self.base_url = settings.EXTERNAL_API_BASE_URL.rstrip("/")
        self.timeout = settings.EXTERNAL_API_TIMEOUT
        self.username = settings.EXTERNAL_API_USERNAME
        self.password = settings.EXTERNAL_API_PASSWORD
        self.api_key = settings.EXTERNAL_API_KEY
        self._token: Optional[str] = self.api_key if self.api_key else None

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        auth: bool = True
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                if auth and self._token:
                    headers["Authorization"] = f"Bearer {self._token}"
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"External API error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error calling external API: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to connect to external service"
            )

    async def _login(self) -> str:
        """Authenticate and cache bearer token"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/login",
                    json={"username": self.username, "password": self.password},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                token = resp.json().get("access_token")
                if not token:
                    raise ValueError("access_token not found in login response")
                self._token = token
                return token
        except Exception as e:
            logger.error(f"External API login failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="External API login failed")

    async def _ensure_token(self):
        if not self._token:
            if self.username and self.password:
                await self._login()
            else:
                self._token = self.api_key

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a campaign in the external system"""
        if self.username and self.password:
            await self._login()
        else:
            self._token = self.api_key
        return await self._make_request("POST", "create-campaign", campaign_data)

    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a campaign in the external system (POST to /update-campaign, with full re-auth)"""
        if self.username and self.password:
            await self._login()
        else:
            self._token = self.api_key
        # The external API expects PUT to /update-campaign
        return await self._make_request("PUT", "update-campaign", campaign_data)

    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details from the external system"""
        return await self._make_request("GET", f"campaigns/{campaign_id}")

# Singleton instance
external_api = ExternalAPIClient()
