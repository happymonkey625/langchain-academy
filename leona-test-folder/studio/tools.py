from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    """Initialize and return Google Drive service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

@tool
def list_folders() -> str:
    """Lists all folders in Google Drive."""
    service = get_google_drive_service()
    
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder'",
        spaces='drive',
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    folders = results.get('files', [])
    if not folders:
        return "No folders found."
    
    return "\n".join([f"- {folder['name']} (ID: {folder['id']})" for folder in folders])

@tool
def search_in_folder(folder_id: str, query: str) -> str:
    """Searches for files in a specific folder matching the query."""
    service = get_google_drive_service()
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and fullText contains '{query}'",
        spaces='drive',
        fields="files(id, name, mimeType)"
    ).execute()
    
    files = results.get('files', [])
    if not files:
        return f"No files found matching '{query}' in the specified folder."
    
    return "\n".join([f"- {file['name']} ({file['mimeType']})" for file in files]) 