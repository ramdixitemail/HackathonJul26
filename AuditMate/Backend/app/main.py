"""AuditMate FastAPI Backend."""
import sys
from pathlib import Path

# Add AuditMate root to path (Backend/app/main.py -> Backend -> AuditMate)
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from Agents.common import (
    AuditIntake, EvidenceCollectionRequest, QnAQuery, MODE,
    list_evidence_sets, load_evidence_set, save_evidence_set
)
from Agents.audit_intake_agent.agent import AuditIntakeAgent
from Agents.orchestrator.graph import OrchestratorGraph
from Agents.qna_agent.router import route as route_qna
from Agents.graph_agent.agent import GraphAgent

app = FastAPI(title="AuditMate", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
intake_agent = AuditIntakeAgent()
orchestrator = OrchestratorGraph()
graph_agent = GraphAgent()


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": MODE,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AuditMate API", "mode": MODE}


@app.post("/api/audit-intake")
async def audit_intake(request: AuditIntake):
    """Process audit intake."""
    result = intake_agent.intake(request)
    return {
        "audit_id": result["audit_id"],
        "audit_points": [
            {"id": p.id, "text": p.text}
            for p in result["audit_points"]
        ],
        "draft_request": result["draft_request"].model_dump()
    }


@app.post("/api/evidence/collect")
async def evidence_collect(request: EvidenceCollectionRequest):
    """Collect evidence."""
    evidence_set = orchestrator.run(request)
    
    # Save to store
    save_evidence_set(evidence_set)
    
    return evidence_set.model_dump()


@app.get("/api/evidence")
async def list_evidence():
    """List all evidence sets."""
    ids = list_evidence_sets()
    return {"evidence_sets": ids, "count": len(ids)}


@app.get("/api/evidence/{request_id}")
async def get_evidence(request_id: str):
    """Get specific evidence set."""
    evidence_set = load_evidence_set(request_id)
    if not evidence_set:
        raise HTTPException(status_code=404, detail="Evidence set not found")
    return evidence_set.model_dump()


@app.get("/api/evidence/{request_id}/document")
async def get_document(request_id: str):
    """Download evidence document."""
    evidence_set = load_evidence_set(request_id)
    if not evidence_set or not evidence_set.document_path:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return FileResponse(evidence_set.document_path, filename=f"{request_id}.docx")


@app.post("/api/qna")
async def ask_qna(query: QnAQuery):
    """Ask question using Q&A."""
    answer = route_qna(query)
    return answer.model_dump()


@app.get("/api/graph/kpis")
async def get_kpis():
    """Get KPI metrics."""
    kpis = graph_agent.kpis()
    return kpis.model_dump()


@app.post("/api/graph/query")
async def graph_query(question: str = None, filters: dict = None):
    """Query knowledge graph."""
    if not question:
        raise HTTPException(status_code=400, detail="question parameter required")
    
    answer = graph_agent.answer(question, filters)
    return answer.model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
