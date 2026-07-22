"""
Maps collected evidence against a control template's requirements.

Tries the configured LLM first (Groq / Ollama) for a nuanced, cited
judgement; falls back to a deterministic keyword/heuristic engine so the
product always produces a result, even fully offline.
"""
from . import llm_client


SYSTEM_PROMPT = (
    "You are an audit-evidence analyst. You are given a list of evidence items "
    "collected for a change, and a list of control requirements. For EACH "
    "requirement, decide if the evidence SATISFIES, PARTIALLY SATISFIES, or "
    "does NOT satisfy it, citing which evidence item id(s) support your call. "
    "Respond ONLY with a JSON array, no prose, no markdown fences, in this shape: "
    '[{"requirement_id": "req-1", "status": "satisfied", "rationale": "...", '
    '"evidence_ids": ["ev-xxxx"]}]. status must be one of: satisfied, partial, missing.'
)


def _build_prompt(evidence, requirements):
    ev_lines = [
        f'- id={e["id"]} source={e["source"]} type={e["type"]} actor={e.get("actor")} '
        f'title="{e["title"]}" detail="{e["detail"]}"'
        for e in evidence
    ]
    req_lines = [f'- id={r["id"]} text="{r["text"]}" checks_for="{r["checks_for"]}"' for r in requirements]
    return (
        "EVIDENCE:\n" + "\n".join(ev_lines) +
        "\n\nREQUIREMENTS:\n" + "\n".join(req_lines)
    )


def _rule_based(evidence, requirements):
    """Deterministic offline fallback. Uses simple heuristics per requirement
    text so the tool works with zero LLM configuration."""
    results = []
    approvals = [e for e in evidence if e["type"] == "approval"]
    approvers = {e["actor"] for e in approvals}
    pr_items = [e for e in evidence if e["type"] == "pull_request"]
    authors = {e["actor"] for e in pr_items}
    pipeline_runs = [e for e in evidence if e["type"] == "pipeline_run"]
    deploy_gates = [e for e in evidence if e["type"] == "deploy_gate"]

    for req in requirements:
        text = req["text"].lower()
        if "approval" in text:
            if len(approvers) >= 2:
                results.append({
                    "requirement_id": req["id"], "status": "satisfied",
                    "rationale": f"{len(approvers)} distinct approvers found: {', '.join(sorted(approvers))}.",
                    "evidence_ids": [e["id"] for e in approvals],
                })
            elif len(approvers) == 1:
                results.append({
                    "requirement_id": req["id"], "status": "partial",
                    "rationale": "Only one distinct approver found; a second independent approval is missing.",
                    "evidence_ids": [e["id"] for e in approvals],
                })
            else:
                results.append({
                    "requirement_id": req["id"], "status": "missing",
                    "rationale": "No approval evidence was collected for this change.",
                    "evidence_ids": [],
                })
        elif "test" in text:
            passing = [r for r in pipeline_runs if "pass" in r["detail"].lower()
                       or (r.get("detail", "").lower().find("conclusion: success") >= 0)]
            if pipeline_runs and (passing or "pass" in pipeline_runs[0]["detail"].lower()):
                results.append({
                    "requirement_id": req["id"], "status": "satisfied",
                    "rationale": "CI pipeline evidence shows passing test stages.",
                    "evidence_ids": [e["id"] for e in pipeline_runs],
                })
            elif pipeline_runs:
                results.append({
                    "requirement_id": req["id"], "status": "partial",
                    "rationale": "Pipeline evidence found but pass status could not be confirmed.",
                    "evidence_ids": [e["id"] for e in pipeline_runs],
                })
            else:
                results.append({
                    "requirement_id": req["id"], "status": "missing",
                    "rationale": "No CI/pipeline evidence was collected for this change.",
                    "evidence_ids": [],
                })
        elif "segregat" in text or "deploy" in text:
            if deploy_gates:
                deployer = deploy_gates[0]["actor"]
                overlapping = deployer in authors or deployer in approvers
                if not overlapping:
                    results.append({
                        "requirement_id": req["id"], "status": "satisfied",
                        "rationale": f"Deploy was executed by {deployer}, distinct from the author/approvers.",
                        "evidence_ids": [e["id"] for e in deploy_gates],
                    })
                else:
                    results.append({
                        "requirement_id": req["id"], "status": "missing",
                        "rationale": f"Deployer {deployer} overlaps with an author or approver — SoD violation.",
                        "evidence_ids": [e["id"] for e in deploy_gates],
                    })
            else:
                results.append({
                    "requirement_id": req["id"], "status": "missing",
                    "rationale": "No deployment-gate evidence was collected for this change.",
                    "evidence_ids": [],
                })
        else:
            # Generic fallback: satisfied if any evidence at all was collected.
            if evidence:
                results.append({
                    "requirement_id": req["id"], "status": "partial",
                    "rationale": "Evidence was collected but no specific automated check matched this "
                                 "requirement; a reviewer should confirm manually.",
                    "evidence_ids": [e["id"] for e in evidence[:2]],
                })
            else:
                results.append({
                    "requirement_id": req["id"], "status": "missing",
                    "rationale": "No evidence was collected.",
                    "evidence_ids": [],
                })
    return results


def map_evidence_to_requirements(evidence, requirements):
    """Returns (results, engine_used) where engine_used is 'llm' or 'rules'."""
    try:
        prompt = _build_prompt(evidence, requirements)
        parsed = llm_client.call_llm_json(prompt, SYSTEM_PROMPT)
        if isinstance(parsed, list) and parsed:
            valid_ids = {r["id"] for r in requirements}
            cleaned = [p for p in parsed if p.get("requirement_id") in valid_ids]
            if cleaned:
                return cleaned, "llm:" + llm_client.active_provider()
    except Exception:
        pass
    return _rule_based(evidence, requirements), "rules"


def summarize_pack(evidence, requirements, results):
    """One-paragraph narrative summary. Uses the LLM if available, else a
    templated summary built from the mapping results."""
    satisfied = sum(1 for r in results if r["status"] == "satisfied")
    partial = sum(1 for r in results if r["status"] == "partial")
    missing = sum(1 for r in results if r["status"] == "missing")
    try:
        prompt = (
            f"Evidence count: {len(evidence)}. Requirement results: "
            f"{satisfied} satisfied, {partial} partial, {missing} missing. "
            "Write a concise (2-3 sentence) audit-ready summary of this evidence pack's "
            "readiness for review, in a neutral professional tone. No markdown."
        )
        text = llm_client.call_llm(prompt, "You write concise audit evidence-pack summaries.")
        if text.strip():
            return text.strip(), "llm:" + llm_client.active_provider()
    except Exception:
        pass
    if missing == 0 and partial == 0:
        verdict = "All requirements are satisfied by the collected evidence."
    elif missing == 0:
        verdict = f"{satisfied} of {len(results)} requirements are fully satisfied; {partial} need reviewer confirmation."
    else:
        verdict = f"{missing} of {len(results)} requirements are missing evidence and need follow-up before sign-off."
    return (
        f"Collected {len(evidence)} evidence item(s) across the selected sources. {verdict}"
    ), "rules"
