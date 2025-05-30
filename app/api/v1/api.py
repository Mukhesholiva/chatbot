from fastapi import APIRouter
from .endpoints import users
from .endpoints import campaigns
from .endpoints import calls
from .endpoints import roles

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"]) 