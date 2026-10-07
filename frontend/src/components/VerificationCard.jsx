import React from "react";

export function VerificationCard() {
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
            <span className="value" style={{ color: "#38bdf8" }}>Pending Analysis Run</span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Soundness Guarantee</span>
            <span className="value">Bounded (p &le; 0.01)</span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Execution Hash</span>
            <span className="value" style={{ color: "#a5b4fc" }}>0x0000...0000 (Placeholder)</span>
          </div>
          <div className="cert-meta-item">
            <span className="label">Invariant Checks</span>
            <span className="value">0 / 0 Assertions Evaluated</span>
          </div>
        </div>

        <div className="verdict-banner">
          <div>
            <strong>Verified Finding Preview [Placeholder]:</strong>
            <p style={{ marginTop: "0.2rem" }}>
              Upon triggering the analysis agent in Phase 2, this panel will display the mathematically checked
              claim, empirical confidence intervals, and cryptographic proof receipt.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
