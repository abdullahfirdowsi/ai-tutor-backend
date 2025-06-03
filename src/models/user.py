import firebase_admin
from firebase_admin import firestore, auth, credentials
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from src.config.settings import Settings

# Initialize logger
logger = logging.getLogger(__name__)

# Firebase initialization with lazy loading
_firebase_app = None
_db = None

def get_db():
    global _firebase_app, _db
    
    if _db is None:
        try:
            # Get settings
            settings = Settings()
            
            # Check if Firebase is already initialized
            if not _firebase_app:
                # Initialize Firebase with credentials
                if settings.firebase_credentials:
                    try:
                        # Try to initialize with service account credentials JSON
                        cred = credentials.Certificate(settings.firebase_credentials)
                        _firebase_app = firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized with credentials file")
                    except (ValueError, FileNotFoundError) as e:
                        logger.warning(f"Could not initialize Firebase with credentials file: {e}")
                        # Fall back to default initialization if service account fails
                        _firebase_app = firebase_admin.initialize_app()
                        logger.info("Firebase initialized with default credentials")
                else:
                    # Initialize with default credentials
                    _firebase_app = firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")
            
            # Get Firestore client
            _db = firestore.client()
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    return _db

# Get the Firestore client
db = get_db()

# Thread pool for running synchronous Firebase operations asynchronously
executor = ThreadPoolExecutor()

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
            db.collection("users").document(uid).set(user_data)
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
            doc_ref = db.collection("users").document(uid)
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
            doc_ref = db.collection("users").document(uid)
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
            doc_ref = db.collection("learningProgress").document(uid)
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
            doc_ref = db.collection("learningProgress").document(uid)
            
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

