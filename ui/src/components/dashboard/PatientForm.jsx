/**
 * PatientForm — structured, validated input for dashboard.
 * High-contrast labels and inputs for senior clinician readability.
 */
import { ClipboardList, Stethoscope, FlaskRound, ScanLine } from 'lucide-react';
import { FORM_FIELDS, USG_TYPES } from './caseModel';

function Field({ meta, value, error, onChange }) {
  const invalid = !!error;
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-semibold text-text">
        {meta.label}
        {meta.unit && <span className="text-text-muted font-normal ml-1">({meta.unit})</span>}
      </span>
      <input
        type={meta.kind === 'date' ? 'date' : meta.kind === 'number' ? 'number' : 'text'}
        inputMode={meta.kind === 'number' ? 'decimal' : undefined}
        value={value}
        placeholder={meta.placeholder || ''}
        onChange={(e) => onChange(meta.key, e.target.value)}
        className={`bg-white/[0.06] border rounded-lg px-3 py-2.5 text-sm text-text font-medium placeholder:text-text-muted focus:outline-none focus:ring-1 transition-colors ${
          invalid
            ? 'border-danger/60 focus:border-danger focus:ring-danger/20'
            : 'border-border focus:border-teal-500/50 focus:ring-teal-500/20'
        }`}
      />
      {invalid && <span className="text-xs text-danger font-medium">{error}</span>}
    </label>
  );
}

const groupIcon = {
  patient: ClipboardList,
  vitals: Stethoscope,
  labs: FlaskRound,
};

export default function PatientForm({ form, errors = {}, onChange }) {
  const get = (k) => form[k] ?? '';
  const usgErr = errors.usgValue;

  return (
    <div className="space-y-5">
      {/* Patient + dating */}
      <section>
        <SectionLabel icon={ClipboardList} text="Patient & dating" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {FORM_FIELDS.slice(0, 4).map((meta) => (
            <Field key={meta.key} meta={meta} value={get(meta.key)} error={errors[meta.key]} onChange={onChange} />
          ))}
        </div>
      </section>

      {/* Ultrasound measurement */}
      <section>
        <SectionLabel icon={ScanLine} text="Ultrasound measurement" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold text-text">Type</span>
            <select
              value={form.usgType || 'BPD'}
              onChange={(e) => onChange('usgType', e.target.value)}
              className="bg-white/[0.06] border border-border rounded-lg px-3 py-2.5 text-sm text-text font-medium focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/20 transition-colors"
            >
              {USG_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold text-text">Value <span className="text-text-muted font-normal">(mm)</span></span>
            <input
              type="number" inputMode="decimal" value={get('usgValue')} placeholder="58"
              onChange={(e) => onChange('usgValue', e.target.value)}
              className={`bg-white/[0.06] border rounded-lg px-3 py-2.5 text-sm text-text font-medium placeholder:text-text-muted focus:outline-none focus:ring-1 transition-colors ${
                usgErr ? 'border-danger/60 focus:border-danger focus:ring-danger/20' : 'border-border focus:border-teal-500/50 focus:ring-teal-500/20'
              }`}
            />
            {usgErr && <span className="text-xs text-danger font-medium">{usgErr}</span>}
          </label>
        </div>
      </section>

      {/* Vitals */}
      <section>
        <SectionLabel icon={Stethoscope} text="Vitals" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {FORM_FIELDS.slice(4, 6).map((meta) => (
            <Field key={meta.key} meta={meta} value={get(meta.key)} error={errors[meta.key]} onChange={onChange} />
          ))}
        </div>
      </section>

      {/* Labs */}
      <section>
        <SectionLabel icon={FlaskRound} text="Labs" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {FORM_FIELDS.slice(6).map((meta) => (
            <Field key={meta.key} meta={meta} value={get(meta.key)} error={errors[meta.key]} onChange={onChange} />
          ))}
        </div>
      </section>
    </div>
  );
}

function SectionLabel({ icon: Icon, text }) {
  return (
    <div className="flex items-center gap-2 mb-2.5">
      <Icon size={14} className="text-teal-400" />
      <span className="text-xs font-bold uppercase tracking-wide text-text-muted">{text}</span>
    </div>
  );
}
