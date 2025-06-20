from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings using pydantic BaseSettings for environment variable loading
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Tutor"
    DEBUG: bool = True
    
    # CORS Settings
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
    
    # Firebase Settings
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: Optional[str] = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: Optional[str] = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: Optional[str] = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    FIREBASE_UNIVERSE_DOMAIN: Optional[str] = "googleapis.com"
    FIREBASE_DATABASE_URL: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # Google Gemini Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.7
    
    # Google Cloud TTS Settings
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    TTS_LANGUAGE_CODE: str = "en-US"
    TTS_VOICE_NAME: str = "en-US-Neural2-A"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Create a cached instance of settings to avoid loading from environment variables multiple times
    """
    return Settings()

