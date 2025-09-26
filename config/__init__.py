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

__all__ = [
    'get_system_time_iso',
    'get_system_time_display', 
    'get_system_time_for_database',
    'is_using_fixed_time',
    'set_system_time',
    'use_real_time',
    'get_current_date_time',
    'get_current_date_time_iso'
]