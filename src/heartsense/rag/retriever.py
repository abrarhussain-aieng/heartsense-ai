"""Retriever that returns grounded excerpts with source metadata."""
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from heartsense.config import settings

PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"
SCORE_THRESHOLD = 0.25  # cosine similarity floor

@lru_cache(maxsize=1)
def _store() -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.gemini_api_key,
    )
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )

def retrieve(query: str, k: int = 4) -> List[Dict]:
    if not settings.gemini_api_key:
        return []
    try:
        results = _store().similarity_search_with_relevance_scores(query, k=k)
    except Exception:
        return []
    out = []
    for doc, score in results:
        if score is None or score < SCORE_THRESHOLD:
            continue
        out.append({
            "content": doc.page_content,
            "title": doc.metadata.get("title", ""),
            "url": doc.metadata.get("url", ""),
            "source_id": doc.metadata.get("id", ""),
            "relevance": float(score),
        })
    return out