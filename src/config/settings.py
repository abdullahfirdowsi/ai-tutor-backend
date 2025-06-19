from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv
import os
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle single string (like "*" or comma-separated values)
            if v == "*":
                return ["*"]
            # Handle comma-separated origins
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    FIREBASE_API_KEY: Optional[str] = None
    FIREBASE_AUTH_DOMAIN: Optional[str] = None
    
    # Google Gemini settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Default model to use
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.7
    
    # Other application settings that might be needed
    PROJECT_NAME: str = "AI Tutor Pro"
    # Google Cloud TTS settings (if needed)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings to avoid reloading environment variables
    on each function call
    """
    settings = Settings()
    
    # Log which environment variables are missing if needed
    if settings.LOG_LEVEL == "DEBUG":
        for field_name, field in Settings.__annotations__.items():
            if getattr(settings, field_name) is None and 'Optional' not in str(field):
                print(f"Warning: {field_name} environment variable is not set")
    
    return settings
