#!/usr/bin/env python3
"""
Comprehensive Test Message Scenarios for UKConnect Customer Support Agent

This file contains multiple conversation sessions with realistic user messages
to thoroughly test all agent functionality including:
- Policy queries (ukconnect_support_agent)
- Ticket operations (ticket_operations_agent)  
- Master agent delegation and orchestration
- Mixed conversation flows
- Location-aware booking with contextual assumptions
- Modern casual communication styles (Gen Z, mobile-first)

Each session represents a realistic customer interaction with the multi-agent system.

CUSTOMER EMAIL MAPPING:
Each test session uses a specific real customer from the database with location intelligence:

FORMAL/BUSINESS SESSIONS (1-10):
- Session 1: James Thompson (james.thompson@email.co.uk) - CUS001
- Session 2: Sarah Williams (sarah.williams@email.co.uk) - CUS002  
- Session 3: Michael Davies (michael.davies@email.co.uk) - CUS003
- Session 4: Emily Johnson (emily.johnson@email.co.uk) - CUS004
- Session 5: Robert Brown (robert.brown@email.co.uk) - CUS005
- Session 6: Lisa Wilson (lisa.wilson@email.co.uk) - CUS006
- Session 7: David Evans (david.evans@email.co.uk) - CUS007
- Session 8: Jennifer Smith (jennifer.smith@email.co.uk) - CUS008
- Session 9: Christopher Jones (chris.jones@email.co.uk) - CUS009
- Session 10: Amanda Taylor (amanda.taylor@email.co.uk) - CUS010

CASUAL/MODERN SESSIONS (11-15) - Location-Aware:
- Session 11: Alex Smith (alex.smith@student.ac.uk) - CUS051 | London Euston
- Session 12: Jordan Wilson (jordan.wilson@company.co.uk) - CUS052 | London King's Cross
- Session 13: Casey Brown (casey.brown@email.co.uk) - CUS053 | Birmingham New Street
- Session 14: Sam Taylor (sam.taylor@emergency.co.uk) - CUS054 | London King's Cross
- Session 15: Riley Jones (riley.jones@student.ac.uk) - CUS055 | Glasgow Central

The casual sessions (11-15) test location intelligence where customers provide minimal
context (e.g., "need train to manchester") and the system uses their address to assume
departure stations automatically.
"""

# ============================================================================
# SESSION 1: NEW CUSTOMER - POLICY QUESTIONS AND FIRST BOOKING
# ============================================================================

SESSION_1_NEW_CUSTOMER = [
    "Hi, I'm thinking of booking my first train ticket with UKConnect. What are the different ticket types available?",
    
    "What's the difference between Standard and Flexible fares? Which one should I choose for a business trip?",
    
    "If I book a Standard fare and need to cancel, what fees would I have to pay?",
    
    "I need to travel from London to Manchester tomorrow morning for a business meeting. Can you show me what trains are available?",
    
    "Perfect! I can see morning departures available. The 09:30 service looks ideal for my meeting schedule. Can you tell me more about this service - what are the amenities and is there WiFi for working during the journey?",
    
    "That sounds great for business travel. I'd like to book the 09:30 flexible fare. Can you proceed with the booking? My email is james.thompson@email.co.uk and I'll pay with credit card.",
    
    "Excellent! Can you confirm my booking reference and show me my complete ticket details? I want to make sure everything is correct for my business records.",
    
    "Perfect, thank you! Do I need to print anything or will showing the confirmation email on my phone be sufficient at the station?",
    
    "One more question - can I get a detailed invoice for this booking for my company expenses? They need to see the breakdown of costs.",
    
    "That all sounds excellent. Thank you for your help with my first UKConnect booking!"
]

# ============================================================================
# SESSION 2: EXISTING CUSTOMER - REFUND AND REBOOKING
# ============================================================================

