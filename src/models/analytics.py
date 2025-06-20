import firebase_admin
from firebase_admin import firestore
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import math

from models.user import get_db

# Initialize logger
logger = logging.getLogger(__name__)

# Get the Firestore client
db = get_db()

# Thread pool for running synchronous Firebase operations asynchronously
executor = ThreadPoolExecutor()

async def get_user_completed_lessons(
    user_id: str,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get a list of lessons completed by the user
    
    Args:
        user_id: User ID
        limit: Maximum number of completed lessons to return
        skip: Number of completed lessons to skip
        
    Returns:
        List[Dict]: List of completed lessons with details
    """
    try:
        # Get learning progress
        from models.user import get_learning_progress
        progress = await get_learning_progress(user_id)
        
        if not progress or "completed_lessons" not in progress:
            return []
        
        completed_lessons = progress.get("completed_lessons", [])
        
        # Sort by completion date (newest first)
        completed_lessons.sort(
            key=lambda x: x.get("completion_date", datetime.min), 
            reverse=True
        )
        
        # Apply pagination
        paginated_lessons = completed_lessons[skip:skip+limit]
        
        # Get detailed lesson information
        detailed_lessons = []
        for lesson in paginated_lessons:
            lesson_id = lesson.get("lesson_id")
            if not lesson_id:
                continue
                
            # Get lesson details
            from models.lesson import get_lesson_by_id
            lesson_details = await get_lesson_by_id(lesson_id)
            
            if not lesson_details:
                continue
                
            # Combine lesson details with progress information
            detailed_lessons.append({
                "lesson_id": lesson_id,
                "title": lesson_details.get("title", ""),
                "subject": lesson_details.get("subject", ""),
                "topic": lesson_details.get("topic", ""),
                "difficulty": lesson_details.get("difficulty", ""),
                "completion_date": lesson.get("completion_date", datetime.now()),
                "score": lesson.get("score"),
                "time_spent": lesson.get("time_spent", 0),
                "exercises_completed": lesson.get("exercises_completed", 0),
                "exercises_correct": lesson.get("exercises_correct", 0)
            })
            
        return detailed_lessons
        
    except Exception as e:
        logger.error(f"Error getting completed lessons: {str(e)}")
        raise

async def get_user_completion_stats(user_id: str) -> Dict[str, Any]:
    """
    Get user's completion statistics
    
    Args:
        user_id: User ID
        
    Returns:
        Dict: User completion statistics
    """
    try:
        # Get learning progress
        from models.user import get_learning_progress
        progress = await get_learning_progress(user_id)
        
        if not progress:
            # Return empty stats if no progress data
            return {
                "total_lessons_completed": 0,
                "total_lessons_available": 0,
                "overall_completion_rate": 0.0,
                "total_time_spent": 0,
                "average_score": None,
                "subjects": [],
                "difficulty_distribution": {},
                "last_active": None,
                "streak_days": 0,
                "achievements_earned": 0
            }
            
        # Get completed lessons
        completed_lessons = progress.get("completed_lessons", [])
        total_lessons_completed = len(completed_lessons)
        
        # Get total time spent
        total_time_spent = progress.get("total_time_spent", 0)
        
        # Get last active timestamp
        last_active = progress.get("last_active")
        
        # Calculate average score if available
        scores = [lesson.get("score", 0) for lesson in completed_lessons if lesson.get("score") is not None]
        average_score = sum(scores) / len(scores) if scores else None
        
        # Get available lessons count
        def _get_lesson_count():
            return db.collection("lessons").count().get()[0][0]
            
        total_lessons_available = await asyncio.get_event_loop().run_in_executor(
            executor, _get_lesson_count
        )
        
        # Calculate overall completion rate
        overall_completion_rate = (total_lessons_completed / total_lessons_available) * 100 if total_lessons_available > 0 else 0
        
        # Group lessons by subject
        subjects = {}
        difficulty_distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
        
        for lesson in completed_lessons:
            lesson_id = lesson.get("lesson_id")
            if not lesson_id:
                continue
                
            # Get lesson details
            from models.lesson import get_lesson_by_id
            lesson_details = await get_lesson_by_id(lesson_id)
            
            if not lesson_details:
                continue
                
            subject = lesson_details.get("subject", "")
            difficulty = lesson_details.get("difficulty", "")
            
            # Update difficulty distribution
            if difficulty in difficulty_distribution:
                difficulty_distribution[difficulty] += 1
            
            # Update subject stats
            if subject not in subjects:
                subjects[subject] = {
                    "lessons_completed": 0,
                    "total_time_spent": 0,
                    "scores": []
                }
                
            subjects[subject]["lessons_completed"] += 1
            subjects[subject]["total_time_spent"] += lesson.get("time_spent", 0)
            
            if lesson.get("score") is not None:
                subjects[subject]["scores"].append(lesson.get("score"))
                
        # Get total lessons by subject
        def _get_subject_counts():
            subject_counts = {}
            for subject in subjects.keys():
                count = db.collection("lessons").where("subject", "==", subject).count().get()[0][0]
                subject_counts[subject] = count
            return subject_counts
            
        subject_counts = await asyncio.get_event_loop().run_in_executor(
            executor, _get_subject_counts
        )
        
        # Format subject completion data
        subject_completion = []
        for subject, data in subjects.items():
            total_lessons = subject_counts.get(subject, 0)
            completion_rate = (data["lessons_completed"] / total_lessons) * 100 if total_lessons > 0 else 0
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else None
            
            subject_completion.append({
                "subject": subject,
                "lessons_completed": data["lessons_completed"],
                "total_lessons": total_lessons,
                "completion_rate": completion_rate,
                "average_score": avg_score,
                "total_time_spent": data["total_time_spent"]
            })
            
        # Calculate streak days
        streak_days = 0
        if last_active:
            # Get user activity for the last 30 days
            today = datetime.now().date()
            activity_days = set()
            
            # Get activity records
            def _get_recent_activity():
                thirty_days_ago = datetime.now() - timedelta(days=30)
                return db.collection("userActivity").where("user_id", "==", user_id).where(
                    "timestamp", ">=", thirty_days_ago
                ).order_by("timestamp", direction=firestore.Query.DESCENDING).get()
                
            activity_docs = await asyncio.get_event_loop().run_in_executor(
                executor, _get_recent_activity
            )
            
            # Extract unique activity days
            for doc in activity_docs:
                activity_data = doc.to_dict()
                activity_date = activity_data.get("timestamp").date() if activity_data.get("timestamp") else None
                if activity_date:
                    activity_days.add(activity_date)
            
            # Calculate current streak
            current_date = today
            while current_date in activity_days:
                streak_days += 1
                current_date = current_date - timedelta(days=1)
        
        # Get achievements count
        def _get_achievements_count():
            return db.collection("userAchievements").where("user_id", "==", user_id).count().get()[0][0]
            
        achievements_earned = await asyncio.get_event_loop().run_in_executor(
            executor, _get_achievements_count
        )
        
        return {
            "total_lessons_completed": total_lessons_completed,
            "total_lessons_available": total_lessons_available,
            "overall_completion_rate": overall_completion_rate,
            "total_time_spent": total_time_spent,
            "average_score": average_score,
            "subjects": subject_completion,
            "difficulty_distribution": difficulty_distribution,
            "last_active": last_active,
            "streak_days": streak_days,
            "achievements_earned": achievements_earned
        }
        
    except Exception as e:
        logger.error(f"Error getting completion stats: {str(e)}")
        raise

async def get_user_activity(
    user_id: str,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get recent user activity
    
    Args:
        user_id: User ID
        limit: Maximum number of activity items to return
        skip: Number of activity items to skip
        
    Returns:
        List[Dict]: List of user activity items
    """
    try:
        # Run in thread pool to avoid blocking
        def _get_activity():
            activity_ref = db.collection("userActivity").where(
                "user_id", "==", user_id
            ).order_by(
                "timestamp", direction=firestore.Query.DESCENDING
            ).limit(limit).offset(skip)
            
            docs = activity_ref.get()
            
            activity_items = []
            for doc in docs:
                item = doc.to_dict()
                item["id"] = doc.id
                activity_items.append(item)
                
            return activity_items
            
        activity_items = await asyncio.get_event_loop().run_in_executor(executor, _get_activity)
        
        # Get lesson details for relevant activities
        for item in activity_items:
            if "lesson_id" in item:
                lesson_id = item.get("lesson_id")
                if lesson_id:
                    # Get lesson details
                    from models.lesson import get_lesson_by_id
                    lesson = await get_lesson_by_id(lesson_id)
                    if lesson:
                        item["lesson_title"] = lesson.get("title", "")
                    
        return activity_items
        
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise

async def get_dashboard_metrics(user_id: str, time_range: str = "week") -> Dict[str, Any]:
    """
    Get analytics dashboard metrics
    
    Args:
        user_id: User ID
        time_range: Time range for analytics (day, week, month, year)
        
    Returns:
        Dict: Dashboard metrics and analytics
    """
    try:
        # Calculate date ranges based on specified time range
        now = datetime.now()
        if time_range == "day":
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            prev_start_date = start_date - timedelta(days=1)
            prev_end_date = start_date
        elif time_range == "week":
            # Start from Monday of current week
            start_date = now - timedelta(days=now.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            prev_start_date = start_date - timedelta(days=7)
            prev_end_date = start_date
        elif time_range == "month":
            start_date = datetime(now.year, now.month, 1, 0, 0, 0)
            # Previous month (handling year boundary)
            if now.month == 1:
                prev_start_date = datetime(now.year - 1, 12, 1, 0, 0, 0)
                prev_end_date = datetime(now.year, now.month, 1, 0, 0, 0)
            else:
                prev_start_date = datetime(now.year, now.month - 1, 1, 0, 0, 0)
                prev_end_date = start_date
        elif time_range == "year":
            start_date = datetime(now.year, 1, 1, 0, 0, 0)
            prev_start_date = datetime(now.year - 1, 1, 1, 0, 0, 0)
            prev_end_date = start_date
        else:
            # Default to week if invalid range
            start_date = now - timedelta(days=now.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            prev_start_date = start_date - timedelta(days=7)
            prev_end_date = start_date
            
        # Get activity data for current period
        def _get_period_activity(start_date, end_date=None):
            query = db.collection("userActivity").where("user_id", "==", user_id).where(
                "timestamp", ">=", start_date
            )
            
            if end_date:
                query = query.where("timestamp", "<", end_date)
                
            return query.get()
            
        current_activity_docs = await asyncio.get_event_loop().run_in_executor(
            executor, lambda: _get_period_activity(start_date)
        )
        
        # Get activity data for previous period
        prev_activity_docs = await asyncio.get_event_loop().run_in_executor(
            executor, lambda: _get_period_activity(prev_start_date, prev_end_date)
        )
        
        # Parse activity data
        current_activity = [doc.to_dict() for doc in current_activity_docs]
        prev_activity = [doc.to_dict() for doc in prev_activity_docs]
        
        # Calculate metrics
        
        # 1. Time spent metric
        current_time_spent = sum(item.get("time_spent", 0) for item in current_activity if "time_spent" in item)
        prev_time_spent = sum(item.get("time_spent", 0) for item in prev_activity if "time_spent" in item)
        
        time_spent_change = ((current_time_spent - prev_time_spent) / prev_time_spent * 100) if prev_time_spent > 0 else 0
        time_spent_direction = "up" if time_spent_change > 0 else "down" if time_spent_change < 0 else "flat"
        
        # 2. Lessons completed metric
        current_lessons_completed = len([item for item in current_activity if item.get("type") == "lesson_completion"])
        prev_lessons_completed = len([item for item in prev_activity if item.get("type") == "lesson_completion"])
        
        lessons_change = ((current_lessons_completed - prev_lessons_completed) / prev_lessons_completed * 100) if prev_lessons_completed > 0 else 0
        lessons_direction = "up" if lessons_change > 0 else "down" if lessons_change < 0 else "flat"
        
        # 3. Average score metric
        current_scores = [item.get("score", 0) for item in current_activity if "score" in item and item.get("score") is not None]
        prev_scores = [item.get("score", 0) for item in prev_activity if "score" in item and item.get("score") is not None]
        
        current_avg_score = sum(current_scores) / len(current_scores) if current_scores else 0
        prev_avg_score = sum(prev_scores) / len(prev_scores) if prev_scores else 0
        
        score_change = ((current_avg_score - prev_avg_score) / prev_avg_score * 100) if prev_avg_score > 0 else 0
        score_direction = "up" if score_change > 0 else "down" if score_change < 0 else "flat"
        
        # 4. Active days metric
        current_active_days = len(set(item.get("timestamp").date() for item in current_activity if "timestamp" in item))
        prev_active_days = len(set(item.get("timestamp").date() for item in prev_activity if "timestamp" in item))
        
        days_change = ((current_active_days - prev_active_days) / prev_active_days * 100) if prev_active_days > 0 else 0
        days_direction = "up" if days_change > 0 else "down" if days_change < 0 else "flat"
        
        # Create metrics list
        metrics = [
            {
                "label": "Time Spent",
                "value": math.ceil(current_time_spent / 60),  # Convert to minutes
                "unit": "min",
                "change": time_spent_change,
                "change_direction": time_spent_direction
            },
            {
                "label": "Lessons Completed",
                "value": current_lessons_completed,
                "unit": "",
                "change": lessons_change,
                "change_direction": lessons_direction
            },
            {
                "label": "Average Score",
                "value": round(current_avg_score, 1) if current_scores else 0,
                "unit": "%",
                "change": score_change,
                "change_direction": score_direction
            },
            {
                "label": "Active Days",
                "value": current_active_days,
                "unit": "days",
                "change": days_change,
                "change_direction": days_direction
            }
        ]
        
        # Generate time series data
        time_series = []
        
        # Generate date range based on time_range
        date_points = []
        if time_range == "day":
            # Hourly points for a day
            for hour in range(24):
                date_points.append(datetime(now.year, now.month, now.day, hour, 0, 0))
        elif time_range == "week":
            # Daily points for a week
            for day in range(7):
                date_points.append(start_date + timedelta(days=day))
        elif time_range == "month":
            # Daily points for the month
            month_days = (datetime(now.year, now.month % 12 + 1, 1) if now.month < 12 
                         else datetime(now.year + 1, 1, 1)) - timedelta(days=1)
            for day in range(1, month_days.day + 1):
                date_points.append(datetime(now.year, now.month, day))
        elif time_range == "year":
            # Monthly points for a year
            for month in range(1, 13):
                date_points.append(datetime(now.year, month, 1))
        
        # Time spent time series
        time_spent_data = []
        
        for point in date_points:
            if time_range == "day":
                # For day view, filter by hour
                next_point = point + timedelta(hours=1)
                filtered_items = [item for item in current_activity 
                                 if "timestamp" in item and "time_spent" in item
                                 and point <= item["timestamp"] < next_point]
            elif time_range == "week" or time_range == "month":
                # For week/month view, filter by day
                next_point = datetime(point.year, point.month, point.day) + timedelta(days=1)
                filtered_items = [item for item in current_activity 
                                 if "timestamp" in item and "time_spent" in item
                                 and point <= item["timestamp"] < next_point]
            else:
                # For year view, filter by month
                next_month = point.month % 12 + 1
                next_year = point.year + 1 if next_month == 1 else point.year
                next_point = datetime(next_year, next_month, 1)
                filtered_items = [item for item in current_activity 
                                 if "timestamp" in item and "time_spent" in item
                                 and point <= item["timestamp"] < next_point]
            
            # Sum time spent for this point
            point_time_spent = sum(item.get("time_spent", 0) for item in filtered_items)
            
            # Convert to minutes
            point_time_spent = point_time_spent / 60
            
            time_spent_data.append({
                "date": point.date(),
                "value": point_time_spent
            })
            
        # Add time spent time series
        time_series.append({
            "label": "Time Spent (minutes)",
            "data": time_spent_data
        })
        
        # Subject breakdown
        subject_breakdown = {}
        for item in current_activity:
            if "lesson_id" in item:
                lesson_id = item.get("lesson_id")
                if lesson_id:
                    # Get lesson details
                    from models.lesson import get_lesson_by_id
                    lesson = await get_lesson_by_id(lesson_id)
                    if lesson and "subject" in lesson:
                        subject = lesson.get("subject", "")
                        if subject:
                            time_spent = item.get("time_spent", 0) / 60  # Convert to minutes
                            subject_breakdown[subject] = subject_breakdown.get(subject, 0) + time_spent
        
        # Get recent achievements
        def _get_recent_achievements():
            return db.collection("userAchievements").where(
                "user_id", "==", user_id
            ).order_by(
                "earned_at", direction=firestore.Query.DESCENDING
            ).limit(3).get()
            
        achievement_docs = await asyncio.get_event_loop().run_in_executor(
            executor, _get_recent_achievements
        )
        
        recent_achievements = []
        for doc in achievement_docs:
            achievement = doc.to_dict()
            recent_achievements.append({
                "id": doc.id,
                "name": achievement.get("name", ""),
                "description": achievement.get("description", ""),
                "earned_at": achievement.get("earned_at", datetime.now()),
                "type": achievement.get("type", "")
            })
            
        # Get lesson recommendations
        from models.lesson import get_recommended_lessons
        recommendations = await get_recommended_lessons(user_id, limit=3)
        
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "lesson_id": rec.get("id", ""),
                "title": rec.get("title", ""),
                "subject": rec.get("subject", ""),
                "difficulty": rec.get("difficulty", ""),
                "duration_minutes": rec.get("duration_minutes", 0)
            })
            
        return {
            "time_range": time_range,
            "metrics": metrics,
            "time_series": time_series,
            "subject_breakdown": subject_breakdown,
            "recent_achievements": recent_achievements,
            "recommendations": formatted_recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise

async def log_user_activity(
    user_id: str,
    activity_type: str,
    lesson_id: Optional[str] = None,
    time_spent: Optional[int] = None,
    score: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """
    Log user activity
    
    Args:
        user_id: User ID
        activity_type: Type of activity
        lesson_id: Optional lesson ID
        time_spent: Optional time spent in seconds
        score: Optional score
        details: Optional additional details
        
    Returns:
        str: Activity document ID
    """
    try:
        # Create activity data
        activity_data = {
            "user_id": user_id,
            "type": activity_type,
            "timestamp": datetime.now()
        }
        
        if lesson_id:
            activity_data["lesson_id"] = lesson_id
            
        if time_spent is not None:
            activity_data["time_spent"] = time_spent
            
        if score is not None:
            activity_data["score"] = score
            
        if details:
            activity_data["details"] = details
            
        # Run in thread pool to avoid blocking
        def _log_activity():
            doc_ref = db.collection("userActivity").document()
            doc_ref.set(activity_data)
            return doc_ref.id
            
        return await asyncio.get_event_loop().run_in_executor(executor, _log_activity)
        
    except Exception as e:
        logger.error(f"Error logging user activity: {str(e)}")
        raise
