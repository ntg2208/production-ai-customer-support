"""
Ticket Agent Module
Provides ticket operations functionality including search, booking, and refunds.
"""

# Handle imports for both direct execution and package import
try:
    from .agent import ticket_agent, create_ticket_agent
    from .prompt import TICKET_AGENT_INSTRUCTION
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    sys.path.insert(0, current_dir)
    from agent import ticket_agent, create_ticket_agent
    from prompt import TICKET_AGENT_INSTRUCTION

def get_ticket_agent(model_id: str = None):
    """
    Get a ready-to-use ticket agent.
    
    Args:
        model_id: The model ID to use for the agent (uses default from config if None)
        
    Returns:
        Configured ticket agent instance
    """
    return create_ticket_agent(model_id)

# Export main components
__all__ = [
    'ticket_agent',
    'create_ticket_agent', 
    'get_ticket_agent',
    'TICKET_AGENT_INSTRUCTION'
]