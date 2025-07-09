from pydantic_settings import BaseSettings
from typing import List
import os

from typing import Optional
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings.
    For external API auth you can either provide EXTERNAL_API_KEY (static token)
    OR username/password which will be exchanged for a token automatically.
    """
    # API Settings
    PROJECT_NAME: str = "Chatbot API"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    DB_SERVER: str = Field(..., env='DB_SERVER')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    
    # Security Settings
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: str = "*"
    
    # External API Settings
    EXTERNAL_API_BASE_URL: str = Field(..., env='EXTERNAL_API_BASE_URL')
    EXTERNAL_API_KEY: Optional[str] = Field(None, env='EXTERNAL_API_KEY')
    EXTERNAL_API_TIMEOUT: int = 30  # seconds
    EXTERNAL_API_USERNAME: Optional[str] = Field(None, env='EXTERNAL_API_USERNAME')
    EXTERNAL_API_PASSWORD: Optional[str] = Field(None, env='EXTERNAL_API_PASSWORD')
    
    @field_validator('BACKEND_CORS_ORIGINS')
    def assemble_cors_origins(cls, v: str) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # This allows extra fields
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            # Priority: env_variables > .env file > init_settings
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

settings = Settings()