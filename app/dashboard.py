import base64
from io import BytesIO
from typing import Any, Dict, List
import streamlit as st
import sys
import logging
from pathlib import Path
from functools import lru_cache
import time
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import your existing agents
from agents.search_agent import SearchAgent
from agents.analyst_agent import AnalystAgent
from agents.visualizer_agent import VisualizerAgent
import requests

logger = logging.getLogger(__name__)


# -------------------------
# App Config
# -------------------------
st.set_page_config(page_title="Autonomous Research Assistant", layout="wide")
st.title("🔍 Autonomous Research Assistant")
st.markdown(
    """
This tool automates research using AI agents to:
- 🔎 Search academic papers  
- 📝 Summarize key findings  
- 📊 Analyze content  
- 📈 Generate insights  

---
"""
)

# -------------------------
# Sample Data (fallback)
# -------------------------
SAMPLE_DATA = [
    {"topic": "AI", "papers": 42, "trend_score": 0.85},
    {"topic": "Blockchain", "papers": 28, "trend_score": 0.62},
    {"topic": "Quantum", "papers": 35, "trend_score": 0.78}
]

# -------------------------
# Main Workflow
# -------------------------
@lru_cache(maxsize=32)
def run_research(query: str) -> Dict[str, Any]:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/research",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=90
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return {"error": f"Request failed after {max_retries} attempts: {str(e)}"}
            time.sleep(2 ** attempt)  # Exponential backoff

def render_visualizations(viz_data: Dict[str, str]) -> None:
    """Render available visualizations"""
    if not viz_data:
        st.warning("No visualization data available - papers may lack numerical scores")
        return
    
    cols = st.columns(2)
    for i, (viz_name, img_data) in enumerate(viz_data.items()):
        with cols[i % 2]:
            try:
                st.markdown(f"**{viz_name.replace('_', ' ').title()}**")
                st.image(BytesIO(base64.b64decode(img_data)))
            except Exception as e:
                st.error(f"Couldn't display {viz_name}: {str(e)}")

# ... (rest of the dashboard code remains the same)

# -------------------------
# UI Components
# -------------------------
query = st.text_input("Enter research topic:", placeholder="e.g. AI in healthcare 2025")

if st.button("Run Research") and query:
    with st.spinner("Researching..."):
        results = run_research(query)
        
        if "error" in results:
            st.error(f"Research failed: {results['error']}")
        else:
            # Display Results (updated to match API response format)
            st.subheader("📚 Research Papers")
            for paper in results.get("search_results", [])[:5]:
                with st.expander(f"{paper['title']} (Score: {paper.get('relevance_score', 0):.2f})"):
                    st.write(f"**Authors:** {', '.join(paper.get('authors', []))}")
                    st.write(paper.get('content', ''))
                    if 'url' in paper:
                        st.markdown(f"[Read Paper]({paper['url']})")
            
            st.subheader("📊 Analysis")
            st.write(results.get("analysis", {}).get("summary", "No analysis available"))
            
            st.subheader("📈 Trends")
            render_visualizations(results.get("visualizations", {}))



# import os
# import base64
# from io import BytesIO
# from typing import Any, Dict, List

# import streamlit as st

# # Ensure project root on path so intra-package imports work when launched from anywhere
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from workflows.market_research_graph import create_market_research_workflow
# from agents.analyst_agent import AnalystAgent
# from agents.visualizer_agent import VisualizerAgent


# # -------------------------
# # App Config
# # -------------------------
# st.set_page_config(page_title="Autonomous Research Assistant", layout="wide")
# st.title("🔍 Autonomous Research Assistant")
# st.markdown(
#     """
# This tool automates a research workflow using multiple AI agents to:

# - 🔎 Search for relevant information  
# - 📝 Summarize key findings  
# - 📊 Analyze structured data  
# - 📈 Generate visualizations  
# - ✅ Recommend next steps  

# ---
# """
# )


# # -------------------------
# # Input Controls
# # -------------------------
# query = st.text_input(
#     "Enter your research query:",
#     placeholder="e.g. energy trend 2024",
# )

# use_sample_data = st.checkbox(
#     "Use sample tabular data for analysis & visualization (helpful if search returns no data)",
#     value=True,
#     help="When checked, the Analyst & Visualizer agents will run on a built-in demo dataset if no structured data comes back from the research workflow.",
# )


