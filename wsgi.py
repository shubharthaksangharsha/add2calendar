import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create config module directly in code if it doesn't exist
if 'config' not in sys.modules:
    import types
    config_module = types.ModuleType('config')
    
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
        UPLOAD_FOLDER = 'uploads'
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    config_module.Config = Config
    sys.modules['config'] = config_module

# Import the Flask app
from app import app

if __name__ == "__main__":
    app.run() 