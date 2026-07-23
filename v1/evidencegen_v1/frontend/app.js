const API = "/api";

let TEMPLATES = [];
let CURRENT_TEMPLATE = null;
let LAST_PACK = null;

const VIEW_TITLES = {
  dashboard: "Dashboard",
  tasklist: "Task List",
  newpack: "New Evidence Pack",
  review: "Review & Mapping",
  qa: "Q&A Chat",
  intake: "Audit Intake",
  evidencecollection: "Evidence Collection",
  evidencepreview: "Evidence Preview",
  settings: "Settings",
};

// ---------------- Navigation ----------------

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => showView(btn.dataset.view));
});

function showView(view) {
  document.querySelectorAll(".view").forEach((el) => (el.hidden = true));
  document.getElementById(`view-${view}`).hidden = false;
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  document.getElementById("topbar-title").textContent = VIEW_TITLES[view];

  if (view === "dashboard") loadDashboard();
  if (view === "tasklist") loadTaskList();
  if (view === "review" && LAST_PACK) renderReview(LAST_PACK);
  if (view === "settings") loadSettings();
}

// ---------------- New Evidence Pack form ----------------

async function loadTemplates() {
  const res = await fetch(`${API}/templates`);
  TEMPLATES = await res.json();
  const select = document.getElementById("template-select");
  select.innerHTML = TEMPLATES.map((t) => `<option value="${t.id}">${t.name}</option>`).join("");
  select.addEventListener("change", () => selectTemplate(select.value));
  selectTemplate(TEMPLATES[0].id);
}

const ALL_SOURCES = [
  { key: "repo", label: "Code repo (Bitbucket / GitHub)" },
  { key: "approvals", label: "Approvals / Pipelines" },
  { key: "docs", label: "Document repository (Confluence)" },
  { key: "screenshots", label: "Screenshots (portal)" },
  { key: "tickets", label: "Ticketing (Jira)" },
];

function selectTemplate(templateId) {
  CURRENT_TEMPLATE = TEMPLATES.find((t) => t.id === templateId);
  renderSources();
  renderRequirements();
}

function renderSources() {
  const grid = document.getElementById("sources-grid");
  const defaults = new Set(CURRENT_TEMPLATE.default_sources);
  grid.innerHTML = ALL_SOURCES.map(
    (s) => `
    <label class="source-checkbox">
      <input type="checkbox" value="${s.key}" ${defaults.has(s.key) ? "checked" : ""} />
      ${s.label}
    </label>`
  ).join("");
}

function renderRequirements() {
  const list = document.getElementById("requirements-list");
  list.innerHTML = CURRENT_TEMPLATE.requirements
    .map(
      (r, i) => `
    <div class="requirement-row">
      <span class="req-num">${i + 1}</span> ${r.text}
    </div>`
    )
    .join("");
}

// Collect-by radio toggles the identifier field's label/placeholder
document.getElementById("collect-by-row").addEventListener("change", (e) => {
  const val = e.target.value;
  const label = document.getElementById("identifier-label");
  const input = document.getElementById("identifier-input");
  if (val === "control_id") {
    label.textContent = "Control ID";
    input.placeholder = "CTRL-000045";
  } else if (val === "date_range") {
    label.textContent = "Date range + Repo";
    input.placeholder = "2026-06-01..2026-06-30, payments-service";
  } else {
    label.textContent = "Change ID";
    input.placeholder = "CHG-000123";
  }
});

document.getElementById("cancel-btn").addEventListener("click", () => {
  document.getElementById("identifier-input").value = "";
  document.getElementById("run-status-line").textContent = "";
});

document.getElementById("run-collection-btn").addEventListener("click", runCollection);

async function runCollection() {
  const btn = document.getElementById("run-collection-btn");
  const statusLine = document.getElementById("run-status-line");
  const collectBy = document.querySelector('input[name="collect_by"]:checked').value;
  const identifier = document.getElementById("identifier-input").value.trim();
  const sources = Array.from(document.querySelectorAll("#sources-grid input:checked")).map((i) => i.value);

  if (sources.length === 0) {
    statusLine.textContent = "Select at least one source to collect from.";
    return;
  }

  const body = {
    template_id: CURRENT_TEMPLATE.id,
    collect_by: collectBy,
    sources,
  };
  if (collectBy === "control_id") body.control_id = identifier;
  else if (collectBy === "date_range") body.date_range = identifier;
  else body.change_id = identifier;

  btn.disabled = true;
  btn.textContent = "Running agents…";
  statusLine.textContent = "Contacting agents for each selected source…";

  try {
    const res = await fetch(`${API}/packs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).error || "Request failed");
    const pack = await res.json();
    LAST_PACK = pack;
    statusLine.textContent = "Agent collection complete. Loaded evidence into the review screen.";
    renderReview(pack);
    showView("review");
  } catch (err) {
    statusLine.textContent = `Collection failed: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run Collection";
  }
}

// ---------------- Review & Mapping ----------------

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}

