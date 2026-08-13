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
                logger.info("Page %d preview: '%s'", i, content_preview)
                logger.info("Page %d length: %d characters", i, len(page.page_content))
            
            # Filter out empty pages (be very lenient for different PDF types)
            valid_pages = []
            for i, page in enumerate(pages):
                content = page.page_content.strip()
                if len(content) > 3:  # Very lenient - just need some content
                    valid_pages.append(page)
                    logger.info("✅ Page %d accepted: %d characters", i, len(content))
                else:
                    logger.warning("❌ Skipping page %d with minimal content: '%s'", i, content[:100])
            
            documents.extend(valid_pages)
            logger.info("Loaded %d valid pages from %s", len(valid_pages), pdf_path)
            
        except Exception as e:
            logger.error("Error processing %s: %s", pdf_path, str(e))
            # Try multiple alternative PDF readers
            logger.info("Trying alternative PDF processing methods for: %s", pdf_path)
            
            success = False
            
            # Method 1: UnstructuredPDFLoader
            try:
                logger.info("Attempt 1: UnstructuredPDFLoader")
                from langchain_community.document_loaders import UnstructuredPDFLoader
                alt_loader = UnstructuredPDFLoader(pdf_path)
                alt_pages = alt_loader.load()
                
                valid_alt_pages = [page for page in alt_pages if page.page_content.strip()]
                if valid_alt_pages:
                    documents.extend(valid_alt_pages)
                    logger.info("✅ UnstructuredPDFLoader success: %d pages from %s", len(valid_alt_pages), pdf_path)
                    success = True
                
            except Exception as alt_e:
                logger.warning("UnstructuredPDFLoader failed: %s", str(alt_e))
            
            # Method 2: PDFMiner
            if not success:
                try:
                    logger.info("Attempt 2: PDFMiner")
                    from langchain_community.document_loaders import PDFMinerLoader
                    miner_loader = PDFMinerLoader(pdf_path)
                    miner_pages = miner_loader.load()
                    
                    valid_miner_pages = [page for page in miner_pages if page.page_content.strip()]
                    if valid_miner_pages:
                        documents.extend(valid_miner_pages)
                        logger.info("✅ PDFMiner success: %d pages from %s", len(valid_miner_pages), pdf_path)
                        success = True
                        
                except Exception as miner_e:
                    logger.warning("PDFMiner failed: %s", str(miner_e))
            
            # Method 3: Basic text extraction fallback
            if not success:
                try:
                    logger.info("Attempt 3: Creating fallback content")
                    # Create a basic document with filename info
                    from langchain_core.documents import Document
                    fallback_doc = Document(
                        page_content=f"Document: {os.path.basename(pdf_path)}\n\nThis PDF file was uploaded but could not be processed for text extraction. It may contain images, scanned content, or use an unsupported PDF format. File size: {os.path.getsize(pdf_path)} bytes.",
                        metadata={"source": pdf_path, "page": 0}
                    )
                    documents.append(fallback_doc)
                    logger.info("✅ Created fallback document for: %s", pdf_path)
                    success = True
                    
                except Exception as fallback_e:
                    logger.error("All PDF processing methods failed for %s: %s", pdf_path, str(fallback_e))
            
            if not success:
                logger.error("❌ All PDF processing methods failed for: %s", pdf_path)
                continue
    
    logger.info("Total documents collected: %d", len(documents))
    
    if not documents:
        # Create a more helpful error message
        error_msg = "No readable text content found in the uploaded PDF(s). "
        if pdf_paths:
            error_msg += f"Tried processing {len(pdf_paths)} file(s). "
        error_msg += "This could happen if the PDF contains only images, scanned content, or uses an unsupported format. Try uploading a different PDF with text content."
        raise ValueError(error_msg)
        
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