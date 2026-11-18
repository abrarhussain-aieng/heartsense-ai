from functools import lru_cache
from pathlib import Path
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from heartsense.config import settings

PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"

# FIXED: Removed the strict 1.2 threshold. 
# We will do filtering in the LLM prompt instead.
MAX_DISTANCE_THRESHOLD = 2.0 

@lru_cache(maxsize=1)
def _store() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )

def retrieve(query: str, k: int = 8) -> List[Dict]:
    try:
        results = _store().similarity_search_with_score(query, k=k)
    except Exception as e:
        print(f"ChromaDB search failed: {e}")
        return []
        
    out = []
    for doc, distance in results:
        # Print to console for debugging
        print(f"[RAG] Found doc. Distance: {distance}")
        
        if distance > MAX_DISTANCE_THRESHOLD: 
            continue
            
        relevance = max(0.0, 1.0 - (distance / 2.0))
        
        out.append({
            "content": doc.page_content,
            "title": doc.metadata.get("title", ""),
            "url": doc.metadata.get("url", ""),
            "source_id": doc.metadata.get("id", ""),
            "relevance": float(relevance),
        })
        
    return out