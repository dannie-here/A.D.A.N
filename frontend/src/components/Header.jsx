import React from "react";

export function Header({ backendHealth, selectedDataset }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo-mark">A</div>
        <div className="brand-info">
          <h1>
            <span className="acronym">A.D.A.N.</span>
            <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 400 }}>|</span>
            <span style={{ fontSize: "0.85rem", color: "#94a3b8", fontWeight: 500 }}>
              AI Data Analysis &amp; Verification Network
            </span>
          </h1>
          <p>Autonomous Proof-Carrying Analytics Engine • Formal Invariant Verification</p>
        </div>
      </div>

      <div className="header-badges">
        <span className="badge badge-track" title="Smart India Hackathon Problem Statement 08">
          PS08: Proof-Carrying Data Analyst
        </span>
        <span className="badge badge-phase">
          Phase 3: Question Answerability
        </span>
        {selectedDataset && (
          <span
            className="badge"
            style={{
              backgroundColor: "rgba(14, 165, 233, 0.12)",
              color: "#38bdf8",
              borderColor: "rgba(14, 165, 233, 0.3)",
            }}
            title={`Active dataset: ${selectedDataset.filename}`}
          >
            Data: {selectedDataset.filename}
          </span>
        )}
        <span className="badge badge-health">
          <span className="pulse-dot"></span>
          {backendHealth ? "Backend Healthy (200 OK)" : "Engine Ready"}
        </span>
      </div>
    </header>
  );
}
