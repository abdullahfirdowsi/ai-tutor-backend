import firebase_admin
from firebase_admin import firestore
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.ai import generate_lesson_content
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

async def get_lessons(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
    skip: int = 0,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get a list of lessons with optional filtering
    
    Args:
        subject: Optional subject filter
        difficulty: Optional difficulty level filter
        limit: Maximum number of lessons to return
        skip: Number of lessons to skip
        user_id: Optional user ID to check progress
        
    Returns:
        List[Dict]: List of lesson data
    """
    try:
        def _get_lessons():
            # Start with a base query
            query = get_db().collection("lessons")
            
            # Apply filters if provided
            if subject:
                query = query.where("subject", "==", subject)
            if difficulty:
                query = query.where("difficulty", "==", difficulty)
                
            # Order by creation date
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            # Execute query and get results
            docs = query.stream()
            lessons = []
            
            # Apply pagination manually since Firestore doesn't support skip
            count = 0
            for doc in docs:
                if count < skip:
                    count += 1
                    continue
                    
                if len(lessons) >= limit:
                    break
                    
                lesson_data = doc.to_dict()
                lesson_data["id"] = doc.id
                lessons.append(lesson_data)
                count += 1
                
            return lessons
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_lessons)
        
    except Exception as e:
        logger.error(f"Error getting lessons: {str(e)}")
        raise

async def get_lesson_by_id(lesson_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific lesson by ID
    
    Args:
        lesson_id: ID of the lesson to retrieve
        
    Returns:
        Dict: Lesson data or None if not found
    """
    try:
        def _get_lesson():
            doc_ref = get_db().collection("lessons").document(lesson_id)
            doc = doc_ref.get()
            
            if doc.exists:
                lesson_data = doc.to_dict()
                lesson_data["id"] = doc.id
                return lesson_data
                
            return None
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_lesson)
        
    except Exception as e:
        logger.error(f"Error getting lesson {lesson_id}: {str(e)}")
        raise

async def generate_lesson(
    subject: str,
    topic: str,
    difficulty: str,
    duration_minutes: int,
    additional_instructions: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a new lesson using AI
    
    Args:
        subject: Subject area (e.g., "Mathematics", "Physics")
        topic: Specific topic (e.g., "Linear Algebra", "Quantum Mechanics")
        difficulty: Difficulty level (e.g., "Beginner", "Intermediate", "Advanced")
        duration_minutes: Expected duration in minutes
        additional_instructions: Any additional instructions for the AI
        user_id: ID of the user generating the lesson
        
    Returns:
        Dict: Generated lesson data
    """
    try:
        # Generate unique ID for the lesson
        lesson_id = str(uuid.uuid4())
        
        # Generate lesson content using OpenAI
        lesson_content = await generate_lesson_content(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            additional_instructions=additional_instructions
        )
        
        # Create lesson document
        lesson_data = {
            "subject": subject,
            "topic": topic,
            "title": lesson_content.get("title", f"{subject}: {topic}"),
            "difficulty": difficulty,
            "duration_minutes": duration_minutes,
            "content": lesson_content.get("content", []),
            "summary": lesson_content.get("summary", ""),
            "created_at": datetime.now(),
            "created_by": user_id,
            "tags": lesson_content.get("tags", []),
            "resources": lesson_content.get("resources", []),
            "exercises": lesson_content.get("exercises", [])
        }
        
        # Save to Firestore
        def _save_lesson():
            get_db().collection("lessons").document(lesson_id).set(lesson_data)
            return {**lesson_data, "id": lesson_id}
            
        return await asyncio.get_event_loop().run_in_executor(executor, _save_lesson)
        
    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}")
        raise

async def update_lesson_progress(
    user_id: str,
    lesson_id: str,
    progress_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update a user's progress on a specific lesson
    
    Args:
        user_id: ID of the user
        lesson_id: ID of the lesson
        progress_data: Progress data to update
        
    Returns:
        Dict: Updated progress data
    """
    try:
        # Add timestamp
        progress_data["updated_at"] = datetime.now()
        
        # Create a document ID using user and lesson IDs
        doc_id = f"{user_id}_{lesson_id}"
        
        def _update_progress():
            doc_ref = get_db().collection("lessonProgress").document(doc_id)
            
            # Check if document exists
            doc = doc_ref.get()
            
            if doc.exists:
                # Update existing document
                current_data = doc.to_dict()
                merged_data = {**current_data, **progress_data}
                doc_ref.update(progress_data)
                return merged_data
            else:
                # Create new document with initial data
                initial_data = {
                    "user_id": user_id,
                    "lesson_id": lesson_id,
                    "progress": 0,
                    "started_at": datetime.now(),
                    "last_accessed": datetime.now(),
                    "completed": False,
                    "time_spent": 0,
                    "score": None,
                    **progress_data
                }
                doc_ref.set(initial_data)
                return initial_data
                
        return await asyncio.get_event_loop().run_in_executor(executor, _update_progress)
        
    except Exception as e:
        logger.error(f"Error updating lesson progress: {str(e)}")
        raise

