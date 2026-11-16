from functools import lru_cache
from pathlib import Path
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"

@lru_cache(maxsize=1)
def _store() -> Chroma:
    # Use local embeddings so it works without cloud API keys
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )

def retrieve(query: str, k: int = 4) -> List[Dict]:
    try:
        # Returns list of (Document, distance)
        results = _store().similarity_search_with_score(query, k=k)
    except Exception as e:
        print(f"ChromaDB search failed: {e}")
        return []
        
    out = []
    for doc, distance in results:
        # Removed the strict threshold. We will always return the top k results.
        
        # Normalize L2 distance to a 0.0 - 1.0 relevance score.
        relevance = max(0.0, 1.0 - (distance / 2.0))
        
        out.append({
            "content": doc.page_content,
            "title": doc.metadata.get("title", ""),
            "url": doc.metadata.get("url", ""),
            "source_id": doc.metadata.get("id", ""),
            "relevance": float(relevance),
        })
        
    return out