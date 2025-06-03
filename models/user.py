import firebase_admin
from firebase_admin import firestore, auth
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.firebase import get_firestore_client

logger = logging.getLogger(__name__)

# Thread pool for running synchronous Firebase operations asynchronously
executor = ThreadPoolExecutor()

def get_db():
    """
    Get the Firestore client instance lazily.
    This ensures Firebase is properly initialized before accessing Firestore.
    
    Returns:
        firestore.Client: Firestore client
    """
    return get_firestore_client()

async def create_user_profile(uid: str, email: str, display_name: str, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a new user profile in Firestore
    
    Args:
        uid: User ID from Firebase Auth
        email: User email
        display_name: User display name
        preferences: User preferences dictionary
        
    Returns:
        Dict: Created user profile data
    """
    try:
        user_data = {
            "uid": uid,
            "email": email,
            "display_name": display_name,
            "preferences": preferences or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Run in thread pool to avoid blocking
        def _create_profile():
            get_db().collection("users").document(uid).set(user_data)
            return user_data
            
        return await asyncio.get_event_loop().run_in_executor(executor, _create_profile)
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise

async def get_user_profile(uid: str) -> Optional[Dict[str, Any]]:
    """
    Get a user profile from Firestore
    
    Args:
        uid: User ID from Firebase Auth
        
    Returns:
        Dict: User profile data or None if not found
    """
    try:
        # Run in thread pool to avoid blocking
        def _get_profile():
            doc_ref = get_db().collection("users").document(uid)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_profile)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise

async def update_user_profile(uid: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user profile in Firestore
    
    Args:
        uid: User ID from Firebase Auth
        update_data: Dictionary of fields to update
        
    Returns:
        Dict: Updated user profile data
    """
    try:
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now()
        
        # Run in thread pool to avoid blocking
        def _update_profile():
            doc_ref = get_db().collection("users").document(uid)
            doc_ref.update(update_data)
            return {**doc_ref.get().to_dict(), **update_data}
            
        return await asyncio.get_event_loop().run_in_executor(executor, _update_profile)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise

async def get_learning_progress(uid: str) -> Optional[Dict[str, Any]]:
    """
    Get a user's learning progress from Firestore
    
    Args:
        uid: User ID from Firebase Auth
        
    Returns:
        Dict: Learning progress data or None if not found
    """
    try:
        # Run in thread pool to avoid blocking
        def _get_progress():
            doc_ref = get_db().collection("learningProgress").document(uid)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_progress)
        
    except Exception as e:
        logger.error(f"Error getting learning progress: {str(e)}")
        raise

async def update_learning_progress(uid: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's learning progress in Firestore
    
    Args:
        uid: User ID from Firebase Auth
        update_data: Dictionary of fields to update
        
    Returns:
        Dict: Updated learning progress data
    """
    try:
        # Add last_active timestamp
        update_data["last_active"] = datetime.now()
        
        # Run in thread pool to avoid blocking
        def _update_progress():
            doc_ref = get_db().collection("learningProgress").document(uid)
            
            # Create or update document
            if not doc_ref.get().exists:
                doc_ref.set(update_data)
            else:
                doc_ref.update(update_data)
                
            return {**doc_ref.get().to_dict()}
            
        return await asyncio.get_event_loop().run_in_executor(executor, _update_progress)
        
    except Exception as e:
        logger.error(f"Error updating learning progress: {str(e)}")
        raise

