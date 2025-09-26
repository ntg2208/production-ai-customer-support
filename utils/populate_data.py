#!/usr/bin/env python3
"""
UKConnect Rail Database Data Population v2.0
This script populates the enhanced database with comprehensive sample data including available tickets inventory.
"""

import sqlite3
import sys
from datetime import datetime, timedelta
import random
import json

# Set random seed for consistent test data
random.seed(42)

# Deterministic data generation helpers
def get_deterministic_carriage(ticket_id):
    """Get deterministic carriage based on ticket ID"""
    carriages = ['1', '2', '3', '4']
    return carriages[ticket_id % len(carriages)]

def get_deterministic_seat(ticket_id):
    """Get deterministic seat based on ticket ID"""
    seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    seat_number = (ticket_id % 30) + 1
    seat_letter = seat_letters[ticket_id % len(seat_letters)]
    return f"{seat_number:02d}{seat_letter}"

def get_deterministic_ticket_type(ticket_id, available_types):
    """Get deterministic ticket type based on ticket ID"""
    return available_types[ticket_id % len(available_types)]

def get_deterministic_payment_method(customer_id):
    """Get deterministic payment method based on customer ID"""
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay']
    return payment_methods[customer_id % len(payment_methods)]

def get_deterministic_boolean(seed_value, option='table'):
    """Get deterministic boolean based on seed value"""
    # Different offsets for different options to avoid same pattern
    offsets = {'table': 0, 'window_seat': 1, 'quiet_zone': 2}
    offset = offsets.get(option, 0)
    return ((seed_value + offset) % 3) != 0  # 2/3 chance of True

# Import centralized time configuration
try:
    from ..config.time_config import get_system_time_iso
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
    from time_config import get_system_time_iso

