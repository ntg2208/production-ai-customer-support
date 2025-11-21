#!/usr/bin/env python3
"""
UKConnect Rail Vector Database
This module contains the VectorDB class for semantic search of policy documents.
"""

import os
import pickle
import numpy as np
from google import genai
from google.genai import types
from typing import List, Dict, Any
from tqdm import tqdm

# Import model configuration
try:
    from ..config.model_config import get_embedding_model
except ImportError:
    # Fallback for standalone usage
    def get_embedding_model():
        return "gemini-embedding-001"

class VectorDB:
    """
    Vector database for semantic search using Google's Gemini embedding model.
    Handles loading, embedding, and searching of UKConnect policy documents.
    """
    
    def __init__(self, name: str, api_key: str = None):
        """
        Initialize the VectorDB instance.
        
        Args:
            name: Name identifier for this database instance
            api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        # Default to database directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, "vector_db.pkl")
        self._embedding_model = get_embedding_model()

    def load_data(self, dataset: List[Dict[str, Any]]):
        """
        Load and embed dataset into the vector database.
        
        Args:
            dataset: List of documents with structure:
                [
                    {
                        "id": "UKC_FAQ_1",
                        "text": "Question: ... Answer: ...",
                        "metadata": {
                            "question": "...",
                            "answer": "...",
                            "section": "...",
                            "topics": [...],
                            "extraction_method": "...",
                            "confidence": 0.95,
                            "token_count": 62,
                            "created_at": "..."
                        }
                    }
                ]
        """
        # Check if already loaded in memory
        if self.embeddings and self.metadata:
            print("Vector database is already loaded in memory. Skipping data loading.")
            return
            
        # Try to load from disk first if available
        if os.path.exists(self.db_path):
            try:
                print("Loading vector database from disk...")
                self.load_db()
                
                # Validate that the loaded database matches the current dataset
                if self.is_valid_for_dataset(dataset):
                    print(f"✅ Successfully loaded {len(self.metadata)} chunks from disk.")
                    return
                else:
                    print("⚠️ Loaded database doesn't match current dataset. Recreating...")
                    # Clear loaded data and continue to recreate
                    self.embeddings = []
                    self.metadata = []
                    self.query_cache = {}
                    
            except Exception as e:
                print(f"⚠️ Failed to load from disk: {e}")
                print("Will create new vector database from dataset.")
                # Continue to create new database below

        texts_to_embed = []
        metadata = []
        
        # Handle the JSON structure from ukconnect_rag_chunks.json
        with tqdm(total=len(dataset), desc="Processing chunks") as pbar:
            for item in dataset:
                # Extract text content to embed
                text_content = item.get('text', '')
                if not text_content:
                    continue
                    
                texts_to_embed.append(text_content)
                
                # Create metadata from the structure
                item_metadata = {
                    'chunk_id': item.get('id', ''),
                    'text': text_content,
                    'question': item.get('metadata', {}).get('question', ''),
                    'answer': item.get('metadata', {}).get('answer', ''),
                    'section': item.get('metadata', {}).get('section', ''),
                    'topics': item.get('metadata', {}).get('topics', []),
                    'extraction_method': item.get('metadata', {}).get('extraction_method', ''),
                    'confidence': item.get('metadata', {}).get('confidence', 0.0),
                    'token_count': item.get('metadata', {}).get('token_count', 0),
                    'created_at': item.get('metadata', {}).get('created_at', '')
                }
                metadata.append(item_metadata)
                pbar.update(1)

        self._embed_and_store(texts_to_embed, metadata)
        self.save_db()
        
        print(f"✅ Vector database created and saved. Total chunks processed: {len(texts_to_embed)}")

    def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        """
        Generate embeddings for texts and store them with metadata.
        
        Args:
            texts: List of text content to embed
            data: List of metadata corresponding to texts
        """
        batch_size = 128
        with tqdm(total=len(texts), desc="Embedding chunks") as pbar:
            result = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                for text in batch:
                    embedding_result = self.client.models.embed_content(
                        model=self._embedding_model,
                        contents=text,
                        config=types.EmbedContentConfig(output_dimensionality=768)
                    )
                    result.append(embedding_result.embeddings[0].values)
                pbar.update(len(batch))
        
        self.embeddings = np.array(result)
        self.metadata = data

    def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """
        Perform semantic search on the vector database.
        
        Args:
            query: Search query text
            k: Number of top results to return
            
        Returns:
            List of search results with metadata and similarity scores
        """
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            embedding_result = self.client.models.embed_content(
                model=self._embedding_model,
                contents=query,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            query_embedding = embedding_result.embeddings[0].values
            self.query_cache[query] = query_embedding

        if len(self.embeddings) == 0:
            raise ValueError("No data loaded in the vector database.")

        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        top_results = []
        for idx in top_indices:
            result = {
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx]),
            }
            top_results.append(result)
        
        return top_results

    def save_db(self):
        """Save the vector database to disk."""
        data = {
            "embeddings": self.embeddings.tolist(),
            "metadata": self.metadata,
            "query_cache": self.query_cache,
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)

    def load_db(self):
        """Load the vector database from disk."""
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = np.array(data["embeddings"])
        self.metadata = data["metadata"]
        self.query_cache = data["query_cache"]

    def validate_embedded_chunks(self):
        """Validate the embedded chunks for duplicates and consistency."""
        unique_contents = set()
        for meta in self.metadata:
            unique_contents.add(meta.get('text', meta.get('content', '')))
    
        print(f"Validation results:")
        print(f"Total embedded chunks: {len(self.metadata)}")
        print(f"Unique embedded contents: {len(unique_contents)}")
    
        if len(self.metadata) != len(unique_contents):
            print("Warning: There may be duplicate chunks in the embedded data.")
        else:
            print("All embedded chunks are unique.")
            
    def get_stats(self):
        """Get comprehensive statistics about the loaded data."""
        if not self.metadata:
            print("No data loaded.")
            return
            
        print(f"📊 Vector Database Statistics:")
        print(f"Total chunks: {len(self.metadata)}")
        
        # Section distribution
        sections = {}
        topics = {}
        extraction_methods = {}
        
        for meta in self.metadata:
            section = meta.get('section', 'Unknown')
            sections[section] = sections.get(section, 0) + 1
            
            item_topics = meta.get('topics', [])
            for topic in item_topics:
                topics[topic] = topics.get(topic, 0) + 1
                
            method = meta.get('extraction_method', 'Unknown')
            extraction_methods[method] = extraction_methods.get(method, 0) + 1
        
        print(f"\n📋 Sections:")
        for section, count in sorted(sections.items()):
            print(f"  - {section}: {count}")
            
        print(f"\n🏷️ Top Topics:")
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {topic}: {count}")
            
        print(f"\n🔧 Extraction Methods:")
        for method, count in sorted(extraction_methods.items()):
            print(f"  - {method}: {count}")

    def clear_cache(self):
        """Clear the query embedding cache."""
        self.query_cache = {}
        print("Query cache cleared.")
    
    def is_valid_for_dataset(self, dataset: List[Dict[str, Any]]) -> bool:
        """
        Check if the current vector database is valid for the given dataset.
        
        Args:
            dataset: The dataset to validate against
            
        Returns:
            bool: True if the database is valid for this dataset
        """
        if len(self.embeddings) == 0 or not self.metadata:
            return False
            
        # Check if the number of chunks matches
        if len(self.metadata) != len(dataset):
            print(f"Dataset size mismatch: DB has {len(self.metadata)}, dataset has {len(dataset)}")
            return False
            
        # Check if chunk IDs match (basic validation)
        db_ids = {meta.get('chunk_id', '') for meta in self.metadata}
        dataset_ids = {item.get('id', '') for item in dataset}
        
        if db_ids != dataset_ids:
            print("Dataset chunk IDs don't match the database")
            return False
            
        return True

    def get_embedding_info(self):
        """Get information about the embeddings."""
        if len(self.embeddings) == 0:
            print("No embeddings loaded.")
            return
            
        print(f"📈 Embedding Information:")
        print(f"Shape: {self.embeddings.shape}")
        print(f"Memory usage: {self.embeddings.nbytes / 1024 / 1024:.2f} MB")
        print(f"Data type: {self.embeddings.dtype}")

def create_vector_db(name: str = "ukconnect_vector_db", api_key: str = None) -> VectorDB:
    """
    Factory function to create a VectorDB instance.
    
    Args:
        name: Name for the database instance
        api_key: Google API key (optional)
        
    Returns:
        Configured VectorDB instance
    """
    return VectorDB(name, api_key)

# Example usage function
def load_ukconnect_policy_db(json_file_path: str = "ukconnect_rag_chunks.json") -> VectorDB:
    """
    Convenience function to load UKConnect policy data into VectorDB.
    
    Args:
        json_file_path: Path to the JSON file containing policy chunks
        
    Returns:
        Loaded VectorDB instance
    """
    import json
    
    # Load the transformed dataset
    with open(json_file_path, 'r') as f:
        transformed_dataset = json.load(f)
    
    # Create and load VectorDB
    vector_db = create_vector_db("ukconnect_policy")
    vector_db.load_data(transformed_dataset)
    
    return vector_db

if __name__ == "__main__":
    # Example usage
    print("UKConnect Rail Vector Database")
    print("=" * 40)
    
    # This would typically be called from another module
    # db = load_ukconnect_policy_db()
    # db.get_stats()
    # results = db.search("refund policy")
    # print(f"Found {len(results)} results")