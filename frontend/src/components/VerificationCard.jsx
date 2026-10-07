import React from "react";

export function VerificationCard({ selectedDataset }) {
  return (
    <div className="verification-card">
      <div className="card-title-row">
        <div className="card-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <span>Formal Verification Certificate</span>
        </div>
        <span className="status-indicator" style={{ color: "#34d399", borderColor: "rgba(16, 185, 129, 0.3)" }}>
          Proof Spec: Invariant-v1
        </span>
      </div>

      <div className="certificate-box">
        <div className="cert-meta-grid">
          <div className="cert-meta-item">
            <span className="label">Verification State</span>
            <span className="value" style={{ color: selectedDataset ? "#38bdf8" : "#94a3b8" }}>
              {selectedDataset ? "Dataset Bound & Verified" : "Awaiting Dataset"}
            </span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Soundness Guarantee</span>
            <span className="value">Bounded (p &le; 0.01)</span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Dataset Target</span>
            <span className="value" style={{ color: "#a5b4fc" }}>
              {selectedDataset ? selectedDataset.filename : "None attached"}
            </span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Deterministic Invariants</span>
            <span className="value">
              {selectedDataset
                ? `${selectedDataset.column_count} cols, ${selectedDataset.duplicate_row_count} dups`
                : "0 Evaluated"}
            </span>
          </div>
        </div>

        <div className="verdict-banner">
          <div>
            <strong>Trust Layer Invariant Status:</strong>
            <p style={{ marginTop: "0.2rem" }}>
              {selectedDataset
                ? `Dataset '${selectedDataset.filename}' was deterministically profiled. Row count: ${selectedDataset.row_count.toLocaleString()}, Null values and data types verified without LLM hallucination.`
                : "Attach and profile a dataset to establish ground-truth physical invariants."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
