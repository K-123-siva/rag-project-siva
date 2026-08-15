import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Embeddings Model (FREE - Hugging Face)
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free Hugging Face embeddings
    
    # LLM Model (Groq API - Fast and FREE tier available)
    LLM_MODEL = "llama-3.3-70b-versatile"  # Latest Groq model
    
    # RAG Configuration
    CHUNK_SIZE = 1000  # Larger chunks for better context
    CHUNK_OVERLAP = 200  # More overlap to preserve context
    SEARCH_K = 10  # Retrieve 10 most relevant chunks
    TEMPERATURE = 0.1  # Lower temperature for more accurate extraction
    MAX_TOKENS = 600  # More tokens for detailed answers
    
    # File Processing Limits
    PERSIST_DIR = "db"
    MAX_PAGES = 300
    MAX_FILES = 5
