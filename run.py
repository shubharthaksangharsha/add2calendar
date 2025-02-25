from app import app
from dotenv import load_dotenv
import os

load_dotenv()

# Allow HTTP for development
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 