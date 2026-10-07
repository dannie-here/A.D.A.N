import React from "react";

export function PipelineTimeline() {
  const steps = [
    {
      num: "01",
      title: "Query & Invariants",
      desc: "Translates query into verifiable mathematical invariants & statistical hypotheses.",
      state: "Ready for Ingestion",
    },
    {
      num: "02",
      title: "Code Synthesis",
      desc: "Synthesizes deterministic Python analysis script with strict assertions.",
      state: "Ready for Pipeline",
    },
    {
      num: "03",
      title: "Sandboxed Trace",
      desc: "Executes in an isolated runner and captures execution state & hashes.",
      state: "Awaiting Trigger",
    },
    {
      num: "04",
      title: "Proof Construction",
      desc: "Constructs formal verification certificate guaranteeing result validity.",
      state: "Standby",
    },
  ];

  return (
    <section className="timeline-card">
      <div className="card-title-row">
        <div className="card-title">
          <span>Agentic Analysis &amp; Verification Pipeline</span>
        </div>
        <span className="status-indicator">Pipeline Status: Standby [Phase 1]</span>
      </div>

      <div className="timeline-steps">
        {steps.map((step) => (
          <div key={step.num} className="timeline-step">
            <div className="timeline-step-header">
              <span className="step-number">{step.num}</span>
              <span className="step-label">{step.title}</span>
            </div>
            <p className="step-desc">{step.desc}</p>
            <div className="step-state">
              <span className="pulse-dot" style={{ width: "5px", height: "5px" }}></span>
              <span>{step.state}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
