from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.api import api_router
from .db.session import engine
from .db.base import Base
from .core.config import settings
from .api.v1 import auth, campaign, voicebot, organizations
from .middleware.auth_middleware import token_expiration_middleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Add token expiration middleware
app.middleware("http")(token_expiration_middleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        # Don't raise the exception, allow the app to start even if DB is not available

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(campaign.router, prefix=settings.API_V1_STR)
app.include_router(voicebot.router, prefix=settings.API_V1_STR)
app.include_router(organizations.router, prefix=settings.API_V1_STR) 