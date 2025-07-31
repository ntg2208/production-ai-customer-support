"""
Policy Agent Module
Provides easy access to policy agent functionality with automatic vector database setup.
"""

# Handle imports for both direct execution and package import
try:
    from .agent import policy_agent, create_policy_agent
    from .setup import setup_policy_vector_db, initialize_policy_agent
    from .prompt import POLICY_AGENT_INSTRUCTION
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    sys.path.insert(0, current_dir)
    from agent import policy_agent, create_policy_agent
    from setup import setup_policy_vector_db, initialize_policy_agent
    from prompt import POLICY_AGENT_INSTRUCTION

# Simple factory function that combines setup and agent creation
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

# Export main components
__all__ = [
    'policy_agent',
    'create_policy_agent', 
    'get_policy_agent',
    'setup_policy_vector_db',
    'initialize_policy_agent',
    'POLICY_AGENT_INSTRUCTION'
]