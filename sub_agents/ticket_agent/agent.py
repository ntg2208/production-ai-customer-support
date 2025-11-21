"""
Ticket Agent Implementation
Enhanced ticket agent with search, booking, and refund capabilities plus user state context.
"""

from google.adk.agents import Agent

# Direct imports to avoid package import issues
import sys
import os
import importlib.util

# Add required paths
production_path = os.path.join(os.path.dirname(__file__), '../..')
tools_path = os.path.join(production_path, 'tools')
config_path = os.path.join(production_path, 'config')

for path in [production_path, tools_path, config_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import tools directly
from ticket_tools import ALL_TICKET_TOOLS

# Import local prompt directly
prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.py')
spec = importlib.util.spec_from_file_location("ticket_prompt", prompt_path)
ticket_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ticket_prompt)
TICKET_AGENT_INSTRUCTION = ticket_prompt.TICKET_AGENT_INSTRUCTION

# Model configuration
from model_config import get_ticket_agent_model
MODEL_ID = get_ticket_agent_model()

# Ticket agent implementation with full capabilities
ticket_agent = Agent(
    model = MODEL_ID,
    name = "ticket_operations_agent",
    description = "Handles ticket search, booking, and refund operations for UKConnect customers. Can search available tickets, process new bookings, calculate and process refunds, and manage customer ticket accounts. Does not handle company policies or general inquiries.",
    instruction = TICKET_AGENT_INSTRUCTION,
    tools = ALL_TICKET_TOOLS
)

def create_ticket_agent(model_id: str = None):
    """
    Create a ticket agent instance with the specified model.
    
    Args:
        model_id: The model ID to use for the agent (uses default from config if None)
        
    Returns:
        Configured ticket agent instance with full ticket operations capabilities
    """
    if model_id is None:
        model_id = MODEL_ID
    
    return Agent(
        model = model_id,
        name = "ticket_operations_agent",
        description = "Handles ticket search, booking, and refund operations for UKConnect customers. Can search available tickets, process new bookings, calculate and process refunds, and manage customer ticket accounts. Does not handle company policies or general inquiries.",
        instruction = TICKET_AGENT_INSTRUCTION,
        tools = ALL_TICKET_TOOLS
    )