function renderEvidenceDetail(e) {
  if (e.type === "code_snippet") {
    return `<pre class="code-diff">${escapeHtml(e.detail)}</pre>`;
  }
  return `<div>${escapeHtml(e.detail)}</div>`;
}

function statusPillClass(status) {
  if (status === "satisfied") return "status-satisfied";
  if (status === "partial") return "status-partial";
  return "status-missing";
}

function renderReview(pack) {
  document.getElementById("review-empty").hidden = true;
  document.getElementById("review-content").hidden = false;

  document.getElementById("review-meta").innerHTML = `
    <span><strong>Pack:</strong> ${pack.id}</span>
    <span><strong>Template:</strong> ${pack.template_name}</span>
    <span><strong>Identifier:</strong> ${pack.change_id || pack.control_id || pack.date_range || "—"}</span>
    <span><strong>Created:</strong> ${new Date(pack.created_at).toLocaleString()}</span>
    <span><strong>Mapping engine:</strong> ${pack.mapping_engine}</span>
  `;

  document.getElementById("review-summary").textContent = pack.summary;

  document.getElementById("review-requirements").innerHTML = pack.mapping_results
    .map(
      (r) => `
    <div class="req-result">
      <span class="status-pill ${statusPillClass(r.status)}">${r.status}</span>
      <div>
        <div><strong>${r.requirement_text}</strong></div>
        <div class="muted">${r.rationale}</div>
      </div>
    </div>`
    )
    .join("");

  document.getElementById("review-evidence").innerHTML = pack.evidence
    .map(
      (e) => `
    <div class="evidence-item">
      <div class="ev-title">${escapeHtml(e.title)} ${e.is_mock ? '<span class="mock-tag">mock</span>' : '<span class="mock-tag">live</span>'}</div>
      ${renderEvidenceDetail(e)}
      <div class="ev-meta">${e.source_label} · ${e.actor} · ${new Date(e.timestamp).toLocaleString()}</div>
    </div>`
    )
    .join("");

  document.getElementById("review-log").innerHTML = pack.agent_log
    .map(
      (l) => `
    <div class="log-row">
      <span class="${l.status === "ok" ? "log-status-ok" : "log-status-error"}">${l.status.toUpperCase()}</span>
      <span>${l.source}</span> — <span class="muted">${l.detail}</span>
    </div>`
    )
    .join("");
}

// ---------------- Dashboard ----------------

async function loadDashboard() {
  const res = await fetch(`${API}/packs`);
  const packs = await res.json();

  const satisfied = packs.filter((p) => p.mapping_results.every((r) => r.status === "satisfied")).length;
  const needsWork = packs.length - satisfied;

  document.getElementById("dashboard-stats").innerHTML = `
    <div class="stat-box"><div class="stat-num">${packs.length}</div><div class="stat-label">Evidence packs generated</div></div>
    <div class="stat-box"><div class="stat-num">${satisfied}</div><div class="stat-label">Fully satisfied</div></div>
    <div class="stat-box"><div class="stat-num">${needsWork}</div><div class="stat-label">Need follow-up</div></div>
  `;

  document.getElementById("dashboard-recent").innerHTML =
    packs
      .slice(0, 5)
      .map((p) => packRowHtml(p))
      .join("") || `<p class="muted">No evidence packs yet — create one from "New Evidence Pack".</p>`;

  attachPackRowHandlers();
}

function packRowHtml(p) {
  const identifier = p.change_id || p.control_id || p.date_range || "—";
  return `
  <div class="pack-row" data-pack-id="${p.id}">
    <div class="pack-row-title">${identifier} — ${p.template_name}</div>
    <div class="pack-row-sub">${new Date(p.created_at).toLocaleString()} · ${p.evidence.length} evidence item(s)</div>
  </div>`;
}

function attachPackRowHandlers() {
  document.querySelectorAll(".pack-row").forEach((row) => {
    row.addEventListener("click", async () => {
      const res = await fetch(`${API}/packs/${row.dataset.packId}`);
      LAST_PACK = await res.json();
      renderReview(LAST_PACK);
      showView("review");
    });
  });
}

// ---------------- Task List ----------------

async function loadTaskList() {
  const res = await fetch(`${API}/packs`);
  const packs = await res.json();
  const container = document.getElementById("tasklist-table");
  if (packs.length === 0) {
    container.innerHTML = `<p class="muted">No evidence packs yet.</p>`;
    return;
  }
  container.innerHTML = packs.map((p) => packRowHtml(p)).join("");
  attachPackRowHandlers();
}

