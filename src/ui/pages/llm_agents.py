# --- src/ui/pages/llm_agents.py ---
import streamlit as st
from core_logic.agents.task_manager import TaskManager
from core_logic.agents.llm_interactions import LLMAgent
from utils.helpers import _create_project_zip
import random

# Initialize the TaskManager with LLMAgent
ORCHESTRATOR_MODEL = "gemini/gemini-1.5-flash-latest"
SUB_AGENT_MODEL = "gemini/gemini-1.5-flash-latest"
REFINER_MODEL = "gemini/gemini-1.5-flash-latest"
KEYS = ["AIzaSyBkTJsctYOkljL0tx-6Y8NwYCaSz-r0XmU", "AIzaSyDbzt8ZGVd3P15MMuIUh8wz1lzT5jRLWlc"]
GEMINI_API_KEY = random.choice(KEYS)

llm_agent = LLMAgent(ORCHESTRATOR_MODEL, SUB_AGENT_MODEL, REFINER_MODEL,GEMINI_API_KEY)
task_manager = TaskManager(llm_agent)

def display_llm_agents():
    """Renders the page for interacting with LLM agents."""
    st.title("🤖 AI Task Orchestrator - Sahara Analytics")
    st.markdown(
        """
        Welcome to the AI Task Orchestrator! Use this tool to break down complex financial objectives into manageable sub-tasks and generate detailed reports.
        """
    )
    
    objective = st.text_area("Enter your objective:", placeholder="Describe the financial analysis task you need to perform.")
    file_content = st.text_area("Enter file content (optional):", placeholder="Paste or upload balance sheet data here.")
    use_search = st.checkbox("Use search to find additional information")

    if st.button("Start Task"):
        with st.spinner("Processing your task..."):
            sub_task_results = task_manager.start_task(objective, file_content, use_search)
            refined_output = task_manager.generate_report(objective, sub_task_results)

            # Dummy values for folder structure and code blocks
            project_name = "default_project"
            folder_structure = ["code"]
            code_blocks = [("main.py", refined_output)]
            zip_buffer = _create_project_zip(project_name, folder_structure, code_blocks)

            st.success("Task completed successfully!")

            st.download_button(
                label="Download Project Files",
                data=zip_buffer.getvalue(),
                file_name=f"{project_name}.zip",
                mime="application/zip"
            )

            st.subheader("Refined Output")
            st.text_area("", value=refined_output, height=300, max_chars=5000)
