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

# Try importing enhanced PDF extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available - using basic PyPDFLoader")

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf not available")

def extract_text_enhanced(pdf_path):
    """Enhanced text extraction supporting multiple methods for better accuracy"""
    from langchain_core.documents import Document
    extracted_pages = []
    
    # Method 1: Try pdfplumber (best for tables and structured content)
    if PDFPLUMBER_AVAILABLE:
        try:
            logger.info(f"Trying pdfplumber extraction for {pdf_path}")
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    
                    # Also extract tables
                    tables = page.extract_tables()
                    table_text = ""
                    if tables:
                        for table in tables:
                            for row in table:
                                if row:
                                    table_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                    
                    # Combine text and tables
                    full_text = text if text else ""
                    if table_text:
                        full_text += "\n\nTABLES:\n" + table_text
                    
                    if full_text.strip():
                        doc = Document(
                            page_content=full_text,
                            metadata={
                                "source": pdf_path,
                                "page": page_num,
                                "filename": os.path.basename(pdf_path)
                            }
                        )
                        extracted_pages.append(doc)
                        logger.info(f"pdfplumber: Page {page_num+1} extracted ({len(full_text)} chars)")
            
            if extracted_pages:
                logger.info(f"✅ pdfplumber extracted {len(extracted_pages)} pages")
                return extracted_pages
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
    
    # Method 2: Try pypdf (fallback)
    if PYPDF_AVAILABLE:
        try:
            logger.info(f"Trying pypdf extraction for {pdf_path}")
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "page": page_num,
                            "filename": os.path.basename(pdf_path)
                        }
                    )
                    extracted_pages.append(doc)
                    logger.info(f"pypdf: Page {page_num+1} extracted ({len(text)} chars)")
            
            if extracted_pages:
                logger.info(f"✅ pypdf extracted {len(extracted_pages)} pages")
                return extracted_pages
        except Exception as e:
            logger.warning(f"pypdf extraction failed: {e}")
    
    # Method 3: PyPDFLoader (last resort)
    try:
        logger.info(f"Using PyPDFLoader for {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        for page in pages:
            if page.page_content.strip():
                extracted_pages.append(page)
        
        if extracted_pages:
            logger.info(f"✅ PyPDFLoader extracted {len(extracted_pages)} pages")
            return extracted_pages
    except Exception as e:
        logger.error(f"PyPDFLoader extraction failed: {e}")
    
    return extracted_pages

def process_pdfs(pdf_paths):
    """Enhanced PDF processing with multiple extraction methods"""
    documents = []
    
    for pdf_path in pdf_paths:
        try:
            logger.info("=" * 60)
            logger.info(f"Processing PDF: {pdf_path}")
            logger.info("=" * 60)
            
            # Use enhanced extraction
            pages = extract_text_enhanced(pdf_path)
            
            if pages:
                logger.info(f"✅ Extracted {len(pages)} pages from {os.path.basename(pdf_path)}")
                
                # Log content preview for each page
                for i, page in enumerate(pages):
                    content = page.page_content.strip()
                    if content:
                        preview = content[:500].replace('\n', ' ')
                        logger.info(f"Page {i+1} preview: {preview}...")
                        documents.append(page)
            else:
                logger.warning(f"⚠️ No text extracted from {pdf_path}")
                from langchain_core.documents import Document
                filename = os.path.basename(pdf_path)
                fallback_doc = Document(
                    page_content=f"Document '{filename}' was uploaded but no text could be extracted. It may be an image-based PDF, scanned document, or contain only images.",
                    metadata={"source": pdf_path, "filename": filename}
                )
                documents.append(fallback_doc)
                
        except Exception as e:
            logger.error(f"❌ Failed to process {pdf_path}: {str(e)}", exc_info=True)
            from langchain_core.documents import Document
            filename = os.path.basename(pdf_path)
            
            error_doc = Document(
                page_content=f"Error processing document '{filename}': {str(e)}",
                metadata={"source": pdf_path, "filename": filename, "error": str(e)}
            )
            documents.append(error_doc)
    
    logger.info("=" * 60)
    logger.info(f"📊 TOTAL: {len(documents)} document pages extracted")
    logger.info("=" * 60)
    
    if not documents:
        raise ValueError("No documents were successfully processed from the uploaded PDFs")
    
    # Split documents into chunks with better overlap for context preservation
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        length_function=len,
    )
    splits = text_splitter.split_documents(documents)
    logger.info(f"📄 Created {len(splits)} text chunks from {len(documents)} document pages")
    
    # Log sample chunks
    if splits:
        for i, chunk in enumerate(splits[:3]):  # Show first 3 chunks
            preview = chunk.page_content[:200].replace('\n', ' ')
            logger.info(f"Chunk {i+1} preview: {preview}...")
    
    # Create embeddings
    try:
        logger.info(f"🔧 Creating embeddings with model: {Config.EMBEDDING_MODEL}")
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create in-memory vectorstore
        logger.info("🗄️ Building vector database...")
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
        )
        
        logger.info(f"✅ Vectorstore created with {len(splits)} chunks!")
        return vectorstore
        
    except Exception as e:
        logger.error(f"❌ Vectorstore creation failed: {str(e)}", exc_info=True)
        raise ValueError(f"System error during vectorstore creation: {str(e)}")

def get_retriever(vectorstore):
    """Create retriever with optimized search parameters for structured documents"""
    logger.info("Creating retriever with MMR (Maximum Marginal Relevance) search")
    
    # Use MMR to get diverse, relevant chunks - important for structured docs
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Diversified search for better coverage
        search_kwargs={
            "k": 10,  # Retrieve more chunks
            "fetch_k": 20,  # Fetch more initially before MMR filtering
            "lambda_mult": 0.5  # Balance between relevance and diversity
        }
    )
    
    logger.info("✅ Retriever created with MMR search (k=10, fetch_k=20)")
    return retriever