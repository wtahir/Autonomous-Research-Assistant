import os
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import List, Dict
import json
import requests
import feedparser

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAgent:
    """
    A specialized agent for conducting academic research via arXiv and Azure OpenAI.
    """

    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01"
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        logger.info("SearchAgent initialized successfully")

    def run(self, query: str, max_results: int = 5) -> List[Dict]:
        """Main entry point to execute a research query"""
        try:
            logger.info(f"Executing search for query: {query}")

            # Step 1: Generate search queries
            queries = self._generate_search_queries(query)
            logger.info(f"Generated search queries: {queries}")

            # Step 2: Search arXiv for each query
            all_results = []
            for q in queries:
                results = self._arxiv_search(q, max_results)
                all_results.extend(results)

            # Step 3: Analyze and summarize
            analysis = self._analyze_results(query, all_results)

            # Step 4: Format
            formatted_results = self._format_results(all_results)
            logger.info(f"Search completed. Found {len(formatted_results)} results.")

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RuntimeError(f"Search execution failed: {str(e)}")

    def _generate_search_queries(self, topic: str) -> List[str]:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "Generate 2 detailed research search query variations."},
                {"role": "user", "content": topic}
            ],
            temperature=0.7,
            max_tokens=100
        )
        queries = response.choices[0].message.content.strip().split("\n")
        return [q.strip("- ").strip() for q in queries if q.strip()]

    def _arxiv_search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {
            "search_query": query,
            "max_results": max_results,
            "sortBy": "relevance"
        }
        response = requests.get("http://export.arxiv.org/api/query", params=params)
        feed = feedparser.parse(response.text)

        return [{
            "title": entry.title,
            "url": entry.id,
            "authors": [author.name for author in entry.authors],
            "summary": entry.summary
        } for entry in feed.entries]
    

    def _analyze_results(self, query: str, results: List[Dict]) -> Dict:
        content = json.dumps(results[:3], indent=2)  # limit to 3 for brevity
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "Summarize the key findings from academic search results."},
                {"role": "user", "content": f"Query: {query}\n\nResults:\n{content}"}
            ],
            temperature=0.3
        )
        return {
            "summary": response.choices[0].message.content
        }

    def _format_results(self, raw_results: List[Dict]) -> List[Dict]:
        formatted = []
        for i, result in enumerate(raw_results):
            formatted.append({
                "title": result["title"],
                "url": result["url"],
                "content": result["summary"][:300] + "...",
                "authors": result["authors"],
                "relevance_score": self._calculate_relevance(result["summary"]),
                "quality_score": self._calculate_quality(result["summary"]),
            })
        return sorted(formatted, key=lambda x: x["relevance_score"], reverse=True)

    def _calculate_relevance(self, content: str) -> float:
        return 0.9  # Placeholder

    def _calculate_quality(self, content: str) -> float:
        return 0.8  # Placeholder


# Example usage
if __name__ == "__main__":
    agent = SearchAgent()
    results = agent.run("latest AI trends in 2025")
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"\nTitle: {r['title']}")
        print(f"URL: {r['url']}")
        print(f"Score: {r['relevance_score']:.2f}")
        print(f"Summary: {r['content'][:100]}...")


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