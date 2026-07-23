"""Document Repository Agent for collecting evidence from documents."""
from pathlib import Path
from typing import List, Dict, Any
from ..common import SourceType, EvidenceItem, Provenance, DOC_FOLDER


class DocRepoAgent:
    """Agent for collecting evidence from document repositories."""
    
    def __init__(self):
        """Initialize document repo agent."""
        self.doc_folder = Path(DOC_FOLDER)
    
    def collect(self, query: str, start_id: int = 1, max_pages: int = 5) -> List[EvidenceItem]:
        """
        Collect evidence items from documents.
        
        Args:
            query: Search query
            start_id: Starting ID for evidence items
            max_pages: Max pages to return
            
        Returns:
            List of EvidenceItem objects
        """
        items = []
        item_id = start_id
        
        # Mock data: Design document for dbLink audit
        design_doc = {
            "title": "Design: Daily TXN Load via dbLink",
            "file": "design_txn_load_dblink.md",
            "summary": "Daily transaction load process using database link for data integration",
            "content": """
# Design: Daily TXN Load via dbLink

## Overview
Daily transaction loading via SRC_DBLINK ensures segregated data access.

## Components
- Source: src_transactions@SRC_DBLINK (read-only)
- Processing: PKG_TXN_LOAD.load_txn
- Control: PKG_TXN_CTRL.commit_batch with transaction handling
- Scheduler: Control-M LOAD_TN_DAILY

## Audit Trail
- CHG-000123: Implementation
- JIRA-4521: Data integration task
- AUD-2026-0161: Related audit

## Compliance
All reads via dblink; transaction control with COMMIT/ROLLBACK.
            """,
            "related_audit_points": ["CHG-000123", "JIRA-4521", "AUD-2026-0161"]
        }
        
        items.append(EvidenceItem(
            id=f"EV-{item_id:04d}",
            type=SourceType.DOC,
            summary=design_doc["title"],
            content=design_doc["content"],
            audit_points=design_doc["related_audit_points"],
            provenance=Provenance(
                system="folder",
                method="search",
                ref=design_doc["file"],
                extra={"query": query}
            )
        ))
        item_id += 1
        
        # Mock data: Runbook
        runbook = {
            "title": "Runbook: Payments Recovery",
            "file": "runbook_payments_recovery.md",
            "summary": "Recovery procedures for payment processing",
            "content": "Procedures for recovering failed payments with dblink verification."
        }
        
        items.append(EvidenceItem(
            id=f"EV-{item_id:04d}",
            type=SourceType.DOC,
            summary=runbook["title"],
            content=runbook["content"],
            provenance=Provenance(
                system="folder",
                method="search",
                ref=runbook["file"],
                extra={"query": query}
            )
        ))
        
        return items


if __name__ == "__main__":
    agent = DocRepoAgent()
    items = agent.collect("dblink transaction control")
    for item in items:
        print(f"{item.id}: {item.type} - {item.summary}")
