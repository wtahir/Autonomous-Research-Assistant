from typing import Dict, Any, List
from openai import AzureOpenAI
import time
import os
from dotenv import load_dotenv
import logging
from rag.retriever import Retriever
from agents.search_agent import SearchAgent
from agents.analyst_agent import AnalystAgent
from agents.visualizer_agent import VisualizerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class CoordinatorAgent:
    def __init__(self):
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01"
            )
            self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            self.search_agent = SearchAgent()
            self.retriever = Retriever()
            self.analyst = AnalystAgent()
            self.visualizer = VisualizerAgent()
            logger.info("CoordinatorAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CoordinatorAgent: {str(e)}")
            raise

    def coordinate(self, query: str) -> Dict[str, Any]:
        try:
            # Step 1: Search for papers
            search_results = self.search_agent.run(query, max_results=10)
            if not search_results:
                logger.warning(f"No search results for query: {query}")
                return {"error": "No papers found"}

            # Step 2: Retrieve relevant papers from Chroma
            context = {"documents": search_results}
            retrieved_papers = self.retriever.retrieve_relevant_info(query, context)

            # Step 3: Analyze papers
            analysis = self.analyst.analyze(retrieved_papers, query)

            # Step 4: Generate visualizations
            visualizations = self.visualizer.generate_visualizations(search_results)

            # Step 5: Coordinate next steps
            context = {
                "query": query,
                "search_summary": [p["title"] for p in search_results[:3]],
                "analysis_summary": analysis.get("summary", "")
            }
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert project coordinator for data science research projects.
                    Provide strategic next steps in bullet points for:
                    1. Which agents to engage
                    2. Refining research direction
                    3. Quality control
                    4. Final synthesis"""
                },
                {"role": "user", "content": f"Context: {context}"}
            ]
            start = time.time()
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            logger.info(f"Coordinator GPT-4o call took {time.time() - start} seconds")
            next_steps = self._parse_response(response.choices[0].message.content)

            result = {
                "search_results": search_results,
                "analysis": analysis,
                "visualizations": visualizations,
                "next_steps": next_steps,
                "refinements": self._generate_refinements(context)
            }
            logger.info(f"Coordinator response: {result}")
            return result
        except Exception as e:
            logger.error(f"Coordination failed: {str(e)}")
            return {"error": f"Coordination failed: {str(e)}"}

    def _parse_response(self, content: str) -> List[str]:
        return [line.strip("-* \n") for line in content.split("\n") if line.strip()]

    def _generate_refinements(self, context: Dict) -> Dict:
        query = context.get("query", "")
        source = context.get("source", "arXiv")
        refinement = (
            f"Try '{query} site:*.edu.pk'" 
            if "pakistan" in query.lower() 
            else "Use more specific keywords"
        )
        return {
            "query_refinement": refinement,
            "suggested_source": source
        }

# if __name__ == "__main__":
#     # Test the coordinator
#     try:
#         agent = CoordinatorAgent()
#         sample_context = {
#             "query": "test query",
#             "results": ["result1", "result2"]
#         }
#         result = agent.coordinate(sample_context)
#         print("Coordination successful!")
#         print("Next steps:", result["next_steps"])
#         print("Refinements:", result["refinements"])
#     except Exception as e:
#         print(f"Test failed: {str(e)}")