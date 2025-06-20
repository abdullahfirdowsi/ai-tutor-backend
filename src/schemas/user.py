from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
class LearningPreferences(BaseModel):
    """User learning preferences settings"""
    difficulty_preference: Optional[str] = Field(None, description="Preferred difficulty level")
    lesson_duration_preference: Optional[int] = Field(None, description="Preferred lesson duration in minutes")
    daily_goal: Optional[int] = Field(None, description="Daily learning goal in minutes")
    weekly_goal: Optional[int] = Field(None, description="Weekly learning goal in minutes")
    preferred_subjects: List[str] = Field(default_factory=list, description="List of preferred subjects")
    learning_style: Optional[str] = Field(None, description="Preferred learning style")
    ai_assistance_level: Optional[str] = Field(None, description="AI assistance level preference")


class UserActivityResponse(BaseModel):
    """User's recent activity response model"""
    activities: List[Dict[str, Any]] = Field(default_factory=list, description="List of user's recent activities")
    total: int = Field(0, description="Total number of activities returned")
class NotificationSettings(BaseModel):
    """User notification settings"""
    email_notifications: bool = Field(True, description="Enable email notifications")
    push_notifications: bool = Field(True, description="Enable push notifications")
    daily_reminders: bool = Field(True, description="Enable daily reminders")
    weekly_progress_reports: bool = Field(True, description="Enable weekly progress reports")
    achievement_notifications: bool = Field(True, description="Enable achievement notifications")
    lesson_recommendations: bool = Field(True, description="Enable lesson recommendations")
    reminder_time: Optional[str] = Field(None, description="Preferred time for reminders")

class PrivacySettings(BaseModel):
    """User privacy settings"""
    profile_visibility: str = Field("private", description="Profile visibility setting")
    share_progress: bool = Field(False, description="Share learning progress with others")
    data_collection: bool = Field(True, description="Allow data collection for personalization")
    analytics_tracking: bool = Field(True, description="Allow analytics tracking")

class AccessibilitySettings(BaseModel):
    """User accessibility settings"""
    font_size: str = Field("medium", description="Font size preference")
    high_contrast: bool = Field(False, description="Enable high contrast mode")
    reduce_motion: bool = Field(False, description="Reduce motion in animations")
    screen_reader_support: bool = Field(False, description="Enable screen reader support")

class LocalizationSettings(BaseModel):
    """User localization settings"""
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")
    date_format: str = Field("MM/DD/YYYY", description="Preferred date format")
    time_format: str = Field("12h", description="Preferred time format")

class UserSettings(BaseModel):
    """Complete user settings model"""
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings)
    localization: LocalizationSettings = Field(default_factory=LocalizationSettings)

class UserSettingsResponse(UserSettings):
    """User settings response model"""
    user_id: str
    updated_at: Optional[datetime] = None
class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    """User creation model with password"""
    password: str = Field(..., min_length=8)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr

class UserResponse(BaseModel):
    """User response after authentication"""
    uid: str
    email: str
    display_name: str
    token: str

class UserProfileUpdate(BaseModel):
    """User profile update model"""
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserProfileResponse(BaseModel):
    """User profile response model"""
    uid: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class LessonProgress(BaseModel):
    """Model for tracking progress in a specific lesson"""
    lesson_id: str
    title: str
    completed: bool
    completion_date: Optional[datetime] = None
    score: Optional[float] = None
    time_spent: int = 0  # Time spent in seconds

class CurrentLesson(BaseModel):
    """Model for the user's current lesson"""
    lesson_id: str
    title: str
    progress: float = 0.0  # 0.0 to 1.0
    last_position: Optional[str] = None  # Last section or position in the lesson

class LearningProgressResponse(BaseModel):
    """User's learning progress response model"""
    completed_lessons: List[LessonProgress] = Field(default_factory=list)
    current_lesson: Optional[CurrentLesson] = None
    total_time_spent: int = 0  # Total time spent in seconds
    statistics: Dict[str, Any] = Field(default_factory=dict)
    last_active: Optional[datetime] = None

