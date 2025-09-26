#!/usr/bin/env python3
"""
UKConnect Customer Support Agent - Test Scenario Runner

This script provides a command-line interface to run test scenarios 
against the master agent without requiring Jupyter notebook.

Usage:
    python run_test_scenarios.py                    # Run a quick demo
    python run_test_scenarios.py --session 1        # Run specific session
    python run_test_scenarios.py --all             # Run all scenarios (takes 10-15 min)
    python run_test_scenarios.py --list            # List available scenarios
"""

import sys
import os
import argparse
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import centralized time configuration
try:
    from config.time_config import get_system_time_iso
except ImportError:
    # Add config to path and try again
    config_path = os.path.join(os.path.dirname(__file__), 'config')
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from time_config import get_system_time_iso

# Terminal colors for better output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    
    # Combined styles
    GREEN_BOLD = '\033[32m\033[1m'
    BLUE_BOLD = '\033[34m\033[1m'
    YELLOW_BOLD = '\033[33m\033[1m'
    RED_BOLD = '\033[31m\033[1m'
    CYAN_BOLD = '\033[36m\033[1m'

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from agent import get_master_agent
    from test_message_scenarios import get_all_sessions, get_session_messages, print_session_summary
    from google.adk.sessions import InMemorySessionService
    from google.adk import Runner
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Agent name mapping for better display
AGENT_MAPPING = {
    'ukconnect_support_agent': 'Policy Agent',
    'ticket_operations_agent': 'Ticket Agent', 
    'master_agent': 'Master Agent'
}

def clean_template_variables(response_text, session):
    """
    Clean up template variables in agent responses with actual customer data.
    
    Args:
        response_text (str): The agent response text
        session: The session object containing customer state
        
    Returns:
        str: Cleaned response text with template variables replaced
    """
    if not response_text:
        return response_text
    
    try:
        # Get customer information from session state
        user_info = session.state.get('user_information', {})
        customer_name = user_info.get('name', 'Customer')
        customer_id = user_info.get('customer_id', 'N/A')
        
        # Get location context from session state
        location_context = session.state.get('location_context', {})
        
        # Replace user information template variables
        cleaned_response = response_text.replace(
            '{user_information[name]}', customer_name
        ).replace(
            '{user_information[customer_id]}', customer_id
        ).replace(
            '{user_information[email]}', session.user_id
        )
        
        # Replace location context template variables
        if location_context:
            cleaned_response = cleaned_response.replace(
                '{location_context[default_departure_station]}', 
                location_context.get('default_departure_station', 'your local station')
            ).replace(
                '{location_context[location_city]}', 
                location_context.get('location_city', 'your area')
            ).replace(
                '{location_context[location_area]}', 
                location_context.get('location_area', 'your area')
            ).replace(
                '{location_context[travel_context]}', 
                location_context.get('travel_context', 'your travel needs')
            ).replace(
                '{location_context[location_assumption]}', 
                location_context.get('location_assumption', 'based on your location')
            )
        
        return cleaned_response
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Template cleanup failed: {e}{Colors.RESET}")
        return response_text

async def setup_realistic_customer_state(session_key=None):
    """
    Setup realistic customer state with real database data for specific test sessions
    
    Args:
        session_key: The test session identifier (e.g., 'session_1_new_customer')
        
    Returns:
        dict: Customer state with user information, bookings, and transactions
    """
    try:
        # Import the customer setup utility
        import importlib.util
        customer_setup_path = os.path.join(os.path.dirname(__file__), 'utils', 'customer_setup.py')
        spec = importlib.util.spec_from_file_location("customer_setup", customer_setup_path)
        customer_setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(customer_setup)
        
        if session_key:
            # Use specific customer for the session - use centralized time config
            state = await customer_setup.setup_customer_for_session(session_key)
        else:
            # Fallback to first customer (James Thompson) - use centralized time config
            state = await customer_setup.setup_customer_for_session('session_1_new_customer')
            
        # Display customer information with colors
        print(f"✅ Customer loaded: {Colors.GREEN_BOLD}{state['user_information']['name']}{Colors.RESET}")
        print(f"📧 Email: {state['user_email']}")
        print(f"🆔 Customer ID: {state['user_information']['customer_id']}")
        print(f"🕐 Current time: {state['date_time']}")
        print(f"🎫 Active tickets: {len(state['active_ticket_reference'])}")
        print(f"💳 Recent transactions: {len(state['history_transaction'])}")
        
        # Show active bookings details if any
        if state['active_ticket_reference']:
            print(f"\n📋 Active Bookings:")
            for booking in state['active_ticket_reference']:
                print(f"  • {Colors.CYAN}{booking['booking_reference']}{Colors.RESET}: {booking['from_station']} → {booking['to_station']}")
                print(f"    Date: {booking['departure_time']} | Type: {booking['ticket_type']} | Price: £{booking['paid_price']}")
        
        return state
        
    except Exception as e:
        print(f"⚠️  Customer setup failed: {e}")
        print("Using basic fallback customer state...")
        
        # Fallback to basic customer state
        return {
            "user_email": "james.thompson@email.co.uk",
            "user_information": {
                "name": "James Thompson", 
                "customer_id": "CUS001",
                "email": "james.thompson@email.co.uk",
                "phone": "+44 20 7946 0101",
                "address": "42 Baker Street, London W1U 6TQ"
            },
            "active_ticket_reference": [],
            "history_transaction": [],
            "date_time": "Tuesday 2025-09-16 14:00 GMT"
        }

