"""GitHub Agent for collecting evidence from version control."""
import json
from pathlib import Path
from typing import List, Dict, Any
from ..common import SourceType, EvidenceItem, Provenance, FlowStep, is_mock


class GitHubAgent:
    """Agent for collecting evidence from GitHub."""
    
    def __init__(self):
        """Initialize GitHub agent."""
        self.mode = "mock"  # Default to mock
    
    def find_last_pr(self, branch: str = None, change_id: str = None) -> Dict[str, Any]:
        """
        Find last PR matching criteria.
        
        Args:
            branch: Branch name filter
            change_id: Change ID filter
            
        Returns:
            PR information
        """
        # Mock data: PR 141 for CHG-000123
        return {
            "pr_number": 141,
            "branch": "release/2026.1",
            "change_id": "CHG-000123",
            "approvers": ["a_rao", "s_kaur"],
            "approver_count": 2,
            "all_checks_passed": True,
            "has_deploy_approver": True,
            "merged_at": "2026-03-20",
            "checks": ["unit", "integration"]
        }
    
    def get_code_by_jira(self, jira_id: str, max_snippets: int = 20) -> List[Dict[str, Any]]:
        """
        Get code snippets by JIRA ID.
        
        Args:
            jira_id: JIRA ID to search
            max_snippets: Max snippets to return
            
        Returns:
            List of code snippets
        """
        # Mock data for JIRA-4521
        if jira_id == "JIRA-4521":
            return [
                {
                    "file": "scripts/load_txn.sh",
                    "line": 15,
                    "content": "sqlplus -s <<EOF\n# JIRA-4521 entrypoint\n@PKG_TXN_LOAD.load_txn\nEOF",
                    "type": "code_snippet"
                },
                {
                    "file": "db/oracle/PKG_TXN_LOAD.sql",
                    "line": 8,
                    "content": "CREATE DATABASE LINK SRC_DBLINK; SELECT * FROM src_transactions@SRC_DBLINK;",
                    "type": "code_snippet"
                }
            ]
        return []
    
    def trace_code_flow(self, change_id: str) -> Dict[str, Any]:
        """
        Trace code flow for a change.
        
        Args:
            change_id: Change ID to trace
            
        Returns:
            Code flow information
        """
        # Mock data for CHG-000123
        flow_steps = [
            FlowStep(
                type="control-m",
                ref="scheduler/LOAD_TN_DAILY.xml",
                line=12,
                detail="Control-M job referencing CHG-000123",
                excerpt="<job name='LOAD_TXN'>"
            ),
            FlowStep(
                type="shell",
                ref="scripts/load_txn.sh",
                line=15,
                detail="Bash script calling PKG_TXN_LOAD.load_txn",
                excerpt="sqlplus -s @PKG_TXN_LOAD.load_txn"
            ),
            FlowStep(
                type="oracle",
                ref="db/oracle/PKG_TXN_LOAD.sql",
                line=8,
                detail="Reads from src_transactions@SRC_DBLINK",
                excerpt="SELECT * FROM src_transactions@SRC_DBLINK"
            ),
            FlowStep(
                type="oracle",
                ref="db/oracle/PKG_TXN_CTRL.sql",
                line=25,
                detail="COMMIT and transaction control",
                excerpt="COMMIT; EXCEPTION WHEN OTHERS THEN ROLLBACK;"
            ),
        ]
        
        return {
            "flow": flow_steps,
            "dblink": {
                "name": "SRC_DBLINK",
                "defined_in": "db/oracle/PKG_TXN_LOAD.sql",
                "line": 5
            },
            "data_sources_found": ["src_transactions@SRC_DBLINK", "src_customer@SRC_DBLINK"],
            "transaction_control": {
                "commit_line": 25,
                "rollback_line": 26
            },
            "checks": {
                "dblink_definition": "PASS",
                "data_from_dblink_only": "PASS",
                "transaction_control": "PASS"
            }
        }
    
    def collect(self, operations: List[str], targets: Dict[str, Any], start_id: int = 1) -> List[EvidenceItem]:
        """
        Collect evidence items based on operations.
        
        Args:
            operations: List of operations to perform
            targets: Target IDs and criteria
            start_id: Starting ID for evidence items
            
        Returns:
            List of EvidenceItem objects
        """
        items = []
        item_id = start_id
        
        # Find last PR
        if "find_last_pr" in operations:
            pr_info = self.find_last_pr()
            items.append(EvidenceItem(
                id=f"EV-{item_id:04d}",
                type=SourceType.PR,
                summary=f"PR #{pr_info['pr_number']} - Branch {pr_info['branch']}",
                content=f"PR merged on {pr_info['merged_at']}. Approvers: {', '.join(pr_info['approvers'])}",
                checks={
                    "all_checks_passed": "PASS" if pr_info['all_checks_passed'] else "FAIL",
                    "has_deploy_approver": "PASS" if pr_info['has_deploy_approver'] else "FAIL"
                },
                audit_points=["CHG-000123"],
                provenance=Provenance(
                    system="github",
                    method="api",
                    ref=f"PR {pr_info['pr_number']}",
                    extra={"change_id": pr_info.get('change_id')}
                )
            ))
            item_id += 1
        
        # Get code by JIRA
        if "get_code_by_jira" in operations and targets.get("jira_ids"):
            for jira_id in targets["jira_ids"]:
                snippets = self.get_code_by_jira(jira_id)
                for snippet in snippets:
                    items.append(EvidenceItem(
                        id=f"EV-{item_id:04d}",
                        type=SourceType.CODE_SNIPPET,
                        summary=f"Code snippet for {jira_id}: {snippet['file']}:{snippet['line']}",
                        content=snippet['content'],
                        audit_points=[jira_id],
                        provenance=Provenance(
                            system="github",
                            method="code_search",
                            ref=snippet['file'],
                            line=snippet['line']
                        )
                    ))
                    item_id += 1
        
        # Trace code flow
        if "trace_code_flow" in operations:
            flow_info = self.trace_code_flow(targets.get("change_ids", ["CHG-000123"])[0] if targets.get("change_ids") else "CHG-000123")
            items.append(EvidenceItem(
                id=f"EV-{item_id:04d}",
                type=SourceType.CODE_FLOW,
                summary="Code flow trace for transaction processing",
                flow=flow_info["flow"],
                checks=flow_info["checks"],
                audit_points=["CHG-000123", "JIRA-4521"],
                provenance=Provenance(
                    system="github",
                    method="code_trace",
                    extra={"dblink": flow_info["dblink"]}
                )
            ))
        
        return items


if __name__ == "__main__":
    agent = GitHubAgent()
    items = agent.collect(
        ["find_last_pr", "get_code_by_jira", "trace_code_flow"],
        {"jira_ids": ["JIRA-4521"], "change_ids": ["CHG-000123"]}
    )
    for item in items:
        print(f"{item.id}: {item.type} - {item.summary}")
