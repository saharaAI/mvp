# --- src/ui/app.py ---
import streamlit as st
import os
import sys
import random
from core_logic.agents.llm_interactions import LLMAgent
from core_logic.agents.task_manager import TaskManager
from ui.pages.home import display_home
from ui.pages.pdf_analysis import display_pdf_analysis
from ui.pages.llm_agents import display_llm_agents
from .data_manager import DataManager 

# --- API Key Handling ---
KEYS = ["AIzaSyBkTJsctYOkljL0tx-6Y8NwYCaSz-r0XmU", "AIzaSyDbzt8ZGVd3P15MMuIUh8wz1lzT5jRLWlc"] 
st.set_page_config(layout='wide', page_title='Sahara Analytics', page_icon='📄')
st.sidebar.header("API Keys")
user_api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password")

if user_api_key:
    gemini_api_key = user_api_key 
else:
    gemini_api_key = random.choice(KEYS)

os.environ["GEMINI_API_KEY"] = gemini_api_key

# --- Initialize Agents --- 
orchestrator = LLMAgent("orchestrator") 
expert = LLMAgent("expert")
executor = LLMAgent("executor")
task_manager = TaskManager(orchestrator, expert, executor)

# --- Page Navigation ---
PAGE_NAMES_TO_FUNCS = {
    "Accueil": display_home,
    "Analyse PDF": display_pdf_analysis,
    "LLM Agents": display_llm_agents,
}

def main():
    """Main function for the Streamlit app."""
    selected_page = st.sidebar.radio("Aller à", list(PAGE_NAMES_TO_FUNCS.keys()))
    PAGE_NAMES_TO_FUNCS[selected_page]()

    if selected_page == "Analyse PDF":
        objective = st.text_area("Enter your objective:")
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

        if st.button("Start Task") and uploaded_file is not None:
            with st.spinner("Processing your task..."):
                # --- PDF Extraction ---
                data_manager = DataManager(file_content=uploaded_file.read())
                pdf_text = data_manager.load_data(data_format="pdf")

                # --- Start Task Orchestration ---
                report = task_manager.start_task(objective, pdf_text)

                # --- Display Report ---
                st.subheader("Refined Output")
                st.text_area("", value=report, height=300)

if __name__ == "__main__":
    main()