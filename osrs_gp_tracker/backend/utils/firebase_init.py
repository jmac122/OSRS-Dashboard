#!/usr/bin/env python3
"""
Centralized Firebase initialization utility
Ensures all scripts use the same Firebase configuration method
"""

import os
import logging
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialize Firebase Admin SDK using environment variables
    Returns the Firestore client or None if initialization fails
    """
    # Load environment variables
    load_dotenv()
    
    try:
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            logger.info("Firebase already initialized, getting existing client")
            return firestore.client()
        except ValueError:
            # Firebase not initialized yet, proceed with initialization
            pass
        
        # Build Firebase configuration from environment variables
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
        
        # Validate required configuration
        required_fields = ['project_id', 'private_key', 'client_email']
        missing_fields = []
        
        for field in required_fields:
            if not firebase_config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing required Firebase configuration: {missing_fields}")
            logger.error("Please check your .env file and ensure these environment variables are set:")
            for field in missing_fields:
                env_var = f"FIREBASE_{field.upper()}"
                logger.error(f"  - {env_var}")
            return None
        
        # Initialize Firebase with service account credentials
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        # Test the connection
        test_ref = db.collection('health_check').document('test')
        test_ref.get()
        
        logger.info("Firebase initialized successfully")
        return db
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        logger.error("This could be due to:")
        logger.error("  1. Missing or incorrect environment variables in .env file")
        logger.error("  2. Invalid Firebase service account credentials")
        logger.error("  3. Network connectivity issues")
        logger.error("  4. Firebase project configuration problems")
        return None

def get_firestore_client():
    """
    Get Firestore client, initializing Firebase if needed
    """
    try:
        # Try to get existing client first
        return firestore.client()
    except:
        # Initialize Firebase and return client
        return initialize_firebase()

def check_firebase_env():
    """
    Check if all required Firebase environment variables are set
    Returns tuple (is_configured, missing_vars)
    """
    load_dotenv()
    
    required_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def print_firebase_status():
    """
    Print detailed Firebase configuration status for debugging
    """
    print("🔥 Firebase Configuration Status")
    print("=" * 40)
    
    is_configured, missing_vars = check_firebase_env()
    
    if is_configured:
        print("✅ All required environment variables are set")
        
        # Try to initialize
        db = initialize_firebase()
        if db:
            print("✅ Firebase initialization successful")
            print("✅ Firestore connection working")
            return True
        else:
            print("❌ Firebase initialization failed")
            return False
    else:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please check your .env file in the project root")
        return False

if __name__ == "__main__":
    print_firebase_status() 