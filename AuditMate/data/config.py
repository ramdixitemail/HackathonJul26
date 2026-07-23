"""Configuration for data module."""
import sys
from pathlib import Path

# Add parent to path for imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

GRAPH_BACKEND = "json"  # or "neo4j"
GRAPH_JSON = str(ROOT / "data" / "graph.json")
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
