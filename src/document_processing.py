from langchain_community.document_loaders import PyPDFLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import Config
from src.logger import setup_logger
logger = setup_logger(__name__)
import os
import tempfile

def process_pdfs(pdf_paths):
    """Process multiple PDF files into a vector store (cloud-compatible in-memory version)."""
    documents = []
    
    for pdf_path in pdf_paths:
        try:
            logger.info("Loading PDF: %s", pdf_path)
            
            # Check if file exists and has content
            if not os.path.exists(pdf_path):
                logger.error("File does not exist: %s", pdf_path)
                continue
                
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                logger.error("File is empty: %s", pdf_path)
                continue
                
            logger.info("PDF file size: %d bytes", file_size)
            
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            logger.info("Raw pages loaded: %d", len(pages))
            
            # Debug: log first few characters of each page
            for i, page in enumerate(pages[:3]):  # Check first 3 pages
                content_preview = page.page_content[:200].strip()
                logger.info("Page %d preview: %s", i, content_preview)
            
            # Filter out empty pages (be more lenient)
            valid_pages = []
            for page in pages:
                content = page.page_content.strip()
                if len(content) > 10:  # At least 10 characters
                    valid_pages.append(page)
                else:
                    logger.warning("Skipping page with minimal content: %s", content[:50])
            
            documents.extend(valid_pages)
            logger.info("Loaded %d valid pages from %s", len(valid_pages), pdf_path)
            
        except Exception as e:
            logger.error("Error processing %s: %s", pdf_path, str(e))
            # Try alternative PDF readers if PyPDF fails
            try:
                logger.info("Trying alternative PDF processing for: %s", pdf_path)
                from langchain_community.document_loaders import UnstructuredPDFLoader
                alt_loader = UnstructuredPDFLoader(pdf_path)
                alt_pages = alt_loader.load()
                
                valid_alt_pages = [page for page in alt_pages if page.page_content.strip()]
                documents.extend(valid_alt_pages)
                logger.info("Alternative loader success: %d pages from %s", len(valid_alt_pages), pdf_path)
                
            except Exception as alt_e:
                logger.error("Alternative loader also failed for %s: %s", pdf_path, str(alt_e))
                continue
    
    logger.info("Total documents collected: %d", len(documents))
    
    if not documents:
        raise ValueError("No valid documents found in the uploaded PDFs. Please check if the PDFs contain readable text content.")
        
    logger.info("Total loaded documents: %d", len(documents))
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )
    splits = text_splitter.split_documents(documents)
    
    if not splits:
        raise ValueError("No text chunks created from documents")
        
    logger.info("Split %d documents into %d chunks", len(documents), len(splits))
    
    # Create embeddings using free Hugging Face model
    try:
        logger.info("Creating embeddings with model: %s", Config.EMBEDDING_MODEL)
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Test embedding creation with a sample text
        test_embedding = embeddings.embed_query("test")
        if not test_embedding:
            raise ValueError("Embedding model is not working properly")
            
        logger.info("Embedding model loaded successfully")
        
    except Exception as e:
        logger.error("Failed to create embeddings: %s", str(e))
        raise ValueError(f"Embedding model creation failed: {str(e)}")
    
    # Create Chroma vectorstore - IN MEMORY for cloud deployment
    try:
        if Config.DEPLOYMENT_MODE == "cloud":
            # In-memory vectorstore for cloud deployment (no persistence)
            logger.info("Creating in-memory vectorstore for cloud deployment")
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                # No persist_directory - keeps it in memory only
            )
        else:
            # Local development with persistence
            logger.info("Creating persistent vectorstore for local deployment")
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=Config.PERSIST_DIR,
            )
        
        logger.info("Vectorstore created successfully with %d chunks", len(splits))
        
    except Exception as e:
        logger.error("Failed to create vectorstore: %s", str(e))
        raise ValueError(f"Vectorstore creation failed: {str(e)}")
    
    return vectorstore

def get_retriever(vectorstore):
    logger.info("Creating retriever with search_k=%d", Config.SEARCH_K)
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": Config.SEARCH_K}
    )