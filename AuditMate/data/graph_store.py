"""Graph store for knowledge graph backend."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .config import GRAPH_BACKEND, GRAPH_JSON


class JsonGraphStore:
    """JSON-based graph store."""
    
    def __init__(self, graph_path: str = GRAPH_JSON):
        """Initialize JSON store."""
        self.graph_path = Path(graph_path)
        self.graph_data = {}
        self.last_cypher = None
        self._load()
    
    def _load(self):
        """Load graph data from JSON file."""
        if self.graph_path.exists():
            with open(self.graph_path, 'r') as f:
                self.graph_data = json.load(f)
    
    def applications(self) -> List[Dict[str, Any]]:
        """Get all applications."""
        return self.graph_data.get("applications", [])
    
    def kpis(self) -> Dict[str, Any]:
        """Calculate KPIs from graph data."""
        vulnerabilities = self.graph_data.get("vulnerabilities", [])
        siis = self.graph_data.get("siis", [])
        audit_items = self.graph_data.get("audit_items", [])
        remediation_plans = self.graph_data.get("remediation_plans", [])
        
        # Open vulnerabilities
        open_vuln = sum(1 for v in vulnerabilities if v.get("status") in ["open", "in_remediation"])
        
        # Audit items due in 30 days
        today = datetime.now()
        thirty_days = today + timedelta(days=30)
        due_30d = sum(1 for a in audit_items 
                      if datetime.fromisoformat(a.get("due_date", "2099-01-01")) <= thirty_days)
        
        # High severity SIIs
        high_sii = sum(1 for s in siis if s.get("severity") == "high")
        
        # Remediations on track (in_progress)
        total_plans = len(remediation_plans)
        on_track = sum(1 for p in remediation_plans if p.get("status") == "in_progress")
        on_track_pct = (on_track / total_plans * 100) if total_plans > 0 else 0
        
        return {
            "open_vulnerabilities": open_vuln,
            "audit_items_due_30d": due_30d,
            "high_severity_siis": high_sii,
            "remediations_on_track_pct": round(on_track_pct, 1)
        }
    
    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query graph data with filters.
        
        Args:
            filters: Dict with entity, severity, status, application_id, overdue
            
        Returns:
            List of matching rows
        """
        entity_type = filters.get("entity", "sii")  # sii, vulnerability, audit_item
        severity = filters.get("severity")
        status = filters.get("status")
        application_id = filters.get("application_id")
        overdue = filters.get("overdue", False)
        
        if entity_type == "sii":
            source = self.graph_data.get("siis", [])
        elif entity_type == "vulnerability":
            source = self.graph_data.get("vulnerabilities", [])
        elif entity_type == "audit_item":
            source = self.graph_data.get("audit_items", [])
        else:
            source = []
        
        # Apply filters
        results = []
        apps_map = {app["application_id"]: app for app in self.graph_data.get("applications", [])}
        
        for item in source:
            if severity and item.get("severity") != severity:
                continue
            if status and item.get("status") != status:
                continue
            if application_id and item.get("application_id") != application_id:
                continue
            
            # Check if overdue
            if overdue:
                due_date = datetime.fromisoformat(item.get("due_date", "2099-01-01"))
                if due_date > datetime.now():
                    continue
            
            # Find remediation info
            remediation = None
            for plan in self.graph_data.get("remediation_plans", []):
                if plan.get("target_id") == item.get("id"):
                    remediation = plan
                    break
            
            app_id = item.get("application_id")
            app_info = apps_map.get(app_id, {})
            
            row = {
                "id": item.get("id"),
                "application": app_info.get("name", app_id),
                "title": item.get("title"),
                "severity": item.get("severity"),
                "status": item.get("status"),
                "due_date": item.get("due_date"),
                "remediation": remediation.get("id") if remediation else None,
                "eta": remediation.get("eta") if remediation else None,
                "owner": remediation.get("owner") if remediation else app_info.get("owner")
            }
            results.append(row)
        
        # Set Cypher equivalent
        self.last_cypher = f"MATCH (n:{entity_type}) WHERE n.severity = '{severity}' RETURN n"
        
        return results


class Neo4jGraphStore:
    """Neo4j-based graph store."""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j store."""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except ImportError:
            raise ImportError("neo4j not installed. Install: pip install neo4j")
        self.last_cypher = None
    
    def applications(self) -> List[Dict[str, Any]]:
        """Get all applications."""
        with self.driver.session() as session:
            result = session.run("MATCH (a:Application) RETURN a")
            return [dict(record["a"]) for record in result]
    
    def kpis(self) -> Dict[str, Any]:
        """Calculate KPIs from Neo4j."""
        with self.driver.session() as session:
            # Open vulnerabilities
            open_vuln_result = session.run(
                "MATCH (v:Vulnerability) WHERE v.status IN ['open', 'in_remediation'] RETURN count(v) as count"
            )
            open_vuln = open_vuln_result.single()["count"]
            
            # High SIIs
            high_sii_result = session.run(
                "MATCH (s:SII) WHERE s.severity = 'high' RETURN count(s) as count"
            )
            high_sii = high_sii_result.single()["count"]
            
            # Remediation on track
            on_track_result = session.run(
                "MATCH (p:RemediationPlan) WHERE p.status = 'in_progress' RETURN count(p) as count"
            )
            on_track = on_track_result.single()["count"]
            
            total_result = session.run("MATCH (p:RemediationPlan) RETURN count(p) as count")
            total = total_result.single()["count"]
            on_track_pct = (on_track / total * 100) if total > 0 else 0
            
            return {
                "open_vulnerabilities": open_vuln,
                "audit_items_due_30d": 2,  # Placeholder
                "high_severity_siis": high_sii,
                "remediations_on_track_pct": round(on_track_pct, 1)
            }
    
    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query Neo4j with filters."""
        entity_type = filters.get("entity", "SII")
        
        cypher = f"MATCH (n:{entity_type}) RETURN n"
        
        if filters.get("severity"):
            cypher += f" WHERE n.severity = '{filters['severity']}'"
        
        with self.driver.session() as session:
            result = session.run(cypher)
            rows = [dict(record["n"]) for record in result]
        
        self.last_cypher = cypher
        return rows


def get_store(backend: str = GRAPH_BACKEND):
    """Get graph store instance based on backend."""
    if backend == "json":
        return JsonGraphStore()
    elif backend == "neo4j":
        from ..common.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        return Neo4jGraphStore(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    else:
        raise ValueError(f"Unknown backend: {backend}")


if __name__ == "__main__":
    store = get_store()
    print("KPIs:")
    kpis = store.kpis()
    for key, value in kpis.items():
        print(f"  {key}: {value}")
    
    print("\nHigh-severity overdue SIIs:")
    results = store.query({
        "entity": "sii",
        "severity": "high",
        "overdue": True
    })
    for row in results:
        print(f"  {row['id']}: {row['title']} ({row['application']}) - Owner: {row['owner']}")
