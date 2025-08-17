
import json
import os
import re
from datetime import datetime
from typing import Any, Dict
import pytz

import streamlit as st
import google.generativeai as genai

# Configuration
SYSTEM_MESSAGE = "Think privately but never reveal reasoning. Output only JSON or final formatted text."
DEFAULT_AUDIENCE = "People in Riyadh, Saudi Arabia"

# KSA Cultural Calendar
CULTURAL_EVENTS = {
    1: ["New Year period", "Winter shopping season"],
    2: ["Valentine's season", "Winter activities"],
    3: ["Spring season begins", "Outdoor activities increase"],
    4: ["Spring weather", "Ramadan season (varies yearly)"],
    5: ["End of school year approaching", "Eid preparations (varies)"],
    6: ["Summer vacation begins", "Travel season"],
    7: ["Peak summer", "Indoor activities focus"],
    8: ["Back-to-school preparations", "Summer sales"],
    9: ["School year begins", "Autumn preparations"],
    10: ["Mild weather returns", "Outdoor events resume"],
    11: ["Pleasant weather", "National Day season (Sept 23rd nearby)"],
    12: ["Winter season", "Year-end shopping", "Holiday preparations"],
}


def get_current_context() -> Dict[str, Any]:
    """Get current date, season, and cultural context for KSA market."""
    # Use KSA timezone (UTC+3)
    ksa_tz = pytz.timezone('Asia/Riyadh')
    now = datetime.now(ksa_tz)
    
    # Basic date info
    current_month = now.strftime("%B")
    current_year = now.year
    current_day = now.day
    
    # Season detection (Northern Hemisphere - KSA)
    month = now.month
    if month in [12, 1, 2]:
        season = "Winter"
    elif month in [3, 4, 5]:
        season = "Spring"
    elif month in [6, 7, 8]:
        season = "Summer"
    else:
        season = "Autumn"
    
    # Cultural events
    cultural_events = CULTURAL_EVENTS.get(month, [])
    
    # Weekend context (KSA weekend is Friday-Saturday)
    weekday = now.strftime("%A")
    is_weekend = weekday in ["Friday", "Saturday"]
    
    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "current_month": current_month,
        "current_year": current_year,
        "season": season,
        "cultural_events": cultural_events,
        "weekday": weekday,
        "is_weekend": is_weekend,
        "context_note": f"Current date: {current_month} {current_day}, {current_year} ({season} season in KSA)"
    }


def get_api_key() -> str:
    """Fetch Gemini API key from Streamlit Secrets or environment variables."""
    key = None
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    if not key:
        try:
            key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            pass
    if not key:
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return key or ""


def init_genai(api_key: str) -> None:
    """Initialize the Google Generative AI client."""
    genai.configure(api_key=api_key)


def create_model(model_name: str = "gemini-1.5-flash"):
    """Create a GenerativeModel with the required system instruction."""
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_MESSAGE,
    )


def parse_json_str(text: str) -> Dict[str, Any]:
    """Robustly parse a JSON string returned by the model."""
    text = text.strip()
    # Fast path
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try fenced blocks ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Try extracting the first {...} block
    obj_match = re.search(r"\{[\s\S]*\}", text)
    if obj_match:
        candidate = obj_match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("Model did not return valid JSON.")


def call_gemini_json(model, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
    """Call Gemini with JSON-only response enforced and return parsed dict."""
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "response_mime_type": "application/json",
        },
    )
    text = getattr(response, "text", None) or ""
    return parse_json_str(text)
