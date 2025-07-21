from workflows.market_research_graph import create_market_research_workflow
from langgraph.graph import Graph
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Autonomous Research Assistant")

# Initialize the workflow
workflow = create_market_research_workflow()

@app.post("/research")
async def conduct_research(query: str):
    """Endpoint to trigger research workflow"""
    results = workflow.invoke({"query": query})
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)