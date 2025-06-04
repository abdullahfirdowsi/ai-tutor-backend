#!/usr/bin/env python3
"""
Test script to verify Google Gemini integration
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ai import generate_lesson_content, generate_answer

async def test_lesson_generation():
    """Test lesson generation with Gemini"""
    print("Testing lesson generation...")
    try:
        lesson = await generate_lesson_content(
            subject="Mathematics",
            topic="Basic Algebra",
            difficulty="beginner",
            duration_minutes=30
        )
        print("✅ Lesson generation successful!")
        print(f"Title: {lesson.get('title', 'No title')}")
        print(f"Summary: {lesson.get('summary', 'No summary')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Lesson generation failed: {str(e)}")
        return False

async def test_answer_generation():
    """Test answer generation with Gemini"""
    print("\nTesting answer generation...")
    try:
        answer = await generate_answer(
            question="What is 2 + 2?",
            context="Basic arithmetic"
        )
        print("✅ Answer generation successful!")
        print(f"Answer: {answer.get('answer', 'No answer')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Answer generation failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Google Gemini Integration")
    print("=" * 40)
    
    # Test lesson generation
    lesson_success = await test_lesson_generation()
    
    # Test answer generation
    answer_success = await test_answer_generation()
    
    print("\n" + "=" * 40)
    if lesson_success and answer_success:
        print("🎉 All tests passed! Gemini integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        
if __name__ == "__main__":
    asyncio.run(main())

