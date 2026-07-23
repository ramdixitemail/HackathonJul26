"""
Code repo agent — collects commit / pull-request / approval / code-snippet
evidence for a given change or branch from GitHub (real, if GITHUB_TOKEN +
GITHUB_REPO are set), else returns realistic mock data.

Real-data lookup order (first that returns results wins):
  1. Search for a pull request matching the change id -> pull its full
     approval/review history + a code snippet from its diff.
  2. Treat the identifier as a branch name -> fetch the last commit on
     that branch + a code snippet from that commit's diff.
  3. Fall back to the most recent commits on the repo's default branch.
  4. Fall back to mock data (no token/repo configured, or all of the
     above failed/errored).
"""
import os
import requests
from .base import new_id, now_iso, has_real_credentials, random_person

MAX_SNIPPET_CHARS = 1200


def _headers():
    token = os.environ["GITHUB_TOKEN"]
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def _truncate(text, limit=MAX_SNIPPET_CHARS):
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n... (truncated)"


# ---------------------------------------------------------------------
# Mock data (used when no real credentials, or every real lookup fails)
# ---------------------------------------------------------------------

def _mock(change_id):
    author = random_person()
    approver1 = random_person(exclude=author)
    approver2 = random_person(exclude=author)
    mock_snippet = (
        "--- a/src/payments/retry_policy.py\n"
        "+++ b/src/payments/retry_policy.py\n"
        "@@ -12,7 +12,7 @@ def should_retry(attempt, error):\n"
        "-    return attempt < 3\n"
        "+    return attempt < 5 and error.is_transient\n"
    )
    return [
        {
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "pull_request",
            "title": f"PR #482 — {change_id}: update payment retry policy",
            "detail": f"Opened by {author}. 6 files changed, 2 approvals required by branch protection.",
            "actor": author,
            "url": "https://github.com/example-org/payments-service/pull/482",
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
            "type": "code_snippet",
            "title": "Diff — src/payments/retry_policy.py",
            "detail": mock_snippet,
            "actor": author,
            "url": "https://github.com/example-org/payments-service/pull/482/files",
            "timestamp": now_iso(140),
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


# ---------------------------------------------------------------------
# Real GitHub API calls
# ---------------------------------------------------------------------

def _pr_reviews(repo, pr_number):
    """Full approval/review history for a PR: every reviewer and their
    decision (APPROVED / CHANGES_REQUESTED / COMMENTED), in order."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    resp = requests.get(url, headers=_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def _pr_first_file_patch(repo, pr_number):
    """One representative code snippet (first changed file's diff) for a PR."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    resp = requests.get(url, headers=_headers(), params={"per_page": 1}, timeout=10)
    resp.raise_for_status()
    files = resp.json()
    if not files:
        return None
    f = files[0]
    return f.get("filename"), f.get("patch", "")


def _commit_first_file_patch(repo, sha):
    """One representative code snippet (first changed file's diff) for a commit."""
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    resp = requests.get(url, headers=_headers(), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    files = data.get("files") or []
    if not files:
        return None
    f = files[0]
    return f.get("filename"), f.get("patch", "")


def _real(change_id, repo):
    """Search for a pull request matching the change id; if found, also
    pull its full approval history and a code snippet from its diff."""
    url = f"https://api.github.com/search/issues?q={change_id}+repo:{repo}+type:pr"
    resp = requests.get(url, headers=_headers(), timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    evidence = []

    for pr in items[:3]:
        pr_number = pr.get("number")
        evidence.append({
            "id": new_id(),
            "source": "repo",
            "source_label": "Code repo (Bitbucket / GitHub)",
            "type": "pull_request",
            "title": f"PR #{pr_number} — {pr.get('title')}",
            "detail": f"State: {pr.get('state')}, comments: {pr.get('comments')}",
            "actor": pr.get("user", {}).get("login", "unknown"),
            "url": pr.get("html_url"),
            "timestamp": pr.get("updated_at"),
            "is_mock": False,
        })

        # Full PR approval history
        try:
            reviews = _pr_reviews(repo, pr_number)
            for rv in reviews:
                state = rv.get("state", "COMMENTED")
                evidence.append({
                    "id": new_id(),
                    "source": "repo",
                    "source_label": "Code repo (Bitbucket / GitHub)",
                    "type": "approval",
                    "title": f"Review by {rv.get('user', {}).get('login', 'unknown')} — {state}",
                    "detail": f"Review state: {state} on PR #{pr_number}.",
                    "actor": rv.get("user", {}).get("login", "unknown"),
                    "url": rv.get("html_url", pr.get("html_url")),
                    "timestamp": rv.get("submitted_at", pr.get("updated_at")),
                    "is_mock": False,
                })
        except Exception:
            pass

        # One code snippet from the PR's diff
        try:
            snippet = _pr_first_file_patch(repo, pr_number)
            if snippet:
                filename, patch = snippet
                evidence.append({
                    "id": new_id(),
                    "source": "repo",
                    "source_label": "Code repo (Bitbucket / GitHub)",
                    "type": "code_snippet",
                    "title": f"Diff — {filename}",
                    "detail": _truncate(patch) or "(no textual diff available for this file)",
                    "actor": pr.get("user", {}).get("login", "unknown"),
                    "url": f"{pr.get('html_url')}/files",
                    "timestamp": pr.get("updated_at"),
                    "is_mock": False,
                })
        except Exception:
            pass

    return evidence


def _last_commit_for_branch(repo, branch):
    """Treat the identifier as a branch name and fetch its last commit,
    plus a code snippet from that commit's diff."""
    url = f"https://api.github.com/repos/{repo}/commits"
    resp = requests.get(url, headers=_headers(), params={"sha": branch, "per_page": 1}, timeout=10)
    resp.raise_for_status()
    commits = resp.json()
    if not commits:
        return []

    c = commits[0]
    sha = c.get("sha", "")
    commit_info = c.get("commit", {})
    author_info = commit_info.get("author", {})
    evidence = [{
        "id": new_id(),
        "source": "repo",
        "source_label": "Code repo (Bitbucket / GitHub)",
        "type": "commit",
        "title": f"Last commit on branch '{branch}' — {sha[:7]}",
        "detail": f"{commit_info.get('message', '').splitlines()[0][:120]}. "
                  f"Author: {author_info.get('name', 'unknown')} on {author_info.get('date', 'unknown date')}.",
        "actor": (c.get("author") or {}).get("login") or author_info.get("name", "unknown"),
        "url": c.get("html_url"),
        "timestamp": author_info.get("date", now_iso(0)),
        "is_mock": False,
    }]

    try:
        snippet = _commit_first_file_patch(repo, sha)
        if snippet:
            filename, patch = snippet
            evidence.append({
                "id": new_id(),
                "source": "repo",
                "source_label": "Code repo (Bitbucket / GitHub)",
                "type": "code_snippet",
                "title": f"Diff — {filename}",
                "detail": _truncate(patch) or "(no textual diff available for this file)",
                "actor": (c.get("author") or {}).get("login") or author_info.get("name", "unknown"),
                "url": c.get("html_url"),
                "timestamp": author_info.get("date", now_iso(0)),
                "is_mock": False,
            })
    except Exception:
        pass

    return evidence


def _real_commits(repo, limit=5):
    """Fallback for repos with no PR workflow and no matching branch name:
    pull the most recent real commits directly from the default branch."""
    url = f"https://api.github.com/repos/{repo}/commits"
    resp = requests.get(url, headers=_headers(), params={"per_page": limit}, timeout=10)
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
                      f"{author_info.get('date', 'unknown date')}. No open PR or matching branch "
                      f"found for this change; showing raw commit history instead.",
            "actor": (c.get("author") or {}).get("login") or author_info.get("name", "unknown"),
            "url": c.get("html_url"),
            "timestamp": author_info.get("date", now_iso(0)),
            "is_mock": False,
        })
    return evidence


def collect(change_id, control_id=None, **kwargs):
    identifier = change_id or control_id or ""
    repo = os.environ.get("GITHUB_REPO")

    if has_real_credentials("GITHUB_TOKEN") and repo:
        # 1. PR search -> full approval history + code snippet
        try:
            real = _real(identifier, repo)
            if real:
                return real
        except Exception:
            pass

        # 2. Treat identifier as a branch name -> last commit + snippet
        if identifier:
            try:
                branch_result = _last_commit_for_branch(repo, identifier)
                if branch_result:
                    return branch_result
            except Exception:
                pass

        # 3. Fall back to recent commits on the default branch
        try:
            real_commits = _real_commits(repo)
            if real_commits:
                return real_commits
        except Exception:
            pass

    # 4. No credentials, or everything above failed
    return _mock(identifier or "CHG-000000")
