"""
Production AI Customer Support System

A comprehensive customer support system with specialized agents for handling
policy inquiries and ticket operations, coordinated by a master agent.
"""

# Version info
__version__ = '1.0.0'

# Main exports - use lazy imports to avoid circular import issues
__all__ = ['get_master_agent', 'get_policy_agent', 'get_ticket_agent']

def get_master_agent():
    """Get master agent instance"""
    from .agent import get_master_agent as _get_master_agent
    return _get_master_agent()

def get_policy_agent():
    """Get policy agent instance"""
    from .sub_agents import get_policy_agent as _get_policy_agent
    return _get_policy_agent()

def get_ticket_agent():
    """Get ticket agent instance"""
    from .sub_agents import get_ticket_agent as _get_ticket_agent
    return _get_ticket_agent()