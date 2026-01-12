"""
Run script for Flask application
Loads environment variables and starts the app
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and create app
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Run the app
    print(f"""
    ╔═══════════════════════════════════════════════════╗
    ║         DocHub API Server Starting...            ║
    ╠═══════════════════════════════════════════════════╣
    ║  Environment: {os.environ.get('FLASK_ENV', 'development'):<35} ║
    ║  Host:        {host:<35} ║
    ║  Port:        {port:<35} ║
    ║  URL:         http://{host}:{port:<25} ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )






