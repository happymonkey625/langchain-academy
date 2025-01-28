import os
from langchain_google_community import GoogleDriveLoader
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Suppress oauth2client cache warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_PATH = str(Path.home() / '.credentials' / 'token.json')
CREDENTIALS_PATH = 'credentials.json'

def verify_credentials_file():
    """Verify credentials.json exists and is valid."""
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"credentials.json not found in {os.path.abspath(CREDENTIALS_PATH)}")
        
        with open(CREDENTIALS_PATH, 'r') as f:
            creds_data = json.load(f)
            required_keys = ['installed', 'client_id', 'client_secret']
            if not all(key in creds_data.get('installed', {}) for key in required_keys):
                raise ValueError("credentials.json is missing required fields")
            
        logging.info("credentials.json verified successfully")
        return True
    except Exception as e:
        logging.error(f"Credentials verification failed: {str(e)}")
        raise

def get_google_drive_service():
    """Initialize and return Google Drive service using LangChain's GoogleDriveLoader."""
    try:
        logging.info("Starting Google Drive authentication process...")
        
        # Verify credentials file
        verify_credentials_file()
        
        # Ensure credentials directory exists
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        
        logging.info(f"Using token path: {TOKEN_PATH}")
        logging.info(f"Using credentials path: {os.path.abspath(CREDENTIALS_PATH)}")
        
        # Initialize the loader
        loader = GoogleDriveLoader(
            credentials_path=CREDENTIALS_PATH,
            token_path=TOKEN_PATH,
            folder_id=os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
            recursive=False
        )
        
        logging.info("Attempting to get Google Drive service...")
        service = loader.get_service()
        logging.info("Successfully authenticated with Google Drive")
        
        # Verify service works
        try:
            service.files().list(pageSize=1).execute()
            logging.info("Successfully tested Google Drive API connection")
        except Exception as e:
            logging.error(f"Failed to test Google Drive connection: {str(e)}")
            raise
        
        return service
        
    except Exception as e:
        logging.error(f"Error initializing Google Drive service: {str(e)}")
        raise

def get_root_folder_id():
    """Get the root folder ID for the application."""
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    logging.info(f"Environment variables loaded: {dict(os.environ)}")  # Debug line
    logging.info(f"Retrieved folder ID: {folder_id}")  # Debug line
    
    if not folder_id:
        logging.warning("GOOGLE_DRIVE_FOLDER_ID not set in environment variables")
    return folder_id 