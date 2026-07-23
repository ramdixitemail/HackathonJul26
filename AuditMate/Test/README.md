# Test Directory - Synthetic Audit Data

This directory contains sample data for testing the AuditMate system in mock mode.

## Structure

- **audit_samples/** - Sample audit requests
- **github_repo_sample/** - Mock GitHub repository with change history
- **documents/** - Reference documents (design docs, runbooks)
- **portal_screenshots/** - Compliance portal screenshots (HTML)

## Key Scenarios

### Scenario 1: Transaction Load Audit (AUD-2026-0142)

Audits the CHG-000123 change for transaction loading via database link:

- **Change**: CHG-000123 - Secure transaction load with dbLink
- **JIRA**: JIRA-4521 - Database link integration
- **PR**: #141 - Implementation (approvers: a_rao, s_kaur; merged 2026-03-20)
- **Application**: APP-001 (Payments Service)

Evidence collected:
- PR #141 with four-eyes approval
- Code flow: Control-M → Shell → PL/SQL → dbLink → COMMIT/ROLLBACK
- Design documentation from Test/documents/
- Portal compliance screenshot

## Data References

All synthetic data is defined in:
- `data/graph.json` - Knowledge graph (applications, SIIs, vulnerabilities)
- Test/github_repo_sample/git_meta.json - Change history

## Using Mock Mode

```bash
export AUDITMATE_MODE=mock
export GITHUB_SOURCE=fixtures
python -m Agents.orchestrator.run "Trace CHG-000123..."
```

All operations complete offline with deterministic results.
