from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.api import api_router
from .db.session import engine
from .db.base import Base
from .core.config import settings
from .api.v1 import auth, campaign, voicebot, organizations

app = FastAPI(
    title="Chatbot API",
    description="API for the Chatbot application",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(campaign.router, prefix=settings.API_V1_STR)
app.include_router(voicebot.router, prefix=settings.API_V1_STR)
app.include_router(organizations.router, prefix=settings.API_V1_STR) 