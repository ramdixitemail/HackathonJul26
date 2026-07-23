import React, { useEffect, useState } from 'react';
import { collectEvidence } from '../api/client';

interface Props {
  auditData: any;
  onComplete: (data: any) => void;
}

export default function EvidenceCollectionScreen({ auditData, onComplete }: Props) {
  const [loading, setLoading] = useState(false);
  const [enableGitHub, setEnableGitHub] = useState(true);
  const [enableDocRepo, setEnableDocRepo] = useState(true);
  const [enablePortal, setEnablePortal] = useState(true);
  const [evidencePrompt, setEvidencePrompt] = useState('');

  useEffect(() => {
    const fallbackInstruction = auditData?.request?.instruction || '';
    setEvidencePrompt(auditData?.auditText || fallbackInstruction);
  }, [auditData]);

  const handleRun = async () => {
    setLoading(true);
    try {
      const request = {
        ...(auditData.request || {}),
        instruction: evidencePrompt,
      };
      request.agents = {
        github: { enabled: enableGitHub },
        doc_repo: { enabled: enableDocRepo },
        portal: { enabled: enablePortal }
      };

      const res = await collectEvidence(request);
      onComplete(res);
    } catch (e) {
      console.error(e);
      alert('Error collecting evidence');
    } finally {
      setLoading(false);
    }
  };

  const toggleAgent = (agent: string, enabled: boolean) => {
    switch (agent) {
      case 'github':
        setEnableGitHub(enabled);
        break;
      case 'doc_repo':
        setEnableDocRepo(enabled);
        break;
      case 'portal':
        setEnablePortal(enabled);
        break;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Evidence Collection Configuration</h2>
        <p>Select which agents should collect evidence</p>
      </div>

      <div>
        <label>
          What evidence do you need?
          <span className="label-hint"> - edit before running</span>
        </label>
        <textarea
          value={evidencePrompt}
          onChange={e => setEvidencePrompt(e.target.value)}
          placeholder="Describe what evidence should be collected..."
        />

        <h3>Collection Agents</h3>

        <div className="agent-card">
          <div>
            <strong>GitHub Agent</strong>
            <p>Collects PRs, approvals, code flow, and change history</p>
          </div>
          <div
            className={`agent-card-toggle ${enableGitHub ? 'enabled' : ''}`}
            onClick={() => toggleAgent('github', !enableGitHub)}
          >
            <div className="agent-card-toggle-dot"></div>
          </div>
        </div>

        <div className="agent-card">
          <div>
            <strong>Document Repository Agent</strong>
            <p>Collects design documents, runbooks, and guides</p>
          </div>
          <div
            className={`agent-card-toggle ${enableDocRepo ? 'enabled' : ''}`}
            onClick={() => toggleAgent('doc_repo', !enableDocRepo)}
          >
            <div className="agent-card-toggle-dot"></div>
          </div>
        </div>

        <div className="agent-card">
          <div>
            <strong>Portal Agent</strong>
            <p>Captures compliance portal screenshots</p>
          </div>
          <div
            className={`agent-card-toggle ${enablePortal ? 'enabled' : ''}`}
            onClick={() => toggleAgent('portal', !enablePortal)}
          >
            <div className="agent-card-toggle-dot"></div>
          </div>
        </div>

        <button className="button button-primary" onClick={handleRun} disabled={loading} style={{ marginTop: '20px' }}>
          {loading ? <span className="spinner"></span> : 'Run Collection'}
        </button>
      </div>
    </div>
  );
}
