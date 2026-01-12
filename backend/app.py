"""
Main Flask Application
DocHub - Document Management System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
import os

# Import blueprints
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.categories import categories_bp
from routes.users import users_bp
from routes.stats import stats_bp
from routes.chatbot.chat import chat_bp

# Import database
from database import init_db, close_db


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Disable strict slashes to avoid 308 redirects
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    CORS(app, 
         origins=app.config['CORS_ORIGINS'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Content-Type'])  # Allow streaming headers
    JWTManager(app)
    
    # Initialize database
    init_db(app)
    
    # Register teardown
    @app.teardown_appcontext
    def teardown_db(exception=None):
        close_db()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'environment': config_name,
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': 'DocHub API',
            'version': '1.0.0',
            'environment': config_name,
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'documents': '/api/documents',
                'categories': '/api/categories',
                'users': '/api/users',
                'stats': '/api/stats',
                'chat': '/api/chat'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': 'Invalid request data'}), 400
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

