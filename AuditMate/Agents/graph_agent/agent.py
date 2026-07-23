"""Graph agent for knowledge graph queries."""
import sys
from pathlib import Path
from typing import List, Dict, Any
from ..common import is_mock, lm_complete, KAnswer, KPIs

# Add parent to path for imports
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from data.graph_store import get_store


class GraphAgent:
    """Agent for querying knowledge graph."""
    
    def __init__(self):
        """Initialize graph agent."""
        self.store = get_store()
    
    def kpis(self) -> KPIs:
        """Get KPI metrics."""
        kpi_dict = self.store.kpis()
        return KPIs(**kpi_dict)
    
    def _parse_filters(self, question: str) -> Dict[str, Any]:
        """Parse question to extract filters."""
        question_lower = question.lower()
        filters = {}
        
        # Determine entity type
        if any(word in question_lower for word in ["sii", "item", "issue"]):
            filters["entity"] = "sii"
        elif any(word in question_lower for word in ["vulnerability", "cve", "vuln"]):
            filters["entity"] = "vulnerability"
        elif any(word in question_lower for word in ["audit", "audit_item"]):
            filters["entity"] = "audit_item"
        else:
            filters["entity"] = "sii"  # Default
        
        # Severity
        if any(word in question_lower for word in ["high", "critical"]):
            filters["severity"] = "high" if "high" in question_lower else "critical"
        elif "medium" in question_lower:
            filters["severity"] = "medium"
        elif "low" in question_lower:
            filters["severity"] = "low"
        
        # Status
        if "overdue" in question_lower or "past due" in question_lower:
            filters["overdue"] = True
        
        if any(word in question_lower for word in ["open", "active"]):
            filters["status"] = "open"
        
        # Application
        for i in range(1, 5):
            app_id = f"APP-{i:03d}"
            if app_id in question_lower:
                filters["application_id"] = app_id
                break
        
        return filters
    
    def answer(self, question: str, filters: Dict[str, Any] = None) -> KAnswer:
        """
        Answer knowledge graph query.
        
        Args:
            question: Query question
            filters: Optional filters
            
        Returns:
            KAnswer with narrative and table
        """
        if not filters:
            filters = self._parse_filters(question)
        
        # Query graph
        rows = self.store.query(filters)
        cypher = self.store.last_cypher
        
        # Generate narrative
        if is_mock():
            narrative = self._generate_narrative(question, rows)
        else:
            rows_text = "\n".join([str(row) for row in rows])
            prompt = f"Summarize this knowledge graph query result:\nQuestion: {question}\nResults:\n{rows_text}"
            narrative = lm_complete(prompt, mock_value=self._generate_narrative(question, rows))
        
        # Build cited paths (simplified for mock)
        cited_paths = [
            "Application-HAS-SII",
            "SII-REMEDIATED_BY-RemediationPlan"
        ]
        
        return KAnswer(
            narrative=narrative,
            table=rows,
            cited_paths=cited_paths,
            cypher=cypher
        )
    
    def _generate_narrative(self, question: str, rows: List[Dict[str, Any]]) -> str:
        """Generate deterministic narrative."""
        if not rows:
            return "No matching records found in the knowledge graph."
        
        # Count by severity or status
        narrative_parts = []
        
        if len(rows) == 1:
            row = rows[0]
            narrative_parts.append(f"Found 1 match: {row.get('id', 'N/A')} - {row.get('title', 'N/A')} on {row.get('application', 'N/A')} (Severity: {row.get('severity', 'N/A')}, Status: {row.get('status', 'N/A')}).")
        else:
            severity_counts = {}
            app_counts = {}
            for row in rows:
                sev = row.get('severity', 'unknown')
                app = row.get('application', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                app_counts[app] = app_counts.get(app, 0) + 1
            
            narrative_parts.append(f"Found {len(rows)} records:")
            for sev in ['critical', 'high', 'medium', 'low']:
                if sev in severity_counts:
                    narrative_parts.append(f"  - {severity_counts[sev]} {sev}-severity")
            
            narrative_parts.append(f"Across {len(app_counts)} applications.")
        
        # Add owner info if available
        owners = set(row.get('owner') for row in rows if row.get('owner'))
        if owners:
            narrative_parts.append(f"Owners: {', '.join(sorted(owners))}")
        
        return " ".join(narrative_parts)


if __name__ == "__main__":
    agent = GraphAgent()
    
    print("KPIs:")
    kpis = agent.kpis()
    print(f"  Open vulnerabilities: {kpis.open_vulnerabilities}")
    print(f"  High SIIs: {kpis.high_severity_siis}")
    print(f"  Remediations on track: {kpis.remediations_on_track_pct}%")
    
    print("\nQuery: High-severity SIIs past due")
    answer = agent.answer("Show me high-severity SIIs that are overdue")
    print(f"Answer: {answer.narrative}")
    for row in answer.table:
        print(f"  {row}")
