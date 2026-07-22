import os
import uuid
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory

from templates_config import CONTROL_TEMPLATES, SOURCE_LABELS, get_template
from agents import run_agents
from llm import llm_client
from llm.mapping import map_evidence_to_requirements, summarize_pack
from llm.qa import answer_question
import storage

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


# ---------- Frontend ----------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# ---------- API: templates ----------

@app.route("/api/templates")
def api_templates():
    return jsonify(CONTROL_TEMPLATES)


# ---------- API: system status (for Settings page) ----------

@app.route("/api/status")
def api_status():
    def configured(*keys):
        return all(os.environ.get(k) for k in keys)

    return jsonify({
        "llm_provider": llm_client.active_provider(),
        "integrations": {
            "github": configured("GITHUB_TOKEN", "GITHUB_REPO"),
            "confluence": configured("CONFLUENCE_BASE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"),
            "jira": configured("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"),
        },
    })


# ---------- API: evidence packs ----------

@app.route("/api/packs", methods=["GET"])
def api_list_packs():
    return jsonify(storage.list_packs())


@app.route("/api/packs/<pack_id>", methods=["GET"])
def api_get_pack(pack_id):
    pack = storage.get_pack(pack_id)
    if not pack:
        return jsonify({"error": "not found"}), 404
    return jsonify(pack)


@app.route("/api/packs", methods=["POST"])
def api_create_pack():
    body = request.get_json(force=True) or {}
    template_id = body.get("template_id")
    template = get_template(template_id)
    if not template:
        return jsonify({"error": f"unknown template_id '{template_id}'"}), 400

    collect_by = body.get("collect_by", "change_id")
    change_id = body.get("change_id")
    control_id = body.get("control_id")
    date_range = body.get("date_range")
    sources = body.get("sources") or template["default_sources"]

    evidence, agent_log = run_agents(sources, change_id=change_id, control_id=control_id)
    results, mapping_engine = map_evidence_to_requirements(evidence, template["requirements"])
    summary, summary_engine = summarize_pack(evidence, template["requirements"], results)

    # attach requirement text onto results for display convenience
    req_by_id = {r["id"]: r["text"] for r in template["requirements"]}
    for r in results:
        r["requirement_text"] = req_by_id.get(r["requirement_id"], r["requirement_id"])

    pack_id = f"pack-{uuid.uuid4().hex[:8]}"
    pack = {
        "id": pack_id,
        "template_id": template_id,
        "template_name": template["name"],
        "collect_by": collect_by,
        "change_id": change_id,
        "control_id": control_id,
        "date_range": date_range,
        "sources": sources,
        "source_labels": [SOURCE_LABELS.get(s, s) for s in sources],
        "status": "collected",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "evidence": evidence,
        "agent_log": agent_log,
        "mapping_results": results,
        "mapping_engine": mapping_engine,
        "summary": summary,
        "summary_engine": summary_engine,
    }
    storage.save_pack(pack)
    return jsonify(pack), 201


@app.route("/api/packs/<pack_id>", methods=["DELETE"])
def api_delete_pack(pack_id):
    storage.delete_pack(pack_id)
    return jsonify({"deleted": pack_id})


# ---------- API: Q&A chat over a pack ----------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json(force=True) or {}
    question = body.get("question", "").strip()
    pack_id = body.get("pack_id")
    if not question:
        return jsonify({"error": "question is required"}), 400

    pack = storage.get_pack(pack_id) if pack_id else None
    if not pack:
        packs = storage.list_packs()
        pack = packs[0] if packs else {"evidence": [], "mapping_results": []}

    answer, engine = answer_question(question, pack)
    return jsonify({"answer": answer, "engine": engine, "pack_id": pack.get("id")})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
