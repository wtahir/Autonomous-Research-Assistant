from rag.vector_store import VectorStoreManager
from agents.search_agent import SearchAgent
import json
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_papers(papers: list[dict], directory: str = "data/raw"):
    os.makedirs(directory, exist_ok=True)
    for i, paper in enumerate(papers):
        try:
            filename = f"paper_{i+1}.json"
            filepath = os.path.join(directory, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(paper, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved paper {i+1} to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save paper {i+1}: {str(e)}")

def load_papers(directory: str = "data/raw") -> list[dict]:
    papers = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(directory, filename), encoding='utf-8') as f:
                        papers.append(json.load(f))
                    logger.info(f"Loaded paper from {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
    return papers

def main():
    vector_store = VectorStoreManager(persist_dir="data/vector_store")
    search_agent = SearchAgent()
    query = "AI evolution 2024"
    logger.info(f"Fetching 100 papers for query: {query}")
    
    # Fetch up to 100 papers
    papers = search_agent.run(query=query, max_results=100)
    
    # If fewer than 100, try additional queries
    if len(papers) < 100:
        logger.warning(f"Fetched only {len(papers)} papers, attempting to fetch more...")
        additional_queries = [
            "artificial intelligence trends 2024",
            "machine learning advancements 2024",
            "deep learning evolution 2024"
        ]
        for additional_query in additional_queries:
            if len(papers) >= 100:
                break
            remaining = 100 - len(papers)
            additional_papers = search_agent.run(query=additional_query, max_results=remaining)
            papers.extend([p for p in additional_papers if p not in papers])  # Avoid duplicates
            logger.info(f"Fetched {len(additional_papers)} papers for query: {additional_query}")
    
    logger.info(f"Total papers fetched: {len(papers)}")
    
    # Save papers to data/raw/
    save_papers(papers)
    
    # Load papers from data/raw/
    loaded_papers = load_papers()
    if not loaded_papers:
        logger.error("No papers loaded from data/raw/")
        return
    
    # Add papers to Chroma
    vector_store.add_documents(loaded_papers)
    logger.info(f"Added {len(loaded_papers)} papers to Chroma database")

if __name__ == "__main__":
    main()