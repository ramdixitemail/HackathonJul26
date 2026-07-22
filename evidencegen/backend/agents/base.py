"""
Shared helpers for evidence-collector agents.

Every agent follows the same contract:

    collect(context: dict) -> list[dict]

where each returned evidence item looks like:

    {
        "id": "ev-...",
        "source": "repo" | "docs" | "approvals" | "screenshots" | "tickets",
        "source_label": "Code repo (Bitbucket / GitHub)",
        "type": "commit" | "pull_request" | "approval" | "pipeline_run" | ...,
        "title": "...",
        "detail": "...",
        "actor": "person or system that produced this evidence",
        "url": "https://... (mock or real)",
        "timestamp": "ISO 8601",
        "is_mock": bool,
    }

If a real API token is configured (see each agent's REQUIRED_ENV), the agent
tries the real API first and falls back to realistic mock data on any
failure, so the product always demoes end-to-end even with zero setup.
"""
import os
import uuid
import random
from datetime import datetime, timedelta


def new_id(prefix="ev"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def now_iso(offset_minutes=0):
    return (datetime.utcnow() - timedelta(minutes=offset_minutes)).isoformat(timespec="seconds") + "Z"


def has_real_credentials(*env_vars):
    """Return True only if every listed env var is set and non-empty."""
    return all(os.environ.get(v) for v in env_vars)


MOCK_PEOPLE = [
    "a.rao", "s.khan", "m.chen", "j.patel", "l.fernandes", "d.silva",
]


def random_person(exclude=None):
    pool = [p for p in MOCK_PEOPLE if p != exclude] or MOCK_PEOPLE
    return random.choice(pool)
