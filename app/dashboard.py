import streamlit as st
from workflows.market_research_graph import create_market_research_workflow
import base64
from io import BytesIO
import pandas as pd

def show_dashboard():
    st.set_page_config(page_title="Autonomous Research Assistant", layout="wide")
    
    st.title("Autonomous Research Assistant")
    st.markdown("""
    This tool automates the research process using AI agents to:
    - Search for relevant information
    - Summarize key findings
    - Analyze data
    - Generate visualizations
    """)
    
    query = st.text_input("Enter your research query:", placeholder="e.g., 'Latest trends in renewable energy 2024'")
    
    if st.button("Start Research") and query:
        with st.spinner("Conducting research... This may take a few minutes"):
            workflow = create_market_research_workflow()
            results = workflow.invoke({"query": query})
            
            display_results(results)

def display_results(results: dict):
    st.header("Research Findings")
    
    # Show summaries
    with st.expander("Key Summaries"):
        for i, summary in enumerate(results.get("summaries", [])):
            st.subheader(f"Source {i+1}")
            st.write(summary)
    
    # Show analysis
    st.header("Data Analysis")
    st.write(results.get("analysis", {}).get("insights", ""))
    
    # Show visualizations
    st.header("Visualizations")
    viz_data = results.get("visualizations", {})
    
    cols = st.columns(2)
    for i, (viz_name, viz_base64) in enumerate(viz_data.items()):
        with cols[i % 2]:
            st.subheader(viz_name.replace("_", " ").title())
            st.image(base64.b64decode(viz_base64))
    
    # Show recommendations
    st.header("Recommendations")
    st.write(results.get("analysis", {}).get("recommendations", ""))

if __name__ == "__main__":
    show_dashboard()