SESSION_2_REFUND_REBOOKING = [
    "Hello, I have a booking reference UKC021 that I need to cancel. Can you help me with this?",
    
    "Before I cancel, can you tell me how much refund I would get for this booking? I want to understand the refund calculation.",
    
    "That refund amount is reasonable given the timing. Please go ahead and process the cancellation. The reason is that my meeting was moved to next week.",
    
    "Great! Now I need to book a new ticket for the same route but next Tuesday instead. Can you search for trains from London Euston to Manchester Piccadilly on September 23rd? I'd like to see all the available options.",
    
    "I can see several options for Tuesday. Can you show me the price comparison between Standard and Flexible fares for the morning departures? I want to make sure I choose the right fare type this time.",
    
    "Given what just happened with my original booking, I think the Flexible fare makes more sense. Can you show me the 9:30 UK101 service in Flexible fare - what's the total cost and what are the benefits?",
    
    "Before I commit to this booking, can you explain UKConnect's 24-hour cancellation policy for Flexible fares? I want to understand my options if plans change again.",
    
    "That flexibility sounds perfect for my needs. Please book the 9:30 UK101 Flexible fare for September 23rd. My email is sarah.williams@email.co.uk and I'll pay with my debit card.",
        
    "Perfect! Can you show me all my current active bookings now? I want to make sure the cancelled booking is gone and the new one is confirmed."
]

# ============================================================================
# SESSION 3: COMPLEX CUSTOMER - MULTIPLE QUERIES AND MODIFICATIONS
# ============================================================================

SESSION_3_COMPLEX_QUERIES = [
    "Hi, I'm planning a trip from Birmingham New Street to London Euston and have several questions. First, what trains are available tomorrow afternoon between 2 PM and 6 PM?",
    
    "I see there are different ticket types available. Can UKConnect fares be booked on partner rail services, or only on UKConnect trains? I want to understand my options.",
    
    "I'm particularly interested in first class travel. Can you show me what's available in first class for those afternoon departures? I'd like to compare the options.",
    
    "What are the specific benefits of first class compared to standard? And what's the price difference for the trains you've shown me?",
    
    "I notice there's also flexible fares. Can you explain the difference between First Class and Flexible Standard? Which would give me better value for a business trip?",
    
    "If I initially book a Standard fare, can I upgrade to First Class later, or do I need to decide now? What would be the upgrade process?",
    
    "Before I make my decision, I want to understand the refund policy for first class tickets. What happens if I need to cancel 2 hours before departure?",
    
    "I also need to know about luggage allowances and onboard amenities. How much luggage can I bring with a first class ticket, and what services are included?",
    
    "Based on everything you've told me, I think the UK401 first class service at 3:30 PM works best. Can you book this for me? My email is michael.davies@email.co.uk, and I'll pay with Apple Pay.",
    
    "Excellent! After booking, can I make changes to this ticket online, or do I need to call customer service? What's the latest time I can make changes before departure?",
    
    "Perfect! Can you show me my complete booking confirmation and tell me exactly what I need to bring for check-in tomorrow?"
]

# ============================================================================
# SESSION 4: BUSINESS TRAVELER - GROUP BOOKING AND CORPORATE NEEDS
# ============================================================================

SESSION_4_BUSINESS_TRAVELER = [
    "Good morning, I need to arrange travel for a business meeting. Can you help me with group bookings? We have 6 people traveling from London to Edinburgh.",
    
    "How many passengers can I book together in one transaction? What's the process for group bookings?",
    
    "What's the process for booking more than 9 passengers? Do you have a group booking form or special rates for larger groups?",
    
    "For now, let me start by booking for 3 of us. Can you search for trains from London King's Cross to Edinburgh Waverley tomorrow morning? We'd prefer first class if available.",
    
    "I can see several morning options. Can you show me the availability and pricing for first class on the 7:00 AM UK502 service? We need to sit together if possible.",
    
    "What's the total cost for 3 first class tickets on that service? We need to ensure we can get proper invoices for our company accounting - what documentation will you provide?",
    
    "Before I proceed with the booking, what's your policy on corporate accounts and payment methods? Can I use a corporate credit card?",
    
    "Perfect. Can you check if there are 3 first class seats available together on the UK502 service? If not, what's the closest seating arrangement you can offer?",
    
    "That seating arrangement works for us. Please book 3 first class tickets on the 7:00 AM UK502 service for tomorrow. The travelers are myself (emily.johnson@email.co.uk), plus my colleagues Sarah Williams and Michael Davies.",
    
    "Excellent! Can you show me the group booking confirmation with all three tickets? I need to forward the details to my colleagues and our finance department."
]

# ============================================================================
# SESSION 5: CUSTOMER WITH ISSUES - COMPLAINTS AND PROBLEM RESOLUTION
# ============================================================================

