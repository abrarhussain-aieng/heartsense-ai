import re
import logging
from nemoguardrails import RailsConfig, LLMRails
from heartsense.config import settings
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

EXPLICIT_TERMS = [
    r"\bsex\b", r"\bsexual\b", r"\bdick\b", r"\bpussy\b", r"\bpenis\b", r"\bvagina\b",
    r"\bporn\b", r"\bnude\b"
]

# UPDATED: Aggressive filtering to catch exact phrases that bypassed NeMo
MEDICAL_OVERRIDES = [
    r"\bprescribe\b", r"\bdiagnose\b", r"\bdiagnosis\b", 
    r"risk factor", 
    r"do i have heart disease", 
    r"am i going to have", 
    r"medical advice", 
    r"understand my heart health",
    r"my doctor said"
]

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
  "Am I going to have a heart attack?"
  "My doctor said my blood pressure is 140/90. Is that bad?"

define bot refuse medical advice
  "I am a cardiovascular health assistant and cannot provide diagnoses, prescribe medication, or offer personalized medical advice. Please consult a licensed clinician."

define flow refuse medical advice
  user ask for medical advice
  bot refuse medical advice
"""

_config = None
_rails = None

def _get_nemo_llm():
    if settings.groq_api_key:
        return ChatGroq(model=settings.groq_model, groq_api_key=settings.groq_api_key, temperature=0.0)
    elif settings.gemini_api_key:
        return ChatGoogleGenerativeAI(model=settings.gemini_model, google_api_key=settings.gemini_api_key, temperature=0.0)
    raise ValueError("No valid LLM API key found")

def build_rails() -> LLMRails:
    global _config, _rails
    if _rails is None:
        _config = RailsConfig.from_content(RAILS_CONFIG)
        _rails = LLMRails(_config, llm=_get_nemo_llm())
    return _rails

async def check_input(text: str) -> dict:
    text_lower = text.lower()
    
    # 1. Block Explicit Content
    for pattern in EXPLICIT_TERMS:
        if re.search(pattern, text_lower):
            return {"allowed": False, "message": "I am a cardiovascular health assistant and cannot answer questions about sexual health or explicit topics."}
            
    # 2. Block Medical Advice (Regex Pre-filter)
    for pattern in MEDICAL_OVERRIDES:
        if re.search(pattern, text_lower):
            return {"allowed": False, "message": "I am a cardiovascular health assistant and cannot provide diagnoses, prescribe medication, or offer personalized medical advice. Please consult a licensed clinician."}

    # 3. NeMo Fallback
    try:
        rails = build_rails()
        result = await rails.generate_async(messages=[{"role": "user", "content": text}])
        content = result.get("content", "") if isinstance(result, dict) else str(result)
        content = content.strip()
        
        if "cannot provide diagnoses" in content.lower():
            return {"allowed": False, "message": content}
        return {"allowed": True, "message": ""}
    except Exception as e:
        logger.error(f"NeMo Guardrail Error: {e}")
        return {"allowed": True, "message": ""}