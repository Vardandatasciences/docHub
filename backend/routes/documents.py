"""
Document Management Routes
Upload, List, Download, Delete, Update
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database import execute_query, get_cursor
from utils.s3_helper import upload_file, download_file, get_processing_status
from utils.validators import validate_file_type, get_file_extension, sanitize_filename
import os
import tempfile
import json

documents_bp = Blueprint('documents', __name__)


def get_or_create_uncategorized_category(user_id: int) -> int:
    """
    Get or create the default 'Uncategorized' category.
    Used when uploading documents without a user-selected category.
    """
    # Try to find existing
    category = execute_query(
        "SELECT id FROM categories WHERE name = %s LIMIT 1",
        ('Uncategorized',),
        fetch_one=True
    )
    if category:
        return category['id']

    # Create new 'Uncategorized' category
    category_id = execute_query(
        """
        INSERT INTO categories (name, color, description, document_count, is_active, created_by)
        VALUES (%s, %s, %s, 0, TRUE, %s)
        """,
        (
            'Uncategorized',
            'hsl(222 14% 25%)',  # neutral gray
            'Default category for uncategorized documents',
            user_id,
        ),
        commit=True
    )
    return category_id


@documents_bp.route('/', methods=['GET'])
@jwt_required()
def get_documents():
    """Get all documents with filters"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = """
            SELECT 
                d.*,
                c.name as category_name,
                c.color as category_color,
                u.name as uploaded_by_name,
                u.email as uploaded_by_email
            FROM documents d
            JOIN categories c ON d.category_id = c.id
            JOIN users u ON d.uploaded_by = u.id
            WHERE d.is_archived = FALSE
        """
        params = []
        
        # Add category filter
        if category_id:
            query += " AND d.category_id = %s"
            params.append(category_id)
        
        # Add search filter
        if search:
            query += " AND (d.name LIKE %s OR d.summary LIKE %s OR c.name LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        # Add pagination
        query += " ORDER BY d.uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        
        documents = execute_query(query, tuple(params), fetch_all=True)
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM documents d WHERE d.is_archived = FALSE"
        count_params = []
        if category_id:
            count_query += " AND d.category_id = %s"
            count_params.append(category_id)
        if search:
            count_query += " AND (d.name LIKE %s OR d.summary LIKE %s)"
            count_params.extend([search_term, search_term])
        
        total = execute_query(count_query, tuple(count_params), fetch_one=True)['count']
        
        # Format documents
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                'id': doc['id'],
                'name': doc['name'],
                'originalName': doc['original_name'],
                'category': doc['category_name'],
                'categoryId': doc['category_id'],
                'categoryColor': doc['category_color'],
                'size': doc['file_size_formatted'],
                'type': doc['file_type'],
                'uploadedAt': doc['uploaded_at'].isoformat() if doc['uploaded_at'] else None,
                'uploadedBy': doc['uploaded_by_name'],
                'url': doc['s3_url'],
                's3Key': doc['s3_key'],
                'summary': doc.get('summary'),
                'pageCount': doc.get('page_count'),
                'status': doc.get('status'),
                'processingStatus': doc.get('processing_status'),
                'suggestedCategory': doc.get('suggested_category'),
                # ai_tags is JSON; return as-is, frontend can handle null / list
                'aiTags': json.loads(doc['ai_tags']) if doc.get('ai_tags') else None,
            })
        
        return jsonify({
            'documents': formatted_docs,
            'total': total,
            'page': page,
            'perPage': per_page,
            'totalPages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get documents', 'details': str(e)}), 500


@documents_bp.route('/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    """Get single document by ID"""
    try:
        document = execute_query(
            """
            SELECT 
                d.*,
                c.name as category_name,
                c.color as category_color,
                u.name as uploaded_by_name
            FROM documents d
            JOIN categories c ON d.category_id = c.id
            JOIN users u ON d.uploaded_by = u.id
            WHERE d.id = %s AND d.is_archived = FALSE
            """,
            (doc_id,),
            fetch_one=True
        )
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'document': {
                'id': document['id'],
                'name': document['name'],
                'originalName': document['original_name'],
                'category': document['category_name'],
                'categoryId': document['category_id'],
                'categoryColor': document['category_color'],
                'size': document['file_size_formatted'],
                'type': document['file_type'],
                'uploadedAt': document['uploaded_at'].isoformat(),
                'uploadedBy': document['uploaded_by_name'],
                'url': document['s3_url'],
                's3Key': document['s3_key'],
                'summary': document.get('summary'),
                'extractedText': document.get('extracted_text'),
                'pageCount': document.get('page_count'),
                'wordCount': document.get('word_count'),
                'author': document.get('author'),
                'title': document.get('title'),
                'status': document.get('status'),
                'processingStatus': document.get('processing_status'),
                'suggestedCategory': document.get('suggested_category'),
                'aiTags': json.loads(document['ai_tags']) if document.get('ai_tags') else None,
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get document', 'details': str(e)}), 500


@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document with a user-selected category (existing flow)"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        # Debug logging
        print(f"📤 Upload request from user {user_id}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        # Check if file is present
        if 'file' not in request.files:
            print("❌ Error: No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("❌ Error: Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form data
        category_id = request.form.get('category_id', type=int)
        custom_name = request.form.get('custom_name')
        
        print(f"Category ID received: {category_id} (type: {type(category_id)})")
        print(f"Filename: {file.filename}")
        
        if not category_id:
            print("❌ Error: Category ID is missing or invalid")
            return jsonify({'error': 'Category is required', 'received_category_id': str(request.form.get('category_id'))}), 400
        
        # Validate file type
        if not validate_file_type(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Verify category exists
        category = execute_query(
            "SELECT id, name FROM categories WHERE id = %s AND is_active = TRUE",
            (category_id,),
            fetch_one=True
        )
        
        if not category:
            return jsonify({'error': 'Invalid category'}), 404
        
        # Sanitize filename
        original_filename = sanitize_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Upload to S3
            upload_result = upload_file(
                file_path=temp_path,
                user_id=user_id,
                custom_file_name=custom_name or original_filename,
                module='documents'
            )
            
            if not upload_result.get('success'):
                return jsonify({'error': 'File upload failed', 'details': upload_result}), 500
            
            # Extract S3 URL and key from upload result
            file_info = upload_result.get('file_info', {})
            s3_url = file_info.get('url', '')
            s3_key = file_info.get('s3Key', '')
            
            if not s3_url:
                return jsonify({'error': 'S3 URL not returned from upload', 'details': upload_result}), 500
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            file_size_formatted = format_file_size(file_size)
            
            # Insert document record
            doc_id = execute_query(
                """
                INSERT INTO documents (
                    name, original_name, category_id, file_type, file_size, 
                    file_size_formatted, s3_key, s3_url, uploaded_by, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ready')
                """,
                (
                    custom_name or original_filename,
                    original_filename,
                    category_id,
                    file_extension,
                    file_size,
                    file_size_formatted,
                    s3_key,
                    s3_url,
                    user_id
                ),
                commit=True
            )
            
            # Update category count
            execute_query(
                "UPDATE categories SET document_count = document_count + 1 WHERE id = %s",
                (category_id,),
                commit=True
            )
            
            # Start background processing for OCR and AI analysis
            # Only process if it's an image or might be a scanned PDF
            file_type_lower = file_extension.lower()
            needs_processing = file_type_lower in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp', 'pdf']
            
            if needs_processing:
                try:
                    from utils.document_processor import DocumentProcessor
                    # Pass the real Flask app object so background threads have app context
                    app = current_app._get_current_object()
                    processor = DocumentProcessor(app=app)
                    # Process in background (file will be cleaned up by processor)
                    processor.process_async(
                        document_id=doc_id,
                        file_path=temp_path,
                        file_type=file_extension
                    )
                    print(f"✅ Background processing started for document {doc_id}")
                except Exception as proc_error:
                    print(f"⚠️ Failed to start background processing: {str(proc_error)}")
                    # Don't fail the upload if processing setup fails
                    # Clean up temp file manually
                    if os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except Exception:
                            pass
            else:
                # Clean up temp file if not processing
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            # Get created document
            document = execute_query(
                """
                SELECT 
                    d.*,
                    c.name as category_name,
                    c.color as category_color,
                    u.name as uploaded_by_name
                FROM documents d
                JOIN categories c ON d.category_id = c.id
                JOIN users u ON d.uploaded_by = u.id
                WHERE d.id = %s
                """,
                (doc_id,),
                fetch_one=True
            )
            
            return jsonify({
                'message': 'Document uploaded successfully',
                'document': {
                    'id': document['id'],
                    'name': document['name'],
                    'category': document['category_name'],
                    'categoryColor': document['category_color'],
                    'size': document['file_size_formatted'],
                    'type': document['file_type'],
                    'uploadedAt': document['uploaded_at'].isoformat(),
                    'uploadedBy': document['uploaded_by_name'],
                    'url': document['s3_url'],
                    'status': document['status'],
                    'suggestedCategory': document.get('suggested_category'),
                    'aiTags': json.loads(document.get('ai_tags')) if document.get('ai_tags') else None
                },
                'uploadResult': upload_result,
                'processing': 'started' if needs_processing else 'not_needed'
            }), 201
            
        finally:
            # Note: Temp file cleanup is now handled by document_processor
            # Only clean up here if processing wasn't started
            # (Processing will clean up the file after use)
            pass
        
    except Exception as e:
        return jsonify({'error': 'Upload failed', 'details': str(e)}), 500


@documents_bp.route('/upload-auto', methods=['POST'])
@jwt_required()
def upload_document_auto():
    """
    Upload a new document WITHOUT requiring the user to select a category first.
    
    Flow:
    - File is uploaded
    - Document is stored under a default 'Uncategorized' category
    - Background AI processing runs (OCR + categorization + tags)
    - Frontend can later update the category via a separate endpoint
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        print(f"📤 [AUTO] Upload request from user {user_id}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        # Check if file is present
        if 'file' not in request.files:
            print("❌ Error: No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("❌ Error: Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Optional custom name
        custom_name = request.form.get('custom_name')
        
        print(f"[AUTO] Filename: {file.filename}")
        
        # Validate file type
        if not validate_file_type(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get or create 'Uncategorized' category
        category_id = get_or_create_uncategorized_category(user_id)
        print(f"[AUTO] Using category_id={category_id} ('Uncategorized')")
        
        # Sanitize filename
        original_filename = sanitize_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Upload to S3
            upload_result = upload_file(
                file_path=temp_path,
                user_id=user_id,
                custom_file_name=custom_name or original_filename,
                module='documents'
            )
            
            if not upload_result.get('success'):
                return jsonify({'error': 'File upload failed', 'details': upload_result}), 500
            
            # Extract S3 URL and key from upload result
            file_info = upload_result.get('file_info', {})
            s3_url = file_info.get('url', '')
            s3_key = file_info.get('s3Key', '')
            
            if not s3_url:
                return jsonify({'error': 'S3 URL not returned from upload', 'details': upload_result}), 500
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            file_size_formatted = format_file_size(file_size)
            
            # Insert document record under 'Uncategorized'
            doc_id = execute_query(
                """
                INSERT INTO documents (
                    name, original_name, category_id, file_type, file_size, 
                    file_size_formatted, s3_key, s3_url, uploaded_by, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ready')
                """,
                (
                    custom_name or original_filename,
                    original_filename,
                    category_id,
                    file_extension,
                    file_size,
                    file_size_formatted,
                    s3_key,
                    s3_url,
                    user_id
                ),
                commit=True
            )
            
            # Update category count for 'Uncategorized'
            execute_query(
                "UPDATE categories SET document_count = document_count + 1 WHERE id = %s",
                (category_id,),
                commit=True
            )
            
            # Start background processing for OCR and AI analysis
            file_type_lower = file_extension.lower()
            needs_processing = file_type_lower in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp', 'pdf']
            
            if needs_processing:
                try:
                    from utils.document_processor import DocumentProcessor
                    app = current_app._get_current_object()
                    processor = DocumentProcessor(app=app)
                    processor.process_async(
                        document_id=doc_id,
                        file_path=temp_path,
                        file_type=file_extension
                    )
                    print(f"✅ [AUTO] Background processing started for document {doc_id}")
                except Exception as proc_error:
                    print(f"⚠️ [AUTO] Failed to start background processing: {str(proc_error)}")
                    # Don't fail the upload if processing setup fails
                    if os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except Exception:
                            pass
            else:
                # Clean up temp file if not processing
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass
            
            # Get created document
            document = execute_query(
                """
                SELECT 
                    d.*,
                    c.name as category_name,
                    c.color as category_color,
                    u.name as uploaded_by_name
                FROM documents d
                JOIN categories c ON d.category_id = c.id
                JOIN users u ON d.uploaded_by = u.id
                WHERE d.id = %s
                """,
                (doc_id,),
                fetch_one=True
            )
            
            return jsonify({
                'message': 'Document uploaded successfully',
                'document': {
                    'id': document['id'],
                    'name': document['name'],
                    'category': document['category_name'],
                    'categoryId': document['category_id'],
                    'categoryColor': document['category_color'],
                    'size': document['file_size_formatted'],
                    'type': document['file_type'],
                    'uploadedAt': document['uploaded_at'].isoformat(),
                    'uploadedBy': document['uploaded_by_name'],
                    'url': document['s3_url'],
                    'status': document['status'],
                    'suggestedCategory': document.get('suggested_category'),
                    'aiTags': json.loads(document.get('ai_tags')) if document.get('ai_tags') else None
                },
                'uploadResult': upload_result,
                'processing': 'started' if needs_processing else 'not_needed'
            }), 201
            
        finally:
            # Temp file cleanup is handled by document_processor when processing is started.
            # For error cases where processing didn't start, we attempted cleanup above.
            pass
        
    except Exception as e:
        return jsonify({'error': 'Upload failed', 'details': str(e)}), 500


@documents_bp.route('/<int:doc_id>/category', methods=['PUT'])
@jwt_required()
def update_document_category(doc_id):
    """
    Update document category after upload.
    Optionally update summary as well.
    
    Expected JSON body:
    {
      "category_id": 123,
      "summary": "Optional summary text" (optional)
    }
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        data = request.get_json() or {}
        new_category_id = data.get('category_id')
        summary = data.get('summary')
        
        if not new_category_id:
            return jsonify({'error': 'category_id is required'}), 400
        
        # Get current document
        document = execute_query(
            "SELECT id, category_id, uploaded_by FROM documents WHERE id = %s AND is_archived = FALSE",
            (doc_id,),
            fetch_one=True
        )
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Optional: permission check (uploader or admin)
        user = execute_query(
            "SELECT role FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        if document['uploaded_by'] != user_id and user['role'] != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        old_category_id = document['category_id']
        
        if old_category_id == new_category_id:
            return jsonify({'message': 'Category unchanged'}), 200
        
        # Validate new category exists
        new_category = execute_query(
            "SELECT id, name FROM categories WHERE id = %s AND is_active = TRUE",
            (new_category_id,),
            fetch_one=True
        )
        if not new_category:
            return jsonify({'error': 'Invalid category'}), 404
        
        # Update document category and optionally summary
        if summary:
            execute_query(
                "UPDATE documents SET category_id = %s, summary = %s WHERE id = %s",
                (new_category_id, summary[:2000], doc_id),  # Limit summary to 2000 chars
                commit=True
            )
        else:
            execute_query(
                "UPDATE documents SET category_id = %s WHERE id = %s",
                (new_category_id, doc_id),
                commit=True
            )
        
        # Update category counts
        if old_category_id:
            execute_query(
                "UPDATE categories SET document_count = document_count - 1 WHERE id = %s",
                (old_category_id,),
                commit=True
            )
        execute_query(
            "UPDATE categories SET document_count = document_count + 1 WHERE id = %s",
            (new_category_id,),
            commit=True
        )
        
        return jsonify({'message': 'Category updated successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to update category', 'details': str(e)}), 500


@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete a document (soft delete)"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        # Get document
        document = execute_query(
            "SELECT * FROM documents WHERE id = %s AND is_archived = FALSE",
            (doc_id,),
            fetch_one=True
        )
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check permissions (only uploader or admin can delete)
        user = execute_query(
            "SELECT role FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        if document['uploaded_by'] != user_id and user['role'] != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        # Soft delete
        execute_query(
            "UPDATE documents SET is_archived = TRUE, archived_at = NOW() WHERE id = %s",
            (doc_id,),
            commit=True
        )
        
        # Update category count
        execute_query(
            "UPDATE categories SET document_count = document_count - 1 WHERE id = %s",
            (document['category_id'],),
            commit=True
        )
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Delete failed', 'details': str(e)}), 500


def format_file_size(bytes_size):
    """Format file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

