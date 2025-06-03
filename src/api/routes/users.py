from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any, List
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions

from schemas.user import UserProfileUpdate, UserProfileResponse, LearningProgressResponse
from models.user import get_user_profile, update_user_profile, get_learning_progress
from utils.auth import get_current_user

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current user's profile
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        UserProfileResponse: User profile data
        
    Raises:
        HTTPException: If profile retrieval fails
    """
    try:
        user_id = current_user["uid"]
        user_profile = await get_user_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
        return UserProfileResponse(
            uid=user_id,
            email=current_user.get("email", ""),
            display_name=user_profile.get("display_name", ""),
            avatar_url=user_profile.get("avatar_url", ""),
            preferences=user_profile.get("preferences", {}),
            created_at=user_profile.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving user profile"
        )

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update the current user's profile
    
    Args:
        profile_update: Profile data to update
        current_user: Current authenticated user from token
        
    Returns:
        UserProfileResponse: Updated user profile
        
    Raises:
        HTTPException: If profile update fails
    """
    try:
        user_id = current_user["uid"]
        
        # Update profile in Firestore
        updated_profile = await update_user_profile(user_id, profile_update.dict(exclude_unset=True))
        
        # Update display name in Firebase Auth if provided
        if profile_update.display_name:
            firebase_auth.update_user(
                user_id,
                display_name=profile_update.display_name
            )
            
        return UserProfileResponse(
            uid=user_id,
            email=current_user.get("email", ""),
            display_name=updated_profile.get("display_name", ""),
            avatar_url=updated_profile.get("avatar_url", ""),
            preferences=updated_profile.get("preferences", {}),
            created_at=updated_profile.get("created_at", "")
        )
        
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during profile update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating user profile"
        )

@router.get("/me/progress", response_model=LearningProgressResponse)
async def get_my_learning_progress(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the current user's learning progress
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        LearningProgressResponse: User's learning progress data
        
    Raises:
        HTTPException: If learning progress retrieval fails
    """
    try:
        user_id = current_user["uid"]
        progress_data = await get_learning_progress(user_id)
        
        if not progress_data:
            # Return empty progress if not found
            return LearningProgressResponse(
                completed_lessons=[],
                current_lesson=None,
                total_time_spent=0,
                statistics={},
                last_active=None
            )
            
        return LearningProgressResponse(**progress_data)
        
    except Exception as e:
        logger.error(f"Error retrieving learning progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving learning progress"
        )

