from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = logging.getLogger(__name__)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user
    
    Args:
        token: JWT token from request
        
    Returns:
        Dict: User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the Firebase token
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token.get("uid")
        
        if not uid:
            raise credentials_exception
            
        # Get the user from Firebase Auth
        user = firebase_auth.get_user(uid)
        
        # Return user data
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "email_verified": user.email_verified,
            "disabled": user.disabled
        }
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during authentication: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        raise credentials_exception

