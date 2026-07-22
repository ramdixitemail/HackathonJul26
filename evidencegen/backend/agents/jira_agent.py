"""
Ticketing agent — collects the change/incident ticket from Jira (real, if
JIRA_BASE_URL + JIRA_EMAIL + JIRA_API_TOKEN are set), else mock data.
"""
import os
import requests
from .base import new_id, now_iso, has_real_credentials


def _mock(change_id):
    return [
        {
            "id": new_id(),
            "source": "tickets",
            "source_label": "Ticketing (Jira)",
            "type": "change_ticket",
            "title": f"{change_id} — Change ticket",
            "detail": "Status: Done. Linked to CAB approval and deployment window.",
            "actor": "jira",
            "url": f"https://example.atlassian.net/browse/{change_id}",
            "timestamp": now_iso(220),
            "is_mock": True,
        },
    ]


def _real(change_id, base_url, email, token):
    auth = (email, token)
    url = f"{base_url}/rest/api/3/issue/{change_id}"
    resp = requests.get(url, auth=auth, timeout=10)
    resp.raise_for_status()
    issue = resp.json()
    fields = issue.get("fields", {})
    return [{
        "id": new_id(),
        "source": "tickets",
        "source_label": "Ticketing (Jira)",
        "type": "change_ticket",
        "title": f"{issue.get('key')} — {fields.get('summary', '')}",
        "detail": f"Status: {fields.get('status', {}).get('name', 'unknown')}",
        "actor": fields.get("reporter", {}).get("displayName", "unknown"),
        "url": f"{base_url}/browse/{issue.get('key')}",
        "timestamp": fields.get("updated", now_iso(0)),
        "is_mock": False,
    }]


def collect(change_id, control_id=None, **kwargs):
    base_url = os.environ.get("JIRA_BASE_URL")
    if has_real_credentials("JIRA_EMAIL", "JIRA_API_TOKEN") and base_url and change_id:
        try:
            real = _real(change_id, base_url, os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
            if real:
                return real
        except Exception:
            pass
    return _mock(change_id or control_id or "CHG-000000")
