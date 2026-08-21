from unittest.mock import patch
from utils.guardrails import check_construction_guardrail


@patch("utils.guardrails.generate")
def test_construction_query_allowed(mock_generate):
    # Mock Ollama outputting ALLOW
    mock_generate.return_value = "ALLOW"
    
    allowed, message = check_construction_guardrail("What is the cost of concrete?", model="llama3.1")
    
    assert allowed is True
    assert message == ""
    mock_generate.assert_called_once()


@patch("utils.guardrails.generate")
def test_off_topic_query_blocked(mock_generate):
    # Mock Ollama outputting BLOCK
    mock_generate.return_value = "BLOCK"
    
    allowed, message = check_construction_guardrail("Write a python function to sort a list", model="llama3.1")
    
    assert allowed is False
    assert "Guardrail Warning" in message
    mock_generate.assert_called_once()


@patch("utils.guardrails.generate")
def test_greeting_query_allowed(mock_generate):
    # Mock Ollama outputting ALLOW for greetings
    mock_generate.return_value = "ALLOW"
    
    allowed, message = check_construction_guardrail("hello there", model="llama3.1")
    
    assert allowed is True
    assert message == ""


@patch("utils.guardrails.generate")
def test_ollama_offline_failsafe(mock_generate):
    # Mock Ollama offline error response
    mock_generate.return_value = "⚠️ Could not reach Ollama (Connection error)"
    
    allowed, message = check_construction_guardrail("Concrete estimation", model="llama3.1")
    
    # We should allow the query to pass through so the main client can display the connection error
    assert allowed is True
    assert message == ""
