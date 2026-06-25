/* ===========================================================================
   api.js - sloj za komunikaciju s backendom
   ---------------------------------------------------------------------------
   Sve HTTP pozive prema FastAPI backendu drzimo ovdje na jednom mjestu.
   Komponente ne pozivaju fetch direktno - one zovu ove funkcije.
   =========================================================================== */

// Adresa backenda. Ako backend pokreces na drugom portu, promijeni ovdje.
const BASE_URL = 'http://localhost:8000';

// Pomocna funkcija: napravi GET zahtjev i vrati JSON. Baca gresku ako padne.
async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Greska ${res.status} na ${path}`);
  }
  return res.json();
}

// Pomocna funkcija: POST s JSON tijelom.
async function post(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Greska ${res.status} na ${path}`);
  }
  return res.json();
}

// --- KARTICA 1: statistike ---
export const getStats = () => get('/api/stats');
export const getDescribe = () => get('/api/describe');
export const getFeatures = () => get('/api/features');
export const getGroupAverages = (groupCol) =>
  get(`/api/groups/${encodeURIComponent(groupCol)}`);

// --- KARTICA 2: grafovi ---
export const getDistributions = (bins = 10) =>
  get(`/api/charts/distributions?bins=${bins}`);
export const getCorrelation = () => get('/api/charts/correlation');
export const getPassFail = () => get('/api/charts/pass-fail');
export const getComparison = (groupCol) =>
  get(`/api/charts/comparison/${encodeURIComponent(groupCol)}`);

// --- KARTICA 3: predikcija ---
export const getMetrics = () => get('/api/ml/metrics');
export const getOptions = () => get('/api/ml/options');
export const predict = (student) => post('/api/ml/predict', student);
