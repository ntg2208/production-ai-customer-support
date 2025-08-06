#!/usr/bin/env python3
"""
Customer Setup Utility for Test Scenarios
Provides realistic customer state setup using actual database customers
"""

import sys
import os
import json

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.database import UKConnectDB

# Import centralized time configuration
try:
    from config.time_config import get_system_time_iso, get_system_time_display
except ImportError:
    # If that doesn't work, try adding config to path
    config_path = os.path.join(project_root, 'config')
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from time_config import get_system_time_iso, get_system_time_display

# Import location intelligence (handle both relative and absolute imports)
try:
    from .location_intelligence import get_customer_location_context
except ImportError:
    try:
        from location_intelligence import get_customer_location_context
    except ImportError:
        # Fallback: add utils to path and try again
        utils_path = os.path.dirname(os.path.abspath(__file__))
        if utils_path not in sys.path:
            sys.path.insert(0, utils_path)
        from location_intelligence import get_customer_location_context

# Customer mapping for test scenarios
CUSTOMER_SCENARIO_MAPPING = {
    'session_1_new_customer': {
        'customer_email': 'james.thompson@email.co.uk',
        'customer_id': 'CUS001',
        'name': 'James Thompson',
        'description': 'New customer learning about UKConnect services'
    },
    'session_2_refund_rebooking': {
        'customer_email': 'sarah.williams@email.co.uk',
        'customer_id': 'CUS002',
        'name': 'Sarah Williams',
        'description': 'Existing customer with booking history for refund scenarios'
    },
    'session_3_complex_queries': {
        'customer_email': 'michael.davies@email.co.uk',
        'customer_id': 'CUS003',
        'name': 'Michael Davies',
        'description': 'Customer for complex multi-part queries'
    },
    'session_4_business_traveler': {
        'customer_email': 'emily.johnson@email.co.uk',
        'customer_id': 'CUS004',
        'name': 'Emily Johnson',
        'description': 'Business traveler with corporate requirements'
    },
    'session_5_customer_issues': {
        'customer_email': 'robert.brown@email.co.uk',
        'customer_id': 'CUS005',
        'name': 'Robert Brown',
        'description': 'Customer with service issues and complaints'
    },
    'session_6_return_customer': {
        'customer_email': 'lisa.wilson@email.co.uk',
        'customer_id': 'CUS006',
        'name': 'Lisa Wilson',
        'description': 'Returning customer with travel history'
    },
    'session_7_price_sensitive': {
        'customer_email': 'david.evans@email.co.uk',
        'customer_id': 'CUS007',
        'name': 'David Evans',
        'description': 'Budget-conscious customer'
    },
    'session_8_accessibility': {
        'customer_email': 'jennifer.smith@email.co.uk',
        'customer_id': 'CUS008',
        'name': 'Jennifer Smith',
        'description': 'Customer requiring accessibility assistance'
    },
    'session_9_international': {
        'customer_email': 'chris.jones@email.co.uk',
        'customer_id': 'CUS009',
        'name': 'Christopher Jones',
        'description': 'International visitor with special requirements'
    },
    'session_10_mixed_complex': {
        'customer_email': 'amanda.taylor@email.co.uk',
        'customer_id': 'CUS010',
        'name': 'Amanda Taylor',
        'description': 'Complex scenario testing all agent capabilities'
    },
    
    # Casual communication sessions (CUS051-CUS055)
    'session_11_casual_student': {
        'customer_email': 'alex.smith@student.ac.uk',
        'customer_id': 'CUS051',
        'name': 'Alex Smith',
        'description': 'Gen Z student with casual communication style'
    },
    'session_12_young_professional': {
        'customer_email': 'jordan.wilson@company.co.uk',
        'customer_id': 'CUS052',
        'name': 'Jordan Wilson',
        'description': 'Millennial professional with efficient communication'
    },
    'session_13_mobile_user': {
        'customer_email': 'casey.brown@email.co.uk',
        'customer_id': 'CUS053',
        'name': 'Casey Brown',
        'description': 'Mobile-first user with abbreviations and casual style'
    },
    'session_14_urgent_travel': {
        'customer_email': 'sam.taylor@emergency.co.uk',
        'customer_id': 'CUS054',
        'name': 'Sam Taylor',
        'description': 'Urgent traveler needing time-critical booking'
    },
    'session_15_social_style': {
        'customer_email': 'riley.jones@student.ac.uk',
        'customer_id': 'CUS055',
        'name': 'Riley Jones',
        'description': 'Social media generation with emoji communication'
    }
}

