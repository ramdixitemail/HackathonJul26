# AuditMate - Full Stack AI Audit Assistant

**AuditMate** is a complete full-stack application for AI-powered audit assistance. It orchestrates the flow: **Audit Text → Extract Points → Collect Evidence via 3 Agents → Generate DOCX Pack → Ask (Evidence + Knowledge-Graph Q&A with KPI Dashboard)**.

## Features

✅ **Multi-Mode LLM Support**: Mock (offline), Ollama (local), or Vertex AI (GCP)  
✅ **Flexible Graph Backend**: JSON or Neo4j  
✅ **3 Evidence Collection Agents**: GitHub, Document Repo, Portal  
✅ **Intelligent Q&A Router**: Automatically routes to evidence or knowledge graph  
✅ **DOCX Report Generation**: Professional audit packs  
✅ **KPI Dashboard**: Real-time audit metrics  
✅ **Mock Mode**: Full offline operation for development and testing  

## Stack

- **Backend**: Python 3.11, FastAPI, LangGraph, Pydantic v2
- **Frontend**: React 18, TypeScript, Vite
- **Graph**: JSON (default) or Neo4j
- **LLM**: OpenAI Vertex AI (Gemini), Ollama (local), or Mock

## Quick Start

### Setup

```bash
cd AuditMate
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r Agents/requirements.txt -r Backend/requirements.txt
python -m playwright install chromium

cp .env.example .env
```

### Run in Mock Mode (Recommended for Demo)

**Terminal 1 - Backend:**
```bash
export AUDITMATE_MODE=mock
python -m uvicorn Backend.app.main:app --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm install
# If backend is on a different port (e.g. 8001), set proxy target first:
# Windows (PowerShell): $env:VITE_API_PROXY_TARGET="http://127.0.0.1:8001"
# Windows (cmd): set VITE_API_PROXY_TARGET=http://127.0.0.1:8001 && npm run dev
# macOS/Linux: export VITE_API_PROXY_TARGET=http://127.0.0.1:8001
npm run dev
```

Then open http://localhost:5173 in your browser.

### Or Run CLI Agents Directly

```bash
export AUDITMATE_MODE=mock
export PYTHONPATH=.

python -m Agents.orchestrator.run \
  "Collect evidence for CHG-000123. Trace the dbLink flow and show transaction control. Pull the design page. Capture the portal for APP-001. For JIRA-4521 include the code snippet." \
  --repo acme/payments-service \
  --app APP-001 \
  --request-id REQ-AUD-2026-0142
```

## Architecture

### Folder Structure

```
AuditMate/
├── Agents/
│   ├── common/              # Shared config, schemas, storage
│   ├── github_agent/        # Collect from version control
│   ├── doc_repo_agent/      # Collect from documents
│   ├── portal_agent/        # Capture screenshots
│   ├── audit_intake_agent/  # Process audit requests
│   ├── orchestrator/        # LangGraph + DOCX writer
│   ├── qna_agent/          # Evidence-based Q&A
│   └── graph_agent/        # Knowledge graph queries
├── Backend/
│   └── app/
│       ├── main.py         # FastAPI application
│       └── routers/        # API endpoints
├── Frontend/
│   └── src/
│       ├── App.tsx         # Main React app
│       ├── screens/        # UI screens
│       ├── api/           # API client
│       └── types/         # TypeScript types
├── data/
│   ├── graph.json         # Knowledge graph seed data
│   ├── graph_store.py     # JSON & Neo4j backends
│   └── neo4j/            # Neo4j scripts
├── Test/
│   ├── github_repo_sample/  # Mock GitHub repo
│   ├── documents/           # Design docs & runbooks
│   ├── portal_screenshots/  # Portal screenshots
│   └── audit_samples/       # Sample audit requests
└── Evidence/               # Generated reports
```

### Data Flow

```
User Input (AuditIntake)
        ↓
Parse Intent (extract CHG-*, JIRA-*, operations)
        ↓
Enable Agents (github, doc_repo, portal)
        ↓
Collect Evidence (3 agents in parallel)
        ↓
Generate Narrative & Relations
        ↓
Write DOCX Report
        ↓
Save EvidenceSet to store
        ↓
User Ask Question (Q&A Router)
        ↓
Route: Evidence or Knowledge Graph or Blended
        ↓
Return Answer with Citations
```

## API Endpoints

### Audit Intake
```
POST /api/audit-intake
  → Extract audit points & draft collection request
```

### Evidence Collection
```
POST /api/evidence/collect
  → Run 3 agents, generate DOCX
GET /api/evidence
  → List all evidence sets
GET /api/evidence/{id}
  → Load specific evidence set
GET /api/evidence/{id}/document
  → Download DOCX report
```

### Q&A
```
POST /api/qna
  → Route to evidence or graph based on question
GET /api/graph/kpis
  → Get KPI metrics
POST /api/graph/query
  → Direct graph query
```

### Health
```
GET /api/health
  → {status, mode, version}
```

## Configuration

Set via `.env`:

```bash
# LLM Mode: mock | ollama | vertex
AUDITMATE_MODE=mock

# Graph Backend: json | neo4j
GRAPH_BACKEND=json

# GitHub Source: fixtures | api
GITHUB_SOURCE=fixtures

# Doc Provider: folder | gcs | confluence | sharepoint
DOC_PROVIDER=folder
```

