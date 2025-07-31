#!/usr/bin/env python3
"""
Location Intelligence for UKConnect Rail System
Maps customer addresses to nearest major rail stations for contextual booking.
"""

import re
from typing import Dict, Tuple, Optional

# Major UK rail stations mapping
STATION_MAPPING = {
    # London stations - map to specific stations based on area
    'london': {
        'default': 'London Euston',
        'areas': {
            # Central/West London → Euston
            'baker street': 'London Euston',
            'marylebone': 'London Euston', 
            'euston': 'London Euston',
            'regent street': 'London Euston',
            'oxford street': 'London Euston',
            'bloomsbury': 'London Euston',
            'fitzrovia': 'London Euston',
            'gower street': 'London Euston',
            
            # North/East London → King's Cross
            "king's cross": "London King's Cross",
            'camden': "London King's Cross",
            'islington': "London King's Cross",
            'hackney': "London King's Cross",
            
            # City/Financial → King's Cross (business travelers)
            'city of london': "London King's Cross",
            'fleet street': "London King's Cross",
            'queen victoria street': "London King's Cross",
            'canary wharf': "London King's Cross",
            'ec1': "London King's Cross",
            'ec2': "London King's Cross",
            'ec3': "London King's Cross",
            'ec4': "London King's Cross",
            'e14': "London King's Cross",
            
            # West London → Paddington
            'paddington': 'London Paddington',
            'bayswater': 'London Paddington',
            'notting hill': 'London Paddington',
            'hyde park': 'London Paddington',
            
            # South London → Waterloo
            'waterloo': 'London Waterloo',
            'south bank': 'London Waterloo',
            'lambeth': 'London Waterloo',
            'southwark': 'London Waterloo'
        }
    },
    
    # Other major cities - single station mapping
    'manchester': 'Manchester Piccadilly',
    'birmingham': 'Birmingham New Street', 
    'edinburgh': 'Edinburgh Waverley',
    'glasgow': 'Glasgow Central',
    'liverpool': 'Liverpool Lime Street',
    'leeds': 'Leeds Station',
    'bristol': 'Bristol Temple Meads',
    'cardiff': 'Cardiff Central',
    'newcastle': 'Newcastle Central',
    'sheffield': 'Sheffield Station',
    'nottingham': 'Nottingham Station',
    'leicester': 'Leicester Station',
    'coventry': 'Coventry Station',
    'oxford': 'Oxford Station',
    'cambridge': 'Cambridge Station',
    'bath': 'Bath Spa',
    'york': 'York Station',
    'chester': 'Chester Station',
    'preston': 'Preston Station',
    'derby': 'Derby Station',
    'stoke-on-trent': 'Stoke-on-Trent Station',
    'wolverhampton': 'Wolverhampton Station',
    'reading': 'Reading Station',
    'brighton': 'Brighton Station',
    'exeter': 'Exeter St Davids',
    'plymouth': 'Plymouth Station',
    'portsmouth': 'Portsmouth & Southsea',
    'southampton': 'Southampton Central',
    'bournemouth': 'Bournemouth Station',
    'swindon': 'Swindon Station',
    'gloucester': 'Gloucester Station',
    'worcester': 'Worcester Foregate Street',
    'hereford': 'Hereford Station',
    'shrewsbury': 'Shrewsbury Station',
    'chester': 'Chester Station',
    'bangor': 'Bangor Station',
    'swansea': 'Swansea Station',
    'newport': 'Newport Station',
    'aberdeen': 'Aberdeen Station',
    'dundee': 'Dundee Station',
    'stirling': 'Stirling Station',
    'perth': 'Perth Station',
    'inverness': 'Inverness Station',
    'fort william': 'Fort William Station'
}

def extract_city_from_address(address: str) -> Optional[str]:
    """
    Extract city name from UK address.
    
    Args:
        address (str): Full UK address
        
    Returns:
        str: City name or None if not found
    """
    address_lower = address.lower()
    
    # Check for London postcodes first (WC, EC, E14, etc.)
    if re.search(r'\b(w[0-9]|wc[0-9]|ec[0-9]|e[0-9]|sw[0-9]|se[0-9]|n[0-9]|nw[0-9])', address_lower):
        return 'london'
    
    # Check for explicit "London" mention
    if 'london' in address_lower:
        return 'london'
    
    # Check for other cities in the address
    for city in STATION_MAPPING.keys():
        if city != 'london' and city in address_lower:
            return city
    
    # Common city variations
    city_variations = {
        'birmingham': ['bham', 'birm'],
        'edinburgh': ['edinburgh', 'edi'],
        'glasgow': ['glasgow', 'glas'],
        'manchester': ['manchester', 'manc'],
        'liverpool': ['liverpool', 'pool']
    }
    
    for standard_city, variations in city_variations.items():
        for variation in variations:
            if variation in address_lower:
                return standard_city
    
    return None

