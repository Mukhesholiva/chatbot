from fastapi import APIRouter
from .endpoints import users as endpoints_users
from .endpoints import roles
from . import users

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])  # This includes the registration endpoint
api_router.include_router(endpoints_users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"]) 