"""
Audit Intake analyzer.

Takes raw, free-text audit correspondence (an email, a policy excerpt, an
auditor's request) and extracts:
  - detected_points: individual audit/control points found in the text
  - suggested_repo:  a repo name if one is mentioned, else a placeholder
  - suggested_goals: a short goal list derived from the detected points

Uses the configured LLM (Groq / Ollama) if available; otherwise falls back
to a deterministic heuristic so this always produces a usable result.
"""
import re
from . import llm_client

SYSTEM_PROMPT = (
    "You are an audit-intake assistant. You are given raw free-text from an auditor "
    "or a compliance policy. Extract the individual, concrete audit/control points "
    "it is asking about (each a short, specific sentence), a repository name if one "
    "is mentioned (org/repo format), and a short list of evidence-collection goals. "
    "Respond ONLY with a JSON object, no prose, no markdown fences, in this shape: "
    '{"detected_points": ["...", "..."], "suggested_repo": "org/repo" or null, '
    '"suggested_goals": ["...", "..."]}'
)

DEFAULT_REPO_PLACEHOLDER = "your-org/your-repo"

_REPO_PATTERN = re.compile(r"\b([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)\b")
_REPO_HINT_WORDS = {"repo", "repository", "github.com"}

_KEYWORD_HINTS = (
    "must", "should", "shall", "require", "ensure", "verify", "confirm",
    "need to", "mandatory", "approval", "approved", "test", "review",
    "document", "screenshot", "evidence", "segregat", "control", "policy",
    "compliance", "sign-off", "signoff", "audit",
)


def _split_candidate_lines(text):
    # Prefer explicit line breaks / bullets; fall back to sentence splitting
    # for single-paragraph input.
    raw_lines = [l.strip(" \t-*•0123456789.)") for l in text.splitlines()]
    lines = [l for l in raw_lines if len(l) > 8]
    if len(lines) <= 1:
        lines = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 8]
    return lines


def _rule_based(audit_text):
    lines = _split_candidate_lines(audit_text)

    scored = []
    for line in lines:
        lower = line.lower()
        score = sum(1 for k in _KEYWORD_HINTS if k in lower)
        scored.append((score, line))

    # Prefer keyword-hinting lines, but if none score, keep the first few lines
    # so the tool still produces something useful from plain text.
    hinted = [l for s, l in scored if s > 0]
    points = hinted if hinted else [l for _, l in scored]
    points = points[:8] if points else ["(no specific audit points detected — please refine manually)"]

    repo = None
    for word in _REPO_HINT_WORDS:
        if word in audit_text.lower():
            match = _REPO_PATTERN.search(audit_text)
            if match:
                repo = match.group(1)
            break
    if not repo:
        match = _REPO_PATTERN.search(audit_text)
        if match and "/" in match.group(1) and "." not in match.group(1).split("/")[0]:
            repo = match.group(1)

    goals = points[:5]

    return {
        "detected_points": points,
        "suggested_repo": repo or DEFAULT_REPO_PLACEHOLDER,
        "suggested_goals": goals,
    }, "rules"


def analyze(audit_text):
    """Returns (result_dict, engine_used)."""
    audit_text = (audit_text or "").strip()
    if not audit_text:
        return {
            "detected_points": [],
            "suggested_repo": DEFAULT_REPO_PLACEHOLDER,
            "suggested_goals": [],
        }, "rules"

    try:
        prompt = f"AUDIT TEXT:\n{audit_text}"
        parsed = llm_client.call_llm_json(prompt, SYSTEM_PROMPT)
        if isinstance(parsed, dict) and parsed.get("detected_points"):
            parsed.setdefault("suggested_repo", DEFAULT_REPO_PLACEHOLDER)
            parsed.setdefault("suggested_goals", parsed["detected_points"][:5])
            if not parsed.get("suggested_repo"):
                parsed["suggested_repo"] = DEFAULT_REPO_PLACEHOLDER
            return parsed, "llm:" + llm_client.active_provider()
    except Exception:
        pass

    return _rule_based(audit_text)
