from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from schemas.analytics import (
    ActivityResponse,
    CompletedLessonsResponse,
    CompletionStats,
    DashboardResponse
)
from models.analytics import (
    get_user_completed_lessons,
    get_user_completion_stats,
    get_user_activity,
    get_dashboard_metrics
)
from utils.auth import get_current_user

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me/completed-lessons", response_model=CompletedLessonsResponse)
async def get_completed_lessons(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a list of lessons completed by the current user
    
    Args:
        limit: Maximum number of completed lessons to return
        skip: Number of completed lessons to skip (for pagination)
        current_user: Current authenticated user
        
    Returns:
        CompletedLessonsResponse: List of completed lessons with details
    """
    try:
        user_id = current_user["uid"]
        
        completed_lessons = await get_user_completed_lessons(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        
        return CompletedLessonsResponse(
            lessons=completed_lessons,
            total=len(completed_lessons),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving completed lessons: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completed lessons"
        )

@router.get("/me/completion-stats", response_model=CompletionStats)
async def get_completion_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get completion statistics for the current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CompletionStats: User's completion statistics
    """
    try:
        user_id = current_user["uid"]
        
        stats = await get_user_completion_stats(user_id)
        
        return CompletionStats(**stats)
        
    except Exception as e:
        logger.error(f"Error retrieving completion stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completion statistics"
        )

@router.get("/me/activity", response_model=ActivityResponse)
async def get_user_recent_activity(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get recent activity for the current user
    
    Args:
        limit: Maximum number of activity items to return
        skip: Number of activity items to skip (for pagination)
        current_user: Current authenticated user
        
    Returns:
        ActivityResponse: List of recent user activity
    """
    try:
        user_id = current_user["uid"]
        
        activity_items = await get_user_activity(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        
        return ActivityResponse(
            items=activity_items,
            total=len(activity_items),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity"
        )

@router.get("/dashboard", response_model=DashboardResponse)
async def get_analytics_dashboard(
    time_range: str = Query("week", description="Time range for analytics (day, week, month, year)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get analytics dashboard data
    
    Args:
        time_range: Time range for analytics (day, week, month, year)
        current_user: Current authenticated user
        
    Returns:
        DashboardResponse: Dashboard metrics and analytics
    """
    try:
        user_id = current_user["uid"]
        
        # Validate time range
        valid_ranges = ["day", "week", "month", "year"]
        if time_range not in valid_ranges:
            time_range = "week"  # Default to week if invalid
            
        dashboard_data = await get_dashboard_metrics(
            user_id=user_id,
            time_range=time_range
        )
        
        return DashboardResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard"
        )
