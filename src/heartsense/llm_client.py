from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from heartsense.config import settings

def get_llm(temperature: float = 0.0):
    if settings.gemini_api_key:
        primary = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            max_retries=1,
            timeout=30,
        )
    else:
        primary = None

    fallback = None
    if settings.groq_api_key:
        fallback = ChatGroq(
            model=settings.groq_model,
            groq_api_key=settings.groq_api_key,
            temperature=temperature,
            max_retries=1,
            timeout=30,
        )

    if primary and fallback:
        return primary.with_fallbacks([fallback])
    if primary:
        return primary
    if fallback:
        return fallback
    raise RuntimeError("No LLM API key configured (GEMINI_API_KEY or GROQ_API_KEY)")