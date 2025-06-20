#!/usr/bin/env python
"""
Script to safely clean the Firebase Firestore database for AI Tutor Pro.
This script deletes all documents from all collections in the database.

Usage:
    python clean_db.py [--force]

Options:
    --force    Skip confirmation prompt and proceed with deletion
"""

import sys
import os
import logging
import argparse
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import Firebase utilities
from utils.firebase import initialize_firebase, get_firestore_client
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("clean_db")

# List of known collections to clean
KNOWN_COLLECTIONS = [
    "lessons",
    "lessonProgress",
    "users",
    "qa_history",
    "learning_progress",
    "user_settings",
    "analytics"
]

async def get_all_collections() -> List[str]:
    """
    Get a list of all collections in the Firestore database.
    
    Returns:
        List[str]: List of collection IDs
    """
    try:
        db = get_firestore_client()
        collections = [col.id for col in db.collections()]
        return collections
    except Exception as e:
        logger.error(f"Error getting collections: {str(e)}")
        return KNOWN_COLLECTIONS

async def count_documents(collection_id: str) -> int:
    """
    Count the number of documents in a collection.
    
    Args:
        collection_id: ID of the collection
        
    Returns:
        int: Number of documents in the collection
    """
    try:
        db = get_firestore_client()
        docs = db.collection(collection_id).limit(1000).stream()
        count = sum(1 for _ in docs)
        return count
    except Exception as e:
        logger.error(f"Error counting documents in {collection_id}: {str(e)}")
        return 0

async def delete_collection(collection_id: str, batch_size: int = 100) -> int:
    """
    Delete all documents in a collection.
    
    Args:
        collection_id: ID of the collection
        batch_size: Number of documents to delete in each batch
        
    Returns:
        int: Number of documents deleted
    """
    db = get_firestore_client()
    collection_ref = db.collection(collection_id)
    docs_deleted = 0
    
    try:
        # Get a batch of documents
        docs = collection_ref.limit(batch_size).stream()
        docs = list(docs)  # Materialize the stream
        
        # If there are no documents, we're done
        if not docs:
            return 0
            
        # Create a new batch
        batch = db.batch()
        
        # Add each document to the delete batch
        for doc in docs:
            batch.delete(doc.reference)
            docs_deleted += 1
            
        # Commit the batch
        batch.commit()
        
        # If we've deleted a full batch, there might be more
        if len(docs) >= batch_size:
            # Recursive call to delete the next batch
            docs_deleted += await delete_collection(collection_id, batch_size)
            
        return docs_deleted
        
    except Exception as e:
        logger.error(f"Error deleting documents from {collection_id}: {str(e)}")
        return docs_deleted

async def clean_database(force: bool = False) -> None:
    """
    Clean the entire database by deleting all documents from all collections.
    
    Args:
        force: Skip confirmation prompt if True
    """
    try:
        # Initialize Firebase
        initialize_firebase()
        logger.info("Firebase initialized successfully")
        
        # Get all collections
        collections = await get_all_collections()
        
        if not collections:
            logger.info("No collections found in the database.")
            return
            
        logger.info(f"Found {len(collections)} collections: {', '.join(collections)}")
        
        # Count total documents for progress reporting
        total_docs = 0
        collection_counts = {}
        
        logger.info("Counting documents in collections...")
        for collection_id in collections:
            count = await count_documents(collection_id)
            collection_counts[collection_id] = count
            total_docs += count
            
        logger.info(f"Total documents across all collections: {total_docs}")
        
        # Print document counts per collection
        for collection_id, count in collection_counts.items():
            logger.info(f"Collection '{collection_id}': {count} documents")
            
        # Get confirmation from user
        if not force:
            print("\n" + "="*80)
            print("WARNING: This will delete ALL data from the following collections:")
            for collection_id, count in collection_counts.items():
                print(f"  - {collection_id}: {count} documents")
            print(f"Total: {total_docs} documents will be permanently deleted.")
            print("="*80)
            
            confirmation = input("\nAre you sure you want to proceed? (yes/no): ")
            
            if confirmation.lower() not in ["yes", "y"]:
                logger.info("Operation cancelled by user.")
                return
                
        logger.info("Starting database cleanup...")
        
        # Delete documents from each collection
        total_deleted = 0
        
        for collection_id, count in collection_counts.items():
            if count > 0:
                logger.info(f"Deleting documents from '{collection_id}'...")
                deleted = await delete_collection(collection_id)
                logger.info(f"Deleted {deleted} documents from '{collection_id}'")
                total_deleted += deleted
                
        logger.info(f"Database cleanup completed. Deleted {total_deleted} documents from {len(collections)} collections.")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Clean the Firebase Firestore database")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    print(f"AI Tutor Pro - Database Cleanup Script ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("-" * 80)
    
    try:
        # Run the async cleanup function
        asyncio.run(clean_database(force=args.force))
        print("-" * 80)
        print("Database cleanup completed successfully.")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
