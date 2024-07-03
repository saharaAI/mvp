# --- src/ui/pages/home.py ---
import streamlit as st

def display_home():
    """Renders the content for the home page."""
    st.markdown('<p class="big-font centered">Sahara Analytics</p>', unsafe_allow_html=True)
    st.write("Welcome to Sahara Analytics!")
    st.write("Explore the various functionalities available through the sidebar.")
