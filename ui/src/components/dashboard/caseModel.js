/**
 * caseModel.js — the bridge between the novice-friendly form and the
 * orchestrator's case JSON contract.
 *
 * The UI never asks a clinician to type JSON. They fill a form (or paste
 * notes that auto-fill the form). This module serializes that form into the
 * exact `case` payload the FastAPI `/cases` endpoint already expects, and
 * parses extracted/raw JSON back into form fields. No API behaviour changes —
 * the submitted shape is identical to the legacy textarea.
 */

// ── Pipeline state machine (mirrors orchestrator/lifecycle.py) ─────────────
export const STATES = [
  'RECEIVED', 'STRUCTURED', 'ANALYZED', 'CHECKED',
  'AUDITED', 'ESCALATED', 'HUMAN_REVIEWED', 'SEALED',
];

/** The four specialist agents, in coordination order. */
export const PIPELINE_STEPS = [
  { id: 'intake',      label: 'Intake',        sub: 'normalize',   reached: 'STRUCTURED' },
  { id: 'dating_risk', label: 'Dating & Risk', sub: 'GA + flags',  reached: 'ANALYZED' },
  { id: 'guideline',   label: 'Guideline',     sub: 'compliance',  reached: 'CHECKED' },
  { id: 'auditor',     label: 'Auditor',       sub: 'challenge',   reached: 'AUDITED' },
];

/**
 * How many pipeline steps are complete for a given status.
 * -1 → nothing started yet (RECEIVED / blank / loading).
 */
export function completedSteps(status) {
  if (!status || status === 'RECEIVED') return 0;
  const order = ['STRUCTURED', 'ANALYZED', 'CHECKED', 'AUDITED'];
  // ESCALATED/HUMAN_REVIEWED/SEALED/AUTO_CLEARED all imply the full pipeline ran.
  if (['AUDITED', 'ESCALATED', 'HUMAN_REVIEWED', 'SEALED', 'AUTO_CLEARED', 'QUARANTINED'].includes(status)) return 4;
  const i = order.indexOf(status);
  return i < 0 ? 0 : i + 1;
}

/** Display metadata for a status badge. tone ∈ teal | amber | danger | success. */
export function statusMeta(status) {
  switch (status) {
    case 'SEALED':         return { label: 'Sealed',          tone: 'success' };
    case 'AUTO_CLEARED':   return { label: 'Auto-cleared',    tone: 'success' };
    case 'ESCALATED':      return { label: 'Awaiting review', tone: 'danger' };
    case 'HUMAN_REVIEWED': return { label: 'Reviewed',        tone: 'amber' };
    case 'QUARANTINED':    return { label: 'Quarantined',     tone: 'danger' };
    case '':
    case undefined:
    case null:             return { label: 'Draft',           tone: 'teal' };
    default:               return { label: (status || '').replace(/_/g, ' '), tone: 'teal' };
  }
}

export const isAwaitingDecision = (s) => s === 'ESCALATED';
export const isComplete = (s) => s === 'SEALED' || s === 'AUTO_CLEARED';

// ── Form model ─────────────────────────────────────────────────────────────
export const EMPTY_FORM = {
  caseId: '',
  age: '', parity: '',
  lmpDate: '', usgDate: '',
  usgType: 'BPD', usgValue: '',
  bpSys: '', bpDia: '',
  urineProtein: '', glucose: '', hb: '',
};

export const USG_TYPES = ['BPD', 'CRL', 'FL', 'HC', 'AC'];

/** Field metadata used to render the PatientForm grid declaratively. */
export const FORM_FIELDS = [
  { key: 'age',          label: 'Age',            unit: 'yrs',   kind: 'number', placeholder: '29',  min: 0, max: 120 },
  { key: 'parity',       label: 'Parity',         unit: '',      kind: 'text',   placeholder: 'G3P2' },
  { key: 'lmpDate',      label: 'LMP date',       unit: '',      kind: 'date' },
  { key: 'usgDate',      label: 'USG date',       unit: '',      kind: 'date' },
  { key: 'bpSys',        label: 'BP systolic',    unit: 'mmHg',  kind: 'number', placeholder: '150', min: 40, max: 300 },
  { key: 'bpDia',        label: 'BP diastolic',   unit: 'mmHg',  kind: 'number', placeholder: '98',  min: 20, max: 200 },
  { key: 'urineProtein', label: 'Urine protein',  unit: '',      kind: 'text',   placeholder: '2+' },
  { key: 'glucose',      label: 'Fasting glucose',unit: 'mg/dL', kind: 'number', placeholder: '104', min: 20, max: 1000 },
  { key: 'hb',           label: 'Haemoglobin',    unit: 'g/dL',  kind: 'number', placeholder: '10.1',min: 2,  max: 25 },
];

