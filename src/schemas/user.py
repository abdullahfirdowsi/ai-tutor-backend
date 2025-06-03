from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

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