def populate_data(db_path=None):
    """Populate the enhanced database. If no path provided, uses the default database location."""
    if db_path is None:
        import os
        # Default to the database directory relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, '..', 'database', 'ukconnect_rail.db')
        db_path = os.path.abspath(db_path)
    """
    Populate the enhanced database with comprehensive sample data.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Populating UKConnect Rail database v2.0 with sample data...")
        print(f"Database path: {db_path}")
        
        # Clear existing data (for fresh start)
        print("\n🧹 Clearing existing data...")
        cursor.execute("DELETE FROM booking_history")
        cursor.execute("DELETE FROM transaction_info")
        cursor.execute("DELETE FROM booked_tickets")
        cursor.execute("DELETE FROM available_tickets")
        cursor.execute("DELETE FROM train_schedules")
        cursor.execute("DELETE FROM customer_info")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('customer_info', 'available_tickets', 'booked_tickets', 'transaction_info', 'train_schedules', 'booking_history')")
        
        # Insert Customer Data (55 customers including casual test users)
        print("👥 Inserting customer data...")
        
        customers = [
            (1, 'CUS001', 'James Thompson', '42 Baker Street, London W1U 6TQ', 'james.thompson@email.co.uk', '+44 20 7946 0101'),
            (2, 'CUS002', 'Sarah Williams', '15 High Street, Manchester M1 1FB', 'sarah.williams@email.co.uk', '+44 161 234 5678'),
            (3, 'CUS003', 'Michael Davies', '78 Corporation Street, Birmingham B2 4QZ', 'michael.davies@email.co.uk', '+44 121 345 6789'),
            (4, 'CUS004', 'Emily Johnson', '123 Princes Street, Edinburgh EH2 4AD', 'emily.johnson@email.co.uk', '+44 131 456 7890'),
            (5, 'CUS005', 'Robert Brown', '56 Bold Street, Liverpool L1 4DS', 'robert.brown@email.co.uk', '+44 151 567 8901'),
            (6, 'CUS006', 'Lisa Wilson', '89 Park Row, Leeds LS1 5HD', 'lisa.wilson@email.co.uk', '+44 113 678 9012'),
            (7, 'CUS007', 'David Evans', '34 Queen Street, Cardiff CF10 2BX', 'david.evans@email.co.uk', '+44 29 2345 6789'),
            (8, 'CUS008', 'Jennifer Smith', '67 Union Street, Glasgow G1 3RB', 'jennifer.smith@email.co.uk', '+44 141 234 5678'),
            (9, 'CUS009', 'Christopher Jones', '91 North Street, Brighton BN1 1ZA', 'chris.jones@email.co.uk', '+44 1273 345 678'),
            (10, 'CUS010', 'Amanda Taylor', '12 King Street, Bristol BS1 4EF', 'amanda.taylor@email.co.uk', '+44 117 456 7890'),
            (11, 'CUS011', 'Oliver Harris', '23 Victoria Road, Newcastle NE1 5DX', 'oliver.harris@email.co.uk', '+44 191 234 5678'),
            (12, 'CUS012', 'Sophie Clark', '67 Castle Street, Liverpool L2 7LJ', 'sophie.clark@email.co.uk', '+44 151 345 6789'),
            (13, 'CUS013', 'Daniel Wright', '89 George Street, Oxford OX1 2BJ', 'daniel.wright@email.co.uk', '+44 1865 234 567'),
            (14, 'CUS014', 'Emma Turner', '45 Royal Mile, Edinburgh EH1 1RE', 'emma.turner@email.co.uk', '+44 131 567 8901'),
            (15, 'CUS015', 'Thomas Moore', '156 Deansgate, Manchester M3 3FE', 'thomas.moore@email.co.uk', '+44 161 678 9012'),
            (16, 'CUS016', 'Charlotte White', '34 Regent Street, Cambridge CB2 1DP', 'charlotte.white@email.co.uk', '+44 1223 345 678'),
            (17, 'CUS017', 'Jack Robinson', '78 Queen Victoria Street, London EC4V 4EJ', 'jack.robinson@email.co.uk', '+44 20 7123 4567'),
            (18, 'CUS018', 'Grace Martin', '92 High Street, Bath BA1 5AQ', 'grace.martin@email.co.uk', '+44 1225 567 890'),
            (19, 'CUS019', 'Henry Lee', '15 Buchanan Street, Glasgow G1 2FF', 'henry.lee@email.co.uk', '+44 141 456 7890'),
            (20, 'CUS020', 'Chloe Hall', '203 Corporation Street, Birmingham B4 6QD', 'chloe.hall@email.co.uk', '+44 121 789 0123'),
            (21, 'CUS021', 'William Green', '67 North Street, York YO1 6JD', 'william.green@email.co.uk', '+44 1904 234 567'),
            (22, 'CUS022', 'Mia Adams', '134 Market Street, Sheffield S1 2GH', 'mia.adams@email.co.uk', '+44 114 345 6789'),
            (23, 'CUS023', 'George Baker', '56 High Street, Exeter EX4 3LS', 'george.baker@email.co.uk', '+44 1392 456 789'),
            (24, 'CUS024', 'Isla Mitchell', '89 Union Street, Aberdeen AB11 6BD', 'isla.mitchell@email.co.uk', '+44 1224 567 890'),
            (25, 'CUS025', 'Noah Campbell', '23 Mill Lane, Canterbury CT1 2SX', 'noah.campbell@email.co.uk', '+44 1227 678 901'),
            (26, 'CUS026', 'Poppy Scott', '45 Church Street, Brighton BN1 1UE', 'poppy.scott@email.co.uk', '+44 1273 789 012'),
            (27, 'CUS027', 'Jacob Murphy', '178 High Street, Coventry CV1 1NP', 'jacob.murphy@email.co.uk', '+44 24 7890 1234'),
            (28, 'CUS028', 'Evie Roberts', '67 King Street, Leicester LE1 6RN', 'evie.roberts@email.co.uk', '+44 116 901 2345'),
            (29, 'CUS029', 'Lucas Thompson', '234 London Road, Portsmouth PO2 0LN', 'lucas.thompson@email.co.uk', '+44 23 9012 3456'),
            (30, 'CUS030', 'Ruby Phillips', '89 High Street, Nottingham NG1 5FS', 'ruby.phillips@email.co.uk', '+44 115 123 4567'),
            (31, 'CUS031', 'Mason Evans', '145 Princes Street, Stirling FK8 1HQ', 'mason.evans@email.co.uk', '+44 1786 234 567'),
            (32, 'CUS032', 'Lily Cooper', '56 Castle Street, Swansea SA1 1JF', 'lily.cooper@email.co.uk', '+44 1792 345 678'),
            (33, 'CUS033', 'Sebastian Ward', '78 Victoria Street, Derby DE1 1EE', 'sebastian.ward@email.co.uk', '+44 1332 456 789'),
            (34, 'CUS034', 'Freya Hughes', '23 George Street, Hull HU1 3BH', 'freya.hughes@email.co.uk', '+44 1482 567 890'),
            (35, 'CUS035', 'Leo Price', '67 Market Square, Warwick CV34 4SA', 'leo.price@email.co.uk', '+44 1926 678 901'),
            (36, 'CUS036', 'Ava Johnson', '12 High Street, Preston PR1 2QP', 'ava.johnson@email.co.uk', '+44 1772 234 567'),
            (37, 'CUS037', 'Ethan Wilson', '89 King Street, Stoke-on-Trent ST1 1HZ', 'ethan.wilson@email.co.uk', '+44 1782 345 678'),
            (38, 'CUS038', 'Isabella Davis', '45 Market Street, Blackpool FY1 1HJ', 'isabella.davis@email.co.uk', '+44 1253 456 789'),
            (39, 'CUS039', 'Alfie Brown', '67 Church Street, Carlisle CA1 1QS', 'alfie.brown@email.co.uk', '+44 1228 567 890'),
            (40, 'CUS040', 'Amelia Jones', '23 High Street, Truro TR1 2LL', 'amelia.jones@email.co.uk', '+44 1872 678 901'),
            (41, 'CUS041', 'Oscar Miller', '89 Castle Street, Inverness IV1 1EJ', 'oscar.miller@email.co.uk', '+44 1463 789 012'),
            (42, 'CUS042', 'Scarlett Garcia', '34 Queen Street, Dundee DD1 3BG', 'scarlett.garcia@email.co.uk', '+44 1382 890 123'),
            (43, 'CUS043', 'Harry Rodriguez', '56 Market Place, Durham DH1 3NJ', 'harry.rodriguez@email.co.uk', '+44 191 901 234'),
            (44, 'CUS044', 'Emily Martinez', '78 High Street, Worcester WR1 2QQ', 'emily.martinez@email.co.uk', '+44 1905 012 345'),
            (45, 'CUS045', 'Charlie Anderson', '12 King Street, Gloucester GL1 1QR', 'charlie.anderson@email.co.uk', '+44 1452 123 456'),
            (46, 'CUS046', 'Sophie Taylor', '89 Castle Street, Chester CH1 2DS', 'sophie.taylor@email.co.uk', '+44 1244 234 567'),
            (47, 'CUS047', 'Archie Thomas', '45 High Street, Salisbury SP1 1TB', 'archie.thomas@email.co.uk', '+44 1722 345 678'),
            (48, 'CUS048', 'Grace Jackson', '67 Market Street, Winchester SO23 9EX', 'grace.jackson@email.co.uk', '+44 1962 456 789'),
            (49, 'CUS049', 'George White', '23 Queen Street, Hereford HR1 2PJ', 'george.white@email.co.uk', '+44 1432 567 890'),
            (50, 'CUS050', 'Ella Harris', '89 King Street, Bangor LL57 1UP', 'ella.harris@email.co.uk', '+44 1248 678 901'),
            
            # Additional customers for casual test sessions (CUS051-CUS055)
            (51, 'CUS051', 'Alex Smith', '12 Gower Street, London WC1E 6BT', 'alex.smith@student.ac.uk', '+44 20 7679 2000'),
            (52, 'CUS052', 'Jordan Wilson', '45 Canary Wharf, London E14 5AB', 'jordan.wilson@company.co.uk', '+44 20 7418 2000'),
            (53, 'CUS053', 'Casey Brown', '23 Broad Street, Birmingham B1 2HF', 'casey.brown@email.co.uk', '+44 121 248 2000'),
            (54, 'CUS054', 'Sam Taylor', '67 Fleet Street, London EC4Y 1HT', 'sam.taylor@emergency.co.uk', '+44 20 7353 2000'),
            (55, 'CUS055', 'Riley Jones', '89 University Avenue, Glasgow G12 8QQ', 'riley.jones@student.ac.uk', '+44 141 330 2000')
        ]
        
        cursor.executemany('''
        INSERT INTO customer_info (id, customer_id, name, address, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', customers)
        
        # Insert Train Schedules (base services)
        print("🚂 Inserting train schedules...")
        
        train_schedules = [
            # London to Manchester route
            ('UK101', 'London to Manchester Express', 'Virgin Trains', 'London Euston', 'Manchester Piccadilly', '09:30', '11:38', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK102', 'London to Manchester Express', 'Virgin Trains', 'London Euston', 'Manchester Piccadilly', '11:30', '13:38', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK103', 'London to Manchester Express', 'Virgin Trains', 'London Euston', 'Manchester Piccadilly', '13:30', '15:38', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Manchester to London route
            ('UK201', 'Manchester to London Express', 'Virgin Trains', 'Manchester Piccadilly', 'London Euston', '08:15', '10:23', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK202', 'Manchester to London Express', 'Virgin Trains', 'Manchester Piccadilly', 'London Euston', '10:15', '12:23', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # London to Birmingham route
            ('UK301', 'London to Birmingham Service', 'CrossCountry', 'London Euston', 'Birmingham New Street', '08:00', '09:23', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK302', 'London to Birmingham Service', 'CrossCountry', 'London Euston', 'Birmingham New Street', '09:00', '10:23', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Birmingham to London route
            ('UK401', 'Birmingham to London Service', 'CrossCountry', 'Birmingham New Street', 'London Euston', '07:30', '08:53', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK402', 'Birmingham to London Service', 'CrossCountry', 'Birmingham New Street', 'London Euston', '08:30', '09:53', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # London to Edinburgh route
            ('UK501', 'London to Edinburgh Service', 'LNER', 'London King\'s Cross', 'Edinburgh Waverley', '06:00', '10:28', 268, 630, 'Daily', 'Every 30 minutes', 450, 60, 390, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK502', 'London to Edinburgh Service', 'LNER', 'London King\'s Cross', 'Edinburgh Waverley', '07:00', '11:28', 268, 630, 'Daily', 'Every 30 minutes', 450, 60, 390, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Edinburgh to London route
            ('UK601', 'Edinburgh to London Service', 'LNER', 'Edinburgh Waverley', 'London King\'s Cross', '08:00', '12:28', 268, 630, 'Daily', 'Every 30 minutes', 450, 60, 390, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            ('UK602', 'Edinburgh to London Service', 'LNER', 'Edinburgh Waverley', 'London King\'s Cross', '09:00', '13:28', 268, 630, 'Daily', 'Every 30 minutes', 450, 60, 390, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Regional routes
            ('UK701', 'Liverpool to Manchester Service', 'Northern Rail', 'Liverpool Lime Street', 'Manchester Piccadilly', '08:00', '08:47', 47, 55, 'Daily', 'Every 30 minutes', 200, 0, 200, 1, 0, 1, '{"wheelchair_access": true}', 'active'),
            ('UK801', 'Glasgow to Edinburgh Service', 'ScotRail', 'Glasgow Central', 'Edinburgh Waverley', '08:00', '08:55', 55, 75, 'Daily', 'Every 15 minutes', 300, 20, 280, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active')
        ]
        
        cursor.executemany('''
        INSERT INTO train_schedules (train_number, service_name, operator, from_station, to_station, 
                                   departure_time, arrival_time, journey_duration, distance_km, 
                                   operating_days, service_frequency, max_capacity, first_class_capacity, 
                                   standard_class_capacity, has_wifi, has_catering, has_power_sockets, 
                                   accessibility_features, service_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', train_schedules)
        
        # Insert Available Tickets (100 tickets)
        print("🎫 Inserting available tickets inventory...")
        
        available_tickets = []
        ticket_id = 1
        
        # Define routes with pricing (aligned with company policy ticket types)
        # Policy ticket types: Flexible, Standard, First Class
        routes = [
            ('London Euston', 'Manchester Piccadilly', ['UK101', 'UK102', 'UK103'], 320, {'standard': 67.5, 'flexible': 89.0, 'first_class': 125.0}),
            ('Manchester Piccadilly', 'London Euston', ['UK201', 'UK202'], 320, {'standard': 67.5, 'flexible': 89.0, 'first_class': 125.0}),
            ('London Euston', 'Birmingham New Street', ['UK301', 'UK302'], 190, {'standard': 52.5, 'flexible': 70.0, 'first_class': 95.0}),
            ('Birmingham New Street', 'London Euston', ['UK401', 'UK402'], 190, {'standard': 52.5, 'flexible': 70.0, 'first_class': 95.0}),
            ('London King\'s Cross', 'Edinburgh Waverley', ['UK501', 'UK502'], 630, {'standard': 98.0, 'flexible': 130.0, 'first_class': 185.0}),
            ('Edinburgh Waverley', 'London King\'s Cross', ['UK601', 'UK602'], 630, {'standard': 98.0, 'flexible': 130.0, 'first_class': 185.0}),
            ('Liverpool Lime Street', 'Manchester Piccadilly', ['UK701'], 55, {'standard': 25.0, 'flexible': 35.0}),
            ('Glasgow Central', 'Edinburgh Waverley', ['UK801'], 75, {'standard': 18.5, 'flexible': 28.0, 'first_class': 45.0})
        ]
        
        # Generate dates for next 30 days (starting tomorrow to ensure future departures)
        current_system_time = datetime.fromisoformat(get_system_time_iso())
        base_date = current_system_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)  # Start from tomorrow to ensure future bookings
        
        for day_offset in range(30):
            current_date = base_date + timedelta(days=day_offset)
            
            for from_station, to_station, train_numbers, distance, prices in routes:
                for train_number in train_numbers:
                    # Get departure time from train schedules
                    cursor.execute("SELECT departure_time, arrival_time FROM train_schedules WHERE train_number = ?", (train_number,))
                    schedule = cursor.fetchone()
                    if not schedule:
                        continue
                    
                    dep_time_str, arr_time_str = schedule
                    dep_time = datetime.strptime(f"{current_date.strftime('%Y-%m-%d')} {dep_time_str}", '%Y-%m-%d %H:%M')
                    arr_time = datetime.strptime(f"{current_date.strftime('%Y-%m-%d')} {arr_time_str}", '%Y-%m-%d %H:%M')
                    
                    # If arrival is next day, adjust
                    if arr_time < dep_time:
                        arr_time += timedelta(days=1)
                    
                    # Generate tickets for this service (limited to reach ~100 total)
                    if ticket_id > 100:
                        break
                    
                    # Create 1-2 tickets per service to stay around 100 total
                    tickets_per_service = min(2, 101 - ticket_id)
                    
                    for i in range(tickets_per_service):
                        if ticket_id > 100:
                            break
                            
                        # Deterministic seat assignment based on ticket ID
                        carriage = get_deterministic_carriage(ticket_id)
                        seat_num = get_deterministic_seat(ticket_id)
                        
                        # Deterministic ticket type based on ticket ID
                        available_types = list(prices.keys())
                        ticket_type = get_deterministic_ticket_type(ticket_id, available_types)
                        
                        base_price = prices[ticket_type]
                        
                        # Dynamic pricing (peak times cost more)
                        if dep_time.hour in [7, 8, 9, 17, 18, 19]:  # Rush hours
                            current_price = base_price * 1.2
                        elif dep_time.weekday() >= 5:  # Weekends
                            current_price = base_price * 0.9
                        else:
                            current_price = base_price
                        
                        # Booking class mapping
                        booking_class = 'first_class' if ticket_type == 'first_class' else 'standard'
                        
                        # Deterministic amenities based on ticket ID
                        amenities = {
                            "wifi": True,
                            "power_socket": True,
                            "table": get_deterministic_boolean(ticket_id, 'table'),
                            "window_seat": get_deterministic_boolean(ticket_id, 'window_seat'),
                            "quiet_zone": get_deterministic_boolean(ticket_id, 'quiet_zone')
                        }
                        
                        available_tickets.append((
                            ticket_id,
                            train_number,
                            from_station,
                            to_station,
                            dep_time.strftime('%Y-%m-%d %H:%M:%S'),
                            arr_time.strftime('%Y-%m-%d %H:%M:%S'),
                            seat_num,
                            carriage,
                            ticket_type,
                            base_price,
                            round(current_price, 2),
                            'available',
                            booking_class,
                            json.dumps(amenities),
                            distance
                        ))
                        
                        ticket_id += 1
                
                if ticket_id > 100:
                    break
            
            if ticket_id > 100:
                break
        
        cursor.executemany('''
        INSERT INTO available_tickets (id, train_number, from_station, to_station, departure_time, 
                                     arrival_time, seat_number, carriage, ticket_type, base_price, 
                                     current_price, availability_status, booking_class, amenities, route_distance_km)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', available_tickets)
        
        print(f"   Generated {len(available_tickets)} available tickets")
        
        # Insert some Booked Tickets (20 booked from available inventory)
        print("📋 Inserting booked tickets...")
        
        # Book some of the available tickets
        cursor.execute("SELECT * FROM available_tickets WHERE id <= 20 ORDER BY id")
        tickets_to_book = cursor.fetchall()
        
        booked_tickets = []
        for i, ticket in enumerate(tickets_to_book, 1):
            customer_id = ((i - 1) % 55) + 1  # Distribute among all 55 customers
            booking_ref = f"UKC{i:03d}"
            
            # Update available ticket status to 'sold'
            cursor.execute("UPDATE available_tickets SET availability_status = 'sold' WHERE id = ?", (ticket[0],))
            
            # Create booking record
            booked_tickets.append((
                i,
                booking_ref,
                customer_id,
                ticket[0],  # original_available_ticket_id
                ticket[1],  # train_number
                ticket[2],  # from_station
                ticket[3],  # to_station
                ticket[4],  # departure_time
                ticket[5],  # arrival_time (estimated_arrival_time)
                ticket[6],  # seat_number
                ticket[7],  # carriage
                ticket[8],  # ticket_type
                ticket[9],  # base_price (original_price)
                ticket[10], # current_price (paid_price)
                'confirmed', # booking_status
                'upcoming', # travel_status
                (current_system_time - timedelta(days=(i % 10) + 1)).strftime('%Y-%m-%d %H:%M:%S'), # purchase_date
                None, # check_in_time
                None, # boarding_time
                None, # special_requirements
                None, # group_booking_id
                0,    # is_return_ticket
                None, # return_ticket_id
                5 + (i % 21), # loyalty_points_earned (5-25 deterministic)
                0     # loyalty_points_used
            ))
        
        cursor.executemany('''
        INSERT INTO booked_tickets (id, booking_reference, customer_id, original_available_ticket_id,
                                  train_number, from_station, to_station, departure_time, estimated_arrival_time,
                                  seat_number, carriage, ticket_type, original_price, paid_price,
                                  booking_status, travel_status, purchase_date, check_in_time, boarding_time,
                                  special_requirements, group_booking_id, is_return_ticket, return_ticket_id,
                                  loyalty_points_earned, loyalty_points_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', booked_tickets)
        
        # Insert Transaction Data for booked tickets
        print("💳 Inserting transaction data...")
        
        transactions = []
        for i, booking in enumerate(booked_tickets, 1):
            # Deterministic payment method based on customer ID
            customer_internal_id = booking[2]  # customer_id
            payment_method = get_deterministic_payment_method(customer_internal_id)
            
            # Get customer reference from booking data
            customer_internal_id = booking[2]  # customer_id (internal integer)
            customer_reference = f"CUS{customer_internal_id:03d}"  # Convert to CUS001 format
            
            transactions.append((
                i,
                booking[2],  # customer_id (internal integer)
                customer_reference,  # customer_reference (CUS001)
                booking[0],  # booked_ticket_id
                booking[1],  # booking_reference (UKC001)
                'purchase',
                booking[13], # paid_price
                payment_method,
                booking[16], # purchase_date (transaction_time)
                'completed',
                f"REF{i:06d}",
                'Stripe' if payment_method in ['credit_card', 'debit_card'] else payment_method.title(),
                'GBP',
                1.0000,
                0.50 if payment_method in ['credit_card', 'debit_card'] else 0.00
            ))
        
        cursor.executemany('''
        INSERT INTO transaction_info (id, customer_id, customer_reference, booked_ticket_id, booking_reference,
                                    transaction_type, amount, payment_method, transaction_time, status, 
                                    reference_number, payment_processor, currency, exchange_rate, processing_fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', transactions)
        
        # Insert Booking History for booked tickets
        print("📝 Inserting booking history...")
        
        booking_history = []
        for i, booking in enumerate(booked_tickets, 1):
            booking_history.append((
                i,
                booking[0],  # booked_ticket_id
                'booked',
                None,
                'confirmed',
                json.dumps({"booking_reference": booking[1], "customer_id": booking[2]}),
                'Customer booking',
                'customer',
                booking[16], # purchase_date
                f"Ticket booked successfully for {booking[5]} to {booking[6]}"
            ))
        
        cursor.executemany('''
        INSERT INTO booking_history (id, booked_ticket_id, action, old_status, new_status,
                                   changed_fields, reason, changed_by, change_timestamp, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', booking_history)
        
        # ========================================================================
        # TEST CASE SPECIFIC ENHANCEMENTS
        # ========================================================================
        print("🧪 Adding test-case-specific data...")
        
        # Add missing train schedules for test cases
        print("   Adding test-specific train schedules...")
        
        test_schedules = [
            # Session 1: UK102 11:30 London Euston → Manchester
            ('UK102', 'London to Manchester Express', 'Virgin Trains', 'London Euston', 'Manchester Piccadilly', '11:30', '13:38', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Session 2: UK101 9:30 London Euston → Manchester (for rebooking)
            ('UK101', 'London to Manchester Express', 'Virgin Trains', 'London Euston', 'Manchester Piccadilly', '09:30', '11:38', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Session 3: UK401 15:30 Birmingham → London (first class afternoon)
            ('UK401', 'Birmingham to London Service', 'CrossCountry', 'Birmingham New Street', 'London Euston', '15:30', '16:53', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "audio_announcements": true}', 'active'),
            
            # Session 8: UK301 09:00 London → Birmingham (accessible)
            ('UK301', 'London to Birmingham Service', 'CrossCountry', 'London Euston', 'Birmingham New Street', '09:00', '10:23', 83, 190, 'Daily', 'Every hour', 350, 40, 310, 1, 1, 1, '{"wheelchair_access": true, "guide_dog_space": true, "audio_announcements": true}', 'active'),
            
            # Session 14: UK999 16:45 London KC → Manchester (urgent same-day)
            ('UK999', 'London to Manchester Urgent', 'Virgin Trains', 'London King\'s Cross', 'Manchester Piccadilly', '16:45', '19:15', 150, 328, 'Daily', 'Limited service', 200, 30, 170, 1, 1, 1, '{"wheelchair_access": true, "priority_boarding": true}', 'active'),
            
            # Session 14: UK997 18:00 London KC → Manchester (urgent alternative)
            ('UK997', 'London to Manchester Urgent', 'Virgin Trains', 'London King\'s Cross', 'Manchester Piccadilly', '18:00', '20:30', 150, 328, 'Daily', 'Limited service', 200, 30, 170, 1, 1, 1, '{"wheelchair_access": true}', 'active'),
            
            # Session 5: U502 15:00 London KC → Edinburgh (urgent same-day)
            ('UK503', 'London to Edinburgh Urgent', 'LNER', 'London King\'s Cross', 'Edinburgh Waverley', '15:00', '19:28', 268, 630, 'Daily', 'Limited service', 300, 40, 260, 1, 1, 1, '{"wheelchair_access": true, "priority_boarding": true}', 'active'),
            
            # Session 10: UK202 for Manchester → London with accessibility
            ('UK202', 'Manchester to London Service', 'Virgin Trains', 'Manchester Piccadilly', 'London Euston', '08:15', '10:23', 128, 320, 'Daily', 'Every 2 hours', 400, 50, 350, 1, 1, 1, '{"wheelchair_access": true, "guide_dog_space": true, "audio_announcements": true}', 'active')
        ]
        
        # Insert additional schedules if they don't already exist
        for schedule in test_schedules:
            cursor.execute("SELECT COUNT(*) FROM train_schedules WHERE train_number = ?", (schedule[0],))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                INSERT INTO train_schedules (train_number, service_name, operator, from_station, to_station, 
                                           departure_time, arrival_time, journey_duration, distance_km, 
                                           operating_days, service_frequency, max_capacity, first_class_capacity, 
                                           standard_class_capacity, has_wifi, has_catering, has_power_sockets, 
                                           accessibility_features, service_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', schedule)
        
        # Add test-specific available tickets
        print("   Adding test-specific available tickets...")
        
        test_tickets = []
        current_time = get_system_time_iso()
        
        # Calculate dynamic dates relative to current system time
        today = current_system_time.date()
        tomorrow = today + timedelta(days=1)
        next_tuesday = today + timedelta(days=(1 - today.weekday()) % 7 + 7)  # Next Tuesday
        next_week = today + timedelta(days=7)
        friday = today + timedelta(days=(4 - today.weekday()) % 7)  # This week's Friday, or next Friday if past
        
        # Define test-specific tickets with exact specifications
        test_ticket_specs = [
            # Session 1: UK102 11:30 flexible fare, seat 12A carriage 2 (tomorrow)
            {
                'train_number': 'UK102',
                'from_station': 'London Euston',
                'to_station': 'Manchester Piccadilly', 
                'departure_time': f'{tomorrow} 11:30:00',
                'arrival_time': f'{tomorrow} 13:38:00',
                'seat_number': '12A',
                'carriage': '2',
                'ticket_type': 'flexible',
                'base_price': 89.0,
                'current_price': 89.0,
                'amenities': '{"window_seat": true, "quiet_zone": true, "table": true, "wifi": true, "power_socket": true}',
                'distance': 320
            },
            
            # Session 2: UK101 9:30 flexible fare for rebooking (next week)
            {
                'train_number': 'UK101',
                'from_station': 'London Euston',
                'to_station': 'Manchester Piccadilly',
                'departure_time': f'{next_week} 09:30:00',
                'arrival_time': f'{next_week} 11:38:00', 
                'seat_number': '08A',
                'carriage': '1',
                'ticket_type': 'flexible',
                'base_price': 89.0,
                'current_price': 89.0,
                'amenities': '{"wifi": true, "power_socket": true, "flexible_changes": true}',
                'distance': 320
            },
            
            # Session 3: UK401 15:30 first class Birmingham → London (tomorrow)
            {
                'train_number': 'UK401',
                'from_station': 'Birmingham New Street',
                'to_station': 'London Euston',
                'departure_time': f'{tomorrow} 15:30:00',
                'arrival_time': f'{tomorrow} 16:53:00',
                'seat_number': '01A',
                'carriage': '1', 
                'ticket_type': 'first_class',
                'base_price': 125.0,
                'current_price': 125.0,
                'amenities': '{"complimentary_meal": true, "priority_boarding": true, "wifi": true, "power_socket": true, "table": true}',
                'distance': 190
            },
            
            # Session 4: UK502 7:00 AM first class group booking (3 seats tomorrow)
            {
                'train_number': 'UK502',
                'from_station': 'London King\'s Cross',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{tomorrow} 07:00:00',
                'arrival_time': f'{tomorrow} 11:28:00',
                'seat_number': '01A',
                'carriage': '1',
                'ticket_type': 'first_class',
                'base_price': 225.0,
                'current_price': 225.0,
                'amenities': '{"complimentary_meal": true, "priority_boarding": true, "wifi": true, "power_socket": true}',
                'distance': 630
            },
            
            # Session 4: Additional group seats
            {
                'train_number': 'UK502',
                'from_station': 'London King\'s Cross',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{tomorrow} 07:00:00',
                'arrival_time': f'{tomorrow} 11:28:00',
                'seat_number': '01B',
                'carriage': '1',
                'ticket_type': 'first_class',
                'base_price': 225.0,
                'current_price': 225.0,
                'amenities': '{"complimentary_meal": true, "priority_boarding": true, "wifi": true, "power_socket": true}',
                'distance': 630
            },
            
            {
                'train_number': 'UK502',
                'from_station': 'London King\'s Cross',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{tomorrow} 07:00:00',
                'arrival_time': f'{tomorrow} 11:28:00',
                'seat_number': '01C',
                'carriage': '1',
                'ticket_type': 'first_class',
                'base_price': 225.0,
                'current_price': 225.0,
                'amenities': '{"complimentary_meal": true, "priority_boarding": true, "wifi": true, "power_socket": true}',
                'distance': 630
            },
            
            # Session 5: UK503 15:00 same-day urgent Edinburgh (TODAY)
            {
                'train_number': 'UK503',
                'from_station': 'London King\'s Cross',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{today} 15:00:00',
                'arrival_time': f'{today} 19:28:00',
                'seat_number': '08A',
                'carriage': '1',
                'ticket_type': 'flexible',
                'base_price': 156.0,
                'current_price': 187.2,  # +20% urgent premium
                'amenities': '{"wifi": true, "power_socket": true, "priority_boarding": true}',
                'distance': 630
            },
            
            # Session 6: UK801 Friday Glasgow → Edinburgh
            {
                'train_number': 'UK801',
                'from_station': 'Glasgow Central',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{friday} 08:00:00',  # Friday
                'arrival_time': f'{friday} 08:55:00',
                'seat_number': '12A',
                'carriage': '2',
                'ticket_type': 'flexible',
                'base_price': 28.0,
                'current_price': 28.0,
                'amenities': '{"wifi": true, "power_socket": true, "flexible_changes": true}',
                'distance': 75
            },
            
            # Session 7: UK701 budget Liverpool → Manchester
            {
                'train_number': 'UK701',
                'from_station': 'Liverpool Lime Street',
                'to_station': 'Manchester Piccadilly',
                'departure_time': f'{tomorrow} 08:00:00',
                'arrival_time': f'{tomorrow} 08:47:00',
                'seat_number': '15A',
                'carriage': '3',
                'ticket_type': 'standard',
                'base_price': 25.0,
                'current_price': 25.0,
                'amenities': '{"wifi": true}',
                'distance': 55
            },
            
            # Session 8: UK301 9:00 AM accessible London → Birmingham
            {
                'train_number': 'UK301',
                'from_station': 'London Euston',
                'to_station': 'Birmingham New Street',
                'departure_time': f'{tomorrow} 09:00:00',
                'arrival_time': f'{tomorrow} 10:23:00',
                'seat_number': 'WCA1',  # Wheelchair accessible seat
                'carriage': '1',
                'ticket_type': 'standard',
                'base_price': 63.0,
                'current_price': 63.0,
                'amenities': '{"wheelchair_accessible": true, "guide_dog_space": true, "wifi": true, "power_socket": true, "priority_boarding": true}',
                'distance': 190
            },
            
            # Session 9: UK502 first class international visitor
            {
                'train_number': 'UK502',
                'from_station': 'London King\'s Cross',
                'to_station': 'Edinburgh Waverley',
                'departure_time': f'{next_tuesday} 07:00:00',  # Next Tuesday
                'arrival_time': f'{next_tuesday} 11:28:00',
                'seat_number': '02A',
                'carriage': '1',
                'ticket_type': 'first_class',
                'base_price': 225.0,
                'current_price': 225.0,
                'amenities': '{"complimentary_meal": true, "priority_boarding": true, "wifi": true, "power_socket": true, "table": true}',
                'distance': 630
            },
            
            # Session 14: UK999 16:45 urgent same-day London KC → Manchester (TODAY)
            {
                'train_number': 'UK999',
                'from_station': 'London King\'s Cross',
                'to_station': 'Manchester Piccadilly',
                'departure_time': f'{today} 16:45:00',
                'arrival_time': f'{today} 19:15:00',
                'seat_number': '08A',
                'carriage': '1',
                'ticket_type': 'flexible',
                'base_price': 135.0,
                'current_price': 162.0,  # +20% urgent premium
                'amenities': '{"wifi": true, "power_socket": true, "priority_boarding": true}',
                'distance': 328
            },
            
            # Session 14: UK997 18:00 urgent alternative (TODAY)
            {
                'train_number': 'UK997',
                'from_station': 'London King\'s Cross',
                'to_station': 'Manchester Piccadilly',
                'departure_time': f'{today} 18:00:00',
                'arrival_time': f'{today} 20:30:00',
                'seat_number': '06A',
                'carriage': '1',
                'ticket_type': 'standard',
                'base_price': 98.0,
                'current_price': 117.6,  # +20% urgent premium
                'amenities': '{"wifi": true, "power_socket": true}',
                'distance': 328
            }
        ]
        
        # Generate test-specific tickets
        for i, spec in enumerate(test_ticket_specs, start=101):  # Start after existing tickets
            test_tickets.append((
                i,  # id
                spec['train_number'],
                spec['from_station'],
                spec['to_station'],
                spec['departure_time'],
                spec['arrival_time'],
                spec['seat_number'],
                spec['carriage'],
                spec['ticket_type'],
                spec['base_price'],
                spec['current_price'],
                'available',
                'first_class' if spec['ticket_type'] == 'first_class' else 'standard',
                spec['amenities'],
                spec['distance'],
                current_time,
                current_time
            ))
        
        # Insert test-specific tickets
        cursor.executemany('''
        INSERT INTO available_tickets (id, train_number, from_station, to_station, departure_time, 
                                     arrival_time, seat_number, carriage, ticket_type, base_price, 
                                     current_price, availability_status, booking_class, amenities, 
                                     route_distance_km, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_tickets)
        
        print(f"   Added {len(test_tickets)} test-specific available tickets")
        
        # Add pre-existing bookings for refund scenarios
        print("   Adding pre-existing bookings for refund tests...")
        
        # Check existing booking references to avoid conflicts
        cursor.execute("SELECT MAX(CAST(SUBSTR(booking_reference, 4) AS INTEGER)) FROM booked_tickets WHERE booking_reference LIKE 'UKC%'")
        max_booking_num = cursor.fetchone()[0] or 0
        
        # Create UKC005 booking for Sarah Williams (Session 2 refund test)
        # Use UKC021 instead of UKC005 to avoid conflicts
        cursor.execute('''
        INSERT INTO booked_tickets (id, booking_reference, customer_id, original_available_ticket_id,
                                  train_number, from_station, to_station, departure_time, estimated_arrival_time,
                                  seat_number, carriage, ticket_type, original_price, paid_price,
                                  booking_status, travel_status, purchase_date, check_in_time, boarding_time,
                                  special_requirements, group_booking_id, is_return_ticket, return_ticket_id,
                                  loyalty_points_earned, loyalty_points_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            21,  # id (after existing 20 bookings)
            'UKC021',  # booking_reference (changed from UKC005)
            2,   # customer_id (Sarah Williams)
            5,   # original_available_ticket_id 
            'UK102',
            'London Euston',
            'Manchester Piccadilly',
            f'{tomorrow} 11:30:00',  # Tomorrow (cancellable)
            f'{tomorrow} 13:38:00',
            '05A',
            '1',
            'standard',
            89.0,   # original_price
            89.0,   # paid_price
            'confirmed',
            'upcoming',
            (current_system_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),  # purchase_date (yesterday)
            None,   # check_in_time
            None,   # boarding_time
            None,   # special_requirements
            None,   # group_booking_id
            0,      # is_return_ticket
            None,   # return_ticket_id
            15,     # loyalty_points_earned
            0       # loyalty_points_used
        ))
        
        # Create UKC010 booking for Amanda Taylor (Session 10 modify test)
        # Use UKC022 instead of UKC010 to avoid conflicts
        cursor.execute('''
        INSERT INTO booked_tickets (id, booking_reference, customer_id, original_available_ticket_id,
                                  train_number, from_station, to_station, departure_time, estimated_arrival_time,
                                  seat_number, carriage, ticket_type, original_price, paid_price,
                                  booking_status, travel_status, purchase_date, check_in_time, boarding_time,
                                  special_requirements, group_booking_id, is_return_ticket, return_ticket_id,
                                  loyalty_points_earned, loyalty_points_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            22,  # id
            'UKC022',  # booking_reference (changed from UKC010)
            10,  # customer_id (Amanda Taylor) 
            8,   # original_available_ticket_id
            'UK201',
            'Manchester Piccadilly',
            'London Euston',
            (current_system_time + timedelta(days=15)).strftime('%Y-%m-%d') + ' 08:15:00',  # Future date (modifiable)
            (current_system_time + timedelta(days=15)).strftime('%Y-%m-%d') + ' 10:23:00',
            '03A',
            '1',
            'flexible',
            106.8,  # original_price
            106.8,  # paid_price
            'confirmed',
            'upcoming',
            (current_system_time - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),  # purchase_date (2 days ago)
            None,   # check_in_time
            None,   # boarding_time
            'Wheelchair accessibility required',  # special_requirements
            None,   # group_booking_id
            0,      # is_return_ticket
            None,   # return_ticket_id
            20,     # loyalty_points_earned
            5       # loyalty_points_used
        ))
        
        # Add corresponding transactions for the refund bookings
        cursor.execute('''
        INSERT INTO transaction_info (id, customer_id, customer_reference, booked_ticket_id, booking_reference,
                                    transaction_type, amount, payment_method, transaction_time, status, 
                                    reference_number, payment_processor, currency, exchange_rate, processing_fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            21,  # id
            2,   # customer_id (Sarah Williams)
            'CUS002',  # customer_reference
            21,  # booked_ticket_id
            'UKC021',
            'purchase',
            89.0,
            'debit_card',
            (current_system_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'completed',
            'REF000021',
            'Stripe',
            'GBP',
            1.0000,
            0.50
        ))
        
        cursor.execute('''
        INSERT INTO transaction_info (id, customer_id, customer_reference, booked_ticket_id, booking_reference,
                                    transaction_type, amount, payment_method, transaction_time, status, 
                                    reference_number, payment_processor, currency, exchange_rate, processing_fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            22,  # id
            10,  # customer_id (Amanda Taylor)
            'CUS010',  # customer_reference
            22,  # booked_ticket_id
            'UKC022',
            'purchase',
            106.8,
            'corporate_account',
            (current_system_time - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'completed',
            'REF000022',
            'Stripe',
            'GBP', 
            1.0000,
            0.50
        ))
        
        print("   Added UKC005 and UKC010 bookings for refund test scenarios")
        
        # Commit all changes
        conn.commit()
        
        print("\n✅ Enhanced database v2.0 populated successfully!")
        
        # Display summary statistics
        cursor.execute("SELECT COUNT(*) FROM customer_info")
        customers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM available_tickets")
        available_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM booked_tickets")
        booked_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transaction_info")
        transactions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM train_schedules")
        schedules_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM booking_history")
        history_count = cursor.fetchone()[0]
        
        print(f"\n📊 Enhanced Database Summary:")
        print(f"- Customers: {customers_count}")
        print(f"- Available tickets (for purchase): {available_count}")
        print(f"- Booked tickets: {booked_count}")
        print(f"- Transactions: {transactions_count}")
        print(f"- Train schedules: {schedules_count}")
        print(f"- Booking history entries: {history_count}")
        print(f"- Total database entries: {customers_count + available_count + booked_count + transactions_count + schedules_count + history_count}")
        
        # Show availability status
        cursor.execute("SELECT availability_status, COUNT(*) FROM available_tickets GROUP BY availability_status")
        availability_stats = cursor.fetchall()
        print(f"\n🎫 Ticket Availability:")
        for status, count in availability_stats:
            print(f"- {status}: {count} tickets")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()
            print(f"\n📦 Database connection closed")

def verify_data(db_path=None):
    """Verify data. If no path provided, uses the default database location."""
    if db_path is None:
        import os
        # Default to the database directory relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, '..', 'database', 'ukconnect_rail.db')
        db_path = os.path.abspath(db_path)
    """
    Verify that all enhanced data was inserted correctly.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying enhanced data v2.0...")
        
        # Test inventory management queries
        print("\n📋 Inventory Management Verification:")
        
        # Check available tickets by route
        cursor.execute('''
        SELECT from_station, to_station, COUNT(*) as available_count
        FROM available_tickets
        WHERE availability_status = 'available'
        GROUP BY from_station, to_station
        ORDER BY available_count DESC
        LIMIT 5
        ''')
        available_routes = cursor.fetchall()
        print("Available tickets by route:")
        for from_st, to_st, count in available_routes:
            print(f"  - {from_st} → {to_st}: {count} available")
        
        # Check sold tickets
        cursor.execute('''
        SELECT from_station, to_station, COUNT(*) as sold_count
        FROM available_tickets
        WHERE availability_status = 'sold'
        GROUP BY from_station, to_station
        ORDER BY sold_count DESC
        ''')
        sold_routes = cursor.fetchall()
        print("\nSold tickets by route:")
        for from_st, to_st, count in sold_routes:
            print(f"  - {from_st} → {to_st}: {count} sold")
        
        # Check booking to available ticket linkage
        cursor.execute('''
        SELECT b.booking_reference, b.from_station, b.to_station, a.availability_status
        FROM booked_tickets b
        JOIN available_tickets a ON b.original_available_ticket_id = a.id
        LIMIT 5
        ''')
        bookings_check = cursor.fetchall()
        print("\nBooking-Inventory linkage verification:")
        for ref, from_st, to_st, status in bookings_check:
            print(f"  - {ref}: {from_st} → {to_st} (original ticket status: {status})")
        
        # Check pricing variations
        cursor.execute('''
        SELECT ticket_type, AVG(base_price) as avg_base, AVG(current_price) as avg_current
        FROM available_tickets
        WHERE availability_status = 'available'
        GROUP BY ticket_type
        ''')
        pricing_stats = cursor.fetchall()
        print("\nPricing analysis:")
        for ticket_type, avg_base, avg_current in pricing_stats:
            price_change = ((avg_current - avg_base) / avg_base) * 100 if avg_base > 0 else 0
            print(f"  - {ticket_type}: £{avg_base:.2f} base → £{avg_current:.2f} current ({price_change:+.1f}%)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("UKConnect Rail Enhanced Database Data Population v2.0")
    print("=" * 70)
    
    # Allow custom database path from command line, otherwise use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        import os
        # Default to the database directory relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, '..', 'database', 'ukconnect_rail.db')
        db_path = os.path.abspath(db_path)
    
    # Check if database exists
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='available_tickets'")
        if not cursor.fetchone():
            print("❌ Enhanced database schema not found!")
            print("Please run create_schema.py first to create the database tables.")
            sys.exit(1)
        conn.close()
    except Exception as e:
        print(f"❌ Cannot access database: {e}")
        sys.exit(1)
    
    # Populate data
    success = populate_data(db_path)
    
    if success:
        # Verify data
        verify_data(db_path)
        print(f"\n🎉 Enhanced data population complete! Database ready at: {db_path}")
        print(f"Successfully created a comprehensive booking system with:")
        print("✅ 55 customers across the UK")
        print("✅ 100 available tickets for purchase (inventory)")
        print("✅ 20 booked tickets (with inventory tracking)")
        print("✅ 15 train schedules across major routes")
        print("✅ Complete transaction and audit trail")
        print("✅ Dynamic pricing and seat management")
        print("\nYour enhanced AI agent can now handle:")
        print("- Real ticket availability searches")
        print("- Proper booking and refund workflows")
        print("- Inventory management")
        print("- Complex customer support scenarios")
        print("\nNext: Update database.py with inventory management functions! 🚀")
    else:
        print("\n💥 Enhanced data population failed!")
        sys.exit(1)