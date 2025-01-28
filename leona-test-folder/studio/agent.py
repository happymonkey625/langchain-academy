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
import logging

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
SYSTEM_PROMPT = """You are a helpful AI assistant that helps users find and understand information in their Google Drive.
You have access to the following tools:
- search_drive_content: Searches through Google Drive folders and documents, returning both locations and content summaries

Follow these steps when helping users:
1. Use search_drive_content to find relevant documents
2. Review the content summaries provided
3. Provide a clear, organized response that includes:
   - Where the relevant information was found (file paths)
   - A synthesis of the key information from the documents
   - Any relevant connections between documents
"""

system_message = SystemMessage(content=SYSTEM_PROMPT)

def agent_step(messages: List[BaseMessage]) -> BaseMessage:
    """Execute one step of the agent."""
    try:
        chain = create_chain()
        # First try to list folders
        folders = list_folders()
        
        # If we have a query in the message, search in relevant folders
        user_query = messages[-1].content if messages else ""
        search_results = []
        
        # Extract folder IDs from the folders response
        folder_ids = []
        for line in folders.split('\n'):
            if '(ID:' in line:
                folder_id = line.split('(ID:')[1].strip()[:-1]  # Remove the closing parenthesis
                folder_ids.append(folder_id)
        
        # Search in each folder
        for folder_id in folder_ids:
            result = search_in_folder(folder_id, user_query)
            if not result.startswith("No files found"):
                search_results.append(result)
        
        # Combine the results
        response = f"Folders found:\n{folders}\n\n"
        if search_results:
            response += "Search results:\n" + "\n".join(search_results)
        else:
            response += f"No files found matching your query: '{user_query}'"
            
        return HumanMessage(content=response)
    except Exception as e:
        logging.error(f"Error in agent_step: {str(e)}")
        return HumanMessage(content=f"Error accessing Google Drive: {str(e)}")

class ReflectiveAgent:
    def __init__(self, llm=None, tools=None):
        self.llm = llm or ChatOpenAI()
        self.tools = tools or [list_folders, search_in_folder]
        self.model_with_tools = self.llm.bind_tools(self.tools)

    def reflect_on_response(self, original_response: str) -> str:
        """
        Analyzes and potentially improves the response before delivering it.
        """
        reflection_prompt = f"""
        Please analyze the following response and improve it if necessary:
        
        Original Response: {original_response}
        
        Consider the following aspects:
        1. Completeness: Does it fully address the user's needs?
        2. Clarity: Is it clear and well-structured?
        3. Accuracy: Are all statements correct?
        4. Actionability: Does it provide concrete steps if needed?
        
        If improvements are needed, provide an enhanced version. If the response is already optimal, return it unchanged.
        
        Enhanced Response:
        """
        
        messages = [HumanMessage(content=reflection_prompt)]
        response = self.llm.invoke(messages)
        return response.content

    async def get_initial_response(self, message: str) -> str:
        """Gets initial response using existing agent logic."""
        try:
            # First list all folders
            folders_result = await list_folders.ainvoke("")  # Use empty string as input
            
            # Search in each folder for the query
            search_results = []
            for line in folders_result.split('\n'):
                if '(ID:' in line:
                    folder_id = line.split('(ID:')[1].strip()[:-1]
                    result = await search_in_folder.ainvoke({"folder_id": folder_id, "query": message})
                    if not result.startswith("No files found"):
                        search_results.append(result)
            
            # Combine results
            response = f"I searched your Google Drive and found:\n\n"
            if search_results:
                response += "\n".join(search_results)
            else:
                response += f"No files found matching your query: '{message}'"
            
            return response
            
        except Exception as e:
            logging.error(f"Error getting initial response: {str(e)}")
            return f"Error accessing Google Drive: {str(e)}"

    async def process_message(self, message: str) -> str:
        """Process message with reflection."""
        try:
            initial_response = await self.get_initial_response(message)
            if not initial_response:
                return "I couldn't access Google Drive. Please check your authentication."
            final_response = self.reflect_on_response(initial_response)
            return final_response
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return f"An error occurred: {str(e)}"
