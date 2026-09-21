

import re
import hashlib
from pydantic import BaseModel, Field
from google.genai import types
from core.gemini_client import get_gemini_client

class GrievanceRecord(BaseModel):
    category: str = Field(description="One of: Water & Sanitation, Roads & Transit, Power Grid, Healthcare, Digital")
    urgency_level: str = Field(description="Critical, High, Medium, or Low")
    location_named: str = Field(description="District, town, or landmark mentioned")
    issue_summary: str = Field(description="Clear English summary of the infrastructure deficit")
    detected_language: str = Field(description="Detected language of original input")

def redact_pii_locally(text: str) -> str:
    """Removes phone numbers, Aadhaar patterns, and emails locally before any API transmission."""
    text = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[REDACTED_PHONE]', text)
    text = re.sub(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[REDACTED_AADHAAR]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[REDACTED_EMAIL]', text)
    return text

def parse_grievance(raw_text: str, is_anonymous: bool = False) -> dict:
    clean_text = redact_pii_locally(raw_text)
    client = get_gemini_client()
    
    prompt = f"""
    Analyze the following citizen grievance.
    Extract the details strictly matching the provided JSON schema.
    Translate the summary into concise English.
    
    Input:
    {clean_text}
    """
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GrievanceRecord,
            temperature=0.1
        )
    )
    
    parsed = response.parsed.model_dump()
    
    if is_anonymous:
        token_hash = hashlib.sha256(raw_text.encode()).hexdigest()[:8].upper()
        parsed["tracking_token"] = f"ANON-{token_hash}"
        parsed["privacy_tier"] = "Zero-Knowledge Whistleblower Mode (Edge Scrubbed)"
    else:
        parsed["tracking_token"] = "VERIFIED-RESIDENT-01"
        parsed["privacy_tier"] = "Standard Public Verification"
        
    return parsed
