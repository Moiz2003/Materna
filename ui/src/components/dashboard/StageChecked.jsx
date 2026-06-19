/**
 * StageChecked — Guideline + Auditor output. Shows compliance verdict,
 * missing investigations, and any auditor challenge with narrative.
 */
import { Scale, ShieldAlert, ShieldCheck, SearchCheck, Search } from 'lucide-react';
import { FadeIn } from '../ui/fade-in';
import GlassPanel from '../ui/glass-panel';

export default function StageChecked({ compliance = {}, auditor = {} }) {
  const hasCompliance = compliance.veto !== undefined;
  const hasAuditor = auditor.challenged !== undefined;
  if (!hasCompliance && !hasAuditor) return null;

  const isVetoed = compliance.veto;
  const isChallenged = auditor.challenged;

  return (
    <FadeIn>
      <GlassPanel glow={isVetoed || isChallenged ? 'amber' : 'teal'} intensity={0.35} className="p-5 space-y-4">
        <div className="flex items-center gap-2.5">
          <Scale size={18} className="text-teal-400" />
          <h3 className="font-display font-semibold text-base text-text">Guideline & audit</h3>
        </div>

        {hasCompliance && (
          <div className={`rounded-xl border px-4 py-3 ${isVetoed ? 'border-danger/25 bg-danger/10' : 'border-success/25 bg-success/10'}`}>
            <div className={`flex items-center gap-2 text-sm font-bold ${isVetoed ? 'text-danger' : 'text-success'}`}>
              {isVetoed ? <ShieldAlert size={16} /> : <ShieldCheck size={16} />}
              {isVetoed ? 'VETO — human review required' : 'Compliant with antenatal guidelines'}
            </div>
            {isVetoed && (compliance.missing_investigations || []).length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {compliance.missing_investigations.map((m, i) => (
                  <span key={i} className="text-xs font-mono px-2 py-1 rounded-md bg-danger/10 border border-danger/20 text-danger">
                    {m}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {hasAuditor && (
          isChallenged ? (
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 space-y-2">
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
                <Search size={15} /> Auditor challenged the guideline result
              </div>
              {auditor.narrative && <p className="text-sm text-text-muted leading-relaxed">{auditor.narrative}</p>}
              {(auditor.reasons || []).length > 0 && (
                <ul className="text-xs text-amber-400/90 space-y-0.5 list-disc ml-4">
                  {auditor.reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-success font-medium">
              <SearchCheck size={15} /> Auditor concurred — no challenge raised
            </div>
          )
        )}
      </GlassPanel>
    </FadeIn>
  );
}
