# Google Drive Authentication Setup Guide

## Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Name your project (e.g., "Drive API Test")
5. Click "Create"

## Step 2: Enable Google Drive API
1. Select your project
2. Go to "APIs & Services" > "Library"
3. Search for "Google Drive API"
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Fill in required fields:
   - App name
   - User support email
   - Developer contact information
4. Click "Save and Continue"
5. Skip "Scopes" section
6. Add your email as a test user
7. Click "Save and Continue"

## Step 4: Create OAuth Client ID
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as the application type
   - Note: While you might see "Web application" as an option, choose "Desktop app" for this use case
   - This is because we're running a local Python application, not a web server
4. Name your client (e.g., "Drive API Desktop Client")
5. Click "Create"
6. Download the client configuration file

## Step 5: Set Up Credentials
1. Rename downloaded file to `credentials.json`
2. Place it in your project root directory (same level as main.py)
3. Create a credentials directory in your home folder:
   ```bash
   mkdir -p ~/.credentials
   ```
4. Make sure `credentials.json` is in your .gitignore

## Step 6: Configure Root Folder
1. Open Google Drive in your browser
2. Navigate to the folder you want the agent to access
3. Get the folder ID from the URL:
   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Copy the FOLDER_ID_HERE part
4. Add the folder ID to your `.env` file:
   ```
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   ```
5. Make sure the Google account you'll authenticate with has access to this folder

## Step 7: First Run
1. Delete any existing `token.pickle` and `.encryption_key` files
2. Run your application
3. Browser should open for authentication
4. Choose your Google account
5. Grant requested permissions (make sure to use the account that has access to your target folder)

## Troubleshooting
If browser doesn't open:
1. Check logs for error messages
2. Verify `credentials.json` exists and is valid
3. Try running with elevated permissions
4. Check if port 8080 is available

If you can't access files:
1. Verify the folder ID in your `.env` file is correct
2. Confirm your Google account has access to the folder
3. Check the logs for any permission-related errors
4. Try listing folders first to verify basic access works 