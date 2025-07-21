from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import pickle
import os

class VectorStoreManager:
    def __init__(self, persist_dir="data/vector_store"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.persist_dir = persist_dir
        self.vector_store = None
        
        if os.path.exists(persist_dir):
            self.vector_store = self._load_vector_store()
    
    def _load_vector_store(self):
        """Load existing vector store from disk"""
        return FAISS.load_local(self.persist_dir, self.embeddings)
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc["url"]} for doc in documents]
        
        splits = text_splitter.create_documents(texts, metadatas=metadatas)
        
        if self.vector_store:
            self.vector_store.add_documents(splits)
        else:
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
        
        self.vector_store.save_local(self.persist_dir)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.vector_store:
            return []
            
        docs = self.vector_store.similarity_search(query, k=k)
        return [{"content": doc.page_content, "source": doc.metadata["source"]} for doc in docs]