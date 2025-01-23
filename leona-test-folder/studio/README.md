# Google Drive ReAct Agent

A LangGraph-based agent that can interact with Google Drive to help users find and search through their files and folders using natural language queries.

## Features

- Natural language interaction with Google Drive
- Folder listing and searching
- File content search within folders
- Reflective responses with self-improvement
- Persistent authentication
- Modular and extensible architecture

## Project Structure

```
studio/
├── main.py          # Main entry point and CLI interface
├── agent.py         # Agent implementation with ReflectiveAgent
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

## Using ReflectiveAgent

The application includes a ReflectiveAgent that enhances responses by:
1. Generating initial responses
2. Analyzing them for:
   - Completeness
   - Clarity
   - Accuracy
   - Actionability
3. Improving responses when needed

Example usage:
```python
from studio.agent import ReflectiveAgent

agent = ReflectiveAgent()
response = await agent.process_message("Find presentations in my work folder")
```

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

## Google Drive Authentication Setup

1. Create Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Drive API

2. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials

3. Set Up Authentication:
   - Rename downloaded file to `credentials.json`
   - Place it in your project root directory
   - First run will open browser for authentication
   - Credentials are cached in `token.pickle`

4. Managing Tokens:
   - `token.pickle` stores authenticated credentials
   - Delete it to force re-authentication
   - Update SCOPES to require re-authentication

### Troubleshooting Authentication

Common issues and solutions:

1. Missing credentials.json:
   ```bash
   FileNotFoundError: Missing credentials.json
   ```
   Solution: Download OAuth credentials from Google Cloud Console

2. Invalid token:
   ```bash
   Delete token.pickle and restart the application
   ```

3. Scope changes:
   ```bash
   Delete token.pickle if you modify SCOPES
   ```

4. Permission issues:
   - Ensure Google Drive API is enabled
   - Check OAuth consent screen settings
   - Verify SCOPES in tools.py 