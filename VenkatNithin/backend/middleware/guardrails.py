"""
backend/middleware/guardrails.py
---------------------------------
Domain guardrail middleware and utility for Ollama AI Assistant.
Restricts LLM queries strictly to Construction Intelligent Hub topics and returns a standard refusal
response for out-of-domain queries.
"""
import re
import logging
from typing import Tuple, List, Set

logger = logging.getLogger(__name__)

STANDARD_REFUSAL_MESSAGE = (
    "I am the Construction Intelligent Hub AI Assistant. I can only answer questions related to "
    "construction, civil engineering, project management, site safety, materials, risk analysis, "
    "and the features available in this platform. Please ask a construction-related question."
)

# Allowed Construction Domain Topics & Key Words
ALLOWED_CONSTRUCTION_TOPICS: Set[str] = {
    # Core domain
    "construction", "civil", "engineering", "building", "builder", "structure", "structural",
    "architecture", "architectural", "foundation", "beam", "column", "slab", "truss",
    # Materials & Estimation
    "material", "materials", "cement", "sand", "steel", "rebar", "concrete", "brick", "bricks",
    "mortar", "aggregate", "paint", "tiles", "plumbing", "electrical", "boq", "quantity",
    "takeoff", "estimation", "estimate", "budget", "cost", "costing",
    # Safety & Risk
    "safety", "osha", "hazard", "ppe", "helmet", "vest", "harness", "scaffolding", "risk",
    "inspection", "violation", "incident", "emergency", "sop", "compliance",
    # Site Operations & Telematics
    "site", "equipment", "telematics", "excavator", "crane", "bulldozer", "fleet", "machinery",
    "schedule", "delay", "gantt", "milestone", "inventory", "stock", "waste", "recycling",
    "noise", "decibel", "air quality", "aqi", "water", "leakage", "energy", "weather",
    # Project & Regulations
    "contractor", "supervisor", "workforce", "hiring", "worker", "labor", "daily report",
    "building code", "regulation", "code", "blueprint", "drawing", "specification", "clause",
    "hub", "platform", "assistant", "system", "feature", "dashboard", "document", "analyzer"
}

# Explicitly Restricted Off-Domain Topics & Keywords
RESTRICTED_TOPICS: Set[str] = {
    # Sports & Entertainment
    "cricket", "football", "soccer", "basketball", "baseball", "tennis", "sports", "match",
    "ipl", "nfl", "nba", "fifa", "movie", "movies", "film", "cinema", "actor", "actress",
    "celebrity", "song", "music", "game", "gaming", "entertainment", "tv show", "netflix",
    # Politics & General News
    "politics", "election", "president", "prime minister", "government election", "political",
    "democrat", "republican", "parliament", "vote",
    # Unrelated Programming / General Tech
    "python tutorial", "javascript tutorial", "java tutorial", "c++ tutorial", "leetcode",
    "binary tree", "sorting algorithm", "react tutorial", "angular tutorial",
    # Medical & Legal Advice
    "medical advice", "doctor", "medicine", "symptom", "disease", "treatment", "hospital",
    "legal advice", "court case", "lawsuit", "attorney", "divorce",
    # Finance & Crypto
    "cryptocurrency", "bitcoin", "ethereum", "dogecoin", "crypto", "stock market", "trading",
    "forex", "investing in stocks",
    # General Trivia & Social
    "general knowledge", "trivia", "joke", "jokes", "dating", "relationship", "social media",
    "instagram", "tiktok", "facebook", "twitter", "recipe", "cooking", "astrology", "horoscope"
}

# Greetings and system queries allowed for general interaction
SYSTEM_GREETINGS: Set[str] = {
    "hi", "hello", "hey", "greetings", "help", "who are you", "what can you do", "info", "capabilities"
}


class OllamaGuardrail:
    """
    Reusable domain guardrail engine for Ollama and AI assistant integrations.
    """

    @classmethod
    def is_construction_related(cls, prompt: str) -> bool:
        """
        Evaluate if a user prompt is within the construction domain scope.
        """
        if not prompt or not prompt.strip():
            return True

        prompt_clean = prompt.strip().lower()
        words = set(re.findall(r"\b[a-z0-9\'-]+\b", prompt_clean))

        # Check for system greetings or short capability queries
        if prompt_clean in SYSTEM_GREETINGS or any(g in prompt_clean for g in ["what can you do", "who are you", "help me"]):
            return True

        # Check for explicit restricted topics first
        for restricted in RESTRICTED_TOPICS:
            if restricted in prompt_clean:
                logger.warning(f"Guardrail triggered: prompt contains restricted topic '{restricted}'")
                return False

        # Check for allowed construction topics
        for allowed in ALLOWED_CONSTRUCTION_TOPICS:
            if allowed in prompt_clean or any(w.startswith(allowed) for w in words):
                return True

        # If prompt has no construction keywords and is clearly off-topic question
        # Check phrase match or keyword presence
        logger.warning(f"Guardrail triggered: prompt '{prompt[:50]}...' does not match construction domain.")
        return False

    @classmethod
    def validate(cls, prompt: str) -> Tuple[bool, str]:
        """
        Validate prompt and return (is_valid, message).
        If is_valid is False, message will be the exact required refusal response.
        """
        is_valid = cls.is_construction_related(prompt)
        if not is_valid:
            return False, STANDARD_REFUSAL_MESSAGE
        return True, ""


def validate_construction_domain(prompt: str) -> Tuple[bool, str]:
    """Standalone utility wrapper for domain validation."""
    return OllamaGuardrail.validate(prompt)
