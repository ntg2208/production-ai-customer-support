#!/usr/bin/env python3
"""
UKConnect Rail Database Query Interface v2.0
Enhanced database interface with inventory management for available tickets.
"""

import sqlite3
import sys
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Import centralized time configuration
try:
    from ..config.time_config import get_system_time_iso, get_system_time_for_database
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
    from time_config import get_system_time_iso, get_system_time_for_database

# Import city station mapping from utils
try:
    from ..utils.city_station_mapping import normalize_location_input, get_stations_by_city, search_cities_and_stations
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
    from city_station_mapping import normalize_location_input, get_stations_by_city, search_cities_and_stations

class UKConnectDB:
    """Enhanced database interface for UKConnect Rail AI Agent with inventory management"""
    
    def __init__(self, db_path=None, current_date=None):
        """
        Initialize database connection with enhanced v2.0 features
        
        Args:
            db_path (str, optional): Path to SQLite database file. If None, uses default location.
            current_date (str, optional): DEPRECATED - use centralized time config instead. 
                                        For backward compatibility only.
        """
        if db_path is None:
            # Default to database directory relative to this file
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, "ukconnect_rail.db")
        else:
            self.db_path = db_path
        self.conn = None
        # For backward compatibility, but centralized config takes precedence
        self.current_date = current_date
    
    def get_current_datetime(self):
        """Get current datetime for queries using centralized time configuration"""
        # Use centralized time configuration (takes precedence over constructor parameter)
        return get_system_time_for_database()
    
    def get_current_datetime_plus_hours(self, hours):
        """Get current datetime plus specified hours for queries"""
        # Get the system time and add hours
        system_time = get_system_time_iso()
        return f"datetime('{system_time}', '+{hours} hours')"
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            # print(f"✅ Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            # print("📦 Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as e:
            print(f"❌ Query error: {e}")
            return None

    # ==============================================
    # AVAILABLE TICKETS INVENTORY QUERIES
    # ==============================================
    
    def search_available_tickets(self, from_station=None, to_station=None, departure_date=None, 
                               ticket_type=None, max_price=None):
        """
        Search available tickets for purchase
        
        Args:
            from_station (str, optional): Origin station or city name
            to_station (str, optional): Destination station or city name  
            departure_date (str, optional): Date in 'YYYY-MM-DD' format (searches from this date onward)
            ticket_type (str, optional): 'advance', 'standard', 'flex', 'first_class'
            max_price (float, optional): Maximum price filter
            
        Returns:
            list: Available tickets matching search criteria (returns all matching results)
        """
        query = '''
        SELECT id, train_number, from_station, to_station, departure_time, arrival_time,
               seat_number, carriage, ticket_type, base_price, current_price, 
               booking_class, amenities, route_distance_km
        FROM available_tickets
        WHERE availability_status = 'available'
        '''
        params = []
        
        # Add location filters
        if from_station:
            from_info = normalize_location_input(from_station)
            if from_info["stations"]:
                placeholders = ", ".join("?" * len(from_info["stations"]))
                query += f" AND from_station IN ({placeholders})"
                params.extend(from_info["stations"])
        
        if to_station:
            to_info = normalize_location_input(to_station)
            if to_info["stations"]:
                placeholders = ", ".join("?" * len(to_info["stations"]))
                query += f" AND to_station IN ({placeholders})"
                params.extend(to_info["stations"])
        
        # Add other filters  
        if departure_date:
            query += " AND DATE(departure_time) >= ?"
            params.append(departure_date)
        
        if ticket_type:
            query += " AND ticket_type = ?"
            params.append(ticket_type)
        
        if max_price:
            query += " AND current_price <= ?"
            params.append(max_price)
        
        # Only show future departures
        query += f" AND departure_time > {self.get_current_datetime()}"
        
        query += " ORDER BY departure_time, current_price"
        
        results = self.execute_query(query, tuple(params))
        
        # Parse amenities JSON
        if results:
            for ticket in results:
                try:
                    ticket['amenities'] = json.loads(ticket['amenities']) if ticket['amenities'] else {}
                except json.JSONDecodeError:
                    ticket['amenities'] = {}
        
        return results or []
    
    def search_available_tickets_from_city(self, from_city, departure_date=None, ticket_type=None, max_price=None, limit=50):
        """
        Search available tickets departing from a specific city to all other destinations
        
        Args:
            from_city (str): Origin city name
            departure_date (str, optional): Date in 'YYYY-MM-DD' format (searches from this date onward)
            ticket_type (str, optional): 'advance', 'standard', 'flex', 'first_class'
            max_price (float, optional): Maximum price filter
            limit (int): Maximum results to return
            
        Returns:
            list: Available tickets from the specified city to all destinations
        """
        # Use the city mapping to get all stations for the city
        from_info = normalize_location_input(from_city)
        
        if not from_info["stations"]:
            return []
        
        query = '''
        SELECT id, train_number, from_station, to_station, departure_time, arrival_time,
               seat_number, carriage, ticket_type, base_price, current_price, 
               booking_class, amenities, route_distance_km
        FROM available_tickets
        WHERE availability_status = 'available'
        '''
        params = []
        
        # Add city stations filter
        placeholders = ", ".join("?" * len(from_info["stations"]))
        query += f" AND from_station IN ({placeholders})"
        params.extend(from_info["stations"])
        
        # Add other filters  
        if departure_date:
            query += " AND DATE(departure_time) >= ?"
            params.append(departure_date)
        
        if ticket_type:
            query += " AND ticket_type = ?"
            params.append(ticket_type)
        
        if max_price:
            query += " AND current_price <= ?"
            params.append(max_price)
        
        # Only show future departures
        query += f" AND departure_time > {self.get_current_datetime()}"
        
        query += " ORDER BY departure_time, current_price"
        
        results = self.execute_query(query, tuple(params))
        
        # Parse amenities JSON
        if results:
            for ticket in results:
                try:
                    ticket['amenities'] = json.loads(ticket['amenities']) if ticket['amenities'] else {}
                except json.JSONDecodeError:
                    ticket['amenities'] = {}
        
        return results or []
    
    def get_available_ticket_details(self, ticket_id):
        """
        Get detailed information about an available ticket
        
        Args:
            ticket_id (int): Available ticket ID
            
        Returns:
            dict or None: Ticket details if found and available
        """
        query = '''
        SELECT a.*, ts.service_name, ts.operator, ts.has_wifi, ts.has_catering, 
               ts.has_power_sockets, ts.accessibility_features
        FROM available_tickets a
        JOIN train_schedules ts ON a.train_number = ts.train_number 
                                AND a.from_station = ts.from_station 
                                AND a.to_station = ts.to_station
        WHERE a.id = ? AND a.availability_status = 'available'
        '''
        results = self.execute_query(query, (ticket_id,))
        
        if results:
            ticket = results[0]
            # Parse JSON fields
            try:
                ticket['amenities'] = json.loads(ticket['amenities']) if ticket['amenities'] else {}
                ticket['accessibility_features'] = json.loads(ticket['accessibility_features']) if ticket['accessibility_features'] else {}
            except json.JSONDecodeError:
                ticket['amenities'] = {}
                ticket['accessibility_features'] = {}
            return ticket
        
        return None
    
    def check_seat_availability(self, train_number, departure_date, carriage=None):
        """
        Check seat availability for a specific train and date
        
        Args:
            train_number (str): Train number
            departure_date (str): Date in 'YYYY-MM-DD' format
            carriage (str, optional): Specific carriage number
            
        Returns:
            dict: Availability summary
        """
        query = '''
        SELECT carriage, COUNT(*) as available_seats,
               GROUP_CONCAT(seat_number) as available_seat_numbers
        FROM available_tickets
        WHERE train_number = ? AND DATE(departure_time) >= ? AND availability_status = 'available'
        '''
        params = [train_number, departure_date]
        
        if carriage:
            query += " AND carriage = ?"
            params.append(carriage)
        
        query += " GROUP BY carriage ORDER BY carriage"
        
        results = self.execute_query(query, tuple(params))
        
        return {
            'train_number': train_number,
            'departure_date': departure_date,
            'carriages': results or [],
            'total_available': sum(row['available_seats'] for row in results) if results else 0
        }

    # ==============================================
    # BOOKING AND TRANSACTION OPERATIONS
    # ==============================================
    
    def book_ticket(self, customer_email, ticket_id, payment_method='credit_card'):
        """
        Book an available ticket for a customer
        
        Args:
            customer_email (str): Customer email address
            ticket_id (int): ID of the available ticket to book
            payment_method (str): Payment method
            
        Returns:
            dict: Booking result with booking reference or error
        """
        try:
            cursor = self.conn.cursor()
            
            # Start transaction for booking atomicity
            cursor.execute("BEGIN TRANSACTION")
            
            # Get customer info
            customer = self.find_customer_by_email(customer_email)
            if not customer:
                cursor.execute("ROLLBACK")
                return {'error': 'Customer not found'}
            
            customer_id = customer[0]['id']
            
            # Validate ticket_id
            if not isinstance(ticket_id, int) or ticket_id <= 0:
                cursor.execute("ROLLBACK")
                return {'error': 'Invalid ticket ID provided'}
            
            # Get and reserve the specific available ticket atomically
            cursor.execute("""
                SELECT a.id, a.train_number, a.from_station, a.to_station, a.departure_time, a.arrival_time,
                       a.seat_number, a.carriage, a.ticket_type, a.base_price, a.current_price, 
                       a.booking_class, a.amenities, a.route_distance_km
                FROM available_tickets a
                WHERE a.id = ? AND a.availability_status = 'available'
            """, (ticket_id,))
            
            available_ticket_row = cursor.fetchone()
            if not available_ticket_row:
                cursor.execute("ROLLBACK")
                return {'error': 'Ticket not available or already booked'}
            
            # Convert row to dict for compatibility
            available_ticket = dict(available_ticket_row)
            
            # Immediately mark ticket as sold to prevent double booking
            cursor.execute("""
                UPDATE available_tickets 
                SET availability_status = 'sold' 
                WHERE id = ? AND availability_status = 'available'
            """, (ticket_id,))
            
            # Check if update succeeded (ticket wasn't taken by another transaction)
            if cursor.rowcount == 0:
                cursor.execute("ROLLBACK")
                return {'error': 'Ticket was just booked by another customer. Please select a different ticket.'}
            
            # Generate unique booking reference more robustly
            max_attempts = 10
            booking_reference = None
            
            for attempt in range(max_attempts):
                # Get the highest existing booking number
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTR(booking_reference, 4) AS INTEGER)) 
                    FROM booked_tickets 
                    WHERE booking_reference LIKE 'UKC%' AND LENGTH(booking_reference) = 6
                """)
                result = cursor.fetchone()
                max_booking_num = result[0] if result[0] is not None else 0
                
                # Generate next booking reference
                next_booking_num = max_booking_num + 1 + attempt  # Add attempt to avoid collisions
                booking_reference = f"UKC{next_booking_num:03d}"
                
                # Check if this reference already exists
                cursor.execute("SELECT COUNT(*) FROM booked_tickets WHERE booking_reference = ?", (booking_reference,))
                if cursor.fetchone()[0] == 0:
                    break  # Found unique reference
                    
            if booking_reference is None:
                cursor.execute("ROLLBACK")
                return {'error': 'Unable to generate unique booking reference. Please try again.'}
            
            # Create booking record from available ticket data
            booking_data = (
                booking_reference,
                customer_id,
                ticket_id,  # Store reference to original available ticket ID
                available_ticket['train_number'],
                available_ticket['from_station'],
                available_ticket['to_station'],
                available_ticket['departure_time'],
                available_ticket['arrival_time'],
                available_ticket['seat_number'],
                available_ticket['carriage'],
                available_ticket['ticket_type'],
                available_ticket['base_price'],
                available_ticket['current_price'],
                'confirmed',
                'upcoming',
                get_system_time_iso(),
                None, None, None, None, 0, None,
                max(1, int(available_ticket['current_price'] * 0.1)),  # loyalty points
                0
            )
            
            cursor.execute('''
            INSERT INTO booked_tickets (booking_reference, customer_id, original_available_ticket_id,
                                      train_number, from_station, to_station, departure_time, estimated_arrival_time,
                                      seat_number, carriage, ticket_type, original_price, paid_price,
                                      booking_status, travel_status, purchase_date, check_in_time, boarding_time,
                                      special_requirements, group_booking_id, is_return_ticket, return_ticket_id,
                                      loyalty_points_earned, loyalty_points_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', booking_data)
            
            # Ticket is already marked as 'sold' in available_tickets table
            # This maintains the original inventory record for audit purposes
            
            booked_ticket_id = cursor.lastrowid
            
            # Create transaction record
            customer_reference = f"CUS{customer_id:03d}"
            transaction_data = (
                customer_id,
                customer_reference,
                booked_ticket_id,
                booking_reference,
                'purchase',
                available_ticket['current_price'],
                payment_method,
                get_system_time_iso(),
                'completed',
                f"PAY{booked_ticket_id:06d}",
                'Stripe' if payment_method in ['credit_card', 'debit_card'] else payment_method.title(),
                'GBP',
                1.0000,
                0.50 if payment_method in ['credit_card', 'debit_card'] else 0.00
            )
            
            cursor.execute('''
            INSERT INTO transaction_info (customer_id, customer_reference, booked_ticket_id, booking_reference,
                                        transaction_type, amount, payment_method, transaction_time, status, 
                                        reference_number, payment_processor, currency, exchange_rate, processing_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', transaction_data)
            
            # Create booking history entry
            history_data = (
                booked_ticket_id,
                'booked',
                'available',
                'confirmed',
                json.dumps({
                    "booking_reference": booking_reference,
                    "customer_id": customer_id,
                    "original_available_ticket_id": ticket_id,
                    "moved_from_inventory": True,
                    "payment_method": payment_method
                }),
                'Customer booking',
                'customer',
                get_system_time_iso(),
                f"Ticket moved from available inventory (ID {ticket_id}) to booked status for {available_ticket['from_station']} to {available_ticket['to_station']}"
            )
            
            cursor.execute('''
            INSERT INTO booking_history (booked_ticket_id, action, old_status, new_status,
                                       changed_fields, reason, changed_by, change_timestamp, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', history_data)
            
            self.conn.commit()
            
            return {
                'success': True,
                'booking_reference': booking_reference,
                'booked_ticket_id': booked_ticket_id,
                'original_available_ticket_id': ticket_id,
                'ticket_moved_from_inventory': True,
                'ticket_details': {
                    'from_station': available_ticket['from_station'],
                    'to_station': available_ticket['to_station'],
                    'departure_time': available_ticket['departure_time'],
                    'seat_number': available_ticket['seat_number'],
                    'carriage': available_ticket['carriage'],
                    'price_paid': available_ticket['current_price']
                }
            }
            
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            return {'error': f'Booking failed: {e}'}
    
    def refund_ticket(self, booking_reference, reason='Customer request'):
        """
        Process a ticket refund and return it to available inventory
        
        Args:
            booking_reference (str): Booking reference to refund
            reason (str): Reason for refund
            
        Returns:
            dict: Refund result with amount or error
        """
        try:
            cursor = self.conn.cursor()
            
            # Get booked ticket details
            booked_ticket = self.get_booked_ticket_details(booking_reference)
            if not booked_ticket:
                return {'error': 'Booking not found'}
            
            if booked_ticket[0]['booking_status'] in ['cancelled', 'refunded']:
                return {'error': f'Ticket already {booked_ticket[0]["booking_status"]}'}
            
            ticket = booked_ticket[0]
            
            # Calculate refund amount
            refund_calc = self.calculate_refund_amount(booking_reference)
            if 'error' in refund_calc:
                return refund_calc
            
            # Create new available ticket from booked ticket data
            available_ticket_data = (
                ticket['train_number'],
                ticket['from_station'],
                ticket['to_station'],
                ticket['departure_time'],
                ticket['estimated_arrival_time'],  # Use estimated_arrival_time as arrival_time
                ticket['seat_number'],
                ticket['carriage'],
                ticket['ticket_type'],
                ticket['paid_price'],  # Use paid_price as base_price
                ticket['paid_price'],  # Use paid_price as current_price
                'available',  # availability_status
                'standard' if ticket['ticket_type'] in ['advance', 'standard', 'flex'] else 'first_class',  # booking_class
                None,  # amenities (JSON string)
                None,  # route_distance_km
                get_system_time_iso(),  # created_at
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')   # updated_at
            )
            
            cursor.execute('''
            INSERT INTO available_tickets (train_number, from_station, to_station, departure_time, arrival_time,
                                         seat_number, carriage, ticket_type, base_price, current_price,
                                         availability_status, booking_class, amenities, route_distance_km,
                                         created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', available_ticket_data)
            
            # Get the ID of the newly created available ticket
            new_available_ticket_id = cursor.lastrowid
            
            # Create booking history entry BEFORE deleting the booked ticket (so we have valid booked_ticket_id)
            history_data = (
                ticket['id'],  # Use the actual booked_ticket_id before deletion
                'refunded',
                'confirmed',
                'refunded',
                json.dumps({
                    "original_booked_ticket_id": ticket['id'],
                    "booking_reference": booking_reference,
                    "new_available_ticket_id": new_available_ticket_id,
                    "refund_amount": refund_calc['refund_amount'],
                    "refund_percentage": refund_calc['refund_percentage'],
                    "reason": reason,
                    "customer_id": ticket['customer_id']
                }),
                reason,
                'system',
                get_system_time_iso(),
                f"Ticket refunded and moved to available inventory: £{refund_calc['refund_amount']} ({refund_calc['refund_percentage']}%). Booking {booking_reference} converted to available ticket ID {new_available_ticket_id}"
            )
            
            cursor.execute('''
            INSERT INTO booking_history (booked_ticket_id, action, old_status, new_status,
                                       changed_fields, reason, changed_by, change_timestamp, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', history_data)
            
            # Create refund transaction (use actual booked_ticket_id before deletion)
            customer_reference = f"CUS{ticket['customer_id']:03d}"  
            refund_data = (
                ticket['customer_id'],
                customer_reference,
                ticket['id'],  # Use actual booked_ticket_id before deletion
                booking_reference,
                'refund',
                refund_calc['refund_amount'],
                ticket['original_payment_method'] if 'original_payment_method' in ticket else 'credit_card',
                get_system_time_iso(),
                'completed',
                f"REF{ticket['id']:06d}",
                'Stripe',
                'GBP',
                1.0000,
                0.00
            )
            
            cursor.execute('''
            INSERT INTO transaction_info (customer_id, customer_reference, booked_ticket_id, booking_reference,
                                        transaction_type, amount, payment_method, transaction_time, status, 
                                        reference_number, payment_processor, currency, exchange_rate, processing_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', refund_data)
            
            # Delete the booked ticket record LAST (after creating history and transaction records)
            cursor.execute('''
            DELETE FROM booked_tickets 
            WHERE booking_reference = ?
            ''', (booking_reference,))
            
            self.conn.commit()
            
            return {
                'success': True,
                'refund_amount': refund_calc['refund_amount'],
                'refund_percentage': refund_calc['refund_percentage'],
                'ticket_moved_to_inventory': True,
                'new_available_ticket_id': new_available_ticket_id,
                'booking_reference_removed': booking_reference
            }
            
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            return {'error': f'Refund failed: {e}'}

    # ==============================================
    # ENHANCED CUSTOMER QUERIES
    # ==============================================
    
    def find_customer_by_email(self, email):
        """Find customer by email address"""
        query = '''
        SELECT id, customer_id, name, email, phone, address
        FROM customer_info
        WHERE email = ?
        '''
        return self.execute_query(query, (email,))
    
    def get_customer_information(self, email):
        """
        Get comprehensive customer information by email address
        
        Args:
            email (str): Customer email address
            
        Returns:
            dict: Customer information with booking and transaction summary, or None if not found
        """
        customer_query = '''
        SELECT id, customer_id, name, email, phone, address
        FROM customer_info
        WHERE email = ?
        '''
        customers = self.execute_query(customer_query, (email,))
        
        if not customers:
            return None
        
        customer = customers[0]
        
        # Get booking count and recent activity
        booking_query = '''
        SELECT COUNT(*) as total_bookings,
               COUNT(CASE WHEN booking_status = 'confirmed' THEN 1 END) as active_bookings,
               MAX(purchase_date) as last_booking_date
        FROM booked_tickets
        WHERE customer_id = ?
        '''
        booking_stats = self.execute_query(booking_query, (customer["id"],))
        
        # Get transaction summary
        transaction_query = '''
        SELECT COUNT(*) as total_transactions,
               SUM(CASE WHEN transaction_type = 'purchase' THEN amount ELSE 0 END) as total_spent,
               SUM(CASE WHEN transaction_type = 'refund' THEN amount ELSE 0 END) as total_refunded,
               MAX(transaction_time) as last_transaction_date
        FROM transaction_info
        WHERE customer_id = ?
        '''
        transaction_stats = self.execute_query(transaction_query, (customer["id"],))
        
        # Combine all information
        result = {
            "customer_details": {
                "id": customer["id"],
                "customer_id": customer["customer_id"],  # CUS001 format
                "name": customer["name"],
                "email": customer["email"],
                "phone": customer["phone"],
                "address": customer["address"]
            },
            "booking_summary": {
                "total_bookings": booking_stats[0]["total_bookings"] if booking_stats else 0,
                "active_bookings": booking_stats[0]["active_bookings"] if booking_stats else 0,
                "last_booking_date": booking_stats[0]["last_booking_date"] if booking_stats else None
            },
            "transaction_summary": {
                "total_transactions": transaction_stats[0]["total_transactions"] if transaction_stats else 0,
                "total_spent": float(transaction_stats[0]["total_spent"] or 0) if transaction_stats else 0.0,
                "total_refunded": float(transaction_stats[0]["total_refunded"] or 0) if transaction_stats else 0.0,
                "last_transaction_date": transaction_stats[0]["last_transaction_date"] if transaction_stats else None
            }
        }
        
        return result
    
    def get_customer_bookings(self, email):
        """
        Get all bookings for a customer with enhanced details
        
        Args:
            email (str): Customer email address
            
        Returns:
            list: All bookings for the customer with enhanced information
        """
        query = '''
        SELECT bt.booking_reference, bt.from_station, bt.to_station, bt.departure_time,
               bt.seat_number, bt.carriage, bt.ticket_type, bt.paid_price,
               bt.booking_status, bt.travel_status, bt.purchase_date,
               bt.loyalty_points_earned, bt.special_requirements,
               c.customer_id, c.name, c.email as customer_email, c.phone,
               ts.service_name, ts.operator
        FROM booked_tickets bt
        JOIN customer_info c ON bt.customer_id = c.id
        LEFT JOIN train_schedules ts ON bt.train_number = ts.train_number 
                                     AND bt.from_station = ts.from_station 
                                     AND bt.to_station = ts.to_station
        WHERE c.email = ?
        ORDER BY bt.departure_time DESC
        '''
        return self.execute_query(query, (email,))
    
    def get_booked_ticket_details(self, booking_reference):
        """Get complete booked ticket information"""
        query = '''
        SELECT bt.*, c.customer_id, c.name, c.email, c.phone
        FROM booked_tickets bt
        JOIN customer_info c ON bt.customer_id = c.id
        WHERE bt.booking_reference = ?
        '''
        return self.execute_query(query, (booking_reference,))
    
    def find_active_customer_tickets(self, customer_email):
        """
        Find active tickets for a customer based on current date
        
        Args:
            customer_email (str): Customer email address
            
        Returns:
            list: Active tickets (confirmed status and future departure) for the customer
        """
        query = '''
        SELECT bt.booking_reference, bt.from_station, bt.to_station, bt.departure_time,
               bt.estimated_arrival_time, bt.seat_number, bt.carriage, bt.ticket_type, 
               bt.paid_price, bt.booking_status, bt.travel_status, bt.train_number,
               c.name, c.email as customer_email, c.phone,
               ts.service_name, ts.operator
        FROM booked_tickets bt
        JOIN customer_info c ON bt.customer_id = c.id
        LEFT JOIN train_schedules ts ON bt.train_number = ts.train_number 
                                     AND bt.from_station = ts.from_station 
                                     AND bt.to_station = ts.to_station
        WHERE c.email = ? 
        AND bt.booking_status = 'confirmed'
        AND bt.departure_time > {}
        ORDER BY bt.departure_time ASC
        '''.format(self.get_current_datetime())
        
        return self.execute_query(query, (customer_email,))
    
    def search_customer_recent_transactions(self, customer_email, limit=10, days_back=30):
        """
        Search recent transactions for a customer using their email address
        
        Args:
            customer_email (str): Customer email address
            limit (int): Maximum number of transactions to return (default: 10)
            days_back (int): Number of days to look back from current date (default: 30)
            
        Returns:
            list: Recent transactions for the customer with booking details
        """
        query = '''
        SELECT ti.*, c.name, c.email, c.customer_id,
               bt.booking_reference, bt.from_station, bt.to_station, 
               bt.departure_time, bt.ticket_type, bt.booking_status
        FROM transaction_info ti
        JOIN customer_info c ON ti.customer_id = c.id
        LEFT JOIN booked_tickets bt ON ti.booked_ticket_id = bt.id
        WHERE c.email = ? 
        AND ti.transaction_time >= datetime({}, '-{} days')
        ORDER BY ti.transaction_time DESC
        LIMIT ?
        '''.format(self.get_current_datetime(), days_back)
        
        return self.execute_query(query, (customer_email, limit))

    # ==============================================
    # ENHANCED REFUND CALCULATIONS
    # ==============================================
    
    def calculate_refund_amount(self, booking_reference):
        """
        Calculate refund amount using enhanced rules
        
        Args:
            booking_reference (str): Booking reference code
            
        Returns:
            dict: Refund calculation details or error message
        """
        # Get booked ticket details
        ticket_query = '''
        SELECT ticket_type, paid_price, departure_time, booking_status
        FROM booked_tickets
        WHERE booking_reference = ?
        '''
        ticket = self.execute_query(ticket_query, (booking_reference,))
        
        if not ticket:
            return {'error': 'Booking not found'}
        
        ticket_data = ticket[0]
        ticket_type = ticket_data['ticket_type']
        price = float(ticket_data['paid_price'])
        departure_time = datetime.fromisoformat(ticket_data['departure_time'])
        status = ticket_data['booking_status']
        
        # Check if ticket can be refunded
        if status in ['used', 'cancelled', 'refunded']:
            return {'error': f'Ticket cannot be refunded - status is {status}'}
        
        # Calculate hours until departure
        if self.current_date:
            now = datetime.fromisoformat(self.current_date)
        else:
            now = datetime.fromisoformat(get_system_time_iso())
        hours_until_departure = (departure_time - now).total_seconds() / 3600
        
        # Get applicable refund rule
        rules_query = '''
        SELECT refund_percentage, cancellation_fee, rule_description
        FROM refund_rules
        WHERE ticket_type = ? AND hours_before_departure <= ? AND is_active = 1
        ORDER BY hours_before_departure DESC
        LIMIT 1
        '''
        rules = self.execute_query(rules_query, (ticket_type, hours_until_departure))
        print(ticket_type, hours_until_departure)
        
        if not rules:
            return {'error': 'No refund rules found for this ticket type'}
        
        rule = rules[0]
        refund_percentage = rule['refund_percentage']
        cancellation_fee = float(rule['cancellation_fee']) if rule['cancellation_fee'] else 0.0
        
        refund_amount = (price * (refund_percentage / 100)) - cancellation_fee
        refund_amount = max(0, refund_amount)  # Never negative
        
        return {
            'original_price': price,
            'refund_percentage': refund_percentage,
            'cancellation_fee': cancellation_fee,
            'refund_amount': round(refund_amount, 2),
            'hours_until_departure': round(hours_until_departure, 1),
            'can_refund': True,
            'rule_description': rule['rule_description']
        }

    # ==============================================
    # TRANSACTION OPERATIONS
    # ==============================================
    
    def get_customer_transaction_history(self, customer_reference):
        """
        Get transaction history for a customer by customer reference (CUS001)
        
        Args:
            customer_reference (str): Customer reference like 'CUS001'
            
        Returns:
            list: Transaction history for the customer
        """
        query = '''
        SELECT ti.*, c.name, c.email
        FROM transaction_info ti
        JOIN customer_info c ON ti.customer_id = c.id
        WHERE ti.customer_reference = ?
        ORDER BY ti.transaction_time DESC
        '''
        return self.execute_query(query, (customer_reference,))
    
    def get_booking_transaction_details(self, booking_reference):
        """
        Get all transactions for a specific booking reference
        
        Args:
            booking_reference (str): Booking reference like 'UKC001'
            
        Returns:
            list: All transactions related to the booking
        """
        query = '''
        SELECT ti.*, c.name, c.email, c.customer_id as customer_reference_id
        FROM transaction_info ti
        JOIN customer_info c ON ti.customer_id = c.id
        WHERE ti.booking_reference = ?
        ORDER BY ti.transaction_time
        '''
        return self.execute_query(query, (booking_reference,))

    # ==============================================
    # ANALYTICS AND REPORTING
    # ==============================================
    
    def get_inventory_summary(self):
        """Get summary of ticket inventory status"""
        query = '''
        SELECT 
            availability_status,
            COUNT(*) as count,
            AVG(current_price) as avg_price,
            MIN(departure_time) as earliest_departure,
            MAX(departure_time) as latest_departure
        FROM available_tickets
        GROUP BY availability_status
        '''
        return self.execute_query(query)
    
    def get_popular_routes(self, limit=10):
        """Get most popular routes based on bookings"""
        query = '''
        SELECT 
            from_station,
            to_station,
            COUNT(*) as total_bookings,
            AVG(paid_price) as avg_price,
            COUNT(CASE WHEN booking_status = 'confirmed' THEN 1 END) as active_bookings
        FROM booked_tickets
        GROUP BY from_station, to_station
        ORDER BY total_bookings DESC
        LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def get_revenue_summary(self, start_date=None, end_date=None):
        """Get revenue summary for specified period"""
        query = '''
        SELECT 
            transaction_type,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM transaction_info
        WHERE status = 'completed'
        '''
        params = []
        
        if start_date:
            query += " AND DATE(transaction_time) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(transaction_time) <= ?"
            params.append(end_date)
        
        query += " GROUP BY transaction_type ORDER BY total_amount DESC"
        
        return self.execute_query(query, tuple(params))
    
    

def run_inventory_demo():
    """Demonstrate the enhanced inventory management features"""
    
    print("=" * 70)
    print("UKConnect Rail Enhanced Database Demo")
    print("=" * 70)
    
    # Initialize database connection
    db = UKConnectDB()
    if not db.connect():
        print("Failed to connect to database!")
        return
    
    try:
        print("\n🎫 1. AVAILABLE TICKETS SEARCH")
        print("-" * 40)
        
        # Search available tickets
        print("Searching London to Manchester tickets:")
        available = db.search_available_tickets("london", "manchester", limit=5)
        for ticket in available:
            print(f"  ✅ {ticket['train_number']}: {ticket['from_station']} → {ticket['to_station']}")
            print(f"     Departure: {ticket['departure_time']}, Seat: {ticket['seat_number']}{ticket['carriage']}")
            print(f"     Type: {ticket['ticket_type']}, Price: £{ticket['current_price']}")
        
        print("\n📋 2. BOOKING WORKFLOW")
        print("-" * 40)
        
        if available:
            # Try to book the first available ticket
            ticket_to_book = available[0]
            print(f"Attempting to book ticket ID {ticket_to_book['id']}...")
            
            booking_result = db.book_ticket("james.thompson@email.co.uk", ticket_to_book['id'])
            if 'success' in booking_result:
                print(f"  ✅ Booking successful!")
                print(f"     Booking Reference: {booking_result['booking_reference']}")
                print(f"     Route: {booking_result['ticket_details']['from_station']} → {booking_result['ticket_details']['to_station']}")
            else:
                print(f"  ❌ Booking failed: {booking_result['error']}")
        
        print("\n💰 3. INVENTORY SUMMARY")
        print("-" * 40)
        
        # Show inventory status
        inventory = db.get_inventory_summary()
        for status in inventory:
            print(f"  {status['availability_status']}: {status['count']} tickets, £{status['avg_price']:.2f} avg price")
        
        print("\n📊 4. POPULAR ROUTES")
        print("-" * 40)
        
        routes = db.get_popular_routes(5)
        for route in routes:
            print(f"  {route['from_station']} → {route['to_station']}: {route['total_bookings']} bookings, £{route['avg_price']:.2f} avg")
        
        print("\n💳 5. REVENUE SUMMARY")
        print("-" * 40)
        
        revenue = db.get_revenue_summary()
        for rev in revenue:
            print(f"  {rev['transaction_type']}: {rev['transaction_count']} transactions, £{rev['total_amount']:.2f} total")
        
        print("\n✅ Enhanced inventory demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_inventory_demo()