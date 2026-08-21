"""
Thin wrapper around the local Ollama HTTP API.
Requires Ollama to be installed and running on the same machine
(https://ollama.com  ->  `ollama serve`, then `ollama pull <model>`).
"""

import requests

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1"


def check_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_models() -> list[str]:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except requests.exceptions.RequestException:
        return []


def generate(prompt: str, model: str = DEFAULT_MODEL, system: str | None = None,
             temperature: float = 0.3) -> str:
    """One-shot text generation (used for estimation summaries, doc analysis, etc.)"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    try:
        r = requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return (
            f"⚠️ Could not reach Ollama ({e}).\n\n"
            f"Make sure it's running: `ollama serve`, and that the model is pulled: "
            f"`ollama pull {model}`."
        )


def chat(messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 0.3) -> str:
    """Multi-turn chat, messages = [{'role': 'user'/'assistant'/'system', 'content': ...}]"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("message", {}).get("content", "").strip()
    except requests.exceptions.RequestException as e:
        return (
            f"⚠️ Could not reach Ollama ({e}).\n\n"
            f"Make sure it's running: `ollama serve`, and that the model is pulled: "
            f"`ollama pull {model}`."
        )
