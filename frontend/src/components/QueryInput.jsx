import React, { useState } from "react";

export function QueryInput({ selectedDataset, onAnalysisComplete }) {
  const [question, setQuestion] = useState("What is the total revenue?");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorDetails, setErrorDetails] = useState(null);

  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const sampleQuestionChips = [
    { label: "Total Revenue (Answerable)", text: "What is the total revenue?" },
    { label: "Avg Unit Price (Answerable)", text: "What is the average unit_price?" },
    { label: "Total Profit (Cannot Determine)", text: "What is the total profit?" },
    { label: "Revenue in 2035 (Out of Range)", text: "What was revenue in 2035?" },
    { label: "Revenue in Q1 (Ambiguity)", text: "What was revenue in Q1?" },
    { label: "Duplicate Rows (Audit)", text: "How many duplicate rows exist?" },
  ];

  const handleChipClick = (text) => {
    setQuestion(text);
    setErrorDetails(null);
  };

  const handleAnalyze = async () => {
    setErrorDetails(null);

    // 1. Client-side check for dataset presence
    if (!selectedDataset) {
      setErrorDetails({
        error: "ERROR",
        source: "Frontend Investigation Workspace",
        reason: "No dataset selected for analysis.",
        evidence: "selected_dataset = null",
        recovery_retry: "Upload or select a dataset from the sidebar before submitting an investigation query.",
        final_status: "ANALYSIS FAILED",
      });
      return;
    }

    // 2. Client-side check for question non-emptiness
    const cleanQ = question.trim();
    if (!cleanQ) {
      setErrorDetails({
        error: "ERROR",
        source: "Frontend Input Validator",
        reason: "Question must not be empty or composed solely of whitespace.",
        evidence: "question = ''",
        recovery_retry: "Type a clear, non-empty analytical query or select one of the suggested templates.",
        final_status: "ANALYSIS FAILED",
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      const response = await fetch(`${apiBase}/api/questions/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: selectedDataset.dataset_id,
          question: cleanQ,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // If structured A.D.A.N. error was returned in detail
        if (data.detail && typeof data.detail === "object" && data.detail.error === "ERROR") {
          setErrorDetails(data.detail);
        } else {
          setErrorDetails({
            error: "ERROR",
            source: "Question Analysis API",
            reason: typeof data.detail === "string" ? data.detail : "API returned an unexpected error.",
            evidence: `HTTP ${response.status} from ${apiBase}/api/questions/analyze`,
            recovery_retry: "Check dataset status and resubmit your query.",
            final_status: "ANALYSIS FAILED",
          });
        }
        return;
      }

      // Success -> notify parent component with analysis result
      onAnalysisComplete(data);
    } catch (err) {
      setErrorDetails({
        error: "ERROR",
        source: "Network / Client Subsystem",
        reason: err.message || "Could not reach the backend Question Analysis service.",
        evidence: `target_url = ${apiBase}/api/questions/analyze`,
        recovery_retry: "Verify that the FastAPI backend server is running and accessible.",
        final_status: "ANALYSIS FAILED",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <section className="investigation-panel">
      <div className="panel-header-row">
        <div className="panel-title">
          <span>Analytical Query &amp; Answerability Check</span>
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
              Target: {selectedDataset.filename}
            </span>
          )}
        </div>
        <div className="query-chips" style={{ flexWrap: "wrap" }}>
          {sampleQuestionChips.map((chip) => (
            <button
              key={chip.label}
              type="button"
              className={`query-chip ${question === chip.text ? "active" : ""}`}
              onClick={() => handleChipClick(chip.text)}
              title={chip.text}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      <div className="investigation-input-wrapper">
        <textarea
          className="investigation-textarea"
          value={question}
          onChange={(e) => {
            setQuestion(e.target.value);
            setErrorDetails(null);
          }}
          placeholder={
            selectedDataset
              ? `State your query against '${selectedDataset.filename}' to evaluate answerability...`
              : "Select a dataset in the sidebar first, then enter your analytical question..."
          }
          rows={3}
        />
      </div>

      <div className="input-action-bar">
        <span className="input-hint">
          {selectedDataset
            ? "Deterministic answerability analysis • No hallucinated calculations • Strict evidence check"
            : "No dataset selected. Select or upload a dataset in the sidebar to enable analysis."}
        </span>
        <button
          type="button"
          className="analyze-button"
          disabled={isAnalyzing}
          onClick={handleAnalyze}
          title="Analyze question answerability against dataset profile"
        >
          {isAnalyzing ? (
            <>
              <span className="spinner"></span>
              Evaluating Answerability...
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              Analyze Question Answerability
            </>
          )}
        </button>
      </div>

      {/* Structured A.D.A.N. Error Card (Required Format) */}
      {errorDetails && (
        <div className="adan-error-card">
          <div className="adan-error-card-header">
            <span className="adan-error-title">{errorDetails.error || "ERROR"}</span>
            <button
              type="button"
              style={{ background: "none", border: "none", color: "#fda4af", cursor: "pointer", fontSize: "1rem" }}
              onClick={() => setErrorDetails(null)}
            >
              &times;
            </button>
          </div>
          <div className="adan-error-field">
            <span className="adan-error-label">Source:</span>
            <span className="adan-error-value">{errorDetails.source}</span>
          </div>
          <div className="adan-error-field">
            <span className="adan-error-label">Reason:</span>
            <span className="adan-error-value">{errorDetails.reason}</span>
          </div>
          <div className="adan-error-field">
            <span className="adan-error-label">Evidence:</span>
            <span className="adan-error-value">{errorDetails.evidence}</span>
          </div>
          <div className="adan-error-field">
            <span className="adan-error-label">Recovery / Retry:</span>
            <span className="adan-error-value">{errorDetails.recovery_retry}</span>
          </div>
          <div className="adan-error-field" style={{ marginTop: "0.25rem" }}>
            <span className="adan-error-label">Final status:</span>
            <span className="adan-error-status-badge">{errorDetails.final_status}</span>
          </div>
        </div>
      )}
    </section>
  );
}
