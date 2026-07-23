"""Intent parser for audit instructions."""
import re
from typing import Tuple, Dict, List, Any
from .schemas import ParsedIntent


# Regex patterns for targets
CHANGE_ID_PATTERN = r'CHG-\d+'
JIRA_ID_PATTERN = r'(?!CHG)([A-Z]+-\d+)'
BRANCH_PATTERN = r'(release|feature|hotfix|main)/[\w\-.]+'
APP_ID_PATTERN = r'APP-\d+'

# Keywords to operations mapping
KEYWORD_OPERATIONS = {
    'last_pr': 'find_last_pr',
    'jira': 'get_code_by_jira',
    'snippet': 'get_code_by_jira',
    'dblink': 'trace_code_flow',
    'flow': 'trace_code_flow',
    'control-m': 'trace_code_flow',
    'shell': 'trace_code_flow',
    'oracle': 'trace_code_flow',
    'trace': 'trace_code_flow',
    'confluence': 'fetch_doc_page',
    'sharepoint': 'fetch_doc_page',
    'design': 'fetch_doc_page',
    'document': 'fetch_doc_page',
    'runbook': 'fetch_doc_page',
    'screenshot': 'capture_portal',
    'portal': 'capture_portal',
    'compliance': 'capture_portal',
    'secret': 'secrets_scan',
    'hardcoded': 'secrets_scan',
    'credential': 'secrets_scan',
    'approval': 'check_approvals',
    'four-eyes': 'check_approvals',
    'sod': 'check_approvals',
    'segregation': 'check_approvals',
}

GRAPH_WORDS = {
    'sii', 'vulnerability', 'cve', 'remediation', 'application',
    'overdue', 'past_due', 'portfolio', 'audit_item', 'on_track', 'at_risk'
}

EVIDENCE_WORDS = {
    'ev-', 'evidence', 'dblink', 'pr', 'pull_request', 'snippet',
    'screenshot', 'commit', 'approval', 'flow', 'transaction_control'
}


def parse_instruction(text: str) -> ParsedIntent:
    """
    Parse audit instruction to extract targets and operations.
    
    Args:
        text: Instruction text
        
    Returns:
        ParsedIntent with targets, operations, unresolved
    """
    targets = {}
    operations = set()
    unresolved = []
    
    # Extract targets
    targets['change_ids'] = re.findall(CHANGE_ID_PATTERN, text)
    targets['jira_ids'] = re.findall(JIRA_ID_PATTERN, text)
    targets['branches'] = re.findall(BRANCH_PATTERN, text)
    targets['application_ids'] = re.findall(APP_ID_PATTERN, text)
    
    # Find operations from keywords
    text_lower = text.lower()
    for keyword, operation in KEYWORD_OPERATIONS.items():
        if keyword in text_lower:
            operations.add(operation)
    
    # Default operation if none found
    if not operations:
        operations.add('trace_code_flow')
    
    return ParsedIntent(
        targets=targets,
        operations=list(operations),
        unresolved=unresolved
    )
