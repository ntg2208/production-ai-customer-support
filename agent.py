"""
Customer Support Coordinator Implementation
The main coordinator agent to provide seamless customer assistance, working with 2 specialist teams: booking team and policy team
Provides comprehensive support across all service areas
"""

from google.adk.agents import Agent

# Import centralized model configuration with fallback
try:
    from .config.model_config import get_master_agent_model
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config.model_config import get_master_agent_model

# Model configuration
MODEL_ID = get_master_agent_model()

# Cache for master agent instance
_master_agent = None

def get_master_agent():
    """Get the configured customer support coordinator instance with proper sub-agent initialization"""
    global _master_agent

    if _master_agent is None:
        # Import sub-agents with proper initialization
        try:
            # Initialize Policy Agent with its vector database (global resource)
            from .sub_agents.policy_agent import initialize_policy_agent
            policy_agent, vector_db = initialize_policy_agent()

            # Initialize Ticket Agent with its database tools (global resource)
            from .sub_agents.ticket_agent.agent import ticket_agent

            from .prompt import MASTER_AGENT_INSTRUCTION
        except ImportError:
            # Fallback for direct execution
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sub_agents', 'policy_agent'))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sub_agents', 'ticket_agent'))

            # Initialize with proper setup functions
            from sub_agents.policy_agent import initialize_policy_agent
            policy_agent, vector_db = initialize_policy_agent()

            from sub_agents.ticket_agent.agent import ticket_agent
            from prompt import MASTER_AGENT_INSTRUCTION

        # Create customer support coordinator with fully initialized sub-agents
        _master_agent = Agent(
            model=MODEL_ID,
            name="master_agent",
            instruction=MASTER_AGENT_INSTRUCTION,
            sub_agents=[ticket_agent, policy_agent]
        )

    return _master_agent

if __name__ == "__main__":
    print("✅ Customer Support Coordinator created with seamless assistance!")
    print("🎯 Natural conversation flow implemented!")
    print("🔄 Ready to provide comprehensive support across all service areas!")

    try:
        agent = get_master_agent()
        print(f"✅ Customer Support Coordinator: {agent.name}")
        print(f"📝 Sub-agents: {len(agent.sub_agents)}")
        for i, sub_agent in enumerate(agent.sub_agents):
            print(f"   - Sub-agent {i+1}: {sub_agent.name}")
        print(f"📝 Instruction length: {len(agent.instruction)} characters")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
