from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.config import Config
from src.logger import setup_logger
import os
from datetime import datetime

logger = setup_logger(__name__)

# FREE MODELS AVAILABLE ON GROQ (Developer Tier - No Cost)
# Note: openai/gpt-oss models are FREE and open-source, despite the "openai" prefix
# These are NOT OpenAI's proprietary models - they're open-source alternatives
FREE_MODELS = {
    "openai/gpt-oss-20b": {
        "name": "GPT OSS 20B (FREE)", 
        "available": True,
        "cost": "FREE",
        "speed": "1000 t/s",
        "context": 131072,
        "note": "Open-source, fast, FREE for all users"
    },
    "openai/gpt-oss-120b": {
        "name": "GPT OSS 120B (FREE)",
        "available": True,
        "cost": "FREE",
        "speed": "500 t/s",
        "context": 131072,
        "note": "Open-source, more capable, FREE for all users"
    }
}

# DEPRECATED/ENTERPRISE-ONLY MODELS
DEPRECATED_MODELS = {
    "llama-3.3-70b-versatile": {
        "name": "Llama 3.3 70B Versatile",
        "available": False,
        "deprecated_date": "2026-06-17",
        "replacement": "openai/gpt-oss-120b",
        "reason": "Moved to Enterprise tier only (requires paid plan). FREE alternative: openai/gpt-oss-120b or openai/gpt-oss-20b"
    },
    "llama-3.1-8b-instant": {
        "name": "Llama 3.1 8B Instant",
        "available": False,
        "deprecated_date": "2026-06-17",
        "replacement": "openai/gpt-oss-20b",
        "reason": "Deprecated. FREE alternative: openai/gpt-oss-20b"
    }
}

def check_model_availability(model_id):
    """Check if a model is available and return status message"""
    
    # Check if it's a FREE model
    if model_id in FREE_MODELS:
        model_data = FREE_MODELS[model_id]
        if model_data["available"]:
            return True, None
    
    # Check if it's deprecated
    if model_id in DEPRECATED_MODELS:
        model_data = DEPRECATED_MODELS[model_id]
        dep_date = model_data.get("deprecated_date", "Unknown")
        replacement = model_data.get("replacement", "openai/gpt-oss-20b")
        reason = model_data.get("reason", "Model no longer available")
        
        warning_msg = f"""
⚠️ MODEL NOT AVAILABLE ⚠️
Model: {model_data['name']} ({model_id})
Status: {reason}
Deprecated on: {dep_date}

✅ FREE ALTERNATIVE: {replacement}
   • 100% FREE (no cost per token)
   • Available on Developer tier
   • Open-source model

For current FREE models, visit: https://console.groq.com/docs/models
"""
        return False, warning_msg
    
    # Unknown model - let it try
    return True, None

def create_rag_chain(retriever):
    """Create RAG chain using FREE Groq models"""
    
    # Get Groq API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in your .env file or Streamlit secrets.\n"
            "Get your FREE API key from: https://console.groq.com/keys"
        )
    
    # PRIMARY FREE MODEL: openai/gpt-oss-20b
    # Note: Despite the "openai" prefix, this is a FREE open-source model
    # It's NOT OpenAI's proprietary model - it's available at no cost
    model_id = "openai/gpt-oss-20b"
    
    # Check model availability
    is_available, warning_msg = check_model_availability(model_id)
    
    if not is_available:
        logger.warning(warning_msg)
        raise ValueError(warning_msg)
    
    logger.info(f"Using FREE Groq model: {model_id}")
    logger.info("Model: GPT OSS 20B (Open-source, not OpenAI proprietary)")
    logger.info("Cost: FREE | Speed: 1000 t/s | Context: 131K tokens")
    
    # Initialize Groq LLM with FREE model
    try:
        llm = ChatGroq(
            model=model_id,  # FREE open-source model
            temperature=0.1,  # Low temperature for accurate extraction
            max_tokens=600,   # More tokens for detailed lists
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        logger.info(f"✓ Successfully initialized FREE Groq model: {model_id}")
    except Exception as e:
        logger.error(f"Failed to initialize model {model_id}: {e}")
        logger.info("Attempting fallback to openai/gpt-oss-120b (also FREE)...")
        
        # Fallback to another FREE model
        llm = ChatGroq(
            model="openai/gpt-oss-120b",  # Also FREE
            temperature=0.1,
            max_tokens=600,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        logger.info("✓ Using fallback FREE model: openai/gpt-oss-120b")
    
    # Enhanced prompt template focused on extraction
    template = """You are an AI assistant that extracts information from documents accurately.

DOCUMENT CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Read the provided document context CAREFULLY
2. Extract ONLY information that is explicitly stated in the context
3. For questions asking for lists (e.g., "top 10 commands", "list all"):
   - Extract the EXACT items mentioned in the document
   - List them clearly with numbers or bullet points
   - Include descriptions or details if available in the context
4. For specific questions (e.g., "what does X do"):
   - Quote or cite the specific text from the document
5. If the information is NOT in the context, respond: "This information is not available in the uploaded document."
6. Do NOT make up information or provide general knowledge - only use what's in the context
7. Be thorough - if there's a list, include all items mentioned

ANSWER:"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Function to format retrieved documents with better context
    def format_docs(docs):
        if not docs:
            return "No relevant content found."
        
        # Format documents with clear separation and metadata
        formatted = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content.strip()
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"[Source {i} - Page {page}]\n{content}")
        
        result = "\n\n---\n\n".join(formatted)
        logger.info(f"Retrieved {len(docs)} document chunks for context")
        
        # Log first 300 chars for debugging
        logger.info(f"Context preview: {result[:300]}...")
        
        return result
    
    # Create the RAG chain with improved retrieval
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    logger.info("Created RAG chain with Groq")
    
    # Wrapper to match interface and add logging
    class GroqRAGChain:
        def __init__(self, chain):
            self.chain = chain
            
        def invoke(self, inputs):
            question = inputs.get("input", "")
            try:
                logger.info(f"Processing question: {question}")
                answer = self.chain.invoke(question)
                logger.info(f"Generated answer (length: {len(answer)} chars)")
                logger.info(f"Answer preview: {answer[:200]}...")
                return {"answer": answer}
            except Exception as e:
                logger.error(f"Error processing question: {e}", exc_info=True)
                return {"answer": f"Error processing your question: {str(e)}"}
    
    return GroqRAGChain(rag_chain)
