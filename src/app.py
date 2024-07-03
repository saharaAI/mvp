# --- src/app.py ---
import streamlit as st
import os
import sys
import random
from core_logic.agents.llm_interactions import LLMAgent
from core_logic.agents.task_manager import TaskManager
from ui.pages.home import display_home
from ui.pages.pdf_analysis import display_pdf_analysis
from ui.pages.llm_agents import display_llm_agents
from utils.helpers import _create_project_zip
from datetime import datetime
import re

# Get the absolute path to the 'src' directory 
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))

# Add the 'src' directory to the Python path
sys.path.insert(0, src_dir)

# Define API keys
KEYS = ["AIzaSyBkTJsctYOkljL0tx-6Y8NwYCaSz-r0XmU", "AIzaSyDbzt8ZGVd3P15MMuIUh8wz1lzT5jRLWlc"]
GEMINI_API_KEY = random.choice(KEYS)

# Sidebar for API key inputs
st.set_page_config(layout='wide', page_title='Sahara Analytics', page_icon='📄')
st.sidebar.header("API Keys")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
anthropic_api_key = st.sidebar.text_input("Anthropic API Key", type="password")

# Define the models
ORCHESTRATOR_MODEL = "gemini/gemini-1.5-flash-latest"
SUB_AGENT_MODEL = "gemini/gemini-1.5-flash-latest"
REFINER_MODEL = "gemini/gemini-1.5-flash-latest"

# Initialize LLM agent and task manager with the API key
llm_agent = LLMAgent(ORCHESTRATOR_MODEL, SUB_AGENT_MODEL, REFINER_MODEL, GEMINI_API_KEY)
task_manager = TaskManager(llm_agent)

# Dictionary mapping page names to their respective functions
PAGE_NAMES_TO_FUNCS = {
    "Accueil": display_home,
    "Analyse PDF": display_pdf_analysis,
    "LLM Agents": display_llm_agents,
}

def main():
    selected_page = st.sidebar.radio("Aller à", list(PAGE_NAMES_TO_FUNCS.keys()))
    PAGE_NAMES_TO_FUNCS[selected_page]()

    if selected_page == "Analyse PDF":
        objective = st.text_area("Enter your objective:")
        file_content = st.text_area("Enter file content (optional):")
        use_search = st.checkbox("Use search")

        if st.button("Start Task"):
            with st.spinner("Processing your task..."):
                sub_task_results = task_manager.start_task(objective, file_content, use_search)
                refined_output = task_manager.generate_report(objective, sub_task_results)
                project_name = re.sub(r'\W+', '_', objective)
                timestamp = datetime.now().strftime("%H-%M-%S")
                # Define folder_structure and code_blocks as needed
                folder_structure = ['src/']  # Example, adjust as needed
                code_blocks = []  # Example, add actual file contents here
                zip_buffer = _create_project_zip(project_name, folder_structure, code_blocks)
                st.success("Task completed successfully!")
                st.download_button(
                    label="Download Project Files",
                    data=zip_buffer.getvalue(),
                    file_name=f"{project_name}.zip",
                    mime="application/zip"
                )
                st.subheader("Refined Output")
                st.text_area("", value=refined_output, height=300)

if __name__ == "__main__":
    main()
