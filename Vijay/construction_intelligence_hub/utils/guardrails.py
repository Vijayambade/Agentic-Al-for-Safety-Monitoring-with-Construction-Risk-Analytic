"""
Guardrail logic to restrict LLM queries to construction-related topics.
Uses Ollama to perform light classifier checks.
"""

from utils.ollama_client import generate

def check_construction_guardrail(query: str, model: str) -> tuple[bool, str]:
    """
    Checks if a user query is related to construction.
    
    Args:
        query: The user query string.
        model: The model to use for classification.
        
    Returns:
        A tuple of (is_allowed: bool, refusal_message: str).
    """
    # System prompt to classify the user query
    system_prompt = (
        "You are a strict guardrail classifier for a construction dashboard assistant.\n"
        "Your task is to classify whether the user's input query is related to construction, building, architecture, engineering, scheduling, materials, project management, estimation, safety, or related construction activities.\n"
        "You should also ALLOW standard short greetings (like 'hi', 'hello', 'hey', 'good morning', 'good afternoon') or queries asking who you are or what you can do.\n"
        "Reply with exactly 'ALLOW' if the query is construction-related or a standard greeting/general query about your capabilities.\n"
        "Reply with exactly 'BLOCK' if the query is completely unrelated to construction (such as general knowledge, coding, writing poems, science, history, geography, mathematics, or random off-topic questions).\n"
        "Do not explain. Just output ALLOW or BLOCK."
    )
    
    # We query Ollama using low temperature for deterministic results
    response = generate(
        prompt=f"User Query: {query}",
        model=model,
        system=system_prompt,
        temperature=0.0
    )
    
    cleaned_response = response.strip().upper()
    
    # If there is a connection/reachability issue, we don't want to block the user
    # because of the guardrail itself; the main helper will handle showing the reachability warning.
    if "⚠️" in cleaned_response or "COULD NOT REACH OLLAMA" in cleaned_response:
        return True, ""
        
    if "BLOCK" in cleaned_response:
        return False, (
            "⚠️ **Guardrail Warning:** I'm sorry, but I can only answer construction-related queries. "
            "Please ask a question related to civil engineering, project management, cost estimation, materials, safety, scheduling, or other construction topics."
        )
        
    return True, ""
