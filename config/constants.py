"""
Centralized Constants Module for UKConnect Customer Support System

Contains all magic numbers, strings, and configuration constants used
throughout the application. Centralizing these values makes maintenance
easier and reduces the risk of inconsistent values across the codebase.

Usage:
    from config.constants import DATABASE, AGENTS, LIMITS
"""

from dataclasses import dataclass
from typing import List, Dict


# =============================================================================
# Database Constants
# =============================================================================

@dataclass(frozen=True)
class DatabaseConstants:
    """Database-related constants"""
    # Default database filename
    DEFAULT_DB_NAME: str = "ukconnect_rail.db"

    # Connection settings
    CONNECTION_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    # Query limits
    DEFAULT_QUERY_LIMIT: int = 100
    MAX_QUERY_LIMIT: int = 1000

    # Booking reference format
    BOOKING_PREFIX: str = "UKC"
    BOOKING_REF_LENGTH: int = 6

    # Customer reference format
    CUSTOMER_PREFIX: str = "CUS"
    CUSTOMER_REF_LENGTH: int = 6

    # Transaction reference format
    TRANSACTION_PREFIX: str = "TXN"
    PAYMENT_PREFIX: str = "PAY"
    REFUND_PREFIX: str = "REF"


DATABASE = DatabaseConstants()


# =============================================================================
# Agent Constants
# =============================================================================

@dataclass(frozen=True)
class AgentConstants:
    """Agent-related constants"""
    # Agent names (must match agent definitions)
    MASTER_AGENT_NAME: str = "master_agent"
    POLICY_AGENT_NAME: str = "ukconnect_support_agent"
    TICKET_AGENT_NAME: str = "ticket_operations_agent"

    # Display names for logging/UI
    AGENT_DISPLAY_NAMES: Dict[str, str] = None

    # Default model settings
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: float = 0.3

    # Conversation limits
    MAX_CONVERSATION_TURNS: int = 50
    MAX_MESSAGE_LENGTH: int = 10000

    def __post_init__(self):
        # Workaround for frozen dataclass with mutable defaults
        object.__setattr__(self, 'AGENT_DISPLAY_NAMES', {
            self.MASTER_AGENT_NAME: "Master Agent",
            self.POLICY_AGENT_NAME: "Policy Agent",
            self.TICKET_AGENT_NAME: "Ticket Agent",
        })


# Create instance with proper initialization
class _AgentConstants:
    MASTER_AGENT_NAME: str = "master_agent"
    POLICY_AGENT_NAME: str = "ukconnect_support_agent"
    TICKET_AGENT_NAME: str = "ticket_operations_agent"
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: float = 0.3
    MAX_CONVERSATION_TURNS: int = 50
    MAX_MESSAGE_LENGTH: int = 10000

    AGENT_DISPLAY_NAMES: Dict[str, str] = {
        "master_agent": "Master Agent",
        "ukconnect_support_agent": "Policy Agent",
        "ticket_operations_agent": "Ticket Agent",
    }


AGENTS = _AgentConstants()


# =============================================================================
# Search and Limit Constants
# =============================================================================

@dataclass(frozen=True)
class LimitConstants:
    """Limits and thresholds"""
    # Search limits
    DEFAULT_SEARCH_LIMIT: int = 20
    MAX_SEARCH_LIMIT: int = 100
    DEFAULT_RECENT_DAYS: int = 30

    # RAG/Vector search
    DEFAULT_RAG_RESULTS: int = 5
    MAX_RAG_RESULTS: int = 10
    MIN_SIMILARITY_THRESHOLD: float = 0.5

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 50

    # Response truncation
    MAX_TOOL_RESPONSE_LENGTH: int = 300
    MAX_LOG_MESSAGE_LENGTH: int = 200


LIMITS = LimitConstants()


# =============================================================================
# Ticket Types and Statuses
# =============================================================================

@dataclass(frozen=True)
class TicketTypeConstants:
    """Ticket types and related constants"""
    ADVANCE: str = "advance"
    STANDARD: str = "standard"
    FLEX: str = "flex"
    FIRST_CLASS: str = "first_class"

    ALL_TYPES: tuple = ("advance", "standard", "flex", "first_class")


TICKET_TYPES = TicketTypeConstants()


