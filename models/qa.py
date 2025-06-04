import firebase_admin
from firebase_admin import firestore
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.ai import generate_answer
from utils.firebase import get_firestore_client

logger = logging.getLogger(__name__)

# Thread pool for running synchronous Firebase operations asynchronously
executor = ThreadPoolExecutor()

def get_db():
    """
    Get the Firestore client instance lazily.
    This ensures Firebase is properly initialized before accessing Firestore.
    
    Returns:
        firestore.Client: Firestore client
    """
    return get_firestore_client()

async def submit_question(
    user_id: str,
    question: str,
    context: Optional[str] = None,
    lesson_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit a question and store it in Firestore
    
    Args:
        user_id: ID of the user asking the question
        question: The question text
        context: Optional context for the question
        lesson_id: Optional lesson ID if related to a specific lesson
        
    Returns:
        Dict: Created question data
    """
    try:
        # Generate a unique ID for the question
        question_id = str(uuid.uuid4())
        
        # Create question document
        question_data = {
            "id": question_id,
            "user_id": user_id,
            "question": question,
            "context": context,
            "lesson_id": lesson_id,
            "created_at": datetime.now(),
            "status": "pending",  # pending, completed, failed
            "answer": None,
            "answer_created_at": None,
            "references": []
        }
        
        # Save to Firestore
        def _save_question():
            get_db().collection("qa").document(question_id).set(question_data)
            return question_data
            
        return await asyncio.get_event_loop().run_in_executor(executor, _save_question)
        
    except Exception as e:
        logger.error(f"Error submitting question: {str(e)}")
        raise

async def get_answer(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an answer for a question using AI
    
    Args:
        question_data: Question data dictionary
        
    Returns:
        Dict: Updated question data with answer
    """
    try:
        question_id = question_data.get("id")
        
        # Check if answer already exists
        if question_data.get("status") == "completed" and question_data.get("answer"):
            return question_data
            
        # Get related lesson content if lesson_id is provided
        lesson_content = None
        if question_data.get("lesson_id"):
            from models.lesson import get_lesson_by_id
            lesson = await get_lesson_by_id(question_data.get("lesson_id"))
            if lesson:
                lesson_content = lesson.get("content")
                
        # Generate answer using Google Gemini
        answer_data = await generate_answer(
            question=question_data.get("question"),
            context=question_data.get("context"),
            lesson_content=lesson_content
        )
        
        # Update question document with answer
        update_data = {
            "answer": answer_data.get("answer"),
            "answer_created_at": datetime.now(),
            "status": "completed",
            "references": answer_data.get("references", [])
        }
        
        # Save to Firestore
        def _update_answer():
            get_db().collection("qa").document(question_id).update(update_data)
            return {**question_data, **update_data}
            
        return await asyncio.get_event_loop().run_in_executor(executor, _update_answer)
        
    except Exception as e:
        # Update status to failed
        if question_id:
            def _mark_failed():
                get_db().collection("qa").document(question_id).update({
                    "status": "failed",
                    "error": str(e)
                })
                
            await asyncio.get_event_loop().run_in_executor(executor, _mark_failed)
            
        logger.error(f"Error generating answer: {str(e)}")
        raise

async def get_qa_history(
    user_id: str,
    lesson_id: Optional[str] = None,
    question_id: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get Q&A history for a user
    
    Args:
        user_id: ID of the user
        lesson_id: Optional filter by lesson ID
        question_id: Optional filter by question ID
        limit: Maximum number of items to return
        skip: Number of items to skip
        
    Returns:
        List[Dict]: List of Q&A items
    """
    try:
        def _get_history():
            # Start with a base query
            query = get_db().collection("qa").where("user_id", "==", user_id)
            
            # Apply filters if provided
            if lesson_id:
                query = query.where("lesson_id", "==", lesson_id)
                
            if question_id:
                # If question ID is provided, we're looking for a specific item
                doc = get_db().collection("qa").document(question_id).get()
                if doc.exists and doc.to_dict().get("user_id") == user_id:
                    return [doc.to_dict()]
                return []
                
            # Order by creation date
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            # Execute query and get results
            docs = query.stream()
            qa_items = []
            
            # Apply pagination manually
            count = 0
            for doc in docs:
                if count < skip:
                    count += 1
                    continue
                    
                if len(qa_items) >= limit:
                    break
                    
                qa_items.append(doc.to_dict())
                count += 1
                
            return qa_items
            
        return await asyncio.get_event_loop().run_in_executor(executor, _get_history)
        
    except Exception as e:
        logger.error(f"Error getting Q&A history: {str(e)}")
        raise

