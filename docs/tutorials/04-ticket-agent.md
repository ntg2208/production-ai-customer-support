# Tutorial 4: Ticket Agent Build (25 min)

## 🎯 Overview
Build the Ticket Agent - an operations specialist that handles booking management, customer data, and database transactions.

## 🛠️ What You'll Learn
- Database integration patterns
- Transaction management
- Booking workflow implementation
- Tool-based agent architecture

## 🏗️ Ticket Agent Architecture

```
Customer Request → Ticket Agent → Database Tools → Database Operations → Response
                       ↓
                [Specialized Tools]
                • Booking search
                • Customer lookup
                • Payment processing
                • Modification tools
```

## 🔧 Core Implementation

### Agent Setup
```python
# sub_agents/ticket_agent/agent.py
from google.adk.agents import Agent
from tools.ticket_tools import TicketTools

ticket_agent = Agent(
    model="gemini-2.0-flash",
    instructions=TICKET_AGENT_PROMPT,
    tools=[
        TicketTools.search_tickets,
        TicketTools.book_ticket,
        TicketTools.modify_booking,
        TicketTools.cancel_booking,
        TicketTools.get_customer_info
    ]
)
```

### Key Tools
- **search_tickets**: Find available trains and fares
- **book_ticket**: Create new reservations
- **modify_booking**: Change existing bookings
- **cancel_booking**: Process cancellations and refunds
- **get_customer_info**: Retrieve customer account details

## 🎯 Use Cases Handled

1. **Ticket Search**: "Show me trains from London to Manchester tomorrow"
2. **Booking Creation**: "Book me the 9:30 AM departure"
3. **Modifications**: "Change my booking to next Friday"
4. **Cancellations**: "Cancel booking UKC005"

## 🧪 Testing

```bash
# Test ticket agent operations
python -c "
from sub_agents.ticket_agent.agent import ticket_agent
response = ticket_agent.run('Search trains London to Manchester tomorrow')
print(response)
"
```

## 🚀 Next Steps
**Tutorial 5**: Implement the Master Agent to orchestrate both specialists.