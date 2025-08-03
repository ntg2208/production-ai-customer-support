# UKConnect AI Customer Support - API Reference

## 🎯 Overview
This document provides comprehensive API documentation for integrating with the UKConnect AI Customer Support system, including REST endpoints, WebSocket connections, and SDK usage.

## 🏗️ API Architecture

```
Client Application → API Gateway → Master Agent → [Policy Agent | Ticket Agent] → Response
                         ↓                ↓                     ↓
                    [Authentication] [Rate Limiting]    [Database/Vector DB]
```

## 🔑 Authentication

### API Key Authentication
```http
POST /api/v1/chat
Authorization: Bearer your_api_key_here
Content-Type: application/json
```

### JWT Token Authentication
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600
}
```

## 💬 Chat API

### Send Message
Send a customer message to the AI support system.

```http
POST /api/v1/chat
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "I need to book a train ticket from London to Manchester",
  "customer_id": "CUS001", 
  "session_id": "session_123",
  "context": {
    "previous_bookings": ["UKC001", "UKC002"],
    "preferred_station": "London Euston"
  }
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you book a train ticket from London to Manchester. Let me check the available options for you.",
  "session_id": "session_123",
  "agent_used": "ticket_agent",
  "confidence": 0.95,
  "response_time": 1.2,
  "suggested_actions": [
    {
      "type": "show_tickets",
      "data": {
        "route": "London Euston to Manchester Piccadilly",
        "date": "2024-03-15"
      }
    }
  ],
  "metadata": {
    "routing_decision": "booking_query",
    "context_preserved": true,
    "tools_used": ["search_tickets"]
  }
}
```

### Get Chat History
Retrieve conversation history for a session.

```http
GET /api/v1/chat/{session_id}/history
Authorization: Bearer {token}
```

**Response:**
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "timestamp": "2024-03-15T10:30:00Z",
      "type": "user",
      "content": "I need to book a train ticket",
      "metadata": {}
    },
    {
      "timestamp": "2024-03-15T10:30:01Z", 
      "type": "assistant",
      "content": "I'd be happy to help you book a train ticket...",
      "agent": "master_agent",
      "metadata": {
        "confidence": 0.95,
        "tools_used": []
      }
    }
  ],
  "total_messages": 2,
  "session_duration": 300
}
```

## 🎫 Booking API

### Search Tickets
Search for available train tickets.

```http
GET /api/v1/tickets/search?from=London%20Euston&to=Manchester%20Piccadilly&date=2024-03-15&passengers=1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "results": [
    {
      "departure_time": "09:30",
      "arrival_time": "12:45",
      "duration": "3h 15m",
      "operator": "UKConnect",
      "train_id": "UK001",
      "fares": [
        {
          "type": "Standard",
          "price": 85.50,
          "flexibility": "Limited changes",
          "refundable": false
        },
        {
          "type": "Flexible", 
          "price": 125.00,
          "flexibility": "Free changes",
          "refundable": true
        }
      ],
      "availability": "Available"
    }
  ],
  "search_metadata": {
    "total_results": 15,
    "search_time": 0.8,
    "filters_applied": ["direct_trains_only"]
  }
}
```

### Create Booking
Create a new train booking.

```http
POST /api/v1/bookings
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "customer_id": "CUS001",
  "departure_station": "London Euston",
  "arrival_station": "Manchester Piccadilly", 
  "departure_datetime": "2024-03-15T09:30:00Z",
  "ticket_type": "Standard",
  "passengers": 1,
  "payment_details": {
    "payment_method": "card",
    "card_token": "tok_visa_4242"
  }
}
```

**Response:**
```json
{
  "booking_id": "UKC123",
  "status": "confirmed",
  "reference": "UKC123",
  "total_amount": 85.50,
  "booking_details": {
    "departure_station": "London Euston",
    "arrival_station": "Manchester Piccadilly",
    "departure_datetime": "2024-03-15T09:30:00Z",
    "ticket_type": "Standard",
    "passengers": 1
  },
  "payment_status": "successful",
  "tickets": [
    {
      "ticket_id": "TKT001",
      "passenger_name": "John Smith",
      "seat": "12A",
      "coach": "B"
    }
  ]
}
```

### Get Booking Details
Retrieve details for a specific booking.

```http
GET /api/v1/bookings/{booking_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "booking_id": "UKC123",
  "customer_id": "CUS001",
  "status": "confirmed",
  "booking_date": "2024-03-14T15:30:00Z",
  "travel_details": {
    "departure_station": "London Euston",
    "arrival_station": "Manchester Piccadilly",
    "departure_datetime": "2024-03-15T09:30:00Z",
    "arrival_datetime": "2024-03-15T12:45:00Z"
  },
  "payment_details": {
    "amount": 85.50,
    "currency": "GBP",
    "payment_method": "card",
    "transaction_id": "txn_123"
  },
  "modification_history": [],
  "cancellation_policy": {
    "cancellable": true,
    "refund_amount": 68.40,
    "cancellation_fee": 17.10
  }
}
```

