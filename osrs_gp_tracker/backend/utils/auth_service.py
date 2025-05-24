import os
import logging
import hashlib
import secrets
from typing import Optional, Dict
from functools import wraps
from flask import request, jsonify, session
from .database_service import item_db

logger = logging.getLogger(__name__)

class AdminAuthService:
    """Simple admin authentication service"""
    
    def __init__(self):
        # Default admin credentials (should be changed in production)
        self.admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        self.admin_password_hash = self._hash_password(os.getenv('ADMIN_PASSWORD', 'osrsadmin123'))
        
    def _hash_password(self, password: str) -> str:
        """Hash a password with salt"""
        salt = os.getenv('PASSWORD_SALT', 'osrs_gp_tracker_salt')
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def authenticate_admin(self, username: str, password: str) -> bool:
        """Authenticate admin credentials"""
        if username == self.admin_username:
            password_hash = self._hash_password(password)
            return password_hash == self.admin_password_hash
        return False
    
    def login_admin(self, username: str, password: str) -> Dict:
        """Login admin and create session"""
        if self.authenticate_admin(username, password):
            # Create session token
            session_token = secrets.token_urlsafe(32)
            session['admin_token'] = session_token
            session['admin_user'] = username
            
            logger.info(f"Admin login successful: {username}")
            return {
                'success': True,
                'token': session_token,
                'message': 'Admin authentication successful'
            }
        else:
            logger.warning(f"Failed admin login attempt: {username}")
            return {
                'success': False,
                'error': 'Invalid admin credentials'
            }
    
    def logout_admin(self) -> Dict:
        """Logout admin and clear session"""
        session.pop('admin_token', None)
        session.pop('admin_user', None)
        return {'success': True, 'message': 'Logged out successfully'}
    
    def is_admin_authenticated(self) -> bool:
        """Check if current session is admin authenticated"""
        return 'admin_token' in session and 'admin_user' in session
    
    def get_current_admin_user(self) -> Optional[str]:
        """Get current admin username"""
        return session.get('admin_user')

# Global instance
auth_service = AdminAuthService()

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_service.is_admin_authenticated():
            return jsonify({'error': 'Admin authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_user_or_admin(f):
    """Decorator to require either user authentication or admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin authenticated
        if auth_service.is_admin_authenticated():
            return f(*args, **kwargs)
        
        # Check if user authenticated (Firebase auth)
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
            
        return f(*args, **kwargs)
    return decorated_function 