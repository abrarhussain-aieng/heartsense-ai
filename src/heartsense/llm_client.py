import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from heartsense.config import settings

def get_llm(temperature: float = 0.0):
    models = []

    # 1. Groq Primary (Blazing fast, highly reliable)
    if settings.groq_api_key:
        models.append(
            ChatGroq(
                model=settings.groq_model,
                groq_api_key=settings.groq_api_key,
                temperature=temperature,
                max_retries=1,
                timeout=15,
            )
        )

    # 2. Cerebras Secondary (Extremely fast, but sometimes queues)
    if settings.cerebras_api_key:
        models.append(
            ChatOpenAI(
                model=settings.cerebras_model,
                api_key=settings.cerebras_api_key,
                base_url="https://api.cerebras.ai/v1",
                temperature=temperature,
                max_retries=1,
                timeout=15,
                default_headers={"X-Cerebras-3rd-Party-Integration": "langchain"}
            )
        )

    # 3. Gemini Tertiary (Reliable fallback)
    if settings.gemini_api_key:
        models.append(
            ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.gemini_api_key,
                temperature=temperature,
                max_retries=1,
                timeout=20,
            )
        )

    if not models:
        raise RuntimeError("No LLM API key configured (GROQ, CEREBRAS, or GEMINI)")

    # Chain them together
    if len(models) > 1:
        return models[0].with_fallbacks(models[1:])
    return models[0]