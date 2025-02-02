import logging
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import json
import base64
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from typing import List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from router import create_agent_graph
from agent import ReflectiveAgent

# Create the agent graph
graph = create_agent_graph()

# Add these constants at the top level
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']  # Adjust scopes as needed

def get_google_credentials():
    """Get Google credentials from environment variables."""
    try:
        # Get credentials from environment variables
        credentials_json = os.getenv('GOOGLE_CREDENTIALS')
        token_json = os.getenv('GOOGLE_TOKEN')
        
        if not credentials_json or not token_json:
            raise ValueError("Missing required environment variables: GOOGLE_CREDENTIALS and/or GOOGLE_TOKEN")
            
        # Decode base64 encoded credentials
        credentials_info = json.loads(base64.b64decode(credentials_json))
        token_info = json.loads(base64.b64decode(token_json))
        
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Store refreshed token back to environment
                token_json = base64.b64encode(creds.to_json().encode()).decode()
                # In a cloud environment, you might need to update this differently
                os.environ['GOOGLE_TOKEN'] = token_json
                
        return creds
    except Exception as e:
        logging.error(f"Error getting credentials: {str(e)}")
        raise

async def process_user_input(user_input: str, use_reflection: bool = False) -> List[str]:
    """Process user input and return agent responses."""
    if use_reflection:
        agent = ReflectiveAgent()
        response = await agent.process_message(user_input)
        return [response]
    else:
        # Initialize state
        state = {"messages": [HumanMessage(content=user_input)]}
        # Run the graph
        result = graph.invoke(state)
        # Extract responses
        return [msg.content for msg in result["messages"] if msg.content is not None]

async def main():
    try:
        # Get credentials before starting the main loop
        creds = get_google_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        while True:
            user_input = input("\nAsk about your Google Drive (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break
            
            responses = await process_user_input(user_input, use_reflection=True)
            for response in responses:
                print(f"\nAssistant: {response}")
                
    except Exception as e:
        logging.error(f"Error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())