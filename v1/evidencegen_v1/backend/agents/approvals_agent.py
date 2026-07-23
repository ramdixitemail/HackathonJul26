"""
Approvals / Pipelines agent — collects CI test results and deployment
approval-gate evidence. Uses the GitHub Actions runs API (real, if
GITHUB_TOKEN + GITHUB_REPO are set) else realistic mock data.
"""
import os
import requests
from .base import new_id, now_iso, has_real_credentials, random_person


def _mock(change_id):
    deployer = random_person()
    return [
        {
            "id": new_id(),
            "source": "approvals",
            "source_label": "Approvals / Pipelines",
            "type": "pipeline_run",
            "title": f"CI pipeline #1204 for {change_id}",
            "detail": "Stages: lint (pass), unit-tests (pass, 842/842), integration-tests (pass, 96/96).",
            "actor": "ci-runner",
            "url": "https://ci.example.com/pipelines/1204",
            "timestamp": now_iso(110),
            "is_mock": True,
        },
        {
            "id": new_id(),
            "source": "approvals",
            "source_label": "Approvals / Pipelines",
            "type": "deploy_gate",
            "title": f"Production deploy gate approved for {change_id}",
            "detail": f"Deploy executed by {deployer} via release pipeline (separate from PR author/approvers).",
            "actor": deployer,
            "url": "https://ci.example.com/pipelines/1204/deploy",
            "timestamp": now_iso(90),
            "is_mock": True,
        },
    ]


def _real(change_id, repo):
    token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    resp = requests.get(url, headers=headers, timeout=10, params={"per_page": 5})
    resp.raise_for_status()
    runs = resp.json().get("workflow_runs", [])
    evidence = []
    for run in runs[:3]:
        evidence.append({
            "id": new_id(),
            "source": "approvals",
            "source_label": "Approvals / Pipelines",
            "type": "pipeline_run",
            "title": f"{run.get('name')} — run #{run.get('run_number')}",
            "detail": f"Conclusion: {run.get('conclusion')}",
            "actor": run.get("actor", {}).get("login", "unknown"),
            "url": run.get("html_url"),
            "timestamp": run.get("updated_at"),
            "is_mock": False,
        })
    return evidence


def collect(change_id, control_id=None, **kwargs):
    repo = os.environ.get("GITHUB_REPO")
    if has_real_credentials("GITHUB_TOKEN") and repo:
        try:
            real = _real(change_id or control_id or "", repo)
            if real:
                return real
        except Exception:
            pass
    return _mock(change_id or control_id or "CHG-000000")
