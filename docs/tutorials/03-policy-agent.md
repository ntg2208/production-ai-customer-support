# Tutorial 3: Policy Agent Build (20 min)

## 🎯 Overview
Build the Policy Agent - a RAG-powered specialist that handles company policies, refund rules, and knowledge-based customer queries.

## 🧠 What You'll Learn
- RAG (Retrieval-Augmented Generation) implementation
- Policy document processing and search
- Agent specialization patterns
- Integration with vector database

## 🏗️ Policy Agent Architecture

```
Customer Query → Policy Agent → Vector Search → LLM Generation → Response
                      ↓
              [Vector Database]
              • Policy docs
              • FAQ content  
              • Knowledge base
```

## 🔧 Implementation

### Core Agent Setup
```python
# sub_agents/policy_agent/agent.py
from google.adk.agents import Agent
from ..database.vector_db import VectorDatabase

class PolicyAgent:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.agent = Agent(
            model="gemini-2.0-flash",
            instructions=POLICY_AGENT_PROMPT
        )
    
    def handle_query(self, query, context):
        # Retrieve relevant policy information
        relevant_docs = self.vector_db.search(query, top_k=3)
        
        # Generate contextual response
        enhanced_prompt = f"""
        Customer Query: {query}
        Context: {context}
        Relevant Policies: {relevant_docs}
        
        Provide accurate policy information based on the retrieved documents.
        """
        
        return self.agent.generate(enhanced_prompt)
```

### Key Capabilities
- **Policy Retrieval**: Search company documentation using semantic similarity
- **Refund Calculations**: Apply complex refund rules based on ticket type and timing
- **Compliance**: Ensure responses meet regulatory requirements
- **FAQ Handling**: Answer common policy questions efficiently

## 🔍 RAG Implementation Details

### Document Processing
```python
# Document chunking for optimal retrieval
def process_policy_documents():
    chunks = []
    for document in policy_docs:
        # Split into semantically meaningful chunks
        doc_chunks = chunk_document(document, size=800, overlap=100)
        chunks.extend(doc_chunks)
    return chunks
```

### Vector Search
```python
def search_policies(query, top_k=3):
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    # Find similar policy chunks
    similar_chunks = vector_search(query_embedding, top_k)
    
    return [chunk['content'] for chunk in similar_chunks]
```

## 🎯 Use Cases Handled

1. **Refund Inquiries**: "What's your refund policy?"
2. **Fare Information**: "What's the difference between Standard and Flexible tickets?"
3. **Terms & Conditions**: "Can I change my booking?"
4. **Regulatory Questions**: "What are your accessibility provisions?"

## 🧪 Testing

```bash
# Test policy agent functionality
python -c "
from sub_agents.policy_agent import PolicyAgent
agent = PolicyAgent()
response = agent.handle_query('refund policy', {})
print(response)
"
```

## 🚀 Next Steps
**Tutorial 4**: Build the Ticket Agent for operational tasks and database interactions.