SESSION_5_PROBLEM_RESOLUTION = [
    "Hi, I'm having issues with my booking. I tried to book online but the payment failed, and now I'm not sure if my ticket was actually reserved.",
    
    "My email is robert.brown@email.co.uk. Can you check if I have any active bookings or recent transactions? I'm worried about double-charging.",
    
    "I was trying to book a train from London King's Cross to Edinburgh for today, but the website said there was a payment error. Can you help me complete this booking?",
    
    "I need to travel in 3 hours for an important meeting. Can you search for available trains from London King's Cross to Edinburgh departing after 2 PM today? I need to see all options.",
    
    "What's your policy on last-minute bookings? Are there additional fees for booking this close to departure time, and what are my fare options?",
    
    "I can see the UK502 service at 3:00 PM might work. What's the price for Standard versus Flexible fare on that train? Given the urgency, which would you recommend?",
    
    "Before I book, I want to understand what happens if my train is delayed or cancelled by UKConnect. What protection do I have as a passenger?",
    
    "That's reassuring. I'll go with the Flexible fare for peace of mind. Can you book me the UK502 service at 3:00 PM in Flexible fare? I'll pay with my Visa card.",
    
    "Great! Now I'm concerned about getting to the station on time. What do I need to know about check-in and boarding procedures for a departure in 3 hours?",
    
    "Can I change my seat selection after booking, or do I need to accept the assigned seat? Also, is there mobile check-in available?",
    
    "One final question - if I miss this train due to London traffic, what are my options with a Flexible fare ticket? Can I catch the next available service?"
]

# ============================================================================
# SESSION 6: RETURN CUSTOMER - LOYALTY AND FREQUENT TRAVELER QUERIES
# ============================================================================

SESSION_6_FREQUENT_TRAVELER = [
    "Hello, I'm a regular UKConnect customer and travel the Glasgow to Edinburgh route weekly. Do you have any loyalty programs or frequent traveler benefits?",
    
    "I usually book the same route - Glasgow Central to Edinburgh Waverley every Monday and Friday. Can you show me what tickets are available for this Friday morning?",
    
    "I can see the UK801 service at 8:00 AM. What are the fare options for this service, and how do loyalty points work? What benefits do they provide?",
    
    "As a frequent traveler, what should I consider when choosing between Standard, Flexible, and First Class fares? Which gives the best value for regular weekly travel?",
    
    "I'm interested in flexible fares for my regular travel since my meeting times sometimes change. Can you show me the price and benefits for the UK801 Flexible fare this Friday?",
    
    "That sounds good for Friday. For my return journey on Sunday, I'd like to try first class as a treat. What additional services are included with first class tickets on the Edinburgh to Glasgow route?",
    
    "Can you search for first class tickets from Edinburgh Waverley to Glasgow Central on Sunday evening? I'd prefer a departure around 6-8 PM.",
    
    "Perfect! I'd like to book both tickets - the Friday morning UK801 Flexible fare and the Sunday evening first class return. My email is lisa.wilson@email.co.uk.",
    
    "Excellent! Can you show me my complete booking summary with both tickets? I also want to see my loyalty points balance and what I'll earn from these bookings.",
    
    "Since I travel this route so regularly, do you offer any season ticket options or weekly/monthly passes that might be more economical for commuters like me?"
]

# ============================================================================
# SESSION 7: PRICE-SENSITIVE CUSTOMER - BUDGET TRAVEL AND COMPARISONS
# ============================================================================

SESSION_7_BUDGET_TRAVEL = [
    "Hi, I'm looking for the cheapest way to travel from Liverpool Lime Street to Manchester Piccadilly tomorrow. What are my most affordable options?",
    
    "Can you show me all available trains on this route with their prices? I need to compare costs to find the best value.",
    
    "I can see the UK701 service. What's the difference in price between Standard and Flexible fares for this route? I want to understand what I'm paying for.",
    
    "Are there any discounts available for students or young travelers? I'm a university student and trying to keep costs down.",
    
    "Can you explain why train prices vary throughout the day? Are there specific off-peak times that would be cheaper for this route?",
    
    "The UK701 service at £25 for Standard looks affordable. Before I book, what exactly is included with a Standard fare ticket? Any restrictions I should know about?",
    
    "If I book the cheapest Standard fare, what restrictions should I be aware of? Can I change my travel plans if needed, or am I locked in?",
    
    "I understand the restrictions, and the price works for my budget. Can you book me the UK701 Standard fare for tomorrow? My email is david.evans@email.co.uk, and I'll pay with PayPal.",
    
    "Great! After booking, if I happen to find a better price elsewhere, can I still make changes or get a price match?",
    
    "What's your best price guarantee policy? Do you match competitor prices, and how does that process work for students like me?"
]

