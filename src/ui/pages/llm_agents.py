# --- src/ui/pages/llm_agents.py ---
import streamlit as st
from core_logic.agents.task_manager import TaskManager  # Relative import
from core_logic.agents.llm_interactions import LLMAgent  # Relative import
from utils.helpers import _create_project_zip
from data_manager import DataManager
import random

# Initialize the TaskManager with LLMAgent
orchestrator = LLMAgent("orchestrator")
expert = LLMAgent("expert")
executor = LLMAgent("executor")
task_manager = TaskManager(orchestrator, expert, executor) 

def display_llm_agents():
    """Renders the page for interacting with LLM agents."""
    st.title("🤖 AI Task Orchestrator - Sahara Analytics")
    st.markdown(
        """
        Welcome to the AI Task Orchestrator! Use this tool to break down complex financial objectives into manageable sub-tasks and generate detailed reports.
        """
    )

    objective = st.text_area("Enter your objective:", 
                            placeholder="Describe the financial analysis task you need to perform.")
    uploaded_file = st.file_uploader("Upload your balance sheet (PDF)", type=["pdf"])
    use_search = st.checkbox("Use search to find additional information")

    if st.button("Start Task") and uploaded_file is not None:
        with st.spinner("Processing your task..."):
            # Extract text from the uploaded PDF
            data_manager = DataManager(file_content=uploaded_file.read())
            extracted_text = data_manager.load_data(data_format="pdf")

            sub_task_results = task_manager.start_task(objective, extracted_text, use_search)
            refined_output = task_manager.generate_report(objective, sub_task_results)

            # --- Dummy values for folder structure and code blocks (Modify or remove if not needed) ---
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