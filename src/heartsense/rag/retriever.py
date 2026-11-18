from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PERSIST_DIR = Path("chroma")
COLLECTION = "cardiovascular_knowledge"
PDF_DIR = Path("data/rag_pdfs")

# Load embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load Vector Store
vectorstore = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=str(PERSIST_DIR),
)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# Load documents for BM25 (Keyword search)
docs = []
for pdf_file in PDF_DIR.glob("*.pdf"):
    loader = PyPDFLoader(str(pdf_file))
    docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400, 
    chunk_overlap=100, 
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(docs)

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 6

def retrieve(query: str, k: int = 8) -> list[dict]:
    """
    Manual Hybrid Search: Combines BM25 and Vector retrieval, then deduplicates.
    Avoids the incompatible EnsembleRetriever import.
    """
    try:
        # 1. Get results from both retrievers
        vector_docs = vector_retriever.invoke(query)
        bm25_docs = bm25_retriever.invoke(query)

        # 2. Merge and deduplicate (based on page content)
        seen_content = set()
        merged_docs = []

        for doc in vector_docs + bm25_docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                merged_docs.append(doc)

        # 3. Format for the MCP tool
        formatted_results = []
        for doc in merged_docs[:k]:
            formatted_results.append({
                "content": doc.page_content,
                "title": doc.metadata.get("source", "AHA Guideline"),
                "url": ""
            })
        return formatted_results

    except Exception as e:
        print(f"Retrieval failed: {e}")
        return []