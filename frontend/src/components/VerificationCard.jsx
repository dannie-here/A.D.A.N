import React from "react";

export function VerificationCard({ selectedDataset, questionAnalysis }) {
  const getVerificationStateText = () => {
    if (!selectedDataset) return "Awaiting Dataset";
    if (!questionAnalysis) return "Dataset Profiled • Awaiting Query Analysis";
    switch (questionAnalysis.status) {
      case "ANSWERABLE":
        return "Answerability Confirmed (Calculation Not Yet Run)";
      case "CANNOT_DETERMINE":
        return "Cannot Determine (Missing Prerequisites)";
      case "NEEDS_CLARIFICATION":
        return "Clarification Required (Ambiguity Detected)";
      default:
        return "Pending Analysis";
    }
  };

  const getVerificationColor = () => {
    if (!questionAnalysis) return selectedDataset ? "#38bdf8" : "#94a3b8";
    if (questionAnalysis.status === "ANSWERABLE") return "#34d399";
    if (questionAnalysis.status === "CANNOT_DETERMINE") return "#fb7185";
    return "#fcd34d";
  };

  return (
    <div className="verification-card">
      <div className="card-title-row">
        <div className="card-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <span>Formal Verification Inspector</span>
        </div>
        <span className="status-indicator" style={{ color: "#34d399", borderColor: "rgba(16, 185, 129, 0.3)" }}>
          Trust Spec: PS08-Phase3
        </span>
      </div>

      <div className="certificate-box">
        <div className="cert-meta-grid">
          <div className="cert-meta-item">
            <span className="label">Verification State</span>
            <span className="value" style={{ color: getVerificationColor() }}>
              {getVerificationStateText()}
            </span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Calculation Status</span>
            <span className="value" style={{ color: "#fbbf24" }}>
              Not Yet Calculated (Phase 4)
            </span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Dataset Target</span>
            <span className="value" style={{ color: "#a5b4fc" }}>
              {selectedDataset ? selectedDataset.filename : "None attached"}
            </span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Relevant Columns</span>
            <span className="value">
              {questionAnalysis && questionAnalysis.evidence.relevant_columns.length > 0
                ? questionAnalysis.evidence.relevant_columns.join(", ")
                : selectedDataset
                ? `${selectedDataset.column_count} columns available`
                : "None"}
            </span>
          </div>
        </div>

        <div className="verdict-banner">
          <div>
            <strong>Phase 3 Trust Layer Notice:</strong>
            <p style={{ marginTop: "0.2rem" }}>
              {questionAnalysis
                ? `Question answerability was classified as ${questionAnalysis.status}. Notice: No numerical answer has been computed or claimed. Formal execution traces and proofs will be generated in subsequent phases.`
                : "Enter an analytical question above to evaluate whether the required columns and timeframes exist in the dataset."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
