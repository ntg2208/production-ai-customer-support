#!/usr/bin/env python3
"""
Event Logger Utility for UKConnect Customer Support Agent
Provides comprehensive logging and display of agent events and interactions
"""

import warnings
warnings.filterwarnings('ignore')

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

async def process_and_display_events(events, query):
    """
    Process agent events and display results nicely for sub-agent architecture
    
    Args:
        events: Async generator of agent events
        query: The original user query
    """
    print(f"\n{'='*70}")
    print(f"🔍 {Colors.GREEN_BOLD}User Query: {query}{Colors.RESET}")
    print(f"{'='*70}")
    
    sub_agent_delegations = []
    tool_calls_made = []
    master_handled_directly = True
    
    # Known agent names and their types
    AGENT_MAPPING = {
        'ukconnect_support_agent': 'Policy Agent',
        'ticket_operations_agent': 'Ticket Agent',
        'master_agent': 'Master Agent'
    }
    
    def identify_agent_type(agent_name):
        """Identify agent type based on exact agent name"""
        if not agent_name:
            return "Unknown Agent"
        return AGENT_MAPPING.get(agent_name, f"Unknown Agent ({agent_name})")
    
    async for event in events:
        # Get the agent name from the event
        event_agent = getattr(event, 'author', None) or getattr(event, 'agent_name', None)
        
        # Check if this is a sub-agent delegation
        if event_agent and event_agent != 'master_agent':
            master_handled_directly = False
            agent_type = identify_agent_type(event_agent)
            
            sub_agent_info = {
                'agent_name': event_agent,
                'agent_type': agent_type
            }
            
            # Only add if not already tracked
            if sub_agent_info not in sub_agent_delegations:
                sub_agent_delegations.append(sub_agent_info)
                print(f"\n🔄 SUB-AGENT DELEGATION:")
                print(f"   Delegated to: {agent_type} ({event_agent})")
        
        # Show tool calls
        calls = event.get_function_calls()
        if calls:
            master_handled_directly = False
            for call in calls:
                agent_type = identify_agent_type(event_agent)
                
                tool_info = {
                    'tool_name': call.name,
                    'agent': event_agent or 'unknown',
                    'agent_type': agent_type,
                    'args': call.args
                }
                tool_calls_made.append(tool_info)
                
                print(f"\n🛠️ TOOL CALL:")
                print(f"   Agent: {agent_type}")
                print(f"   Tool: {call.name}")
                
                # Show relevant arguments
                if call.args:
                    if 'query' in call.args:
                        print(f"   Query: {call.args['query']}")
                    if 'from_station' in call.args or 'to_station' in call.args:
                        print(f"   Route: {call.args.get('from_station', 'N/A')} → {call.args.get('to_station', 'N/A')}")
                    if 'from_location' in call.args or 'to_location' in call.args:
                        print(f"   Route: {call.args.get('from_location', 'N/A')} → {call.args.get('to_location', 'N/A')}")
                    if 'booking_reference' in call.args:
                        print(f"   Booking: {call.args['booking_reference']}")
                    if 'limit' in call.args:
                        print(f"   Limit: {call.args['limit']}")
        
        # Show tool responses
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                result_preview = str(response.response)[:200] + "..." if len(str(response.response)) > 200 else str(response.response)
                
                # Determine result type based on tool name
                if response.name == 'search_policy_knowledge':
                    print(f"\n✅ POLICY SEARCH RESULT:")
                    print(f"   Found relevant policy information")
                elif 'search' in response.name.lower() and 'route' in response.name.lower():
                    print(f"\n✅ TICKET SEARCH RESULT:")
                    if isinstance(response.response, dict) and 'tickets' in response.response:
                        ticket_count = len(response.response['tickets'])
                        print(f"   Found {ticket_count} available tickets")
                    elif isinstance(response.response, dict) and 'total_tickets' in response.response:
                        ticket_count = response.response['total_tickets']
                        print(f"   Found {ticket_count} available tickets")
                    else:
                        print(f"   {result_preview}")
                elif 'booking' in response.name.lower():
                    print(f"\n✅ BOOKING OPERATION RESULT:")
                    print(f"   {result_preview}")
                elif 'refund' in response.name.lower():
                    print(f"\n✅ REFUND CALCULATION RESULT:")
                    if isinstance(response.response, dict) and 'refund_amount' in response.response:
                        amount = response.response['refund_amount']
                        print(f"   Refund amount: £{amount}")
                    else:
                        print(f"   {result_preview}")
                elif response.name == 'transfer_to_agent':
                    print(f"\n✅ DELEGATION RESULT:")
                    print(f"   Transferred to specialist agent")
                else:
                    print(f"\n✅ TOOL RESULT ({response.name}):")
                    print(f"   {result_preview}")
        
        # Show final response
        if event.is_final_response():
            final_response = event.content.parts[0].text
            
            # Determine who gave the final response
            responder_type = identify_agent_type(event_agent) if event_agent else "Master Agent"
            
            print(f"\n🤖 {responder_type.upper()} RESPONSE:")
            print(f"{'─'*50}")
            print(f"{Colors.GREEN_BOLD}{final_response}{Colors.RESET}")
            print(f"{'─'*50}")
    
    # Summary
    print(f"\n📊 INTERACTION SUMMARY:")
    if sub_agent_delegations:
        print(f"   Sub-agents involved: {len(sub_agent_delegations)}")
        for i, delegation in enumerate(sub_agent_delegations, 1):
            print(f"   {i}. {delegation['agent_type']} ({delegation['agent_name']})")
    
    if tool_calls_made:
        print(f"   Tools used: {len(tool_calls_made)}")
        for tool in tool_calls_made:
            print(f"   - {tool['tool_name']} (by {tool['agent_type']})")
    
    if master_handled_directly and not sub_agent_delegations and not tool_calls_made:
        print(f"   Master agent handled query directly without delegation")
    
    print(f"\n{'='*70}")


