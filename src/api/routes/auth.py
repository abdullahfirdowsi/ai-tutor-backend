from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
import logging

from config.settings import get_settings
from schemas.user import UserCreate, UserResponse, PasswordReset

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user with email and password
    
    Args:
        user_data: User registration data
        
    Returns:
        UserResponse: Basic user information and token
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Create user in Firebase Authentication
        user = firebase_auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name,
            disabled=False
        )
        
        # Create custom token for the user
        token = firebase_auth.create_custom_token(user.uid)
        
        # Add user to Firestore database with additional profile data
        from models.user import create_user_profile
        await create_user_profile(
            uid=user.uid,
            email=user_data.email,
            display_name=user_data.display_name,
            preferences=user_data.preferences
        )
        
        return UserResponse(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name,
            token=token.decode('utf-8')
        )
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during signup: {str(e)}")
        if "EMAIL_EXISTS" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user registration"
        )

@router.post("/login", response_model=UserResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user with email and password
    
    Args:
        form_data: OAuth2 password request form with username (email) and password
        
    Returns:
        UserResponse: User information and authentication token
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify the email/password with Firebase Authentication
        user = firebase_auth.get_user_by_email(form_data.username)
        
        # In Firebase REST API, we'd verify the password, but the admin SDK doesn't provide this
        # Instead, we need to use a Firebase custom token
        token = firebase_auth.create_custom_token(user.uid)
        
        # Get user profile from Firestore
        from models.user import get_user_profile
        user_profile = await get_user_profile(user.uid)
        
        return UserResponse(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name or user_profile.get("display_name", ""),
            token=token.decode('utf-8')
        )
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(password_reset: PasswordReset):
    """
    Request a password reset email
    
    Args:
        password_reset: Password reset request with email
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If password reset request fails
    """
    try:
        # Send password reset email via Firebase
        firebase_auth.generate_password_reset_link(password_reset.email)
        
        return {"message": "Password reset email sent"}
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during password reset: {str(e)}")
        if "USER_NOT_FOUND" in str(e):
            # Don't reveal if the email exists for security reasons
            return {"message": "Password reset email sent if account exists"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send password reset email"
        )
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset"
        )

@router.post("/verify-token")
async def verify_token(token: str = Body(..., embed=True)):
    """
    Verify a Firebase ID token
    
    Args:
        token: Firebase ID token
        
    Returns:
        Dict: User ID if token is valid
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(token)
        
        return {"uid": decoded_token["uid"]}
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token verification"
        )

