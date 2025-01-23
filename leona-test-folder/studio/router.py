from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agent import agent_step
from tools import list_folders, search_in_folder

class AgentState(TypedDict):
    """State for the agent workflow."""
    messages: List[BaseMessage]
    next: str

def create_agent_graph() -> StateGraph:
    """Create the agent workflow graph."""
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", lambda state: {
        "messages": [agent_step(state["messages"])],
        "next": None
    })
    workflow.add_node("tools", ToolNode([list_folders, search_in_folder]))
    
    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "continue": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()