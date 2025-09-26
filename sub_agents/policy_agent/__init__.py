"""
Policy Agent Module
Provides easy access to policy agent functionality with automatic vector database setup.
"""

# Export main components - import only when needed to avoid circular imports
__all__ = [
    'create_policy_agent', 
    'get_policy_agent',
    'setup_policy_vector_db',
    'initialize_policy_agent',
    'POLICY_AGENT_INSTRUCTION'
]

def create_policy_agent(model_id: str = None):
    """Import and create policy agent to avoid circular imports"""
    from .agent import create_policy_agent as _create_policy_agent
    return _create_policy_agent(model_id)

def setup_policy_vector_db():
    """Import and setup vector db to avoid circular imports"""
    from .setup import setup_policy_vector_db as _setup_policy_vector_db
    return _setup_policy_vector_db()

def initialize_policy_agent():
    """Import and initialize policy agent to avoid circular imports"""
    from .setup import initialize_policy_agent as _initialize_policy_agent
    return _initialize_policy_agent()

def get_policy_agent(model_id: str = None, auto_setup: bool = True):
    """
    Get a ready-to-use policy agent with optional automatic setup.
    
    Args:
        model_id: The model ID to use for the agent (uses default from config if None)
        auto_setup: Whether to automatically setup the vector database
        
    Returns:
        tuple: (agent, vector_db) if auto_setup=True, otherwise just agent
    """
    if auto_setup:
        return initialize_policy_agent()
    else:
        return create_policy_agent(model_id)

# Import POLICY_AGENT_INSTRUCTION safely
try:
    from .prompt import POLICY_AGENT_INSTRUCTION
except ImportError:
    POLICY_AGENT_INSTRUCTION = "Policy agent instruction not available"