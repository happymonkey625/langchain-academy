import logging
from auth import get_google_drive_service, get_root_folder_id
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_drive_connection():
    """Test Google Drive authentication and connection."""
    try:
        # Get service
        service = get_google_drive_service()
        
        # Get root folder ID
        folder_id = get_root_folder_id()
        if not folder_id:
            print("Warning: No root folder ID configured")
            return
        
        # Test listing files
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10
        ).execute()
        
        print("\nSuccessfully connected to Google Drive!")
        print(f"Found {len(results.get('files', []))} files in root folder")
        
    except Exception as e:
        print(f"\nError testing Google Drive connection: {str(e)}")

if __name__ == "__main__":
    test_google_drive_connection() 