from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings using pydantic BaseSettings for environment variable loading
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Tutor"
    DEBUG: bool = True
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
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
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
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

