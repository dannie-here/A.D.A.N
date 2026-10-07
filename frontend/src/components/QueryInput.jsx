import React, { useState } from "react";

export function QueryInput() {
  const [query, setQuery] = useState(
    "Verify whether the treatment group shows a statistically significant lift (p < 0.01) with bounded variance."
  );
  const [selectedMode, setSelectedMode] = useState("Hypothesis Verification");
  const [showNotice, setShowNotice] = useState(false);

  const sampleChips = [
    "Hypothesis Verification",
    "Invariant Bounds Audit",
    "Causal Impact Proof",
    "Data Integrity Check",
  ];

  const handleAnalyzeClick = () => {
    setShowNotice(true);
    setTimeout(() => {
      setShowNotice(false);
    }, 4500);
  };

  return (
    <section className="investigation-panel">
      <div className="panel-header-row">
        <div className="panel-title">
          <span>Investigation Hypothesis / Query</span>
        </div>
        <div className="query-chips">
          {sampleChips.map((chip) => (
            <button
              key={chip}
              type="button"
              className={`query-chip ${selectedMode === chip ? "active" : ""}`}
              onClick={() => setSelectedMode(chip)}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      <div className="investigation-input-wrapper">
        <textarea
          className="investigation-textarea"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="State your analytical query or mathematical invariant to verify against the dataset..."
          rows={3}
        />
      </div>

      <div className="input-action-bar">
        <span className="input-hint">
          Deterministic execution &bull; Formal invariant checking &bull; Zero hallucinated findings
        </span>
        <button
          type="button"
          className="analyze-button"
          onClick={handleAnalyzeClick}
          title="Analysis execution will be active in later phases"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Run Proof-Carrying Analysis
        </button>
      </div>

      {showNotice && (
        <div className="phase-notice-modal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>
            <strong>Phase 1 Notice:</strong> The analysis pipeline is deliberately non-functional in this foundation phase.
            Agent synthesis, sandbox execution, and proof generation will be wired up in subsequent phases.
          </span>
        </div>
      )}
    </section>
  );
}
