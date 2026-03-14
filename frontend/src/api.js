import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ---- Ingestion ----
export const simulateIoTData = (count = 100) =>
  api.post('/ingestion/simulate-iot/', { count });

export const uploadCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_name', file.name);
  return api.post('/ingestion/upload-csv/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDataSummary = () =>
  api.get('/ingestion/summary/');

// ---- Validation ----
export const runValidation = () =>
  api.post('/validation/run/');

export const getReliabilitySummary = () =>
  api.get('/validation/summary/');

export const getReliabilityScores = () =>
  api.get('/validation/scores/');

// ---- Anomaly Detection ----
export const runAnomalyDetection = (contamination = 0.1) =>
  api.post('/anomaly-detection/run/', { contamination });

export const getAnomalySummary = () =>
  api.get('/anomaly-detection/summary/');

export const getAnomalyRecords = () =>
  api.get('/anomaly-detection/records/');

// ---- Alerts ----
export const generateAlerts = () =>
  api.post('/alerts/generate/');

export const getAlertLogs = () =>
  api.get('/alerts/logs/');

export const resolveAlert = (id) =>
  api.post(`/alerts/resolve/${id}/`);

// ---- Dashboard ----
export const getDashboardOverview = () =>
  api.get('/alerts/dashboard/');

export default api;
