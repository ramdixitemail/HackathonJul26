import React, { useState, useEffect } from 'react';
import { EvidenceSet, QnAAnswer } from '../types';
import { ask, kpis } from '../api/client';

interface Props {
  evidence: EvidenceSet | null;
}

export default function AskAuditMateScreen({ evidence }: Props) {
  const [kpiData, setKpiData] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [scope, setScope] = useState('auto');

  useEffect(() => {
    // Load KPIs on mount
    kpis().then(setKpiData).catch(console.error);
  }, []);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setLoading(true);

    try {
      const answer = await ask(input, scope, evidence?.request_id);
      setMessages(prev => [...prev, { role: 'bot', content: answer.answer, citations: answer.citations, routed_to: answer.routed_to }]);
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: 'bot', content: 'Error processing question' }]);
    } finally {
      setInput('');
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Ask AuditMate</h2>
        <p>Ask questions about your audit evidence and knowledge graph</p>
      </div>

      {kpiData && (
        <>
          <h3>KPI Dashboard</h3>
          <div className="kpi-grid">
            <div className="kpi-tile">
              <div className="kpi-value">{kpiData.open_vulnerabilities}</div>
              <div className="kpi-label">Open Vulnerabilities</div>
            </div>
            <div className="kpi-tile">
              <div className="kpi-value">{kpiData.high_severity_siis}</div>
              <div className="kpi-label">High Severity SIIs</div>
            </div>
            <div className="kpi-tile">
              <div className="kpi-value">{kpiData.audit_items_due_30d}</div>
              <div className="kpi-label">Audit Items Due 30d</div>
            </div>
            <div className="kpi-tile">
              <div className="kpi-value">{kpiData.remediations_on_track_pct}%</div>
              <div className="kpi-label">Remediations On Track</div>
            </div>
          </div>
        </>
      )}

      <h3>Query Scope</h3>
      <div style={{ marginBottom: '15px' }}>
        <label>
          <input type="radio" value="auto" checked={scope === 'auto'} onChange={e => setScope(e.target.value)} /> Auto
        </label>
        <label style={{ marginLeft: '15px' }}>
          <input type="radio" value="evidence" checked={scope === 'evidence'} onChange={e => setScope(e.target.value)} /> Evidence
        </label>
        <label style={{ marginLeft: '15px' }}>
          <input type="radio" value="graph" checked={scope === 'graph'} onChange={e => setScope(e.target.value)} /> Knowledge Graph
        </label>
      </div>

      <div className="chat-container">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.role === 'user' ? 'user' : msg.routed_to === 'graph' ? 'kg' : 'bot'}`}>
              <p>{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div>
                  {msg.citations.map((c: any, i: number) => (
                    <span key={i} className="citation-chip">{c.label}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <form onSubmit={handleAsk} className="chat-input">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
          />
          <button type="submit" className="button button-primary" disabled={loading}>
            {loading ? <span className="spinner"></span> : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}
