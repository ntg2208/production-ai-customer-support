#!/usr/bin/env python3
"""
UKConnect Rail Database Schema Creation v2.0
This script creates the enhanced database schema with available tickets inventory system.
"""

import sqlite3
import sys
from datetime import datetime

def create_database_schema(db_path=None):
    """Create the enhanced database schema. If no path provided, uses the default database location."""
    if db_path is None:
        import os
        # Default to the database directory relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, '..', 'database', 'ukconnect_rail.db')
        db_path = os.path.abspath(db_path)
    """
    Create the enhanced database schema for UKConnect Rail booking system with inventory management.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        # Connect to SQLite database (creates file if doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Creating UKConnect Rail database schema v2.0...")
        print(f"Database path: {db_path}")
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create Customer_Info table (with customer_id as UKC format)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id VARCHAR(6) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            address TEXT NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Available_Tickets table (NEW - for inventory management)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS available_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number VARCHAR(20) NOT NULL,
            from_station VARCHAR(100) NOT NULL,
            to_station VARCHAR(100) NOT NULL,
            departure_time TIMESTAMP NOT NULL,
            arrival_time TIMESTAMP NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            carriage VARCHAR(10) NOT NULL,
            ticket_type VARCHAR(20) NOT NULL CHECK (ticket_type IN ('standard', 'flexible', 'first_class')),
            base_price DECIMAL(10,2) NOT NULL,
            current_price DECIMAL(10,2) NOT NULL,
            availability_status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (availability_status IN ('available', 'reserved', 'sold', 'blocked')),
            booking_class VARCHAR(20) NOT NULL CHECK (booking_class IN ('economy', 'standard', 'first_class')),
            amenities TEXT, -- JSON string for seat amenities (wifi, power, table, etc.)
            route_distance_km INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Booked_Tickets table (renamed from ticket_info with enhancements)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS booked_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_reference VARCHAR(10) NOT NULL UNIQUE,
            customer_id INTEGER NOT NULL,
            original_available_ticket_id INTEGER, -- Reference to the original available ticket
            train_number VARCHAR(20) NOT NULL,
            from_station VARCHAR(100) NOT NULL,
            to_station VARCHAR(100) NOT NULL,
            departure_time TIMESTAMP NOT NULL,
            estimated_arrival_time TIMESTAMP NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            carriage VARCHAR(10) NOT NULL,
            ticket_type VARCHAR(20) NOT NULL CHECK (ticket_type IN ('standard', 'flexible', 'first_class')),
            original_price DECIMAL(10,2) NOT NULL,
            paid_price DECIMAL(10,2) NOT NULL, -- Actual price paid (may include discounts)
            booking_status VARCHAR(20) NOT NULL CHECK (booking_status IN ('confirmed', 'pending', 'cancelled', 'refunded', 'modified', 'used')),
            travel_status VARCHAR(20) NOT NULL DEFAULT 'upcoming' CHECK (travel_status IN ('upcoming', 'in_progress', 'completed', 'missed', 'cancelled')),
            purchase_date TIMESTAMP NOT NULL,
            check_in_time TIMESTAMP, -- When customer checked in for travel
            boarding_time TIMESTAMP, -- When customer actually boarded
            special_requirements TEXT, -- Wheelchair access, assistance, dietary needs, etc.
            group_booking_id VARCHAR(20), -- For linking multiple tickets in one booking
            is_return_ticket BOOLEAN DEFAULT 0,
            return_ticket_id INTEGER, -- Reference to return journey ticket
            loyalty_points_earned INTEGER DEFAULT 0,
            loyalty_points_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customer_info (id) ON DELETE CASCADE,
            FOREIGN KEY (original_available_ticket_id) REFERENCES available_tickets (id),
            FOREIGN KEY (return_ticket_id) REFERENCES booked_tickets (id)
        )
        ''')
        
        # Create Transaction_Info table (enhanced with booking_reference and customer_id)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            customer_reference VARCHAR(6), -- CUS001, CUS002, etc.
            booked_ticket_id INTEGER, -- Changed from ticket_id to booked_ticket_id
            booking_reference VARCHAR(10), -- UKC001, UKC002, etc.
            transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'refund', 'modification', 'cancellation_fee', 'loyalty_redemption', 'loyalty_earning')),
            amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'voucher', 'apple_pay', 'google_pay', 'loyalty_points', 'corporate_account')),
            transaction_time TIMESTAMP NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'pending', 'failed', 'cancelled', 'disputed', 'refunded')),
            reference_number VARCHAR(50),
            payment_processor VARCHAR(30), -- Stripe, PayPal, etc.
            currency VARCHAR(3) DEFAULT 'GBP',
            exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
            processing_fee DECIMAL(10,2) DEFAULT 0.00,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customer_info (id) ON DELETE CASCADE,
            FOREIGN KEY (booked_ticket_id) REFERENCES booked_tickets (id) ON DELETE CASCADE
        )
        ''')
        
        # Create Refund Rules table (enhanced)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS refund_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_type VARCHAR(20) NOT NULL,
            hours_before_departure INTEGER NOT NULL,
            refund_percentage INTEGER NOT NULL CHECK (refund_percentage >= 0 AND refund_percentage <= 100),
            modification_fee DECIMAL(10,2) DEFAULT 0.00,
            cancellation_fee DECIMAL(10,2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT 1,
            effective_date DATE NOT NULL,
            expiry_date DATE,
            rule_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Train_Schedules table (NEW - for managing train services)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS train_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number VARCHAR(20) NOT NULL,
            service_name VARCHAR(100), -- e.g., "London to Edinburgh Express"
            operator VARCHAR(50) NOT NULL, -- e.g., "Virgin Trains", "CrossCountry"
            from_station VARCHAR(100) NOT NULL,
            to_station VARCHAR(100) NOT NULL,
            departure_time TIME NOT NULL,
            arrival_time TIME NOT NULL,
            journey_duration INTEGER NOT NULL, -- in minutes
            distance_km INTEGER,
            operating_days VARCHAR(20) NOT NULL, -- e.g., "Mon-Fri", "Daily", "Weekends"
            service_frequency VARCHAR(30), -- e.g., "Every 30 minutes", "Hourly"
            max_capacity INTEGER NOT NULL,
            first_class_capacity INTEGER DEFAULT 0,
            standard_class_capacity INTEGER NOT NULL,
            has_wifi BOOLEAN DEFAULT 0,
            has_catering BOOLEAN DEFAULT 0,
            has_power_sockets BOOLEAN DEFAULT 0,
            accessibility_features TEXT, -- JSON string
            service_status VARCHAR(20) DEFAULT 'active' CHECK (service_status IN ('active', 'suspended', 'cancelled', 'delayed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Booking_History table (NEW - for audit trail)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS booking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booked_ticket_id INTEGER NOT NULL,
            action VARCHAR(30) NOT NULL, -- e.g., 'booked', 'modified', 'cancelled', 'refunded'
            old_status VARCHAR(20),
            new_status VARCHAR(20),
            changed_fields TEXT, -- JSON string of what changed
            reason TEXT, -- Reason for change
            changed_by VARCHAR(20) DEFAULT 'customer', -- 'customer', 'agent', 'system'
            change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (booked_ticket_id) REFERENCES booked_tickets (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for better performance
        print("Creating indexes...")
        
        # Customer indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_email ON customer_info (email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_info (customer_id)')
        
        # Available tickets indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avail_departure ON available_tickets (departure_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avail_route ON available_tickets (from_station, to_station)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avail_status ON available_tickets (availability_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avail_train ON available_tickets (train_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avail_price ON available_tickets (current_price)')
        
        # Booked tickets indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_booking_ref ON booked_tickets (booking_reference)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_customer_id ON booked_tickets (customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_departure ON booked_tickets (departure_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_status ON booked_tickets (booking_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_travel_status ON booked_tickets (travel_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booked_group ON booked_tickets (group_booking_id)')
        
        # Transaction indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_customer ON transaction_info (customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_customer_ref ON transaction_info (customer_reference)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_ticket ON transaction_info (booked_ticket_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_booking_ref ON transaction_info (booking_reference)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_type ON transaction_info (transaction_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_time ON transaction_info (transaction_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_status ON transaction_info (status)')
        
        # Train schedules indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_train ON train_schedules (train_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_route ON train_schedules (from_station, to_station)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_departure ON train_schedules (departure_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_operator ON train_schedules (operator)')
        
        # Booking history indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_ticket ON booking_history (booked_ticket_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON booking_history (change_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_action ON booking_history (action)')
        
        # Insert enhanced refund rules
        print("Inserting enhanced refund rules...")
        
        refund_rules = [
            # Policy-compliant refund rules based on UKConnect company policy
            
            # FLEXIBLE FARES: Full refund available without fees (anytime)
            ('flexible', 0, 100, 0.00, 0.00, '2025-01-01', None, 'Flexible fares - full refund without fees anytime'),
            
            # STANDARD FARES: Full refund within 24 hours; partial refund after with fees £25-£75
            ('standard', 24, 100, 0.00, 0.00, '2025-01-01', None, 'Standard fares - full refund within 24 hours of booking'),
            ('standard', 4, 75, 0.00, 25.00, '2025-01-01', None, 'Standard fares - 75% refund 4-24 hours before departure'),
            ('standard', 0, 50, 0.00, 50.00, '2025-01-01', None, 'Standard fares - 50% refund less than 4 hours before departure'),
            
            # FIRST CLASS FARES: Full refund within 24 hours; partial refund after with fees £25-£100  
            ('first_class', 24, 100, 0.00, 0.00, '2025-01-01', None, 'First class fares - full refund within 24 hours of booking'),
            ('first_class', 4, 75, 0.00, 50.00, '2025-01-01', None, 'First class fares - 75% refund 4-24 hours before departure'),
            ('first_class', 0, 50, 0.00, 75.00, '2025-01-01', None, 'First class fares - 50% refund less than 4 hours before departure')
        ]
        
        cursor.executemany('''
        INSERT INTO refund_rules (ticket_type, hours_before_departure, refund_percentage, 
                                modification_fee, cancellation_fee, effective_date, expiry_date, rule_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', refund_rules)
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Enhanced database schema v2.0 created successfully!")
        print("\nTables created:")
        print("- customer_info (unchanged)")
        print("- available_tickets (NEW - inventory management)")
        print("- booked_tickets (enhanced from ticket_info)")
        print("- transaction_info (enhanced)")
        print("- refund_rules (enhanced)")
        print("- train_schedules (NEW - service management)")
        print("- booking_history (NEW - audit trail)")
        print("\nIndexes created for optimal query performance")
        print("Enhanced refund rules inserted with effective dates")
        
        # Display table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nTotal tables: {len(tables)}")
        
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

def verify_schema(db_path=None):
    """Verify schema. If no path provided, uses the default database location."""
    if db_path is None:
        import os
        # Default to the database directory relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, '..', 'database', 'ukconnect_rail.db')
        db_path = os.path.abspath(db_path)
    """
    Verify that all tables were created correctly in the v2 schema.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying enhanced database schema v2.0...")
        
        # Check each table exists and get column info
        tables = ['customer_info', 'available_tickets', 'booked_tickets', 'transaction_info', 
                 'refund_rules', 'train_schedules', 'booking_history']
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\n📋 {table}: {len(columns)} columns")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
        
        # Check refund rules were inserted
        cursor.execute("SELECT COUNT(*) FROM refund_rules")
        rule_count = cursor.fetchone()[0]
        print(f"\n📏 Enhanced refund rules inserted: {rule_count}")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        print(f"\n📊 Performance indexes created: {len(indexes)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("UKConnect Rail Enhanced Database Schema Creator v2.0")
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
    
    # Create enhanced schema
    success = create_database_schema(db_path)
    
    if success:
        # Verify schema
        verify_schema(db_path)
        print(f"\n🎉 Enhanced setup complete! Database ready at: {db_path}")
        print("\nKey improvements in v2.0:")
        print("✅ Available tickets inventory system")
        print("✅ Enhanced booking management with status tracking")
        print("✅ Train schedules and service management")
        print("✅ Comprehensive audit trail")
        print("✅ Advanced transaction processing")
        print("✅ Loyalty points and group booking support")
        print("\nNext steps:")
        print("1. Run populate_data.py to add comprehensive sample data")
        print("2. Update database.py with new inventory management functions")
        print("3. Test the enhanced booking and refund workflows")
    else:
        print("\n💥 Enhanced schema creation failed!")
        sys.exit(1)