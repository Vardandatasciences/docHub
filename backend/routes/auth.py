"""
Authentication Routes
Login, Register, Logout, Token Refresh
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import execute_query, get_cursor
from utils.auth_helper import hash_password, verify_password, create_tokens, format_user_response
from utils.validators import validate_email, validate_password, validate_required_fields
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        is_valid, error = validate_required_fields(data, ['name', 'email', 'password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error = validate_password(password)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Check if user already exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        user_id = execute_query(
            """
            INSERT INTO users (name, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, 'user', TRUE)
            """,
            (name, email, password_hash),
            commit=True
        )
        
        # Get created user
        user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        # Create tokens
        tokens = create_tokens(user['id'], user['email'])
        
        return jsonify({
            'message': 'User registered successfully',
            'user': format_user_response(user),
            'tokens': tokens
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        is_valid, error = validate_required_fields(data, ['email', 'password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = execute_query(
            "SELECT * FROM users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user['is_active']:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Verify password
        if not verify_password(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        execute_query(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.now(), user['id']),
            commit=True
        )
        
        # Create tokens
        tokens = create_tokens(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'user': format_user_response(user),
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': format_user_response(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should delete tokens)"""
    return jsonify({
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        identity = get_jwt_identity()
        tokens = create_tokens(identity['id'], identity['email'])
        
        return jsonify({
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500