### Mode Switching

**Use Local Ollama:**
```bash
brew install ollama && ollama serve &
ollama pull qwen2.5:7b-instruct
export AUDITMATE_MODE=ollama
# Run backend
```

**Use Vertex AI (Gemini):**
```bash
export AUDITMATE_MODE=vertex
export GOOGLE_CLOUD_PROJECT=your-gcp-project
gcloud auth application-default login
# Run backend
```

**Use Neo4j:**
```bash
export GRAPH_BACKEND=neo4j
# Ensure Neo4j running on localhost:7687
python data/neo4j/load.py  # Seed graph.json into Neo4j
# Run backend
```

## Verification Checklist

Run these commands to verify the system in mock mode:

### 1. Graph Store
```bash
python data/graph_store.py
# Expected: KPIs + high-severity overdue SIIs
```

### 2. GitHub Agent
```bash
python -m Agents.github_agent.agent
# Expected: 3 items (PR, code_flow, code_snippets)
```

### 3. Orchestrator
```bash
export PYTHONPATH=.
python -m Agents.orchestrator.run "Trace CHG-000123 and show transaction control"
# Expected: 6 items (github 3, doc 2, portal 1), relations, narrative, DOCX + JSON paths
```

### 4. Backend Health
```bash
curl http://localhost:8000/api/health
# Expected: {status: "healthy", mode: "mock", version: "1.0.0"}
```

### 5. Q&A Agent
```bash
python -m Agents.qna_agent.agent
# Expected: Deterministic answer with evidence citations
```

### 6. Graph Agent
```bash
python -m Agents.graph_agent.agent
# Expected: KPIs + high-severity query results
```

## Key Concepts

### Golden Rule
**Every factual field (IDs, file paths, line numbers, approvers, dates, statuses) is code-derived. LLM only narrates/formats and must cite EV-id or graph path. Every LLM step has deterministic fallback for mock mode.**

### Mock Mode
Mock mode runs **fully offline with seeded data** for development and testing. It provides:
- Deterministic results
- Zero external dependencies
- Zero cost
- Perfect for demos and testing

### Evidence Citation
Every answer cites evidence items (EV-0001, EV-0002, etc.) or knowledge graph paths. "No evidence found" is a valid answer.

### Audit Points
Extracted from user input using regex for IDs and keywords. Examples:
- CHG-000123 (change ID)
- JIRA-4521 (ticket ID)
- APP-001 (application ID)
- release/2026.1 (branch)

### Evidence Goals
Automatically determined from audit text:
- last_pr_for_change
- two_independent_approvals
- tests_passed
- segregated_deploy_approval
- traceability_chain
- data_from_dblink_only
- etc.

## Example Audit Scenario

**Audit Request**: "Segregation of duties for prod changes? Tests before release? Who approved each deployment? Data only via database link?"

**Extraction**:
- Change ID: CHG-000123
- Ticket ID: JIRA-4521
- Application: APP-001 (inferred)
- Goals: segregated_deploy_approval, tests_passed, two_independent_approvals, data_from_dblink_only

**Evidence Collected**:
1. **PR #141** (GitHub Agent): 2 approvals, all checks passed, 3/20/2026
2. **Code Flow** (GitHub Agent): Control-M → Shell → PL/SQL → dbLink → COMMIT
3. **Design Doc** (Doc Repo Agent): Design: Daily TXN Load via dbLink
4. **Portal Screenshot** (Portal Agent): APP-001 compliance status

**Q&A Examples**:
- "What checks passed?" → Evidence citations (EV-0002 code flow checks)
- "Show vulnerabilities" → Graph query (3 open vulnerabilities)
- "Who approved the change?" → Evidence citations (PR approvers)

## Development

### Add a New Agent

1. Create `Agents/new_agent/agent.py`
2. Implement `collect()` method returning `List[EvidenceItem]`
3. Update orchestrator graph to call it
4. Add to enabled agents in UI

### Add a New LLM Provider

1. Update `Agents/common/model_provider.py`
2. Add mode check in `chat_model()`
3. Update `.env.example`
4. Test with `export AUDITMATE_MODE=new_provider`

### Add a New Screen

1. Create `Frontend/src/screens/NewScreen.tsx`
2. Export from main App.tsx
3. Add nav item
4. Implement screen logic using API client

## Troubleshooting

### "Module not found" errors
```bash
export PYTHONPATH=.
# Then run Python commands
```

### Frontend can't reach backend
Check vite.config.ts proxy configuration points to http://localhost:8000

### python-docx not installed
```bash
pip install python-docx
```

### Playwright chromium missing
```bash
python -m playwright install chromium
```

### Neo4j connection failed
Ensure Neo4j is running and accessible at NEO4J_URI

## Testing

Mock mode provides full testing capability:
```bash
export AUDITMATE_MODE=mock
# All agents run with deterministic mock data
# Zero external dependencies
# Perfect for CI/CD
```

## License

This project is provided as-is for audit and compliance purposes.

## Support

For issues or questions:
1. Check `.env` configuration
2. Review Test/ folder for example scenarios
3. Run verification checklist
4. Check Backend/Frontend logs

---

**AuditMate v1.0.0** - AI-Powered Audit Assistant
