import os
# -------------------------------------------------------
# LLM Configuration
# -------------------------------------------------------

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5-coder:1.5b"
)