async def initialize_agent():
    """Initialize the master agent and runner with a test session."""
    print("🚀 Initializing master agent...")
    
    try:
        master_agent = get_master_agent()
        session_service = InMemorySessionService()
        runner = Runner(
            agent=master_agent, 
            session_service=session_service,
            app_name="ukconnect_test_scenarios"
        )
        
        print("✅ Master agent initialized successfully!")
        print(f"   Agent Name: {master_agent.name}")
        print(f"   Model: {master_agent.model}")
        
        # Create a placeholder session - actual customer setup will happen in run_session()
        session = await session_service.create_session(
            app_name="ukconnect_test_scenarios",
            user_id="placeholder@ukconnect.com",  # Will be updated in run_session
            state={}  # Will be populated in run_session
        )
        
        print(f"✅ Test session created: {session.id}")
        print("🔧 Customer setup will be handled by individual test sessions")
        
        return runner, session
    except Exception as e:
        print(f"❌ Failed to initialize master agent: {e}")
        sys.exit(1)

def process_and_display_events(events, show_detailed=True):
    """
    Process and display agent events with proper formatting.
    
    Args:
        events: List of agent events from the runner
        show_detailed: Whether to show detailed event information
    """
    if not show_detailed:
        # Simple mode - just show final response
        for event in reversed(events):
            if hasattr(event, 'content') and event.content:
                print(f"🤖 RESPONSE: {event.content}")
                return
        print("🤖 RESPONSE: No response generated")
        return
    
    print("\\n" + "="*80)
    print("🤖 AGENT RESPONSE ANALYSIS")
    print("="*80)
    
    agent_activities = {}
    final_response = None
    
    for event in events:
        event_type = event.__class__.__name__
        
        # Extract agent information from event
        agent_name = 'unknown'
        if hasattr(event, 'agent_id'):
            agent_name = event.agent_id
        elif hasattr(event, 'source') and hasattr(event.source, 'agent_id'):
            agent_name = event.source.agent_id
        
        # Map to friendly name
        display_name = AGENT_MAPPING.get(agent_name, agent_name)
        
        if display_name not in agent_activities:
            agent_activities[display_name] = []
        
        # Handle different event types
        if event_type == 'AgentEvent':
            if hasattr(event, 'content') and event.content:
                agent_activities[display_name].append(f"Message: {event.content}")
                final_response = event.content
        
        elif event_type == 'ToolCallEvent':
            tool_name = getattr(event, 'tool_name', 'unknown_tool')
            agent_activities[display_name].append(f"🔧 Used tool: {tool_name}")
        
        elif event_type == 'ToolResponseEvent':
            tool_name = getattr(event, 'tool_name', 'unknown_tool')
            if hasattr(event, 'response') and event.response:
                response_preview = str(event.response)[:100] + "..." if len(str(event.response)) > 100 else str(event.response)
                agent_activities[display_name].append(f"📤 Tool response: {response_preview}")
        
        elif event_type == 'SubAgentRequestEvent':
            if hasattr(event, 'agent_id') and hasattr(event, 'request'):
                target_agent = AGENT_MAPPING.get(event.agent_id, event.agent_id)
                request_preview = event.request[:80] + "..." if len(event.request) > 80 else event.request
                agent_activities[display_name].append(f"🔀 Delegated to {target_agent}: {request_preview}")
        
        elif event_type == 'SubAgentResponseEvent':
            if hasattr(event, 'agent_id') and hasattr(event, 'response'):
                source_agent = AGENT_MAPPING.get(event.agent_id, event.agent_id)
                response_preview = event.response[:80] + "..." if len(event.response) > 80 else event.response
                agent_activities[display_name].append(f"📨 Response from {source_agent}: {response_preview}")
    
    # Display agent activities
    for agent, activities in agent_activities.items():
        if activities:
            print(f"\\n🤖 {agent}:")
            for activity in activities:
                print(f"   • {activity}")
    
    # Display final response
    if final_response:
        print(f"\\n" + "="*80)
        print("💬 FINAL RESPONSE TO USER:")
        print("="*80)
        print(final_response)
    
    print("\\n" + "="*80)