// ---------------- Q&A Chat ----------------

function appendChatMsg(role, text) {
  const win = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

document.getElementById("chat-send-btn").addEventListener("click", sendChat);
document.getElementById("chat-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});

async function sendChat() {
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question) return;
  appendChatMsg("user", question);
  input.value = "";

  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, pack_id: LAST_PACK ? LAST_PACK.id : null }),
  });
  const data = await res.json();
  appendChatMsg("assistant", data.answer || data.error || "No answer available.");
}

// ---------------- Settings ----------------

async function loadSettings() {
  const res = await fetch(`${API}/status`);
  const status = await res.json();

  const rows = [
    { label: "LLM provider active", on: status.llm_provider !== "offline-rules", value: status.llm_provider },
    { label: "GitHub integration", on: status.integrations.github },
    { label: "Confluence integration", on: status.integrations.confluence },
    { label: "Jira integration", on: status.integrations.jira },
  ];

  document.getElementById("settings-status").innerHTML = rows
    .map(
      (r) => `
    <div class="settings-row">
      <span class="dot ${r.on ? "dot-on" : "dot-off"}"></span>
      <span>${r.label}</span>
      ${r.value ? `<span class="muted">(${r.value})</span>` : r.on ? "" : '<span class="muted">(using mock data)</span>'}
    </div>`
    )
    .join("");

  document.getElementById("env-ref").textContent = `# LLM (pick one — free tiers work great)
GROQ_API_KEY=            # https://console.groq.com — free tier
GROQ_MODEL=llama-3.1-8b-instant
OLLAMA_HOST=             # e.g. http://localhost:11434 for a fully local free LLM
OLLAMA_MODEL=llama3.1

# Real source integrations (optional — mock data is used if unset)
GITHUB_TOKEN=
GITHUB_REPO=org/repo
CONFLUENCE_BASE_URL=
CONFLUENCE_EMAIL=
CONFLUENCE_API_TOKEN=
JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=`;
}

// ---------------- Audit Intake ----------------

let AUDIT_INTAKE_TEXT = "";

const AGENT_LABELS = {
  repo: "GitHub Agent",
  docs: "Document Repo Agent",
  screenshots: "Portal Screenshot Agent",
};
const AGENT_ORDER = ["repo", "docs", "screenshots"];

document.getElementById("detect-points-btn").addEventListener("click", detectAuditPoints);

