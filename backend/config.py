"""
Configuration file for Flask application
Centralized configuration for easy switching between development and production
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'dochub'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File Upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 
                          'jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp'}  # Image formats for OCR
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL') or 'http://localhost:11434'
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL') or 'llama3.1:8b'
    
    # Smart Model Selection
    USE_SMART_MODEL_SELECTION = os.environ.get('USE_SMART_MODEL_SELECTION', 'true').lower() == 'true'
    # Available models on the server (comma-separated, will be auto-detected if empty)
    OLLAMA_AVAILABLE_MODELS = os.environ.get('OLLAMA_AVAILABLE_MODELS', '').split(',') if os.environ.get('OLLAMA_AVAILABLE_MODELS') else []
    
    # Streaming Configuration
    ENABLE_STREAMING = os.environ.get('ENABLE_STREAMING', 'true').lower() == 'true'
    
    # S3 Configuration (from your s3.py)
    S3_API_BASE_URL = os.environ.get('S3_API_BASE_URL') or 'http://15.207.1.40:3000'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:8080', 'http://localhost:8082']
    
    # Pagination
    DOCUMENTS_PER_PAGE = 20
    
    # API Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Frontend URL for development
    FRONTEND_URL = 'http://localhost:8080'
    
    # Development database (can override here)
    # MYSQL_HOST = 'localhost'
    # MYSQL_DB = 'dochub_dev'
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Frontend URL for production (update with your production domain)
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'https://your-production-domain.com'
    
    # Production database (override with environment variables)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'your-production-db-host'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'dochub_production'
    
    # Production should use environment variables for secrets
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Production CORS (update with your production domains)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else [
        'https://your-production-domain.com'
    ]
    
    # Production logging
    LOG_LEVEL = 'INFO'
    
    # Production S3
    S3_API_BASE_URL = os.environ.get('S3_API_BASE_URL') or 'http://15.207.1.40:3000'


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Test database
    MYSQL_DB = 'dochub_test'
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, config['default'])

