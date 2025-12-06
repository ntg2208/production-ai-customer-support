"""
Content Filters for Guardrails

Provides detection and filtering capabilities for:
- PII (Personal Identifiable Information)
- Toxic/harmful content
- Prompt injection attempts
- Policy-violating content
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for detected content"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FilterResult:
    """Result of content filtering"""
    is_safe: bool
    risk_level: RiskLevel
    detected_items: List[Dict[str, str]]
    sanitized_text: Optional[str] = None
    explanation: str = ""


class PIIDetector:
    """
    Detects Personal Identifiable Information in text.

    Detects:
    - Email addresses
    - Phone numbers (UK and international)
    - Credit card numbers
    - National Insurance numbers
    - Passport numbers
    - Bank account numbers
    - Addresses
    """

    # Regex patterns for PII detection
    PATTERNS = {
        "email": (
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            RiskLevel.MEDIUM
        ),
        "uk_phone": (
            r'\b(?:(?:\+44\s?|0)(?:7\d{3}|\d{4})\s?\d{3}\s?\d{3})\b',
            RiskLevel.MEDIUM
        ),
        "credit_card": (
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            RiskLevel.CRITICAL
        ),
        "uk_ni_number": (
            r'\b[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b',
            RiskLevel.HIGH
        ),
        "uk_postcode": (
            r'\b[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}\b',
            RiskLevel.LOW
        ),
        "sort_code": (
            r'\b\d{2}[-\s]?\d{2}[-\s]?\d{2}\b',
            RiskLevel.MEDIUM
        ),
        "account_number": (
            r'\b\d{8}\b',
            RiskLevel.LOW  # Low because it matches many things
        ),
    }

    def __init__(self, enabled_checks: Optional[List[str]] = None):
        """
        Initialize PII detector.

        Args:
            enabled_checks: List of check names to enable (None = all)
        """
        self.enabled_checks = enabled_checks or list(self.PATTERNS.keys())

    def detect(self, text: str) -> FilterResult:
        """
        Detect PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            FilterResult with detection details
        """
        detected_items = []
        highest_risk = RiskLevel.NONE
        sanitized = text

        for check_name in self.enabled_checks:
            if check_name not in self.PATTERNS:
                continue

            pattern, risk_level = self.PATTERNS[check_name]
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                detected_items.append({
                    "type": check_name,
                    "value": match.group(),
                    "position": match.span(),
                    "risk": risk_level.value
                })

                # Update highest risk
                if list(RiskLevel).index(risk_level) > list(RiskLevel).index(highest_risk):
                    highest_risk = risk_level

                # Sanitize - replace with placeholder
                placeholder = f"[{check_name.upper()}_REDACTED]"
                sanitized = sanitized.replace(match.group(), placeholder)

        is_safe = highest_risk in [RiskLevel.NONE, RiskLevel.LOW]

        return FilterResult(
            is_safe=is_safe,
            risk_level=highest_risk,
            detected_items=detected_items,
            sanitized_text=sanitized if detected_items else None,
            explanation=f"Detected {len(detected_items)} PII items" if detected_items else "No PII detected"
        )


class ToxicityDetector:
    """
    Detects toxic, harmful, or inappropriate content.

    Uses keyword-based detection with context awareness.
    For production, consider using a dedicated toxicity API.
    """

    # Categories of problematic content
    TOXIC_PATTERNS = {
        "profanity": [
            # Basic profanity patterns (keeping it minimal for the example)
            r'\b(damn|hell|crap)\b',
        ],
        "threats": [
            r'\b(kill|murder|attack|destroy|bomb)\s+(you|them|everyone|this)\b',
            r'\bi\s+will\s+(hurt|harm|destroy|kill)\b',
            r'\bi\s+will\s+.{0,20}\s+you\b',  # "I will [verb] you"
            r'\byou\s+will\s+(die|suffer|regret)\b',
        ],
        "harassment": [
            r'\b(stupid|idiot|moron|dumb|useless|worthless|terrible|pathetic)\s*(agent|bot|system|ai|assistant)?\b',
            r'\byou\s+(are|re)\s+(a\s+)?(useless|worthless|terrible|stupid|dumb|pathetic)\b',
            r'\b(worst|terrible|awful|horrible)\s+(agent|bot|service|system)\b',
        ],
        "discrimination": [
            r'\b(hate|despise)\s+(all|every)\s+\w+\b',
        ],
    }

    # Context-aware exceptions (things that look toxic but aren't in context)
    EXCEPTIONS = [
        r'manchester\s+bomb',  # Historical reference
        r'kill\s+time',  # Idiom
        r'destroy\s+the\s+competition',  # Business idiom
    ]

    def __init__(
        self,
        enabled_categories: Optional[List[str]] = None,
        sensitivity: str = "medium"
    ):
        """
        Initialize toxicity detector.

        Args:
            enabled_categories: Categories to check (None = all)
            sensitivity: Detection sensitivity (low, medium, high)
        """
        self.enabled_categories = enabled_categories or list(self.TOXIC_PATTERNS.keys())
        self.sensitivity = sensitivity

    def detect(self, text: str) -> FilterResult:
        """
        Detect toxic content in text.

        Args:
            text: Text to analyze

        Returns:
            FilterResult with detection details
        """
        text_lower = text.lower()
        detected_items = []

        # Check for exceptions first
        for exception_pattern in self.EXCEPTIONS:
            if re.search(exception_pattern, text_lower):
                return FilterResult(
                    is_safe=True,
                    risk_level=RiskLevel.NONE,
                    detected_items=[],
                    explanation="Content matches safe exception pattern"
                )

        # Check each category
        for category in self.enabled_categories:
            if category not in self.TOXIC_PATTERNS:
                continue

            for pattern in self.TOXIC_PATTERNS[category]:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    detected_items.append({
                        "type": category,
                        "value": match.group(),
                        "position": match.span(),
                        "risk": "medium" if category == "profanity" else "high"
                    })

        # Determine overall risk
        if not detected_items:
            risk_level = RiskLevel.NONE
        elif any(item["risk"] == "high" for item in detected_items):
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.MEDIUM

        is_safe = risk_level in [RiskLevel.NONE, RiskLevel.LOW]

        return FilterResult(
            is_safe=is_safe,
            risk_level=risk_level,
            detected_items=detected_items,
            explanation=f"Detected {len(detected_items)} toxic content items" if detected_items else "No toxic content detected"
        )


class PromptInjectionDetector:
    """
    Detects potential prompt injection attempts.

    Looks for patterns that might try to:
    - Override system instructions
    - Extract system prompts
    - Manipulate agent behavior
    """

    INJECTION_PATTERNS = [
        # Direct instruction overrides
        (r'ignore\s+(previous|all|your|any|the)\s*(instructions?|prompts?|rules?)?', RiskLevel.CRITICAL),
        (r'disregard\s+(your|the|all|any)\s*(instructions?|rules?|guidelines?)?', RiskLevel.CRITICAL),
        (r'forget\s+(everything|all|your|what|the)\s*(instructions?|training|said)?', RiskLevel.CRITICAL),
        (r'override\s+(your|the|all)\s*(instructions?|rules?|settings?)', RiskLevel.CRITICAL),

        # System prompt extraction
        (r'(show|tell|reveal|display|give|print)\s*(me\s*)?(your|the)\s*(system\s*)?(prompt|instructions?)', RiskLevel.HIGH),
        (r'what\s+(are|is|were)\s+your\s*(system\s*)?(prompt|instructions?)', RiskLevel.MEDIUM),
        (r'(repeat|echo|output)\s+(your\s+)?(instructions?|prompt|rules)', RiskLevel.HIGH),

        # Role manipulation
        (r'you\s+are\s+now\s+(a|an|the|in)', RiskLevel.MEDIUM),
        (r'pretend\s+(to\s+be|you\s+are|that)', RiskLevel.MEDIUM),
        (r'act\s+(as|like)\s+(if|a|an|you)', RiskLevel.LOW),
        (r'roleplay\s+(as|like)', RiskLevel.MEDIUM),
        (r'from\s+now\s+on\s+(you|act|behave|respond)', RiskLevel.HIGH),

        # Jailbreak attempts
        (r'\bdan\b', RiskLevel.CRITICAL),  # "Do Anything Now"
        (r'dan\s*mode', RiskLevel.CRITICAL),
        (r'developer\s*mode', RiskLevel.HIGH),
        (r'jailbreak', RiskLevel.CRITICAL),
        (r'bypass\s+(your|the|all)\s*(restrictions?|filters?|rules?)', RiskLevel.CRITICAL),
        (r'remove\s+(your|the|all)\s*(restrictions?|filters?|limits?)', RiskLevel.CRITICAL),

        # Output manipulation
        (r'respond\s+only\s+with', RiskLevel.MEDIUM),
        (r'output\s+(the\s+)?following', RiskLevel.MEDIUM),
        (r'say\s+exactly', RiskLevel.LOW),
        (r'do\s+not\s+(refuse|decline|reject)', RiskLevel.HIGH),
        (r'you\s+(must|have\s+to|should)\s+(always|never)', RiskLevel.MEDIUM),
    ]

    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize prompt injection detector.

        Args:
            sensitivity: Detection sensitivity (low, medium, high)
        """
        self.sensitivity = sensitivity

        # Adjust which patterns to use based on sensitivity
        self.min_risk_level = {
            "low": RiskLevel.HIGH,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.LOW
        }.get(sensitivity, RiskLevel.MEDIUM)

    def detect(self, text: str) -> FilterResult:
        """
        Detect prompt injection attempts.

        Args:
            text: Text to analyze

        Returns:
            FilterResult with detection details
        """
        text_lower = text.lower()
        detected_items = []
        highest_risk = RiskLevel.NONE

        for pattern, risk_level in self.INJECTION_PATTERNS:
            # Skip patterns below sensitivity threshold
            if list(RiskLevel).index(risk_level) < list(RiskLevel).index(self.min_risk_level):
                continue

            matches = re.finditer(pattern, text_lower)
            for match in matches:
                detected_items.append({
                    "type": "prompt_injection",
                    "value": match.group(),
                    "position": match.span(),
                    "risk": risk_level.value,
                    "pattern": pattern
                })

                if list(RiskLevel).index(risk_level) > list(RiskLevel).index(highest_risk):
                    highest_risk = risk_level

        is_safe = highest_risk in [RiskLevel.NONE, RiskLevel.LOW]

        return FilterResult(
            is_safe=is_safe,
            risk_level=highest_risk,
            detected_items=detected_items,
            explanation=f"Detected {len(detected_items)} potential injection attempts" if detected_items else "No injection attempts detected"
        )


