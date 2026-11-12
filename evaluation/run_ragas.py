import json
import time
from pathlib import Path

from datasets import Dataset
from ragas import evaluate
# Import the Classes (Capital Letters) to instantiate them
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from heartsense.config import settings
from heartsense.rag.retriever import retrieve

DATA = Path(__file__).parent / "rag_eval_dataset.json"

def main():
    start_time = time.time()
    
    groq_key = settings.groq_api_key
    gemini_key = settings.gemini_api_key
    
    if not groq_key or not gemini_key:
        raise RuntimeError("Both GROQ_API_KEY and GEMINI_API_KEY are required in .env")

    raw = json.loads(DATA.read_text(encoding="utf-8"))

    rows = {
        "user_input": [], 
        "response": [], 
        "retrieved_contexts": [], 
        "reference": []
    }
    
    # 1. Use Groq for the LLM judge with max_tokens=4096 to prevent truncation
    print(f"Using Groq Model for Evaluation: {settings.groq_model}")
    llm = LangchainLLMWrapper(
        ChatGroq(
            model=settings.groq_model, 
            groq_api_key=groq_key,
            max_tokens=4096  # <--- CRITICAL FIX for LLMDidNotFinishException
        )
    )
    
    print("Generating answers and retrieving contexts...")
    for item in raw:
        ctxs = retrieve(item["question"], k=4)
        
        response = llm.langchain_llm.invoke(item["question"]).content
        
        if isinstance(response, str):
            answer = response
        elif isinstance(response, list):
            text_blocks = []
            for block in response:
                if isinstance(block, str):
                    text_blocks.append(block)
                elif isinstance(block, dict) and "text" in block:
                    text_blocks.append(block["text"])
            answer = " ".join(text_blocks)
        else:
            answer = str(response)

        rows["user_input"].append(item["question"])
        rows["response"].append(answer)
        rows["retrieved_contexts"].append([c["content"] for c in ctxs])
        rows["reference"].append(item["ground_truth"])

    ds = Dataset.from_dict(rows)
    
    # 2. Use the NEW embedding model (gemini-embedding-001)
    embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",  # <--- CRITICAL FIX for 404 Error
            google_api_key=gemini_key
        )
    )
    
    print("Running Ragas evaluation (this will be fast)...")
    result = evaluate(
        ds,
        metrics=[
            Faithfulness(), 
            AnswerRelevancy(), 
            ContextPrecision(), 
            ContextRecall()
        ],
        llm=llm,
        embeddings=embeddings,
    )
    
    print("\n--- RAGAS RESULTS ---")
    print(result)
    
    # 3. Save results safely
    try:
        result_dict = result.to_pandas().to_dict(orient="records")
        for record in result_dict:
            for key in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
                if key in record:
                    val = record[key]
                    if isinstance(val, float) and str(val) == 'nan':
                        record[key] = 0.0
                    elif isinstance(val, float):
                        record[key] = round(val, 2)
                    else:
                        record[key] = 0.0
                        
        Path("evaluation/ragas_result.json").write_text(json.dumps(result_dict, indent=2))
        print("\n✅ Results saved to evaluation/ragas_result.json")
    except Exception as e:
        print(f"\n⚠️ Could not save results to JSON: {e}")

    end_time = time.time()
    print(f"\n⏱️ Total execution time: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    main()