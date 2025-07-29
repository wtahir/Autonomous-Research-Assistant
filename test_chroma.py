from rag.vector_store import VectorStoreManager
vector_store = VectorStoreManager()
print(len(vector_store.vector_store.get()['ids']))  # Should show ~100
results = vector_store.similarity_search("latest AI trend", k=10)
print([doc.metadata["title"] for doc in results])