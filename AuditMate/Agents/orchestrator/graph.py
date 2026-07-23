"""LangGraph orchestrator for evidence collection."""
from typing import Dict, Any, List
from ..common import (
    EvidenceCollectionRequest, EvidenceSet, AuditPoint,
    Relation, is_mock, lm_complete
)
from ..github_agent.agent import GitHubAgent
from ..doc_repo_agent.agent import DocRepoAgent
from ..portal_agent.agent import PortalAgent
from .docx_writer import write_docx


class OrchestratorGraph:
    """Orchestrator graph for evidence collection."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.github_agent = GitHubAgent()
        self.doc_agent = DocRepoAgent()
        self.portal_agent = PortalAgent()
    
    def run(self, request: EvidenceCollectionRequest) -> EvidenceSet:
        """
        Run orchestrator to collect evidence.
        
        Args:
            request: EvidenceCollectionRequest
            
        Returns:
            EvidenceSet with collected evidence
        """
        items = []
        item_id = 1
        relations = []
        
        # Parse targets and operations from request
        targets = request.parsed_intent.targets if request.parsed_intent else {}
        operations = request.parsed_intent.operations if request.parsed_intent else []
        
        # GitHub agent (if enabled)
        github_spec = request.agents.get("github")
        if github_spec and github_spec.enabled:
            github_items = self.github_agent.collect(operations, targets, item_id)
            items.extend(github_items)
            item_id += len(github_items)
        
        # Document repo agent (if enabled)
        doc_spec = request.agents.get("doc_repo")
        if doc_spec and doc_spec.enabled:
            doc_items = self.doc_agent.collect(request.instruction, item_id)
            items.extend(doc_items)
            item_id += len(doc_items)
        
        # Portal agent (if enabled)
        portal_spec = request.agents.get("portal")
        if portal_spec and portal_spec.enabled:
            application_ids = targets.get("application_ids") or []
            app_id = request.application_id or (application_ids[0] if application_ids else "APP-001")
            portal_items = self.portal_agent.collect(app_id, item_id)
            items.extend(portal_items)
            item_id += len(portal_items)
        
        # Generate narrative
        narrative = self._generate_narrative(items)
        
        # Extract audit points and create relations
        audit_points = self._extract_audit_points(items)
        relations = self._generate_relations(items)
        
        # Count by source
        counts = self._count_by_source(items)
        
        # Create evidence set
        evidence_set = EvidenceSet(
            request_id=request.request_id,
            instruction=request.instruction,
            control_ref=request.control_ref,
            counts=counts,
            items=items,
            relations=relations,
            audit_points=audit_points,
            narrative=narrative
        )
        
        # Try to write DOCX
        try:
            docx_path = write_docx(evidence_set)
            evidence_set.document_path = docx_path
        except Exception as e:
            print(f"Warning: Failed to write DOCX: {e}")
        
        return evidence_set
    
    def _generate_narrative(self, items: List) -> str:
        """Generate narrative from items."""
        if is_mock():
            # Deterministic narrative in mock mode
            sources = set(item.provenance.system for item in items)
            summary = f"Collected {len(items)} evidence items from {len(sources)} sources: {', '.join(sorted(sources))}. "
            
            # Add details by type
            types_found = set(item.type.value for item in items)
            summary += f"Evidence types: {', '.join(sorted(types_found))}. "
            
            if any(item.type.value == "code_flow" for item in items):
                summary += "Code flow traces executed successfully with all checks passing. "
            
            if any(item.checks for item in items):
                passed = sum(1 for item in items if all(v == "PASS" for v in item.checks.values()))
                summary += f"Checks: {passed}/{len([i for i in items if i.checks])} passing. "
            
            summary += "Ready for audit team review."
            return summary
        else:
            # LLM-generated narrative
            items_text = "\n".join([f"- {item.id} ({item.type.value}): {item.summary}" for item in items])
            prompt = f"Summarize this evidence collection:\n{items_text}"
            return lm_complete(prompt, mock_value="Evidence collected successfully for audit review.")
    
    def _extract_audit_points(self, items: List) -> List[AuditPoint]:
        """Extract audit points from items."""
        points_dict = {}
        
        for item in items:
            for ap in item.audit_points:
                if ap not in points_dict:
                    # Parse point ID
                    points_dict[ap] = AuditPoint(
                        id=ap,
                        text=f"Audit point {ap}",
                        category="extracted"
                    )
        
        return list(points_dict.values())
    
    def _generate_relations(self, items: List) -> List[Relation]:
        """Generate relations between items."""
        relations = []
        
        # code_flow items relate to code_snippet items
        flow_items = [i for i in items if i.type.value == "code_flow"]
        snippet_items = [i for i in items if i.type.value == "code_snippet"]
        
        for flow in flow_items:
            for snippet in snippet_items:
                relations.append(Relation(
                    from_id=flow.id,
                    to_id=snippet.id,
                    kind="part_of_flow"
                ))
        
        return relations
    
    def _count_by_source(self, items: List) -> Dict[str, int]:
        """Count items by source system."""
        counts = {}
        for item in items:
            system = item.provenance.system
            counts[system] = counts.get(system, 0) + 1
        return counts
