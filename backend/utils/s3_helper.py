"""
S3 Helper - Wrapper for s3.py RenderS3Client
Provides easy access to S3 operations
"""
from flask import current_app
import sys
import os

# Add parent directory to path to import s3.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from s3 import RenderS3Client
from database import get_mysql_config


_s3_client = None


def get_s3_client():
    """
    Get or create S3 client instance
    Uses configuration from Flask app
    """
    global _s3_client
    
    if _s3_client is None:
        mysql_config = get_mysql_config()
        _s3_client = RenderS3Client(
            api_base_url=current_app.config['S3_API_BASE_URL'],
            mysql_config=mysql_config
        )
    
    return _s3_client


def upload_file(file_path, user_id, custom_file_name=None, module=None, framework_id=None):
    """
    Upload file to S3
    
    Args:
        file_path: Path to file to upload
        user_id: User ID performing upload
        custom_file_name: Optional custom filename
        module: Optional module name
        framework_id: Optional framework ID
    
    Returns:
        Dict with upload result
    """
    client = get_s3_client()
    return client.upload(
        file_path=file_path,
        user_id=str(user_id),
        custom_file_name=custom_file_name,
        module=module,
        framework_id=framework_id
    )


def download_file(s3_key, file_name, destination_path="./downloads", user_id="default-user"):
    """
    Download file from S3
    
    Args:
        s3_key: S3 key of file
        file_name: Original filename
        destination_path: Where to save file
        user_id: User ID performing download
    
    Returns:
        Dict with download result
    """
    client = get_s3_client()
    return client.download(
        s3_key=s3_key,
        file_name=file_name,
        destination_path=destination_path,
        user_id=str(user_id)
    )


def export_data(data, export_format, file_name, user_id):
    """
    Export data to various formats
    
    Args:
        data: Data to export (list of dicts or dict)
        export_format: Format (xlsx, csv, json, xml, pdf, txt)
        file_name: Output filename
        user_id: User ID performing export
    
    Returns:
        Dict with export result
    """
    client = get_s3_client()
    return client.export(
        data=data,
        export_format=export_format,
        file_name=file_name,
        user_id=str(user_id)
    )


def get_processing_status(operation_id):
    """
    Get PDF/document processing status
    
    Args:
        operation_id: Operation ID from upload
    
    Returns:
        Dict with processing status
    """
    client = get_s3_client()
    return client.get_pdf_processing_status(operation_id)


def test_s3_connection():
    """Test S3 connection"""
    client = get_s3_client()
    return client.test_connection()






