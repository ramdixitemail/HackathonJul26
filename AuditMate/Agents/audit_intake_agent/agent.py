"""Audit Intake Agent for processing audit requests."""
import json
import re
from pathlib import Path
from typing import Optional, List
from ..common import (
    AuditIntake, AuditPoint, EvidenceGoal, EvidenceCollectionRequest,
    AgentSpec, ParsedIntent, TEST_DIR
)
from ..common.intent_parser import parse_instruction


class AuditIntakeAgent:
    """Agent for processing audit intake."""
    
    def __init__(self):
        """Initialize audit intake agent."""
        self.audit_samples_dir = TEST_DIR / "audit_samples"
    
    def intake(self, request: AuditIntake) -> dict:
        """
        Process audit intake request.
        
        Args:
            request: AuditIntake request
            
        Returns:
            Dictionary with audit_points and draft EvidenceCollectionRequest
        """
        audit_text = request.audit_text
        audit_id = request.audit_id or "ADHOC"
        
        # Load from file if only ID provided
        if not audit_text and request.audit_id:
            sample_file = self.audit_samples_dir / f"{request.audit_id}.json"
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    sample_data = json.load(f)
                audit_text = sample_data.get("audit_text", "")
                audit_id = sample_data.get("audit_id", request.audit_id)
        
        if not audit_text:
            audit_text = ""
        
        # Extract audit points
        audit_points = self._extract_points(audit_text)
        
        # Determine evidence goals
        goals = self._goals_for(audit_text)
        
        # Parse instruction
        parsed_intent = parse_instruction(audit_text)
        
        # Determine enabled agents
        agents = {
            "github": AgentSpec(enabled="code" in audit_text.lower() or bool(parsed_intent.targets.get("change_ids"))),
            "doc_repo": AgentSpec(enabled="document" in audit_text.lower() or "design" in audit_text.lower()),
            "portal": AgentSpec(enabled="screenshot" in audit_text.lower() or "portal" in audit_text.lower())
        }
        
        # Build collection instruction
        instruction = f"Collect evidence for the audit: {'. '.join([p.text for p in audit_points])}"
        
        # Build request ID
        request_id = f"REQ-{audit_id}"
        
        # Create draft collection request
        draft_request = EvidenceCollectionRequest(
            request_id=request_id,
            instruction=instruction,
            evidence_goals=goals,
            agents=agents,
            parsed_intent=parsed_intent
        )
        
        return {
            "audit_points": audit_points,
            "draft_request": draft_request,
            "audit_id": audit_id
        }
    
    def _extract_points(self, text: str) -> List[AuditPoint]:
        """
        Extract audit points from text.
        
        Args:
            text: Audit text
            
        Returns:
            List of AuditPoint objects
        """
        points = []
        
        # Split on common delimiters
        segments = re.split(r'[,;?]\s+', text)
        
        point_id = 1
        for segment in segments:
            segment = segment.strip()
            if len(segment) >= 12:  # >= 12 chars
                points.append(AuditPoint(
                    id=f"AP-{point_id:03d}",
                    text=segment
                ))
                point_id += 1
        
        # If no points found, create one from whole text
        if not points and text.strip():
            points.append(AuditPoint(
                id="AP-001",
                text=text.strip()
            ))
        
        return points
    
    def _goals_for(self, text: str) -> List[EvidenceGoal]:
        """
        Determine evidence goals from audit text.
        
        Args:
            text: Audit text
            
        Returns:
            List of EvidenceGoal values
        """
        goals = []
        text_lower = text.lower()
        
        # Map keywords to goals
        if any(word in text_lower for word in ["segregation", "sod", "duty"]):
            goals.append(EvidenceGoal.SEGREGATED_DEPLOY_APPROVAL)
        
        if any(word in text_lower for word in ["test", "testing", "pass"]):
            goals.append(EvidenceGoal.TESTS_PASSED)
        
        if any(word in text_lower for word in ["approval", "approve", "who approved"]):
            goals.append(EvidenceGoal.TWO_INDEPENDENT_APPROVALS)
        
        if any(word in text_lower for word in ["dblink", "database link", "data"]):
            goals.append(EvidenceGoal.DATA_FROM_DBLINK_ONLY)
        
        if any(word in text_lower for word in ["deploy", "deployment", "production"]):
            goals.append(EvidenceGoal.LAST_PR_FOR_CHANGE)
        
        # Default if no matches
        if not goals:
            goals.append(EvidenceGoal.TRACEABILITY_CHAIN)
        
        return goals


if __name__ == "__main__":
    agent = AuditIntakeAgent()
    result = agent.intake(AuditIntake(audit_id="AUD-2026-0142"))
    print("Audit Points:")
    for point in result["audit_points"]:
        print(f"  {point.id}: {point.text}")
    print("\nEvidence Goals:")
    for goal in result["draft_request"].evidence_goals:
        print(f"  - {goal.value}")
