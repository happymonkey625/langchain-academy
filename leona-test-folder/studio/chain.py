from typing import List
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from tools import list_folders, search_in_folder

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

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

def create_chain():
    """Create and configure the agent chain."""
    # Initialize the model
    model = ChatOpenAI()
    
    # Bind tools to the model
    model_with_tools = model.bind_tools([list_folders, search_in_folder])
    
    return model_with_tools

def get_system_message() -> SystemMessage:
    """Get the system message for the agent."""
    return SystemMessage(content=SYSTEM_PROMPT)

def execute_chain_step(chain, messages: List[BaseMessage]) -> BaseMessage:
    """Execute one step of the chain."""
    return chain.invoke([get_system_message()] + messages) 