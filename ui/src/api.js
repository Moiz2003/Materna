/**
 * ui/src/api.js — REST client for the orchestrator.
 *
 * Calls the FastAPI routes defined in §8 of the SDD.
 * No localStorage/sessionStorage (Playbook P13 constraint).
 *
 * API base: reads VITE_API_URL env var (set in .env or docker-compose),
 * falls back to localhost:8000 for dev.
 */

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// POST /cases — submit a new case
export async function submitCase(formData) {
  const res = await fetch(`${BASE}/cases`, {
    method: "POST",
    body: formData, // multipart/form-data
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// GET /cases/{id} — case status + findings + flags
export function getCase(caseId) {
  return request("GET", `/cases/${caseId}`);
}

// GET /cases/{id}/room — Band room conversation
export function getRoom(caseId) {
  return request("GET", `/cases/${caseId}/room`);
}

// POST /cases/{id}/decision — record human verdict
export function submitDecision(caseId, decision) {
  return request("POST", `/cases/${caseId}/decision`, decision);
}

// GET /cases/{id}/packet — download sealed PDF
export function getPacketUrl(caseId) {
  return `${BASE}/cases/${caseId}/packet`;
}

// GET /cases/{id}/audit — audit chain + verification
export function getAudit(caseId) {
  return request("GET", `/cases/${caseId}/audit`);
}

// POST /extract — smart extraction from clinical notes
export async function extractCase(clinicalText) {
  const res = await fetch(`${BASE}/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: clinicalText }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// POST /extract-image — extract data from ultrasound image via Gemini Vision
export async function extractFromImage(imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  const res = await fetch(`${BASE}/extract-image`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
