# --- src/app.py ---
import streamlit as st
import os
import sys
import random
from ui.pages.home import display_home
from ui.pages.pdf_analysis import display_pdf_analysis
from ui.pages.llm_agents import display_llm_agents
from core_logic.agents.llm_interactions import LLMAgent
from core_logic.agents.task_manager import TaskManager
from utils.helpers import _create_project_zip

# Set the page configuration as the first Streamlit command
st.set_page_config(layout='wide', page_title='Sahara Analytics', page_icon='📄')

# Define API keys and models
KEYS = ["AIzaSyBkTJsctYOkljL0tx-6Y8NwYCaSz-r0XmU", "AIzaSyDbzt8ZGVd3P15MMuIUh8wz1lzT5jRLWlc"]
GEMINI_API_KEY = random.choice(KEYS)

# Sidebar for API key inputs
st.sidebar.header("API Keys")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
anthropic_api_key = st.sidebar.text_input("Anthropic API Key", type="password")
gemini_api_key_input = st.sidebar.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
if anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
if gemini_api_key_input:
    os.environ["GEMINI_API_KEY"] = gemini_api_key_input

# Get the absolute path to the 'src' directory 
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))

# Add the 'src' directory to the Python path
sys.path.insert(0, src_dir)

# Define the models
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
    "LLM Agents": display_llm_agents,
}

def main():
    selected_page = st.sidebar.radio("Aller à", list(PAGE_NAMES_TO_FUNCS.keys()))
    PAGE_NAMES_TO_FUNCS[selected_page]()

if __name__ == "__main__":
    main()
