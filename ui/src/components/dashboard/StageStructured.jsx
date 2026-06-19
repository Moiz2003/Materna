/**
 * StageStructured — first results card. Confirms the case was normalized by
 * the Intake agent and echoes the structured patient data back to the user.
 */
import { CheckCircle2, Loader2 } from 'lucide-react';
import { FadeIn } from '../ui/fade-in';
import GlassPanel from '../ui/glass-panel';
import { summarizeForm, completedSteps } from './caseModel';

function Cell({ label, value }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-text-subtle uppercase tracking-wide">{label}</span>
      <span className="text-sm text-text font-medium">{value || '—'}</span>
    </div>
  );
}

export default function StageStructured({ form, status }) {
  const analyzing = completedSteps(status) < 4 && status !== 'AUTO_CLEARED';
  const bp = form.bpSys && form.bpDia ? `${form.bpSys}/${form.bpDia}` : '—';
  return (
    <FadeIn>
      <GlassPanel glow="teal" intensity={0.35} className="p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <CheckCircle2 size={18} className="text-success" />
          <h3 className="font-display font-semibold text-base text-text">Case structured</h3>
          <span className="text-sm text-text-muted">· {summarizeForm(form)}</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Cell label="LMP" value={form.lmpDate} />
          <Cell label="USG date" value={form.usgDate} />
          <Cell label={`USG ${form.usgType || ''}`} value={form.usgValue ? `${form.usgValue} mm` : ''} />
          <Cell label="BP" value={bp} />
          <Cell label="Urine protein" value={form.urineProtein} />
          <Cell label="Glucose" value={form.glucose ? `${form.glucose} mg/dL` : ''} />
          <Cell label="Hb" value={form.hb ? `${form.hb} g/dL` : ''} />
          <Cell label="Parity" value={form.parity} />
        </div>
        {analyzing && (
          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border text-sm text-teal-400">
            <Loader2 size={15} className="animate-spin" />
            Analyzing — agents coordinating through Band…
          </div>
        )}
      </GlassPanel>
    </FadeIn>
  );
}
