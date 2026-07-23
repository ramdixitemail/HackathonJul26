import React, { useState, useEffect } from 'react';
import { Screen, EvidenceSet, AuditPoint, QnAAnswer } from './types';
import './styles.css';
import { health } from './api/client';

import AuditIntakeScreen from './screens/AuditIntake';
import EvidenceCollectionScreen from './screens/EvidenceCollection';
import EvidencePreviewScreen from './screens/EvidencePreview';
import AskAuditMateScreen from './screens/AskAuditMate';

function App() {
  const [screen, setScreen] = useState<Screen>('audit');
  const [auditData, setAuditData] = useState<{
    id?: string;
    auditText?: string;
    points?: AuditPoint[];
    request?: any;
  }>({});
  const [evidenceData, setEvidenceData] = useState<EvidenceSet | null>(null);
  const [appMode, setAppMode] = useState<string>('unknown');

  useEffect(() => {
    // Check health on load
    health().then(h => {
      setAppMode(h.mode || 'unknown');
      console.log(`AuditMate running in ${h.mode} mode`);
    }).catch(console.error);
  }, []);

  const handleIntakeComplete = (data: any) => {
    setAuditData(data);
    setScreen('collect');
  };

  const handleCollectComplete = (data: EvidenceSet) => {
    setEvidenceData(data);
    setScreen('preview');
  };

  const handlePreviewToAsk = (data: EvidenceSet) => {
    setEvidenceData(data);
    setScreen('ask');
  };

  return (
    <div className="container">
      <div className="sidebar">
        <h1>AuditMate</h1>
        <div className="nav">
          <div
            className={`nav-item ${screen === 'audit' ? 'active' : ''}`}
            onClick={() => setScreen('audit')}
          >
            1. Audit Intake
          </div>
          <div
            className={`nav-item ${screen === 'collect' ? 'active' : ''}`}
            onClick={() => setScreen('collect')}
          >
            2. Evidence Collection
          </div>
          <div
            className={`nav-item ${screen === 'preview' ? 'active' : ''}`}
            onClick={() => setScreen('preview')}
          >
            3. Evidence Preview
          </div>
          <div
            className={`nav-item ${screen === 'ask' ? 'active' : ''}`}
            onClick={() => setScreen('ask')}
          >
            4. Ask AuditMate
          </div>
        </div>
        <div style={{ marginTop: '40px', fontSize: '12px', opacity: 0.7 }}>
          <p>Mode: <strong>{appMode}</strong></p>
          <p>Version: 1.0.0</p>
        </div>
      </div>

      <div className="main-content">
        <div className="topbar">
          <h1>AuditMate - Full Stack AI Audit Assistant</h1>
          <p>
            {screen === 'audit' && 'Start an audit intake'}
            {screen === 'collect' && 'Configure evidence collection'}
            {screen === 'preview' && 'Review collected evidence'}
            {screen === 'ask' && 'Ask questions using evidence and knowledge graph'}
          </p>
        </div>

        <div className="screen-content">
          {screen === 'audit' && (
            <AuditIntakeScreen onComplete={handleIntakeComplete} />
          )}
          {screen === 'collect' && (
            <EvidenceCollectionScreen
              auditData={auditData}
              onComplete={handleCollectComplete}
            />
          )}
          {screen === 'preview' && (
            <EvidencePreviewScreen
              evidence={evidenceData}
              onAsk={() => handlePreviewToAsk(evidenceData)}
            />
          )}
          {screen === 'ask' && (
            <AskAuditMateScreen evidence={evidenceData} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
