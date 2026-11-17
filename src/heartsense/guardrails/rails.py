import re
import logging
from heartsense.config import settings

logger = logging.getLogger(__name__)

EXPLICIT_TERMS = [
    r"\bsex\b", r"\bsexual\b", r"\bdick\b", r"\bpussy\b", r"\bpenis\b", r"\bvagina\b",
    r"\bporn\b", r"\bnude\b"
]

MEDICAL_OVERRIDES = [
    r"\bprescribe\b", r"\bdiagnose\b", r"\bdiagnosis\b", 
    r"risk factor", 
    r"do i have heart disease", 
    r"am i going to have", 
    r"medical advice", 
    r"understand my heart health",
    r"my doctor said"
]

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

    # 3. Allow the request to pass through to LangGraph
    # REMOVED the NeMo generate_async call because it was generating full essays and wasting Groq tokens (causing 429 errors).
    return {"allowed": True, "message": ""}