# # -------------------------
# # Sample Data (fallback)
# # -------------------------
# SAMPLE_DATA: List[Dict[str, Any]] = [
#     {"month": "Jan-2025", "region": "North", "consumption_gwh": 1200, "renewable_share_pct": 32.5},
#     {"month": "Jan-2025", "region": "South", "consumption_gwh": 980, "renewable_share_pct": 28.1},
#     {"month": "Jan-2025", "region": "East",  "consumption_gwh": 1110, "renewable_share_pct": 35.0},
#     {"month": "Feb-2025", "region": "North", "consumption_gwh": 1185, "renewable_share_pct": 34.2},
#     {"month": "Feb-2025", "region": "South", "consumption_gwh": 1010, "renewable_share_pct": 29.3},
#     {"month": "Feb-2025", "region": "East",  "consumption_gwh": 1152, "renewable_share_pct": 36.8},
#     {"month": "Mar-2025", "region": "North", "consumption_gwh": 1230, "renewable_share_pct": 33.9},
#     {"month": "Mar-2025", "region": "South", "consumption_gwh": 1035, "renewable_share_pct": 30.2},
#     {"month": "Mar-2025", "region": "East",  "consumption_gwh": 1175, "renewable_share_pct": 37.4},
# ]


# # -------------------------
# # Run Workflow
# # -------------------------
# if st.button("Run Research") and query:
#     workflow = create_market_research_workflow()

#     with st.spinner("Running research workflow... (this may take a minute)"):
#         try:
#             results = workflow.invoke({"query": query})
#         except Exception as e:
#             st.error(f"An error occurred while running the workflow: {e}")
#             st.stop()

#     st.success("Research complete!")
#     st.caption("Below is the raw result object returned by the workflow (debug view).")
#     st.json(results)

#     # ------------- Post-processing / Fallback -------------
#     # The workflow may return empty lists for summaries or structured data; if so, optionally run the
#     # Analyst & Visualizer on sample data so the UI has something meaningful to show.
#     analysis_dict = results.get("analysis")
#     viz_dict = results.get("visualizations")

#     need_analysis_fallback = (not analysis_dict) or ("summary" not in analysis_dict)
#     need_viz_fallback = (not viz_dict) or (len(viz_dict) == 0)

#     if use_sample_data and (need_analysis_fallback or need_viz_fallback):
#         st.warning(
#             "The workflow did not return structured data for analysis/visualization. "
#             "Running fallback analysis on sample dataset."
#         )

#         analyst = AnalystAgent()
#         analysis_dict = analyst.analyze(SAMPLE_DATA)

#         visualizer = VisualizerAgent()
#         viz_dict = visualizer.generate_visualizations(SAMPLE_DATA)

#     # Normalize back into results so downstream sections work uniformly.
#     results["analysis"] = analysis_dict or {}
#     results["visualizations"] = viz_dict or {}

#     # -------------------------
#     # Render Sections
#     # -------------------------
#     # 1. Research Findings (search results)
#     st.subheader("📚 Research Findings")
#     search_results = results.get("search_results", [])
#     if search_results:
#         render_search_results(search_results)
#     else:
#         st.info("No search results available.")

#     # 2. Key Summaries
#     st.subheader("📝 Key Summaries")
#     summaries = results.get("summaries", [])
#     if summaries:
#         for i, s in enumerate(summaries):
#             st.markdown(f"**Summary {i+1}:**")
#             st.write(s)
#             st.markdown("---")
#     else:
#         st.info("No summaries generated.")

#     # 3. Data Analysis
#     st.subheader("📊 Data Analysis")
#     analysis_text = results.get("analysis", {}).get("summary")
#     if analysis_text:
#         st.write(analysis_text)
#     else:
#         st.info("No analysis available.")

#     # 4. Visualizations
#     st.subheader("📈 Visualizations")
#     viz_data = results.get("visualizations", {})
#     render_visualizations(viz_data)

#     # 5. Recommendations & Query Refinement
#     st.subheader("✅ Recommendations & Next Steps")
#     final_report = results.get("final_report", {})
#     next_steps = final_report.get("next_steps", [])
#     if next_steps:
#         for step in next_steps:
#             st.markdown(f"- {step}")
#     else:
#         st.info("No recommendations found.")