# ============================================================================
# SESSION 8: ACCESSIBILITY AND SPECIAL NEEDS CUSTOMER
# ============================================================================

SESSION_8_ACCESSIBILITY_NEEDS = [
    "Hello, I need to book a train journey but require wheelchair accessibility. Can you help me find suitable trains with proper accessibility features?",
    
    "I'm looking to travel from London Euston to Birmingham New Street tomorrow morning. Which trains have full wheelchair access and appropriate facilities?",
    
    "Can you show me the specific accessibility features available on UKConnect trains? Do you have dedicated wheelchair spaces, and how do I reserve them?",
    
    "I also travel with a guide dog. What's your policy on assistance animals, and do I need to provide any documentation?",
    
    "Can you search for accessible trains from London Euston to Birmingham New Street tomorrow morning between 8 AM and 11 AM? I need to see all wheelchair-accessible options.",
    
    "I can see the UK301 service at 9:00 AM. Can you confirm this train has wheelchair access and show me the available accessible seating options?",
    
    "How do I ensure my accessibility requirements are properly included in my booking? Do I need to notify you in advance, and what information do you need?",
    
    "Perfect. Can you book the UK301 service with wheelchair accessibility and space for my guide dog? My email is jennifer.smith@email.co.uk and I'll pay with my debit card.",
    
    "Will my accessibility requirements be automatically transferred if I need to make changes to my booking later? How does that process work?",
    
    "What should I do when I arrive at the station? Is there assistance available for boarding, and how far in advance should I request help?",
    
    "Can you provide me with the direct accessibility contact information for both London Euston and Birmingham New Street stations? I want to coordinate my arrival."
]

# ============================================================================
# SESSION 9: INTERNATIONAL VISITOR - PAYMENT AND DOCUMENTATION
# ============================================================================

SESSION_9_INTERNATIONAL_VISITOR = [
    "Hello, I'm visiting the UK from the United States and need to book train tickets. Can you help me understand the booking process for international visitors?",
    
    "What payment methods do you accept for international visitors? Can I use my American credit card, and are there any additional fees?",
    
    "Do you offer currency conversion at the time of booking, or will I be charged in British pounds? I want to understand the exchange process.",
    
    "I need to travel from London King's Cross to Edinburgh Waverley next Tuesday for tourism. What fare type would you recommend for flexibility as a visitor?",
    
    "Can you search for available tickets on that route for next Tuesday? I'd like to see the options for both Flexible and First Class fares.",
    
    "The first class option looks appealing for sightseeing. Can you tell me what's included with first class and how the pricing compares to Flexible fare?",
    
    "What documentation do I need for travel? Do I need to show my passport on the train, and are there any ID requirements?",
    
    "For expense reporting back home, what kind of receipts and documentation will you provide? I need detailed invoices for my company.",
    
    "Perfect! I'd like to book the first class ticket for next Tuesday's journey. My email is chris.jones@email.co.uk and I'll pay with my American Express card.",
    
    "If my travel plans change due to weather or other circumstances, what's your policy on modifications for international visitors? Are the rules different for us?",
    
    "Finally, can you provide me with information about what to expect on my journey and any tips for first-time train travelers in the UK?"
]

# ============================================================================
# SESSION 10: MIXED COMPLEX SESSION - TESTING ALL FUNCTIONALITY
# ============================================================================

