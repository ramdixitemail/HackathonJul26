from . import github_agent, confluence_agent, jira_agent, approvals_agent, screenshots_agent

AGENT_REGISTRY = {
    "repo": github_agent,
    "docs": confluence_agent,
    "tickets": jira_agent,
    "approvals": approvals_agent,
    "screenshots": screenshots_agent,
}


def run_agents(source_keys, change_id=None, control_id=None):
    """Run each requested source's agent and return a flat evidence list,
    plus a per-source status log (ok / error)."""
    evidence = []
    log = []
    for key in source_keys:
        agent = AGENT_REGISTRY.get(key)
        if not agent:
            log.append({"source": key, "status": "skipped", "detail": "unknown source"})
            continue
        try:
            items = agent.collect(change_id=change_id, control_id=control_id)
            evidence.extend(items)
            log.append({
                "source": key,
                "status": "ok",
                "detail": f"{len(items)} item(s) collected"
                          + (" (mock)" if items and items[0].get("is_mock") else " (live)"),
            })
        except Exception as exc:
            log.append({"source": key, "status": "error", "detail": str(exc)})
    return evidence, log
