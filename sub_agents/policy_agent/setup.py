"""
Vector Database Setup for Policy Agent
Direct copy from notebook cells #14-16 with minimal changes for internal imports.
"""

import json
import os

# Handle imports - use direct imports instead of package imports
import sys

# Add required paths to import modules directly
production_path = os.path.join(os.path.dirname(__file__), '../..')
database_path = os.path.join(production_path, 'database')
tools_path = os.path.join(production_path, 'tools')

# Add paths if not already present
for path in [production_path, database_path, tools_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Direct imports
from vector_db import VectorDB
from policy_search import set_vector_db

def setup_policy_vector_db():
    """
    Setup the policy vector database exactly as done in the notebook.
    
    Returns:
        VectorDB: Initialized and loaded vector database instance
    """
    # Load the transformed dataset (copied from notebook cell #14)
    data_path = os.path.join(os.path.dirname(__file__), '../../database/ukconnect_rag_chunks.json')
    with open(data_path, 'r') as f:
        transformed_dataset = json.load(f)

    print("✅ Policy knowledge dataset loaded")
    print(f"📊 Dataset contains {len(transformed_dataset)} knowledge chunks")

    # Check if vector database exists and is valid
    vector_db_path = os.path.join(os.path.dirname(__file__), '../../database/vector_db.pkl')
    vector_db_exists = os.path.exists(vector_db_path)
    
    if vector_db_exists:
        print("Found existing vector database, will attempt to load from disk.")

    # Initialize the VectorDB (copied from notebook cell #16)
    base_db = VectorDB("base_db")

    # Load and process the data (copied from notebook cell #16)
    base_db.load_data(transformed_dataset)
    set_vector_db(base_db)
    
    print("✅ Vector database setup completed")
    return base_db

def initialize_policy_agent():
    """
    Initialize the policy agent with vector database setup.
    This function combines the vector DB setup with agent creation.
    """
    # Setup vector database first
    vector_db = setup_policy_vector_db()
    
    # Import and create the policy agent
    from .agent import create_policy_agent
    agent = create_policy_agent()
    
    print("✅ Policy agent initialized with vector database")
    return agent, vector_db