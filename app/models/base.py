from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, HttpUrl


class Reference(BaseModel):
    """Reference information for a QA message"""
    title: str
    source: str
    url: Optional[HttpUrl] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to Python",
                "source": "Python Documentation",
                "url": "https://docs.python.org/3/tutorial/introduction.html"
            }
        }


class QAMessage(BaseModel):
    """A question-answer message pair"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.now)
    lesson_id: Optional[str] = None
    references: List[Reference] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "What is Python?",
                "answer": "Python is a high-level, interpreted programming language...",
                "created_at": "2023-09-01T12:00:00Z",
                "lesson_id": "123",
                "references": [
                    {
                        "title": "Python Overview",
                        "source": "Python Documentation",
                        "url": "https://www.python.org/about/"
                    }
                ]
            }
        }


class QuestionResponse(BaseModel):
    """Response format from the /api/qa/ask endpoint"""
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.now)
    lesson_id: Optional[str] = None
    references: List[Reference] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "What is Python?",
                "answer": "Python is a high-level, interpreted programming language...",
                "created_at": "2023-09-01T12:00:00Z",
                "lesson_id": "123",
                "references": [
                    {
                        "title": "Python Overview",
                        "source": "Python Documentation",
                        "url": "https://www.python.org/about/"
                    }
                ]
            }
        }


class QASession(BaseModel):
    """A complete QA session including server-generated fields"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    title: str
    topic: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    message_count: int = 0
    lesson_id: Optional[str] = None
    messages: List[QAMessage] = Field(default_factory=list)
    is_active: bool = True
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v, values):
        """Always set updated_at to the current time when the model is updated"""
        return datetime.now()
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123456",
                "title": "Learning Python Basics",
                "topic": "Python Programming",
                "created_at": "2023-09-01T12:00:00Z",
                "updated_at": "2023-09-01T13:00:00Z",
                "message_count": 2,
                "lesson_id": "123",
                "messages": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "question": "What is Python?",
                        "answer": "Python is a high-level, interpreted programming language...",
                        "created_at": "2023-09-01T12:00:00Z",
                        "lesson_id": "123",
                        "references": []
                    }
                ],
                "is_active": True
            }
        }


class QASessionsResponse(BaseModel):
    """Response interface for QA sessions list"""
    sessions: List[QASession]
    total: int
    skip: int
    limit: int
    
    class Config:
        schema_extra = {
            "example": {
                "sessions": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123456",
                        "title": "Learning Python Basics",
                        "topic": "Python Programming",
                        "created_at": "2023-09-01T12:00:00Z",
                        "updated_at": "2023-09-01T13:00:00Z",
                        "message_count": 2,
                        "lesson_id": "123",
                        "messages": [],
                        "is_active": True
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10
            }
        }


class QASessionCreate(BaseModel):
    """Interface for creating a new QA session"""
    title: str = Field(..., min_length=3, max_length=100)
    topic: Optional[str] = Field(None, max_length=100)
    lesson_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Learning Python Basics",
                "topic": "Python Programming",
                "lesson_id": "123"
            }
        }


class UpdateSessionRequest(BaseModel):
    """Interface for updating an existing QA session"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    topic: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Python Session",
                "topic": "Advanced Python",
                "is_active": True
            }
        }


class AskQuestionRequest(BaseModel):
    """Interface for asking a question in a QA session"""
    question: str
    context: Optional[str] = None
    lesson_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is a Python dictionary?",
                "context": "I'm learning about data structures in Python",
                "lesson_id": "123"
            }
        }


class SessionQuestionRequest(AskQuestionRequest):
    """Extended version of AskQuestionRequest that includes session_id"""
    session_id: str
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is a Python dictionary?",
                "context": "I'm learning about data structures in Python",
                "lesson_id": "123",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class QAHistoryResponse(BaseModel):
    """Response for QA history items"""
    items: List[QAMessage]
    total: int
    skip: int
    limit: int
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "question": "What is Python?",
                        "answer": "Python is a high-level, interpreted programming language...",
                        "created_at": "2023-09-01T12:00:00Z",
                        "lesson_id": "123",
                        "references": []
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10
            }
        }


# Additional helper models for request validation and database operations

class QAMessageDB(QAMessage):
    """Database model for QA message with session reference"""
    session_id: str


class UpdateMessageCountRequest(BaseModel):
    """Request to update message count"""
    count: int = Field(..., ge=0)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    status: int
