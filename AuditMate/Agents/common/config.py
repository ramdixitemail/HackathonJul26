"""Configuration module for AuditMate."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Calculate ROOT as the AuditMate directory
ROOT = Path(__file__).parent.parent.parent
TEST_DIR = ROOT / "Test"
DATA_DIR = ROOT / "data"
EVIDENCE_DIR = ROOT / "Evidence"
EVIDENCE_STORE = EVIDENCE_DIR / "_store"
PORTAL_TEST_DIR = TEST_DIR / "portal_screenshots"

# LLM Configuration
MODE = os.getenv("AUDITMATE_MODE", "mock")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
VERTEX_MODEL = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
GCP_PROJECT = os.getenv("GCP_PROJECT", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "europe-west1")

# Graph Configuration
GRAPH_BACKEND = os.getenv("GRAPH_BACKEND", "json")
GRAPH_JSON = os.getenv("GRAPH_JSON", str(DATA_DIR / "graph.json"))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# GitHub Configuration
GITHUB_SOURCE = os.getenv("GITHUB_SOURCE", "fixtures")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "acme/payments-service")
GITHUB_API = os.getenv("GITHUB_API", "https://api.github.com")
SAMPLE_DIR = TEST_DIR / "github_repo_sample"

# Document Configuration
DOC_PROVIDER = os.getenv("DOC_PROVIDER", "folder")
DOC_FOLDER = os.getenv("DOC_FOLDER", str(TEST_DIR / "documents"))


def summary():
    """Print configuration summary."""
    return f"""
AuditMate Configuration Summary
==============================
Mode: {MODE}
Root: {ROOT}
Graph Backend: {GRAPH_BACKEND}
GitHub Source: {GITHUB_SOURCE}
Doc Provider: {DOC_PROVIDER}
"""


def ensure_dirs():
    """Ensure all required directories exist."""
    for dir_path in [EVIDENCE_DIR, EVIDENCE_STORE, PORTAL_TEST_DIR, DATA_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Ensured directories: {EVIDENCE_DIR}, {EVIDENCE_STORE}, {PORTAL_TEST_DIR}")


if __name__ == "__main__":
    print(summary())
    ensure_dirs()