def get_london_station_from_address(address: str) -> str:
    """
    Determine specific London station based on address area.
    
    Args:
        address (str): London address
        
    Returns:
        str: Specific London station name
    """
    address_lower = address.lower()
    london_config = STATION_MAPPING['london']
    
    # Check specific area mappings
    for area, station in london_config['areas'].items():
        if area in address_lower:
            return station
    
    # Check postcode patterns for business vs residential areas
    if re.search(r'\bec[0-9]', address_lower) or 'canary wharf' in address_lower:
        return "London King's Cross"  # Business areas
    elif re.search(r'\bw[0-9]', address_lower):
        return 'London Paddington'  # West London
    elif re.search(r'\bse[0-9]|sw[0-9]', address_lower):
        return 'London Waterloo'  # South London
    
    # Default to Euston for central/unspecified London
    return london_config['default']

def map_address_to_station(address: str) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Map a customer address to their nearest major rail station.
    
    Args:  
        address (str): Customer's full address
        
    Returns:
        Tuple[Optional[str], Dict[str, str]]: (station_name, context_info)
    """
    if not address:
        return None, {'error': 'No address provided'}
    
    city = extract_city_from_address(address)
    if not city:
        return None, {'error': 'Could not determine city from address', 'address': address}
    
    # Handle London's multiple stations
    if city == 'london':
        station = get_london_station_from_address(address)
        context = {
            'city': 'London',
            'station': station,
            'area': _extract_london_area(address),
            'is_business_area': "King's Cross" in station or 'canary wharf' in address.lower()
        }
    else:
        station = STATION_MAPPING.get(city)
        if not station:
            return None, {'error': f'No station mapping found for city: {city}'}
        
        context = {
            'city': city.title(),
            'station': station,
            'area': city.title(),
            'is_business_area': False
        }
    
    return station, context

def _extract_london_area(address: str) -> str:
    """Extract London area name from address."""
    address_lower = address.lower()
    
    # Common London areas
    areas = ['baker street', 'canary wharf', 'fleet street', 'gower street', 
             'regent street', 'oxford street', "king's cross", 'paddington']
    
    for area in areas:
        if area in address_lower:
            return area.title()
    
    # Extract postcode area
    postcode_match = re.search(r'\b([A-Z]{1,2}[0-9]{1,2}[A-Z]?)\s*[0-9][A-Z]{2}\b', address, re.IGNORECASE)
    if postcode_match:
        return postcode_match.group(1)
    
    return 'Central London'

def get_customer_location_context(customer_data: Dict) -> Dict[str, str]:
    """
    Generate location context for a customer based on their database record.
    
    Args:
        customer_data (Dict): Customer record from database
        
    Returns:
        Dict[str, str]: Location context information
    """
    address = customer_data.get('address', '')
    name = customer_data.get('name', 'Customer')
    email = customer_data.get('email', '')
    
    station, context = map_address_to_station(address)
    
    if station:
        return {
            'name': name,
            'email': email,
            'home_address': address,
            'default_departure_station': station,
            'location_city': context['city'],
            'location_area': context['area'],
            'is_business_traveler': context.get('is_business_area', False),
            'travel_context': f"Customer based in {context['city']}, typically travels from {station}",
            'location_assumption': f"When customer mentions only destinations, assume departure from {station}"
        }
    else:
        return {
            'name': name,
            'email': email,
            'home_address': address,
            'error': context.get('error', 'Location mapping failed'),
            'travel_context': 'Location context unavailable',
            'location_assumption': 'Ask customer for departure station'
        }

# Test function for development
def test_location_mapping():
    """Test the location mapping with sample addresses."""
    test_addresses = [
        "12 Gower Street, London WC1E 6BT",  # London (university area) → Euston
        "45 Canary Wharf, London E14 5AB",   # London (business) → King's Cross
        "23 Broad Street, Birmingham B1 2HF", # Birmingham → New Street
        "67 Fleet Street, London EC4Y 1HT",   # London (City) → King's Cross
        "89 University Avenue, Glasgow G12 8QQ" # Glasgow → Central
    ]
    
    for address in test_addresses:
        station, context = map_address_to_station(address)
        print(f"Address: {address}")
        print(f"Station: {station}")
        print(f"Context: {context}")
        print("-" * 50)

if __name__ == "__main__":
    test_location_mapping()