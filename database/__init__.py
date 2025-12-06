"""
Database module for the customer support system.
Contains database utilities and vector database functionality.
"""

try:
    from .vector_db import VectorDB
    from .database import UKConnectDB, run_inventory_demo

    __all__ = ['VectorDB', 'UKConnectDB', 'run_inventory_demo']
except ImportError as e:
    print(f"Warning: Could not import database components: {e}")
    __all__ = []