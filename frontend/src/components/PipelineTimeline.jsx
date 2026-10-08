import React from "react";

export function PipelineTimeline({ selectedDataset, questionAnalysis }) {
  const steps = [
    {
      num: "01",
      title: "Dataset Profiling",
      desc: selectedDataset
        ? `Dataset '${selectedDataset.filename}' profiled: ${selectedDataset.column_count} features, ${selectedDataset.row_count.toLocaleString()} rows.`
        : "Awaiting dataset upload and schema profiling.",
      state: selectedDataset ? "Profiled (Phase 2)" : "Awaiting Dataset",
      active: !!selectedDataset,
    },
    {
      num: "02",
      title: "Question Answerability",
      desc: questionAnalysis
        ? `Decision: ${questionAnalysis.status}. ${questionAnalysis.evidence.relevant_columns.length} relevant columns identified.`
        : "Evaluates if required fields, aggregations, and date ranges exist.",
      state: questionAnalysis ? questionAnalysis.status : "Awaiting Query",
      active: !!questionAnalysis,
      isAnswerable: questionAnalysis && questionAnalysis.status === "ANSWERABLE",
    },
    {
      num: "03",
      title: "Code Synthesis",
      desc: "Synthesizes deterministic Python analysis script with strict assertions.",
      state: "Phase 4 Standby",
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
          Pipeline Status: {questionAnalysis ? `Answerability: ${questionAnalysis.status}` : selectedDataset ? "Dataset Ready [Phase 3]" : "Standby"}
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
                  backgroundColor: step.active ? (step.isAnswerable ? "#10b981" : "#38bdf8") : undefined,
                }}
              ></span>
              <span style={{ color: step.active ? (step.isAnswerable ? "#34d399" : "#38bdf8") : undefined }}>
                {step.state}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
