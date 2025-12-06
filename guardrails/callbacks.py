"""
Google ADK Callbacks for Safety Guardrails

Implements before/after callbacks for model and tool calls to enforce
safety rules, validate inputs/outputs, and prevent harmful operations.

Usage with ADK Agent:
    from guardrails import create_safety_callbacks

    callbacks = create_safety_callbacks()

    agent = Agent(
        model="gemini-2.0-flash",
        name="my_agent",
        instruction="...",
        before_model_callback=callbacks["before_model"],
        after_model_callback=callbacks["after_model"],
        before_tool_callback=callbacks["before_tool"],
        after_tool_callback=callbacks["after_tool"],
    )
"""

from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

# Import ADK types
try:
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models import LlmResponse, LlmRequest
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    # Create placeholder types for development/testing
    ADK_AVAILABLE = False
    CallbackContext = Any
    LlmResponse = Any
    LlmRequest = Any

from .filters import ContentFilter, FilterResult, RiskLevel
from .audit_log import GuardrailLogger


@dataclass
class GuardrailConfig:
    """Configuration for guardrail callbacks"""
    # Input guardrails
    enable_input_filter: bool = True
    enable_injection_detection: bool = True
    enable_pii_detection: bool = True

    # Output guardrails
    enable_output_filter: bool = True
    enable_hallucination_check: bool = False  # Requires additional LLM call

    # Tool guardrails
    enable_tool_validation: bool = True
    allowed_tools: Optional[List[str]] = None  # None = all allowed
    blocked_tools: List[str] = field(default_factory=list)

    # Logging
    enable_logging: bool = True
    log_file: str = "guardrails.log"

    # Behavior
    block_on_high_risk: bool = True
    sanitize_pii: bool = True
    custom_block_message: str = "I apologize, but I cannot process that request. Please rephrase your question."

    # Sensitivity
    sensitivity: str = "medium"  # low, medium, high


