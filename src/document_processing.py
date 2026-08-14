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
    """Enhanced PDF processing with better text extraction"""
    documents = []
    
    for pdf_path in pdf_paths:
        try:
            logger.info("Processing PDF: %s", pdf_path)
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            logger.info(f"Loaded {len(pages)} pages from PDF")
            
            # Process each page and extract content
            valid_pages = 0
            for i, page in enumerate(pages):
                content = page.page_content.strip()
                
                # Log first 500 chars of each page for debugging
                if content:
                    logger.info(f"Page {i+1} content preview: {content[:200]}...")
                    documents.append(page)
                    valid_pages += 1
                else:
                    logger.warning(f"Page {i+1} has no text content")
            
            logger.info(f"✅ Successfully extracted {valid_pages} valid pages from {os.path.basename(pdf_path)}")
            
            # Only create fallback if NO pages had ANY content
            if valid_pages == 0:
                logger.warning(f"No text content found in PDF: {pdf_path}")
                from langchain_core.documents import Document
                
                filename = os.path.basename(pdf_path)
                fallback_doc = Document(
                    page_content=f"Document '{filename}' was uploaded but no text could be extracted. It may be an image-based PDF or scanned document.",
                    metadata={"source": pdf_path, "filename": filename}
                )
                documents.append(fallback_doc)
                
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {str(e)}", exc_info=True)
            from langchain_core.documents import Document
            filename = os.path.basename(pdf_path)
            
            error_doc = Document(
                page_content=f"Error processing document '{filename}': {str(e)}",
                metadata={"source": pdf_path, "filename": filename, "error": str(e)}
            )
            documents.append(error_doc)
    
    logger.info(f"Total documents extracted: {len(documents)}")
    
    if not documents:
        raise ValueError("No documents were successfully processed from the uploaded PDFs")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    logger.info(f"Created {len(splits)} text chunks from {len(documents)} documents")
    
    # Log sample of chunks for debugging
    if splits:
        logger.info(f"Sample chunk preview: {splits[0].page_content[:150]}...")
    
    # Create embeddings - simple and reliable
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create in-memory vectorstore (cloud-friendly)
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
        )
        
        logger.info("✅ Vectorstore created successfully!")
        return vectorstore
        
    except Exception as e:
        logger.error("Vectorstore creation failed: %s", str(e))
        raise ValueError(f"System error: {str(e)}")

def get_retriever(vectorstore):
    """Create retriever with optimized search parameters"""
    logger.info("Creating retriever with similarity search")
    
    # Increase k to get more context chunks for better answers
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 8  # Retrieve more chunks for comprehensive answers
        }
    )
    
    logger.info("✅ Retriever created successfully")
    return retriever