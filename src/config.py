import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # 🆓 100% FREE - No API keys needed!
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free Hugging Face embeddings
    
    # Choose deployment mode based on environment
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")  # "local" or "cloud"
    
    # Local Ollama settings (fallback to HuggingFace if Ollama not available)
    LLM_MODEL_LOCAL = "tinyllama:1.1b"  # For local Ollama
    
    # Cloud: 100% FREE HuggingFace models (no API keys required!)
    LLM_MODEL_CLOUD = "microsoft/DialoGPT-medium"  # Free conversational model
    
    # Use appropriate model based on deployment
    LLM_MODEL = LLM_MODEL_LOCAL if DEPLOYMENT_MODE == "local" else LLM_MODEL_CLOUD
    
    CHUNK_SIZE = 800  # Smaller for HuggingFace models
    CHUNK_OVERLAP = 150
    SEARCH_K = 4  # Reduced for faster processing
    TEMPERATURE = 0.7
    MAX_TOKENS = 150  # Optimized for free models
    PERSIST_DIR = "db"
    MAX_PAGES = 300
    MAX_FILES = 3
