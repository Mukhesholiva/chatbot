from fastapi import APIRouter
from .endpoints import users, campaigns, calls, roles, call_artifacts, call_rating, voices

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(call_artifacts.router, prefix="/calls", tags=["call artifacts"])
api_router.include_router(call_rating.router, prefix="/calls", tags=["call ratings"])
api_router.include_router(voices.router, prefix="/voices", tags=["voices"])