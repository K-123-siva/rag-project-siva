# streamlit_app.py - 🆓 100% FREE RAG System 
import asyncio
import os
import sys

# Add src to Python path
sys.path.append('src')

import streamlit as st
from src.document_processing import process_pdfs, get_retriever
from src.llm_chain import create_rag_chain
from src.utils import save_uploaded_files,reset_context
from src.config import Config
from src.logger import setup_logger
from dotenv import load_dotenv

logger = setup_logger(__name__)
load_dotenv()

# 🆓 No API keys needed! Using FREE HuggingFace models
logger.info("🆓 Starting 100% FREE RAG system - no API costs!")

st.set_page_config(
    page_title="NeuroQuery - 🆓 FREE AI Document Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

with st.sidebar:
    st.title("PDF Upload")
    st.write(f"Upload up to {Config.MAX_FILES} PDF files (max {Config.MAX_PAGES} pages each)")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Process PDFs"):
        reset_context()  # Reset context before processing new files
        logger.info("User uploaded %d PDF(s)", len(uploaded_files))
        try:
            with st.spinner("Processing PDFs..."):
                pdf_paths = save_uploaded_files(uploaded_files)
                vectorstore = process_pdfs(pdf_paths)
                retriever = get_retriever(vectorstore)
                rag_chain = create_rag_chain(retriever)

                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = rag_chain
                logger.info("RAG chain created successfully with %d documents", len(vectorstore._collection.get()['ids']))
                st.success("PDFs processed successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Clear context if no file is uploaded
    if not uploaded_files and st.session_state.vectorstore:
        reset_context()
        st.success("Context cleared because no files are uploaded.")

    # Manual reset button
    if st.button("Clear All Context"):
        reset_context()
        st.success("Context and uploaded files cleared.")


st.title("🧠 NeuroQuery - FREE AI Document Assistant")
st.markdown("### 🆓 **100% FREE** - No API Keys Required!")
st.markdown("*Powered by free Hugging Face models - works with ANY PDF type!*")

# Add usage instructions
st.info("📋 **How to use:** Upload ANY PDF (text or scanned), ask questions, and get intelligent AI responses - completely free!")

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
                logger.error(f"Error generating answer: {str(e)}")
                st.error(f"Error generating answer: {str(e)}")