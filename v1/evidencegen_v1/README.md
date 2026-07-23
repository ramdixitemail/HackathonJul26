# EvidenceGen — Audit Evidence Generator

An end-to-end audit-evidence-pack generator: pick a control template (e.g.
*Change Management — SoD + 4-eyes + tests*), point it at a change/control ID,
and it dispatches collector **agents** against your evidence sources (code
repo, docs, approvals/pipelines, screenshots, ticketing), then uses an
**LLM (or an offline rule engine)** to map the collected evidence against
each requirement and produce a review-ready summary.

It works with **zero configuration** — every agent falls back to realistic
mock evidence and the mapping engine falls back to deterministic rules, so
you get a fully working demo immediately. Add API tokens for GitHub,
Confluence, or Jira, and/or a free LLM key, and it upgrades to live data
automatically — no code changes required.

## Quick start

```bash
cd evidencegen
./run.sh
```

Then open **http://localhost:5050**.

(No `.env` needed to try it — see "Going live" below to connect real
sources and a free LLM.)

## What's inside

```
evidencegen/
├── backend/
│   ├── app.py                # Flask app + REST API
│   ├── templates_config.py   # Control templates & their requirements
│   ├── storage.py            # JSON-file pack storage (swap for a real DB later)
│   ├── agents/                # One module per evidence source
│   │   ├── github_agent.py       # Code repo (GitHub; Bitbucket-shaped too)
│   │   ├── confluence_agent.py   # Document repository
│   │   ├── jira_agent.py         # Ticketing
│   │   ├── approvals_agent.py    # CI pipeline + deploy-gate approvals
│   │   └── screenshots_agent.py  # Portal-captured screenshots
│   └── llm/
│       ├── llm_client.py     # Groq / Ollama / offline-rules provider switch
│       ├── mapping.py        # Evidence → requirement mapping (LLM or rules)
│       └── qa.py             # Q&A chat over a stored evidence pack
├── frontend/                 # Vanilla HTML/CSS/JS UI (no build step)
├── requirements.txt
├── .env.example
└── run.sh
```

## How the "agents" work

Every source has a `collect(change_id, control_id) -> [evidence...]` function
with the exact same contract. Each one:

1. Checks whether real credentials are configured (env vars).
2. If yes, calls the real API and returns real evidence.
3. If no credentials are set, **or** the real call fails for any reason, it
   returns realistic mock evidence — so a demo, a broken token, or a rate
   limit never breaks the flow, it just labels the evidence `is_mock: true`.

This means you can add one integration at a time (e.g. just GitHub) and the
rest keep working as mocks.

## Going live: connect real sources & a free LLM

Copy `.env.example` to `.env` and fill in what you have:

- **LLM (pick one, both are free):**
  - [Groq](https://console.groq.com) — free-tier API, fast hosted Llama
    models. Set `GROQ_API_KEY`.
  - [Ollama](https://ollama.com) — fully local, no API key, no cost. Install
    it, `ollama pull llama3.1`, run `ollama serve`, then set
    `OLLAMA_HOST=http://localhost:11434`.
  - Set neither and the app uses a built-in deterministic rule engine — it
    always produces an answer, it's just less nuanced than an LLM.

- **Real sources (optional, each is independent):**
  - `GITHUB_TOKEN` + `GITHUB_REPO` — pulls real PRs/commits and CI runs.
  - `CONFLUENCE_BASE_URL` + `CONFLUENCE_EMAIL` + `CONFLUENCE_API_TOKEN` —
    pulls real change-record pages.
  - `JIRA_BASE_URL` + `JIRA_EMAIL` + `JIRA_API_TOKEN` — pulls the real change
    ticket.

The **Settings** page in the app shows which of these are currently active.

## Extending it

- **New control template:** add an entry to `CONTROL_TEMPLATES` in
  `backend/templates_config.py` with its `requirements` list.
- **New evidence source:** add `backend/agents/your_agent.py` with a
  `collect(change_id, control_id)` function returning the same evidence-item
  shape as the others, then register it in `backend/agents/__init__.py`'s
  `AGENT_REGISTRY` and add its label to `SOURCE_LABELS`.
- **Swap storage for a real database:** reimplement the four functions in
  `backend/storage.py` (`list_packs`, `get_pack`, `save_pack`,
  `delete_pack`) against Postgres/SQLite — nothing else needs to change.

## API reference

| Method & path              | Purpose                                   |
|----------------------------|--------------------------------------------|
| `GET /api/templates`       | List control templates                     |
| `GET /api/packs`           | List all generated evidence packs           |
| `POST /api/packs`          | Run collection + mapping, create a new pack |
| `GET /api/packs/<id>`      | Fetch one pack                              |
| `DELETE /api/packs/<id>`   | Delete a pack                               |
| `POST /api/chat`           | Ask a question about a pack (Q&A chat)      |
| `GET /api/status`          | Which LLM/integrations are active           |
