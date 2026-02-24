"""
Recommendation service: external APIs (ZenQuotes, AdviceSlip) + DB-backed emotion mappings.
Admin-editable mappings in Recommendation table override default suggestion text.
"""
import requests
from typing import Dict, Any, Optional

# Default suggestion text when no DB mapping exists
DEFAULT_MAPPING = {
    "happy": "Keep your momentum going.",
    "sad": "Try slow breathing exercises.",
    "angry": "Ground yourself for 30 seconds.",
    "neutral": "Focus on one task at a time.",
    "focused": "Deep work session recommended.",
    "calm": "Maintain with short breaks.",
}


def get_quote() -> Dict[str, str]:
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = r.json()
        if data and isinstance(data, list) and len(data) > 0:
            item = data[0]
            return {"quote": item.get("q", ""), "author": item.get("a", "Unknown")}
    except Exception:
        pass
    return {"quote": "Progress begins with a single step.", "author": "NeuroHarmonics"}


def get_advice() -> str:
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        data = r.json()
        slip = data.get("slip") or {}
        return slip.get("advice", "Take a moment to breathe.")
    except Exception:
        pass
    return "Take a moment to breathe."


def get_suggestion_for_emotion(emotion: str, db_session=None) -> str:
    """Return suggestion text for emotion: from DB if available, else default mapping."""
    if db_session:
        try:
            from models import Recommendation
            rec = db_session.query(Recommendation).filter_by(emotion=(emotion or "").strip().lower()).first()
            if rec and rec.content:
                return rec.content.strip()
        except Exception:
            pass
    return DEFAULT_MAPPING.get((emotion or "").strip().lower(), "Stay mindful.")


def generate_recommendation(emotion: str, db_session=None) -> Dict[str, Any]:
    """Legacy: recommendation + quote + advice."""
    suggestion = get_suggestion_for_emotion(emotion, db_session)
    return {
        "recommendation": suggestion,
        "quote": get_quote().get("quote", ""),
        "advice": get_advice(),
    }


def get_recommendations(dominant_emotion: str, db_session=None) -> Dict[str, Any]:
    """Return structure for GET /api/recommendations: motivational_quote, harmonic_suggestion, calming_tip."""
    quote_data = get_quote()
    advice = get_advice()
    suggestion = get_suggestion_for_emotion(dominant_emotion, db_session)
    return {
        "motivational_quote": quote_data,
        "harmonic_suggestion": (dominant_emotion or "neutral").lower(),
        "calming_tip": suggestion + " " + advice if suggestion else advice,
    }