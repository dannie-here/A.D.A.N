import React from "react";

export function Sidebar() {
  const placeholderColumns = [
    { name: "record_id", type: "UUID / String" },
    { name: "timestamp_utc", type: "DateTime" },
    { name: "feature_val", type: "Float64" },
    { name: "control_group", type: "Boolean" },
    { name: "outcome_metric", type: "Float64" },
  ];

  return (
    <aside className="workspace-sidebar">
      <div className="sidebar-title">
        <span>Investigation Dataset</span>
        <span style={{ fontSize: "0.68rem", color: "#38bdf8" }}>[Placeholder]</span>
      </div>

      <div className="dataset-card">
        <div className="dataset-card-header">
          <div>
            <div className="dataset-name">benchmark_trial_dataset.parquet</div>
            <div style={{ fontSize: "0.68rem", color: "#64748b", marginTop: "2px" }}>
              SHA256: 4e92...f81a
            </div>
          </div>
          <span className="dataset-status-pill">Ready</span>
        </div>

        <div className="dataset-stats">
          <div className="dataset-stat-box">
            <span>Rows</span>
            <strong>250,000</strong>
          </div>
          <div className="dataset-stat-box">
            <span>Features</span>
            <strong>18 Columns</strong>
          </div>
        </div>

        <div className="schema-preview">
          <div className="schema-preview-label">Sample Schema Specification</div>
          <div className="schema-list">
            {placeholderColumns.map((col) => (
              <div key={col.name} className="schema-item">
                <span className="schema-col-name">{col.name}</span>
                <span className="schema-col-type">{col.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="sidebar-notice">
        <strong>Phase 1 Architecture Notice:</strong>
        <p style={{ marginTop: "0.3rem" }}>
          Live dataset upload, schema introspection, and automated summary statistics will be connected in Phase 2.
        </p>
      </div>
    </aside>
  );
}
