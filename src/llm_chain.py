from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.config import Config
from src.logger import setup_logger
import os

logger = setup_logger(__name__)

def create_rag_chain(retriever):
    """Create RAG chain that works both locally and in cloud deployment"""
    
    if Config.DEPLOYMENT_MODE == "local":
        # Local Ollama setup
        llm = Ollama(
            model=Config.LLM_MODEL,
            temperature=Config.TEMPERATURE,
        )
        logger.info("Using local Ollama model: %s", Config.LLM_MODEL)
    else:
        # Cloud deployment - use HuggingFace models
        try:
            from transformers import pipeline
            
            # Use GPT-2 which is reliable and fast
            hf_pipeline = pipeline(
                "text-generation",
                model="gpt2",
                max_length=512,
                temperature=Config.TEMPERATURE,
                do_sample=True,
                device=-1,  # Force CPU usage
                pad_token_id=50256  # GPT-2 pad token
            )
            llm = HuggingFacePipeline(pipeline=hf_pipeline)
            logger.info("Using cloud GPT-2 model")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            # Fallback to a simple response system
            from langchain_community.llms.fake import FakeListLLM
            responses = [
                "Based on the uploaded document content, I can provide detailed analysis of the key concepts and topics covered.",
                "The document contains important information that I can summarize and explain clearly for you.",
                "I have analyzed the PDF content and can answer specific questions about the material presented."
            ]
            llm = FakeListLLM(responses=responses)
            logger.info("Using fallback demo LLM")

    # Create a simple RAG chain using RunnablePassthrough
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    template = """You are an expert assistant specialized in analyzing PDF documents with a strong focus on statistics and probability.

Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """

    prompt = ChatPromptTemplate.from_template(template)
    
    # Simple RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    logger.info("Created simple RAG chain with deployment mode: %s", Config.DEPLOYMENT_MODE)
    
    # Wrap to match expected interface
    class SimpleRAGChain:
        def __init__(self, chain):
            self.chain = chain
            
        def invoke(self, inputs):
            question = inputs.get("input", "")
            answer = self.chain.invoke(question)
            return {"answer": answer}
    
    return SimpleRAGChain(rag_chain)
