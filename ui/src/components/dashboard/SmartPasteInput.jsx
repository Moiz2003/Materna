/**
 * SmartPasteInput — the PRIMARY input method.
 *
 * A clinician pastes free-text chart notes (English or Urdu) and the AI
 * extracts structured data into the form. Demo cases load with one click.
 * This is visually dominant; the manual form and raw JSON are secondary.
 */
import { Sparkles, Loader2, Wand2, FlaskConical } from 'lucide-react';
import GlassPanel from '../ui/glass-panel';
import { DEMO_CASES } from './caseModel';

const PLACEHOLDER =
  'e.g. "29yo G3P2, LMP Dec 1 2025, USG Jun 10 2026 BPD 58mm, ' +
  'BP 150/98, urine protein 2+, fasting glucose 104, Hb 10.1…"';

export default function SmartPasteInput({
  notes, onNotesChange, onExtract, extracting, onLoadDemo, disabled, isExpert = false,
}) {
  return (
    <GlassPanel glow="teal" intensity={0.25} className="p-5">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-teal-500/15 border border-teal-500/25 flex items-center justify-center flex-shrink-0">
          <Sparkles size={18} className="text-teal-400" />
        </div>
        <div className="min-w-0">
          <h2 className="font-display font-semibold text-base text-text leading-tight">Smart Paste</h2>
          <p className="text-xs text-text-muted mt-0.5">
            Paste whatever the chart says — we’ll extract the data and fill the form.
          </p>
        </div>
      </div>

      <textarea
        rows={4}
        value={notes}
        onChange={(e) => onNotesChange(e.target.value)}
        placeholder={PLACEHOLDER}
        disabled={disabled}
        className="w-full bg-bg-dark border border-border rounded-xl p-3.5 text-sm text-text font-mono leading-relaxed placeholder:text-text-subtle focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/20 resize-y transition-colors disabled:opacity-40"
      />

      <div className="flex flex-wrap items-center gap-3 mt-3">
        <button
          onClick={onExtract}
          disabled={extracting || disabled || !notes.trim()}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-teal-600 to-teal-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-teal-500/20 hover:shadow-teal-500/30 hover:brightness-110 transition-all disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed"
        >
          {extracting
            ? <><Loader2 size={16} className="animate-spin" /> Extracting…</>
            : <><Wand2 size={16} /> Extract &amp; Fill Form</>}
        </button>

        {!isExpert && (
          <>
            <div className="flex items-center gap-2 text-xs text-text-subtle">
              <FlaskConical size={13} className="text-text-subtle" />
              <span className="font-medium uppercase tracking-wide">Demo</span>
            </div>
            {DEMO_CASES.map((c) => (
              <button
                key={c.id}
                onClick={() => onLoadDemo(c)}
                disabled={disabled}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium border border-border hover:border-teal-500/40 rounded-lg text-text-muted hover:text-text transition-all disabled:opacity-40"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${c.risk === 'high' ? 'bg-danger' : 'bg-amber-400'}`} />
                {c.id} · {c.label}
              </button>
            ))}
          </>
        )}
        {isExpert && (
          <span className="text-[10px] text-text-subtle font-mono">⌘D to load demo</span>
        )}
      </div>
    </GlassPanel>
  );
}
