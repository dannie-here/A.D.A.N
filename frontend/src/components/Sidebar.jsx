import React, { useState, useRef } from "react";

export function Sidebar({ selectedDataset, onDatasetSelected, onDatasetReset }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const handleFileChange = (e) => {
    setErrorMessage("");
    setSuccessMessage("");
    const selected = e.target.files && e.target.files[0];
    if (selected) {
      validateAndSetFile(selected);
    }
  };

  const validateAndSetFile = (f) => {
    const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
    if (![".csv", ".xlsx", ".xls"].includes(ext)) {
      setErrorMessage(`Unsupported format '${ext}'. Please choose a .csv or .xlsx file.`);
      setFile(null);
      return;
    }
    if (f.size === 0) {
      setErrorMessage("Selected file is empty (0 bytes).");
      setFile(null);
      return;
    }
    setFile(f);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    setErrorMessage("");
    setSuccessMessage("");
    const dropped = e.dataTransfer.files && e.dataTransfer.files[0];
    if (dropped) {
      validateAndSetFile(dropped);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setErrorMessage("");
    setSuccessMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiBase}/api/datasets/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Dataset upload failed");
      }

      setSuccessMessage(`Dataset profiled: ${data.profile.filename}`);
      onDatasetSelected(data.profile);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setErrorMessage(err.message || "Failed to upload and profile dataset.");
    } finally {
      setIsUploading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <aside className="workspace-sidebar">
      <div className="sidebar-title">
        <span>Investigation Dataset</span>
        {selectedDataset && (
          <button
            type="button"
            className="reset-dataset-btn"
            onClick={onDatasetReset}
            title="Unload current dataset"
          >
            Change Dataset
          </button>
        )}
      </div>

      {/* Upload Zone (shown when no dataset is loaded or changing dataset) */}
      {!selectedDataset && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div
            className={`upload-dropzone ${isDragOver ? "drag-active" : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="file-input-hidden"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
            />
            <svg
              className="upload-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <div>
              <div className="upload-prompt">
                {file ? file.name : "Select or Drop Dataset"}
              </div>
              <div className="upload-subprompt">Supports CSV, XLSX (Up to 50MB)</div>
            </div>
          </div>

          {file && (
            <div className="file-selected-bar">
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {file.name} ({formatBytes(file.size)})
              </span>
              <button
                type="button"
                style={{ background: "none", border: "none", color: "#f43f5e", cursor: "pointer" }}
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
              >
                &times;
              </button>
            </div>
          )}

          <button
            type="button"
            className="upload-action-btn"
            disabled={!file || isUploading}
            onClick={handleUpload}
          >
            {isUploading ? (
              <>
                <span className="spinner"></span>
                Profiling Dataset...
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Upload &amp; Deterministic Profile
              </>
            )}
          </button>
        </div>
      )}

      {/* Error and Success Banners */}
      {errorMessage && (
        <div className="alert-box alert-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div style={{ flex: 1 }}>{errorMessage}</div>
          <button
            type="button"
            style={{ background: "none", border: "none", color: "inherit", cursor: "pointer" }}
            onClick={() => setErrorMessage("")}
          >
            &times;
          </button>
        </div>
      )}

      {successMessage && !selectedDataset && (
        <div className="alert-box alert-success">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span>{successMessage}</span>
        </div>
      )}

      {/* Profiler Results Card (Active Dataset) */}
      {selectedDataset && (
        <div className="dataset-card">
          <div className="dataset-card-header">
            <div>
              <div className="dataset-name" title={selectedDataset.filename}>
                {selectedDataset.filename}
              </div>
              <div style={{ fontSize: "0.68rem", color: "#64748b", marginTop: "2px" }}>
                Format: {selectedDataset.file_type.toUpperCase()} &bull; {formatBytes(selectedDataset.file_size_bytes)}
              </div>
            </div>
            <span className="dataset-status-pill">Profiled</span>
          </div>

          <div className="dataset-stats">
            <div className="dataset-stat-box">
              <span>Rows</span>
              <strong>{selectedDataset.row_count.toLocaleString()}</strong>
            </div>
            <div className="dataset-stat-box">
              <span>Columns</span>
              <strong>{selectedDataset.column_count}</strong>
            </div>
            <div className="dataset-stat-box">
              <span>Duplicate Rows</span>
              <strong style={{ color: selectedDataset.duplicate_row_count > 0 ? "#fbbf24" : "#34d399" }}>
                {selectedDataset.duplicate_row_count}
              </strong>
            </div>
            <div className="dataset-stat-box">
              <span>Numeric Cols</span>
              <strong>{selectedDataset.numeric_columns.length}</strong>
            </div>
          </div>

          {/* Columns & Missing Values */}
          <div className="schema-preview">
            <div className="schema-preview-label">
              Columns Profile ({selectedDataset.columns.length})
            </div>
            <div className="columns-scroll-area">
              {selectedDataset.columns.map((col) => (
                <div key={col.name} className="schema-item">
                  <span className="schema-col-name" title={col.name}>
                    {col.name}
                  </span>
                  <div style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
                    <span className="schema-col-type">{col.dtype}</span>
                    <span
                      className="stat-metric-pill"
                      style={{
                        color: col.missing_count > 0 ? "#f87171" : "#94a3b8",
                      }}
                      title={`${col.missing_count} missing values`}
                    >
                      {col.missing_count === 0 ? "0 null" : `${col.missing_percentage}% null`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Date Ranges (where detected) */}
          {selectedDataset.date_ranges && selectedDataset.date_ranges.length > 0 && (
            <div className="date-ranges-section">
              <div className="schema-preview-label">Detected Date Ranges</div>
              {selectedDataset.date_ranges.map((dr) => (
                <div key={dr.column_name} className="date-range-card">
                  <div className="date-range-name">{dr.column_name}</div>
                  <div className="date-range-dates">
                    <span>{dr.min_date.split("T")[0]}</span>
                    <span style={{ color: "#64748b" }}>&rarr;</span>
                    <span>{dr.max_date.split("T")[0]}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Numeric Summaries */}
          {selectedDataset.numeric_statistics &&
            Object.keys(selectedDataset.numeric_statistics).length > 0 && (
              <div className="numeric-stats-section">
                <div className="schema-preview-label">Numeric Summaries</div>
                <div className="columns-scroll-area" style={{ maxHeight: "150px" }}>
                  {Object.entries(selectedDataset.numeric_statistics).map(([colName, stat]) => (
                    <div key={colName} className="stat-column-card">
                      <div className="stat-column-name">
                        <span>{colName}</span>
                      </div>
                      <div className="stat-grid-4">
                        <div className="stat-mini-box">
                          <span className="lbl">Min</span>
                          <span className="val">{stat.min}</span>
                        </div>
                        <div className="stat-mini-box">
                          <span className="lbl">Max</span>
                          <span className="val">{stat.max}</span>
                        </div>
                        <div className="stat-mini-box">
                          <span className="lbl">Mean</span>
                          <span className="val">{stat.mean}</span>
                        </div>
                        <div className="stat-mini-box">
                          <span className="lbl">Median</span>
                          <span className="val">{stat.median}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}

      {/* Trust layer notice */}
      <div className="sidebar-notice">
        <strong>PS08 Trust Layer Foundation:</strong>
        <p style={{ marginTop: "0.3rem" }}>
          Every metric above is deterministically computed via Python and verified prior to any AI question answering or code generation.
        </p>
      </div>
    </aside>
  );
}
