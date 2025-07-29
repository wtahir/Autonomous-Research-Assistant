# from langgraph.graph import StateGraph
# from typing import Dict, Any, TypedDict

# from agents.search_agent import SearchAgent
# from agents.summarizer_agent import SummarizerAgent
# from agents.analyst_agent import AnalystAgent
# from agents.visualizer_agent import VisualizerAgent
# from agents.coordinator_agent import CoordinatorAgent
# from rag.retriever import Retriever

# # Optional: define state schema for type safety
# class MarketResearchState(TypedDict, total=False):
#     query: str
#     search_results: list
#     summaries: list
#     analysis: dict
#     visualizations: dict
#     final_report: dict  # or whatever coordinator outputs

# def create_market_research_workflow():
#     # Initialize all agents
#     search_agent = SearchAgent()
#     summarizer = SummarizerAgent()
#     analyst = AnalystAgent()
#     visualizer = VisualizerAgent()
#     coordinator = CoordinatorAgent()
#     retriever = Retriever()

#     # Create the stateful graph
#     workflow = StateGraph(MarketResearchState)

#     # Add nodes and transitions
#     workflow.add_node("search", lambda state: {
#         "query": state["query"],
#         "search_results": search_agent.run(state["query"])
#     })
#     workflow.add_node("retrieve", lambda state: {
#         "search_results": retriever.retrieve_relevant_info(state["query"], state)
#     })
#     workflow.add_node("summarize", lambda state: {
#         "summaries": [summarizer.summarize(doc["content"]) for doc in state["search_results"]]
#     })
#     workflow.add_node("analyze", lambda state: {
#         "analysis": analyst.analyze(state["summaries"])
#     })
#     workflow.add_node("visualize", lambda state: visualizer.generate_visualizations(state.get("raw_data_for_visualization", [])))
#     workflow.add_node("coordinate", lambda state: {"final_report": coordinator.coordinate(state)})

#     # Define flow
#     workflow.set_entry_point("search")
#     workflow.add_edge("search", "retrieve")
#     workflow.add_edge("retrieve", "summarize")
#     workflow.add_edge("summarize", "analyze")
#     workflow.add_edge("analyze", "visualize")
#     workflow.add_edge("visualize", "coordinate")
#     workflow.set_finish_point("coordinate")

#     # Compile and return
#     return workflow.compile()



from langgraph.graph import StateGraph
from typing import Dict, Any, TypedDict
import sys
from pathlib import Path
import logging

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import agents from your structure
from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.analyst_agent import AnalystAgent
from agents.visualizer_agent import VisualizerAgent
from agents.coordinator_agent import CoordinatorAgent
from rag.retriever import Retriever

logger = logging.getLogger(__name__)

class MarketResearchState(TypedDict, total=False):
    query: str
    search_results: list
    summaries: list
    analysis: dict
    visualizations: dict
    final_report: dict

