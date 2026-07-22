"""
Screenshots agent — collects screenshot evidence captured by the internal
audit portal (e.g. an approval-screen capture uploaded during the change).
There is no common free public API for this, so this agent always returns
realistic mock/placeholder evidence, but keeps the same collect() contract
so it can be swapped for a real internal-portal integration later.
"""
from .base import new_id, now_iso


def collect(change_id, control_id=None, **kwargs):
    ident = change_id or control_id or "CHG-000000"
    return [
        {
            "id": new_id(),
            "source": "screenshots",
            "source_label": "Screenshots (portal)",
            "type": "screenshot",
            "title": f"Approval screen capture — {ident}",
            "detail": "Portal-captured screenshot of the approval workflow at time of sign-off.",
            "actor": "audit-portal",
            "url": "https://portal.example.com/evidence/screenshots/approval-482.png",
            "timestamp": now_iso(140),
            "is_mock": True,
        },
    ]