async def run_single_message(runner, session, message, show_detailed=True):
    """
    Run a single message through the master agent.
    
    Args:
        runner: The initialized agent runner
        session: The session object
        message (str): User message to process
        show_detailed (bool): Whether to show detailed analysis
    
    Returns:
        str: Agent response
    """
    # Display user message in green bold only when show_detailed=False
    if not show_detailed:
        print(f"\n{Colors.GREEN_BOLD}🗣️  USER: {message}{Colors.RESET}")
        # Add 3 second delay to prevent agent hallucination
        time.sleep(3)
    
    try:
        # Import required types for message creation
        from google.genai.types import Content, Part
        
        # Import event logger directly with absolute path
        import importlib.util
        event_logger_path = os.path.join(os.path.dirname(__file__), 'utils', 'event_logger.py')
        spec = importlib.util.spec_from_file_location("event_logger", event_logger_path)
        event_logger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(event_logger)
        process_and_display_events = event_logger.process_and_display_events
        
        # Create message content
        content = Content(role='user', parts=[Part(text=message)])
        
        # Run the agent using run_async (as shown in the notebook)
        events = runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        )
        
        if show_detailed:
            # Use the detailed event logger
            await process_and_display_events(events, message)
            
            # We need to run the events again to get the final response since the logger consumes them
            events_for_response = runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            )
            
            final_response = "No response generated"
            async for event in events_for_response:
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                        final_response = event.content.parts[0].text
                        break
        else:
            # Simple mode - just get the response
            final_response = "No response generated"
            async for event in events:
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                        final_response = event.content.parts[0].text
                        break
            
            print(f"{Colors.GREEN_BOLD}🤖 RESPONSE: {final_response}{Colors.RESET}")
        
        # Clean up template variables that weren't replaced
        final_response = clean_template_variables(final_response, session)
        
        return final_response
    
    except Exception as e:
        print(f"{Colors.RED_BOLD}❌ Error processing message: {e}{Colors.RESET}")
        # Try a basic approach as fallback
        try:
            print(f"{Colors.YELLOW}🔄 Attempting basic message processing...{Colors.RESET}")
            response = f"Received message: {message}"
            print(f"{Colors.GREEN_BOLD}🤖 BASIC RESPONSE: {response}{Colors.RESET}")
            return response
        except Exception as e2:
            print(f"{Colors.RED_BOLD}❌ Basic processing also failed: {e2}{Colors.RESET}")
            return f"Error: {e}"

async def run_session(runner, session, session_key, show_detailed=True):
    """Run a specific test session with proper customer setup."""
    all_sessions = get_all_sessions()
    
    if session_key not in all_sessions:
        print(f"❌ Session '{session_key}' not found!")
        print("Available sessions:")
        for key in all_sessions.keys():
            print(f"  - {key}")
        return False
    
    session_data = all_sessions[session_key]
    messages = session_data['messages']
    
    # Setup the correct customer for this session
    print(f"{Colors.BLUE}🔍 Setting up customer for {session_key}...{Colors.RESET}")
    try:
        customer_state = await setup_realistic_customer_state(session_key)
        
        # Create a new session with the correct customer for this specific test
        session_service = runner.session_service
        new_session = await session_service.create_session(
            app_name="ukconnect_test_scenarios",
            user_id=customer_state["user_email"],
            state=customer_state
        )
        
        print(f"{Colors.GREEN}✅ Customer setup complete for {customer_state['user_information']['name']}{Colors.RESET}")
        
        # Use the new session for this test
        session = new_session
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Using existing session customer due to setup error: {e}{Colors.RESET}")
    
    print(f"{Colors.CYAN_BOLD}🚀 Starting {session_data['title']}{Colors.RESET}")
    print(f"{Colors.BLUE}📝 Total messages: {len(messages)}{Colors.RESET}")
    print(f"{Colors.BLUE}🎭 Expected Agents: {', '.join(session_data['expected_agents'])}{Colors.RESET}")
    print(f"{Colors.BLUE}⚡ Key Functionality: {', '.join(session_data['key_functionality'])}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 100}{Colors.RESET}")
    
    start_time = time.time()
    
    # Run through all messages in the session
    for i, message in enumerate(messages, 1):
        print(f"\n\n{Colors.YELLOW_BOLD}🔄 MESSAGE {i}/{len(messages)}{Colors.RESET}")
        response = await run_single_message(runner, session, message, show_detailed)
        
        # Small delay to make it easier to follow
        if show_detailed:
            time.sleep(1)
        else:
            time.sleep(0.5)
    
    end_time = time.time()
    print(f"\n{Colors.GREEN_BOLD}✅ Session completed in {end_time - start_time:.1f} seconds!{Colors.RESET}")
    return True

