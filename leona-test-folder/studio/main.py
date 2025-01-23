from typing import List
from langchain_core.messages import HumanMessage
from router import create_agent_graph, AgentState

# Create the agent graph
graph = create_agent_graph()

def process_user_input(user_input: str) -> List[str]:
    """Process user input and return agent responses."""
    # Initialize state
    state = {"messages": [HumanMessage(content=user_input)]}
    
    # Run the graph
    result = graph.invoke(state)
    
    # Extract responses
    return [msg.content for msg in result["messages"] if msg.content is not None]

if __name__ == "__main__":
    # Example usage
    while True:
        user_input = input("\nAsk about your Google Drive (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
            
        responses = process_user_input(user_input)
        for response in responses:
            print(f"\nAssistant: {response}")