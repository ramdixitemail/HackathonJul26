"""Pydantic v2 schemas for AuditMate."""
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


# Enums
class SourceType(str, Enum):
    """Evidence source types."""
    PR = "pr"
    APPROVAL = "approval"
    COMMIT = "commit"
    PIPELINE = "pipeline"
    DEPLOY = "deploy"
    CODE_SNIPPET = "code_snippet"
    CODE_FLOW = "code_flow"
    CONFIG = "config"
    DOC = "doc"
    SCREENSHOT = "screenshot"


class EvidenceGoal(str, Enum):
    """Evidence collection goals."""
    LAST_PR_FOR_CHANGE = "last_pr_for_change"
    TWO_INDEPENDENT_APPROVALS = "two_independent_approvals"
    TESTS_PASSED = "tests_passed"
    SEGREGATED_DEPLOY_APPROVAL = "segregated_deploy_approval"
    TRACEABILITY_CHAIN = "traceability_chain"
    BRANCH_PROTECTION = "branch_protection"
    JIRA_CODE_SNIPPET = "jira_code_snippet"
    DBLINK_DEFINITION = "dblink_definition"
    DATA_FROM_DBLINK_ONLY = "data_from_dblink_only"
    TRANSACTION_CONTROL = "transaction_control"
    CODE_FLOW = "code_flow"
    SECRETS_ABSENT = "secrets_absent"
    LINKED_DESIGN_DOC = "linked_design_doc"
    PORTAL_COMPLIANCE = "portal_compliance"


# Core Models
class AuditPoint(BaseModel):
    """Audit point extracted from audit text."""
    id: str
    text: str
    category: Optional[str] = None


class AgentSpec(BaseModel):
    """Agent specification."""
    enabled: bool = True
    input: Dict[str, Any] = Field(default_factory=dict)


class AuditIntake(BaseModel):
    """Audit intake request."""
    audit_id: Optional[str] = None
    audit_text: Optional[str] = None
    document_ref: Optional[str] = None


class ParsedIntent(BaseModel):
    """Parsed intent from instruction."""
    targets: Dict[str, Any] = Field(default_factory=dict)
    operations: List[str] = Field(default_factory=list)
    unresolved: List[str] = Field(default_factory=list)


class EvidenceCollectionRequest(BaseModel):
    """Request to collect evidence."""
    request_id: str
    requested_by: Optional[str] = None
    control_ref: Optional[str] = None
    instruction: str
    parsed_intent: Optional[ParsedIntent] = None
    evidence_goals: List[EvidenceGoal] = Field(default_factory=list)
    agents: Dict[str, AgentSpec] = Field(default_factory=dict)
    application_id: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)


class Provenance(BaseModel):
    """Evidence provenance information."""
    system: str
    method: str
    ref: Optional[str] = None
    line: Optional[int] = None
    captured_at: Optional[datetime] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class FlowStep(BaseModel):
    """Step in a code flow."""
    type: str
    ref: str
    line: Optional[int] = None
    detail: str
    excerpt: Optional[str] = None


class EvidenceItem(BaseModel):
    """Single evidence item."""
    id: str
    type: SourceType
    summary: str
    content: Optional[str] = None
    image: Optional[str] = None
    flow: Optional[List[FlowStep]] = None
    checks: Dict[str, str] = Field(default_factory=dict)
    audit_points: List[str] = Field(default_factory=list)
    provenance: Provenance


class Relation(BaseModel):
    """Relationship between evidence items."""
    from_id: str
    to_id: str
    kind: str


class EvidenceSet(BaseModel):
    """Collection of evidence items."""
    request_id: str
    instruction: str
    control_ref: Optional[str] = None
    storage: Optional[str] = None
    counts: Dict[str, int] = Field(default_factory=dict)
    items: List[EvidenceItem] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)
    audit_points: List[AuditPoint] = Field(default_factory=list)
    narrative: Optional[str] = None
    document_path: Optional[str] = None


class QnAQuery(BaseModel):
    """Query for Q&A."""
    question: str
    scope: str = "auto"
    evidence_id: Optional[str] = None
    request_id: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    """Citation for answer."""
    label: str
    ref: Optional[str] = None
    kind: str = "evidence"


class QnAAnswer(BaseModel):
    """Answer to a question."""
    answer: str
    routed_to: str = "evidence"
    citations: List[Citation] = Field(default_factory=list)
    table: Optional[List[Dict[str, Any]]] = None
    unsupported: bool = False


class KGQuery(BaseModel):
    """Query for knowledge graph."""
    question: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)


class KAnswer(BaseModel):
    """Knowledge graph answer."""
    narrative: str
    table: List[Dict[str, Any]] = Field(default_factory=list)
    cited_paths: List[str] = Field(default_factory=list)
    cypher: Optional[str] = None


class KPIs(BaseModel):
    """KPI metrics."""
    open_vulnerabilities: int = 0
    audit_items_due_30d: int = 0
    high_severity_siis: int = 0
    remediations_on_track_pct: float = 0.0
