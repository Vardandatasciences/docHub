"""
User Management Routes
List users, update profile
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import execute_query
from utils.auth_helper import format_user_response

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only in production)"""
    try:
        users = execute_query(
            """
            SELECT 
                u.*,
                COUNT(DISTINCT d.id) as document_count
            FROM users u
            LEFT JOIN documents d ON u.id = d.uploaded_by AND d.is_archived = FALSE
            WHERE u.is_active = TRUE
            GROUP BY u.id
            ORDER BY u.name
            """,
            fetch_all=True
        )
        
        formatted_users = []
        for user in users:
            user_data = format_user_response(user)
            user_data['documentCount'] = user['document_count']
            formatted_users.append(user_data)
        
        return jsonify({
            'users': formatted_users
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        data = request.get_json()
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data and data['name'].strip():
            updates.append("name = %s")
            params.append(data['name'].strip())
        
        if 'department' in data:
            updates.append("department = %s")
            params.append(data['department'].strip() if data['department'] else None)
        
        if 'phone' in data:
            updates.append("phone = %s")
            params.append(data['phone'].strip() if data['phone'] else None)
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(user_id)
        
        execute_query(
            f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
            tuple(params),
            commit=True
        )
        
        # Get updated user
        user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': format_user_response(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500






