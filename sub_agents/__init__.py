"""
Sub-agents module for the customer support system.
Contains specialized agents for policy and ticket operations.
"""

# Export modules - avoid direct imports to prevent circular import issues
__all__ = ['policy_agent', 'ticket_agent']

# Lazy import functions to avoid circular imports
def get_policy_agent():
    """Get policy agent instance"""
    from .policy_agent.agent import policy_agent
    return policy_agent

def get_ticket_agent():
    """Get ticket agent instance"""
    from .ticket_agent.agent import ticket_agent
    return ticket_agent