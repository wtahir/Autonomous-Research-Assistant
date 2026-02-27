# Autonomous Research Assistant

An AI-powered system that automates market research by coordinating multiple specialized agents

## Features

- **Search Agent**: Finds relevant information from various sources
- **Summarizer Agent**: Extracts key insights from documents
- **Analyst Agent**: Performs professional data analysis
- **Visualizer Agent**: Creates informative visualizations
- **Coordinator Agent**: Orchestrates the workflow
- **RAG System**: For information retrieval and knowledge management
- **Dashboard**: User interface for interacting with the system

## Architecture

The system uses LangGraph to create a stateful workflow where each agent performs a specific task and passes results to the next agent. The architecture follows a modular design for easy extension.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set your OpenAI API key in environment variables
4. Run the API: `python main.py`
5. Run the dashboard: `streamlit run app/dashboard.py`

## Usage

1. Access the dashboard at `http://localhost:8501`
2. Enter your research query
3. View the automated research results including:
   - Summarized findings
   - Data analysis
   - Visualizations
   - Recommendations

## Customization

You can easily add new agents by:
1. Creating a new file in `agents/`
2. Implementing the agent logic
3. Adding it to the workflow in `workflows/market_research_graph.py`