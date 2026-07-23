"""
Pluggable LLM client.

Priority order (first available wins):
  1. Groq free-tier API      — set GROQ_API_KEY (https://console.groq.com, free)
  2. Local Ollama             — set OLLAMA_HOST (e.g. http://localhost:11434), OLLAMA_MODEL
  3. Offline rule-based engine — always available, zero setup, no network needed

Every provider is used through the same call_llm(prompt, system) -> str
interface, so the rest of the app never needs to know which one is active.
"""
import os
import json
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")


def active_provider():
    if GROQ_API_KEY:
        return "groq"
    if OLLAMA_HOST:
        return "ollama"
    return "offline-rules"


def _call_groq(system, prompt):
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_ollama(system, prompt):
    resp = requests.post(
        f"{OLLAMA_HOST.rstrip('/')}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def call_llm(prompt, system="You are a helpful assistant."):
    """Returns raw text from whichever provider is configured. Raises on failure
    so callers can fall back to the offline rule engine."""
    provider = active_provider()
    if provider == "groq":
        return _call_groq(system, prompt)
    if provider == "ollama":
        return _call_ollama(system, prompt)
    raise RuntimeError("no LLM provider configured")


def call_llm_json(prompt, system):
    """Calls the LLM and parses a JSON object/array from the response,
    tolerating ```json fences. Raises on any failure."""
    text = call_llm(prompt, system)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())
