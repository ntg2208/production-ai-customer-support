#!/usr/bin/env python3
"""
City-to-Station Mapping for UKConnect Rail
This module provides mapping between city names and station names to enable
flexible searches where users can specify cities instead of exact station names.
"""

# City to Station Mapping
CITY_STATION_MAP = {
    # London - Multiple stations
    "london": [
        "London Euston",
        "London King's Cross", 
        "London Paddington",
        "London Victoria",
        "London St Pancras",
        "London Marylebone",
        "London Waterloo"
    ],
    
    # Major Cities - Primary stations
    "manchester": ["Manchester Piccadilly"],
    "birmingham": ["Birmingham New Street"],
    "edinburgh": ["Edinburgh Waverley"],
    "glasgow": ["Glasgow Central"],
    "liverpool": ["Liverpool Lime Street"],
    "leeds": ["Leeds"],
    "cardiff": ["Cardiff Central"],
    "bristol": ["Bristol Temple Meads"],
    "newcastle": ["Newcastle Central"],
    "sheffield": ["Sheffield"],
    "york": ["York"],
    "oxford": ["Oxford"],
    "cambridge": ["Cambridge"],
    "brighton": ["Brighton"],
    "bath": ["Bath Spa"],
    "exeter": ["Exeter St Davids"],
    "portsmouth": ["Portsmouth Harbour"],
    "canterbury": ["Canterbury West"],
    "dover": ["Dover Priory"],
    "hull": ["Hull"],
    "coventry": ["Coventry"],
    "leicester": ["Leicester"],
    "nottingham": ["Nottingham"],
    "derby": ["Derby"],
    "aberdeen": ["Aberdeen"],
    "stirling": ["Stirling"],
    "swansea": ["Swansea"],
    "warwick": ["Warwick"],
    
    # Special mappings
    "gatwick": ["Gatwick Airport"],
    "airport": ["Gatwick Airport"]
}

# Station to City reverse mapping for easy lookup
STATION_CITY_MAP = {}
for city, stations in CITY_STATION_MAP.items():
    for station in stations:
        STATION_CITY_MAP[station.lower()] = city

def get_stations_by_city(city_name: str) -> list:
    """
    Get all stations for a given city name
    
    Args:
        city_name (str): City name (case insensitive)
        
    Returns:
        list: List of station names in the city, or empty list if not found
        
    Example:
        stations = get_stations_by_city("london")
        # Returns: ['London Euston', 'London King\'s Cross', ...]
    """
    if not city_name or not isinstance(city_name, str):
        return []
    
    city_key = city_name.lower().strip()
    return CITY_STATION_MAP.get(city_key, [])

def get_city_by_station(station_name: str) -> str:
    """
    Get city name for a given station name
    
    Args:
        station_name (str): Station name (case insensitive)
        
    Returns:
        str: City name, or empty string if not found
        
    Example:
        city = get_city_by_station("London Euston")
        # Returns: "london"
    """
    if not station_name or not isinstance(station_name, str):
        return ""
    
    station_key = station_name.lower().strip()
    return STATION_CITY_MAP.get(station_key, "")