SESSION_10_COMPREHENSIVE_TEST = [
    "Hi, I need help with multiple things today. First, can you show me my current bookings? My email is amanda.taylor@email.co.uk",
    
    "I need to understand your refund policy for different ticket types before making decisions. What are the specific rules for Standard, Flexible, and First Class fares?",
    
    "I have booking reference UKC022 that I might need to cancel due to a schedule conflict. Can you look up this booking and calculate what refund I would get?",
    
    "Actually, instead of canceling completely, can I change this booking to a different date? What's your rebooking policy and what would be the cost difference?",
    
    "Let me keep that original booking for now. I need to book additional travel for next month. Can you search for trains from Manchester Piccadilly to London Euston on October 15th?"
    
    "I can see several options for that date. Can you show me a detailed price comparison between Standard, Flexible, and First Class for the morning departures? I want to understand the value differences.",
    
    "What happens if I initially book a Standard fare and later want to upgrade to First Class? Is that possible, and what's the process?",
    
    "I also need information about group bookings for future travel. How many people can I book together in one transaction, and are there group discounts available?",
    
    "For my upcoming travel in August, I need accessibility assistance for wheelchair access. How do I ensure this is properly arranged when booking?",
    
    "Can you search specifically for first class tickets with wheelchair accessibility from Manchester Piccadilly to London Euston on October 15th morning?"
    
    "The UK202 service looks good. Before I book, what payment methods do you accept, and can I use corporate payment accounts for business travel?",
    
    "Perfect! Please book the UK202 first class service for October 15th with wheelchair accessibility noted. I'll pay with my corporate credit card."
    
    "Excellent! Now can you show me a complete summary of all my active bookings and recent transactions so I can review everything together?",
    
    "Finally, I need detailed invoice documentation for my company accounting. What's the process for getting comprehensive invoices with all the required business details?",
    
    "Thank you for all the comprehensive help today! Can you summarize everything we've accomplished in this session and confirm all my upcoming travel arrangements?"
]

# ============================================================================
# SESSION 11: CASUAL GEN Z STUDENT - LONDON BASED
# ============================================================================

SESSION_11_CASUAL_STUDENT = [
    "yo need train to manchester",
    
    "tomorrow morning",
    
    "cheapest option pls",
    
    "what time does it leave?",
    
    "how much?",
    
    "ok sounds good",
    
    "book the cheapest one",
    
    "paying with apple pay",
    
    "mobile ticket ok?",
    
    "perfect thx"
]

# ============================================================================
# SESSION 12: MILLENNIAL YOUNG PROFESSIONAL - LONDON BASED
# ============================================================================

SESSION_12_YOUNG_PROFESSIONAL = [
    "hey quick question",
    
    "need to get to edinburgh next week",
    
    "work meeting tuesday september 23rd"
    
    "flexible fare prob best right?",
    
    "whats available tuesday morning?",
    
    "how much is first class?",
    
    "worth the upgrade for 4hr journey?",
    
    "ok flexible sounds good",
    
    "can i get seat with table?",
    
    "book the 7am flexible train",
    
    "paying with corporate card",
    
    "email receipt for expenses"
]

# ============================================================================
# SESSION 13: MOBILE-FIRST USER - BIRMINGHAM BASED  
# ============================================================================

SESSION_13_MOBILE_USER = [
    "train booking help pls",
    
    "need to get to london",
    
    "tomorrow afternoon",
    
    "standard vs flexible?",
    
    "whats the price diff?",
    
    "can i change the ticket later?",
    
    "if i miss the train?",
    
    "flexible sounds safer",
    
    "mobile ticket ok?",
    
    "book the flexible ticket",
    
    "paying with google pay",
    
    "thanks all set"
]

# ============================================================================
# SESSION 14: URGENT TRAVELER - LONDON BASED
# ============================================================================

SESSION_14_URGENT_TRAVEL = [
    "URGENT - need train to manchester NOW",
    
    "have to leave within 2 hours",
    
    "price doesnt matter - fastest option",
    
    "book the earliest train",
    
    "yes confirm the booking",
    
    "paying with credit card",
    
    "send confirmation to my email"
]

# ============================================================================
# SESSION 15: SOCIAL MEDIA STYLE - GLASGOW BASED
# ============================================================================

SESSION_15_SOCIAL_STYLE = [
    "hiii 👋",
    
    "need train help",
    
    "glasgow to edinburgh this fri",
    
    "student discount available? 🎓",
    
    "broke uni student lol",
    
    "cheapest option pls",
    
    "what time is it?",
    
    "can i split payment?",
    
    "book cheapest ticket",
    
    "ok just paypal then",
    
    "tysm ur amazing 🙌"
]

