import React, { useState } from "react";

export function QueryInput({ selectedDataset }) {
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
    }, 5000);
  };

  return (
    <section className="investigation-panel">
      <div className="panel-header-row">
        <div className="panel-title">
          <span>Investigation Hypothesis / Query</span>
          {selectedDataset && (
            <span
              style={{
                fontSize: "0.72rem",
                color: "#38bdf8",
                fontWeight: 500,
                fontFamily: "var(--font-mono)",
                background: "rgba(14, 165, 233, 0.1)",
                padding: "0.15rem 0.45rem",
                borderRadius: "4px",
                border: "1px solid rgba(14, 165, 233, 0.25)",
              }}
            >
              Target: {selectedDataset.filename} ({selectedDataset.row_count.toLocaleString()} rows, {selectedDataset.column_count} cols)
            </span>
          )}
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
          placeholder={
            selectedDataset
              ? `State your analytical query or invariant to verify against '${selectedDataset.filename}'...`
              : "State your analytical query or mathematical invariant to verify against the dataset..."
          }
          rows={3}
        />
      </div>

      <div className="input-action-bar">
        <span className="input-hint">
          {selectedDataset
            ? "Deterministic profile established • Invariant bounds verified • Ready for Phase 3 pipeline"
            : "No dataset loaded. Upload and profile a dataset via the sidebar first."}
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
            <strong>Phase 2 Status:</strong> Dataset upload and deterministic profiling are complete.
            The analysis pipeline (AI question answering, code synthesis, sandbox execution, and formal proof generation)
            will be wired up in subsequent phases.
          </span>
        </div>
      )}
    </section>
  );
}
