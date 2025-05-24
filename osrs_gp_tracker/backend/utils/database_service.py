import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import firebase_admin
from firebase_admin import firestore
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationError:
    field: str
    value: Any
    expected_type: str
    message: str

class ItemDatabaseService:
    """Service for managing global items and user data in Firestore"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Get Firestore client, initializing if needed"""
        if self.db is None:
            try:
                self.db = firestore.client()
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}")
                return None
        return self.db
    
    # ==================== GLOBAL ITEMS ====================
    
    def get_global_items(self, activity_type: str, category: str = None) -> Dict:
        """Get global items for an activity type and optional category"""
        try:
            base_ref = self._get_db().collection('global_items').document(activity_type)
            
            if category:
                # Get specific category (e.g., farming/herbs)
                category_ref = base_ref.collection(category)
                docs = category_ref.stream()
                return {doc.id: doc.to_dict() for doc in docs}
            else:
                # Get all categories for activity type
                doc = base_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    # Also get subcollections
                    collections = base_ref.collections()
                    for collection in collections:
                        docs = collection.stream()
                        data[collection.id] = {doc.id: doc.to_dict() for doc in docs}
                    return data
                return {}
                
        except Exception as e:
            logger.error(f"Error getting global items for {activity_type}/{category}: {e}")
            return {}
    
    def add_global_item(self, db_client, activity_type: str, category: str, item_id: str, item_data: Dict) -> bool:
        """Add a new global item (admin only)"""
        try:
            # Use passed db_client or fallback to self._get_db()
            db = db_client if db_client else self._get_db()
            
            # Validate item data
            validation_errors = self._validate_item_data(activity_type, category, item_data)
            if validation_errors:
                logger.error(f"Validation errors for {item_id}: {validation_errors}")
                return False
            
            # Add metadata
            item_data.update({
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'source': 'admin'
            })
            
            # Save to Firestore
            ref = db.collection('global_items').document(activity_type).collection(category).document(item_id)
            ref.set(item_data)
            
            logger.info(f"Added global item: {activity_type}/{category}/{item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding global item {item_id}: {e}")
            return False
    
    def update_global_item(self, activity_type: str, category: str, item_id: str, updates: Dict) -> bool:
        """Update an existing global item"""
        try:
            updates['updated_at'] = datetime.now()
            
            ref = self._get_db().collection('global_items').document(activity_type).collection(category).document(item_id)
            ref.update(updates)
            
            logger.info(f"Updated global item: {activity_type}/{category}/{item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating global item {item_id}: {e}")
            return False
    
    def delete_global_item(self, activity_type: str, category: str, item_id: str) -> bool:
        """Delete a global item (admin only)"""
        try:
            ref = self._get_db().collection('global_items').document(activity_type).collection(category).document(item_id)
            ref.delete()
            
            logger.info(f"Deleted global item: {activity_type}/{category}/{item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting global item {item_id}: {e}")
            return False
    
    # ==================== USER SELECTIONS ====================
    
    def get_user_selections(self, user_id: str, activity_type: str) -> List[str]:
        """Get user's selected items for comparison"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).collection('item_selections').document(activity_type)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get('selected_items', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting user selections for {user_id}/{activity_type}: {e}")
            return []
    
    def update_user_selections(self, user_id: str, activity_type: str, item_ids: List[str]) -> bool:
        """Update user's selected items for comparison"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).collection('item_selections').document(activity_type)
            doc_ref.set({
                'selected_items': item_ids,
                'updated_at': datetime.now()
            })
            
            logger.info(f"Updated user selections for {user_id}/{activity_type}: {len(item_ids)} items")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user selections for {user_id}/{activity_type}: {e}")
            return False
    
    # ==================== USER OVERRIDES ====================
    
    def get_user_overrides(self, user_id: str) -> Dict:
        """Get user's parameter overrides"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).document('custom_overrides')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user overrides for {user_id}: {e}")
            return {}
    
    def update_user_override(self, user_id: str, parameter_name: str, value: Any) -> bool:
        """Update a single user parameter override"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).document('custom_overrides')
            doc_ref.set({
                parameter_name: value,
                'updated_at': datetime.now()
            }, merge=True)
            
            logger.info(f"Updated user override for {user_id}: {parameter_name} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user override for {user_id}: {e}")
            return False
    
    # ==================== USER PROFILE ====================
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile including admin status"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).document('profile')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return {'admin': False, 'created_at': datetime.now()}
            
        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return {'admin': False}
    
    def set_user_admin(self, user_id: str, is_admin: bool) -> bool:
        """Set user admin status"""
        try:
            doc_ref = self._get_db().collection('users').document(user_id).document('profile')
            doc_ref.set({
                'admin': is_admin,
                'updated_at': datetime.now()
            }, merge=True)
            
            logger.info(f"Set admin status for {user_id}: {is_admin}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting admin status for {user_id}: {e}")
            return False
    
    # ==================== VALIDATION ====================
    
    def _validate_item_data(self, activity_type: str, category: str, data: Dict) -> List[ValidationError]:
        """Validate item data based on activity type and category"""
        errors = []
        
        # Common validations
        if not isinstance(data.get('name'), str) or not data.get('name'):
            errors.append(ValidationError('name', data.get('name'), 'str', 'Name is required and must be a string'))
        
        # Activity-specific validations
        if activity_type == 'farming' and category == 'herbs':
            errors.extend(self._validate_farming_herb(data))
        elif activity_type == 'hunter' and category == 'birdhouses':
            errors.extend(self._validate_birdhouse(data))
        elif activity_type == 'runecraft' and category == 'gotr_strategies':
            errors.extend(self._validate_gotr_strategy(data))
        elif activity_type == 'slayer' and category == 'monsters':
            errors.extend(self._validate_slayer_monster(data))
        
        return errors
    
    def _validate_farming_herb(self, data: Dict) -> List[ValidationError]:
        """Validate farming herb data"""
        errors = []
        
        required_fields = {
            'seed_id': int,
            'herb_id': int,
            'growth_time_minutes': (int, float),
            'farming_level_req': int,
            'default_yield': (int, float)
        }
        
        for field, expected_type in required_fields.items():
            value = data.get(field)
            if value is None:
                errors.append(ValidationError(field, None, str(expected_type), f'{field} is required'))
            elif not isinstance(value, expected_type):
                errors.append(ValidationError(field, value, str(expected_type), f'{field} must be {expected_type}'))
            elif isinstance(value, (int, float)) and value < 0:
                errors.append(ValidationError(field, value, 'positive number', f'{field} must be positive'))
        
        return errors
    
    def _validate_birdhouse(self, data: Dict) -> List[ValidationError]:
        """Validate birdhouse data"""
        errors = []
        
        required_fields = {
            'log_id': int,
            'hunter_req': int,
            'exp_per_birdhouse': (int, float),
            'avg_nests_per_run': (int, float)
        }
        
        for field, expected_type in required_fields.items():
            value = data.get(field)
            if value is None:
                errors.append(ValidationError(field, None, str(expected_type), f'{field} is required'))
            elif not isinstance(value, expected_type):
                errors.append(ValidationError(field, value, str(expected_type), f'{field} must be {expected_type}'))
        
        return errors
    
    def _validate_gotr_strategy(self, data: Dict) -> List[ValidationError]:
        """Validate GOTR strategy data"""
        errors = []
        
        required_fields = {
            'rune_id': int,
            'avg_runes_per_game': (int, float),
            'points_req': int
        }
        
        for field, expected_type in required_fields.items():
            value = data.get(field)
            if value is None:
                errors.append(ValidationError(field, None, str(expected_type), f'{field} is required'))
            elif not isinstance(value, expected_type):
                errors.append(ValidationError(field, value, str(expected_type), f'{field} must be {expected_type}'))
        
        return errors
    
    def _validate_slayer_monster(self, data: Dict) -> List[ValidationError]:
        """Validate slayer monster data"""
        errors = []
        
        required_fields = {
            'avg_loot_value_per_kill': (int, float),
            'kills_per_hour': (int, float),
            'avg_supply_cost_per_hour': (int, float)
        }
        
        for field, expected_type in required_fields.items():
            value = data.get(field)
            if value is None:
                errors.append(ValidationError(field, None, str(expected_type), f'{field} is required'))
            elif not isinstance(value, expected_type):
                errors.append(ValidationError(field, value, str(expected_type), f'{field} must be {expected_type}'))
            elif isinstance(value, (int, float)) and value < 0:
                errors.append(ValidationError(field, value, 'positive number', f'{field} must be positive'))
        
        return errors
    
    # ==================== WIKI SYNC SUPPORT ====================
    
    def bulk_add_global_items(self, activity_type: str, category: str, items: Dict[str, Dict]) -> Dict:
        """Bulk add items from wiki sync (returns success/failure stats)"""
        stats = {'success': 0, 'failed': 0, 'errors': []}
        
        for item_id, item_data in items.items():
            success = self.add_global_item(activity_type, category, item_id, item_data)
            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
                stats['errors'].append(f"Failed to add {item_id}")
        
        return stats
    
    def log_sync_operation(self, activity_type: str, category: str, stats: Dict) -> bool:
        """Log wiki sync operation results"""
        try:
            doc_ref = self._get_db().collection('admin').document('sync_logs')
            
            log_entry = {
                'timestamp': datetime.now(),
                'activity_type': activity_type,
                'category': category,
                'items_processed': stats['success'] + stats['failed'],
                'items_success': stats['success'],
                'items_failed': stats['failed'],
                'errors': stats.get('errors', [])
            }
            
            # Add to sync log array
            doc_ref.update({
                f'sync_history': firestore.ArrayUnion([log_entry])
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging sync operation: {e}")
            return False

    def add_sync_log(self, db_client, sync_log: Dict) -> bool:
        """Add a sync operation log"""
        try:
            # Use passed db_client or fallback to self._get_db()
            db = db_client if db_client else self._get_db()
            
            # Add timestamp if not present
            if 'timestamp' not in sync_log:
                sync_log['timestamp'] = datetime.now().isoformat()
            
            # Save to sync_logs collection
            ref = db.collection('sync_logs').document()
            ref.set(sync_log)
            
            logger.info(f"Added sync log: {sync_log.get('sync_type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding sync log: {e}")
            return False

# Global instance
item_db = ItemDatabaseService() 