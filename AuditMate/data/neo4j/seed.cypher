"""Neo4j seed data from graph.json."""

// Create Applications
UNWIND [
  {application_id: "APP-001", name: "Payments Service", tier: "critical", owner: "M.Singh"},
  {application_id: "APP-002", name: "Settlement Engine", tier: "critical", owner: "A.Rao"},
  {application_id: "APP-003", name: "Reporting Batch", tier: "high", owner: "S.Kaur"},
  {application_id: "APP-004", name: "Client Portal", tier: "high", owner: "J.Doe"}
] AS app
MERGE (a:Application {application_id: app.application_id})
SET a.name = app.name, a.tier = app.tier, a.owner = app.owner;

// Create SIIs
UNWIND [
  {id: "SII-2041", application_id: "APP-001", title: "Missing Four-Eyes Approval on Production Changes", severity: "high", status: "overdue", due_date: "2026-06-30"},
  {id: "SII-2088", application_id: "APP-002", title: "Inadequate Database Link Segregation", severity: "high", status: "overdue", due_date: "2026-05-31"},
  {id: "SII-2102", application_id: "APP-001", title: "Incomplete Transaction Control Implementation", severity: "high", status: "at_risk", due_date: "2026-07-15"},
  {id: "SII-2156", application_id: "APP-003", title: "Batch Job Scheduling Risk", severity: "medium", status: "open", due_date: "2026-08-31"},
  {id: "SII-2201", application_id: "APP-004", title: "Session Management Gap", severity: "low", status: "open", due_date: "2026-09-30"}
] AS s
MERGE (sii:SII {id: s.id})
SET sii.title = s.title, sii.severity = s.severity, sii.status = s.status, sii.due_date = s.due_date
WITH sii, s
MATCH (a:Application {application_id: s.application_id})
MERGE (a)-[:HAS_SII]->(sii);

// Create Vulnerabilities
UNWIND [
  {id: "VUL-001", application_id: "APP-002", title: "Log4j RCE Vulnerability", severity: "critical", status: "open", component: "logging-library", found_at: "2026-04-15"},
  {id: "VUL-002", application_id: "APP-001", title: "SQL Injection in Reports", severity: "high", status: "in_remediation", component: "reporting-module", found_at: "2026-05-01"},
  {id: "VUL-003", application_id: "APP-003", title: "Cleartext Password Storage", severity: "critical", status: "open", component: "config-module", found_at: "2026-06-10"},
  {id: "VUL-004", application_id: "APP-004", title: "CSRF Token Validation", severity: "medium", status: "open", component: "web-framework", found_at: "2026-06-20"},
  {id: "VUL-005", application_id: "APP-001", title: "Hardcoded Credentials", severity: "high", status: "open", component: "database-connector", found_at: "2026-06-25"}
] AS v
MERGE (vuln:Vulnerability {id: v.id})
SET vuln.title = v.title, vuln.severity = v.severity, vuln.status = v.status, vuln.component = v.component, vuln.found_at = v.found_at
WITH vuln, v
MATCH (a:Application {application_id: v.application_id})
MERGE (a)-[:HAS_VULNERABILITY]->(vuln);

// Create Remediation Plans
UNWIND [
  {id: "PLN-001", target_id: "SII-2041", target_type: "sii", status: "in_progress", pct_complete: 60, eta: "2026-08-05", owner: "M.Singh"},
  {id: "PLN-002", target_id: "SII-2088", target_type: "sii", status: "pending", pct_complete: 0, eta: "2026-07-30", owner: "A.Rao"},
  {id: "PLN-003", target_id: "VUL-001", target_type: "vulnerability", status: "in_progress", pct_complete: 45, eta: "2026-07-31", owner: "A.Rao"},
  {id: "PLN-004", target_id: "VUL-003", target_type: "vulnerability", status: "blocked", pct_complete: 0, eta: "2026-08-15", owner: "S.Kaur"},
  {id: "PLN-005", target_id: "SII-2102", target_type: "sii", status: "in_progress", pct_complete: 75, eta: "2026-07-20", owner: "M.Singh"}
] AS plan
MERGE (p:RemediationPlan {id: plan.id})
SET p.status = plan.status, p.pct_complete = plan.pct_complete, p.eta = plan.eta, p.owner = plan.owner;
