from langchain_core.tools import tool
from auth import (
    get_google_drive_service, 
    get_root_folder_id,
    CREDENTIALS_PATH,
    TOKEN_PATH
)
import logging
from typing import Dict, List, Tuple
from langchain_community.document_loaders import GoogleDriveLoader
import os

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

@tool
def search_drive_content(query: str) -> str:
    """
    Searches through Google Drive folders and documents, returning both locations and content summaries.
    """
    try:
        service = get_google_drive_service()
        root_folder_id = get_root_folder_id()
        
        logging.info(f"Starting search with root folder ID: {root_folder_id}")
        
        if not root_folder_id:
            return "No root folder configured. Please set GOOGLE_DRIVE_FOLDER_ID in .env file."

        # Get root folder details
        root_folder = service.files().get(fileId=root_folder_id, fields='name').execute()
        root_name = root_folder.get('name', 'Root Folder')
        root_url = f"https://drive.google.com/drive/folders/{root_folder_id}"
        
        # Get all files in the root folder
        results = service.files().list(
            q=f"'{root_folder_id}' in parents",  # Simplified query
            spaces='drive',
            fields="files(id, name, mimeType)",
            pageSize=1000
        ).execute()
        
        files = results.get('files', [])
        logging.info(f"Found {len(files)} files in root folder")

        if not files:
            return "No files found in the specified folder."

        # Format response
        response = "Upon searching your Google Drive, I found the following documents and files:\n\n"
        
        # Sort files by name
        files.sort(key=lambda x: x['name'])
        
        # List all files with numbers
        for i, file in enumerate(files, 1):
            response += f"{i}. {file['name']}\n"

        return response

    except Exception as e:
        logging.error(f"Error searching drive: {str(e)}")
        return f"Error searching Google Drive: {str(e)}"

def load_google_doc_content(file_id: str) -> str:
    """Loads and summarizes content from a Google Doc."""
    try:
        service = get_google_drive_service()
        file = service.files().get(fileId=file_id, fields='mimeType').execute()
        
        if 'google-apps.document' in file.get('mimeType', ''):
            doc = service.files().export(
                fileId=file_id,
                mimeType='text/plain'
            ).execute()
            
            if isinstance(doc, bytes):
                content = doc.decode('utf-8')
            else:
                content = doc
                
            # Return first 500 chars with smart truncation at sentence end
            preview = content[:500]
            last_period = preview.rfind('.')
            if last_period > 0:
                preview = preview[:last_period + 1]
            return preview + ("..." if len(content) > 500 else "")
        return ""
    except Exception as e:
        logging.error(f"Error loading document content: {str(e)}")
        return "" 