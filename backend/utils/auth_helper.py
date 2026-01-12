"""
Authentication helper functions
Password hashing and JWT utilities
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta


def hash_password(password):
    """Hash a password"""
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash, password):
    """Verify a password against its hash"""
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


def create_tokens(user_id, email):
    """
    Create access and refresh tokens
    
    Args:
        user_id: User ID
        email: User email
    
    Returns:
        Dict with access_token and refresh_token
    """
    identity = {
        'id': user_id,
        'email': email
    }
    
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def format_user_response(user):
    """
    Format user data for API response
    Removes sensitive information like password hash
    
    Args:
        user: User dict from database
    
    Returns:
        Formatted user dict
    """
    if not user:
        return None
    
    return {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'department': user.get('department'),
        'phone': user.get('phone'),
        'profile_image_url': user.get('profile_image_url'),
        'is_active': user['is_active'],
        'last_login': user.get('last_login').isoformat() if user.get('last_login') else None,
        'created_at': user.get('created_at').isoformat() if user.get('created_at') else None
    }






