# Tutorial 2: Database & RAG Setup (25 min)

## 🎯 Overview
This tutorial covers setting up the hybrid data architecture that powers the UKConnect system: relational database for operational data and vector database for knowledge retrieval.

## 🏗️ What You'll Learn
- Database schema design for customer support
- Vector database setup for RAG (Retrieval-Augmented Generation)
- Data population and initialization
- Integration testing

## 📊 Database Architecture

### Dual Database Approach
```
┌─────────────────┐    ┌─────────────────┐
│ Relational DB   │    │ Vector Database │
│ (SQLite/PG)     │    │ (Embeddings)    │
├─────────────────┤    ├─────────────────┤
│ • Customers     │    │ • Policy Docs   │
│ • Bookings      │    │ • FAQ Content   │
│ • Transactions  │    │ • Knowledge Base│
│ • Train Data    │    │ • Help Articles │
└─────────────────┘    └─────────────────┘
```

## 🗄️ Relational Database Setup

### Schema Overview
The system uses 4 core tables:

#### 1. **customers** - Customer profile data
```sql
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    address TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **bookings** - Travel bookings and reservations
```sql
CREATE TABLE bookings (
    booking_id TEXT PRIMARY KEY,
    customer_id TEXT,
    departure_station TEXT,
    arrival_station TEXT,
    departure_datetime TIMESTAMP,
    ticket_type TEXT,
    price DECIMAL(10,2),
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

#### 3. **transactions** - Payment and refund records
```sql
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    booking_id TEXT,
    amount DECIMAL(10,2),
    transaction_type TEXT,
    payment_method TEXT,
    status TEXT,
    processed_at TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
```

#### 4. **fares** - Pricing and route information
```sql
CREATE TABLE fares (
    route_id INTEGER PRIMARY KEY,
    departure_station TEXT,
    arrival_station TEXT,
    distance_miles INTEGER,
    standard_price DECIMAL(10,2),
    flexible_price DECIMAL(10,2)
);
```

### Database Initialization
```bash
# Initialize schema and populate sample data
cd production-ai-customer-support
python -c "from utils.create_schema import create_database_schema; create_database_schema()"
python -c "from utils.populate_data import populate_data; populate_data()"
```

## 🔍 Vector Database Setup

### Purpose & Technology
- **Semantic search** for company policies and documentation
- **Google Embeddings API** for vector generation
- **Pickle storage** for development (production uses vector DBs)

### Document Processing Pipeline
```
Policy Documents → Text Chunking → Embeddings → Vector Storage
```

### Implementation Steps

#### 1. **Document Preparation**
```python
# Located in: database/UKConnect_policy.txt
# Contains: Refund policies, terms & conditions, fare rules
```

#### 2. **Chunking Strategy**
```python
# From utils/chunking_data.py
- Chunk size: 500-1000 characters
- Overlap: 100 characters
- Preserve context boundaries
```

#### 3. **Vector Generation**
```python
# From database/vector_db.py
import google.generativeai as genai

def generate_embeddings(text_chunks):
    embeddings = []
    for chunk in text_chunks:
        result = genai.embed_content(
            model="models/embedding-001",
            content=chunk
        )
        embeddings.append(result['embedding'])
    return embeddings
```

### Vector Database Initialization
```bash
# Setup vector database for policy documents
python -c "from database.vector_db import setup_vector_database; setup_vector_database()"
```

## 🔧 Configuration Setup

### Environment Variables
Create `.env` file with required configurations:
```bash
# API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration  
DATABASE_URL=sqlite:///database/ukconnect_rail.db

# Vector Database
VECTOR_DB_PATH=database/vector_db.pkl
```

### Directory Structure
```
production-ai-customer-support/
├── database/
│   ├── ukconnect_rail.db          # SQLite database
│   ├── vector_db.pkl              # Vector embeddings
│   ├── UKConnect_policy.txt       # Policy documents
│   ├── ukconnect_qa_pairs.json    # Q&A pairs
│   └── ukconnect_rag_chunks.json  # Processed chunks
```

## 📝 Data Population

### Sample Data Overview
- **15 realistic customers** with complete profiles
- **25+ train bookings** across different scenarios
- **Route data** for major UK rail connections
- **Transaction history** for testing refunds/modifications

### Customer Data Examples
```python
# From utils/populate_data.py
customers = [
    {
        "customer_id": "CUS001",
        "name": "James Thompson", 
        "email": "james.thompson@email.co.uk",
        "address": "45 Baker Street, London, W1U 7EW",
        "phone": "+44 20 7946 0958"
    },
    # ... 14 more customers
]
```

### Booking Scenarios
```python
bookings = [
    {
        "booking_id": "UKC001",
        "customer_id": "CUS001",
        "departure_station": "London Euston",
        "arrival_station": "Manchester Piccadilly",
        "ticket_type": "Standard",
        "price": 85.50,
        "status": "Active"
    },
    # ... complex scenarios for testing
]
```

## 🧪 Testing the Setup

### Database Verification
```python
# Test database connectivity
python -c "
from database.database import DatabaseManager
db = DatabaseManager()
print('Customers:', len(db.get_all_customers()))
print('Bookings:', len(db.get_all_bookings()))
"
```

### Vector Database Testing
```python
# Test vector search functionality
python -c "
from database.vector_db import VectorDatabase
vdb = VectorDatabase()
results = vdb.search('refund policy', top_k=3)
print('Search results:', len(results))
"
```

### Integration Test
```bash
# Run basic system test
python run_test_scenarios.py --session 1
```

## 🔍 RAG System Deep Dive

### Retrieval Process
1. **Query Analysis**: Extract semantic meaning from customer question
2. **Vector Search**: Find relevant policy documents using similarity
3. **Context Preparation**: Combine retrieved chunks with query context
4. **Generation**: LLM generates response using retrieved information

### Performance Optimization
- **Chunk Overlap**: Ensures context continuity
- **Relevance Filtering**: Threshold-based result filtering  
- **Caching**: Frequent queries cached for speed
- **Batch Processing**: Efficient embedding generation

## 📊 Monitoring & Maintenance

### Health Checks
```python
# Database health monitoring
def check_database_health():
    # Verify table integrity
    # Check data consistency  
    # Monitor query performance
    pass
```

### Vector Database Maintenance
```python
# Periodic vector database updates
def update_vector_database():
    # Re-process modified documents
    # Regenerate embeddings
    # Update search indices
    pass
```

## 🚀 Next Steps

With your database infrastructure ready:
- **Tutorial 3**: Build the Policy Agent for RAG-powered responses
- **Tutorial 4**: Create the Ticket Agent for operational tasks
- **Tutorial 5**: Implement the Master Agent orchestrator

## 💡 Key Takeaways

1. **Hybrid approach** combines structured data (relational) with unstructured knowledge (vector)
2. **Proper chunking** is critical for effective RAG performance
3. **Sample data** should reflect real-world usage patterns
4. **Health monitoring** ensures system reliability
5. **Environment configuration** enables easy deployment across environments

Your data foundation is now ready to power intelligent customer support interactions!