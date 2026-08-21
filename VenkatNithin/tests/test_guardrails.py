"""
tests/test_guardrails.py
-------------------------
Unit tests for Ollama Construction Domain Guardrails.
Verifies that construction domain queries are allowed, and off-topic queries are refused
with the exact required standard message.
"""
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.middleware.guardrails import (
    OllamaGuardrail,
    validate_construction_domain,
    STANDARD_REFUSAL_MESSAGE,
)
from backend.services.ai_service import call_construction_llm


def test_allowed_construction_queries():
    """Verify that construction-related queries pass domain guardrail validation."""
    construction_prompts = [
        "What is the recommended concrete mix ratio for M25 grade?",
        "How do I calculate steel reinforcement for a concrete slab?",
        "What are standard OSHA safety requirements for scaffolding?",
        "Explain the process of site waste management.",
        "How does material estimation work in this hub?",
        "What is the difference between RCC and Steel Structure?",
        "How do I inspect foundation settlement risks?",
        "What is decibel monitoring on site?",
    ]

    for prompt in construction_prompts:
        is_valid, msg = validate_construction_domain(prompt)
        assert is_valid is True, f"Failed allowed prompt: '{prompt}'"
        assert msg == ""


def test_restricted_off_domain_queries():
    """Verify that off-topic queries are rejected with the standard refusal message."""
    restricted_prompts = [
        "Who won the cricket match yesterday?",
        "What are the best movies of 2025?",
        "Who is running in the presidential election?",
        "Write a Python tutorial for binary search tree.",
        "Give me medical advice for a headache.",
        "What is the current price of Bitcoin cryptocurrency?",
        "Tell me a joke about animals.",
    ]

    for prompt in restricted_prompts:
        is_valid, msg = validate_construction_domain(prompt)
        assert is_valid is False, f"Failed to catch off-domain prompt: '{prompt}'"
        assert msg == STANDARD_REFUSAL_MESSAGE


def test_call_construction_llm_guardrail_integration():
    """Verify that call_construction_llm returns the standard refusal message for restricted prompts."""
    prompt = "Which team won the IPL cricket finals?"
    response = call_construction_llm(prompt)
    assert response == STANDARD_REFUSAL_MESSAGE

    # Allowed prompt returns actual response
    allowed_prompt = "What is M25 grade concrete?"
    allowed_response = call_construction_llm(allowed_prompt)
    assert allowed_response != STANDARD_REFUSAL_MESSAGE
    assert "concrete" in allowed_response.lower() or "mix" in allowed_response.lower()
