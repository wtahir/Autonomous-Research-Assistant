from langgraph.graph import Graph
from typing import Dict, Any
from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.analyst_agent import AnalystAgent
from agents.visualizer_agent import VisualizerAgent
from agents.coordinator_agent import CoordinatorAgent
from rag.retriever import Retriever

def create_market_research_workflow():
    # Initialize all agents
    search_agent = SearchAgent()
    summarizer = SummarizerAgent()
    analyst = AnalystAgent()
    visualizer = VisualizerAgent()
    coordinator = CoordinatorAgent()
    retriever = Retriever()
    
    # Define the graph
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("search", lambda state: search_agent.run(state["query"]))
    workflow.add_node("retrieve", lambda state: retriever.retrieve_relevant_info(state["query"], state))
    workflow.add_node("summarize", lambda state: {
        "summaries": [summarizer.summarize(doc["content"]) for doc in state["search_results"]]
    })
    workflow.add_node("analyze", lambda state: analyst.analyze(state["summaries"]))
    workflow.add_node("visualize", lambda state: visualizer.generate_visualizations(state["analysis"]))
    workflow.add_node("coordinate", lambda state: coordinator.coordinate(state))
    
    # Define edges
    workflow.add_edge("search", "retrieve")
    workflow.add_edge("retrieve", "summarize")
    workflow.add_edge("summarize", "analyze")
    workflow.add_edge("analyze", "visualize")
    workflow.add_edge("visualize", "coordinate")
    
    # Set entry and end points
    workflow.set_entry_point("search")
    workflow.set_finish_point("coordinate")
    
    # Compile the workflow
    return workflow.compile()