from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
load_dotenv()

class SummarizerAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version="2024-02-01",
            model="gpt-4-turbo",
            temperature=0.3
        )
        self.chain = self._create_chain()
    
    def _create_chain(self):
        prompt = ChatPromptTemplate.from_template("""
        You are an expert summarizer with strong technical and business acumen.
        
        Analyze the following content and create a comprehensive summary that:
        1. Captures key points
        2. Identifies trends and patterns
        3. Highlights potential business implications
        4. Notes any data limitations
        
        Content:
        {content}
        
        Summary:
        """)
        
        return prompt | self.llm | StrOutputParser()
    
    def summarize(self, content: str) -> str:
        """Generate a professional summary of the content"""
        return self.chain.invoke({"content": content})

# if __name__ == "__main__":
#     agent = SummarizerAgent()
#     text = """
#     The company's revenue increased by 20% in Q1, driven primarily by growth in the Asia-Pacific region.
#     However, supply chain issues may affect Q2 performance.
#     """
#     summary = agent.summarize(text)
#     print("Summary:\n", summary)
