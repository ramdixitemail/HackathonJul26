import React from 'react';
import { EvidenceSet, EvidenceItem } from '../types';
import { documentUrl } from '../api/client';

interface Props {
  evidence: EvidenceSet | null;
  onAsk: () => void;
}

export default function EvidencePreviewScreen({ evidence, onAsk }: Props) {
  if (!evidence) {
    return <div className="card"><p>No evidence collected yet</p></div>;
  }

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2>Evidence Preview</h2>
          <p>Request ID: {evidence.request_id}</p>
        </div>

        <div>
          <h3>Summary</h3>
          <div className="kpi-grid">
            <div className="kpi-tile">
              <div className="kpi-value">{evidence.items.length}</div>
              <div className="kpi-label">Items Collected</div>
            </div>
            {Object.entries(evidence.counts).map(([source, count]) => (
              <div key={source} className="kpi-tile">
                <div className="kpi-value">{count}</div>
                <div className="kpi-label">{source}</div>
              </div>
            ))}
          </div>

          {evidence.narrative && (
            <>
              <h3>Narrative</h3>
              <p>{evidence.narrative}</p>
            </>
          )}

          <h3>Evidence Items</h3>
          <div className="evidence-grid">
            {evidence.items.map((item: EvidenceItem) => (
              <div key={item.id} className="evidence-card">
                <div className="evidence-card-header">
                  {item.id}
                  <span className="evidence-card-type">{item.type}</span>
                </div>
                <p><strong>{item.summary}</strong></p>
                {item.checks && (
                  <div>
                    {Object.entries(item.checks).map(([check, result]) => (
                      <span key={check} className={`chip ${result === 'PASS' ? 'success' : 'danger'}`}>
                        {check}: {result}
                      </span>
                    ))}
                  </div>
                )}
                {item.content && <p style={{ fontSize: '12px', color: '#666' }}>{item.content.substring(0, 100)}...</p>}
              </div>
            ))}
          </div>

          {evidence.document_path && (
            <div style={{ marginTop: '20px' }}>
              <h3>Download</h3>
              <a href={documentUrl(evidence.request_id)} download className="button button-primary">
                Download DOCX Report
              </a>
            </div>
          )}

          <button className="button button-primary" onClick={onAsk} style={{ marginTop: '20px' }}>
            Use in Q&A
          </button>
        </div>
      </div>
    </div>
  );
}
