import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from typing import List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from router import create_agent_graph
from agent import ReflectiveAgent

# Create the agent graph
graph = create_agent_graph()

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

if __name__ == "__main__":
    import asyncio
    
    async def main():
        while True:
            user_input = input("\nAsk about your Google Drive (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break
                
            # Use reflective agent by default
            responses = await process_user_input(user_input, use_reflection=True)
            for response in responses:
                print(f"\nAssistant: {response}")

    asyncio.run(main())