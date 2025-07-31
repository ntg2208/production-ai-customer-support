#!/usr/bin/env python3
"""
UKConnect Customer Support Agent - Interactive Terminal Test

This script provides an interactive terminal interface where you can:
1. Choose from existing customer emails 
2. Setup a session with that customer's data
3. Manually enter messages one by one to test the agent

Usage:
    python interactive_test.py

Features:
- Select from real customer accounts with location intelligence
- Interactive message input with history
- Detailed agent response analysis
- Customer context display
- Clean exit with quit/exit commands
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
    WHITE = '\033[37m'
    
    # Combined styles
    GREEN_BOLD = '\033[32m\033[1m'
    BLUE_BOLD = '\033[34m\033[1m'
    YELLOW_BOLD = '\033[33m\033[1m'
    RED_BOLD = '\033[31m\033[1m'
    CYAN_BOLD = '\033[36m\033[1m'
    WHITE_BOLD = '\033[37m\033[1m'

try:
    from agent import get_master_agent
    from utils import customer_setup
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the customer_support_agent directory")
    print("and all dependencies are installed (pip install google-generativeai python-dotenv)")
    sys.exit(1)

# Customer options with descriptions
CUSTOMER_OPTIONS = {
    '1': {
        'key': 'session_1_new_customer',
        'name': 'James Thompson',
        'email': 'james.thompson@email.co.uk',
        'id': 'CUS001',
        'location': 'London (Euston)',
        'description': 'New customer, business traveler'
    },
    '2': {
        'key': 'session_2_refund_rebooking', 
        'name': 'Sarah Williams',
        'email': 'sarah.williams@email.co.uk',
        'id': 'CUS002',
        'location': 'Manchester (Piccadilly)',
        'description': 'Existing customer with booking history'
    },
    '3': {
        'key': 'session_3_complex_queries',
        'name': 'Michael Davies', 
        'email': 'michael.davies@email.co.uk',
        'id': 'CUS003',
        'location': 'Birmingham (New Street)',
        'description': 'Complex multi-part queries'
    },
    '4': {
        'key': 'session_4_business_traveler',
        'name': 'Emily Johnson',
        'email': 'emily.johnson@email.co.uk', 
        'id': 'CUS004',
        'location': 'Edinburgh (Waverley)',
        'description': 'Corporate business traveler'
    },
    '5': {
        'key': 'session_5_customer_issues',
        'name': 'Robert Brown',
        'email': 'robert.brown@email.co.uk',
        'id': 'CUS005', 
        'location': 'Glasgow (Central)',
        'description': 'Customer with service issues'
    },
    '6': {
        'key': 'session_6_return_customer',
        'name': 'Lisa Wilson',
        'email': 'lisa.wilson@email.co.uk',
        'id': 'CUS006',
        'location': 'Leeds (Station)',
        'description': 'Frequent traveler, loyalty customer'
    },
    '7': {
        'key': 'session_7_price_sensitive',
        'name': 'David Evans',
        'email': 'david.evans@email.co.uk',
        'id': 'CUS007',
        'location': 'Bristol (Temple Meads)',
        'description': 'Budget-conscious customer'
    },
    '8': {
        'key': 'session_8_accessibility',
        'name': 'Jennifer Smith',
        'email': 'jennifer.smith@email.co.uk',
        'id': 'CUS008',
        'location': 'Liverpool (Lime Street)',
        'description': 'Accessibility and special needs'
    },
    '9': {
        'key': 'session_9_international',
        'name': 'Christopher Jones',
        'email': 'chris.jones@email.co.uk',
        'id': 'CUS009',
        'location': 'Oxford (Station)',
        'description': 'International visitor'
    },
    '10': {
        'key': 'session_10_mixed_complex',
        'name': 'Amanda Taylor',
        'email': 'amanda.taylor@email.co.uk',
        'id': 'CUS010',
        'location': 'Cambridge (Station)',
        'description': 'Complex mixed scenarios'
    },
    '11': {
        'key': 'session_11_casual_student',
        'name': 'Alex Smith',
        'email': 'alex.smith@student.ac.uk',
        'id': 'CUS051',
        'location': 'London (Euston)',
        'description': 'Casual Gen Z student'
    },
    '12': {
        'key': 'session_12_mobile_first',
        'name': 'Jordan Wilson',
        'email': 'jordan.wilson@company.co.uk',
        'id': 'CUS052',
        'location': 'London (King\'s Cross)',
        'description': 'Mobile-first user'
    }
}

def print_banner():
    """Print the application banner"""
    print(f"\n{Colors.CYAN_BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN_BOLD}🚂 UKConnect Customer Support Agent - Interactive Test{Colors.RESET}")
    print(f"{Colors.CYAN_BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.WHITE}Test the multi-agent system with real customer data and manual input{Colors.RESET}")
    print(f"{Colors.WHITE}Choose a customer, then enter messages one by one to see agent responses{Colors.RESET}")
    print(f"{Colors.CYAN_BOLD}{'='*70}{Colors.RESET}\n")

def display_customer_options():
    """Display available customer options"""
    print(f"{Colors.YELLOW_BOLD}📋 Available Customer Accounts:{Colors.RESET}\n")
    
    for option_id, customer in CUSTOMER_OPTIONS.items():
        print(f"{Colors.GREEN}{option_id:2}.{Colors.RESET} {Colors.WHITE_BOLD}{customer['name']}{Colors.RESET}")
        print(f"    {Colors.CYAN}Email:{Colors.RESET} {customer['email']}")
        print(f"    {Colors.CYAN}ID:{Colors.RESET} {customer['id']} | {Colors.CYAN}Location:{Colors.RESET} {customer['location']}")
        print(f"    {Colors.YELLOW}Description:{Colors.RESET} {customer['description']}")
        print()

def get_customer_choice():
    """Get customer selection from user"""
    while True:
        choice = input(f"{Colors.BLUE_BOLD}Choose a customer (1-12):{Colors.RESET} ").strip()
        
        if choice in CUSTOMER_OPTIONS:
            return CUSTOMER_OPTIONS[choice]
        
        if choice.lower() in ['quit', 'exit', 'q']:
            print(f"{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
            sys.exit(0)
        
        print(f"{Colors.RED}❌ Invalid choice. Please enter a number 1-12{Colors.RESET}")

def display_customer_context(customer_state):
    """Display loaded customer context"""
    user_info = customer_state['user_information']
    
    print(f"\n{Colors.GREEN_BOLD}✅ Customer Session Loaded:{Colors.RESET}")
    print(f"{Colors.CYAN}Name:{Colors.RESET} {user_info['name']}")
    print(f"{Colors.CYAN}Email:{Colors.RESET} {customer_state['user_email']}")  
    print(f"{Colors.CYAN}Customer ID:{Colors.RESET} {user_info['customer_id']}")
    print(f"{Colors.CYAN}Address:{Colors.RESET} {user_info['address']}")
    print(f"{Colors.CYAN}Phone:{Colors.RESET} {user_info['phone']}")
    
    # Display location context if available
    if 'location_context' in customer_state:
        loc_ctx = customer_state['location_context']
        print(f"{Colors.CYAN}Default Station:{Colors.RESET} {loc_ctx.get('default_departure_station', 'N/A')}")
    
    # Display active bookings
    active_bookings = customer_state.get('active_ticket_reference', [])
    print(f"\n{Colors.YELLOW}🎫 Active Bookings:{Colors.RESET} {len(active_bookings)}")
    for booking in active_bookings:
        print(f"  • {booking['booking_reference']}: {booking['from_station']} → {booking['to_station']}")
        print(f"    {booking['departure_time']} | {booking['ticket_type']} | £{booking['paid_price']}")
    
    # Display recent transactions  
    transactions = customer_state.get('history_transaction', [])
    print(f"\n{Colors.YELLOW}💳 Recent Transactions:{Colors.RESET} {len(transactions)}")
    for transaction in transactions[:3]:  # Show only first 3
        print(f"  • {transaction['booking_reference']}: £{transaction['amount']} via {transaction['payment_method']}")
        print(f"    {transaction['transaction_time']}")

async def process_and_display_response(events):
    """Process and display agent response events"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE_BOLD}🤖 Agent Response Analysis{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    agent_activities = {}
    final_response = None
    
    # Agent name mapping
    AGENT_MAPPING = {
        'ukconnect_support_agent': 'Policy Agent',
        'ticket_operations_agent': 'Ticket Agent',
        'master_agent': 'Master Agent'
    }
    
    async for event in events:
        # Extract agent information
        agent_name = getattr(event, 'author', None)
        if not agent_name:
            agent_name = getattr(event, 'agent_name', 'unknown')
        
        display_name = AGENT_MAPPING.get(agent_name, agent_name)
        
        if display_name not in agent_activities:
            agent_activities[display_name] = []
        
        # Check for tool calls
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_info = f"🔧 Used tool: {call.name}"
                if call.args:
                    if 'query' in call.args:
                        tool_info += f" (query: {call.args['query'][:50]}...)"
                    elif 'from_station' in call.args or 'to_station' in call.args:
                        tool_info += f" (route: {call.args.get('from_station', 'N/A')} → {call.args.get('to_station', 'N/A')})"
                agent_activities[display_name].append(tool_info)
        
        # Check for tool responses
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                result_preview = str(response.response)[:100] + "..." if len(str(response.response)) > 100 else str(response.response)
                agent_activities[display_name].append(f"📤 Tool result: {result_preview}")
        
        # Check for final response
        if event.is_final_response():
            final_response = event.content.parts[0].text
    
    # Display agent activities
    for agent, activities in agent_activities.items():
        if activities:
            print(f"\n{Colors.MAGENTA}🤖 {agent}:{Colors.RESET}")
            for activity in activities:
                print(f"   • {activity}")
    
    # Display final response
    if final_response:
        print(f"\n{Colors.WHITE_BOLD}{'─'*60}{Colors.RESET}")
        print(f"{Colors.WHITE_BOLD}💬 Agent Response:{Colors.RESET}")
        print(f"{Colors.WHITE_BOLD}{'─'*60}{Colors.RESET}")
        print(f"{Colors.WHITE}{final_response}{Colors.RESET}")
        print(f"{Colors.WHITE_BOLD}{'─'*60}{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ No response generated{Colors.RESET}")

