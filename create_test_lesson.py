#!/usr/bin/env python3
"""
Script to create a test lesson with ID 'lesson-123'
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.firebase import initialize_firebase

async def create_test_lesson():
    """Create a test lesson with ID lesson-123"""
    try:
        # Initialize Firebase first
        initialize_firebase()
        
        # Import after Firebase is initialized
        from utils.firebase import get_firestore_client
        
        db = get_firestore_client()
        
        print("🔧 Creating test lesson with ID 'lesson-123'...")
        
        # Create test lesson data
        lesson_data = {
            "subject": "Mathematics",
            "topic": "Basic Algebra",
            "title": "Introduction to Basic Algebra",
            "difficulty": "beginner",
            "duration_minutes": 30,
            "content": [
                {
                    "title": "What is Algebra?",
                    "content": "Algebra is a branch of mathematics that uses letters and symbols to represent numbers and quantities in formulas and equations.",
                    "order": 1,
                    "type": "text"
                },
                {
                    "title": "Variables and Constants",
                    "content": "In algebra, a variable is a symbol (usually a letter) that represents an unknown value. A constant is a fixed value that doesn't change.",
                    "order": 2,
                    "type": "text"
                },
                {
                    "title": "Basic Operations",
                    "content": "Algebra uses the same four basic operations as arithmetic: addition (+), subtraction (-), multiplication (×), and division (÷).",
                    "order": 3,
                    "type": "text"
                }
            ],
            "summary": "This lesson introduces the fundamental concepts of algebra, including variables, constants, and basic operations.",
            "created_at": datetime.now(),
            "created_by": "system",
            "tags": ["algebra", "mathematics", "beginner", "variables"],
            "resources": [
                {
                    "title": "Khan Academy Algebra",
                    "url": "https://www.khanacademy.org/math/algebra",
                    "type": "link",
                    "description": "Free online algebra course"
                }
            ],
            "exercises": [
                {
                    "question": "What is the value of x in the equation x + 5 = 10?",
                    "options": ["3", "5", "10", "15"],
                    "correct_answer": "5",
                    "explanation": "To solve x + 5 = 10, subtract 5 from both sides: x = 10 - 5 = 5",
                    "difficulty": "easy"
                },
                {
                    "question": "Which of the following is a variable?",
                    "options": ["5", "x", "10", "π"],
                    "correct_answer": "x",
                    "explanation": "A variable is a symbol that represents an unknown value. In this case, 'x' is the variable.",
                    "difficulty": "easy"
                }
            ]
        }
        
        # Save to Firestore with specific ID
        db.collection("lessons").document("lesson-123").set(lesson_data)
        
        print("✅ Test lesson 'lesson-123' created successfully!")
        print(f"   Title: {lesson_data['title']}")
        print(f"   Subject: {lesson_data['subject']}")
        print(f"   Difficulty: {lesson_data['difficulty']}")
        
    except Exception as e:
        print(f"❌ Error creating test lesson: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    print("🎓 Creating Test Lesson")
    print("=" * 30)
    
    await create_test_lesson()
    
if __name__ == "__main__":
    asyncio.run(main())