### Modify Booking
Modify an existing booking.

```http
PUT /api/v1/bookings/{booking_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "new_departure_datetime": "2024-03-16T09:30:00Z",
  "reason": "change_of_plans"
}
```

### Cancel Booking
Cancel a booking and process refund.

```http
DELETE /api/v1/bookings/{booking_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "reason": "unable_to_travel",
  "refund_method": "original_payment_method"
}
```

## 👤 Customer API

### Get Customer Profile
Retrieve customer information and preferences.

```http
GET /api/v1/customers/{customer_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "customer_id": "CUS001",
  "profile": {
    "name": "John Smith",
    "email": "john.smith@email.com",
    "phone": "+44 20 7946 0958",
    "address": {
      "line1": "45 Baker Street",
      "city": "London", 
      "postcode": "W1U 7EW",
      "country": "UK"
    }
  },
  "preferences": {
    "preferred_stations": ["London Euston"],
    "communication_channel": "email",
    "accessibility_needs": []
  },
  "booking_history": [
    {
      "booking_id": "UKC001",
      "travel_date": "2024-02-15",
      "route": "London to Birmingham",
      "status": "completed"
    }
  ],
  "loyalty_status": {
    "tier": "silver",
    "points": 1250,
    "next_tier_points": 750
  }
}
```

### Update Customer Profile
Update customer information.

```http
PUT /api/v1/customers/{customer_id}
Authorization: Bearer {token}
Content-Type: application/json
```

## 📊 Analytics API

### Get Chat Analytics
Retrieve analytics for chat interactions.

```http
GET /api/v1/analytics/chat?start_date=2024-03-01&end_date=2024-03-15
Authorization: Bearer {token}
```

**Response:**
```json
{
  "period": {
    "start_date": "2024-03-01",
    "end_date": "2024-03-15"
  },
  "metrics": {
    "total_conversations": 1250,
    "unique_customers": 890,
    "average_response_time": 1.8,
    "resolution_rate": 0.94,
    "customer_satisfaction": 4.6
  },
  "agent_performance": {
    "master_agent": {
      "queries_handled": 1250,
      "routing_accuracy": 0.97
    },
    "policy_agent": {
      "queries_handled": 450,
      "response_accuracy": 0.96
    },
    "ticket_agent": {
      "queries_handled": 800,
      "success_rate": 0.98
    }
  }
}
```

## 🔌 WebSocket API

### Real-time Chat Connection
Establish WebSocket connection for real-time chat.

```javascript
const ws = new WebSocket('wss://api.ukconnect.com/v1/chat/ws');

ws.onopen = function(event) {
    // Send authentication
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your_jwt_token'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'message') {
        displayMessage(data.content);
    }
};

// Send message
ws.send(JSON.stringify({
    type: 'message',
    content: 'I need help with my booking',
    session_id: 'session_123'
}));
```

## 📚 SDK Usage

### Python SDK
```python
from ukconnect import UKConnectClient

# Initialize client
client = UKConnectClient(api_key='your_api_key')

# Send chat message
response = client.chat.send_message(
    message="I need to book a train ticket",
    customer_id="CUS001"
)

# Search tickets
tickets = client.tickets.search(
    from_station="London Euston",
    to_station="Manchester Piccadilly",
    date="2024-03-15"
)

# Create booking
booking = client.bookings.create(
    customer_id="CUS001",
    ticket_id="TKT001",
    payment_method="card"
)
```

### JavaScript SDK
```javascript
import UKConnect from '@ukconnect/sdk';

const client = new UKConnect({
    apiKey: 'your_api_key',
    baseURL: 'https://api.ukconnect.com/v1'
});

// Send chat message
const response = await client.chat.sendMessage({
    message: "I need to book a train ticket",
    customerId: "CUS001"
});

// Search tickets
const tickets = await client.tickets.search({
    from: "London Euston",
    to: "Manchester Piccadilly", 
    date: "2024-03-15"
});
```

## ⚡ Rate Limiting

### Rate Limits
- **Chat API**: 100 requests per minute per API key
- **Booking API**: 50 requests per minute per API key
- **Analytics API**: 20 requests per minute per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## ❌ Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": {
      "field": "departure_date",
      "issue": "Date must be in the future"
    },
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_FAILED` (401)
- `INSUFFICIENT_PERMISSIONS` (403)
- `RESOURCE_NOT_FOUND` (404)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_SERVER_ERROR` (500)

## 🔧 Environment URLs

### Development
```
Base URL: https://dev-api.ukconnect.com/v1
WebSocket: wss://dev-api.ukconnect.com/v1/chat/ws
```

### Production
```
Base URL: https://api.ukconnect.com/v1
WebSocket: wss://api.ukconnect.com/v1/chat/ws
```

This API reference provides comprehensive integration guidance for the UKConnect AI Customer Support system.