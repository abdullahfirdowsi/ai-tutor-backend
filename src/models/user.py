import firebase_admin
from firebase_admin import firestore, auth, credentials
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from src.config.settings import Settings
async def get_user_settings(uid: str) -> Optional[Dict[str, Any]]:
    """
    Get a user's settings from Firestore
    
    Args:
        uid: User ID from Firebase Auth
        
    Returns:
        Dict: User settings data or None if not found
    """
    try:
        # Run in thread pool to avoid blocking
        def _get_settings():
            doc_ref = db.collection("userSettings").document(uid)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_settings)
        
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise

async def update_user_settings(uid: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's settings in Firestore
    
    Args:
        uid: User ID from Firebase Auth
        settings_data: Dictionary of settings to update
        
    Returns:
        Dict: Updated user settings data
    """
    try:
        # Add updated_at timestamp
        settings_data["updated_at"] = datetime.now()
        settings_data["user_id"] = uid
        
        # Run in thread pool to avoid blocking
        def _update_settings():
            doc_ref = db.collection("userSettings").document(uid)
            
            # Create or update document
            if not doc_ref.get().exists:
                doc_ref.set(settings_data)
            else:
                doc_ref.update(settings_data)
                
            return doc_ref.get().to_dict()
            
        return await asyncio.get_event_loop().run_in_executor(executor, _update_settings)
        
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise
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
        
async def get_lesson_progress(uid: str, lesson_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user's progress for a specific lesson
    
    Args:
        uid: User ID from Firebase Auth
        lesson_id: Lesson ID
        
    Returns:
        Dict: Lesson progress data or None if not found
    """
    try:
        def _get_lesson_progress():
            # Get user's learning progress document
            doc_ref = db.collection("learningProgress").document(uid)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            progress_data = doc.to_dict()
            completed_lessons = progress_data.get("completed_lessons", [])
            
            # Look for the lesson in completed lessons
            lesson_progress = next(
                (lesson for lesson in completed_lessons 
                 if lesson.get("lesson_id") == lesson_id),
                None
            )
            
            # If not in completed lessons, check current lesson
            if not lesson_progress and progress_data.get("current_lesson", {}).get("lesson_id") == lesson_id:
                lesson_progress = progress_data["current_lesson"]
            
            # Format the response to match LessonProgressResponse schema
            if lesson_progress:
                return {
                    "progress": lesson_progress.get("progress", 0.0),
                    "time_spent": lesson_progress.get("time_spent", 0),
                    "completed": lesson_progress.get("completed", False),
                    "score": lesson_progress.get("score"),
                    "last_position": lesson_progress.get("last_position"),
                    "notes": lesson_progress.get("notes"),
                    "last_accessed": lesson_progress.get("last_accessed")
                }
            
            return None
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_lesson_progress)
        
    except Exception as e:
        logger.error(f"Error getting lesson progress: {str(e)}")
        raise

async def update_lesson_progress(uid: str, lesson_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's progress for a specific lesson
    
    Args:
        uid: User ID from Firebase Auth
        lesson_id: Lesson ID
        progress_data: Progress data to update
        
    Returns:
        Dict: Updated lesson progress data
    """
    try:
        # Add timestamps
        progress_data["last_accessed"] = datetime.now()
        progress_data["lesson_id"] = lesson_id
        
        def _update_lesson_progress():
            doc_ref = db.collection("learningProgress").document(uid)
            doc = doc_ref.get()
            
            current_data = doc.to_dict() if doc.exists else {
                "completed_lessons": [],
                "total_time_spent": 0
            }
            
            completed_lessons = current_data.get("completed_lessons", [])
            
            # Find existing lesson progress
            existing_index = next(
                (i for i, lesson in enumerate(completed_lessons)
                 if lesson.get("lesson_id") == lesson_id),
                None
            )
            
            if progress_data.get("completed", False):
                # If completing the lesson, add/update in completed_lessons
                if existing_index is not None:
                    completed_lessons[existing_index].update(progress_data)
                else:
                    completed_lessons.append(progress_data)
                    
                # Clear from current_lesson if it was there
                if current_data.get("current_lesson", {}).get("lesson_id") == lesson_id:
                    current_data["current_lesson"] = None
                    
            else:
                # Update current_lesson for in-progress lessons
                current_data["current_lesson"] = progress_data
            
            # Update total time spent
            current_data["total_time_spent"] = (
                current_data.get("total_time_spent", 0) + 
                (progress_data.get("time_spent", 0) - 
                 (completed_lessons[existing_index].get("time_spent", 0) if existing_index is not None else 0))
            )
            
            # Update the document
            if doc.exists:
                doc_ref.update(current_data)
            else:
                doc_ref.set(current_data)
            
            return progress_data
            
        return await asyncio.get_event_loop().run_in_executor(executor, _update_lesson_progress)
        
    except Exception as e:
        logger.error(f"Error updating lesson progress: {str(e)}")
        raise

