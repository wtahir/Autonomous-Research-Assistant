from rag.vector_store import VectorStoreManager
from typing import List, Dict

class Retriever:
    def __init__(self):
        self.vector_store = VectorStoreManager()
    
    def retrieve_relevant_info(self, query: str, context: Dict) -> List[Dict]:
        """Retrieve relevant information from vector store"""
        # First do a simple similarity search
        base_results = self.vector_store.similarity_search(query)
        
        # Add RAG-fusion style multi-query generation
        expanded_queries = self._generate_related_queries(query)
        expanded_results = []
        
        for eq in expanded_queries:
            expanded_results.extend(self.vector_store.similarity_search(eq))
        
        # Combine and deduplicate results
        all_results = base_results + expanded_results
        unique_results = self._deduplicate_results(all_results)
        
        return unique_results
    
    def _generate_related_queries(self, query: str) -> List[str]:
        """Generate related queries for more comprehensive retrieval"""
        # In a real implementation, you'd use an LLM here
        return [
            f"different perspectives on {query}",
            f"recent developments in {query}",
            f"statistical data about {query}"
        ]
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content"""
        seen = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result["content"])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(result)
        
        return unique_results