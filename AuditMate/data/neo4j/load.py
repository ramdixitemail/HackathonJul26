"""Load graph.json data into Neo4j."""
import json
import sys
from pathlib import Path

def load_graph_to_neo4j(graph_json_path: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
    """Load graph.json into Neo4j."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("neo4j package not installed. Install with: pip install neo4j")
        return
    
    with open(graph_json_path, 'r') as f:
        graph_data = json.load(f)
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    with driver.session() as session:
        # Create applications
        for app in graph_data.get("applications", []):
            session.run("""
                MERGE (a:Application {application_id: $app_id})
                SET a.name = $name, a.tier = $tier, a.owner = $owner
            """, app_id=app["application_id"], name=app["name"], tier=app["tier"], owner=app["owner"])
        
        # Create SIIs
        for sii in graph_data.get("siis", []):
            session.run("""
                MERGE (s:SII {id: $id})
                SET s.title = $title, s.severity = $severity, s.status = $status, s.due_date = $due_date
                WITH s
                MATCH (a:Application {application_id: $app_id})
                MERGE (a)-[:HAS_SII]->(s)
            """, id=sii["id"], title=sii["title"], severity=sii["severity"], 
                status=sii["status"], due_date=sii["due_date"], app_id=sii["application_id"])
        
        print("Graph data loaded successfully")
    
    driver.close()


if __name__ == "__main__":
    graph_json = Path(__file__).parent.parent / "graph.json"
    load_graph_to_neo4j(
        str(graph_json),
        "bolt://localhost:7687",
        "neo4j",
        "password"
    )
