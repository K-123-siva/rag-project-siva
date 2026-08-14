from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)

def create_rag_chain(retriever):
    """Create RAG chain using Ollama for accurate document extraction"""
    
    logger.info(f"Using Ollama model: {Config.LLM_MODEL} for document analysis")
    
    # Initialize Ollama LLM with optimized settings for extraction
    llm = Ollama(
        model=Config.LLM_MODEL,
        temperature=0.1,  # Low temperature for accurate extraction
        num_predict=600,   # More tokens for detailed lists
    )
    
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
    
    logger.info("✅ Created RAG chain with Ollama")
    
    # Wrapper to match interface and add logging
    class OllamaRAGChain:
        def __init__(self, chain):
            self.chain = chain
            
        def invoke(self, inputs):
            question = inputs.get("input", "")
            try:
                logger.info(f"🔍 Processing question: {question}")
                answer = self.chain.invoke(question)
                logger.info(f"✅ Generated answer (length: {len(answer)} chars)")
                logger.info(f"Answer preview: {answer[:200]}...")
                return {"answer": answer}
            except Exception as e:
                logger.error(f"❌ Error processing question: {e}", exc_info=True)
                return {"answer": f"Error processing your question: {str(e)}"}
    
    return OllamaRAGChain(rag_chain)