#     refinement = final_report.get("refinements", {}).get("query_refinement")
#     if refinement:
#         st.subheader("🛠️ Query Refinement Suggestion")
#         st.write(refinement)

# else:
#     st.info("Enter a query and press **Run Research** to begin.")


# # =========================================================
# # Helper Rendering Functions
# # =========================================================
# def render_search_results(search_results: Any) -> None:
#     """
#     Render search results robustly whether they're:
#       - list of dicts from SearchAgent
#       - list of strings
#       - something else unexpected
#     """
#     if isinstance(search_results, list):
#         for i, item in enumerate(search_results):
#             st.markdown(f"**Result {i+1}:**")
#             if isinstance(item, dict):
#                 title = item.get("title") or "(untitled)"
#                 url = item.get("url") or ""
#                 snippet = (
#                     item.get("snippet")
#                     or item.get("summary")
#                     or item.get("content")
#                     or ""
#                 )
#                 st.markdown(f"**{title}**")
#                 if url:
#                     st.write(url)
#                 if snippet:
#                     st.write(snippet)
#             else:
#                 st.write(str(item))
#             st.markdown("---")
#     else:
#         st.write(search_results)

# def render_visualizations(viz_data: Dict[str, str]) -> None:
#     """
#     Accepts dict like {name: base64_png_string} and renders in columns.
#     """
#     if not viz_data:
#         st.info("No visualizations available.")
#         return

#     cols = st.columns(min(3, len(viz_data)))
#     for i, (viz_name, b64img) in enumerate(viz_data.items()):
#         with cols[i % len(cols)]:
#             st.markdown(f"**{viz_name.replace('_', ' ').title()}**")
#             if not b64img:
#                 st.write("No image.")
#                 continue
#             try:
#                 img_bytes = base64.b64decode(b64img)
#                 st.image(BytesIO(img_bytes))
#             except Exception as e:
#                 st.error(f"Failed to render {viz_name}: {e}")


# import streamlit as st
# # from agents.search_agent import SearchAgent  # Your existing search agent
# from typing import List, Dict
# import json
# import time

# import sys
# from pathlib import Path

# # Add this at the top of dashboard.py
# sys.path.insert(0, str(Path(__file__).parent.parent))

# # Now your imports will work
# from agents.search_agent import SearchAgent

# class ResearchDashboard:
#     def __init__(self):
#         self.search_agent = SearchAgent()
#         st.set_page_config(page_title="Academic Research Assistant", layout="wide")
        
#     def show(self):
#         st.title("📚 Academic Research Assistant")
        
#         # Search Input
#         query = st.text_input("Enter your research topic:", 
#                             placeholder="e.g., 'Quantum computing advances 2024'")
        
#         if st.button("Start Research") and query:
#             with st.spinner("🔍 Searching arXiv and analyzing results..."):
#                 start_time = time.time()
                
#                 # Step 1: Get data from SearchAgent
#                 try:
#                     results = self.search_agent.run(query)
                    
#                     # Step 2: Display raw results
#                     st.subheader(f"📄 Found {len(results)} papers")
#                     for paper in results[:5]:  # Show top 5
#                         with st.expander(f"**{paper['title']}** (Score: {paper['relevance_score']:.1f}/1.0)"):
#                             st.write(f"**Authors**: {', '.join(paper['authors'])}")
#                             st.write(f"**Summary**: {paper['content']}")
#                             st.write(f"[Read paper]({paper['url']})")
                    
#                     # Step 3: Show analysis
#                     st.subheader("🧠 AI Analysis")
#                     st.markdown(results[0]['summary'])  # Using the summary from SearchAgent
                    
#                     # Step 4: Download option
#                     st.download_button(
#                         label="📥 Download Results (JSON)",
#                         data=json.dumps(results, indent=2),
#                         file_name=f"research_{query[:20]}.json"
#                     )
                    
#                     st.success(f"Research completed in {time.time()-start_time:.1f} seconds")
                
#                 except Exception as e:
#                     st.error(f"Research failed: {str(e)}")

# if __name__ == "__main__":
#     dashboard = ResearchDashboard()
#     dashboard.show()