def print_help():
    """Print help information"""
    print(f"\n{Colors.YELLOW_BOLD}💡 Available Commands:{Colors.RESET}")
    print(f"{Colors.CYAN}• Enter any message{Colors.RESET} - Send message to agent")
    print(f"{Colors.CYAN}• /help{Colors.RESET} - Show this help")
    print(f"{Colors.CYAN}• /customer{Colors.RESET} - Show current customer info")
    print(f"{Colors.CYAN}• /clear{Colors.RESET} - Clear screen")
    print(f"{Colors.CYAN}• quit/exit{Colors.RESET} - Exit the program")
    print()

async def interactive_session(runner, session, customer_state):
    """Main interactive session loop"""
    message_count = 0
    
    print(f"\n{Colors.GREEN_BOLD}🚀 Interactive Session Started!{Colors.RESET}")
    print(f"{Colors.WHITE}You can now enter messages to test the agent.{Colors.RESET}")
    print_help()
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Colors.GREEN_BOLD}You:{Colors.RESET} ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"{Colors.YELLOW}👋 Thanks for testing UKConnect! Goodbye!{Colors.RESET}")
                break
            
            if user_input.lower() == '/help':
                print_help()
                continue
            
            if user_input.lower() == '/customer':
                display_customer_context(customer_state)
                continue
            
            if user_input.lower() == '/clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                print(f"{Colors.GREEN}Customer: {customer_state['user_information']['name']}{Colors.RESET}")
                continue
            
            if not user_input:
                print(f"{Colors.YELLOW}Please enter a message or 'quit' to exit{Colors.RESET}")
                continue
            
            message_count += 1
            print(f"\n{Colors.BLUE}🔄 Processing message {message_count}...{Colors.RESET}")
            
            # Create message content
            content = Content(role='user', parts=[Part(text=user_input)])
            
            # Run the agent
            events = runner.run_async(
                user_id=customer_state["user_email"],
                session_id=session.id,
                new_message=content
            )
            
            # Process and display response
            await process_and_display_response(events)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Session interrupted. Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error processing message: {e}{Colors.RESET}")
            continue