async def setup_customer_for_session(session_key, current_date=None):
    """
    Setup realistic customer state for a specific test session using actual database data
    
    Args:
        session_key: The session identifier (e.g., 'session_1_new_customer')
        current_date: Current date for database queries (optional, uses centralized config if None)
        
    Returns:
        dict: Complete customer state with user information, bookings, and transactions
    """
    
    if session_key not in CUSTOMER_SCENARIO_MAPPING:
        raise ValueError(f"Unknown session key: {session_key}")
    
    # Use centralized time config if current_date not provided
    if current_date is None:
        current_date = get_system_time_iso()
    
    customer_info = CUSTOMER_SCENARIO_MAPPING[session_key]
    customer_email = customer_info['customer_email']
    
    print(f"🔍 Setting up customer for {session_key}...")
    print(f"📧 Customer: {customer_info['name']} ({customer_email})")
    print(f"🕐 Using time: {current_date}")
    
    try:
        # Connect to database (will use centralized time config internally)
        db = UKConnectDB()
        if not db.connect():
            raise Exception("Cannot connect to database")
        
        try:
            # Get customer information from database
            customer_data = db.find_customer_by_email(customer_email)
            if not customer_data:
                print(f"⚠️  Customer {customer_email} not found in database, using default info")
                customer_data = [{
                    'name': customer_info['name'],
                    'customer_id': customer_info['customer_id'],
                    'email': customer_email,
                    'phone': '+44 20 1234 5678',
                    'address': 'Test Address, London'
                }]
            
            # Get active bookings
            active_bookings = db.find_active_customer_tickets(customer_email) or []
            
            # Get recent transactions
            recent_transactions = db.search_customer_recent_transactions(customer_email) or []
            
            # Get location context from customer address
            location_context = get_customer_location_context(customer_data[0])
            
            # Build comprehensive customer state with location intelligence
            state = {
                "user_email": customer_email,
                "user_information": customer_data[0],
                "active_ticket_reference": active_bookings,
                "history_transaction": recent_transactions[:3],  # Limit to 3 most recent
                "date_time": current_date,
                "location_context": location_context
            }
            
            # Display setup summary
            print(f"✅ Customer setup complete:")
            print(f"   Name: {state['user_information']['name']}")
            print(f"   Customer ID: {state['user_information']['customer_id']}")
            print(f"   Email: {state['user_email']}")
            print(f"   Phone: {state['user_information']['phone']}")
            print(f"   Address: {state['user_information']['address']}")
            print(f"   Active bookings: {len(state['active_ticket_reference'])}")
            print(f"   Recent transactions: {len(state['history_transaction'])}")
            
            # Show location intelligence
            if 'default_departure_station' in location_context:
                print(f"📍 Location Intelligence:")
                print(f"   Default departure: {location_context['default_departure_station']}")
                print(f"   Location city: {location_context['location_city']}")
                print(f"   Travel context: {location_context['travel_context']}")
            elif 'error' in location_context:
                print(f"⚠️  Location Intelligence: {location_context['error']}")
            
            # Show booking details if any
            if state['active_ticket_reference']:
                print(f"\n📋 Active Bookings:")
                for booking in state['active_ticket_reference']:
                    print(f"   • {booking['booking_reference']}: {booking['from_station']} → {booking['to_station']}")
                    print(f"     Date: {booking['departure_time']} | Type: {booking['ticket_type']} | Price: £{booking['paid_price']}")
            
            # Show transaction details if any
            if state['history_transaction']:
                print(f"\n💳 Recent Transactions:")
                for transaction in state['history_transaction']:
                    print(f"   • {transaction['transaction_type']}: £{transaction['amount']} ({transaction['status']})")
                    print(f"     Date: {transaction['transaction_time']} | Method: {transaction['payment_method']}")
            
            return state
            
        finally:
            db.close()
    
    except Exception as e:
        print(f"⚠️  Database setup failed: {e}")
        print("Using fallback customer state...")
        
        # Fallback to basic customer state
        fallback_customer_data = {
            "name": customer_info['name'],
            "customer_id": customer_info['customer_id'],
            "email": customer_email,
            "phone": "+44 20 1234 5678",
            "address": "Test Address, London"
        }
        
        # Get location context even for fallback
        location_context = get_customer_location_context(fallback_customer_data)
        
        return {
            "user_email": customer_email,
            "user_information": fallback_customer_data,
            "active_ticket_reference": [],
            "history_transaction": [],
            "date_time": current_date,
            "location_context": location_context
        }

def get_customer_info_for_session(session_key):
    """
    Get customer information for a specific session
    
    Args:
        session_key: The session identifier
        
    Returns:
        dict: Customer information including email, name, and description
    """
    
    if session_key not in CUSTOMER_SCENARIO_MAPPING:
        return None
    
    return CUSTOMER_SCENARIO_MAPPING[session_key]

def list_all_session_customers():
    """
    List all available session customers
    
    Returns:
        dict: All customer mappings
    """
    
    print("📋 Available Test Session Customers:")
    print("=" * 60)
    
    for session_key, customer_info in CUSTOMER_SCENARIO_MAPPING.items():
        print(f"\n{session_key}:")
        print(f"   Customer: {customer_info['name']} ({customer_info['customer_id']})")
        print(f"   Email: {customer_info['customer_email']}")
        print(f"   Description: {customer_info['description']}")
    
    return CUSTOMER_SCENARIO_MAPPING

if __name__ == "__main__":
    import asyncio
    
    # Test the customer setup
    async def test_customer_setup():
        print("🧪 Testing customer setup for different sessions...")
        
        test_sessions = ['session_1_new_customer', 'session_11_casual_student', 'session_12_young_professional']
        
        for session in test_sessions:
            print(f"\n{'='*60}")
            print(f"Testing {session}")
            print(f"{'='*60}")
            
            try:
                state = await setup_customer_for_session(session)
                print(f"✅ Success: Customer state created for {session}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    asyncio.run(test_customer_setup())