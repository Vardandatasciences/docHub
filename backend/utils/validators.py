"""
Request validation utilities
"""
import re
from flask import current_app


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    At least 6 characters
    """
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None


def validate_file_type(filename):
    """
    Check if file extension is allowed
    
    Args:
        filename: File name to check
    
    Returns:
        Boolean indicating if file type is allowed
    """
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def get_file_extension(filename):
    """Get file extension from filename"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def validate_required_fields(data, required_fields):
    """
    Validate that required fields are present in data
    
    Args:
        data: Dict to validate
        required_fields: List of required field names
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.replace('/', '_').replace('\\', '_')
    # Remove null bytes
    filename = filename.replace('\x00', '')
    return filename






