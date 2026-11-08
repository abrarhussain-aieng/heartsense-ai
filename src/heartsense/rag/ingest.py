"""Ingest curated cardiovascular sources into ChromaDB."""
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from heartsense.config import settings

SOURCES_FILE = Path(__file__).parent / "sources.json"
PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"

def ingest():
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY required for Gemini embeddings")

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

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.gemini_api_key,
    )
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(PERSIST_DIR),
    )
    return {"documents": len(docs), "chunks": len(chunks)}

if __name__ == "__main__":
    print(ingest())