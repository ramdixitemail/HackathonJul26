"""
Control template library.

Each template defines the requirements an evidence pack must satisfy,
and which evidence sources are relevant to checking them.
"""

CONTROL_TEMPLATES = [
    {
        "id": "change-mgmt-sod-4eyes-tests",
        "name": "Change Management — SoD + 4-eyes + tests",
        "description": "Validates that a production change had segregation of duties, "
                        "independent (4-eyes) approval, and passing automated tests before deploy.",
        "default_sources": ["repo", "docs", "approvals", "screenshots"],
        "requirements": [
            {
                "id": "req-1",
                "text": "Two independent approvals",
                "checks_for": "Two distinct approvers (not the change author) approved the change "
                              "in the pull request or approval workflow.",
            },
            {
                "id": "req-2",
                "text": "Tests passed",
                "checks_for": "The automated test suite / pipeline reports a passing status "
                              "for the change prior to deployment.",
            },
            {
                "id": "req-3",
                "text": "Segregated deploy",
                "checks_for": "The person who deployed the change is not the same person who "
                              "authored or approved it (segregation of duties).",
            },
        ],
    },
    {
        "id": "access-review-quarterly",
        "name": "Access Review — Quarterly user access recertification",
        "description": "Validates that privileged access was reviewed and recertified by an "
                        "independent approver on a quarterly cadence.",
        "default_sources": ["docs", "approvals", "screenshots"],
        "requirements": [
            {
                "id": "req-1",
                "text": "Access list reviewed",
                "checks_for": "A documented review of the current access list exists for the period.",
            },
            {
                "id": "req-2",
                "text": "Independent recertification",
                "checks_for": "The reviewer is not the access holder and signed off on the recertification.",
            },
            {
                "id": "req-3",
                "text": "Exceptions remediated",
                "checks_for": "Any flagged exceptions have a documented remediation action or ticket.",
            },
        ],
    },
    {
        "id": "incident-response-postmortem",
        "name": "Incident Response — Postmortem completeness",
        "description": "Validates that an incident has a complete, reviewed postmortem with tracked action items.",
        "default_sources": ["docs", "tickets", "screenshots"],
        "requirements": [
            {
                "id": "req-1",
                "text": "Postmortem document exists",
                "checks_for": "A postmortem / RCA document exists for the incident.",
            },
            {
                "id": "req-2",
                "text": "Root cause identified",
                "checks_for": "The document states a specific root cause, not just symptoms.",
            },
            {
                "id": "req-3",
                "text": "Action items tracked",
                "checks_for": "Follow-up action items are logged as tickets with owners.",
            },
        ],
    },
]

SOURCE_LABELS = {
    "repo": "Code repo (Bitbucket / GitHub)",
    "docs": "Document repository (Confluence)",
    "approvals": "Approvals / Pipelines",
    "screenshots": "Screenshots (portal)",
    "tickets": "Ticketing (Jira)",
}


def get_template(template_id):
    for t in CONTROL_TEMPLATES:
        if t["id"] == template_id:
            return t
    return None
