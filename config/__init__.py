"""
Configuration package for UKConnect Rail System
"""

from .time_config import (
    get_system_time_iso,
    get_system_time_display,
    get_system_time_for_database,
    is_using_fixed_time,
    set_system_time,
    use_real_time,
    # Legacy compatibility
    get_current_date_time,
    get_current_date_time_iso
)

from .constants import (
    DATABASE,
    AGENTS,
    LIMITS,
    TICKET_TYPES,
    BOOKING_STATUS,
    TRAVEL_STATUS,
    PAYMENT,
    VALIDATION,
    ERROR_MESSAGES,
    DISPLAY,
)

__all__ = [
    # Time config
    'get_system_time_iso',
    'get_system_time_display',
    'get_system_time_for_database',
    'is_using_fixed_time',
    'set_system_time',
    'use_real_time',
    'get_current_date_time',
    'get_current_date_time_iso',
    # Constants
    'DATABASE',
    'AGENTS',
    'LIMITS',
    'TICKET_TYPES',
    'BOOKING_STATUS',
    'TRAVEL_STATUS',
    'PAYMENT',
    'VALIDATION',
    'ERROR_MESSAGES',
    'DISPLAY',
]