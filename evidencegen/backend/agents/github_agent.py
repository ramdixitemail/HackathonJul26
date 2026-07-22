"""
Code repo agent — collects commit / pull-request / approval evidence
for a given change from GitHub (real, if GITHUB_TOKEN + GITHUB_REPO are
set) or Bitbucket, else returns realistic mock data.
"""
import os
import requests
from .base import new_id, now_iso, has_real_credentials, random_person


def _mock(change_id):
    author = random_person()
    approver1 = random_person(exclude=author)
    approver2 = random_person(exclude=author)
    return [
        {
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "pull_request",
            "title": f"PR #482 — {change_id}: update payment retry policy",
            "detail": f"Opened by {author}. 6 files changed, 2 approvals required by branch protection.",
            "actor": author,
            "url": f"https://github.com/example-org/payments-service/pull/482",
            "timestamp": now_iso(180),
            "is_mock": True,
        },
        {
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "approval",
            "title": f"Review approved by {approver1}",
            "detail": "Approved via GitHub required-reviewers check.",
            "actor": approver1,
            "url": "https://github.com/example-org/payments-service/pull/482#pullrequestreview-1",
            "timestamp": now_iso(150),
            "is_mock": True,
        },
        {
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "approval",
            "title": f"Review approved by {approver2}",
            "detail": "Second independent approval, satisfies branch protection rule.",
            "actor": approver2,
            "url": "https://github.com/example-org/payments-service/pull/482#pullrequestreview-2",
            "timestamp": now_iso(130),
            "is_mock": True,
        },
        {
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "commit",
            "title": "Merge commit 8f3a2c1 into main",
            "detail": f"Merged by {approver1} after checks passed.",
            "actor": approver1,
            "url": "https://github.com/example-org/payments-service/commit/8f3a2c1",
            "timestamp": now_iso(120),
            "is_mock": True,
        },
    ]


def _real(change_id, repo):
    """Best-effort real GitHub pull search by branch/PR title containing change_id."""
    token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/search/issues?q={change_id}+repo:{repo}+type:pr"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    evidence = []
    for pr in items[:3]:
        evidence.append({
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "pull_request",
            "title": pr.get("title"),
            "detail": f"State: {pr.get('state')}, comments: {pr.get('comments')}",
            "actor": pr.get("user", {}).get("login", "unknown"),
            "url": pr.get("html_url"),
            "timestamp": pr.get("updated_at"),
            "is_mock": False,
        })
    return evidence


def _real_commits(repo, limit=5):
    """Fallback for repos with no PR workflow: pull the most recent real
    commits directly from the default branch. Used when a PR search finds
    nothing, so a plain single-branch repo still returns live evidence
    instead of falling back to mock."""
    token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/commits"
    resp = requests.get(url, headers=headers, params={"per_page": limit}, timeout=10)
    resp.raise_for_status()
    commits = resp.json()
    evidence = []
    for c in commits:
        sha = c.get("sha", "")[:7]
        commit_info = c.get("commit", {})
        author_info = commit_info.get("author", {})
        evidence.append({
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "commit",
            "title": f"Commit {sha} — {commit_info.get('message', '').splitlines()[0][:80]}",
            "detail": f"Author: {author_info.get('name', 'unknown')} on "
                      f"{author_info.get('date', 'unknown date')}. No open PR matched this "
                      f"change; showing raw commit history instead.",
            "actor": (c.get("author") or {}).get("login") or author_info.get("name", "unknown"),
            "url": c.get("html_url"),
            "timestamp": author_info.get("date", now_iso(0)),
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
        try:
            real_commits = _real_commits(repo)
            if real_commits:
                return real_commits
        except Exception:
            pass
    return _mock(change_id or control_id or "CHG-000000")
