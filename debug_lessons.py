#!/usr/bin/env python3
"""
Debug script to check lessons in Firestore database
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.firebase import initialize_firebase

async def check_lessons():
    """Check what lessons exist in the database"""
    try:
        # Initialize Firebase first
        initialize_firebase()
        
        # Now import after Firebase is initialized
        from src.models.lesson import get_lessons, get_lesson_by_id
        
        print("📚 Checking lessons in database...")
        
        # Get all lessons
        lessons = await get_lessons(limit=50)
        
        if not lessons:
            print("❌ No lessons found in database")
            return
            
        print(f"✅ Found {len(lessons)} lessons:")
        print("=" * 50)
        
        for i, lesson in enumerate(lessons, 1):
            print(f"{i}. ID: {lesson.get('id', 'No ID')}")
            print(f"   Title: {lesson.get('title', 'No title')}")
            print(f"   Subject: {lesson.get('subject', 'No subject')}")
            print(f"   Difficulty: {lesson.get('difficulty', 'No difficulty')}")
            print(f"   Created: {lesson.get('created_at', 'No date')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error checking lessons: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_specific_lesson(lesson_id: str = "lesson-123"):
    """Test accessing a specific lesson"""
    try:
        from src.models.lesson import get_lesson_by_id
        
        print(f"\n🔍 Testing access to lesson: {lesson_id}")
        lesson = await get_lesson_by_id(lesson_id)
        
        if lesson:
            print(f"✅ Found lesson: {lesson.get('title', 'No title')}")
        else:
            print(f"❌ Lesson '{lesson_id}' not found")
            
    except Exception as e:
        print(f"❌ Error accessing lesson '{lesson_id}': {str(e)}")

async def main():
    """Main function"""
    print("🔧 AI Tutor Database Debug Tool")
    print("=" * 40)
    
    await check_lessons()
    await test_specific_lesson()
    
if __name__ == "__main__":
    asyncio.run(main())

