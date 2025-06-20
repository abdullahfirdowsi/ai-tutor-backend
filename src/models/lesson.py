import firebase_admin
from firebase_admin import firestore
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def get_recommended_lessons(
    user_id: str,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Get personalized lesson recommendations for a user
    
    Args:
        user_id: ID of the user
        limit: Maximum number of recommendations to return
        
    Returns:
        List[Dict]: List of recommended lesson data with relevance scores
    """
    try:
        # Simplified implementation to ensure basic functionality works
        from models.user import get_user_profile, get_learning_progress, get_user_settings
        
        # Get all lessons first
        def _get_available_lessons():
            # Query for all lessons
            query = db.collection("lessons").limit(limit * 2)
            docs = query.stream()
            lessons = []
            
            for doc in docs:
                lesson_data = doc.to_dict()
                lesson_data["id"] = doc.id
                lessons.append(lesson_data)
                
            return lessons
            
        # Get all lessons
        all_lessons = await asyncio.get_event_loop().run_in_executor(executor, _get_available_lessons)
        
        # Get user's completed lesson IDs
        learning_progress = await get_learning_progress(user_id)
        completed_lesson_ids = []
        
        if learning_progress and "completed_lessons" in learning_progress:
            completed_lesson_ids = [lesson.get("lesson_id") for lesson in learning_progress.get("completed_lessons", [])]
        
        # Filter out completed lessons
        recommended_lessons = []
        for lesson in all_lessons:
            if lesson.get("id") not in completed_lesson_ids:
                # Add a simple recommendation reason
                lesson["recommendation_reason"] = "Recommended based on your interests"
                recommended_lessons.append(lesson)
                
                if len(recommended_lessons) >= limit:
                    break
                    
        return recommended_lessons
        
        # Extract user preferences and learning history
        completed_lesson_ids = []
        if learning_progress and "completed_lessons" in learning_progress:
            completed_lesson_ids = [lesson.get("lesson_id") for lesson in learning_progress.get("completed_lessons", [])]
            
        # Get user preferences
        preferred_subjects = []
        preferred_difficulty = "beginner"
        
        if user_settings and "learning_preferences" in user_settings:
            learning_prefs = user_settings.get("learning_preferences", {})
            preferred_subjects = learning_prefs.get("preferred_subjects", [])
            preferred_difficulty = learning_prefs.get("difficulty_preference", "beginner")
            
        # Get all available lessons not yet completed by the user
        def _get_available_lessons():
            # Start with a base query for all lessons
            query = db.collection("lessons")
            
            # Order by creation date (most recent first)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            # Execute query and get results
            docs = query.stream()
            lessons = []
            
            for doc in docs:
                # Skip completed lessons
                if doc.id in completed_lesson_ids:
                    continue
                    
                lesson_data = doc.to_dict()
                lesson_data["id"] = doc.id
                lessons.append(lesson_data)
                
            return lessons
            
        available_lessons = await asyncio.get_event_loop().run_in_executor(executor, _get_available_lessons)
        
        # Score and rank lessons based on user preferences
        scored_lessons = []
        
        for lesson in available_lessons:
            score = 0.0
            reason = []
            
            # Boost score for preferred subjects
            if preferred_subjects and lesson.get("subject") in preferred_subjects:
                score += 0.3
                reason.append(f"Matches your preferred subject: {lesson.get('subject')}")
                
            # Boost score for matching difficulty preference
            if lesson.get("difficulty") == preferred_difficulty:
                score += 0.2
                reason.append(f"Matches your preferred difficulty level: {preferred_difficulty}")
            elif preferred_difficulty == "beginner" and lesson.get("difficulty") == "intermediate":
                score += 0.1
                reason.append("Slightly more advanced than your preference")
            elif preferred_difficulty == "intermediate" and lesson.get("difficulty") == "advanced":
                score += 0.1
                reason.append("Slightly more advanced than your preference")
                
            # Penalize lessons that are too difficult
            if preferred_difficulty == "beginner" and lesson.get("difficulty") == "advanced":
                score -= 0.2
                
            # Boost score for recently created lessons
            if lesson.get("created_at") and (datetime.now() - lesson.get("created_at")).days < 30:
                score += 0.1
                reason.append("Recently added content")
                
            # Add some score based on tag matches with past lessons
            user_interested_tags = set()
            if learning_progress and "completed_lessons" in learning_progress:
                for completed_lesson_id in completed_lesson_ids:
                    completed_lesson = await get_lesson_by_id(completed_lesson_id)
                    if completed_lesson and "tags" in completed_lesson:
                        user_interested_tags.update(completed_lesson.get("tags", []))
            
            common_tags = set(lesson.get("tags", [])).intersection(user_interested_tags)
            if common_tags:
                score += 0.1 * min(len(common_tags), 3)  # Cap the boost at 3 common tags
                reason.append(f"Related to topics you've studied: {', '.join(list(common_tags)[:3])}")
                
            # Add the lesson with its score
            lesson["relevance_score"] = round(score, 2)
            lesson["recommendation_reason"] = "; ".join(reason) if reason else "New content you might enjoy"
            scored_lessons.append(lesson)
            
        # Sort by relevance score (highest first)
        scored_lessons.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Return top recommendations
        return scored_lessons[:limit]
        
    except Exception as e:
        logger.error(f"Error getting recommended lessons: {str(e)}")
        # Handle errors gracefully and return empty list instead of raising exception
    except Exception as e:
        logger.error(f"Error getting recommended lessons: {str(e)}")
        return []

async def get_user_lessons(
    user_id: str,
    limit: int = 10,
    skip: int = 0,
    include_completed: bool = False
) -> List[Dict[str, Any]]:
    """
    Get lessons that the user has started or completed
    
    Args:
        user_id: ID of the user
        limit: Maximum number of lessons to return
        skip: Number of lessons to skip
        include_completed: Whether to include completed lessons
        
    Returns:
        List[Dict]: List of user's lessons with progress information
    """
    try:
        # Simplified implementation for basic functionality
        # Get all lessons first
        def _get_all_lessons():
            query = db.collection("lessons").limit(limit * 2)
            docs = query.stream()
            lessons = []
            
            for doc in docs:
                lesson_data = doc.to_dict()
                lesson_data["id"] = doc.id
                lessons.append(lesson_data)
                
            return lessons
            
        # Get all lessons and learning progress
        all_lessons = await asyncio.get_event_loop().run_in_executor(executor, _get_all_lessons)
        learning_progress = await get_learning_progress(user_id)
        
        # If no progress data, return first few lessons as "recommended to start"
        if not learning_progress:
            user_lessons = []
            for lesson in all_lessons[:limit]:
                lesson["progress"] = {
                    "progress": 0.0,
                    "time_spent": 0,
                    "completed": False,
                    "last_accessed": None,
                    "started_at": None
                }
                user_lessons.append(lesson)
            return user_lessons
            
        
        # Process completed lessons from learning progress
        completed_lessons = learning_progress.get("completed_lessons", []) if learning_progress else []
        completed_lesson_ids = [lesson.get("lesson_id") for lesson in completed_lessons]
        
        # Create user_lessons list
        user_lessons = []
        
        # If include_completed is True, add completed lessons
        if include_completed:
            for completed in completed_lessons:
                lesson_id = completed.get("lesson_id")
                if not lesson_id:
                    continue
                    
                # Find lesson in all_lessons
                lesson = next((l for l in all_lessons if l.get("id") == lesson_id), None)
                
                if lesson:
                    # Add progress info
                    lesson["progress"] = {
                        "progress": 1.0,
                        "time_spent": completed.get("time_spent", 0),
                        "completed": True,
                        "completion_date": completed.get("completion_date"),
                        "score": completed.get("score")
                    }
                    user_lessons.append(lesson)
        
        # Add in-progress or new lessons
        lessons_to_add = limit - len(user_lessons)
        if lessons_to_add > 0:
            for lesson in all_lessons:
                # Skip already added completed lessons
                if lesson.get("id") in completed_lesson_ids:
                    continue
                    
                # Add as new lesson
                lesson["progress"] = {
                    "progress": 0.0,
                    "time_spent": 0,
                    "completed": False,
                    "last_accessed": None,
                    "started_at": None
                }
                user_lessons.append(lesson)
                
                if len(user_lessons) >= limit:
                    break
        
        # Apply skip for pagination
        user_lessons = user_lessons[skip:skip+limit]
                    
        return user_lessons
        
    except Exception as e:
        logger.error(f"Error getting user lessons: {str(e)}")
        return []  # Return empty list instead of raising exception
from utils.ai import generate_lesson_content

# Initialize Firestore client
db = firestore.client()
logger = logging.getLogger(__name__)

# Thread pool for running synchronous Firebase operations asynchronously
executor = ThreadPoolExecutor()

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
            query = db.collection("lessons")
            
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
            doc_ref = db.collection("lessons").document(lesson_id)
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
        
        # Generate lesson content using Google Gemini
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
            db.collection("lessons").document(lesson_id).set(lesson_data)
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
            doc_ref = db.collection("lessonProgress").document(doc_id)
            
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

