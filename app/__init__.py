from flask import Flask
import os

app = Flask(__name__)

# Try to import config, but have fallback if it fails
try:
    from config import Config
    app.config.from_object(Config)
except ImportError:
    # Fallback configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Import routes after app is created to avoid circular imports
from app import routes 