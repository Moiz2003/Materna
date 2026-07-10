/**
 * ui/src/api.js — REST client, wired to Clinify's secure proxy.
 *
 * When embedded in Clinify (served at /materna-ui/), VITE_API_URL is set to
 * /api/materna so all calls go through Clinify's Express proxy which enforces
 * JWT + doctor-role auth before forwarding to the FastAPI backend.
 *
 * Auth sources (tried in order):
 *   1. localStorage 'user' key (set by Clinify React app on login)
 *   2. httpOnly cookie 'token' — browser sends it automatically via credentials,
 *      so we include credentials: 'same-origin' on all requests as a fallback.
 */

const BASE = import.meta.env.VITE_API_URL || "";

function clinifyAuth() {
  try {
    const stored = localStorage.getItem('user');
    if (!stored) return {};
    const token = JSON.parse(stored)?.token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

/**
 * Build fetch options with credentials included. This ensures httpOnly cookies
 * are sent as a fallback when localStorage is unavailable (XSS-hardened setups).
 */
function authOpts(overrides = {}) {
  return {
    credentials: 'same-origin',
    ...overrides,
  };
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`, authOpts({
    method: "GET",
    headers: clinifyAuth(),
  }));
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function request(method, path, body = null) {
  const opts = authOpts({
    method,
    headers: { "Content-Type": "application/json", ...clinifyAuth() },
  });
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function submitCase(formData) {
  const res = await fetch(`${BASE}/cases`, authOpts({
    method: "POST",
    headers: clinifyAuth(),
    body: formData,
  }));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export function getCase(caseId) {
  return request("GET", `/cases/${caseId}`);
}

export function getRoom(caseId) {
  return request("GET", `/cases/${caseId}/room`);
}

export function submitDecision(caseId, decision) {
  return request("POST", `/cases/${caseId}/decision`, decision);
}

export function getPacketUrl(caseId) {
  return `${BASE}/cases/${caseId}/packet`;
}

export function getAudit(caseId) {
  return request("GET", `/cases/${caseId}/audit`);
}

export async function extractCase(clinicalText) {
  const res = await fetch(`${BASE}/extract`, authOpts({
    method: "POST",
    headers: { "Content-Type": "application/json", ...clinifyAuth() },
    body: JSON.stringify({ text: clinicalText }),
  }));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function demoTamper(caseId) {
  const res = await fetch(`${BASE}/demo/tamper/${caseId}`, authOpts({
    method: 'POST',
    headers: clinifyAuth(),
  }));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function extractFromImage(imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  const res = await fetch(`${BASE}/extract-image`, authOpts({
    method: "POST",
    headers: clinifyAuth(),
    body: fd,
  }));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
