# --- src/ui/app.py --- 
import streamlit as st
import os
import sys
from ui.pages.home import display_home
from ui.pages.pdf_analysis import display_pdf_analysis
from ui.pages.llm_agents import display_llm_agents
from core_logic.agents.agents import LLMAgent
from core_logic.tasks.tasks import TaskManager

# Get the absolute path to the 'src' directory 
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"src") )

# Add the 'src' directory to the Python path
sys.path.insert(0, src_dir)

# Define the models (consider moving these to a config file)
ORCHESTRATOR_MODEL = "gemini/gemini-1.5-flash-latest"
SUB_AGENT_MODEL = "gemini/gemini-1.5-flash-latest"
REFINER_MODEL = "gemini/gemini-1.5-flash-latest"

# Initialize LLM agent and task manager
llm_agent = LLMAgent(ORCHESTRATOR_MODEL, SUB_AGENT_MODEL, REFINER_MODEL)
task_manager = TaskManager(llm_agent)

# Dictionary mapping page names to their respective functions
PAGE_NAMES_TO_FUNCS = {
    "Accueil": display_home,
    "Analyse PDF": display_pdf_analysis,
    "Website Crawl": display_website_crawl,  # Assuming you have this implemented
    "LLM Agents": display_llm_agents,
}

def main():
    st.set_page_config(layout='wide', page_title='Sahara Analytics', page_icon='📄')

    # Optional: Hide Streamlit style (Ensure hide_st_style is defined somewhere if used)
    # st.markdown(hide_st_style, unsafe_allow_html=True)

    # API Key Handling (Consider moving to a separate config/secrets management)

    selected_page = st.sidebar.radio("Aller à", list(PAGE_NAMES_TO_FUNCS.keys()))
    PAGE_NAMES_TO_FUNCS[selected_page]()

if __name__ == "__main__":
    main()
