import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # 🆓 100% FREE - No API keys needed!
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free Hugging Face embeddings
    
    # Choose deployment mode based on environment
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")  # "local" or "cloud"
    
    # Local Ollama settings - Using better model for accuracy
    LLM_MODEL_LOCAL = "llama3.2:3b"  # Better model for accurate extraction
    
    # Cloud: 100% FREE HuggingFace models (no API keys required!)
    LLM_MODEL_CLOUD = "microsoft/DialoGPT-medium"  # Free conversational model
    
    # Use appropriate model based on deployment
    LLM_MODEL = LLM_MODEL_LOCAL if DEPLOYMENT_MODE == "local" else LLM_MODEL_CLOUD
    
    CHUNK_SIZE = 1000  # Larger chunks for better context
    CHUNK_OVERLAP = 200  # More overlap to preserve context
    SEARCH_K = 8  # More chunks for comprehensive answers
    TEMPERATURE = 0.1  # Lower temperature for more accurate extraction
    MAX_TOKENS = 600  # More tokens for detailed answers
    PERSIST_DIR = "db"
    MAX_PAGES = 300
    MAX_FILES = 3
