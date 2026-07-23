import React, { useState } from 'react';
import { auditIntake } from '../api/client';

interface Props {
  onComplete: (data: any) => void;
}

export default function AuditIntakeScreen({ onComplete }: Props) {
  const [auditId, setAuditId] = useState('AUD-2026-0142');
  const [auditText, setAuditText] = useState(
    'Segregation of duties for prod changes? Tests before release? Who approved each deployment? Data only via database link? Trace the CHG-000123 change flow. Check JIRA-4521 for code snippets. Show design documentation. Capture portal compliance screenshot.'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyse = async () => {
    setLoading(true);
    try {
      const res = await auditIntake(auditId, auditText);
      setResult(res);
    } catch (e) {
      console.error(e);
      alert('Error analyzing audit');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = () => {
    if (result && result.draft_request) {
      onComplete({
        id: result.audit_id,
        auditText,
        points: result.audit_points,
        request: result.draft_request
      });
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Audit Intake</h2>
        <p>Start a new audit by providing the audit ID and text describing what evidence you need.</p>
      </div>

      <div>
        <label>Audit ID</label>
        <input
          type="text"
          value={auditId}
          onChange={e => setAuditId(e.target.value)}
          placeholder="AUD-2026-0142"
        />

        <label>Audit Text</label>
        <textarea
          value={auditText}
          onChange={e => setAuditText(e.target.value)}
          placeholder="Describe what evidence you need..."
        />

        <button className="button button-primary" onClick={handleAnalyse} disabled={loading}>
          {loading ? <span className="spinner"></span> : 'Analyse'}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3>Extracted Audit Points</h3>
          {result.audit_points && result.audit_points.map((point: any) => (
            <div key={point.id} className="chip" style={{ display: 'block', margin: '5px 0' }}>
              <strong>{point.id}:</strong> {point.text}
            </div>
          ))}

          <h3 style={{ marginTop: '20px' }}>Evidence Goals</h3>
          {result.draft_request.evidence_goals && result.draft_request.evidence_goals.map((goal: string) => (
            <span key={goal} className="chip">{goal}</span>
          ))}

          <button className="button button-primary" onClick={handleGenerate} style={{ marginTop: '20px' }}>
            Generate Evidence Collection
          </button>
        </div>
      )}
    </div>
  );
}
