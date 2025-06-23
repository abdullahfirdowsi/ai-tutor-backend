from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from app.core.auth import AuthUser, get_current_user, get_optional_user
from app.models.base import (
    QASession, 
    QASessionCreate,
    QASessionsResponse, 
    UpdateSessionRequest, 
    AskQuestionRequest,
    QuestionResponse,
    QAMessage,
    QAHistoryResponse,
    UpdateMessageCountRequest
)

# Create API router
router = APIRouter()

# In-memory storage for development (would use a real database in production)
qa_sessions = {}
qa_messages = {}


@router.post("/sessions", response_model=QASession, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: QASessionCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Create a new QA session.
    
    Requires authentication.
    """
    session_id = str(uuid4())
    new_session = QASession(
        id=session_id,
        user_id=current_user.user_id,
        title=session_data.title,
        topic=session_data.topic,
        lesson_id=session_data.lesson_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        message_count=0,
        messages=[],
        is_active=True
    )
    
    # Store in our in-memory database
    qa_sessions[session_id] = new_session
    
    return new_session


@router.get("/sessions", response_model=QASessionsResponse)
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    include_inactive: bool = Query(False),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get a list of QA sessions for the current user.
    
    Requires authentication.
    """
    # Filter sessions for the current user
    user_sessions = [
        session for session in qa_sessions.values()
        if session.user_id == current_user.user_id and (include_inactive or session.is_active)
    ]
    
    # Sort by updated_at in descending order (newest first)
    sorted_sessions = sorted(
        user_sessions, 
        key=lambda x: x.updated_at,
        reverse=True
    )
    
    # Apply pagination
    paginated_sessions = sorted_sessions[skip:skip + limit]
    
    # Return with pagination info
    return QASessionsResponse(
        sessions=paginated_sessions,
        total=len(user_sessions),
        skip=skip,
        limit=limit
    )


@router.get("/sessions/{session_id}", response_model=QASession)
async def get_session(
    session_id: str = Path(..., title="The ID of the QA session to retrieve"),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get a specific QA session by ID.
    
    Requires authentication.
    """
    # Check if session exists
    if session_id not in qa_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Retrieve session
    session = qa_sessions[session_id]
    
    # Check if user owns this session
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session"
        )
    
    return session


@router.patch("/sessions/{session_id}", response_model=QASession)
async def update_session(
    update_data: UpdateSessionRequest,
    session_id: str = Path(..., title="The ID of the QA session to update"),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Update a QA session.
    
    Requires authentication.
    """
    # Check if session exists
    if session_id not in qa_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Get the session
    session = qa_sessions[session_id]
    
    # Check if user owns this session
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this session"
        )
    
    # Update session fields
    if update_data.title is not None:
        session.title = update_data.title
    
    if update_data.topic is not None:
        session.topic = update_data.topic
    
    if update_data.is_active is not None:
        session.is_active = update_data.is_active
    
    # Update timestamp
    session.updated_at = datetime.now()
    
    # Save updated session
    qa_sessions[session_id] = session
    
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str = Path(..., title="The ID of the QA session to delete"),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Delete a QA session.
    
    Requires authentication.
    """
    # Check if session exists
    if session_id not in qa_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Get the session
    session = qa_sessions[session_id]
    
    # Check if user owns this session
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this session"
        )
    
    # Delete the session
    del qa_sessions[session_id]
    
    # Delete associated messages
    qa_messages = {k: v for k, v in qa_messages.items() if not k.startswith(f"{session_id}:")}
    
    return None


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    question_data: AskQuestionRequest,
    user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Ask a question without associating it with a session.
    
    Authentication is optional.
    """
    # Generate question ID
    question_id = str(uuid4())
    
    # In a real implementation, this would call an LLM service
    # For this demo, we'll use a mock response
    answer = f"This is a mock answer to: {question_data.question}"
    
    # Create response
    response = QuestionResponse(
        question_id=question_id,
        question=question_data.question,
        answer=answer,
        created_at=datetime.now(),
        lesson_id=question_data.lesson_id,
        references=[]
    )
    
    # Store the message if the user is authenticated
    if user:
        qa_messages[question_id] = QAMessage(
            id=question_id,
            question=question_data.question,
            answer=answer,
            created_at=response.created_at,
            lesson_id=question_data.lesson_id,
            references=[]
        )
    
    return response


@router.post("/sessions/{session_id}/ask", response_model=QuestionResponse)
async def ask_session_question(
    question_data: AskQuestionRequest,
    session_id: str = Path(..., title="The ID of the QA session to add the question to"),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Ask a question and associate it with a session.
    
    Requires authentication.
    """
    # Check if session exists
    if session_id not in qa_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Get the session
    session = qa_sessions[session_id]
    
    # Check if user owns this session
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add questions to this session"
        )
    
    # Generate question ID
    question_id = str(uuid4())
    
    # In a real implementation, this would call an LLM service
    # For this demo, we'll use a mock response
    answer = f"This is a mock answer to: {question_data.question}"
    
    # Create message
    message = QAMessage(
        id=question_id,
        question=question_data.question,
        answer=answer,
        created_at=datetime.now(),
        lesson_id=question_data.lesson_id,
        references=[]
    )
    
    # Add message to session
    session.messages.append(message)
    session.message_count = len(session.messages)
    session.updated_at = datetime.now()
    
    # Store message in our message collection too
    qa_messages[f"{session_id}:{question_id}"] = message
    
    # Save updated session
    qa_sessions[session_id] = session
    
    # Create response
    response = QuestionResponse(
        question_id=message.id,
        question=message.question,
        answer=message.answer,
        created_at=message.created_at,
        lesson_id=message.lesson_id,
        references=message.references
    )
    
    return response


@router.patch("/sessions/{session_id}/message-count", response_model=QASession)
async def update_message_count(
    update_data: UpdateMessageCountRequest,
    session_id: str = Path(..., title="The ID of the QA session to update"),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Update the message count for a session.
    
    Requires authentication.
    """
    # Check if session exists
    if session_id not in qa_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Get the session
    session = qa_sessions[session_id]
    
    # Check if user owns this session
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this session"
        )
    
    # Update message count
    session.message_count = update_data.count
    
    # Update timestamp
    session.updated_at = datetime.now()
    
    # Save updated session
    qa_sessions[session_id] = session
    
    return session


@router.get("/history", response_model=QAHistoryResponse)
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    lesson_id: Optional[str] = Query(None),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get QA history for the current user.
    
    Requires authentication.
    """
    # Filter messages for the current user
    # In a real implementation, this would query the database
    user_messages = []
    
    # Gather all messages from user's sessions
    for session in qa_sessions.values():
        if session.user_id == current_user.user_id:
            user_messages.extend(session.messages)
    
    # Filter by lesson_id if provided
    if lesson_id:
        user_messages = [msg for msg in user_messages if msg.lesson_id == lesson_id]
    
    # Sort by created_at in descending order (newest first)
    sorted_messages = sorted(
        user_messages, 
        key=lambda x: x.created_at, 
        reverse=True
    )
    
    # Apply pagination
    paginated_messages = sorted_messages[skip:skip + limit]
    
    # Return with pagination info
    return QAHistoryResponse(
        items=paginated_messages,
        total=len(user_messages),
        skip=skip,
        limit=limit
    )
