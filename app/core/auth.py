from typing import Optional, Dict, Any
import time
from functools import lru_cache

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# Initialize Firebase Admin SDK
@lru_cache()
def get_firebase_app():
    """Initialize and cache the Firebase Admin SDK app instance"""
    try:
        if settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        else:
            # Use environment variables if no credentials file is provided
            cred = credentials.ApplicationDefault()
        
        # Check if app is already initialized to avoid initialization error
        try:
            return firebase_admin.get_app()
        except ValueError:
            return firebase_admin.initialize_app(cred)
    except Exception as e:
        # For development, we can continue without Firebase
        print(f"Warning: Failed to initialize Firebase Admin SDK: {e}")
        if settings.DEBUG:
            # In debug mode, we'll use a mock Firebase app
            return None
        else:
            # In production, this is a critical error
            raise

# Security scheme for token authentication
security = HTTPBearer()

class AuthUser:
    """Represents an authenticated user"""
    def __init__(self, user_id: str, email: Optional[str] = None, name: Optional[str] = None, 
                 is_admin: bool = False, claims: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.is_admin = is_admin
        self.claims = claims or {}
        self.authenticated = True

class FirebaseAuth:
    """Firebase authentication handler"""
    def __init__(self):
        # Initialize Firebase when first used
        self.firebase_app = get_firebase_app()
        
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a Firebase ID token and return the decoded token"""
        try:
            # Skip token verification in debug mode if Firebase is not configured
            if settings.DEBUG and self.firebase_app is None:
                if token == "debug-token":
                    # Return a mock user for development
                    return {
                        "uid": "debug-user-id",
                        "email": "debug@example.com",
                        "name": "Debug User",
                        "claims": {"admin": True},
                    }
            
            # Verify the token with Firebase Admin SDK
            decoded_token = firebase_auth.verify_id_token(token)
            
            # Check if token is expired
            if time.time() > decoded_token.get('exp', 0):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}"
            )

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> AuthUser:
        """Extract and validate user from request"""
        token = credentials.credentials
        decoded_token = await self.verify_token(token)
        
        # Extract user information
        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")
        claims = decoded_token.get("claims", {})
        is_admin = claims.get("admin", False)
        
        return AuthUser(
            user_id=user_id,
            email=email,
            name=name,
            is_admin=is_admin,
            claims=claims
        )
    
    async def get_admin_user(self, user: AuthUser = Depends(get_current_user)) -> AuthUser:
        """Verify that the user is an admin"""
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator privileges required"
            )
        return user


# Create a global instance for use as a dependency
firebase_auth_instance = FirebaseAuth()
get_current_user = firebase_auth_instance.get_current_user
get_admin_user = firebase_auth_instance.get_admin_user

# Optional dependency for routes that can work with or without authentication
async def get_optional_user(request: Request) -> Optional[AuthUser]:
    """Get the current user if token is provided, otherwise None"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        decoded_token = await firebase_auth_instance.verify_token(token)
        user_id = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")
        claims = decoded_token.get("claims", {})
        is_admin = claims.get("admin", False)
        
        return AuthUser(
            user_id=user_id,
            email=email,
            name=name,
            is_admin=is_admin,
            claims=claims
        )
    except HTTPException:
        return None
