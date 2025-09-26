# Tutorial 5: Master Agent Design (20 min)

## 🎯 Overview
Build the Master Agent - the central orchestrator that analyzes customer queries and intelligently routes them to specialist agents.

## 🧠 What You'll Learn
- Query intent analysis
- Agent routing logic
- Context management
- Response synthesis

## 🏗️ Master Agent Architecture

```
Customer Query → Master Agent → [Intent Analysis] → Route to Specialist → Synthesize Response
                     ↓                ↓                      ↓
              [Context Mgmt]  [Policy Agent]        [Response Coordination]
                     ↓         [Ticket Agent]              ↓
              [Customer State]     ↓               [Unified Experience]
```

## 🔧 Implementation

### Core Orchestrator
```python
# agent.py
from google.adk.agents import Agent

class MasterAgent:
    def __init__(self):
        self.policy_agent = PolicyAgent()
        self.ticket_agent = TicketAgent()
        
    def process_query(self, query, context):
        # Analyze query intent
        intent = self.analyze_intent(query)
        
        # Route to appropriate agent
        if intent == "policy":
            return self.policy_agent.handle_query(query, context)
        elif intent == "booking":
            return self.ticket_agent.handle_query(query, context)
        else:
            return self.handle_mixed_query(query, context)
```

### Intent Analysis
```python
def analyze_intent(self, query):
    policy_keywords = ["refund", "policy", "terms", "conditions"]
    booking_keywords = ["book", "ticket", "train", "cancel", "modify"]
    
    if any(word in query.lower() for word in policy_keywords):
        return "policy"
    elif any(word in query.lower() for word in booking_keywords):
        return "booking"
    else:
        return "mixed"
```

## 🎯 Orchestration Patterns

1. **Simple Routing**: Direct queries to single agent
2. **Sequential Processing**: Multi-step workflows across agents
3. **Parallel Consultation**: Combine insights from multiple agents
4. **Context Handoff**: Maintain state across agent transitions

## 🧪 Testing

```bash
# Test master agent orchestration
python interactive_test.py
# or
python run_test_scenarios.py --session 1
```

## 🚀 Next Steps
**Tutorial 6**: Add location intelligence for context-aware booking.