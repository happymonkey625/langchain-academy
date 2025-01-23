from typing import List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
from chain import create_chain, execute_chain_step

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

# Create the model with tools
model = ChatOpenAI()
model_with_tools = model.bind_tools([list_folders, search_in_folder])

# System message for the agent
SYSTEM_PROMPT = """You are a helpful AI assistant that helps users find information in their Google Drive.
You have access to the following tools:
- list_folders: Lists all folders in Google Drive
- search_in_folder: Searches for files in a specific folder matching a query

Follow these steps:
1. First understand what the user is looking for
2. List folders if needed
3. Search in relevant folders
4. Provide a clear and concise answer"""

system_message = SystemMessage(content=SYSTEM_PROMPT)

def agent_step(messages: List[BaseMessage]) -> BaseMessage:
    """Execute one step of the agent."""
    chain = create_chain()
    return execute_chain_step(chain, messages)
