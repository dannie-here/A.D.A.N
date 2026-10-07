import React from "react";

export function PipelineTimeline({ selectedDataset }) {
  const steps = [
    {
      num: "01",
      title: "Dataset & Invariants",
      desc: selectedDataset
        ? `Dataset '${selectedDataset.filename}' profiled with ${selectedDataset.column_count} features and ${selectedDataset.row_count.toLocaleString()} rows.`
        : "Translates query into verifiable mathematical invariants & statistical hypotheses.",
      state: selectedDataset ? "Data Profiled" : "Awaiting Dataset",
      active: !!selectedDataset,
    },
    {
      num: "02",
      title: "Code Synthesis",
      desc: "Synthesizes deterministic Python analysis script with strict assertions.",
      state: "Ready for Pipeline",
      active: false,
    },
    {
      num: "03",
      title: "Sandboxed Trace",
      desc: "Executes in an isolated runner and captures execution state & hashes.",
      state: "Awaiting Trigger",
      active: false,
    },
    {
      num: "04",
      title: "Proof Construction",
      desc: "Constructs formal verification certificate guaranteeing result validity.",
      state: "Standby",
      active: false,
    },
  ];

  return (
    <section className="timeline-card">
      <div className="card-title-row">
        <div className="card-title">
          <span>Agentic Analysis &amp; Verification Pipeline</span>
        </div>
        <span className="status-indicator">
          Pipeline Status: {selectedDataset ? "Dataset Ready [Phase 2]" : "Standby [Phase 2]"}
        </span>
      </div>

      <div className="timeline-steps">
        {steps.map((step) => (
          <div
            key={step.num}
            className="timeline-step"
            style={{
              borderColor: step.active ? "#0ea5e9" : undefined,
              backgroundColor: step.active ? "rgba(14, 165, 233, 0.05)" : undefined,
            }}
          >
            <div className="timeline-step-header">
              <span
                className="step-number"
                style={{
                  backgroundColor: step.active ? "rgba(14, 165, 233, 0.2)" : undefined,
                  color: step.active ? "#38bdf8" : undefined,
                }}
              >
                {step.num}
              </span>
              <span className="step-label">{step.title}</span>
            </div>
            <p className="step-desc">{step.desc}</p>
            <div className="step-state">
              <span
                className="pulse-dot"
                style={{
                  width: "5px",
                  height: "5px",
                  backgroundColor: step.active ? "#38bdf8" : undefined,
                }}
              ></span>
              <span style={{ color: step.active ? "#38bdf8" : undefined }}>{step.state}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
