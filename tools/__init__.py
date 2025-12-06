"""
Tools module for the customer support system.
Contains policy search and ticket operation tools.
"""

try:
    # Policy search exports
    from .policy_search import (
        set_vector_db,
        search_policy_knowledge,
        search_policy_knowledge_tool,
    )

    # Ticket tools exports - functions
    from .ticket_tools import (
        # Validation functions
        validate_email,
        validate_booking_reference,
        validate_station_name,
        validate_date_format,
        # Database helper
        get_database_connection,
        # Ticket search functions
        search_available_tickets,
        get_available_ticket_details,
        check_seat_availability,
        # City-based search functions
        search_tickets_by_city,
        search_tickets_from_city,
        search_tickets_to_city,
        search_routes_between_cities,
        get_location_suggestions,
        # Booking functions
        normalize_payment_method,
        book_ticket,
        # Refund functions
        refund_ticket,
        calculate_refund_amount,
        # Customer functions
        get_customer_bookings,
        get_active_tickets_for_customer,
        # Tool instances
        search_available_tickets_tool,
        get_available_ticket_details_tool,
        check_seat_availability_tool,
        search_tickets_by_city_tool,
        search_tickets_from_city_tool,
        search_tickets_to_city_tool,
        search_routes_between_cities_tool,
        get_location_suggestions_tool,
        book_ticket_tool,
        refund_ticket_tool,
        calculate_refund_amount_tool,
        get_customer_bookings_tool,
        get_active_tickets_for_customer_tool,
        ALL_TICKET_TOOLS,
    )

    __all__ = [
        # Policy search
        'set_vector_db',
        'search_policy_knowledge',
        'search_policy_knowledge_tool',
        # Validation
        'validate_email',
        'validate_booking_reference',
        'validate_station_name',
        'validate_date_format',
        # Database
        'get_database_connection',
        # Ticket search
        'search_available_tickets',
        'get_available_ticket_details',
        'check_seat_availability',
        # City search
        'search_tickets_by_city',
        'search_tickets_from_city',
        'search_tickets_to_city',
        'search_routes_between_cities',
        'get_location_suggestions',
        # Booking
        'normalize_payment_method',
        'book_ticket',
        # Refund
        'refund_ticket',
        'calculate_refund_amount',
        # Customer
        'get_customer_bookings',
        'get_active_tickets_for_customer',
        # Tool instances
        'search_available_tickets_tool',
        'get_available_ticket_details_tool',
        'check_seat_availability_tool',
        'search_tickets_by_city_tool',
        'search_tickets_from_city_tool',
        'search_tickets_to_city_tool',
        'search_routes_between_cities_tool',
        'get_location_suggestions_tool',
        'book_ticket_tool',
        'refund_ticket_tool',
        'calculate_refund_amount_tool',
        'get_customer_bookings_tool',
        'get_active_tickets_for_customer_tool',
        'ALL_TICKET_TOOLS',
    ]
except ImportError as e:
    print(f"Warning: Could not import tools: {e}")
    __all__ = []