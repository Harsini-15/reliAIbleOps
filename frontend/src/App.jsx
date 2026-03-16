import React, { useState, useEffect, useRef } from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import api from './api';
import './index.css';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  Title, Tooltip, Legend, Filler
);

// --- Icons (SVG) ---
const ActivityIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const DatabaseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
  </svg>
);

const ShieldCheckIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
    <path d="M9 12l2 2 4-4"></path>
  </svg>
);

const AlertTriangleIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [pipelineState, setPipelineState] = useState(0); // 0: Idle, 1: Ingesting, 2: Validating, 3: ML, 4: Alerts
  const [pipelineMsg, setPipelineMsg] = useState("");
  const fileInputRef = useRef(null);

  const fetchDashboard = async () => {
    try {
      setRefreshing(true);
      const res = await api.get('/alerts/dashboard/');
      setData(res.data);
    } catch (err) {
      console.error("Failed to fetch dashboard", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const runFullPipeline = async () => {
    if (pipelineState > 0) return;
    try {
      setPipelineState(1);
      setPipelineMsg("Simulating IoT Engineering Data...");
      await api.post('/ingestion/simulate-iot/', { count: 300 });

      setPipelineState(2);
      setPipelineMsg("Running Data Reliability Engine...");
      await api.post('/validation/run/');

      setPipelineState(3);
      setPipelineMsg("Executing ML Anomaly Detection (Isolation Forest & Z-Score)...");
      await api.post('/anomaly-detection/run/', { contamination: 0.1 });

      setPipelineState(4);
      setPipelineMsg("Generating Insights & Alerts...");
      await api.post('/alerts/generate/');

      setPipelineMsg("Pipeline execution complete.");
      await fetchDashboard();
      setTimeout(() => setPipelineState(0), 3000);
    } catch (err) {
      console.error(err);
      setPipelineMsg("Pipeline failed.");
      setTimeout(() => setPipelineState(0), 3000);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      setPipelineState(1);
      setPipelineMsg(`Uploading ${file.name}...`);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_name', file.name);
      
      await api.post('/ingestion/upload-csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      setPipelineMsg("Upload complete. Running validation...");
      setPipelineState(2);
      await api.post('/validation/run/');
      
      setPipelineMsg("Running AI Anomaly Detection...");
      setPipelineState(3);
      await api.post('/anomaly-detection/run/');
      
      setPipelineMsg("Generating Alerts...");
      setPipelineState(4);
      await api.post('/alerts/generate/');
      
      setPipelineMsg("Data processing complete.");
      await fetchDashboard();
      setTimeout(() => setPipelineState(0), 3000);
    } catch (err) {
      console.error(err);
      setPipelineMsg("Upload pipeline failed.");
      setTimeout(() => setPipelineState(0), 3000);
    }
    fileInputRef.current.value = "";
  };

  if (loading && !data) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div className="loading-text">Initializing ReliAIbleOps Platform...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div className="loading-text">Unable to connect to ReliAIbleOps API. Please check backend status.</div>
        <button className="btn btn-secondary" onClick={fetchDashboard} style={{ marginTop: '20px' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  // ---- Chart Data Preprocessing ----
  
  // 1. System Performance (CPU vs Memory)
  const sortedData = data.recent_data ? [...data.recent_data].reverse() : [];
  const times = sortedData.map(d => {
    const dObj = new Date(d.timestamp);
    return `${dObj.getHours()}:${String(dObj.getMinutes()).padStart(2, '0')}`;
  });

  const performanceChartData = {
    labels: times,
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: sortedData.map(d => d.cpu_usage),
        borderColor: '#6366f1', // Indigo
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
      {
        label: 'Memory Usage (%)',
        data: sortedData.map(d => d.memory_usage),
        borderColor: '#22d3ee', // Cyan
        backgroundColor: 'transparent',
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
      }
    ]
  };

  // 2. Anomaly Severity Breakdown
  const severityLabels = data.severity_breakdown?.map(item => item.severity.toUpperCase()) || [];
  const severityValues = data.severity_breakdown?.map(item => item.count) || [];
  const severityColors = data.severity_breakdown?.map(item => {
    switch (item.severity) {
      case 'critical': return '#ef4444'; // Red
      case 'high': return '#f97316';     // Orange
      case 'medium': return '#eab308';   // Yellow
      case 'low': return '#10b981';      // Green
      default: return '#6366f1';
    }
  }) || [];

  const anomalyChartData = {
    labels: severityLabels.length ? severityLabels : ['No Anomalies'],
    datasets: [{
      label: 'Detected Anomalies',
      data: severityValues.length ? severityValues : [0],
      backgroundColor: severityColors.length ? severityColors : ['#1e293b'],
      borderRadius: 4,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } } },
    scales: {
      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
      x: { grid: { display: false }, ticks: { color: '#64748b', maxTicksLimit: 10 } }
    },
    interaction: { mode: 'index', intersect: false },
  };

  // Health Score Calculation
  const healthScore = data.system_health_score || 0;
  const strokeDashoffset = 565 - (565 * healthScore) / 100;
  let healthColor = '#10b981'; // Emerald
  if (healthScore < 60) healthColor = '#f43f5e'; // Rose
  else if (healthScore < 85) healthColor = '#f59e0b'; // Amber

  return (
    <div className="app-wrapper">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">ai</div>
            <div>
              <div className="logo-text">ReliAIbleOps</div>
              <div className="logo-subtitle">Engineering Data Intelligence</div>
            </div>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary" onClick={fetchDashboard} disabled={refreshing}>
              <RefreshIcon /> {refreshing ? 'Syncing...' : 'Sync'}
            </button>
            <input 
              type="file" 
              accept=".csv" 
              style={{ display: 'none' }} 
              ref={fileInputRef}
              onChange={handleFileUpload}
            />
            <button className="btn btn-secondary" onClick={() => fileInputRef.current.click()} disabled={pipelineState > 0}>
              Upload CSV
            </button>
            <button className="btn btn-primary" onClick={runFullPipeline} disabled={pipelineState > 0}>
              <ActivityIcon /> Simulate IoT Stream
            </button>
          </div>
        </div>
      </header>

      <main className="app-container">
        
        {/* Pipeline Progress Indicator */}
        <div className="pipeline-section">
          <div className="pipeline-title">Data Intelligence Pipeline</div>
          <div className="pipeline-desc">Real-time processing framework for operational telemetry.</div>
          
          <div className="pipeline-steps">
            <div className={`pipeline-step ${pipelineState >= 1 ? 'active' : ''}`}>
              <div className={`step-number ${pipelineState >= 1 ? 'done' : ''}`}>1</div>
              <span>Ingestion</span>
            </div>
            <div className="step-arrow">→</div>
            
            <div className={`pipeline-step ${pipelineState >= 2 ? 'active' : ''}`}>
              <div className={`step-number ${pipelineState >= 2 ? 'done' : ''}`}>2</div>
              <span>Reliability validation</span>
            </div>
            <div className="step-arrow">→</div>
            
            <div className={`pipeline-step ${pipelineState >= 3 ? 'active' : ''}`}>
              <div className={`step-number ${pipelineState >= 3 ? 'done' : ''}`}>3</div>
              <span>ML Anomaly Detection</span>
            </div>
            <div className="step-arrow">→</div>
            
            <div className={`pipeline-step ${pipelineState >= 4 ? 'active' : ''}`}>
              <div className={`step-number ${pipelineState >= 4 ? 'done' : ''}`}>4</div>
              <span>Decision Intelligence</span>
            </div>
          </div>

          {pipelineState > 0 && (
            <div className="pipeline-status">
              ⚡ {pipelineMsg}
            </div>
          )}
        </div>

        {/* Top KPI Cards */}
        <div className="stats-grid">
          <div className="stat-card indigo">
            <div className="stat-label">Total Data Points</div>
            <div className="stat-value indigo">{data?.total_data_points?.toLocaleString() || 0}</div>
            <div className="stat-sub">Telemetry records ingested</div>
          </div>
          <div className="stat-card emerald">
            <div className="stat-label">Validated Records</div>
            <div className="stat-value emerald">{data?.validated_data_points?.toLocaleString() || 0}</div>
            <div className="stat-sub">Passed reliability checks</div>
          </div>
          <div className="stat-card cyan">
            <div className="stat-label">Avg Reliability</div>
            <div className="stat-value cyan">{data?.avg_reliability_score || 0}%</div>
            <div className="stat-sub">Completeness & Consistency</div>
          </div>
          <div className="stat-card rose">
            <div className="stat-label">Anomalies Detected</div>
            <div className="stat-value rose">{data?.total_anomalies?.toLocaleString() || 0}</div>
            <div className="stat-sub">Isolated by ML pipeline</div>
          </div>
        </div>

        {/* Charts & Health Row */}
        <div className="charts-grid">
          {/* Health Gauge */}
          <div className="health-gauge-container">
            <div className="health-gauge">
              <svg width="180" height="180" viewBox="0 0 200 200">
                <circle className="health-gauge-bg" cx="100" cy="100" r="90" />
                <circle 
                  className="health-gauge-fill" 
                  cx="100" cy="100" r="90" 
                  stroke={healthColor}
                  strokeDasharray="565"
                  strokeDashoffset={strokeDashoffset}
                />
              </svg>
              <div className="health-gauge-value">
                <div className="health-score" style={{ color: healthColor }}>{healthScore}</div>
              </div>
            </div>
            <div className="health-title">System Health</div>
            <div className="health-label">Global Integrity Score</div>
          </div>

          {/* Performance Trend */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">System Performance Telemetry</div>
              <div className="chart-badge">Live</div>
            </div>
            <div className="chart-wrapper">
              <Line data={performanceChartData} options={chartOptions} />
            </div>
          </div>

          {/* Anomaly Distribution */}
          <div className="chart-card">
            <div className="chart-header">
              <div className="chart-title">Anomaly Severity Distribution</div>
              <div className="chart-badge">Isolation Forest + Z-Score</div>
            </div>
            <div className="chart-wrapper">
              <Bar 
                data={anomalyChartData} 
                options={{
                  ...chartOptions,
                  scales: { ...chartOptions.scales, x: { grid: { display: false } } }
                }} 
              />
            </div>
          </div>
        </div>

        {/* Decision Intelligence Row */}
        <div className="section-header">
          <span className="section-icon">🧠</span>
          Decision Intelligence Center
        </div>
        <div className="section-sub">Actionable insights generated by analyzing reliability scores and anomaly patterns.</div>
        
        {data.recommendations?.length > 0 ? (
          <div className="recommendations-grid">
            {data.recommendations.map((rec, i) => (
              <div key={i} className={`rec-card ${rec.type}`}>
                <div className="rec-type">{rec.type}</div>
                <div className="rec-title">{rec.title}</div>
                <div className="rec-message">{rec.message}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="alerts-panel">
            <div className="alert-empty">All systems nominal. No actionable intelligence required.</div>
          </div>
        )}

        {/* Active Alerts List */}
        <div className="alerts-panel">
          <div className="alerts-header">
            <div className="alerts-title">Incident Response Queue</div>
            {data.unresolved_alerts > 0 && <span className="alert-count-badge">{data.unresolved_alerts} Pendings</span>}
          </div>
          
          {data.recent_alerts?.length > 0 ? (
            <div>
              {data.recent_alerts.map((alert) => (
                <div key={alert.id} className={`alert-item ${alert.level}`}>
                  <div className={`alert-dot ${alert.level}`}></div>
                  <div className="alert-content">
                    <div className="alert-title">{alert.title}</div>
                    <div className="alert-meta">
                      Alert ID: {alert.id} • {new Date(alert.created_at).toLocaleString()} • Source: {alert.source}
                    </div>
                  </div>
                  <button className="btn btn-sm btn-secondary" onClick={() => api.post(`/alerts/resolve/${alert.id}/`).then(fetchDashboard)}>
                    Resolve
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="alert-empty">No active alerts. Engineering systems are operating reliably.</div>
          )}
        </div>

      </main>

      <footer className="footer">
        ReliAIbleOps Engine v1.0 • Built for Cloud Infrastructure • {new Date().getFullYear()}
      </footer>
    </div>
  );
}

export default App;
