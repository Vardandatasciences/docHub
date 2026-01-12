"""
Category Management Routes
List, Create, Update, Delete categories
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import execute_query

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all active categories"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        query = """
            SELECT 
                c.*,
                u.name as created_by_name,
                COUNT(d.id) as actual_document_count
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
        """
        
        if not include_inactive:
            query += " WHERE c.is_active = TRUE"
        
        query += " GROUP BY c.id ORDER BY c.name"
        
        categories = execute_query(query, fetch_all=True)
        
        formatted_categories = []
        for cat in categories:
            formatted_categories.append({
                'id': cat['id'],
                'name': cat['name'],
                'color': cat['color'],
                'description': cat.get('description'),
                'icon': cat.get('icon'),
                'count': cat['actual_document_count'],
                'isActive': cat['is_active'],
                'createdBy': cat.get('created_by_name'),
                'createdAt': cat['created_at'].isoformat() if cat['created_at'] else None
            })
        
        return jsonify({
            'categories': formatted_categories
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Get single category"""
    try:
        category = execute_query(
            """
            SELECT 
                c.*,
                COUNT(d.id) as document_count
            FROM categories c
            LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
            WHERE c.id = %s
            GROUP BY c.id
            """,
            (category_id,),
            fetch_one=True
        )
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({
            'category': {
                'id': category['id'],
                'name': category['name'],
                'color': category['color'],
                'description': category.get('description'),
                'icon': category.get('icon'),
                'count': category['document_count'],
                'isActive': category['is_active'],
                'createdAt': category['created_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get category', 'details': str(e)}), 500


@categories_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
        
        name = data['name'].strip()
        color = data.get('color', 'hsl(38 92% 50%)')
        description = data.get('description', '').strip()
        icon = data.get('icon', '').strip()
        
        # Check if category already exists
        existing = execute_query(
            "SELECT id FROM categories WHERE name = %s",
            (name,),
            fetch_one=True
        )
        
        if existing:
            return jsonify({'error': 'Category already exists'}), 409
        
        # Insert category
        category_id = execute_query(
            """
            INSERT INTO categories (name, color, description, icon, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, color, description if description else None, icon if icon else None, user_id),
            commit=True
        )
        
        # Get created category
        category = execute_query(
            "SELECT * FROM categories WHERE id = %s",
            (category_id,),
            fetch_one=True
        )
        
        return jsonify({
            'message': 'Category created successfully',
            'category': {
                'id': category['id'],
                'name': category['name'],
                'color': category['color'],
                'description': category.get('description'),
                'icon': category.get('icon'),
                'count': 0,
                'isActive': category['is_active']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create category', 'details': str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update a category"""
    try:
        data = request.get_json()
        
        # Check if category exists
        category = execute_query(
            "SELECT * FROM categories WHERE id = %s",
            (category_id,),
            fetch_one=True
        )
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data and data['name'].strip():
            updates.append("name = %s")
            params.append(data['name'].strip())
        
        if 'color' in data:
            updates.append("color = %s")
            params.append(data['color'])
        
        if 'description' in data:
            updates.append("description = %s")
            params.append(data['description'].strip() if data['description'] else None)
        
        if 'icon' in data:
            updates.append("icon = %s")
            params.append(data['icon'].strip() if data['icon'] else None)
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(category_id)
        
        execute_query(
            f"UPDATE categories SET {', '.join(updates)} WHERE id = %s",
            tuple(params),
            commit=True
        )
        
        # Get updated category
        updated_category = execute_query(
            """
            SELECT 
                c.*,
                COUNT(d.id) as document_count
            FROM categories c
            LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
            WHERE c.id = %s
            GROUP BY c.id
            """,
            (category_id,),
            fetch_one=True
        )
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': {
                'id': updated_category['id'],
                'name': updated_category['name'],
                'color': updated_category['color'],
                'description': updated_category.get('description'),
                'icon': updated_category.get('icon'),
                'count': updated_category['document_count'],
                'isActive': updated_category['is_active']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update category', 'details': str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category (soft delete)"""
    try:
        # Check if category exists
        category = execute_query(
            "SELECT * FROM categories WHERE id = %s",
            (category_id,),
            fetch_one=True
        )
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Check if category has documents
        doc_count = execute_query(
            "SELECT COUNT(*) as count FROM documents WHERE category_id = %s AND is_archived = FALSE",
            (category_id,),
            fetch_one=True
        )['count']
        
        if doc_count > 0:
            return jsonify({
                'error': f'Cannot delete category with {doc_count} documents. Please reassign or delete documents first.'
            }), 400
        
        # Soft delete
        execute_query(
            "UPDATE categories SET is_active = FALSE WHERE id = %s",
            (category_id,),
            commit=True
        )
        
        return jsonify({'message': 'Category deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete category', 'details': str(e)}), 500






