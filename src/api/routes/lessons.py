from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
@router.get("/recommended", response_model=RecommendedLessonsResponse)
async def get_lesson_recommendations(
    limit: int = Query(3, ge=1, le=10, description="Maximum number of recommendations to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get personalized lesson recommendations for the current user
    
    Args:
        limit: Maximum number of recommendations to return
        current_user: Current authenticated user
        
    Returns:
        RecommendedLessonsResponse: List of recommended lessons
    """
    try:
        user_id = current_user["uid"]
        
        # Get personalized recommendations
        recommendations = await get_recommended_lessons(
            user_id=user_id,
            limit=limit
        )
        
        return RecommendedLessonsResponse(
            lessons=recommendations,
            total=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving lesson recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson recommendations"
        )

@router.get("/my-lessons", response_model=UserLessonsResponse)
async def get_my_lessons(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of lessons to return"),
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    include_completed: bool = Query(False, description="Include completed lessons"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the current user's in-progress or completed lessons
    
    Args:
        limit: Maximum number of lessons to return
        skip: Number of lessons to skip (for pagination)
        include_completed: Whether to include completed lessons
        current_user: Current authenticated user
        
    Returns:
        UserLessonsResponse: List of user's lessons with progress information
    """
    try:
        user_id = current_user["uid"]
        
        # Get user's lessons
        user_lessons = await get_user_lessons(
            user_id=user_id,
            limit=limit,
            skip=skip,
            include_completed=include_completed
        )
        
        return UserLessonsResponse(
            lessons=user_lessons,
            total=len(user_lessons),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user lessons: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user lessons"
        )
from schemas.lesson import (
    LessonListResponse,
    LessonResponse,
    LessonGenerateRequest,
    LessonProgressUpdate,
    RecommendedLessonsResponse,
    UserLessonsResponse
)
from models.lesson import (
    get_lessons,
    get_lesson_by_id,
    generate_lesson,
    update_lesson_progress,
    get_recommended_lessons,
    get_user_lessons
)
from models.user import update_learning_progress
from utils.auth import get_current_user

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=LessonListResponse)
async def list_lessons(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of lessons to return"),
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a list of available lessons with optional filtering
    
    Args:
        subject: Optional subject filter
        difficulty: Optional difficulty level filter
        limit: Maximum number of lessons to return
        skip: Number of lessons to skip (for pagination)
        current_user: Current authenticated user
        
    Returns:
        LessonListResponse: List of lessons matching criteria
    """
    try:
        lessons = await get_lessons(
            subject=subject,
            difficulty=difficulty,
            limit=limit,
            skip=skip,
            user_id=current_user["uid"]
        )
        
        return LessonListResponse(
            lessons=lessons,
            total=len(lessons),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving lessons: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lessons"
        )

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str = Path(..., description="The ID of the lesson to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific lesson by ID
    
    Args:
        lesson_id: ID of the lesson to retrieve
        current_user: Current authenticated user
        
    Returns:
        LessonResponse: The requested lesson
        
    Raises:
        HTTPException: If lesson not found
    """
    try:
        lesson = await get_lesson_by_id(lesson_id)
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with ID {lesson_id} not found"
            )
            
        # Update last accessed time for the lesson
        await update_lesson_progress(
            user_id=current_user["uid"],
            lesson_id=lesson_id,
            progress_data={
                "last_accessed": datetime.now()
            }
        )
            
        return LessonResponse(**lesson)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lesson {lesson_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson"
        )

@router.post("/generate", response_model=LessonResponse)
async def create_lesson(
    request: LessonGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a new lesson using AI
    
    Args:
        request: Lesson generation parameters
        current_user: Current authenticated user
        
    Returns:
        LessonResponse: The generated lesson
        
    Raises:
        HTTPException: If lesson generation fails
    """
    try:
        # Generate lesson with Google Gemini
        lesson = await generate_lesson(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            duration_minutes=request.duration_minutes,
            additional_instructions=request.additional_instructions,
            user_id=current_user["uid"]
        )
        
        return LessonResponse(**lesson)
        
    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate lesson: {str(e)}"
        )

@router.post("/{lesson_id}/progress", status_code=status.HTTP_200_OK)
async def track_progress(
    lesson_id: str = Path(..., description="The ID of the lesson"),
    progress: LessonProgressUpdate = ...,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a user's progress on a specific lesson
    
    Args:
        lesson_id: ID of the lesson
        progress: Progress update data
        current_user: Current authenticated user
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If progress update fails
    """
    try:
        user_id = current_user["uid"]
        
        # Update lesson progress
        await update_lesson_progress(
            user_id=user_id,
            lesson_id=lesson_id,
            progress_data=progress.dict()
        )
        
        # If lesson is completed, update learning progress
        if progress.completed:
            lesson = await get_lesson_by_id(lesson_id)
            
            if lesson:
                # Get current learning progress
                from models.user import get_learning_progress
                learning_progress = await get_learning_progress(user_id) or {}
                
                # Get or initialize completed lessons
                completed_lessons = learning_progress.get("completed_lessons", [])
                
                # Add this lesson if not already in the list
                if not any(l.get("lesson_id") == lesson_id for l in completed_lessons):
                    completed_lessons.append({
                        "lesson_id": lesson_id,
                        "title": lesson.get("title", ""),
                        "completed": True,
                        "completion_date": datetime.now(),
                        "score": progress.score,
                        "time_spent": progress.time_spent
                    })
                
                    # Update user's learning progress
                    await update_learning_progress(user_id, {
                        "completed_lessons": completed_lessons,
                        "total_time_spent": learning_progress.get("total_time_spent", 0) + progress.time_spent
                    })
        
        return {"message": "Progress updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating progress for lesson {lesson_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lesson progress"
        )

