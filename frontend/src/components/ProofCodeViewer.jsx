import React from "react";

export function ProofCodeViewer({ selectedDataset }) {
  const datasetName = selectedDataset ? selectedDataset.filename : "dataset.csv";
  const firstCol = selectedDataset && selectedDataset.columns.length > 0
    ? selectedDataset.columns[0].name
    : "outcome_metric";

  const sampleProofScript = `# ==============================================================================
# A.D.A.N. PROOF-CARRYING DATA ANALYSIS SCRIPT (SPECIFICATION TEMPLATE)
# Target: PS08 - Proof-Carrying Data Analyst (Phase 2 Dataset Foundation)
# Target Dataset: ${datasetName}
# ==============================================================================
import numpy as np
import pandas as pd

def verify_dataset_invariants(df: pd.DataFrame) -> dict:
    """Verifies deterministic invariants prior to formal analysis execution."""
    
    # 1. Physical Invariant Checks (Derived from Deterministic Profiler)
    assert "${firstCol}" in df.columns, "Invariant Violation: Column '${firstCol}' missing"
    assert len(df) == ${selectedDataset ? selectedDataset.row_count : 250000}, "Invariant Violation: Row count mismatch"
    
    # 2. Duplicate Integrity Invariant
    duplicate_count = int(df.duplicated().sum())
    assert duplicate_count == ${selectedDataset ? selectedDataset.duplicate_row_count : 0}, "Duplicate count invariant breached"
    
    # 3. Soundness Guarantee & Proof Witness
    return {
        "dataset": "${datasetName}",
        "invariants_verified": True,
        "proof_witness": "VERIFIED_DETERMINISTIC_WITNESS"
    }
`;

  return (
    <div className="proof-code-card">
      <div className="card-title-row">
        <div className="card-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          <span>Proof-Carrying Code Inspector</span>
        </div>
        <span className="status-indicator">
          Format: Python + Invariant Assertions
        </span>
      </div>

      <div className="code-block-container">
        <div className="code-header">
          <span>{datasetName ? `verify_${datasetName.replace(/[^a-zA-Z0-9]/g, '_')}.py` : "analysis_proof_contract.py"}</span>
          <span>Deterministic Runner [Phase 2]</span>
        </div>
        <pre className="code-content">
          <code>{sampleProofScript}</code>
        </pre>
      </div>
    </div>
  );
}
