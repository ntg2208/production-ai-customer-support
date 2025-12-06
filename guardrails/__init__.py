"""
Guardrails Module for UKConnect Customer Support Agent

Provides safety guardrails using Google ADK callbacks to:
- Validate inputs before they reach the LLM
- Filter and moderate outputs before they reach users
- Prevent harmful content, PII exposure, and policy violations
- Log and audit agent behavior

Callback Types:
- before_model_callback: Input validation and filtering
- after_model_callback: Output moderation and filtering
- before_tool_callback: Tool argument validation
- after_tool_callback: Tool result validation
"""

from .callbacks import (
    # Input guardrails
    input_safety_guardrail,
    prompt_injection_guardrail,
    pii_detection_guardrail,
    # Output guardrails
    output_moderation_guardrail,
    hallucination_guardrail,
    # Tool guardrails
    tool_argument_guardrail,
    tool_result_guardrail,
    # Combined guardrails
    create_safety_callbacks,
    GuardrailConfig,
)

from .filters import (
    ContentFilter,
    PIIDetector,
    ToxicityDetector,
)

from .audit_log import GuardrailLogger

__all__ = [
    # Callbacks
    "input_safety_guardrail",
    "prompt_injection_guardrail",
    "pii_detection_guardrail",
    "output_moderation_guardrail",
    "hallucination_guardrail",
    "tool_argument_guardrail",
    "tool_result_guardrail",
    "create_safety_callbacks",
    "GuardrailConfig",
    # Filters
    "ContentFilter",
    "PIIDetector",
    "ToxicityDetector",
    # Logging
    "GuardrailLogger",
]
