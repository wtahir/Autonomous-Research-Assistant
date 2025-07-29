from typing import List, Dict
import logging
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from arxiv import Client, Search, SortCriterion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class SearchAgent:
    def __init__(self):
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01"
            )
            self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            self.arxiv_client = Client()
            logger.info("SearchAgent initialized successfully")
        except Exception as e:
            logger.error(f"SearchAgent initialization failed: {str(e)}")
            raise

    def run(self, query: str, max_results: int = 10) -> List[Dict]:
        if not query:
            logger.warning("Empty query provided")
            return []

        try:
            # Perform arXiv search
            search = Search(
                query=query,
                max_results=max_results,
                sort_by=SortCriterion.SubmittedDate
            )
            results = list(self.arxiv_client.results(search))
            if not results:
                logger.warning(f"No results found for query: {query}")
                return []

            # Compute relevance scores using embeddings
            query_embedding = self._get_embedding(query)
            processed_results = []
            for entry in results:
                try:
                    summary = entry.summary or ""
                    content_embedding = self._get_embedding(summary)
                    relevance_score = self._cosine_similarity(query_embedding, content_embedding)
                    processed_results.append({
                        "title": entry.title,
                        "content": summary,
                        "authors": [author.name for author in entry.authors],
                        "url": entry.pdf_url,
                        "source": "arxiv",
                        "relevance_score": relevance_score,
                        "quality_score": 0.7,  # Placeholder, improve if needed
                        "published": entry.published.isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error processing entry {entry.title}: {str(e)}")
                    continue

            logger.info(f"Processed {len(processed_results)} results for query: {query}")
            return processed_results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            return [0.0] * 1536  # Fallback dimension

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        try:
            from numpy import dot
            from numpy.linalg import norm
            return dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        except Exception:
            return 0.5  # Fallback score

# if __name__ == "__main__":
#     agent = SearchAgent()
#     results = agent.run("Gaming industry trend")
#     print(f"\nFound {len(results)} papers:")
#     for i, paper in enumerate(results, 1):
#         print(f"\n{i}. {paper['title']}")
#         print(f"   Score: {paper['relevance_score']:.2f} (Quality: {paper['quality_score']:.2f})")
#         print(f"   Authors: {', '.join(paper['authors'][:3])}" + ("..." if len(paper['authors']) > 3 else ""))
#         print(f"   Published: {paper.get('published', 'N/A')}")


# simple search agent

# import os
# from openai import AzureOpenAI
# from dotenv import load_dotenv
# from typing import List, Dict
# import json
# import requests
# import feedparser  # Add this at the top

# # Load configuration
# load_dotenv()

# class SimpleSearchAgent:
#     def __init__(self):
#         self.client = AzureOpenAI(
#             azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#             api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#             api_version="2024-02-01"
#         )
#         self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

#     def search(self, query: str) -> Dict:
#         """Execute a research query and return structured results"""
#         try:
#             # Step 1: Generate search queries
#             queries = self._generate_search_queries(query)
#             print(f"Generated search queries: {queries}")

#             # Step 2: Mock web search (replace with real API)
#             results = {q: self._arxiv_search(q) for q in queries}

#             # Step 3: Analyze results
#             analysis = self._analyze_results(query, results)
            
#             return {
#                 "query": query,
#                 "search_queries": queries,
#                 "results": results,
#                 "analysis": analysis
#             }

#         except Exception as e:
#             return {"error": str(e)}

#     def _generate_search_queries(self, topic: str) -> List[str]:
#         """Generate multiple search query variations"""
#         response = self.client.chat.completions.create(
#             model=self.deployment,
#             messages=[{
#                 "role": "system",
#                 "content": "Generate 2 search query variations for research purposes."
#             }, {
#                 "role": "user",
#                 "content": topic
#             }],
#             temperature=0.7,
#             max_tokens=100
#         )
#         return response.choices[0].message.content.split("\n")

#     def _mock_web_search(self, queries: List[str]) -> Dict[str, List[Dict]]:
#         """Simulate web search results (replace with actual API call)"""
#         return {
#             query: [
#                 {
#                     "title": f"Result about {query}",
#                     "url": f"https://example.com/{query.replace(' ', '-')}",
#                     "snippet": f"This is a mock result about {query}"
#                 }
#                 for _ in range(2)  # 2 mock results per query
#             ]
#             for query in queries
#         }
    

#     def _arxiv_search(self, query: str) -> List[Dict]:
#         params = {
#             "search_query": query,
#             "max_results": 5,
#             "sortBy": "relevance"
#         }
#         response = requests.get("http://export.arxiv.org/api/query", params=params)
        
#         # Parse the XML response
#         feed = feedparser.parse(response.text)

#         # Extract entries
#         return [{
#             "title": entry.title,
#             "url": entry.id,
#             "authors": [author.name for author in entry.authors],
#             "summary": entry.summary
#         } for entry in feed.entries]
    
#     def _news_search(self,query: str) -> List[Dict]:
#         params = {
#             "q": query,
#             "apiKey": os.getenv("NEWSAPI_KEY"),
#             "pageSize": 5,
#             "sortBy": "relevancy"
#         }
#         response = requests.get(
#             "https://newsapi.org/v2/everything",
#             params=params
#         )
#         return [{
#             "title": a["title"],
#             "url": a["url"],
#             "snippet": a["description"],
#             "date": a["publishedAt"]
#         } for a in response.json().get("articles", [])]
    

#     def _google_search(self, query: str, api_key: str) -> List[Dict]:
#             params = {
#                 "q": query,
#                 "api_key": os.getenv("SERPAPI_KEY"),
#                 "num": 5  # Number of results
#             }
#             response = requests.get("https://serpapi.com/search", params=params)
#             return [{
#                 "title": r.get("title"),
#                 "url": r.get("link"),
#                 "snippet": r.get("snippet")
#             } for r in response.json().get("organic_results", [])]
    
#     def _google_custom_search(self, query: str) -> List[Dict]:
#         params = {
#             "q": query,
#             "key": os.getenv("GOOGLE_API_KEY"),
#             "cx": os.getenv("GOOGLE_CSE_ID"),  # Custom Search Engine ID
#             "num": 5
#         }
#         response = requests.get(
#             "https://www.googleapis.com/customsearch/v1",
#             params=params
#         )
#         return [{
#             "title": r["title"],
#             "url": r["link"],
#             "snippet": r["snippet"]
#         } for r in response.json().get("items", [])]


#     def _analyze_results(self, query: str, results: Dict) -> Dict:
#         """Analyze and summarize findings"""
#         response = self.client.chat.completions.create(
#             model=self.deployment,
#             messages=[{
#                 "role": "system",
#                 "content": "Analyze these search results and extract key insights."
#             }, {
#                 "role": "user",
#                 "content": f"Original query: {query}\n\nResults:\n{json.dumps(results, indent=2)}"
#             }],
#             temperature=0.3
#         )
#         return {
#             "summary": response.choices[0].message.content,
#             "key_points": []  # Could extract these separately
#         }

# if __name__ == "__main__":
#     agent = SimpleSearchAgent()
#     research = agent.search("latest AI trends in 2025")
#     print("\nResearch Results:")
#     print(json.dumps(research, indent=2))