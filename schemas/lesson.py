from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class LessonContentSection(BaseModel):
    """Model for a section of lesson content"""
    title: str
    content: str
    order: int
    type: str = "text"  # text, video, quiz, interactive
    media_url: Optional[str] = None
    
class LessonResource(BaseModel):
    """Model for a lesson resource"""
    title: str
    url: str
    type: str = "link"  # link, pdf, video, etc.
    description: Optional[str] = None
    
class LessonExercise(BaseModel):
    """Model for a lesson exercise"""
    question: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard
    
class LessonBase(BaseModel):
    """Base model for lesson data"""
    subject: str
    topic: str
    title: str
    difficulty: str
    duration_minutes: int
    tags: List[str] = Field(default_factory=list)
    
class LessonGenerateRequest(BaseModel):
    """Request model for generating a lesson"""
    subject: str = Field(..., min_length=2, max_length=50)
    topic: str = Field(..., min_length=2, max_length=100)
    difficulty: str = Field(..., description="Difficulty level: beginner, intermediate, advanced")
    duration_minutes: int = Field(..., ge=5, le=120)
    additional_instructions: Optional[str] = None
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed = ['beginner', 'intermediate', 'advanced']
        if v.lower() not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(allowed)}")
        return v.lower()
        
class LessonResponse(LessonBase):
    """Response model for a lesson"""
    id: str
    content: List[LessonContentSection] = Field(default_factory=list)
    summary: Optional[str] = None
    resources: List[LessonResource] = Field(default_factory=list)
    exercises: List[LessonExercise] = Field(default_factory=list)
    created_at: datetime
    created_by: Optional[str] = None
    
class LessonProgressUpdate(BaseModel):
    """Model for updating lesson progress"""
    progress: float = Field(..., ge=0, le=1.0, description="Progress from 0.0 to 1.0")
    time_spent: int = Field(..., ge=0, description="Time spent in seconds")
    completed: bool = False
    score: Optional[float] = Field(None, ge=0, le=100, description="Score from 0 to 100")
    last_position: Optional[str] = Field(None, description="Last position in the lesson")
    notes: Optional[str] = None
    
class LessonListItem(BaseModel):
    """Simplified lesson model for listing"""
    id: str
    title: str
    subject: str
    topic: str
    difficulty: str
    duration_minutes: int
    created_at: datetime
    tags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    
class LessonListResponse(BaseModel):
    """Response model for lesson listing"""
    lessons: List[LessonListItem]
    total: int
    skip: int
    limit: int

