# --- src/ui/pages/home.py ---
import streamlit as st

def display_home():
    """Renders the home page."""
    st.title("Welcome to Sahara Analytics")
    st.markdown(
        """
        ### Introduction
        Sahara Analytics offers powerful tools to perform detailed financial analysis and reporting. 
        Leverage our AI-driven task orchestrator to break down complex objectives into actionable insights.
        
        ### Features
        - **Analyze PDFs**: Upload and analyze balance sheets and other financial documents.
        - **LLM Agents**: Interact with our AI agents to orchestrate financial tasks and generate detailed reports.
        
        ### Getting Started
        Use the sidebar to navigate between different functionalities of the app.
        """
    )
