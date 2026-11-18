"""Ingest curated cardiovascular PDFs into ChromaDB."""
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Use local embeddings
from langchain_chroma import Chroma

# Point to the folder where you moved your 3 PDFs
PDF_DIR = Path("data/rag_pdfs")
PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"

def ingest():
    docs = []
    
    # Check if the folder exists and has PDFs
    if not PDF_DIR.exists():
        return {"error": f"Directory {PDF_DIR} not found."}

    # Load all PDFs in the folder
    for pdf_file in PDF_DIR.glob("*.pdf"):
        print(f"Loading: {pdf_file.name}...")
        loader = PyPDFLoader(str(pdf_file))
        docs.extend(loader.load())

    if not docs:
        return {"error": "No PDF documents found to ingest."}

    print(f"Loaded {len(docs)} pages. Splitting into chunks...")
    
    # FIXED: Smaller chunk size and explicit sentence separators to prevent context dilution
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    print(f"Creating {len(chunks)} chunks. Generating embeddings (this may take a moment)...")
    
    # Use your local model - no API keys needed
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Save to ChromaDB
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(PERSIST_DIR),
    )
    
    return {"documents_loaded": len(docs), "chunks_created": len(chunks)}

if __name__ == "__main__":
    result = ingest()
    print("✅ Ingestion Complete!")
    print(result)