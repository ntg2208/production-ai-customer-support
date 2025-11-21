"""
Policy Agent Implementation
Direct copy from notebook with minimal changes for internal imports.
"""

from google.adk.agents import Agent

# Direct imports to avoid package import issues
import sys
import os
import importlib.util

# Add required paths
production_path = os.path.join(os.path.dirname(__file__), '../..')
tools_path = os.path.join(production_path, 'tools')

for path in [production_path, tools_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import tools directly
from policy_search import search_policy_knowledge_tool

# Import local prompt directly
prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.py')
spec = importlib.util.spec_from_file_location("policy_prompt", prompt_path)
policy_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy_prompt)
POLICY_AGENT_INSTRUCTION = policy_prompt.POLICY_AGENT_INSTRUCTION

# Model configuration - add config path and import directly
config_path = os.path.join(production_path, 'config')
if config_path not in sys.path:
    sys.path.insert(0, config_path)

from model_config import get_policy_agent_model
MODEL_ID = get_policy_agent_model()

# Policy agent implementation copied directly from notebook
policy_agent = Agent(
    model = MODEL_ID,
    name = "ukconnect_support_agent",
    description = "Handles inquiries about UKConnect company policies, refund and cancellation rules, booking terms and conditions, payment policies, and fare type differences. Does not handle specific customer bookings, train schedules, or operational requests.",
    instruction = POLICY_AGENT_INSTRUCTION,
    tools = [search_policy_knowledge_tool]  # This now includes the policy search tool
)

def create_policy_agent(model_id: str = None):
    """
    Create a policy agent instance with the specified model.
    
    Args:
        model_id: The model ID to use for the agent (uses default from config if None)
        
    Returns:
        Configured policy agent instance
    """
    if model_id is None:
        model_id = MODEL_ID
    
    return Agent(
        model = model_id,
        name = "ukconnect_support_agent",
        description = "Handles inquiries about UKConnect company policies, refund and cancellation rules, booking terms and conditions, payment policies, and fare type differences. Does not handle specific customer bookings, train schedules, or operational requests.",
        instruction = POLICY_AGENT_INSTRUCTION,
        tools = [search_policy_knowledge_tool]
    )