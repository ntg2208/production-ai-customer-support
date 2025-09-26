"""
Centralized Model Configuration for UKConnect Customer Support Agents
This file controls all AI model configurations across the project.
"""

import os
from typing import Dict

# ==============================================
# DEFAULT MODEL CONFIGURATIONS
# ==============================================

DEFAULT_MODELS = {
    "master_agent": "gemini-2.5-flash",
    "ticket_agent": "gemini-2.0-flash", 
    "policy_agent": "gemini-2.0-flash",
    "embedding": "gemini-embedding-001"
}

# Environment-based model overrides
ENV_MODEL_MAPPING = {
    "master_agent": "GEMINI_MODEL_MASTER",
    "ticket_agent": "GEMINI_MODEL_TICKET",
    "policy_agent": "GEMINI_MODEL_POLICY",
    "embedding": "GEMINI_MODEL_EMBEDDING"
}

# ==============================================
# MODEL ACCESS FUNCTIONS
# ==============================================

def get_model_id(agent_type: str) -> str:
    """
    Get the model ID for a specific agent type.
    
    Args:
        agent_type: Type of agent ("master_agent", "ticket_agent", "policy_agent", "embedding")
        
    Returns:
        str: Model ID for the specified agent type
        
    Raises:
        ValueError: If agent_type is not recognized
    """
    if agent_type not in DEFAULT_MODELS:
        raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {list(DEFAULT_MODELS.keys())}")
    
    # Check for environment variable override
    env_var = ENV_MODEL_MAPPING.get(agent_type)
    if env_var and os.getenv(env_var):
        return os.getenv(env_var)
    
    # Return default model
    return DEFAULT_MODELS[agent_type]

def get_master_agent_model() -> str:
    """Get the model ID for the master agent."""
    return get_model_id("master_agent")

def get_ticket_agent_model() -> str:
    """Get the model ID for the ticket agent."""
    return get_model_id("ticket_agent")

def get_policy_agent_model() -> str:
    """Get the model ID for the policy agent."""
    return get_model_id("policy_agent")

def get_embedding_model() -> str:
    """Get the model ID for embeddings."""
    return get_model_id("embedding")

def get_all_models() -> Dict[str, str]:
    """
    Get all model configurations with environment overrides applied.
    
    Returns:
        Dict[str, str]: Dictionary mapping agent types to their model IDs
    """
    return {
        agent_type: get_model_id(agent_type) 
        for agent_type in DEFAULT_MODELS.keys()
    }

# ==============================================
# CONFIGURATION HELPERS
# ==============================================

def set_model_id(agent_type: str, model_id: str):
    """
    Temporarily override a model ID (useful for testing).
    Note: This only affects the current process and does not persist.
    
    Args:
        agent_type: Type of agent to override
        model_id: New model ID to use
    """
    if agent_type not in DEFAULT_MODELS:
        raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {list(DEFAULT_MODELS.keys())}")
    
    env_var = ENV_MODEL_MAPPING[agent_type]
    os.environ[env_var] = model_id

def reset_model_overrides():
    """Reset all model overrides to defaults."""
    for env_var in ENV_MODEL_MAPPING.values():
        if env_var in os.environ:
            del os.environ[env_var]

def is_using_custom_models() -> bool:
    """Check if any custom model configurations are active."""
    return any(os.getenv(env_var) for env_var in ENV_MODEL_MAPPING.values())

# ==============================================
# LEGACY COMPATIBILITY
# ==============================================

# For backward compatibility with existing code
MODEL_ID = get_master_agent_model()

def get_model_config() -> Dict[str, str]:
    """Legacy compatibility function."""
    return get_all_models()

# ==============================================
# VALIDATION
# ==============================================

def validate_model_ids():
    """
    Validate that all configured model IDs are valid.
    This is a basic validation that checks for expected patterns.
    """
    valid_patterns = ["gemini-", "gpt-", "claude-"]
    
    issues = []
    for agent_type, model_id in get_all_models().items():
        if not any(model_id.startswith(pattern) for pattern in valid_patterns):
            issues.append(f"{agent_type}: '{model_id}' doesn't match expected patterns")
    
    if issues:
        print("⚠️  Model configuration warnings:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ All model configurations appear valid")

if __name__ == "__main__":
    print("🤖 Model Configuration Test")
    print("=" * 40)
    
    models = get_all_models()
    for agent_type, model_id in models.items():
        env_override = os.getenv(ENV_MODEL_MAPPING[agent_type])
        source = "environment" if env_override else "default"
        print(f"{agent_type:12}: {model_id} ({source})")
    
    print(f"\nUsing custom models: {is_using_custom_models()}")
    
    print(f"\nValidating model IDs...")
    validate_model_ids()
    
    print(f"\nTesting model override...")
    set_model_id("master_agent", "gemini-1.5-pro")
    print(f"Master agent model after override: {get_master_agent_model()}")
    
    reset_model_overrides()
    print(f"Master agent model after reset: {get_master_agent_model()}")