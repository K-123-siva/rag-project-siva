# Alternative entry point for cloud deployment platforms
import os
import sys

# Add src to Python path
sys.path.append('src')

# Set page config before importing app
import streamlit as st

st.set_page_config(
    page_title="NeuroQuery - AI Document Assistant",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Import and run the main app
if __name__ == "__main__":
    exec(open("app.py").read())