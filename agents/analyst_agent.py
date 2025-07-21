from typing import List, Dict
from openai import AzureOpenAI
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class AnalystAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01"
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        logger.info("analyst agent initialized successfully")
    
    def analyze(self, data: List[Dict]) -> Dict:
        """Perform professional analysis of structured data"""
        prompt = f"""
        You are a senior data scientist with 10+ years of experience.
        Analyze the following data and provide:

        1. Key insights (in bullet points)
        2. Statistical significance (if any)
        3. Potential biases or limitations
        4. Recommended next steps

        Data:
        {data}

        Return a brief, bullet-pointed summary.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            return {
                "summary": response.choices[0].message.content
            }
        except Exception as e:
            logger.error("Error during completion: %s", e)
            return {"error": str(e)}

        
    # def _create_chain(self):
    #     prompt = ChatPromptTemplate.from_template("""
    #     You are a senior data scientist with 10+ years of experience.
    #     Analyze the following data and provide:

    #     1. Key insights (in bullet points)
    #     2. Statistical significance (if any)
    #     3. Potential biases or limitations
    #     4. Recommended next steps

    #     Data:
    #     {data}
    #     """)
    #     return prompt | self.client | StrOutputParser()

    # def analyze(self, data: List[Dict]) -> Dict:
    #     """Perform professional analysis of structured data"""
    #     raw_output = self.chain.invoke({"data": str(data)})

    #     # Optional: You can further split or parse the output here if needed
    #     return {
    #         "summary": raw_output
    #     }
