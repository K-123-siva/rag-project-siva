from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFacePipeline
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.logger import setup_logger
from transformers import pipeline
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
        # Cloud HuggingFace setup
        try:
            hf_pipeline = pipeline(
                "text-generation",
                model=Config.LLM_MODEL_CLOUD,
                max_length=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                do_sample=True,
                device=-1  # Use CPU for cloud deployment
            )
            llm = HuggingFacePipeline(pipeline=hf_pipeline)
            logger.info("Using cloud HuggingFace model: %s", Config.LLM_MODEL_CLOUD)
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            # Fallback to a simpler model
            hf_pipeline = pipeline("text-generation", model="gpt2", max_length=200)
            llm = HuggingFacePipeline(pipeline=hf_pipeline)
            logger.info("Using fallback GPT-2 model")

    system_prompt = """
    You are an expert assistant specialized in analyzing PDF documents with a strong focus on statistics and probability. Follow these steps:

    1. **Understand the User Query**: Break down the user's intent and what they want to know.
    2. **Extract from Context**: Refer only to the provided document content for relevant information.
    3. **Be Precise**:
    - For definitions, give exact, concise meanings.
    - For explanations, walk through concepts clearly and thoroughly.
    - For calculations, show detailed step-by-step reasoning.
    - For summaries, outline key points using bullet format if needed.

    4. **Respond like a tutor**: Explain in a simple, educational tone.

    Context:
    {context}

    User Question:
    {input}
    """

    logger.info("Creating RAG chain with deployment mode: %s", Config.DEPLOYMENT_MODE)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt=prompt)

    return create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=question_answer_chain,
    )
