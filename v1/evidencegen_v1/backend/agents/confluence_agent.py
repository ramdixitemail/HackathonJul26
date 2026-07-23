"""
Document repository agent — collects change-record / design-doc evidence
from Confluence (real, if CONFLUENCE_BASE_URL + CONFLUENCE_EMAIL +
CONFLUENCE_API_TOKEN are set), else returns realistic mock data.
"""
import os
import requests
from .base import new_id, now_iso, has_real_credentials


def _mock(change_id):
    return [
        {
            "id": new_id(),
            "source": "docs",
            "source_label": "Document repository (Confluence)",
            "type": "change_record",
            "title": f"Change Record — {change_id}",
            "detail": "Confluence page documenting change rationale, rollback plan, "
                      "and risk assessment sign-off.",
            "actor": "change-management-bot",
            "url": "https://example.atlassian.net/wiki/spaces/CHG/pages/000123",
            "timestamp": now_iso(200),
            "is_mock": True,
        },
    ]


def _real(change_id, base_url, email, token):
    auth = (email, token)
    url = f"{base_url}/wiki/rest/api/content/search"
    params = {"cql": f'text ~ "{change_id}"', "limit": 3}
    resp = requests.get(url, params=params, auth=auth, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    evidence = []
    for page in results:
        evidence.append({
            "id": new_id(),
            "source": "docs",
            "source_label": "Document repository (Confluence)",
            "type": "change_record",
            "title": page.get("title"),
            "detail": f"Confluence page id {page.get('id')}",
            "actor": "confluence",
            "url": f"{base_url}/wiki{page.get('_links', {}).get('webui', '')}",
            "timestamp": now_iso(0),
            "is_mock": False,
        })
    return evidence


def collect(change_id, control_id=None, **kwargs):
    base_url = os.environ.get("CONFLUENCE_BASE_URL")
    if has_real_credentials("CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN") and base_url:
        try:
            real = _real(
                change_id or control_id or "",
                base_url,
                os.environ["CONFLUENCE_EMAIL"],
                os.environ["CONFLUENCE_API_TOKEN"],
            )
            if real:
                return real
        except Exception:
            pass
    return _mock(change_id or control_id or "CHG-000000")
