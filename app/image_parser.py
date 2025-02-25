import google.generativeai as genai
from PIL import Image
import os
import json
import re
from datetime import datetime, timedelta

def parse_timetable(image_path):
    # Configure Gemini
    genai.configure(api_key=os.getenv('gemini'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Load the image
    image = Image.open(image_path)
    
    # Prompt for Gemini
    prompt = """
    Analyze this university timetable image and extract the following information in a structured format:
    - Course code
    - Course name
    - Day of the week
    - Start time
    - End time
    - Location
    - Type (Lecture/Workshop/Tutorial)
    
    Format the response as a JSON array of objects with these fields.
    """
    
    # Generate response
    response = model.generate_content([prompt, image])
    
    # Extract JSON from the response
    json_text = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
    if json_text:
        json_str = json_text.group(1)
        events = json.loads(json_str)
        
        # Process the events to match the expected format
        processed_events = []
        for event in events:
            # Convert time format from "10:00am" to "10:00"
            start_time = convert_time_format(event['Start time'])
            end_time = convert_time_format(event['End time'])
            
            processed_event = {
                'course_code': event['Course code'],
                'course_name': event['Course name'],
                'day': event['Day of the week'],
                'start_time': start_time,
                'end_time': end_time,
                'location': event['Location'],
                'type': event['Type']
            }
            processed_events.append(processed_event)
        
        return processed_events
    
    return []

def convert_time_format(time_str):
    """Convert time from '10:00am' format to '10:00' 24-hour format"""
    try:
        # Parse the time string
        time_obj = datetime.strptime(time_str, '%I:%M%p')
        # Convert to 24-hour format
        return time_obj.strftime('%H:%M')
    except ValueError:
        # If the time is in a different format, try alternative parsing
        try:
            time_obj = datetime.strptime(time_str, '%I:%M %p')
            return time_obj.strftime('%H:%M')
        except ValueError:
            print(f"Could not parse time: {time_str}")
            return time_str 