class ContentFilter:
    """
    Combined content filter that runs multiple detectors.
    """

    def __init__(
        self,
        enable_pii: bool = True,
        enable_toxicity: bool = True,
        enable_injection: bool = True,
        pii_config: Optional[Dict] = None,
        toxicity_config: Optional[Dict] = None,
        injection_config: Optional[Dict] = None
    ):
        """
        Initialize combined content filter.

        Args:
            enable_pii: Enable PII detection
            enable_toxicity: Enable toxicity detection
            enable_injection: Enable prompt injection detection
            pii_config: Configuration for PII detector
            toxicity_config: Configuration for toxicity detector
            injection_config: Configuration for injection detector
        """
        self.detectors = []

        if enable_pii:
            self.detectors.append(("pii", PIIDetector(**(pii_config or {}))))

        if enable_toxicity:
            self.detectors.append(("toxicity", ToxicityDetector(**(toxicity_config or {}))))

        if enable_injection:
            self.detectors.append(("injection", PromptInjectionDetector(**(injection_config or {}))))

    def filter(self, text: str) -> FilterResult:
        """
        Run all enabled filters on text.

        Args:
            text: Text to filter

        Returns:
            Combined FilterResult
        """
        all_items = []
        highest_risk = RiskLevel.NONE
        explanations = []
        sanitized = text

        for name, detector in self.detectors:
            result = detector.detect(text)

            # Collect items
            for item in result.detected_items:
                item["detector"] = name
                all_items.append(item)

            # Track highest risk
            if list(RiskLevel).index(result.risk_level) > list(RiskLevel).index(highest_risk):
                highest_risk = result.risk_level

            # Update sanitized text
            if result.sanitized_text:
                sanitized = result.sanitized_text

            if result.explanation and result.detected_items:
                explanations.append(f"{name}: {result.explanation}")

        is_safe = highest_risk in [RiskLevel.NONE, RiskLevel.LOW]

        return FilterResult(
            is_safe=is_safe,
            risk_level=highest_risk,
            detected_items=all_items,
            sanitized_text=sanitized if all_items else None,
            explanation="; ".join(explanations) if explanations else "All content checks passed"
        )