def create_market_research_workflow():
    # Initialize all agents with proper config
    agents = {
        "search": SearchAgent(),
        "summarizer": SummarizerAgent(),
        "analyst": AnalystAgent(),
        "visualizer": VisualizerAgent(),
        "coordinator": CoordinatorAgent(),
        "retriever": Retriever()
    }

    # Define node functions
    def search_node(state: MarketResearchState):
        try:
            raw_results = agents["search"].run(state["query"])
            # Validate results
            validated_results = []
            for result in raw_results:
                if not isinstance(result, dict):
                    continue
                if "title" not in result:
                    result["title"] = "Untitled"
                validated_results.append(result)
            
            return {"search_results": validated_results}
        except Exception as e:
            logger.error(f"Search node failed: {str(e)}")
            return {"search_results": [], "error": str(e)}
    
    def retrieve_node(state: MarketResearchState):
        return {"search_results": agents["retriever"].retrieve_relevant_info(state["query"], state)}
    
    def summarize_node(state: MarketResearchState):
        return {"summaries": [
            agents["summarizer"].summarize(doc["content"]) 
            for doc in state["search_results"]
        ]}
    
    def analyze_node(state: MarketResearchState):
        try:
            papers = state.get("search_results", [])
            if not papers:
                return {"analysis": {"summary": "No papers to analyze"}}
                
            return {
                "analysis": agents["analyst"].analyze(
                    papers, 
                    state.get("query", "")
                )
            }
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {"analysis": {"summary": f"Analysis error: {str(e)}"}}
        
    def visualize_node(state: MarketResearchState):
        # Safely prepare visualization data with error handling
        visualization_data = []
        
        for r in state.get("search_results", []):
            try:
                # Ensure we have a dictionary and extract data safely
                if not isinstance(r, dict):
                    continue
                    
                vis_item = {
                    "title": str(r.get("title", "Untitled Document")),
                    "score": float(r.get("relevance_score", 0)),
                    "source": str(r.get("source", "unknown")),
                    "url": str(r.get("url", "")),
                    "content_preview": (str(r.get("content", ""))[:150] + "...") if r.get("content") else ""
                }
                
                # Add optional fields if they exist
                if "authors" in r:
                    vis_item["authors"] = [str(a) for a in r["authors"] if a]
                if "published_date" in r:
                    vis_item["date"] = str(r["published_date"])
                    
                visualization_data.append(vis_item)
                
            except Exception as e:
                logging.warning(f"Failed to process result for visualization: {str(e)}")
                continue
        
        # Generate visualizations with the cleaned data
        return {
            "visualizations": agents["visualizer"].generate_visualizations(visualization_data),
            "metadata": {
                "total_results": len(visualization_data),
                "successful_results": len(visualization_data),
                "failed_results": len(state.get("search_results", [])) - len(visualization_data)
            }
        }
    
    def coordinate_node(state: MarketResearchState):
        """Enhanced coordinator node with proper validation and error handling"""
        try:
            logger.debug("Coordinator received state keys: %s", state.keys())
            
            # Validate minimum required data
            required_keys = ["query", "search_results", "analysis", "visualizations"]
            if not all(key in state for key in required_keys):
                missing = [k for k in required_keys if k not in state]
                raise ValueError(f"Missing required state keys: {missing}")
            
            # Log sample data for debugging
            if state.get("search_results"):
                sample_result = state["search_results"][0]
                logger.debug(
                    "Sample result passed to coordinator:\n"
                    f"Title: {sample_result.get('title')}\n"
                    f"Score: {sample_result.get('relevance_score')}\n"
                    f"Content length: {len(sample_result.get('content', ''))}"
                )
            
            # Execute coordination
            coordinator_output = agents["coordinator"].coordinate(state)
            logger.info("Coordinator produced output: %s", coordinator_output)
            
            # Validate output structure
            if not isinstance(coordinator_output, dict):
                raise TypeError("Coordinator output must be a dictionary")
                
            required_output_keys = ["next_steps", "refinements"]
            if not all(k in coordinator_output for k in required_output_keys):
                missing = [k for k in required_output_keys if k not in coordinator_output]
                raise ValueError(f"Coordinator missing output keys: {missing}")
            
            return {
                "final_report": coordinator_output,
                "coordinator_insights": coordinator_output  # Added for visibility
            }
            
        except Exception as e:
            logger.error("Coordinator node failed: %s", str(e), exc_info=True)
            return {
                "final_report": {
                    "error": "Coordination failed",
                    "details": str(e)
                },
                "coordinator_failed": True
            }

    # Build workflow
    workflow = StateGraph(MarketResearchState)
    
    # Add nodes
    workflow.add_node("search", search_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("visualize", visualize_node)
    workflow.add_node("coordinate", coordinate_node)
    
    # Define flow
    workflow.set_entry_point("search")
    workflow.add_edge("search", "retrieve")
    workflow.add_edge("retrieve", "summarize")
    workflow.add_edge("summarize", "analyze")
    workflow.add_edge("analyze", "visualize")
    workflow.add_edge("visualize", "coordinate")
    workflow.set_finish_point("coordinate")
    
    return workflow.compile()