async def run_all_sessions(runner, session, show_detailed=False):
    """Run all test sessions."""
    print("🚀 Starting FULL TEST SUITE")
    print("⚠️  This will test all 10 scenarios and may take 10-15 minutes...")
    print("=" * 100)
    
    all_sessions = get_all_sessions()
    total_sessions = len(all_sessions)
    total_messages = sum(len(session['messages']) for session in all_sessions.values())
    
    print(f"📊 Test Suite Overview:")
    print(f"   • Total sessions: {total_sessions}")
    print(f"   • Total messages: {total_messages}")
    print(f"   • Estimated time: {total_messages * 3} seconds\\n")
    
    start_time = time.time()
    successful_sessions = 0
    
    # Run each session
    for session_num, (session_key, session_data) in enumerate(all_sessions.items(), 1):
        print(f"\\n\\n{'='*100}")
        print(f"🎯 SESSION {session_num}/{total_sessions}: {session_data['title']}")
        print(f"📝 Messages: {len(session_data['messages'])}")
        print("="*100)
        
        try:
            success = await run_session(runner, session, session_key, show_detailed)
            if success:
                successful_sessions += 1
        except Exception as e:
            print(f"❌ Session {session_num} failed: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\\n\\n{'='*100}")
    print("🎉 FULL TEST SUITE COMPLETED!")
    print(f"✅ Successful sessions: {successful_sessions}/{total_sessions}")
    print(f"⏱️  Total execution time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"📊 Messages processed: {total_messages}")
    print(f"📈 Average time per message: {total_time/total_messages:.1f} seconds")
    print("="*100)

async def run_quick_demo(runner, session):
    """Run a quick demo with a few messages."""
    demo_messages = [
        "Hi, can you help me find trains from London to Manchester tomorrow morning?",
        "What's the difference between Standard and Flexible fares?",
        "Can you book me ticket ID 2? My email is demo.user@email.co.uk"
    ]
    
    print(f"{Colors.CYAN_BOLD}🚀 Running Quick Demo{Colors.RESET}")
    print(f"{Colors.BLUE}📝 Testing {len(demo_messages)} messages{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n\n{Colors.YELLOW_BOLD}🔄 DEMO MESSAGE {i}/{len(demo_messages)}{Colors.RESET}")
        response = await run_single_message(runner, session, message, show_detailed=True)
        time.sleep(1)
    
    print(f"\n{Colors.GREEN_BOLD}✅ Quick demo completed!{Colors.RESET}")

async def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="UKConnect Customer Support Agent Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_test_scenarios.py                    # Run quick demo
    python run_test_scenarios.py --session 1        # Run session 1
    python run_test_scenarios.py --session session_1_new_customer  # Run by name
    python run_test_scenarios.py --all             # Run all scenarios
    python run_test_scenarios.py --list            # List available scenarios
    python run_test_scenarios.py --quick           # Quick demo (same as no args)
        """
    )
    
    parser.add_argument('--session', '-s', 
                       help='Run specific session (by number 1-10 or by name)')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Run all test scenarios (takes 10-15 minutes)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all available test scenarios')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick demo (default if no args)')
    parser.add_argument('--simple', action='store_true',
                       help='Simple output mode (less detailed)')
    
    args = parser.parse_args()
    
    # List scenarios
    if args.list:
        print_session_summary()
        return
    
    # Initialize the agent
    runner, session = await initialize_agent()
    
    # Determine detailed output mode
    show_detailed = not args.simple
    
    # Run specific session
    if args.session:
        session_key = args.session
        
        # Handle numeric session references (1-10)
        if session_key.isdigit():
            session_num = int(session_key)
            all_sessions = list(get_all_sessions().keys())
            if 1 <= session_num <= len(all_sessions):
                session_key = all_sessions[session_num - 1]
            else:
                print(f"❌ Session number must be between 1 and {len(all_sessions)}")
                return
        
        await run_session(runner, session, session_key, show_detailed)
    
    # Run all scenarios
    elif args.all:
        await run_all_sessions(runner, session, show_detailed)
    
    # Run quick demo (default)
    else:
        await run_quick_demo(runner, session)

if __name__ == "__main__":
    print("🎯 UKConnect Customer Support Agent Test Runner")
    print("=" * 60)
    print(f"📅 Started at: {get_system_time_iso()}")
    print("=" * 60)
    
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n\\n⏹️  Test execution interrupted by user.")
    except Exception as e:
        print(f"\\n\\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    print(f"\\n📅 Completed at: {get_system_time_iso()}")
    print("🎯 Thank you for testing the UKConnect Customer Support Agent!")