const toNum = (v) => {
  if (v === '' || v === null || v === undefined) return null;
  const n = parseFloat(String(v));
  return isNaN(n) ? null : n;
};
const toStr = (v) => (v === null || v === undefined ? '' : String(v));

/** Per-field validation. Returns { field: message } for invalid entries. */
export function validateForm(form) {
  const errs = {};
  for (const f of FORM_FIELDS) {
    if (f.kind !== 'number') continue;
    const raw = form[f.key];
    if (raw === '' || raw === null || raw === undefined) continue;
    const n = toNum(raw);
    if (n === null) { errs[f.key] = 'Must be a number'; continue; }
    if (f.min !== undefined && n < f.min) errs[f.key] = `Min ${f.min}`;
    if (f.max !== undefined && n > f.max) errs[f.key] = `Max ${f.max}`;
  }
  const uv = toNum(form.usgValue);
  if (form.usgValue !== '' && (uv === null || uv <= 0)) errs.usgValue = 'Must be > 0 mm';
  return errs;
}

/**
 * Serialize the form into the orchestrator's case object.
 * `prev` (the previous parsed JSON) is merged first so any advanced/unknown
 * fields a power user added in the raw editor are preserved.
 */
export function buildCase(form, prev = {}) {
  const base = prev && typeof prev === 'object' ? JSON.parse(JSON.stringify(prev)) : {};
  const out = {
    ...base,
    case_id: form.caseId || base.case_id || '',
    demographics: {
      ...(base.demographics || {}),
      age: toNum(form.age),
      parity: form.parity || null,
    },
    lmp_date: form.lmpDate || null,
    usg_date: form.usgDate || null,
    vitals: {
      ...(base.vitals || {}),
      bp_systolic: toNum(form.bpSys),
      bp_diastolic: toNum(form.bpDia),
    },
    labs: {
      ...(base.labs || {}),
      urine_protein: form.urineProtein || null,
      fasting_glucose_mg_dl: toNum(form.glucose),
      hb_g_dl: toNum(form.hb),
    },
  };
  const uv = toNum(form.usgValue);
  out.usg_measurement = uv !== null ? { type: form.usgType || 'BPD', value_mm: uv } : null;
  return out;
}

export const buildCaseJson = (form, prev) => JSON.stringify(buildCase(form, prev), null, 2);

/** Parse a case object (from extraction or the raw editor) into form fields. */
export function parseCaseToForm(obj) {
  const o = obj || {};
  const d = o.demographics || {};
  const v = o.vitals || {};
  const l = o.labs || {};
  const m = o.usg_measurement || {};
  return {
    caseId: toStr(o.case_id),
    age: toStr(d.age),
    parity: toStr(d.parity),
    lmpDate: toStr(o.lmp_date),
    usgDate: toStr(o.usg_date),
    usgType: USG_TYPES.includes(m.type) ? m.type : 'BPD',
    usgValue: toStr(m.value_mm),
    bpSys: toStr(v.bp_systolic),
    bpDia: toStr(v.bp_diastolic),
    urineProtein: toStr(l.urine_protein),
    glucose: toStr(l.fasting_glucose_mg_dl),
    hb: toStr(l.hb_g_dl),
  };
}

/** A human-readable one-line summary of the submitted patient. */
export function summarizeForm(form) {
  const bits = [];
  if (form.age) bits.push(`${form.age}y`);
  if (form.parity) bits.push(form.parity);
  return bits.join(', ') || 'Patient';
}

// ── Demo cases (parsed into forms for one-click loading) ────────────────────
export const DEMO_CASES = [
  {
    id: 'C-0001', label: 'High risk', risk: 'high',
    form: {
      ...EMPTY_FORM, caseId: 'C-0001', age: '29', parity: 'G3P2',
      lmpDate: '2025-12-01', usgDate: '2026-06-10', usgType: 'BPD', usgValue: '58',
      bpSys: '150', bpDia: '98', urineProtein: '2+', glucose: '104', hb: '10.1',
    },
  },
  {
    id: 'C-0003', label: 'Borderline', risk: 'moderate',
    form: {
      ...EMPTY_FORM, caseId: 'C-0003', age: '34', parity: 'G5P4',
      lmpDate: '2026-01-20', usgDate: '2026-06-10', usgType: 'BPD', usgValue: '52',
      bpSys: '142', bpDia: '92', urineProtein: '1+', glucose: '95', hb: '10.5',
    },
  },
  {
    id: 'C-0004', label: 'Severe', risk: 'high',
    form: {
      ...EMPTY_FORM, caseId: 'C-0004', age: '22', parity: 'G2P1',
      lmpDate: '2026-06-01', usgDate: '2026-06-10', usgType: 'CRL', usgValue: '5',
      bpSys: '165', bpDia: '105', urineProtein: '3+', glucose: '88', hb: '9.2',
    },
  },
];
