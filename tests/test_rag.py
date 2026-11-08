from heartsense.rag.retriever import retrieve

def test_retrieve_handles_missing_key():
    # With no GEMINI_API_KEY configured, retriever returns []
    result = retrieve("What is high cholesterol?", k=2)
    assert isinstance(result, list)