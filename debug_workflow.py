import sys
from pathlib import Path
import logging
from typing import List, Dict, Any
import argparse

# Set up proper imports
sys.path.append(str(Path(__file__).parent.parent))

# Import all agents
from agents.search_agent import SearchAgent
from agents.analyst_agent import AnalystAgent
from agents.visualizer_agent import VisualizerAgent
from agents.coordinator_agent import CoordinatorAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def debug_agents_step_by_step(query: str):
    """Test each agent in isolation with full debugging"""
    
    # 1. Initialize all agents
    print("\n=== INITIALIZING AGENTS ===")
    search_agent = SearchAgent()
    analyst_agent = AnalystAgent()
    visualizer_agent = VisualizerAgent()
    coordinator = CoordinatorAgent()
    
    # 2. Test Search Agent
    print("\n=== TESTING SEARCH AGENT ===")
    try:
        search_results = search_agent.run(query)
        print(f"Got {len(search_results)} results")
        
        if search_results:
            first_result = search_results[0]
            print("\nFirst result structure:")
            print(f"Title: {first_result.get('title')}")
            print(f"Score: {first_result.get('relevance_score')}")
            print(f"Content length: {len(first_result.get('content', ''))}")
            print(f"Authors: {first_result.get('authors', [])[:3]}")
            
            assert first_result.get('title') != "Untitled", "Title is defaulting to Untitled"
            assert first_result.get('relevance_score', 0) != 0.0, "Score is defaulting to 0.0"
            
    except Exception as e:
        print(f"SEARCH AGENT FAILED: {str(e)}")
        raise

    # 3. Test Analyst Agent
    print("\n=== TESTING ANALYST AGENT ===")
    try:
        analysis = analyst_agent.analyze(search_results[:3])
        print("Analysis keys:", analysis.keys())
        print(f"Summary: {analysis.get('summary', '')[:200]}...")
    except Exception as e:
        print(f"ANALYST AGENT FAILED: {str(e)}")
        raise

    # 4. Test Visualizer Agent
    print("\n=== TESTING VISUALIZER AGENT ===")
    try:
        visualizations = visualizer_agent.generate_visualizations(search_results[:3])
        print("Visualization keys:", visualizations.keys())
        print("Generated charts:", list(visualizations.keys()))
    except Exception as e:
        print(f"VISUALIZER AGENT FAILED: {str(e)}")
        raise

    # 5. Test Coordinator Agent
    print("\n=== TESTING COORDINATOR AGENT ===")
    try:
        # Create mock workflow state
        workflow_state = {
            "query": query,
            "search_results": search_results[:3],
            "analysis": analysis,
            "visualizations": visualizations
        }
        
        print("\nWorkflow state being sent to coordinator:")
        print(f"- Query: {workflow_state['query']}")
        print(f"- Results count: {len(workflow_state['search_results'])}")
        print(f"- Analysis exists: {'summary' in workflow_state['analysis']}")
        print(f"- Visualizations: {len(workflow_state['visualizations'])}")
        
        coordination_result = coordinator.coordinate(workflow_state)
        
        print("\nCoordinator output:")
        print("Next Steps:")
        for i, step in enumerate(coordination_result.get('next_steps', []), 1):
            print(f" {i}. {step}")
        print("\nRefinements:")
        for k, v in coordination_result.get('refinements', {}).items():
            print(f" - {k}: {v}")
            
        # Verify coordinator output structure
        assert isinstance(coordination_result.get('next_steps', []), list)
        assert isinstance(coordination_result.get('refinements', {}), dict)
        
    except Exception as e:
        print(f"COORDINATOR AGENT FAILED: {str(e)}")
        raise

    # 6. Test Full Workflow
    print("\n=== TESTING FULL WORKFLOW ===")
    try:
        from workflows.market_research_graph import create_market_research_workflow
        workflow = create_market_research_workflow()
        full_results = workflow.invoke({"query": query})
        
        print("\nFinal output structure:")
        print(f"Papers: {len(full_results.get('search_results', []))}")
        print(f"Analysis exists: {'analysis' in full_results}")
        print(f"Visualizations: {len(full_results.get('visualizations', {}))}")
        print(f"Coordinator output exists: {'coordinator_output' in full_results}")
        
    except Exception as e:
        print(f"WORKFLOW FAILED: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="healthcare USA", help="Test query")
    args = parser.parse_args()
    
    print(f"\n{' STARTING DEBUG SESSION ':=^80}")
    print(f"Testing with query: '{args.query}'")
    
    debug_agents_step_by_step(args.query)
    
    print(f"\n{' DEBUG COMPLETE ':=^80}")