# ============================================================================
# SESSION METADATA
# ============================================================================

ALL_TEST_SESSIONS = {
    "session_1_new_customer": {
        "title": "New Customer - Interactive Journey Planning and First Booking",
        "description": "Tests complete journey planning workflow: policy education, fare comparison, seat selection, and booking process with realistic decision-making",
        "customer_email": "james.thompson@email.co.uk",
        "customer_name": "James Thompson",
        "customer_id": "CUS001",
        "messages": SESSION_1_NEW_CUSTOMER,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["policy education", "interactive search", "fare comparison", "seat selection", "booking workflow"]
    },
    
    "session_2_refund_rebooking": {
        "title": "Existing Customer - Interactive Refund and Rebooking Flow",
        "description": "Tests refund calculation, cancellation processing, and comprehensive rebooking with fare comparison and policy education",
        "customer_email": "sarah.williams@email.co.uk",
        "customer_name": "Sarah Williams",
        "customer_id": "CUS002",
        "messages": SESSION_2_REFUND_REBOOKING,
        "expected_agents": ["ticket_operations_agent", "ukconnect_support_agent", "master_agent"],
        "key_functionality": ["refund calculation", "cancellation processing", "interactive rebooking", "fare comparison", "policy education"]
    },
    
    "session_3_complex_queries": {
        "title": "Complex Customer - First Class Evaluation and Decision-Making",
        "description": "Tests complex fare comparisons, first class vs flexible fare analysis, upgrade policies, and informed booking decisions",
        "customer_email": "michael.davies@email.co.uk",
        "customer_name": "Michael Davies",
        "customer_id": "CUS003",
        "messages": SESSION_3_COMPLEX_QUERIES,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["complex fare analysis", "first class evaluation", "upgrade policies", "amenity comparison", "informed decision-making"]
    },
    
    "session_4_business_traveler": {
        "title": "Business Traveler - Interactive Group Booking and Corporate Coordination",
        "description": "Tests group booking process, seating coordination, corporate payment methods, and multi-passenger booking management",
        "customer_email": "emily.johnson@email.co.uk",
        "customer_name": "Emily Johnson",
        "customer_id": "CUS004",
        "messages": SESSION_4_BUSINESS_TRAVELER,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["group booking coordination", "seating management", "corporate payment", "multi-passenger booking", "invoice generation"]
    },
    
    "session_5_problem_resolution": {
        "title": "Customer with Issues - Complaints and Problem Resolution",
        "description": "Tests problem resolution, customer account checking, and urgent booking scenarios",
        "customer_email": "robert.brown@email.co.uk",
        "customer_name": "Robert Brown",
        "customer_id": "CUS005",
        "messages": SESSION_5_PROBLEM_RESOLUTION,
        "expected_agents": ["ticket_operations_agent", "ukconnect_support_agent", "master_agent"],
        "key_functionality": ["account checking", "problem resolution", "urgent booking", "policies"]
    },
    
    "session_6_frequent_traveler": {
        "title": "Return Customer - Loyalty and Frequent Traveler Queries",
        "description": "Tests loyalty program queries, frequent traveler benefits, and multiple bookings",
        "customer_email": "lisa.wilson@email.co.uk",
        "customer_name": "Lisa Wilson",
        "customer_id": "CUS006",
        "messages": SESSION_6_FREQUENT_TRAVELER,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["loyalty programs", "frequent travel", "multiple bookings", "season tickets"]
    },
    
    "session_7_budget_travel": {
        "title": "Price-Sensitive Customer - Budget Travel and Comparisons",
        "description": "Tests price comparisons, budget options, and fare restrictions",
        "customer_email": "david.evans@email.co.uk",
        "customer_name": "David Evans",
        "customer_id": "CUS007",
        "messages": SESSION_7_BUDGET_TRAVEL,
        "expected_agents": ["ticket_operations_agent", "ukconnect_support_agent", "master_agent"],
        "key_functionality": ["price comparisons", "budget travel", "fare restrictions", "discounts"]
    },
    
    "session_8_accessibility_needs": {
        "title": "Accessibility and Special Needs Customer",
        "description": "Tests accessibility requirements, special assistance, and inclusive travel",
        "customer_email": "jennifer.smith@email.co.uk",
        "customer_name": "Jennifer Smith",
        "customer_id": "CUS008",
        "messages": SESSION_8_ACCESSIBILITY_NEEDS,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["accessibility", "special assistance", "inclusive booking", "station support"]
    },
    
    "session_9_international_visitor": {
        "title": "International Visitor - Payment and Documentation",
        "description": "Tests international payment methods, documentation, and visitor-specific policies",
        "customer_email": "chris.jones@email.co.uk",
        "customer_name": "Christopher Jones",
        "customer_id": "CUS009",
        "messages": SESSION_9_INTERNATIONAL_VISITOR,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["international payment", "documentation", "visitor policies", "currency conversion"]
    },
    
    "session_10_comprehensive_test": {
        "title": "Comprehensive Multi-Operation Session - Complete System Demonstration",
        "description": "Advanced session testing booking management, policy analysis, accessibility coordination, corporate invoicing, and complete customer service workflow",
        "customer_email": "amanda.taylor@email.co.uk",
        "customer_name": "Amanda Taylor",
        "customer_id": "CUS010",
        "messages": SESSION_10_COMPREHENSIVE_TEST,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["booking management", "policy analysis", "accessibility coordination", "corporate invoicing", "comprehensive workflow", "multi-operation testing"]
    },
    
    "session_11_casual_student": {
        "title": "Gen Z Student - Casual Communication Style",
        "description": "Tests ultra-casual communication with minimal context, location-based assumptions, and modern payment methods",
        "customer_email": "alex.smith@student.ac.uk",
        "customer_name": "Alex Smith",
        "customer_id": "CUS051",
        "default_location": "London Euston",
        "location_context": "Student based in London (Gower Street - university area)",
        "journey_assumption": "London Euston to destination",
        "messages": SESSION_11_CASUAL_STUDENT,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["casual communication", "location context", "minimal information handling", "mobile payments", "quick booking"]
    },
    
    "session_12_young_professional": {
        "title": "Millennial Professional - Efficient Communication",
        "description": "Tests informal but efficient business travel booking with work context and expense requirements",
        "customer_email": "jordan.wilson@company.co.uk",
        "customer_name": "Jordan Wilson", 
        "customer_id": "CUS052",
        "default_location": "London King's Cross",
        "location_context": "Business professional in London (Canary Wharf - financial district)",
        "journey_assumption": "London King's Cross to destination",
        "messages": SESSION_12_YOUNG_PROFESSIONAL,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["efficient communication", "business travel", "fare comparison", "expense handling", "seat preferences"]
    },
    
    "session_13_mobile_user": {
        "title": "Mobile-First User - Birmingham Based",
        "description": "Tests mobile-centric communication with abbreviations and location-aware journey planning. Customer says 'need to get to london' expecting system to use Birmingham New Street as departure station automatically.",
        "customer_email": "casey.brown@email.co.uk",
        "customer_name": "Casey Brown",
        "customer_id": "CUS053", 
        "default_location": "Birmingham New Street",
        "location_context": "Mobile user based in Birmingham (Broad Street - city center)",
        "journey_assumption": "Birmingham New Street to London (automatic location intelligence)",
        "messages": SESSION_13_MOBILE_USER,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["mobile communication", "fare flexibility", "change policies", "digital payments", "location context", "automatic departure station detection"]
    },
    
    "session_14_urgent_travel": {
        "title": "Urgent Traveler - Time-Critical Booking",
        "description": "Tests high-pressure urgent booking with time constraints and priority customer service",
        "customer_email": "sam.taylor@emergency.co.uk",
        "customer_name": "Sam Taylor",
        "customer_id": "CUS054",
        "default_location": "London King's Cross", 
        "location_context": "Urgent business traveler in London (Fleet Street - financial district)",
        "journey_assumption": "London King's Cross to destination",
        "messages": SESSION_14_URGENT_TRAVEL,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["urgent booking", "time pressure", "fast processing", "priority service", "immediate confirmation"]
    },
    
    "session_15_social_style": {
        "title": "Social Media Generation - Emoji & Casual Style",
        "description": "Tests social media communication style with emojis, student context, and payment flexibility",
        "customer_email": "riley.jones@student.ac.uk",
        "customer_name": "Riley Jones",
        "customer_id": "CUS055",
        "default_location": "Glasgow Central",
        "location_context": "Student based in Glasgow (University Avenue - campus area)",
        "journey_assumption": "Glasgow Central to destination", 
        "messages": SESSION_15_SOCIAL_STYLE,
        "expected_agents": ["ukconnect_support_agent", "ticket_operations_agent", "master_agent"],
        "key_functionality": ["social media style", "emoji communication", "student discounts", "payment flexibility", "casual interaction"]
    }
}