async def main():
    """Main application function"""
    # Print banner
    print_banner()
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print(f"{Colors.RED}❌ GOOGLE_API_KEY not found in environment{Colors.RESET}")
        print(f"{Colors.YELLOW}Please set your Google API key in .env file{Colors.RESET}")
        sys.exit(1)
    
    try:
        # Display customer options
        display_customer_options()
        
        # Get customer choice
        selected_customer = get_customer_choice()
        
        print(f"\n{Colors.BLUE}🔧 Setting up session for {selected_customer['name']}...{Colors.RESET}")
        
        # Initialize master agent
        print(f"{Colors.BLUE}📦 Initializing master agent with sub-agents...{Colors.RESET}")
        master_agent = get_master_agent()
        print(f"{Colors.GREEN}✅ Master agent ready with {len(master_agent.sub_agents)} sub-agents{Colors.RESET}")
        
        # Setup customer state
        print(f"{Colors.BLUE}👤 Loading customer data...{Colors.RESET}")
        customer_state = await customer_setup.setup_customer_for_session(selected_customer['key'])
        
        # Display customer context
        display_customer_context(customer_state)
        
        # Create session service and runner
        print(f"\n{Colors.BLUE}🔧 Creating session and runner...{Colors.RESET}")
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="interactive_test",
            user_id=customer_state["user_email"],
            state=customer_state
        )
        
        runner = Runner(
            agent=master_agent,
            app_name="interactive_test", 
            session_service=session_service
        )
        
        # Start interactive session
        await interactive_session(runner, session, customer_state)
        
    except Exception as e:
        print(f"{Colors.RED}❌ Setup error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the interactive session
    asyncio.run(main())