@dataclass(frozen=True)
class BookingStatusConstants:
    """Booking status values"""
    CONFIRMED: str = "confirmed"
    CANCELLED: str = "cancelled"
    REFUNDED: str = "refunded"
    USED: str = "used"
    PENDING: str = "pending"

    ACTIVE_STATUSES: tuple = ("confirmed", "pending")
    INACTIVE_STATUSES: tuple = ("cancelled", "refunded", "used")


BOOKING_STATUS = BookingStatusConstants()


@dataclass(frozen=True)
class TravelStatusConstants:
    """Travel status values"""
    UPCOMING: str = "upcoming"
    IN_PROGRESS: str = "in_progress"
    COMPLETED: str = "completed"
    MISSED: str = "missed"


TRAVEL_STATUS = TravelStatusConstants()


# =============================================================================
# Payment Constants
# =============================================================================

@dataclass(frozen=True)
class PaymentConstants:
    """Payment-related constants"""
    # Payment methods
    CREDIT_CARD: str = "credit_card"
    DEBIT_CARD: str = "debit_card"
    PAYPAL: str = "paypal"
    APPLE_PAY: str = "apple_pay"
    GOOGLE_PAY: str = "google_pay"
    BANK_TRANSFER: str = "bank_transfer"
    VOUCHER: str = "voucher"
    LOYALTY_POINTS: str = "loyalty_points"

    VALID_METHODS: tuple = (
        "credit_card", "debit_card", "paypal", "apple_pay",
        "google_pay", "bank_transfer", "voucher", "loyalty_points"
    )

    # Currency
    DEFAULT_CURRENCY: str = "GBP"
    DEFAULT_EXCHANGE_RATE: float = 1.0

    # Processing fees
    CARD_PROCESSING_FEE: float = 0.50
    NO_FEE_METHODS: tuple = ("bank_transfer", "voucher", "loyalty_points")


PAYMENT = PaymentConstants()


# =============================================================================
# Validation Constants
# =============================================================================

@dataclass(frozen=True)
class ValidationConstants:
    """Validation-related constants"""
    # Email validation
    MIN_EMAIL_LENGTH: int = 5
    MAX_EMAIL_LENGTH: int = 254

    # Booking reference validation
    MIN_BOOKING_REF_LENGTH: int = 3
    MAX_BOOKING_REF_LENGTH: int = 20

    # Phone number
    UK_PHONE_PATTERN: str = r"^(?:(?:\+44\s?|0)(?:7\d{3}|\d{4})\s?\d{3}\s?\d{3})$"

    # Date format
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    ISO_FORMAT: str = "%Y-%m-%dT%H:%M:%S"


VALIDATION = ValidationConstants()


# =============================================================================
# Error Messages
# =============================================================================

@dataclass(frozen=True)
class ErrorMessageConstants:
    """Standardized error messages"""
    # Database errors
    DB_CONNECTION_FAILED: str = "Failed to connect to database"
    DB_QUERY_FAILED: str = "Database query failed"

    # Validation errors
    INVALID_EMAIL: str = "Invalid email format"
    INVALID_BOOKING_REF: str = "Invalid booking reference"
    INVALID_DATE_FORMAT: str = "Date must be in YYYY-MM-DD format"
    INVALID_TICKET_ID: str = "Ticket ID must be a positive integer"

    # Not found errors
    CUSTOMER_NOT_FOUND: str = "Customer not found"
    BOOKING_NOT_FOUND: str = "Booking not found"
    TICKET_NOT_FOUND: str = "Ticket not found"

    # Business logic errors
    TICKET_UNAVAILABLE: str = "Ticket not available or already booked"
    REFUND_NOT_ALLOWED: str = "Ticket cannot be refunded"
    ALREADY_CANCELLED: str = "Booking has already been cancelled"


ERROR_MESSAGES = ErrorMessageConstants()


# =============================================================================
# UI/Display Constants
# =============================================================================

@dataclass(frozen=True)
class DisplayConstants:
    """Display and formatting constants"""
    # Truncation limits for display
    SHORT_TEXT_LIMIT: int = 50
    MEDIUM_TEXT_LIMIT: int = 100
    LONG_TEXT_LIMIT: int = 200

    # Separator characters
    LINE_SEPARATOR: str = "-" * 50
    DOUBLE_LINE_SEPARATOR: str = "=" * 70


DISPLAY = DisplayConstants()
