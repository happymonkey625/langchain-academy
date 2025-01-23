# Google Drive ReAct Agent

A LangGraph-based agent that can interact with Google Drive to help users find and search through their files and folders using natural language queries.

## Project Structure

```
studio/
├── main.py          # Main entry point and CLI interface
├── agent.py         # Agent implementation
├── chain.py         # Chain and prompt configuration
├── router.py        # Graph structure and routing
├── tools.py         # Google Drive tools
└── requirements.txt # Dependencies
```

### Component Overview

#### 1. `main.py`
- Entry point for the application
- Handles user interaction through CLI
- Processes user input and displays responses
- Manages the conversation flow

#### 2. `agent.py`
- Core agent implementation
- Integrates chain execution with the agent's decision-making
- Handles message processing and agent state

#### 3. `chain.py`
- Manages prompt templates and system messages
- Configures and creates the LangChain chain
- Handles chain execution logic
- Integrates OpenAI model with tools

#### 4. `router.py`
- Defines the graph structure using LangGraph
- Manages state transitions and workflow
- Handles routing between agent and tools
- Implements conditional logic for tool usage

#### 5. `tools.py`
- Google Drive API integration
- Tool implementations for:
  - Listing folders
  - Searching within folders
- Handles authentication and credentials

## Setup and Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Drive API:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download and save as `credentials.json` in the studio folder

3. Set up environment variables:
   - Create a `.env` file
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

## Usage

1. Run the application:
```bash
python main.py
```

2. First-time setup:
   - Browser will open for Google authentication
   - Authorize the application
   - Credentials will be saved in `token.pickle`

3. Example queries:
   - "What folders do I have in my Drive?"
   - "Find all documents containing 'project' in the Reports folder"
   - "List all spreadsheets in my Work folder"

## Flow Diagram

```
User Input → main.py
     ↓
Router (router.py)
     ↓
Agent (agent.py) ←→ Chain (chain.py)
     ↓
Tools (tools.py) ←→ Google Drive API
```

## Features

- Natural language interaction with Google Drive
- Folder listing and searching
- File content search within folders
- Persistent authentication
- Modular and extensible architecture

## Dependencies

- langgraph
- langchain-core
- langchain-community
- langchain-openai
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- pydantic
- typing-extensions

## Error Handling

The application includes error handling for:
- Authentication failures
- API rate limits
- File/folder not found
- Permission issues
- Invalid queries

## Contributing

Feel free to submit issues and enhancement requests! 