from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

class CoordinatorAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version="2024-02-01",
            model="gpt-4o",
            temperature=0.1
        )
    
    def coordinate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the workflow and make high-level decisions"""
        messages = [
            SystemMessage(content="""
            You are an expert project coordinator for data science research projects.
            Your role is to ensure the research workflow produces high-quality,
            actionable insights by making strategic decisions about:
            1. Which agents to engage and when
            2. How to refine the research direction
            3. Quality control of outputs
            4. Final synthesis of findings
            """),
            HumanMessage(content=f"Research context: {context}")
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "next_steps": self._parse_response(response.content),
            "refinements": self._generate_refinements(context)
        }
    
    def _parse_response(self, content: str) -> list:
        """Parse the LLM response into actionable steps"""
        # You can improve this by parsing bullets, JSON, or keywords
        # For now, just split by newlines and strip:
        steps = [line.strip("-* \n") for line in content.split("\n") if line.strip()]
        return steps
    
    def _generate_refinements(self, context: Dict) -> Dict:
        """Generate refinements to the research approach"""
        # Simple example, customize as needed
        return {"query_refinement": "Use more specific keywords based on current results"}

# if __name__ == "__main__":
#     agent = CoordinatorAgent()
#     sample_context = {
#         "topic": "AI in healthcare",
#         "current_step": "data_collection",
#         "previous_findings": ["high accuracy in image classification"]
#     }
#     result = agent.coordinate(sample_context)
#     print(result)
