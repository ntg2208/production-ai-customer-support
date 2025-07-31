"""
Centralized Time Configuration for UKConnect Rail System
This file controls all time-related operations across the project.
"""

from datetime import datetime
from typing import Optional

# ==============================================
# MAIN TIME CONFIGURATION - CHANGE THIS TO CONTROL ALL TIMES
# ==============================================

# Set this to your desired test time, or None to use real current time
SYSTEM_CURRENT_TIME: Optional[str] = "2025-07-29 14:30:00"

# Alternative format for agent prompts 
SYSTEM_CURRENT_TIME_DISPLAY: Optional[str] = "Monday 2025-07-29 14:30 GMT"

# ==============================================
# TIME ACCESS FUNCTIONS
# ==============================================

def get_system_time_iso() -> str:
    """
    Get the system time in ISO format (YYYY-MM-DD HH:MM:SS) for database operations.
    
    Returns:
        str: System time in ISO format
    """
    if SYSTEM_CURRENT_TIME:
        return SYSTEM_CURRENT_TIME
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_system_time_display() -> str:
    """
    Get the system time in display format for agent prompts.
    
    Returns:
        str: System time in display format (e.g., "Monday 2025-07-29 14:30 GMT")
    """
    if SYSTEM_CURRENT_TIME_DISPLAY:
        return SYSTEM_CURRENT_TIME_DISPLAY
    elif SYSTEM_CURRENT_TIME:
        # Convert ISO to display format
        dt = datetime.fromisoformat(SYSTEM_CURRENT_TIME)
        weekday = dt.strftime("%A")
        date_part = dt.strftime("%Y-%m-%d %H:%M")
        return f"{weekday} {date_part} GMT"
    else:
        # Use current time
        now = datetime.now()
        weekday = now.strftime("%A")
        date_part = now.strftime("%Y-%m-%d %H:%M")
        return f"{weekday} {date_part} GMT"

def get_system_time_for_database() -> str:
    """
    Get the system time formatted for database queries with quote marks.
    
    Returns:
        str: Quoted system time for SQL queries
    """
    return f"'{get_system_time_iso()}'"

def is_using_fixed_time() -> bool:
    """
    Check if the system is using a fixed time (not real current time).
    
    Returns:
        bool: True if using fixed time, False if using real time
    """
    return SYSTEM_CURRENT_TIME is not None

# ==============================================
# LEGACY COMPATIBILITY
# ==============================================

def get_current_date_time() -> str:
    """Legacy compatibility function for existing code."""
    return get_system_time_display()

def get_current_date_time_iso() -> str:
    """Legacy compatibility function for existing code."""
    return get_system_time_iso()

# ==============================================
# CONFIGURATION HELPERS
# ==============================================

def set_system_time(time_iso: str, time_display: Optional[str] = None):
    """
    Set the system time (useful for testing).
    
    Args:
        time_iso: Time in ISO format (YYYY-MM-DD HH:MM:SS)
        time_display: Optional display format, will be auto-generated if not provided
    """
    global SYSTEM_CURRENT_TIME, SYSTEM_CURRENT_TIME_DISPLAY
    SYSTEM_CURRENT_TIME = time_iso
    
    if time_display:
        SYSTEM_CURRENT_TIME_DISPLAY = time_display
    else:
        # Auto-generate display format
        dt = datetime.fromisoformat(time_iso)
        weekday = dt.strftime("%A")
        date_part = dt.strftime("%Y-%m-%d %H:%M")
        SYSTEM_CURRENT_TIME_DISPLAY = f"{weekday} {date_part} GMT"

def use_real_time():
    """Switch to using real current time instead of fixed time."""
    global SYSTEM_CURRENT_TIME, SYSTEM_CURRENT_TIME_DISPLAY
    SYSTEM_CURRENT_TIME = None
    SYSTEM_CURRENT_TIME_DISPLAY = None

if __name__ == "__main__":
    print("🕐 Time Configuration Test")
    print("=" * 40)
    print(f"Using fixed time: {is_using_fixed_time()}")
    print(f"System time ISO: {get_system_time_iso()}")
    print(f"System time display: {get_system_time_display()}")
    print(f"System time for DB: {get_system_time_for_database()}")
    
    print(f"\nTesting time change...")
    set_system_time("2025-12-25 09:30:00")
    print(f"New system time ISO: {get_system_time_iso()}")
    print(f"New system time display: {get_system_time_display()}")
    
    print(f"\nTesting real time...")
    use_real_time()
    print(f"Using fixed time: {is_using_fixed_time()}")
    print(f"Real time ISO: {get_system_time_iso()}")