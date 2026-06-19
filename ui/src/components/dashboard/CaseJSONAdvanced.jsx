/**
 * CaseJSONAdvanced — the raw case JSON editor, collapsed by default.
 *
 * Power users / developers can expand this to hand-edit the exact payload.
 * Edits parse back into the form so both stay in sync. A small validity
 * indicator shows whether the JSON is currently parseable.
 */
import { useState } from 'react';
import { ChevronRight, Code2, CheckCircle2, AlertCircle } from 'lucide-react';

export default function CaseJSONAdvanced({ value, onChange }) {
  const [open, setOpen] = useState(false);
  let valid = true;
  try { JSON.parse(value); } catch { valid = false; }

  return (
    <div className="border border-border rounded-xl bg-bg-dark/40 overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2.5 px-4 py-3 text-left hover:bg-bg-elevated/40 transition-colors"
        aria-expanded={open}
      >
        <ChevronRight size={16} className={`text-text-subtle transition-transform duration-200 ${open ? 'rotate-90' : ''}`} />
        <Code2 size={15} className="text-text-muted" />
        <span className="text-sm font-medium text-text-muted">Advanced — edit raw case JSON</span>
        <span className="ml-auto inline-flex items-center gap-1 text-xs">
          {valid
            ? <><CheckCircle2 size={13} className="text-success" /> <span className="text-text-subtle">valid</span></>
            : <><AlertCircle size={13} className="text-danger" /> <span className="text-danger">invalid JSON</span></>}
        </span>
      </button>

      {open && (
        <div className="px-4 pb-4">
          <textarea
            rows={12}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            spellCheck={false}
            className={`w-full bg-bg-dark border rounded-lg p-3 text-[13px] leading-relaxed text-text font-mono focus:outline-none focus:ring-1 transition-colors ${
              valid ? 'border-border focus:border-teal-500/50 focus:ring-teal-500/20' : 'border-danger/50 focus:border-danger focus:ring-danger/20'
            }`}
          />
          <p className="text-xs text-text-subtle mt-2">
            This is the exact payload sent to the review board. Editing here updates the form above.
          </p>
        </div>
      )}
    </div>
  );
}
