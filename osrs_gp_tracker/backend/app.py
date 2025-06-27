"""
Flask backend for OSRS GP/hour tracker.
Provides API endpoints for GE prices, GP/hour calculations, and user configuration management.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from utils.ge_api import get_ge_price
from utils.calculations import calculate_activity_gp_hr, calculate_farming_gp_hr, calculate_birdhouse_gp_hr, calculate_gotr_gp_hr, calculate_slayer_gp_hr, get_slayer_task_breakdown
from utils.database_service import item_db
from utils.auth_service import auth_service, require_admin, require_user_or_admin
from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.comprehensive_item_database import item_database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for frontend communication

# Configure secret key
DEFAULT_SECRET_KEY = 'your-secret-key-change-in-production'
app.secret_key = os.getenv('SECRET_KEY', DEFAULT_SECRET_KEY)

if not app.debug and app.secret_key == DEFAULT_SECRET_KEY:
    logger.critical("CRITICAL: Default SECRET_KEY is being used in a non-debug environment. This is insecure!")
    # In a real production scenario, you might want to raise an exception here or exit.
    # For this exercise, we'll log a critical error.
    # raise RuntimeError("Default SECRET_KEY is insecure and cannot be used in production.")

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
    """Health check endpoint"""
    try:
        # Test Firebase connection by attempting to read
        from firebase_admin import firestore
        db = firestore.client()
        # Try to read a test document
        test_ref = db.collection('health_check').document('test')
        test_ref.get()
        
        return jsonify({
            "status": "healthy",
            "firebase_connected": True
        })
    except Exception as e:
        return jsonify({
            "status": "healthy",
            "firebase_connected": False,
            "firebase_error": str(e)
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
    """Calculate GP/hour for different activities"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        activity_type = data.get('activity_type')
        params = data.get('params', {})
        user_id = data.get('user_id')
        
        if not activity_type:
            return jsonify({'success': False, 'error': 'Activity type is required'}), 400
        
        # Get user overrides for enhanced calculations
        user_overrides = {}
        if user_id and db:
            try:
                user_overrides = item_db.get_user_overrides(user_id)
            except Exception as e:
                logger.warning(f"Could not fetch user overrides for {user_id}: {e}")
        
        # Route to appropriate calculation function
        if activity_type == 'farming':
            result = calculate_farming_gp_hr(params)
        elif activity_type == 'birdhouse':
            result = calculate_birdhouse_gp_hr(params)
        elif activity_type == 'gotr':
            result = calculate_gotr_gp_hr(params)
        elif activity_type == 'slayer':
            # Pass user overrides to slayer calculation
            result = calculate_slayer_gp_hr(params, user_overrides)
        else:
            return jsonify({'success': False, 'error': f'Unknown activity type: {activity_type}'}), 400
        
        return jsonify({
            'success': True,
            'result': result,
            'activity_type': activity_type,
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error calculating GP/hour: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/slayer/breakdown', methods=['POST'])
def get_slayer_breakdown():
    """Get detailed breakdown of Slayer assignments for a specific master and user levels"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        slayer_master_id = data.get('slayer_master_id')
        user_levels = data.get('user_levels', {})
        user_id = data.get('user_id')
        
        if not slayer_master_id:
            return jsonify({'success': False, 'error': 'Slayer master ID is required'}), 400
        
        # Get breakdown data
        breakdown = get_slayer_task_breakdown(slayer_master_id, user_levels, user_id)
        
        return jsonify({
            'success': True,
            'result': breakdown,
            'slayer_master_id': slayer_master_id,
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error getting Slayer breakdown: {e}")
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
        
        # Import and call the new helper function
        from .utils.database_service import save_user_config_to_db
        
        # Call the new helper function, passing the db client
        save_success = save_user_config_to_db(user_id, config, db_client=db)

        if save_success:
            return jsonify({
                "success": True,
                "message": "Configuration saved successfully",
                "user_id": user_id
            })
        else:
            # If saving failed, return an error.
            # The error is already logged in save_user_config_to_db.
            return jsonify({
                "success": False,
                "error": "Failed to save configuration to database."
            }), 500 # Internal server error, as the problem is on the server side

    except Exception as e:
        logger.error(f"Error saving user config for {user_id}: {e}")
        return jsonify({
            "success": False,
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
    """Get default configuration for all activities"""
    config = {
        "farming": {
            "num_patches": 9,
            "avg_yield_per_patch": 8,
            "growth_time_minutes": 80,
            "herb_id": 207,  # Ranarr weed
            "seed_id": 5295,  # Ranarr seed
            "compost_id": 21483  # Ultracompost
        },
        "birdhouse": {
            "num_birdhouses": 4,
            "run_time_minutes": 5,
            "cycle_time_minutes": 50,
            "log_id": 19669,  # Redwood logs
            "seed_id": 5318,  # Potato seed
            "seeds_per_house": 10,
            "avg_nests_per_run": 10,
            "avg_value_per_nest": 5000
        },
        "gotr": {
            "games_per_hour": 4,
            "avg_points_per_game": 350,
            "essence_per_game": 150,
            "essence_id": 7936,  # Pure essence
            "avg_rune_value_per_game": 15000,
            "avg_pearl_value_per_game": 8000
        },
        "slayer": {
            "monster_name": "Rune Dragons",
            "kills_per_hour": 40,
            "avg_loot_value_per_kill": 37000,
            "avg_supply_cost_per_hour": 100000
        }
    }
    
    return jsonify({
        "success": True,
        "config": config
    })

# ==================== ADMIN AUTHENTICATION ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        result = auth_service.login_admin(username, password)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    result = auth_service.logout_admin()
    return jsonify(result)

@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    """Check admin authentication status"""
    is_authenticated = auth_service.is_admin_authenticated()
    current_user = auth_service.get_current_admin_user()
    
    return jsonify({
        'authenticated': is_authenticated,
        'username': current_user if is_authenticated else None
    })

# ==================== GLOBAL ITEMS MANAGEMENT ====================

@app.route('/api/items/<activity_type>', methods=['GET'])
def get_activity_items(activity_type):
    """Get all items for an activity type"""
    try:
        category = request.args.get('category')
        items = item_db.get_global_items(activity_type, category)
        
        return jsonify({
            'success': True,
            'activity_type': activity_type,
            'category': category,
            'items': items
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/items/<activity_type>/<category>', methods=['POST'])
@require_admin
def add_global_item(activity_type, category):
    """Add a new global item (admin only)"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        item_data = data.get('item_data')
        
        if not item_id or not item_data:
            return jsonify({'success': False, 'error': 'item_id and item_data required'}), 400
        
        success = item_db.add_global_item(activity_type, category, item_id, item_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Added item {item_id} to {activity_type}/{category}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add item'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/items/<activity_type>/<category>/<item_id>', methods=['PUT'])
@require_admin
def update_global_item(activity_type, category, item_id):
    """Update a global item (admin only)"""
    try:
        data = request.get_json()
        updates = data.get('updates')
        
        if not updates:
            return jsonify({'success': False, 'error': 'updates required'}), 400
        
        success = item_db.update_global_item(activity_type, category, item_id, updates)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Updated item {item_id}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update item'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/items/<activity_type>/<category>/<item_id>', methods=['DELETE'])
@require_admin
def delete_global_item(activity_type, category, item_id):
    """Delete a global item (admin only)"""
    try:
        success = item_db.delete_global_item(activity_type, category, item_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Deleted item {item_id}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete item'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== USER SELECTIONS ====================

@app.route('/api/user/selections/<activity_type>', methods=['GET'])
@require_user_or_admin
def get_user_selections(activity_type):
    """Get user's selected items for comparison"""
    try:
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({'success': False, 'error': 'User-ID header required'}), 400
        
        selections = item_db.get_user_selections(user_id, activity_type)
        
        return jsonify({
            'success': True,
            'activity_type': activity_type,
            'user_id': user_id,
            'selected_items': selections
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/selections/<activity_type>', methods=['POST'])
@require_user_or_admin
def update_user_selections(activity_type):
    """Update user's selected items for comparison"""
    try:
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({'success': False, 'error': 'User-ID header required'}), 400
        
        data = request.get_json()
        item_ids = data.get('item_ids', [])
        
        success = item_db.update_user_selections(user_id, activity_type, item_ids)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Updated selections for {activity_type}',
                'selected_items': item_ids
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update selections'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== USER OVERRIDES ====================

@app.route('/api/user/overrides', methods=['GET'])
@require_user_or_admin
def get_user_overrides():
    """Get user's parameter overrides"""
    try:
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({'success': False, 'error': 'User-ID header required'}), 400
        
        overrides = item_db.get_user_overrides(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'overrides': overrides
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/overrides', methods=['POST'])
@require_user_or_admin
def update_user_override():
    """Update a user parameter override"""
    try:
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({'success': False, 'error': 'User-ID header required'}), 400
        
        data = request.get_json()
        parameter_name = data.get('parameter_name')
        value = data.get('value')
        
        if not parameter_name:
            return jsonify({'success': False, 'error': 'parameter_name required'}), 400
        
        success = item_db.update_user_override(user_id, parameter_name, value)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Updated override {parameter_name} = {value}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update override'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== WIKI SYNC ====================

@app.route('/api/admin/sync_wiki', methods=['POST'])
@require_admin  # Re-enable admin authentication
def sync_wiki_data():
    """Sync data from OSRS Wiki (admin only)"""
    try:
        data = request.get_json()
        sync_type = data.get('sync_type', 'slayer')
        
        if not db:
            return jsonify({'success': False, 'error': 'Firestore not available'}), 503
        
        # Initialize wiki sync service
        wiki_sync = OSRSWikiSyncService(database_service=item_db)
        
        if sync_type == 'slayer':
            logger.info("🚀 Starting Slayer data sync from admin endpoint...")
            result = wiki_sync.sync_slayer_data(db)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Slayer data sync completed successfully',
                    'sync_type': sync_type,
                    'stats': {
                        'masters_synced': result.get('sync_log', {}).get('masters_synced', 0),
                        'monsters_synced': result.get('sync_log', {}).get('monsters_synced', 0)
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error during sync')
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown sync type: {sync_type}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in wiki sync endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/test_item_database', methods=['GET'])
def test_item_database():
    """Test the comprehensive item database"""
    try:
        # Test with problematic items from the logs
        test_items = [
            'limpwurt seed', 'strawberry seed', 'watermelon seed', 
            'potato cactus seed', 'cactus seed', 'marrentill seed',
            'harralander seed', 'granite maul', 'abyssal whip',
            'rune boots', 'death rune', 'nature rune', 'coins'
        ]
        
        results = {}
        success_count = 0
        
        for item_name in test_items:
            item_id = item_database.get_item_id(item_name)
            results[item_name] = item_id
            if item_id:
                success_count += 1
        
        cache_stats = item_database.get_cache_stats()
        
        return jsonify({
            "success": True,
            "test_results": results,
            "success_rate": f"{success_count}/{len(test_items)}",
            "cache_stats": cache_stats,
            "status": "READY" if success_count == len(test_items) else "NEEDS_WORK"
        })
        
    except Exception as e:
        logger.error(f"Error testing item database: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/admin/build_item_database', methods=['POST'])
@require_admin
def build_item_database():
    """Build the complete OSRS item database (admin only)"""
    try:
        from utils.comprehensive_item_database import item_database
        
        logger.info("🚀 Starting complete item database build...")
        success = item_database.rebuild_complete_database()
        
        if success:
            stats = item_database.get_cache_stats()
            return jsonify({
                'success': True,
                'message': 'Complete item database built successfully',
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to build complete item database'
            }), 500
            
    except Exception as e:
        logger.error(f"Error building item database: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/item_database/status', methods=['GET'])
def get_item_database_status():
    """Get status of the item database"""
    try:
        from utils.comprehensive_item_database import item_database
        stats = item_database.get_cache_stats()
        
        return jsonify({
            'success': True,
            'status': stats,
            'recommendations': {
                'has_complete_db': stats.get('has_complete_database', False),
                'should_build': not stats.get('complete_db_exists', False),
                'total_items': stats.get('total_items', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/item_database/search', methods=['GET'])
def search_items():
    """Search for items by name"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter required'}), 400
        
        from utils.comprehensive_item_database import item_database
        results = item_database.search_items(query, limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run in debug mode for local development
    app.run(debug=True, host='0.0.0.0', port=5000) 