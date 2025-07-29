# import sys
# from pathlib import Path
# from fastapi import FastAPI
# from fastapi import Body
# import uvicorn

# # Add project root to Python path
# sys.path.append(str(Path(__file__).parent))

# from workflows.market_research_graph import create_market_research_workflow

# app = FastAPI(title="Autonomous Research Assistant")

# # Initialize the workflow
# workflow = create_market_research_workflow()

# import logging
# from fastapi import Body, HTTPException

# logger = logging.getLogger(__name__)

# @app.post("/research")

# async def conduct_research(query: str = Body(..., embed=True)):
#     logger.info(f"Received query: {query}")
#     try:
#         results = workflow.invoke({"query": query})
        
#         # Validate and format the response
#         search_results = []
#         for item in results.get("search_results", []):
#             search_results.append({
#                 "title": item.get("title", "Untitled"),
#                 "content": item.get("content", ""),
#                 "url": item.get("url", ""),
#                 "score": item.get("relevance_score", 0)
#             })
            
#         return {
#             "search_results": search_results,
#             "analysis": results.get("analysis", {}),
#             "visualizations": results.get("visualizations", {}),
#             "query": query
#         }
#     except Exception as e:
#         logger.error(f"Error processing query '{query}': {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Research failed",
#                 "message": str(e),
#                 "query": query
#             }
#         )
    
# @app.get("/")
# async def root():
#     return {
#         "message": "Autonomous Research Assistant API",
#         "endpoints": {
#             "POST /research": "Run research workflow"
#         }
#     }
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI
from pydantic import BaseModel
from agents.coordinator_agent import CoordinatorAgent
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
coordinator = CoordinatorAgent()

class ResearchQuery(BaseModel):
    query: str

@app.post("/research")
async def research(query: ResearchQuery):
    logger.info(f"Received query: {query.query}")
    result = coordinator.coordinate(query.query)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")