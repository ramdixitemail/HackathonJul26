"""LLM model provider for AuditMate."""
from .config import MODE


def is_mock():
    """Check if running in mock mode."""
    return MODE == "mock"


def chat_model():
    """Get chat model based on configuration."""
    if MODE == "mock":
        raise RuntimeError("Mock mode: use lm_complete with mock_value instead")
    elif MODE == "ollama":
        try:
            from langchain_ollama import ChatOllama
            from .config import OLLAMA_MODEL, OLLAMA_BASE_URL
            return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        except ImportError:
            raise ImportError("langchain_ollama not installed. Install: pip install langchain-ollama")
    elif MODE == "vertex":
        try:
            from langchain_google_vertexai import ChatVertexAI
            from .config import VERTEX_MODEL, GCP_PROJECT, GCP_LOCATION
            return ChatVertexAI(
                model=VERTEX_MODEL,
                project=GCP_PROJECT,
                location=GCP_LOCATION
            )
        except ImportError:
            raise ImportError("langchain_google_vertexai not installed. Install: pip install langchain-google-vertexai")
    else:
        raise ValueError(f"Unknown mode: {MODE}")


def lm_complete(prompt: str, system: str = None, mock_value: str = None) -> str:
    """
    Complete a prompt using LLM.
    
    Args:
        prompt: User prompt
        system: System prompt
        mock_value: Value to return in mock mode
        
    Returns:
        Completion string
    """
    if is_mock():
        if mock_value is None:
            raise ValueError("Mock mode requires mock_value parameter")
        return mock_value
    
    model = chat_model()
    if system:
        messages = [
            ("system", system),
            ("human", prompt)
        ]
    else:
        messages = [("human", prompt)]
    
    response = model.invoke(messages)
    return response.content
