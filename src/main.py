from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Dict, Callable
import sys
import os
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import routers
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.lessons import router as lessons_router
from api.routes.qa import router as qa_router
from api.routes.analytics import router as analytics_router

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

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = f"{time.time():.7f}"
        
        # Log request details
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"- Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response details
            logger.info(
                f"Response {request_id}: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Took: {process_time:.4f}s"
            )
            
            return response
        except Exception as e:
            # Log any exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {request.method} {request.url.path} "
                f"- Error: {str(e)} - Took: {process_time:.4f}s"
            )
            # Re-raise the exception so FastAPI can handle it
            raise

# Add middleware to app
app.add_middleware(RequestLoggingMiddleware)

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
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])

if __name__ == "__main__":
    # You can also configure uvicorn logging levels
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    uvicorn_log_config["loggers"]["uvicorn.access"]["level"] = settings.LOG_LEVEL
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=uvicorn_log_config
    )

