"""
Statistics Routes
Get dashboard statistics
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database import execute_query

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/', methods=['GET'])
@jwt_required()
def get_stats():
    """Get overall statistics"""
    try:
        # Total documents
        total_docs = execute_query(
            "SELECT COUNT(*) as count FROM documents WHERE is_archived = FALSE",
            fetch_one=True
        )['count']
        
        # Total categories
        total_categories = execute_query(
            "SELECT COUNT(*) as count FROM categories WHERE is_active = TRUE",
            fetch_one=True
        )['count']
        
        # Total users
        total_users = execute_query(
            "SELECT COUNT(*) as count FROM users WHERE is_active = TRUE",
            fetch_one=True
        )['count']
        
        # Total storage used
        total_storage = execute_query(
            "SELECT COALESCE(SUM(file_size), 0) as total FROM documents WHERE is_archived = FALSE",
            fetch_one=True
        )['total']
        
        # Recent uploads (last 7 days)
        recent_uploads = execute_query(
            """
            SELECT COUNT(*) as count 
            FROM documents 
            WHERE is_archived = FALSE 
            AND uploaded_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """,
            fetch_one=True
        )['count']
        
        # Documents by category
        category_stats = execute_query(
            """
            SELECT 
                c.name,
                c.color,
                COUNT(d.id) as count,
                COALESCE(SUM(d.file_size), 0) as total_size
            FROM categories c
            LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
            WHERE c.is_active = TRUE
            GROUP BY c.id
            ORDER BY count DESC
            """,
            fetch_all=True
        )
        
        # Top uploaders
        top_uploaders = execute_query(
            """
            SELECT 
                u.name,
                u.email,
                COUNT(d.id) as upload_count
            FROM users u
            JOIN documents d ON u.id = d.uploaded_by
            WHERE d.is_archived = FALSE
            GROUP BY u.id
            ORDER BY upload_count DESC
            LIMIT 5
            """,
            fetch_all=True
        )
        
        # Documents by file type
        file_type_stats = execute_query(
            """
            SELECT 
                file_type,
                COUNT(*) as count
            FROM documents
            WHERE is_archived = FALSE
            GROUP BY file_type
            ORDER BY count DESC
            """,
            fetch_all=True
        )
        
        return jsonify({
            'totalDocuments': total_docs,
            'totalCategories': total_categories,
            'totalUsers': total_users,
            'totalStorage': total_storage,
            'totalStorageFormatted': format_file_size(total_storage),
            'recentUploads': recent_uploads,
            'categoryStats': [
                {
                    'name': cat['name'],
                    'color': cat['color'],
                    'count': cat['count'],
                    'size': cat['total_size'],
                    'sizeFormatted': format_file_size(cat['total_size'])
                }
                for cat in category_stats
            ],
            'topUploaders': [
                {
                    'name': uploader['name'],
                    'email': uploader['email'],
                    'count': uploader['upload_count']
                }
                for uploader in top_uploaders
            ],
            'fileTypeStats': [
                {
                    'type': ft['file_type'],
                    'count': ft['count']
                }
                for ft in file_type_stats
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500


def format_file_size(bytes_size):
    """Format file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"






