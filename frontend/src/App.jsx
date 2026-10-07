import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { QueryInput } from "./components/QueryInput";
import { PipelineTimeline } from "./components/PipelineTimeline";
import { VerificationCard } from "./components/VerificationCard";
import { ProofCodeViewer } from "./components/ProofCodeViewer";

export function App() {
  const [backendHealth, setBackendHealth] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);

  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  // Check backend health and pre-load any existing dataset profile
  useEffect(() => {
    fetch(`${apiBase}/health`)
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("Failed to reach health endpoint");
      })
      .then((data) => setBackendHealth(data))
      .catch(() => {
        setBackendHealth(null);
      });

    // Check if any datasets were previously uploaded in local storage
    fetch(`${apiBase}/api/datasets`)
      .then((res) => {
        if (res.ok) return res.json();
        return [];
      })
      .then((datasets) => {
        if (datasets && datasets.length > 0) {
          // Select most recently registered dataset
          setSelectedDataset(datasets[datasets.length - 1]);
        }
      })
      .catch(() => {
        // Fallback silently if datasets endpoint is unavailable
      });
  }, [apiBase]);

  const handleDatasetSelected = (profile) => {
    setSelectedDataset(profile);
  };

  const handleDatasetReset = () => {
    setSelectedDataset(null);
  };

  return (
    <div className="app-container">
      <Header backendHealth={backendHealth} selectedDataset={selectedDataset} />
      <div className="workspace-body">
        <Sidebar
          selectedDataset={selectedDataset}
          onDatasetSelected={handleDatasetSelected}
          onDatasetReset={handleDatasetReset}
        />
        <main className="workspace-main">
          <QueryInput selectedDataset={selectedDataset} />
          <PipelineTimeline selectedDataset={selectedDataset} />
          <div className="dual-investigation-grid">
            <VerificationCard selectedDataset={selectedDataset} />
            <ProofCodeViewer selectedDataset={selectedDataset} />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