def process_and_display_events_simple(events, query):
    """
    Simple synchronous version for basic logging (non-async contexts)
    
    Args:
        events: List of agent events
        query: The original user query
    """
    print(f"\n{'='*70}")
    print(f"🔍 {Colors.GREEN_BOLD}User Query: {query}{Colors.RESET}")
    print(f"{'='*70}")
    
    # Known agent names and their types
    AGENT_MAPPING = {
        'ukconnect_support_agent': 'Policy Agent',
        'ticket_operations_agent': 'Ticket Agent',
        'master_agent': 'Master Agent'
    }
    
    def identify_agent_type(agent_name):
        """Identify agent type based on exact agent name"""
        if not agent_name:
            return "Unknown Agent"
        return AGENT_MAPPING.get(agent_name, f"Unknown Agent ({agent_name})")
    
    sub_agent_delegations = []
    tool_calls_made = []
    final_response = None
    
    for event in events:
        # Get the agent name from the event
        event_agent = getattr(event, 'author', None) or getattr(event, 'agent_name', None)
        
        # Check for tool calls
        if hasattr(event, 'get_function_calls'):
            calls = event.get_function_calls()
            if calls:
                for call in calls:
                    agent_type = identify_agent_type(event_agent)
                    tool_calls_made.append({
                        'tool_name': call.name,
                        'agent': event_agent or 'unknown',
                        'agent_type': agent_type
                    })
                    print(f"\n🛠️ TOOL CALL: {call.name} (by {agent_type})")
        
        # Check for final response
        if hasattr(event, 'is_final_response') and event.is_final_response():
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                final_response = event.content.parts[0].text
                responder_type = identify_agent_type(event_agent) if event_agent else "Master Agent"
                
                print(f"\n🤖 {responder_type.upper()} RESPONSE:")
                print(f"{'─'*50}")
                print(f"{Colors.GREEN_BOLD}{final_response}{Colors.RESET}")
                print(f"{'─'*50}")
    
    # Summary
    print(f"\n📊 INTERACTION SUMMARY:")
    if tool_calls_made:
        print(f"   Tools used: {len(tool_calls_made)}")
        for tool in tool_calls_made:
            print(f"   - {tool['tool_name']} (by {tool['agent_type']})")
    
    print(f"\n{'='*70}")
    
    return final_response