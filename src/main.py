from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Dict
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import routers
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.lessons import router as lessons_router
from api.routes.qa import router as qa_router

# Import utilities and config
from utils.firebase import initialize_firebase
from config.settings import get_settings

# Get settings
settings = get_settings()

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Tutor API",
    description="API for AI-powered tutoring platform",
    version="0.1.0",
)

# Startup event to initialize Firebase
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize Firebase
        initialize_firebase()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        # Don't raise exception here to allow app to start even if Firebase init fails
        # In production, you might want to exit the app if critical services fail

# Configure CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify API is running
    """
    return {"status": "healthy", "message": "AI Tutor API is operational"}

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information
    """
    return {
        "message": "Welcome to AI Tutor API",
        "docs": "/docs",
        "version": app.version,
    }

# Include API routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(lessons_router, prefix=f"{settings.API_V1_STR}/lessons", tags=["Lessons"])
app.include_router(qa_router, prefix=f"{settings.API_V1_STR}/qa", tags=["Q&A"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

