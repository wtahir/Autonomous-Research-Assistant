from rag.vector_store import VectorStoreManager
from agents.search_agent import SearchAgent

def initialize():
    search_agent = SearchAgent()
    vector_store = VectorStoreManager()
    
    # Get initial documents
    papers = search_agent.run("economics 2024")
    
    # Prepare documents in correct format
    documents_to_add = [
        {
            "content": f"{p['title']}\n\n{p['content']}", 
            "url": p["url"]
        } 
        for p in papers
    ]
    
    # Add to vector store
    vector_store.add_documents(documents_to_add)
    print(f"Initialized vector store with {len(papers)} documents")

if __name__ == "__main__":
    initialize()