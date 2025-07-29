# from langchain_community.vectorstores import FAISS
# from langchain_openai import AzureOpenAIEmbeddings
# import os
# from typing import Dict, List
# from dotenv import load_dotenv

# load_dotenv()

# class VectorStoreManager:
#     def __init__(self, persist_dir="data/vector_store"):
#         # Initialize embeddings
#         self.embeddings = AzureOpenAIEmbeddings(
#             azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#             api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#             api_version="2024-02-01",
#             azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
#             model="text-embedding-3-large"
#         )
        
#         # Initialize vector store
#         self.persist_dir = persist_dir
#         self.vector_store = None
        
#         # Load existing vector store if available
#         if os.path.exists(self.persist_dir):
#             self.vector_store = FAISS.load_local(
#                 self.persist_dir, 
#                 self.embeddings,
#                 allow_dangerous_deserialization=True
#             )

#     def add_documents(self, documents: List[Dict]):
#         """Add documents to vector store"""
#         if not self.vector_store:
#             # Create new vector store if none exists
#             from langchain.docstore.document import Document
#             docs = [Document(
#                 page_content=doc["content"],
#                 metadata={"source": doc.get("url", "")}
#             ) for doc in documents]
            
#             self.vector_store = FAISS.from_documents(
#                 docs, 
#                 self.embeddings
#             )
#         else:
#             # Add to existing vector store
#             self.vector_store.add_documents(documents)
        
#         # Save the updated vector store
#         self.vector_store.save_local(self.persist_dir)

#     def similarity_search(self, query: str, k: int = 5):
#         """Search for similar documents"""
#         if not self.vector_store:
#             return []
#         return self.vector_store.similarity_search(query, k=k)

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import logging
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class VectorStoreManager:
    def __init__(self, persist_dir: str = "data/vector_store"):
        try:
            required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_EMBEDDING_DEPLOYMENT"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing environment variables: {missing_vars}")

            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01",
                azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
                model="text-embedding-3-large",
                dimensions=1536
            )
            self.persist_dir = Path(persist_dir)
            self.collection_name = "market_research"
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_dir)
            )
            logger.info(f"VectorStoreManager initialized with persist_dir: {self.persist_dir}")

        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise

    def add_documents(self, documents: List[Dict]):
        if not documents:
            logger.warning("No documents provided")
            return
        try:
            docs = [
                Document(
                    page_content=str(doc.get("content", "")),
                    metadata={
                        "source": str(doc.get("url", "")),
                        "title": str(doc.get("title", "")),
                        "authors": ", ".join(doc.get("authors", []))  # Convert list to string
                    }
                ) for doc in documents if isinstance(doc, dict) and doc.get("content")
            ]
            if not docs:
                raise ValueError("No valid documents found")
            self.vector_store.add_documents(docs)
            logger.info(f"Added {len(docs)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 10) -> List[Document]:
        if not query or not isinstance(query, str):
            raise ValueError("Invalid query")
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(results)} results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Search failed for query {query}: {str(e)}")
            return []