import tempfile
import os
from src.config import Config
import streamlit as st
import shutil
from src.logger import setup_logger
logger = setup_logger(__name__)

def reset_context():
    """Reset the session context - cloud-compatible version"""
    st.session_state.vectorstore = None
    st.session_state.rag_chain = None
    st.session_state.messages = []
    
    # Only try to clean up persistent directory in local mode
    if Config.DEPLOYMENT_MODE == "local" and os.path.exists(Config.PERSIST_DIR):
        try:
            shutil.rmtree(Config.PERSIST_DIR)
            logger.info("Cleaned up local persistent directory")
        except Exception as e:
            logger.warning("Could not clean up persistent directory: %s", e)
    
    # Clean up temporary files
    temp_root = tempfile.gettempdir()
    try:
        for folder in os.listdir(temp_root):
            if "tmp" in folder:
                try:
                    folder_path = os.path.join(temp_root, folder)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                except Exception:
                    pass  # Ignore cleanup errors
    except Exception as e:
        logger.warning("Could not clean temp directory: %s", e)
            

def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory and return their paths."""
    # Check file limit first
    if len(uploaded_files) > Config.MAX_FILES:
        logger.info("User uploaded %d PDF(s). More than the maximum allowed (%d)", len(uploaded_files), Config.MAX_FILES)
        raise ValueError(f"Maximum {Config.MAX_FILES} files allowed.")

    temp_dir = tempfile.mkdtemp()
    file_paths = []

    for uploaded_file in uploaded_files:
        if uploaded_file.name.lower().endswith('.pdf'):
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)

    logger.info("Saved %d PDF(s) to temporary directory: %s", len(file_paths), temp_dir)
    return file_paths