# ============================================================================
# DATABASE RESET UTILITY
# ============================================================================

def reset_database():
    """Reset the database to a clean state by running the populate_data script."""
    import subprocess
    import os
    
    print("🔄 Resetting database to clean state...")
    print("=" * 50)
    
    try:
        # Get the path to the populate_data script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        populate_script = os.path.join(current_dir, "utils", "populate_data.py")
        db_path = os.path.join(current_dir, "database", "ukconnect_rail.db")
        
        # Run the populate_data script with the correct database path
        result = subprocess.run([
            "python", populate_script, db_path
        ], capture_output=True, text=True, cwd=os.path.dirname(current_dir))
        
        if result.returncode == 0:
            print("✅ Database reset successful!")
            print("Database is ready for testing with fresh data:")
            print("- 50 customers")
            print("- 100 available tickets (80 available, 20 sold)")
            print("- 20 booked tickets with transaction history")
            print("- 15 train schedules")
            print()
            return True
        else:
            print("❌ Database reset failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_session_by_name(session_name):
    """Get a specific test session by name."""
    return ALL_TEST_SESSIONS.get(session_name)

def get_all_sessions():
    """Get all test sessions."""
    return ALL_TEST_SESSIONS

def get_session_messages(session_name):
    """Get just the messages for a specific session."""
    session = ALL_TEST_SESSIONS.get(session_name)
    return session["messages"] if session else None

def print_session_summary():
    """Print a summary of all available test sessions."""
    print("UKConnect Customer Support Agent - Test Message Scenarios")
    print("=" * 60)
    print(f"Total test sessions: {len(ALL_TEST_SESSIONS)}")
    print()
    
    # Group sessions by type
    formal_sessions = []
    casual_sessions = []
    
    for session_key, session_data in ALL_TEST_SESSIONS.items():
        session_num = int(session_key.split('_')[1])
        if session_num > 10:
            casual_sessions.append((session_key, session_data))
        else:
            formal_sessions.append((session_key, session_data))
    
    print("📋 FORMAL/BUSINESS SESSIONS (1-10):")
    print("-" * 40)
    for session_key, session_data in formal_sessions:
        print(f"   {session_data['title']}")
        print(f"   Customer: {session_data['customer_name']} ({session_data['customer_email']})")
        print(f"   Messages: {len(session_data['messages'])} | Tests: {', '.join(session_data['key_functionality'][:3])}")
        print()
    
    print("💬 CASUAL/MOBILE SESSIONS (11-15):")
    print("-" * 40)
    for session_key, session_data in casual_sessions:
        location_info = f" | Location: {session_data.get('default_location', 'N/A')}" if 'default_location' in session_data else ""
        print(f"   {session_data['title']}")
        print(f"   Customer: {session_data['customer_name']} ({session_data['customer_email']})")
        print(f"   Messages: {len(session_data['messages'])} | Tests: {', '.join(session_data['key_functionality'][:3])}{location_info}")
        print()

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--reset-db":
        print("UKConnect Customer Support Agent - Database Reset")
        print("=" * 60)
        success = reset_database()
        sys.exit(0 if success else 1)
    
    print_session_summary()
    
    # Show database reset option
    print("💡 To reset the database before testing, run:")
    print("   python test_message_scenarios.py --reset-db")
    print()
    
    # Examples of different communication styles
    print("Example - Session 1 (Formal Business Style):")
    print("-" * 50)
    session_1 = get_session_messages("session_1_new_customer")
    for i, message in enumerate(session_1[:3], 1):
        print(f"{i}. {message}")
    print("...")
    
    print("\nExample - Session 11 (Casual Gen Z Style):")
    print("-" * 50)
    session_11 = get_session_messages("session_11_casual_student")
    for i, message in enumerate(session_11, 1):
        print(f"{i}. {message}")