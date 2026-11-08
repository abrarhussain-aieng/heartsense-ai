"""Run Ragas on a small curated dataset using the Gemini LLM + embeddings."""
import json
import os
from pathlib import Path

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from heartsense.rag.retriever import retrieve

DATA = Path(__file__).parent / "rag_eval_dataset.json"

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY required to run Ragas")

    raw = json.loads(DATA.read_text(encoding="utf-8"))

    rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
    llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key))
    for item in raw:
        ctxs = retrieve(item["question"], k=4)
        answer = llm.langchain_llm.invoke(item["question"]).content if hasattr(llm, "langchain_llm") else "n/a"
        rows["question"].append(item["question"])
        rows["answer"].append(answer)
        rows["contexts"].append([c["content"] for c in ctxs])
        rows["ground_truth"].append(item["ground_truth"])

    ds = Dataset.from_dict(rows)
    embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    )
    result = evaluate(
        ds,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm,
        embeddings=embeddings,
    )
    print(result)
    Path("evaluation/ragas_result.json").write_text(json.dumps(result, default=str, indent=2))

if __name__ == "__main__":
    main()