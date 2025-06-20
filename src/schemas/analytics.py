from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, date

# Activity Models
class ActivityItem(BaseModel):
    """Individual user activity entry"""
    id: str
    type: str = Field(..., description="Type of activity (lesson_completion, quiz_attempt, etc.)")
    timestamp: datetime
    details: Dict[str, Any] = Field(default_factory=dict)
    lesson_id: Optional[str] = None
    lesson_title: Optional[str] = None

class ActivityResponse(BaseModel):
    """Response model for user activity"""
    items: List[ActivityItem] = Field(default_factory=list)
    total: int
    skip: int
    limit: int

# Completion Models
class CompletedLessonDetail(BaseModel):
    """Detailed information about a completed lesson"""
    lesson_id: str
    title: str
    subject: str
    topic: str
    difficulty: str
    completion_date: datetime
    score: Optional[float] = None
    time_spent: int = 0  # Time spent in seconds
    exercises_completed: int = 0
    exercises_correct: int = 0
    
class CompletedLessonsResponse(BaseModel):
    """Response model for completed lessons"""
    lessons: List[CompletedLessonDetail] = Field(default_factory=list)
    total: int
    skip: int
    limit: int

# Statistics Models
class SubjectCompletion(BaseModel):
    """Completion statistics for a specific subject"""
    subject: str
    lessons_completed: int = 0
    total_lessons: int = 0
    completion_rate: float = 0.0
    average_score: Optional[float] = None
    total_time_spent: int = 0  # Time spent in seconds

class CompletionStats(BaseModel):
    """User's overall completion statistics"""
    total_lessons_completed: int = 0
    total_lessons_available: int = 0
    overall_completion_rate: float = 0.0
    total_time_spent: int = 0  # Time spent in seconds
    average_score: Optional[float] = None
    subjects: List[SubjectCompletion] = Field(default_factory=list)
    difficulty_distribution: Dict[str, int] = Field(default_factory=dict)
    last_active: Optional[datetime] = None
    streak_days: int = 0
    achievements_earned: int = 0

# Dashboard Models
class TimeSeriesPoint(BaseModel):
    """Single point in a time series"""
    date: date
    value: float

class TimeSeriesData(BaseModel):
    """Time series data for analytics"""
    label: str
    data: List[TimeSeriesPoint] = Field(default_factory=list)

class DashboardMetric(BaseModel):
    """Individual dashboard metric"""
    label: str
    value: Any
    unit: Optional[str] = None
    change: Optional[float] = None  # Percentage change from previous period
    change_direction: Optional[str] = None  # "up", "down", or "flat"

class DashboardResponse(BaseModel):
    """Response model for analytics dashboard"""
    time_range: str
    metrics: List[DashboardMetric] = Field(default_factory=list)
    time_series: List[TimeSeriesData] = Field(default_factory=list)
    subject_breakdown: Dict[str, float] = Field(default_factory=dict)
    recent_achievements: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
