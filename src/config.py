import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # For cloud deployment - using HuggingFace models (no API key needed)
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free Hugging Face model
    
    # Choose deployment mode based on environment
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")  # "local" or "cloud"
    
    # Local Ollama settings
    LLM_MODEL_LOCAL = "tinyllama:1.1b"  # For local Ollama
    
    # Cloud HuggingFace settings (no API key required)
    LLM_MODEL_CLOUD = "microsoft/DialoGPT-small"  # Free cloud model
    
    # Use appropriate model based on deployment
    LLM_MODEL = LLM_MODEL_LOCAL if DEPLOYMENT_MODE == "local" else LLM_MODEL_CLOUD
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    SEARCH_K = 5
    TEMPERATURE = 0.3
    MAX_TOKENS = 512  # Reduced for cloud compatibility
    PERSIST_DIR = "db"
    MAX_PAGES = 300
    MAX_FILES = 3