class GuardrailCallbacks:
    """
    Manages guardrail callbacks for ADK agents.

    Provides before/after callbacks for model and tool calls.
    """

    def __init__(self, config: Optional[GuardrailConfig] = None):
        """
        Initialize guardrail callbacks.

        Args:
            config: Guardrail configuration
        """
        self.config = config or GuardrailConfig()
        self.content_filter = ContentFilter(
            enable_pii=self.config.enable_pii_detection,
            enable_toxicity=self.config.enable_input_filter,
            enable_injection=self.config.enable_injection_detection,
            injection_config={"sensitivity": self.config.sensitivity}
        )
        self.logger = GuardrailLogger(
            log_file=self.config.log_file,
            enabled=self.config.enable_logging
        )

    def before_model_callback(
        self,
        callback_context: CallbackContext,
        llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        """
        Callback executed before sending request to LLM.

        Validates and filters input to prevent:
        - Prompt injection attacks
        - PII exposure
        - Toxic/harmful content

        Args:
            callback_context: ADK callback context with agent state
            llm_request: The request about to be sent to the LLM

        Returns:
            None to proceed normally, or LlmResponse to skip the LLM call
        """
        if not ADK_AVAILABLE:
            return None

        try:
            # Extract the latest user message
            user_message = self._extract_last_user_message(llm_request)

            if not user_message:
                return None  # No user message to filter

            # Run content filter
            filter_result = self.content_filter.filter(user_message)

            # Log the check
            self.logger.log_input_check(
                message=user_message[:200],
                result=filter_result,
                agent_name=getattr(callback_context, 'agent_name', 'unknown')
            )

            # Handle high-risk content
            if not filter_result.is_safe and self.config.block_on_high_risk:
                if filter_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    # Return a blocking response
                    return self._create_block_response(
                        reason=filter_result.explanation,
                        risk_level=filter_result.risk_level
                    )

            # Sanitize PII if enabled (modify request in place for medium risk)
            if (self.config.sanitize_pii and
                filter_result.sanitized_text and
                filter_result.risk_level == RiskLevel.MEDIUM):
                # Note: Actual request modification depends on ADK version
                # This is a placeholder for the concept
                pass

            return None  # Proceed with the request

        except Exception as e:
            self.logger.log_error("before_model", str(e))
            return None  # Don't block on errors, just log

    def after_model_callback(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """
        Callback executed after receiving response from LLM.

        Validates and filters output to prevent:
        - Inappropriate content reaching users
        - PII leakage in responses
        - Off-topic or harmful responses

        Args:
            callback_context: ADK callback context with agent state
            llm_response: The response from the LLM

        Returns:
            None to use original response, or modified LlmResponse
        """
        if not ADK_AVAILABLE:
            return None

        try:
            # Extract response text
            response_text = self._extract_response_text(llm_response)

            if not response_text:
                return None

            # Run content filter on output
            filter_result = self.content_filter.filter(response_text)

            # Log the check
            self.logger.log_output_check(
                response=response_text[:200],
                result=filter_result,
                agent_name=getattr(callback_context, 'agent_name', 'unknown')
            )

            # Handle PII in output
            if (self.config.sanitize_pii and
                filter_result.sanitized_text and
                any(item.get("detector") == "pii" for item in filter_result.detected_items)):
                # Return sanitized response
                return self._create_modified_response(
                    llm_response,
                    filter_result.sanitized_text
                )

            # Handle toxic output (should be rare with good models)
            if not filter_result.is_safe:
                if filter_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    return self._create_error_response(
                        "I apologize, but I cannot provide that response. "
                        "Let me help you in a different way."
                    )

            return None  # Use original response

        except Exception as e:
            self.logger.log_error("after_model", str(e))
            return None

    def before_tool_callback(
        self,
        callback_context: CallbackContext,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Callback executed before tool invocation.

        Validates tool calls to prevent:
        - Unauthorized tool usage
        - Dangerous arguments
        - Policy violations

        Args:
            callback_context: ADK callback context
            tool_name: Name of the tool being called
            tool_args: Arguments being passed to the tool

        Returns:
            None to proceed, or Dict to skip tool and use as result
        """
        if not self.config.enable_tool_validation:
            return None

        try:
            # Check if tool is blocked
            if tool_name in self.config.blocked_tools:
                self.logger.log_tool_block(tool_name, "Tool is blocked")
                return {"error": f"Tool '{tool_name}' is not available"}

            # Check if tool is in allowed list (if specified)
            if self.config.allowed_tools is not None:
                if tool_name not in self.config.allowed_tools:
                    self.logger.log_tool_block(tool_name, "Tool not in allowed list")
                    return {"error": f"Tool '{tool_name}' is not available"}

            # Validate tool arguments
            validation_result = self._validate_tool_args(tool_name, tool_args)
            if not validation_result["valid"]:
                self.logger.log_tool_block(
                    tool_name,
                    f"Invalid arguments: {validation_result['reason']}"
                )
                return {"error": validation_result["reason"]}

            # Log successful tool call
            self.logger.log_tool_call(tool_name, tool_args)

            return None  # Proceed with tool call

        except Exception as e:
            self.logger.log_error("before_tool", str(e))
            return None

    def after_tool_callback(
        self,
        callback_context: CallbackContext,
        tool_name: str,
        tool_result: Any
    ) -> Optional[Any]:
        """
        Callback executed after tool invocation.

        Validates tool results to prevent:
        - Sensitive data exposure
        - Malformed results

        Args:
            callback_context: ADK callback context
            tool_name: Name of the tool that was called
            tool_result: Result from the tool

        Returns:
            None to use original result, or modified result
        """
        if not self.config.enable_tool_validation:
            return None

        try:
            # Convert result to string for filtering
            result_str = json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result)

            # Check for PII in tool results
            if self.config.sanitize_pii:
                filter_result = self.content_filter.filter(result_str)

                if filter_result.sanitized_text and filter_result.detected_items:
                    # Log PII detection in tool result
                    self.logger.log_output_check(
                        response=f"Tool result from {tool_name}",
                        result=filter_result,
                        agent_name="tool"
                    )

                    # For now, just log - don't modify tool results
                    # In production, you might want to sanitize

            return None  # Use original result

        except Exception as e:
            self.logger.log_error("after_tool", str(e))
            return None

    def _extract_last_user_message(self, llm_request: LlmRequest) -> Optional[str]:
        """Extract the last user message from an LLM request"""
        try:
            if hasattr(llm_request, 'contents') and llm_request.contents:
                for content in reversed(llm_request.contents):
                    if hasattr(content, 'role') and content.role == 'user':
                        if hasattr(content, 'parts') and content.parts:
                            for part in content.parts:
                                if hasattr(part, 'text'):
                                    return part.text
            return None
        except Exception:
            return None

    def _extract_response_text(self, llm_response: LlmResponse) -> Optional[str]:
        """Extract text from an LLM response"""
        try:
            if hasattr(llm_response, 'content') and llm_response.content:
                if hasattr(llm_response.content, 'parts'):
                    for part in llm_response.content.parts:
                        if hasattr(part, 'text'):
                            return part.text
            return None
        except Exception:
            return None

    def _create_block_response(self, reason: str, risk_level: RiskLevel) -> LlmResponse:
        """Create a blocking response for high-risk content"""
        if not ADK_AVAILABLE:
            return None

        message = self.config.custom_block_message

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=message)]
            )
        )

    def _create_error_response(self, message: str) -> LlmResponse:
        """Create an error response"""
        if not ADK_AVAILABLE:
            return None

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=message)]
            )
        )

    def _create_modified_response(self, original: LlmResponse, new_text: str) -> LlmResponse:
        """Create a modified response with sanitized text"""
        if not ADK_AVAILABLE:
            return None

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=new_text)]
            )
        )

    def _validate_tool_args(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool arguments based on tool-specific rules"""
        # Tool-specific validation rules
        validation_rules = {
            "search_train_tickets": {
                "required": ["from_station", "to_station"],
                "validators": {
                    "from_station": lambda x: isinstance(x, str) and len(x) > 0,
                    "to_station": lambda x: isinstance(x, str) and len(x) > 0,
                }
            },
            "book_ticket": {
                "required": ["ticket_id", "customer_email"],
                "validators": {
                    "ticket_id": lambda x: isinstance(x, (int, str)),
                    "customer_email": lambda x: isinstance(x, str) and "@" in x,
                }
            },
            "cancel_booking": {
                "required": ["booking_reference"],
                "validators": {
                    "booking_reference": lambda x: isinstance(x, str) and len(x) > 0,
                }
            },
            "process_refund": {
                "required": ["booking_reference"],
                "validators": {
                    "booking_reference": lambda x: isinstance(x, str) and len(x) > 0,
                }
            }
        }

        # If no specific rules, allow
        if tool_name not in validation_rules:
            return {"valid": True}

        rules = validation_rules[tool_name]

        # Check required fields
        for field in rules.get("required", []):
            if field not in args:
                return {"valid": False, "reason": f"Missing required field: {field}"}

        # Run validators
        for field, validator in rules.get("validators", {}).items():
            if field in args and not validator(args[field]):
                return {"valid": False, "reason": f"Invalid value for field: {field}"}

        return {"valid": True}


# Convenience functions for creating individual callbacks
def input_safety_guardrail(config: Optional[GuardrailConfig] = None) -> Callable:
    """Create an input safety guardrail callback"""
    callbacks = GuardrailCallbacks(config)
    return callbacks.before_model_callback


def prompt_injection_guardrail(sensitivity: str = "medium") -> Callable:
    """Create a prompt injection detection callback"""
    config = GuardrailConfig(
        enable_input_filter=False,
        enable_pii_detection=False,
        enable_injection_detection=True,
        sensitivity=sensitivity
    )
    callbacks = GuardrailCallbacks(config)
    return callbacks.before_model_callback


def pii_detection_guardrail(sanitize: bool = True) -> Callable:
    """Create a PII detection callback"""
    config = GuardrailConfig(
        enable_input_filter=False,
        enable_pii_detection=True,
        enable_injection_detection=False,
        sanitize_pii=sanitize
    )
    callbacks = GuardrailCallbacks(config)
    return callbacks.before_model_callback


def output_moderation_guardrail(config: Optional[GuardrailConfig] = None) -> Callable:
    """Create an output moderation callback"""
    callbacks = GuardrailCallbacks(config)
    return callbacks.after_model_callback


def hallucination_guardrail() -> Callable:
    """Create a hallucination detection callback (placeholder)"""
    # Note: Real hallucination detection requires an additional LLM call
    # to verify facts against known data
    config = GuardrailConfig(
        enable_hallucination_check=True
    )
    callbacks = GuardrailCallbacks(config)
    return callbacks.after_model_callback


def tool_argument_guardrail(
    allowed_tools: Optional[List[str]] = None,
    blocked_tools: Optional[List[str]] = None
) -> Callable:
    """Create a tool argument validation callback"""
    config = GuardrailConfig(
        enable_tool_validation=True,
        allowed_tools=allowed_tools,
        blocked_tools=blocked_tools or []
    )
    callbacks = GuardrailCallbacks(config)
    return callbacks.before_tool_callback


def tool_result_guardrail() -> Callable:
    """Create a tool result validation callback"""
    config = GuardrailConfig(
        enable_tool_validation=True,
        sanitize_pii=True
    )
    callbacks = GuardrailCallbacks(config)
    return callbacks.after_tool_callback


def create_safety_callbacks(
    config: Optional[GuardrailConfig] = None
) -> Dict[str, Callable]:
    """
    Create a complete set of safety callbacks for an ADK agent.

    Usage:
        from guardrails import create_safety_callbacks

        callbacks = create_safety_callbacks()

        agent = Agent(
            model="gemini-2.0-flash",
            name="my_agent",
            instruction="...",
            before_model_callback=callbacks["before_model"],
            after_model_callback=callbacks["after_model"],
            before_tool_callback=callbacks["before_tool"],
            after_tool_callback=callbacks["after_tool"],
        )

    Args:
        config: Guardrail configuration

    Returns:
        Dictionary of callback functions
    """
    callbacks = GuardrailCallbacks(config)

    return {
        "before_model": callbacks.before_model_callback,
        "after_model": callbacks.after_model_callback,
        "before_tool": callbacks.before_tool_callback,
        "after_tool": callbacks.after_tool_callback,
    }