async function detectAuditPoints() {
  const text = document.getElementById("intake-text").value.trim();
  const statusLine = document.getElementById("intake-status-line");
  if (!text) {
    statusLine.textContent = "Paste some audit text first.";
    return;
  }
  AUDIT_INTAKE_TEXT = text;
  statusLine.textContent = "Analyzing audit text…";

  try {
    const res = await fetch(`${API}/audit-intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audit_text: text }),
    });
    const data = await res.json();
    statusLine.textContent = `Detected ${data.detected_points.length} audit point(s) (engine: ${data.engine}).`;

    document.getElementById("detected-points-list").innerHTML = data.detected_points
      .map((p, i) => `<div class="requirement-row"><span class="req-num">${i + 1}</span> ${escapeHtml(p)}</div>`)
      .join("");

    document.getElementById("intake-repo-input").value = data.suggested_repo || "";
    document.getElementById("intake-goals-input").value = (data.suggested_goals || []).join("\n");

    document.getElementById("intake-results").hidden = false;
  } catch (err) {
    statusLine.textContent = `Could not analyze audit text: ${err.message}`;
  }
}

document.getElementById("generate-open-btn").addEventListener("click", () => {
  const repo = document.getElementById("intake-repo-input").value.trim();
  const goalsText = document.getElementById("intake-goals-input").value;
  const goals = goalsText.split("\n").map((g) => g.trim()).filter(Boolean);
  const checkedAgents = Array.from(document.querySelectorAll("#intake-agents-grid input:checked")).map((i) => i.value);

  document.getElementById("ec-template-name").value = "Custom — Audit Intake" + (repo ? ` (${repo})` : "");
  document.getElementById("ec-evidence-needed").value = goals.join("\n");

  document.querySelectorAll("#ec-agents-grid input").forEach((cb) => {
    cb.checked = checkedAgents.includes(cb.value);
  });

  EC_SUGGESTED_REPO = repo;
  renderOrchestratorPlan();
  showView("evidencecollection");
});

// ---------------- Evidence Collection ----------------

let EC_SUGGESTED_REPO = "";

document.getElementById("ec-agents-grid").addEventListener("change", renderOrchestratorPlan);

function renderOrchestratorPlan() {
  const checked = Array.from(document.querySelectorAll("#ec-agents-grid input:checked")).map((i) => i.value);
  const steps = AGENT_ORDER.filter((key) => checked.includes(key)).map((key) => AGENT_LABELS[key]);
  steps.push("Store & index evidences");
  document.getElementById("orchestrator-plan").textContent = steps.join("  →  ");
}

document.getElementById("run-evidence-collection-btn").addEventListener("click", runEvidenceCollection);

async function runEvidenceCollection() {
  const btn = document.getElementById("run-evidence-collection-btn");
  const statusLine = document.getElementById("ec-status-line");
  const evidenceNeeded = document.getElementById("ec-evidence-needed").value
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  const sources = Array.from(document.querySelectorAll("#ec-agents-grid input:checked")).map((i) => i.value);

  if (sources.length === 0) {
    statusLine.textContent = "Select at least one agent to run.";
    return;
  }
  if (evidenceNeeded.length === 0) {
    statusLine.textContent = "Describe what evidence you need first.";
    return;
  }

  const identifier = EC_SUGGESTED_REPO && EC_SUGGESTED_REPO !== "your-org/your-repo"
    ? EC_SUGGESTED_REPO
    : `AUDIT-${Date.now()}`;

  const body = {
    template_id: "custom-audit-intake",
    custom_requirements: evidenceNeeded,
    custom_template_name: document.getElementById("ec-template-name").value || "Custom — Audit Intake",
    collect_by: "change_id",
    change_id: identifier,
    sources,
    audit_text: AUDIT_INTAKE_TEXT,
  };

  btn.disabled = true;
  btn.textContent = "Running orchestrator…";
  statusLine.textContent = "Running agents in orchestrator order…";

  try {
    const res = await fetch(`${API}/packs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).error || "Request failed");
    const pack = await res.json();
    LAST_PACK = pack;
    statusLine.textContent = "Evidence collection complete.";
    renderEvidencePreview(pack);
    showView("evidencepreview");
  } catch (err) {
    statusLine.textContent = `Collection failed: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run Evidence Collection";
  }
}

// ---------------- Evidence Preview ----------------

function renderEvidencePreview(pack) {
  document.getElementById("preview-meta").innerHTML = `
    <span><strong>Pack:</strong> ${pack.id}</span>
    <span><strong>Template:</strong> ${escapeHtml(pack.template_name)}</span>
    <span><strong>Identifier:</strong> ${pack.change_id || pack.control_id || "—"}</span>
    <span><strong>Created:</strong> ${new Date(pack.created_at).toLocaleString()}</span>
  `;

  document.getElementById("preview-summary").textContent = pack.summary;

  document.getElementById("preview-requirements").innerHTML = pack.mapping_results
    .map(
      (r) => `
    <div class="req-result">
      <span class="status-pill ${statusPillClass(r.status)}">${r.status}</span>
      <div>
        <div><strong>${escapeHtml(r.requirement_text)}</strong></div>
        <div class="muted">${escapeHtml(r.rationale)}</div>
      </div>
    </div>`
    )
    .join("");

  document.getElementById("preview-evidence").innerHTML = pack.evidence
    .map((e) => renderPreviewEvidenceItem(e))
    .join("");

  document.getElementById("preview-log").innerHTML = pack.agent_log
    .map(
      (l) => `
    <div class="log-row">
      <span class="${l.status === "ok" ? "log-status-ok" : "log-status-error"}">${l.status.toUpperCase()}</span>
      <span>${l.source}</span> — <span class="muted">${escapeHtml(l.detail)}</span>
    </div>`
    )
    .join("");
}

function renderPreviewEvidenceItem(e) {
  const mockTag = e.is_mock ? '<span class="mock-tag">mock</span>' : '<span class="mock-tag">live</span>';
  let mediaHtml = "";
  if (e.source === "screenshots" || e.type === "screenshot") {
    mediaHtml = `
      <div class="screenshot-frame">
        <img src="${e.url}" alt="${escapeHtml(e.title)}"
             onerror="this.onerror=null; this.replaceWith(Object.assign(document.createElement('div'), {className:'screenshot-fallback', textContent:'📷 Screenshot preview unavailable (mock/portal URL) — ${escapeHtml(e.url)}'}));" />
      </div>`;
  }
  return `
    <div class="evidence-item">
      <div class="ev-title">${escapeHtml(e.title)} ${mockTag}</div>
      ${mediaHtml}
      ${renderEvidenceDetail(e)}
      <div class="ev-meta">${e.source_label} · ${e.actor} · ${new Date(e.timestamp).toLocaleString()}</div>
    </div>`;
}

// ---------------- Init ----------------

loadTemplates();
renderOrchestratorPlan();
