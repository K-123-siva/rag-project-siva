import os
import sys
sys.path.append('src')

import streamlit as st
from src.document_processing import process_pdfs, get_retriever
from src.llm_chain import create_rag_chain
from src.utils import save_uploaded_files, reset_context
from src.config import Config
from src.logger import setup_logger
from dotenv import load_dotenv

logger = setup_logger(__name__)
load_dotenv()

st.set_page_config(
    page_title="NeuroQuery - AI Document Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
[data-testid="stHeader"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
.stDeployButton {display: none !important;}

/* Mobile optimizations */
@media (max-width: 768px) {
    /* Ensure sidebar toggle button is always visible and clickable */
    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background-color: #0068c9 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        font-size: 18px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Make sidebar full width when expanded on mobile */
    section[data-testid="stSidebar"] {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stSidebar"][aria-expanded="true"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Better spacing for mobile */
    .main .block-container {
        padding-top: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 5rem;
    }
    
    /* Ensure chat input is visible */
    .stChatFloatingInputContainer {
        bottom: 0 !important;
        position: fixed !important;
    }
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

with st.sidebar:
    st.title("PDF Upload")
    st.write(f"Upload up to {Config.MAX_FILES} PDF files")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    
    if uploaded_files and st.button("Process PDFs"):
        reset_context()
        logger.info("User uploaded %d PDF(s)", len(uploaded_files))
        try:
            with st.spinner("Processing PDFs..."):
                pdf_paths = save_uploaded_files(uploaded_files)
                vectorstore = process_pdfs(pdf_paths)
                retriever = get_retriever(vectorstore)
                rag_chain = create_rag_chain(retriever)
                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = rag_chain
                st.session_state.processed_files = [f.name for f in uploaded_files]
                logger.info("RAG chain created successfully")
                st.success("PDFs processed successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Error: {str(e)}", exc_info=True)
    
    st.divider()
    if st.session_state.vectorstore:
        st.success("**Active Documents:**")
        for filename in st.session_state.processed_files:
            st.markdown(f"- {filename}")
        st.info("Ready to answer questions!")
        if st.button("Clear All Context"):
            reset_context()
            st.rerun()
    else:
        st.info("Upload PDFs above to get started")

st.title("PDF Question Answering System")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the PDFs"):
    if not st.session_state.rag_chain:
        st.error("Please upload and process PDF files first.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.rag_chain.invoke({"input": prompt})
                answer = response["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                st.error(f"Error: {str(e)}")
