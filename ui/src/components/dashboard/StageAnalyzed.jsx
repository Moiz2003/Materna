/**
 * StageAnalyzed — Dating & Risk agent output with GA metrics and risk flags.
 * Click any flag to reveal clinical evidence and reasoning for doctor review.
 */
import { useState } from 'react';
import { CalendarClock, AlertTriangle, ShieldCheck, ChevronDown } from 'lucide-react';
import { FadeIn } from '../ui/fade-in';
import GlassPanel from '../ui/glass-panel';

function GaCell({ label, value, tone = 'teal', icon }) {
  const color = tone === 'amber' ? 'text-amber-400' : tone === 'success' ? 'text-success' : 'text-teal-400';
  return (
    <div className="text-center px-3 py-2.5">
      <div className="text-xs text-text-subtle uppercase tracking-wide">{label}</div>
      <div className={`font-display font-bold text-2xl ${color} mt-1 flex items-center justify-center gap-1.5`}>
        {value}{icon}
      </div>
    </div>
  );
}

const sev = {
  high:     { ring: 'border-danger/30 bg-danger/10',   dot: 'bg-danger',   text: 'text-danger',   label: 'HIGH' },
  moderate: { ring: 'border-amber-500/30 bg-amber-500/10', dot: 'bg-amber-400', text: 'text-amber-400', label: 'MOD' },
  low:      { ring: 'border-teal-500/30 bg-teal-500/10', dot: 'bg-teal-400', text: 'text-teal-400', label: 'LOW' },
};

const FLAG_INFO = {
  preeclampsia_suspected: {
    title: 'Preeclampsia Suspected',
    reasoning:
      'BP ≥ 140/90 mmHg with proteinuria (urine protein ≥ 1+) meets the diagnostic criteria for preeclampsia. ' +
      'This requires urgent obstetric evaluation, serial BP monitoring, and 24‑hour urine protein quantification.',
    evidenceLabels: { bp: 'Blood Pressure', urine_protein: 'Urine Protein' },
  },
  gdm_suspected: {
    title: 'Gestational Diabetes Suspected',
    reasoning:
      'Fasting plasma glucose ≥ 92 mg/dL meets the IADPSG single‑step threshold for gestational diabetes mellitus. ' +
      'Confirm with a 75 g oral glucose tolerance test (OGTT) at 24–28 weeks.',
    evidenceLabels: { fasting_glucose_mg_dl: 'Fasting Glucose (mg/dL)' },
  },
  anaemia: {
    title: 'Anaemia',
    reasoning:
      'Haemoglobin < 11.0 g/dL indicates anaemia in pregnancy per WHO criteria. ' +
      'Iron studies (serum ferritin, TIBC) and supplementation with oral ferrous sulphate 325 mg daily are indicated.',
    evidenceLabels: { hb_g_dl: 'Haemoglobin (g/dL)' },
  },
  dating_discordance: {
    title: 'Dating Discordance',
    reasoning:
      'Gestational age by LMP and ultrasound differ by more than the acceptable margin. ' +
      'Re‑dating by earliest ultrasound is recommended per ACOG guidelines.',
    evidenceLabels: { ga_lmp_weeks: 'GA by LMP (weeks)', ga_usg_weeks: 'GA by USG (weeks)', discordance_weeks: 'Discordance (weeks)' },
  },
};

function getFlagInfo(type) {
  return (
    FLAG_INFO[type] || {
      title: (type || 'flag').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      reasoning:
        'This risk flag was raised by the Dating & Risk agent based on clinical thresholds defined in national antenatal care guidelines. Review the evidence below and confirm or override.',
      evidenceLabels: {},
    }
  );
}

export default function StageAnalyzed({ finding = {}, flags = [] }) {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const hasGa = finding.ga_lmp_weeks != null || finding.ga_usg_weeks != null;
  const hasFlags = flags.length > 0;

  return (
    <FadeIn>
      <GlassPanel glow={hasFlags ? 'amber' : 'emerald'} intensity={hasFlags ? 0.4 : 0.25} className="p-5 space-y-4">
        <div className="flex items-center gap-2.5">
          <CalendarClock size={18} className="text-teal-400" />
          <h3 className="font-display font-semibold text-base text-text">Dating & risk</h3>
        </div>

        {hasGa && (
          <div className="rounded-xl border border-border bg-bg-dark/30 grid grid-cols-3 divide-x divide-border">
            <GaCell label="GA · LMP" value={`${finding.ga_lmp_weeks ?? '—'} wk`} />
            <GaCell label="GA · USG" value={`${finding.ga_usg_weeks ?? '—'} wk`} />
            <GaCell
              label="Discordance"
              tone={finding.discordant ? 'amber' : 'success'}
              value={`${finding.discordance_weeks ?? '—'} wk`}
              icon={finding.discordant ? <AlertTriangle size={16} /> : <ShieldCheck size={16} />}
            />
          </div>
        )}

        <div>
          <div className="flex items-center gap-2 mb-2.5">
            <AlertTriangle size={14} className="text-amber-400" />
            <span className="text-xs font-semibold uppercase tracking-wide text-text-subtle">
              Risk flags {flags.length > 0 && `(${flags.length})`}
            </span>
          </div>
          {flags.length === 0 ? (
            <div className="flex items-center gap-2 text-sm text-success font-medium">
              <ShieldCheck size={15} /> No risk flags detected — eligible for auto-clear
            </div>
          ) : (
            <div className="space-y-2">
              {flags.map((fl, i) => {
                const s = sev[fl.severity] || sev.low;
                const info = getFlagInfo(fl.type);
                const isOpen = expandedIndex === i;
                return (
                  <div key={i} className={`rounded-lg border ${s.ring} bg-bg-dark/30 overflow-hidden transition-all`}>
                    <button
                      type="button"
                      onClick={() => setExpandedIndex(isOpen ? null : i)}
                      className="w-full flex items-center gap-2.5 px-3 py-2.5 hover:bg-bg-dark/50 transition-colors text-left cursor-pointer"
                    >
                      <span className={`w-2 h-2 rounded-full ${s.dot} flex-shrink-0`} />
                      <span className={`text-xs font-bold ${s.text} w-10`}>{s.label}</span>
                      <span className="text-sm font-semibold text-text flex-1">{info.title}</span>
                      {fl.rule_ref && (
                        <span className="text-xs text-text-subtle font-mono bg-bg-dark/60 px-1.5 py-0.5 rounded">
                          {fl.rule_ref}
                        </span>
                      )}
                      <ChevronDown size={14} className={`text-text-subtle flex-shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
                    </button>
                    {isOpen && (
                      <div className="px-3 pb-3 pt-1 border-t border-border/50 space-y-3">
                        <p className="text-xs text-text-subtle leading-relaxed">{info.reasoning}</p>
                        {fl.evidence && Object.keys(fl.evidence).length > 0 && (
                          <div className="rounded-md bg-bg-dark/60 p-2.5 space-y-1.5">
                            <span className="text-[10px] uppercase tracking-widest text-text-subtle font-semibold">Clinical Evidence</span>
                            {Object.entries(fl.evidence).map(([key, val]) => (
                              <div key={key} className="flex justify-between items-center text-xs">
                                <span className="text-text-subtle">{info.evidenceLabels[key] || key.replace(/_/g, ' ')}</span>
                                <span className="font-mono font-semibold text-text">{String(val)}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </GlassPanel>
    </FadeIn>
  );
}