def normalize_location_input(location_input: str) -> dict:
    """
    Normalize location input to determine if it's a city or station
    and return appropriate station list
    
    Args:
        location_input (str): User input for location (city or station name)
        
    Returns:
        dict: {
            "input_type": "city" | "station" | "unknown",
            "stations": [list of station names],
            "city": city name if applicable,
            "original_input": original input
        }
        
    Example:
        result = normalize_location_input("london")
        # Returns: {
        #     "input_type": "city",
        #     "stations": ["London Euston", "London King's Cross", ...],
        #     "city": "london",
        #     "original_input": "london"
        # }
    """
    if not location_input or not isinstance(location_input, str):
        return {
            "input_type": "unknown",
            "stations": [],
            "city": "",
            "original_input": location_input
        }
    
    normalized_input = location_input.lower().strip()
    
    # Check if it's a city name
    if normalized_input in CITY_STATION_MAP:
        return {
            "input_type": "city",
            "stations": CITY_STATION_MAP[normalized_input],
            "city": normalized_input,
            "original_input": location_input
        }
    
    # Check if it's a station name
    if normalized_input in STATION_CITY_MAP:
        # Find the exact station name from our mapping
        for station in STATION_CITY_MAP.keys():
            if station == normalized_input:
                # Get the properly formatted station name
                for city, stations in CITY_STATION_MAP.items():
                    for proper_station in stations:
                        if proper_station.lower() == normalized_input:
                            return {
                                "input_type": "station",
                                "stations": [proper_station],
                                "city": city,
                                "original_input": location_input
                            }
    
    # Try partial matching for station names
    for station in STATION_CITY_MAP.keys():
        if normalized_input in station or station in normalized_input:
            for city, stations in CITY_STATION_MAP.items():
                for proper_station in stations:
                    if proper_station.lower() == station:
                        return {
                            "input_type": "station",
                            "stations": [proper_station],
                            "city": city,
                            "original_input": location_input
                        }
    
    return {
        "input_type": "unknown",
        "stations": [],
        "city": "",
        "original_input": location_input
    }

def get_all_supported_cities() -> list:
    """
    Get list of all supported cities
    
    Returns:
        list: List of supported city names
    """
    return list(CITY_STATION_MAP.keys())

def get_all_supported_stations() -> list:
    """
    Get list of all supported stations
    
    Returns:
        list: List of all supported station names
    """
    all_stations = []
    for stations in CITY_STATION_MAP.values():
        all_stations.extend(stations)
    return sorted(all_stations)

def search_cities_and_stations(query: str) -> dict:
    """
    Search for cities and stations matching a query
    
    Args:
        query (str): Search query
        
    Returns:
        dict: {
            "cities": [list of matching cities],
            "stations": [list of matching stations],
            "suggestions": [list of suggestions]
        }
    """
    if not query or not isinstance(query, str):
        return {"cities": [], "stations": [], "suggestions": []}
    
    query_lower = query.lower().strip()
    matching_cities = []
    matching_stations = []
    suggestions = []
    
    # Search cities
    for city in CITY_STATION_MAP.keys():
        if query_lower in city:
            matching_cities.append(city)
            suggestions.extend(CITY_STATION_MAP[city])
    
    # Search stations
    for station in STATION_CITY_MAP.keys():
        if query_lower in station:
            # Get the properly formatted station name
            for city, stations in CITY_STATION_MAP.items():
                for proper_station in stations:
                    if proper_station.lower() == station:
                        matching_stations.append(proper_station)
                        break
    
    return {
        "cities": matching_cities,
        "stations": matching_stations,
        "suggestions": list(set(suggestions))  # Remove duplicates
    }

# Test functions
def test_city_mapping():
    """Test the city mapping functions"""
    print("=" * 60)
    print("Testing City-Station Mapping")
    print("=" * 60)
    
    # Test city to stations
    print("\n1. Testing get_stations_by_city:")
    cities_to_test = ["london", "manchester", "birmingham", "invalid_city"]
    for city in cities_to_test:
        stations = get_stations_by_city(city)
        print(f"  {city}: {stations}")
    
    # Test station to city
    print("\n2. Testing get_city_by_station:")
    stations_to_test = ["London Euston", "Manchester Piccadilly", "Invalid Station"]
    for station in stations_to_test:
        city = get_city_by_station(station)
        print(f"  {station}: {city}")
    
    # Test normalize input
    print("\n3. Testing normalize_location_input:")
    inputs_to_test = ["london", "London Euston", "manchester", "Invalid Location"]
    for input_str in inputs_to_test:
        result = normalize_location_input(input_str)
        print(f"  {input_str}: {result}")
    
    # Test search
    print("\n4. Testing search_cities_and_stations:")
    queries = ["lon", "man", "king", "invalid"]
    for query in queries:
        result = search_cities_and_stations(query)
        print(f"  {query}: {result}")
    
    print("\n" + "=" * 60)
    print("City Mapping Tests Completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_city_mapping()