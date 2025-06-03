from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

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

