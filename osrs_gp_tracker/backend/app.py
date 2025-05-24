"""
Flask backend for OSRS GP/hour tracker.
Provides API endpoints for GE prices, GP/hour calculations, and user configuration management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from utils.ge_api import get_ge_price
from utils.calculations import calculate_activity_gp_hr

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Firebase Admin SDK
try:
    # For local development, use environment variables or service account key
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
    
    # Check if we have the required Firebase config
    if firebase_config["project_id"]:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        logger.info("Firebase initialized successfully")
    else:
        logger.warning("Firebase configuration not found, running without Firestore")
        db = None
        
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")
    logger.warning("Running without Firestore support")
    db = None

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "firebase_connected": db is not None
    })

@app.route('/api/ge_price/<int:item_id>', methods=['GET'])
def get_item_price(item_id):
    """
    Get Grand Exchange price for a specific item.
    
    Args:
        item_id (int): OSRS item ID
        
    Returns:
        JSON response with price data
    """
    try:
        price_data = get_ge_price(item_id)
        
        if price_data:
            return jsonify({
                "success": True,
                "item_id": item_id,
                "price_data": price_data
            })
        else:
            return jsonify({
                "success": False,
                "error": f"No price data found for item {item_id}"
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching price for item {item_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/calculate_gp_hr', methods=['POST'])
def calculate_gp_hr():
    """
    Calculate GP/hour for a specific activity.
    
    Expected JSON payload:
    {
        "activity_type": "farming|birdhouse|gotr|slayer",
        "params": {...},
        "user_id": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        activity_type = data.get('activity_type')
        params = data.get('params', {})
        user_id = data.get('user_id')
        
        if not activity_type:
            return jsonify({
                "success": False,
                "error": "activity_type is required"
            }), 400
        
        # Merge with user-specific configuration if available
        if user_id and db:
            try:
                user_config = get_user_config(user_id)
                if user_config and activity_type in user_config:
                    # Merge user config with provided params (params take precedence)
                    merged_params = {**user_config[activity_type], **params}
                    params = merged_params
            except Exception as e:
                logger.warning(f"Could not fetch user config for {user_id}: {e}")
        
        # Calculate GP/hour
        result = calculate_activity_gp_hr(activity_type, params)
        
        return jsonify({
            "success": True,
            "activity_type": activity_type,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error calculating GP/hour: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user_config/<string:user_id>', methods=['GET'])
def get_user_configuration(user_id):
    """
    Get user-specific configuration from Firestore.
    
    Args:
        user_id (string): User ID from Firebase Auth
        
    Returns:
        JSON response with user configuration
    """
    try:
        if not db:
            return jsonify({
                "success": False,
                "error": "Firestore not available"
            }), 503
        
        config = get_user_config(user_id)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "config": config or {}
        })
        
    except Exception as e:
        logger.error(f"Error fetching user config for {user_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user_config/<string:user_id>', methods=['POST'])
def save_user_configuration(user_id):
    """
    Save user-specific configuration to Firestore.
    
    Expected JSON payload:
    {
        "config": {
            "farming": {...},
            "birdhouse": {...},
            "gotr": {...},
            "slayer": {...}
        }
    }
    """
    try:
        if not db:
            return jsonify({
                "success": False,
                "error": "Firestore not available"
            }), 503
        
        data = request.get_json()
        
        if not data or 'config' not in data:
            return jsonify({
                "success": False,
                "error": "Configuration data is required"
            }), 400
        
        config = data['config']
        
        # Save to Firestore
        save_user_config(user_id, config)
        
        return jsonify({
            "success": True,
            "message": "Configuration saved successfully",
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Error saving user config for {user_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Helper functions for Firestore operations

def get_user_config(user_id):
    """
    Retrieve user configuration from Firestore.
    
    Args:
        user_id (string): User ID
        
    Returns:
        dict: User configuration or None if not found
    """
    if not db:
        return None
    
    try:
        doc_ref = db.collection('userConfigurations').document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting user config: {e}")
        return None

def save_user_config(user_id, config):
    """
    Save user configuration to Firestore.
    
    Args:
        user_id (string): User ID
        config (dict): Configuration data
    """
    if not db:
        raise Exception("Firestore not available")
    
    try:
        # Add timestamp
        from datetime import datetime
        config['lastUpdated'] = datetime.now()
        
        doc_ref = db.collection('userConfigurations').document(user_id)
        doc_ref.set(config, merge=True)
        
        logger.info(f"Saved configuration for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error saving user config: {e}")
        raise

# Default configurations for new users
DEFAULT_USER_CONFIG = {
    "farming": {
        "seed_id": 5309,  # Torstol seed
        "herb_id": 207,   # Grimy torstol
        "compost_id": 21483,  # Ultracompost
        "avg_yield_per_patch": 8,
        "num_patches": 9,
        "growth_time_minutes": 80
    },
    "birdhouse": {
        "log_id": 19669,  # Redwood logs
        "seed_id": 5318,  # Potato seed
        "avg_nests_per_run": 10,
        "avg_value_per_nest": 5000,
        "run_time_minutes": 5,
        "cycle_time_minutes": 50,
        "num_birdhouses": 4,
        "seeds_per_house": 10
    },
    "gotr": {
        "essence_id": 7936,  # Pure essence
        "games_per_hour": 4,
        "avg_points_per_game": 350,
        "avg_rune_value_per_game": 15000,
        "avg_pearl_value_per_game": 8000,
        "essence_per_game": 150
    },
    "slayer": {
        "monster_name": "Rune Dragons",
        "kills_per_hour": 40,
        "avg_loot_value_per_kill": 37000,
        "avg_supply_cost_per_hour": 100000
    }
}

@app.route('/api/default_config', methods=['GET'])
def get_default_config():
    """Get default configuration for new users."""
    return jsonify({
        "success": True,
        "config": DEFAULT_USER_CONFIG
    })

if __name__ == '__main__':
    # Run in debug mode for local development
    app.run(debug=True, host='0.0.0.0', port=5000) 