from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
@router.get("/sessions", response_model=QASessionListResponse)
async def list_qa_sessions(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions to return"),
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    include_inactive: bool = Query(False, description="Whether to include inactive sessions"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a list of QA sessions for the current user
    
    Args:
        limit: Maximum number of sessions to return
        skip: Number of sessions to skip (for pagination)
        include_inactive: Whether to include inactive sessions
        current_user: Current authenticated user
        
    Returns:
        QASessionListResponse: List of QA sessions
    """
    try:
        user_id = current_user["uid"]
        
        # Get sessions
        sessions = await get_qa_sessions(
            user_id=user_id,
            limit=limit,
            skip=skip,
            include_inactive=include_inactive
        )
        
        return QASessionListResponse(
            sessions=sessions,
            total=len(sessions),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error retrieving QA sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve QA sessions"
        )

@router.post("/sessions", response_model=QASessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session: QASessionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new QA session
    
    Args:
        session: Session creation data
        current_user: Current authenticated user
        
    Returns:
        QASessionResponse: Created session
    """
    try:
        user_id = current_user["uid"]
        
        # Validate lesson ID if provided
        if session.lesson_id:
            from models.lesson import get_lesson_by_id
            lesson = await get_lesson_by_id(session.lesson_id)
            if not lesson:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lesson with ID {session.lesson_id} not found"
                )
        
        # Create session
        created_session = await create_qa_session(
            user_id=user_id,
            title=session.title,
            topic=session.topic,
            lesson_id=session.lesson_id
        )
        
        return QASessionResponse(**created_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating QA session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create QA session"
        )

@router.get("/sessions/{session_id}", response_model=QASessionResponse)
async def get_session(
    session_id: str = Path(..., description="The ID of the session to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific QA session by ID
    
    Args:
        session_id: ID of the session to retrieve
        current_user: Current authenticated user
        
    Returns:
        QASessionResponse: The requested session
        
    Raises:
        HTTPException: If session not found or not authorized
    """
    try:
        user_id = current_user["uid"]
        
        # Get session
        session = await get_qa_session(session_id, user_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QA session with ID {session_id} not found"
            )
            
        return QASessionResponse(**session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving QA session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve QA session"
        )

@router.put("/sessions/{session_id}", response_model=QASessionResponse)
async def update_session(
    session_update: QASessionUpdate,
    session_id: str = Path(..., description="The ID of the session to update"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a QA session
    
    Args:
        session_update: Session update data
        session_id: ID of the session to update
        current_user: Current authenticated user
        
    Returns:
        QASessionResponse: Updated session
        
    Raises:
        HTTPException: If session not found or not authorized
    """
    try:
        user_id = current_user["uid"]
        
        # Update session
        update_data = session_update.dict(exclude_unset=True)
        updated_session = await update_qa_session(session_id, user_id, update_data)
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QA session with ID {session_id} not found"
            )
            
        return QASessionResponse(**updated_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating QA session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update QA session"
        )

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str = Path(..., description="The ID of the session to delete"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a QA session
    
    Args:
        session_id: ID of the session to delete
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If session not found or not authorized
    """
    try:
        user_id = current_user["uid"]
        
        # Delete session
        success = await delete_qa_session(session_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QA session with ID {session_id} not found"
            )
            
        # 204 No Content response (no body)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting QA session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete QA session"
        )
from schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    QAHistoryResponse,
    QAItemResponse,
    QASessionCreate,
    QASessionUpdate,
    QASessionResponse,
    QASessionListResponse
)
from models.qa import (
    submit_question,
    get_answer,
    get_qa_history,
    create_qa_session,
    get_qa_sessions,
    get_qa_session,
    update_qa_session,
    delete_qa_session
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

