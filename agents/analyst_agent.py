# from typing import List, Dict
# from openai import AzureOpenAI
# import logging
# import json
# import os
# from dotenv import load_dotenv
# load_dotenv()

# logger = logging.getLogger(__name__)

# class AnalystAgent:
#     def __init__(self):
#         self.client = AzureOpenAI(
#             azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#             api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#             api_version="2024-02-01"
#         )
#         self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
#         logger.info("analyst agent initialized successfully")
    
#     def analyze(self, data: List[Dict]) -> Dict:
#         """Perform professional analysis of structured data"""
#         prompt = f"""
#         You are a senior data scientist with 10+ years of experience.
#         Analyze the following data and provide:

#         1. Key insights (in bullet points)
#         2. Statistical significance (if any)
#         3. Potential biases or limitations
#         4. Recommended next steps

#         Data:
#         {data}

#         Return a brief, bullet-pointed summary.
#         """

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.deployment,
#                 messages=[
#                     {"role": "system", "content": "You are a helpful data analyst."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=500
#             )
#             return {
#                 "summary": response.choices[0].message.content
#             }
#         except Exception as e:
#             logger.error("Error during completion: %s", e)
#             return {"error": str(e)}

        
from typing import List, Dict
from openai import AzureOpenAI
import logging
import json
import time
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class AnalystAgent:
    def __init__(self):
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01"
            )
            self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            if not self.deployment:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT not set")
            logger.info("AnalystAgent initialized successfully")
        except Exception as e:
            logger.error(f"AnalystAgent initialization failed: {str(e)}")
            raise

    def analyze(self, papers: List[Dict], query: str = "") -> Dict:
        if not papers:
            logger.warning(f"No papers found for query: {query}")
            return {"summary": f"No papers found for query: {query}"}

        analysis_input = []
        for paper in papers[:3]:
            try:
                if not paper.get("content"):
                    logger.warning(f"Skipping paper with missing content: {paper.get('title', 'Untitled')}")
                    continue
                analysis_input.append({
                    "title": paper.get("title", "Untitled Paper"),
                    "key_content": paper.get("content", "")[:1000]
                })
            except Exception as e:
                logger.error(f"Skipping paper due to error: {str(e)}")
                continue

        if not analysis_input:
            logger.warning("No valid papers to analyze after filtering")
            return {"summary": "No valid papers to analyze"}

        try:
            logger.info(f"Analyzing {len(analysis_input)} papers for query: {query}")
            start = time.time()
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior data scientist. Analyze these research papers and provide key insights in bullet points, including statistical significance, biases, and next steps."
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nPapers:\n{json.dumps(analysis_input, indent=2)}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            logger.info(f"GPT-4o call took {time.time() - start} seconds")
            return {"summary": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {"summary": f"Analysis error: {str(e)}"}