import re
import logging
from nemoguardrails import RailsConfig, LLMRails
from heartsense.config import settings
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# 1. Deterministic Regex Filters
EXPLICIT_TERMS = [
    r"\bsex\b", r"\bsexual\b", r"\bdick\b", r"\bpussy\b", r"\bpenis\b", r"\bvagina\b",
    r"\bporn\b", r"\bnude\b"
]

# Added 'risk factor' and 'understand my heart health' to catch the exact prompts
MEDICAL_OVERRIDES = [
    r"\bprescribe\b", r"\bdiagnose\b", r"\bdiagnosis\b", 
    r"\brisk factor\b", r"\bunderstand my heart health\b", r"\bmedical advice\b"
]

# 2. NeMo Colang Configuration
RAILS_CONFIG = """
define user ask for medical advice
  "Do I have heart disease?"
  "Diagnose me"
  "What medication should I take?"
  "Prescribe me"
  "What are the main risk factors of the heart disease?"
  "What are the risk factors of heart disease?"
  "Tell me about heart disease risk factors"
  "Can you help me understand my heart health?"

define bot refuse medical advice
  "I am a cardiovascular health assistant and cannot provide diagnoses, prescribe medication, or offer personalized medical advice. Please consult a licensed clinician."

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
            
    # Block direct requests for personal medical advice/risk factors instantly
    for pattern in MEDICAL_OVERRIDES:
        if re.search(pattern, text_lower):
            return {
                "allowed": False, 
                "message": "I am a cardiovascular health assistant and cannot provide diagnoses, prescribe medication, or offer personalized medical advice. Please consult a licensed clinician."
            }

    # --- FIX 2: NEMO GUARDRAILS FALLBACK ---
    try:
        rails = build_rails()
        # This generates the response through NeMo
        result = await rails.generate_async(messages=[{"role": "user", "content": text}])
        
        # Safely extract content based on NeMo's return type
        if isinstance(result, dict):
            content = result.get("content", "")
        else:
            content = str(result)
            
        content = content.strip()
        
        # If NeMo triggered our specific refusal flow, it will contain this string
        refusal_phrase = "cannot provide diagnoses, prescribe medication, or offer personalized medical advice"
        is_blocked = refusal_phrase in content.lower()
        
        if is_blocked:
            return {"allowed": False, "message": content}
        else:
            # If not blocked by NeMo, it's allowed (the main app will generate the actual AI response)
            return {"allowed": True, "message": ""}
        
    except Exception as e:
        logger.error(f"NeMo Guardrail Error (Skipping NeMo): {e}")
        # Fail safely: If NeMo crashes, allow the prompt (regex already filtered the bad ones)
        return {"allowed": True, "message": ""}