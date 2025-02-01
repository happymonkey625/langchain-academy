# Cloud Deployment Setup

## Prerequisites
1. Base64 encoded Google credentials
2. Base64 encoded token
3. OpenAI API key
4. Google Drive folder ID

## Environment Variables Setup

1. Generate base64 encoded credentials:
```bash
base64 -w 0 credentials.json > credentials_base64.txt
```

2. Generate base64 encoded token:
```python
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
import json

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

token_json = creds.to_json()
token_base64 = base64.b64encode(token_json.encode()).decode()
print(token_base64)
```

3. Set environment variables in your cloud environment:
```bash
GOOGLE_CREDENTIALS=<content_of_credentials_base64.txt>
GOOGLE_TOKEN=<token_base64_from_script>
OPENAI_API_KEY=<your_openai_api_key>
GOOGLE_DRIVE_FOLDER_ID=<your_folder_id>
```

## Deployment

1. Deploy using LangGraph CLI:
```bash
langgraph deploy cloud/
```

## Local Testing of Cloud Version

To test the cloud version locally:

1. Create a `.env` file in the cloud directory:
```bash
GOOGLE_CREDENTIALS=<base64_credentials>
GOOGLE_TOKEN=<base64_token>
OPENAI_API_KEY=<your_key>
GOOGLE_DRIVE_FOLDER_ID=<folder_id>
```

2. Run the cloud version:
```bash
python cloud/main.py 