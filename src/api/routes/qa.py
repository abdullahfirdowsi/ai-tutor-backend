from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    QAHistoryResponse,
    QAItemResponse
)
from models.qa import (
    submit_question,
    get_answer,
    get_qa_history
)
from utils.auth import get_current_user

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    question: QuestionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submit a question and get an AI-generated answer
    
    Args:
        question: The question details
        current_user: Current authenticated user
        
    Returns:
        QuestionResponse: The answer from AI
        
    Raises:
        HTTPException: If question answering fails
    """
    try:
        user_id = current_user["uid"]
        
        # Submit question and get answer
        qa_item = await submit_question(
            user_id=user_id,
            question=question.question,
            context=question.context,
            lesson_id=question.lesson_id
        )
        
        # Get the AI-generated answer
        answer = await get_answer(qa_item)
        
        return QuestionResponse(
            question_id=qa_item.get("id", ""),
            question=question.question,
            answer=answer.get("answer", ""),
            created_at=answer.get("created_at", datetime.now()),
            lesson_id=question.lesson_id,
            references=answer.get("references", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )

@router.get("/history", response_model=QAHistoryResponse)
async def get_history(
    lesson_id: Optional[str] = Query(None, description="Filter by lesson ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the history of Q&A interactions for the current user
    
    Args:
        lesson_id: Optional filter by lesson ID
        limit: Maximum number of items to return
        skip: Number of items to skip (for pagination)
        current_user: Current authenticated user
        
    Returns:
        QAHistoryResponse: List of previous Q&A interactions
    """
    try:
        user_id = current_user["uid"]
        
        # Get Q&A history
        history = await get_qa_history(
            user_id=user_id,
            lesson_id=lesson_id,
            limit=limit,
            skip=skip
        )
        
        # Format response
        items = []
        for item in history:
            try:
                # Skip items that don't have an answer or are not in completed state
                if not item.get("answer") or item.get("status") != "completed":
                    continue
                
                items.append(QAItemResponse(
                    id=item.get("id", ""),
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                    created_at=item.get("created_at", datetime.now()),
                    lesson_id=item.get("lesson_id", None),
                    references=item.get("references", [])
                ))
            except Exception as e:
                logger.error(f"Error processing QA item: {str(e)}")
                # Skip items that cause validation errors
        
        return QAHistoryResponse(
            items=items,
            total=len(items),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving Q&A history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Q&A history"
        )

@router.get("/{question_id}", response_model=QAItemResponse)
async def get_qa_item(
    question_id: str = Path(..., description="The ID of the Q&A item to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific Q&A item by ID
    
    Args:
        question_id: ID of the Q&A item to retrieve
        current_user: Current authenticated user
        
    Returns:
        QAItemResponse: The requested Q&A item
        
    Raises:
        HTTPException: If Q&A item not found
    """
    try:
        user_id = current_user["uid"]
        
        # Get Q&A history filtered by question ID
        history = await get_qa_history(
            user_id=user_id,
            question_id=question_id,
            limit=1,
            skip=0
        )
        
        if not history or len(history) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Q&A item with ID {question_id} not found"
            )
            
        item = history[0]
        
        # Check if the item has the required fields
        if not item.get("answer"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Q&A item with ID {question_id} is not yet complete"
            )
        
        try:
            return QAItemResponse(
                id=item.get("id", ""),
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                created_at=item.get("created_at", datetime.now()),
                lesson_id=item.get("lesson_id", None),
                references=item.get("references", [])
            )
        except Exception as e:
            logger.error(f"Error processing QA item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid QA item data"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Q&A item {question_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Q&A item"
        )

