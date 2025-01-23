from langchain_core.tools import tool
from auth import get_google_drive_service, get_root_folder_id
import logging

@tool
def list_folders() -> str:
    """Lists all folders within the specified root folder."""
    try:
        service = get_google_drive_service()
        root_folder_id = get_root_folder_id()
        
        if not root_folder_id:
            return "No root folder configured. Please set GOOGLE_DRIVE_FOLDER_ID in .env file."
        
        # Query for folders within the root folder
        results = service.files().list(
            q=f"'{root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        folders = results.get('files', [])
        if not folders:
            return "No folders found in the specified directory."
        
        return "\n".join([f"- {folder['name']} (ID: {folder['id']})" for folder in folders])
    except Exception as e:
        logging.error(f"Error listing folders: {str(e)}")
        return f"Error accessing Google Drive: {str(e)}"

@tool
def search_in_folder(folder_id: str, query: str) -> str:
    """Searches for files in a specific folder matching the query."""
    try:
        service = get_google_drive_service()
        root_folder_id = get_root_folder_id()
        
        # First verify if the folder_id is within our root folder
        folder_info = service.files().get(
            fileId=folder_id,
            fields="parents"
        ).execute()
        
        if root_folder_id not in folder_info.get('parents', []):
            return "Access to this folder is not allowed."
        
        results = service.files().list(
            q=f"'{folder_id}' in parents and fullText contains '{query}'",
            spaces='drive',
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            return f"No files found matching '{query}' in the specified folder."
        
        return "\n".join([f"- {file['name']} ({file['mimeType']})" for file in files])
    except Exception as e:
        logging.error(f"Error searching folder: {str(e)}")
        raise

@tool
def get_folder_id(folder_name: str) -> str:
    """Gets the ID of a folder by its name within the root folder."""
    try:
        service = get_google_drive_service()
        root_folder_id = get_root_folder_id()
        
        results = service.files().list(
            q=f"'{root_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        
        folders = results.get('files', [])
        if not folders:
            return f"No folder named '{folder_name}' found."
        
        return f"Folder ID for '{folder_name}': {folders[0]['id']}"
    except Exception as e:
        logging.error(f"Error getting folder ID: {str(e)}")
        raise 