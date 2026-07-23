import { AuditPoint, EvidenceSet, QnAAnswer, KPIs } from '../types';

const API_BASE = '/api';

export const health = async () => {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
};

export const auditIntake = async (auditId: string, auditText: string) => {
  const res = await fetch(`${API_BASE}/audit-intake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ audit_id: auditId, audit_text: auditText })
  });
  return res.json();
};

export const collectEvidence = async (request: any): Promise<EvidenceSet> => {
  const res = await fetch(`${API_BASE}/evidence/collect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return res.json();
};

export const getEvidence = async (requestId: string): Promise<EvidenceSet> => {
  const res = await fetch(`${API_BASE}/evidence/${requestId}`);
  return res.json();
};

export const listEvidence = async () => {
  const res = await fetch(`${API_BASE}/evidence`);
  return res.json();
};

export const documentUrl = (requestId: string) => {
  return `${API_BASE}/evidence/${requestId}/document`;
};

export const ask = async (question: string, scope: string = 'auto', evidenceId?: string): Promise<QnAAnswer> => {
  const res = await fetch(`${API_BASE}/qna`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      scope,
      evidence_id: evidenceId
    })
  });
  return res.json();
};

export const kpis = async (): Promise<KPIs> => {
  const res = await fetch(`${API_BASE}/graph/kpis`);
  return res.json();
};
