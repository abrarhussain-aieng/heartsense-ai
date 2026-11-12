"""Ingest curated cardiovascular sources into ChromaDB."""
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Use local embeddings
from langchain_chroma import Chroma

SOURCES_FILE = Path(__file__).parent / "sources.json"
PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"

def ingest():
    raw = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    docs = [
        Document(
            page_content=item["content"],
            metadata={"id": item["id"], "title": item["title"], "url": item["url"], "source": "curated"},
        )
        for item in raw
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(docs)

    # Use a local model - no API keys needed, no 404 errors, instant speed
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(PERSIST_DIR),
    )
    return {"documents": len(docs), "chunks": len(chunks)}

if __name__ == "__main__":
    print(ingest())