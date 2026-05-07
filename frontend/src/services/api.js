/**
 * PurpleLink API Service
 * Axios-based client for communicating with the FastAPI backend.
 */

import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Stations ────────────────────────────────────────
export async function getStations(type = null, mode = null) {
  const params = {};
  if (type) params.type = type;
  if (mode) params.mode = mode;
  const res = await api.get('/stations', { params });
  return res.data;
}

export async function getStation(stationId) {
  const res = await api.get(`/stations/${stationId}`);
  return res.data;
}

export async function searchStations(query) {
  const res = await api.get(`/stations/search/${encodeURIComponent(query)}`);
  return res.data;
}

export async function getNearbyStops(lat, lon, radius = 500) {
  const res = await api.get('/nearby-stops', { params: { lat, lon, radius } });
  return res.data;
}

export async function getGraphStats() {
  const res = await api.get('/graph-stats');
  return res.data;
}

// ─── Routing ─────────────────────────────────────────
export async function getRoute(source, destination, preference = 'fastest') {
  const res = await api.get('/route', {
    params: { source, destination, preference },
  });
  return res.data;
}

export async function getRouteComparison(source, destination) {
  const res = await api.get('/route/compare', {
    params: { source, destination },
  });
  return res.data;
}

// ─── Disruptions ─────────────────────────────────────
export async function getDisruptions() {
  const res = await api.get('/disruptions');
  return res.data;
}

export async function createDisruption(data) {
  const res = await api.post('/disruptions', data);
  return res.data;
}

export async function deleteDisruption(id) {
  const res = await api.delete(`/disruptions/${id}`);
  return res.data;
}

export async function resetDisruptions() {
  const res = await api.post('/disruptions/reset');
  return res.data;
}

// ─── Health ──────────────────────────────────────────
export async function getHealth() {
  const res = await api.get('/health');
  return res.data;
}

export default api;
