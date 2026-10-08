import React from "react";

export function QuestionAnalysisCard({ analysis, onClear }) {
  if (!analysis) return null;

  const getStatusClass = (status) => {
    switch (status) {
      case "ANSWERABLE":
        return "status-answerable";
      case "CANNOT_DETERMINE":
        return "status-cannot-determine";
      case "NEEDS_CLARIFICATION":
        return "status-needs-clarification";
      default:
        return "";
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "ANSWERABLE":
        return "ANSWERABLE";
      case "CANNOT_DETERMINE":
        return "CANNOT DETERMINE";
      case "NEEDS_CLARIFICATION":
        return "NEEDS CLARIFICATION";
      default:
        return status;
    }
  };

  const { status, reason, evidence, interpretation, suggested_next_step } = analysis;

  return (
    <section className="analysis-result-panel">
      <div className="analysis-header-row">
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <span className={`status-badge-lg ${getStatusClass(status)}`}>
            <span
              className="pulse-dot"
              style={{
                width: "8px",
                height: "8px",
                backgroundColor: "currentColor",
              }}
            ></span>
            {getStatusLabel(status)}
          </span>
          <span style={{ fontSize: "0.74rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            [Phase 3 Decision]
          </span>
        </div>
        {onClear && (
          <button
            type="button"
            className="reset-dataset-btn"
            onClick={onClear}
            title="Dismiss analysis result"
          >
            Clear Result
          </button>
        )}
      </div>

      <div className="analysis-reason-box">
        <strong>Decision Rationale:</strong>
        <p style={{ marginTop: "0.25rem" }}>{reason}</p>
      </div>

      <div className="analysis-evidence-grid">
        {/* Relevant Columns */}
        <div className="evidence-block">
          <span className="evidence-block-title">Identified Relevant Columns</span>
          {evidence && evidence.relevant_columns && evidence.relevant_columns.length > 0 ? (
            <div className="pill-list">
              {evidence.relevant_columns.map((col) => (
                <span key={col} className="evidence-pill">
                  {col}
                </span>
              ))}
            </div>
          ) : (
            <span style={{ color: "var(--text-muted)", fontSize: "0.72rem" }}>
              None identified
            </span>
          )}
        </div>

        {/* Missing Requirements (if any) */}
        <div className="evidence-block">
          <span className="evidence-block-title">Missing Requirements</span>
          {evidence && evidence.missing_requirements && evidence.missing_requirements.length > 0 ? (
            <div className="pill-list">
              {evidence.missing_requirements.map((req, idx) => (
                <span key={idx} className="evidence-pill evidence-pill-missing">
                  {req}
                </span>
              ))}
            </div>
          ) : (
            <span style={{ color: "#34d399", fontSize: "0.72rem", fontFamily: "var(--font-mono)" }}>
              &check; All required fields available
            </span>
          )}
        </div>

        {/* Data Quality Notes */}
        {evidence && evidence.data_quality_notes && evidence.data_quality_notes.length > 0 && (
          <div className="evidence-block" style={{ gridColumn: "1 / -1" }}>
            <span className="evidence-block-title">Data Quality &amp; Profiling Notes</span>
            <div>
              {evidence.data_quality_notes.map((note, idx) => (
                <div key={idx} className="evidence-note">
                  &bull; {note}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Available Date Range if applicable */}
        {evidence && evidence.available_date_range && (
          <div className="evidence-block" style={{ gridColumn: "1 / -1" }}>
            <span className="evidence-block-title">Available Date Range</span>
            <span style={{ fontFamily: "var(--font-mono)", color: "#a5b4fc" }}>
              {evidence.available_date_range}
            </span>
          </div>
        )}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {interpretation && (
          <div style={{ fontSize: "0.74rem", color: "var(--text-secondary)" }}>
            <strong style={{ color: "var(--text-primary)" }}>Interpretation: </strong>
            {interpretation}
          </div>
        )}

        <div className="next-step-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
          <div>
            <strong>Suggested Next Step: </strong>
            <span>{suggested_next_step}</span>
          </div>
        </div>
      </div>

      <div className="phase-disclaimer-banner">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>
          <strong>Trust Layer Guarantee:</strong> Answerability evaluated deterministically.
          No numerical answers are generated in Phase 3. Calculation &amp; proof synthesis will occur in later phases.
        </span>
      </div>
    </section>
  );
}
