import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, Any, Optional
import logging
import os

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global variables to track initialization
_firebase_app = None
_firestore_client = None

def initialize_firebase() -> firebase_admin.App:
    """
    Initialize Firebase Admin SDK
    
    Returns:
        firebase_admin.App: Firebase app instance
    
    Raises:
        ValueError: If required Firebase credentials are missing
    """
    global _firebase_app, _firestore_client
    
    # Check if already initialized
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Create Firebase credentials from environment variables
        if not settings.FIREBASE_PROJECT_ID or not settings.FIREBASE_PRIVATE_KEY or not settings.FIREBASE_CLIENT_EMAIL:
            raise ValueError("Missing required Firebase credentials in environment variables")
        
        # Initialize Firebase with credentials from environment variables
        credential_dict = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": settings.FIREBASE_AUTH_URI,
            "token_uri": settings.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
            "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN
        }
        cred = credentials.Certificate(credential_dict)
        firebase_options = {}
        
        # Add optional settings from environment variables if available
        if settings.FIREBASE_DATABASE_URL:
            firebase_options["databaseURL"] = settings.FIREBASE_DATABASE_URL
            
        if settings.FIREBASE_STORAGE_BUCKET:
            firebase_options["storageBucket"] = settings.FIREBASE_STORAGE_BUCKET
            
        _firebase_app = firebase_admin.initialize_app(cred, firebase_options)
        
        # Initialize Firestore client
        _firestore_client = firestore.client()
        
        return _firebase_app
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

def get_firestore_client() -> firestore.Client:
    """
    Get the Firestore client instance
    
    Returns:
        firestore.Client: Firestore client
        
    Raises:
        RuntimeError: If Firebase is not initialized
    """
    global _firestore_client
    
    if _firestore_client is None:
        # Try to initialize Firebase if not already done
        initialize_firebase()
        
        if _firestore_client is None:
            raise RuntimeError("Firestore client not initialized. Call initialize_firebase() first.")
            
    return _firestore_client

def get_auth_client() -> auth.Client:
    """
    Get the Firebase Auth client instance
    
    Returns:
        auth.Client: Firebase Auth client
        
    Raises:
        RuntimeError: If Firebase is not initialized
    """
    # Ensure Firebase is initialized
    if firebase_admin._apps.get(firebase_admin._DEFAULT_APP_NAME) is None:
        initialize_firebase()
        
    # Auth doesn't have a specific client class, it's accessed through the module
    return auth

def create_custom_token(uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a custom Firebase token for a user
    
    Args:
        uid: User ID
        additional_claims: Optional additional claims to include in the token
        
    Returns:
        str: JWT token string
    """
    auth_client = get_auth_client()
    token = auth_client.create_custom_token(uid, additional_claims)
    return token.decode('utf-8') if isinstance(token, bytes) else token

def verify_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verify a Firebase ID token
    
    Args:
        id_token: Firebase ID token to verify
        
    Returns:
        Dict: Decoded token claims
    """
    auth_client = get_auth_client()
    return auth_client.verify_id_token(id_token)

