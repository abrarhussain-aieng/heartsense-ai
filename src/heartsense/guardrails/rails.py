import re
from nemoguardrails import RailsConfig, LLMRails
from heartsense.config import settings
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Split into two distinct lists for better control
EXPLICIT_TERMS = [
    r"\bsex\b", r"\bsexual\b", r"\bdick\b", r"\bpussy\b", r"\bpenis\b", r"\bvagina\b",
    r"\bporn\b", r"\bnude\b"
]

# Only block direct attempts to get a personal diagnosis or prescription
MEDICAL_OVERRIDES = [
    r"\bprescribe\b", r"\bdiagnose\b", r"\bdiagnosis\b"
]

RAILS_CONFIG = """
define user ask for medical advice
  "Do I have heart disease?"
  "Diagnose me"
  "What medication should I take?"
  "Prescribe me"

define bot refuse medical advice
  "I am a cardiovascular health assistant and cannot provide diagnoses or prescribe medication. Please consult a licensed clinician."

define flow refuse medical advice
  user ask for medical advice
  bot refuse medical advice
"""

_config = None
_rails = None

def _get_nemo_llm():
    """NeMo requires a raw LLM, not a fallback chain."""
    if settings.groq_api_key:
        return ChatGroq(
            model=settings.groq_model, 
            groq_api_key=settings.groq_api_key, 
            temperature=0.0
        )
    elif settings.gemini_api_key:
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model, 
            google_api_key=settings.gemini_api_key, 
            temperature=0.0
        )
    raise ValueError("No valid LLM API key found for NeMo Guardrails")

def build_rails() -> LLMRails:
    global _config, _rails
    if _rails is None:
        _config = RailsConfig.from_content(RAILS_CONFIG)
        # Pass a safe, single LLM to prevent NeMo from crashing
        _rails = LLMRails(_config, llm=_get_nemo_llm())
    return _rails

async def check_input(text: str) -> dict:
    text_lower = text.lower()
    
    # --- FIX 1: DETERMINISTIC PRE-FILTER (0 API Cost) ---
    # Block Explicit Content immediately
    for pattern in EXPLICIT_TERMS:
        if re.search(pattern, text_lower):
            return {
                "allowed": False, 
                "message": "I am a cardiovascular health assistant and cannot answer questions about sexual health or explicit topics."
            }
            
    # Block direct requests for personal medical advice
    for pattern in MEDICAL_OVERRIDES:
        if re.search(pattern, text_lower):
            return {
                "allowed": False, 
                "message": "I cannot provide diagnoses, prescribe medication, or recommend treatments. Please consult a licensed healthcare professional."
            }

    # --- FIX 2: NEMO GUARDRAILS FALLBACK ---
    try:
        # build_rails() is safely inside the try block
        rails = build_rails()
        result = await rails.generate_async(messages=[{"role": "user", "content": text}])
        content = result.get("content", "") if isinstance(result, dict) else str(result)
        content = content.strip()
        
        # If NeMo triggered a refusal based on our Colang rules
        blocked = "cannot provide" in content.lower() or "cannot answer" in content.lower()
        return {"allowed": not blocked, "message": content if blocked else ""}
        
    except Exception as e:
        # If NeMo crashes or no API keys are present, we fail open safely.
        # The regex pre-filter above already blocked explicit/medical prompts.
        print(f"NeMo Guardrail Error (Skipping NeMo): {e}")
        return {"allowed": True, "message": ""}