# Tutorial 6: Location Intelligence (15 min)

## 🎯 Overview
Implement location intelligence to automatically detect customer departure stations and provide context-aware booking recommendations.

## 🗺️ What You'll Learn
- Customer address mapping to train stations
- Smart default detection
- Context-aware booking assistance
- Location-based personalization

## 🏗️ Location Intelligence System

```
Customer Address → Location Mapping → Nearest Station → Smart Defaults
      ↓                    ↓                ↓              ↓
[Address Parser]    [Station Database]  [Distance Calc]  [Booking Context]
```

## 🔧 Implementation

### Location Mapping
```python
# utils/location_intelligence.py
STATION_MAPPINGS = {
    "London": ["London Euston", "London King's Cross", "London Paddington"],
    "Birmingham": ["Birmingham New Street"],
    "Manchester": ["Manchester Piccadilly"],
    "Glasgow": ["Glasgow Central"]
}

def detect_departure_station(customer_address):
    # Extract city from address
    city = extract_city(customer_address)
    
    # Find nearest major station
    return get_primary_station(city)
```

### Smart Booking Context
```python
def enhance_booking_query(query, customer_context):
    if "from" not in query.lower():
        # Add inferred departure station
        departure = detect_departure_station(customer_context["address"])
        enhanced_query = f"Travel from {departure}: {query}"
        return enhanced_query
    return query
```

## 🎯 Use Cases

1. **Minimal Queries**: "need train to manchester tomorrow" → "from London Euston to Manchester"
2. **Smart Defaults**: Auto-fill departure station based on customer location
3. **Route Suggestions**: Recommend optimal connections based on location
4. **Local Services**: Highlight nearby station amenities

## 🧪 Testing

```bash
# Test location intelligence with casual queries
python run_test_scenarios.py --session 11  # London-based customer
python run_test_scenarios.py --session 13  # Birmingham-based customer
```

## 🚀 Next Steps
**Tutorial 7**: Testing & deployment strategies for production readiness.