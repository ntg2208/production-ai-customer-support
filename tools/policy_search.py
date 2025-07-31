"""
Policy Search Tool
Direct copy from external agent_tools.py for policy knowledge search functionality.
"""

from google.adk.tools import FunctionTool

# Global vector database instance
_vector_db = None

def set_vector_db(vector_db):
    """Set the VectorDB instance for policy searches"""
    global _vector_db
    _vector_db = vector_db

def search_policy_knowledge(query: str, k: int) -> str:
    """
    Search the UKConnect policy knowledge base for information.
    
    Args:
        query: The search query for policy information
        k: Number of results to return
    
    Returns:
        Formatted search results from the policy knowledge base
    """
    global _vector_db
    
    if _vector_db is None:
        return "Error: Policy knowledge base not initialized. Please contact support."
    
    try:
        # Handle default value internally
        if k <= 0:
            k = 5
        
        results = _vector_db.search(query, k=k)
        
        if not results:
            return f"No policy information found for query: {query}"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            similarity = result['similarity']
            
            # Format the result for the agent
            result_text = f"""
Result {i} (Relevance: {similarity:.3f}):
Section: {metadata.get('section', 'Unknown')}
Question: {metadata.get('question', 'N/A')}
Answer: {metadata.get('answer', 'N/A')}
Topics: {', '.join(metadata.get('topics', []))}
"""
            formatted_results.append(result_text.strip())
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching policy knowledge base: {str(e)}"

# Policy Knowledge Tool
search_policy_knowledge_tool = FunctionTool(search_policy_knowledge)