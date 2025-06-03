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
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_DATABASE_URL: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
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

