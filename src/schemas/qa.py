from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
class QAMessageReference(BaseModel):
    """Model for a reference in a QA message"""
    title: str
    source: str
    url: Optional[str] = None
    
class QAMessage(BaseModel):
    """Model for a message in a QA session"""
    id: str
    question: str
    answer: str
    created_at: datetime
    references: List[QAMessageReference] = Field(default_factory=list)
    
class QASessionBase(BaseModel):
    """Base model for a QA session"""
    title: str = Field(..., min_length=3, max_length=100)
    topic: Optional[str] = Field(None, max_length=100)
    lesson_id: Optional[str] = None
    
class QASessionCreate(QASessionBase):
    """Model for creating a new QA session"""
    pass
    
class QASessionUpdate(BaseModel):
    """Model for updating a QA session"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    topic: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    
class QASessionResponse(QASessionBase):
    """Response model for a QA session"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    is_active: bool = True
    messages: List[QAMessage] = Field(default_factory=list)
    
class QASessionListItem(BaseModel):
    """Model for a QA session in a list"""
    id: str
    title: str
    topic: Optional[str] = None
    lesson_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    is_active: bool = True
    
class QASessionListResponse(BaseModel):
    """Response model for listing QA sessions"""
    sessions: List[QASessionListItem]
    total: int
    skip: int
    limit: int
class Reference(BaseModel):
    """Model for a reference used in an answer"""
    title: str
    source: str
    url: Optional[str] = None
    
class QuestionRequest(BaseModel):
    """Request model for submitting a question"""
    question: str = Field(..., min_length=5, max_length=1000)
    context: Optional[str] = Field(None, max_length=2000)
    lesson_id: Optional[str] = None
    
class QuestionResponse(BaseModel):
    """Response model for a question and answer"""
    question_id: str
    question: str
    answer: str
    created_at: datetime
    lesson_id: Optional[str] = None
    references: List[Reference] = Field(default_factory=list)
    
class QAItemResponse(BaseModel):
    """Model for a Q&A item in history"""
    id: str
    question: str
    answer: str
    created_at: datetime
    lesson_id: Optional[str] = None
    references: List[Reference] = Field(default_factory=list)
    
class QAHistoryResponse(BaseModel):
    """Response model for Q&A history"""
    items: List[QAItemResponse]
    total: int
    skip: int
    limit: int

