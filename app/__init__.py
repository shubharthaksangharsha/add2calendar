from flask import Flask
from ..config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Import routes after app is created to avoid circular imports
from app import routes 