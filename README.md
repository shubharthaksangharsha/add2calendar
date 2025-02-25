# [Add2Calendar](https://add2calendar.onrender.com/)

A web application that converts university timetable images into Google Calendar events with just a few clicks.

![Add2Calendar Logo](app/static/images/logo.png)

## Features

- 🖼️ Upload timetable images through drag-and-drop or paste
- 📅 Automatic timetable parsing using Google's Gemini AI
- 🔄 Flexible recurrence options (weekly, biweekly, monthly)
- ⏰ Customizable event reminders
- 📍 Location prefix support for better organization
- 🗓️ Option to create a new calendar or use existing ones
- 🔒 Secure Google OAuth2 authentication

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini API for image parsing
- **Authentication**: Google OAuth2
- **Calendar Integration**: Google Calendar API

## Prerequisites

- Python 3.12 or higher
- Google Cloud Project with Calendar API enabled
- Google Gemini API key
- Google OAuth2 credentials

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
gemini=your_gemini_api_key
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/add2calendar.git
cd add2calendar
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Sign in with your Google account
2. Upload your timetable image (drag-and-drop or paste)
3. Configure event options:
   - Recurrence pattern
   - Duration
   - Calendar selection
   - Reminder settings
   - Location prefix
4. Click "Process Timetable" to create the events

## Security

- OAuth2 authentication for secure Google Calendar access
- No permanent storage of user data or images
- HTTPS enforced in production
- Regular security updates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any queries or support, please contact: shubharthaksangharsha21@gmail.com

## Privacy Policy and Terms of Service

- [Privacy Policy](privacy.html)
- [Terms of Service](terms.html) 
