import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { QueryInput } from "./components/QueryInput";
import { PipelineTimeline } from "./components/PipelineTimeline";
import { VerificationCard } from "./components/VerificationCard";
import { ProofCodeViewer } from "./components/ProofCodeViewer";

export function App() {
  const [backendHealth, setBackendHealth] = useState(null);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    fetch(`${apiBase}/health`)
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("Failed to reach health endpoint");
      })
      .then((data) => setBackendHealth(data))
      .catch(() => {
        // Fallback gracefully in Phase 1 when backend server may not yet be running
        setBackendHealth(null);
      });
  }, []);

  return (
    <div className="app-container">
      <Header backendHealth={backendHealth} />
      <div className="workspace-body">
        <Sidebar />
        <main className="workspace-main">
          <QueryInput />
          <PipelineTimeline />
          <div className="dual-investigation-grid">
            <VerificationCard />
            <ProofCodeViewer />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
