from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dateutil.relativedelta import relativedelta
import json
import os

def create_calendar_events(credentials, events, options):
    try:
        # Build the service with the credentials object
        service = build('calendar', 'v3', credentials=credentials)
        
        # Handle calendar creation if needed
        calendar_id = options['calendar_id']
        if calendar_id == 'new':
            calendar = {
                'summary': options['calendar_name'],
                'timeZone': 'Australia/Adelaide'
            }
            created_calendar = service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar['id']
        
        # Set up recurrence rule based on options
        recurrence_type = options['recurrence_type']
        duration = options['duration']
        
        # Calculate end date based on duration
        today = datetime.now()
        end_date = today + relativedelta(months=duration)
        until_date = end_date.strftime('%Y%m%dT000000Z')
        
        # Set up recurrence rule
        if recurrence_type == 'weekly':
            recurrence = [f'RRULE:FREQ=WEEKLY;UNTIL={until_date}']
        elif recurrence_type == 'biweekly':
            recurrence = [f'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={until_date}']
        elif recurrence_type == 'monthly':
            recurrence = [f'RRULE:FREQ=MONTHLY;UNTIL={until_date}']
        else:  # 'none'
            recurrence = []
        
        # Set up reminder
        reminder_time = options['reminder_time']
        reminders = {
            'useDefault': False,
            'overrides': []
        }
        
        if reminder_time > 0:
            reminders['overrides'].append({
                'method': 'popup',
                'minutes': reminder_time
            })
        
        # Process location prefix
        location_prefix = options['location_prefix']
        
        for event in events:
            # Calculate the event date
            event_date = calculate_event_date(event['day'])
            
            # Apply location prefix if provided
            location = event['location']
            if location_prefix and not location.startswith(location_prefix):
                location = f"{location_prefix}{location}"
            
            # Create event body
            event_body = {
                'summary': f"{event['course_code']} - {event['type']}",
                'location': location,
                'description': f"Course: {event['course_name']}\nType: {event['type']}",
                'start': {
                    'dateTime': f"{event_date}T{event['start_time']}:00",
                    'timeZone': 'Australia/Adelaide',
                },
                'end': {
                    'dateTime': f"{event_date}T{event['end_time']}:00",
                    'timeZone': 'Australia/Adelaide',
                },
                'reminders': reminders
            }
            
            # Add recurrence if not 'none'
            if recurrence:
                event_body['recurrence'] = recurrence
            
            try:
                # Create the event
                created_event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
                print(f'Event created: {created_event.get("htmlLink")}')
            except Exception as e:
                print(f'Error creating event: {str(e)}')

    except Exception as e:
        print(f'Error in create_calendar_events: {str(e)}')
        raise

def calculate_event_date(day_of_week):
    # Map day names to numbers (0 = Monday, 6 = Sunday)
    day_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    # Get the first day of the semester (3rd February 2025)
    semester_start = datetime(2025, 2, 3)
    
    # Calculate days to add to get to the first occurrence of the class
    days_to_add = (day_map[day_of_week] - semester_start.weekday()) % 7
    
    # Return the date string
    target_date = semester_start + timedelta(days=days_to_add)
    return target_date.strftime('%Y-%m-%d') 