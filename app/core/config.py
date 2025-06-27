from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Chatbot API"
    API_V1_STR: str = "/api/v1"
    
    # Security Settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # New random secure key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2 hours
    ALGORITHM: str = "HS256"
    
    # Database Settings
    DB_SERVER: str = "183.82.126.21"
    DB_NAME: str = "voicebot"
    DB_USER: str = "sa"
    DB_PASSWORD: str = "Oliva@9876"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # This allows extra fields

settings = Settings()