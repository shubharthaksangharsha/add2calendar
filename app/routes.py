import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for development

from flask import render_template, redirect, request, url_for, session, flash, jsonify
from app import app
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.image_parser import parse_timetable
from app.calendar_helper import create_calendar_events
import functools
from google.oauth2 import id_token
from google.auth.transport import requests
import json

# Get client ID and secret from environment variables
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# OAuth2 configuration
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Add this near the top of your file
print(f"Using Google Client ID: {CLIENT_ID[:5]}...{CLIENT_ID[-5:]}")  # Shows first and last 5 chars only for security

# Decorator for requiring authentication
def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'credentials' not in session:
            return redirect(url_for('google_auth'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template('index.html', 
                         google_authenticated='credentials' in session,
                         email=session.get('email'))

@app.route('/google/auth')
def google_auth():
    # Create a flow instance using client ID and secret from environment variables
    # instead of loading from a file
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [url_for('oauth2callback', _external=True)]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Create flow using client config from environment variables
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [url_for('oauth2callback', _external=True)]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=session['state'],
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    
    # Get user info
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        session['email'] = user_info.get('email')
        session['name'] = user_info.get('name')
    except Exception as e:
        print(f"Error fetching user info: {e}")
    
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect(url_for('index'))

@app.route('/process_timetable', methods=['POST'])
def process_timetable():
    if 'credentials' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
        
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    try:
        # Get options from form
        recurrence_type = request.form.get('recurrenceType', 'biweekly')
        duration = int(request.form.get('duration', '4'))
        calendar_id = request.form.get('calendarId', 'primary')
        reminder_time = int(request.form.get('reminderTime', '10'))
        location_prefix = request.form.get('locationPrefix', '')
        
        # Handle new calendar creation
        if calendar_id == 'new':
            calendar_name = request.form.get('calendarName', 'University Timetable')
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)

        # Parse timetable using Gemini
        timetable_data = parse_timetable(temp_path)
        
        if not timetable_data:
            return jsonify({'success': False, 'error': 'No events parsed from timetable'})

        # Create calendar events using the Google Calendar API
        credentials = Credentials(**session['credentials'])
        
        # Pass options to calendar_helper
        options = {
            'recurrence_type': recurrence_type,
            'duration': duration,
            'calendar_id': calendar_id,
            'reminder_time': reminder_time,
            'location_prefix': location_prefix,
            'calendar_name': request.form.get('calendarName', 'University Timetable')
        }
        
        create_calendar_events(credentials, timetable_data, options)

        # Clean up
        os.remove(temp_path)

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    return render_template('terms.html') 