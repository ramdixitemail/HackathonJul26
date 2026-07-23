"""CLI entry point for orchestrator."""
import argparse
import sys
from pathlib import Path

# Add parent to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from Agents.common import (
    EvidenceCollectionRequest, AgentSpec, save_evidence_set, MODE
)
from Agents.common.intent_parser import parse_instruction
from Agents.orchestrator.graph import OrchestratorGraph


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AuditMate Orchestrator")
    parser.add_argument("instruction", help="Audit instruction text")
    parser.add_argument("--request-id", default="REQ-CLI-0001", help="Request ID")
    parser.add_argument("--repo", default="acme/payments-service", help="Repository")
    parser.add_argument("--app", default="APP-001", help="Application ID")
    parser.add_argument("--control", help="Control reference")
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"AuditMate Orchestrator - Mode: {MODE}")
    print(f"{'='*60}")
    print(f"Instruction: {args.instruction}")
    print(f"Request ID: {args.request_id}")
    print(f"Application: {args.app}")
    
    # Parse instruction
    parsed_intent = parse_instruction(args.instruction)
    print(f"\nParsed Intent:")
    print(f"  Operations: {', '.join(parsed_intent.operations)}")
    print(f"  Change IDs: {', '.join(parsed_intent.targets.get('change_ids', []))}")
    print(f"  JIRA IDs: {', '.join(parsed_intent.targets.get('jira_ids', []))}")
    
    # Build collection request
    request = EvidenceCollectionRequest(
        request_id=args.request_id,
        instruction=args.instruction,
        control_ref=args.control,
        evidence_goals=[],
        agents={
            "github": AgentSpec(enabled=True),
            "doc_repo": AgentSpec(enabled=True),
            "portal": AgentSpec(enabled=True)
        },
        application_id=args.app,
        parsed_intent=parsed_intent
    )
    
    print(f"\nAgents Enabled:")
    for agent_name, spec in request.agents.items():
        print(f"  {agent_name}: {'✓' if spec.enabled else '✗'}")
    
    # Run orchestrator
    print(f"\n{'='*60}")
    print("Running orchestrator...")
    print(f"{'='*60}")
    
    orchestrator = OrchestratorGraph()
    evidence_set = orchestrator.run(request)
    
    # Print results
    print(f"\nEvidence Collection Complete!")
    print(f"{'='*60}")
    print(f"Total Items: {len(evidence_set.items)}")
    print(f"Items by Source:")
    for source, count in evidence_set.counts.items():
        print(f"  {source}: {count}")
    
    print(f"\nEvidence Items:")
    for item in evidence_set.items:
        print(f"  {item.id}: {item.type.value} - {item.summary}")
        if item.checks:
            for check, result in item.checks.items():
                status = "✓" if result == "PASS" else "✗"
                print(f"    {status} {check}: {result}")
    
    if evidence_set.relations:
        print(f"\nRelations:")
        for rel in evidence_set.relations:
            print(f"  {rel.from_id} --[{rel.kind}]--> {rel.to_id}")
    
    if evidence_set.narrative:
        print(f"\nNarrative:")
        print(f"  {evidence_set.narrative}")
    
    # Save to store
    storage_path = save_evidence_set(evidence_set)
    print(f"\nEvidence stored: {storage_path}")
    
    if evidence_set.document_path:
        print(f"Document generated: {evidence_set.document_path}")
    
    print(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
