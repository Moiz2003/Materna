/**
 * ClinicalEvidence — Third-person case studies showing Materna's impact
 * through specific clinical scenarios. Before/After format with metrics.
 * Visually: alternating horizontal cards with large stat callouts.
 */
import { FadeIn } from '../../components/ui/fade-in';
import { ShieldCheck, Clock, AlertTriangle, Stethoscope, TrendingUp, FileCheck } from 'lucide-react';

const CASES = [
  {
    id: 'C-0001',
    title: 'Missed Pre-eclampsia — Caught in 8 Seconds',
    before: 'A 32-year-old G3P2 at 31 weeks presented with BP 150/98 and 2+ proteinuria. In a manual review at a busy OPD, the overworked registrar noted "BP slightly elevated — recheck next visit." The patient was sent home. She returned 4 days later with severe pre-eclampsia, requiring emergency C-section at 32 weeks.',
    after: 'Materna\'s Intake Agent normalised the vitals in 0.8 seconds. The Dating & Risk Agent fired a HIGH-severity pre-eclampsia flag. The Guideline Agent vetoed the case — 24h protein quantification and serial BP monitoring were marked as critical missing investigations. The Auditor Agent confirmed all three flags. Dr. Saima Javed reviewed and approved the escalation in under 60 seconds.',
    outcome: 'The case was flagged, escalated, and sealed with a SHA-256 audit trail before the patient left the examination room.',
    metrics: [
      { v: '8s', l: 'Time to flag' },
      { v: '3', l: 'Agents confirmed PE' },
      { v: 'SHA-256', l: 'Audit sealed' },
    ],
  },
  {
    id: 'C-0004',
    title: 'Dating Discordance — 5mm CRL That Changed Everything',
    before: 'A 22-year-old G2P1\'s LMP suggested 11 weeks gestation. The ultrasound showed CRL of 5mm — consistent with approximately 6 weeks. The handwritten report noted "dates correlate with LMP" because the sonographer misread the chart. The 5-week discordance went undetected through three subsequent visits.',
    after: 'Materna\'s Dating & Risk Agent independently computed GA from both LMP (Hadlock formula) and ultrasound measurement. The 5.0-week discordance triggered an immediate flag. The dating error was surfaced before any clinical decisions were made — preventing incorrect viability assessment, inaccurate anomaly scan scheduling, and erroneous growth charting.',
    outcome: 'The discordance was caught at the first antenatal visit, preventing a cascade of clinical errors spanning the entire pregnancy.',
    metrics: [
      { v: '5.0w', l: 'Discordance detected' },
      { v: '2', l: 'Agents flagged error' },
      { v: '100%', l: 'Deterministic detection' },
    ],
  },
  {
    id: 'C-0003',
    title: 'Triple Flag — One Case, Three Silent Risks',
    before: 'A 34-year-old G5P4 presented with borderline BP 142/92, fasting glucose of 95 mg/dL, and Hb of 10.5 g/dL. In a typical antenatal clinic, each value would be noted separately — the BP "slightly elevated," the glucose "just under threshold," the Hb "mildly low." No single finding triggered alarm. The patient\'s high parity and age multiplied her risk profile, but no one connected the dots.',
    after: 'Materna processed all values simultaneously. The Dating & Risk Agent fired all three flags — pre-eclampsia (borderline BP + high parity), GDM (glucose ≥ 92 per IADPSG), and anaemia (Hb < 11.0). The Guideline Agent issued a compliance veto — OGTT and iron studies were ordered. The human reviewer confirmed all three flags in one review session.',
    outcome: 'Three independent, compounding risks identified in a single pass. Each with audit-traced clinical evidence — BP reading, lab value, and guideline reference.',
    metrics: [
      { v: '3/3', l: 'Flags detected' },
      { v: '< 10s', l: 'Full review time' },
      { v: 'Audited', l: 'Every state transition' },
    ],
  },
];

export default function ClinicalEvidence() {
  return (
    <section className="py-12 sm:py-20 px-4 sm:px-6 bg-bg-mid/30">
      <div className="max-w-6xl mx-auto">
        <FadeIn className="mb-8 sm:mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <Stethoscope size={16} className="text-emerald-400" />
            </span>
            <span className="text-[11px] sm:text-xs font-mono text-emerald-400 uppercase tracking-widest">Clinical Evidence</span>
          </div>
          <h2 className="font-display text-2xl sm:text-4xl font-bold text-text leading-tight max-w-3xl">
            Real clinical scenarios.{' '}
            <span className="text-emerald-400">Real impact</span>.
          </h2>
          <p className="text-text-muted text-sm sm:text-base mt-3 max-w-2xl leading-relaxed">
            Three cases that demonstrate how Materna's multi-agent pipeline catches what manual review misses.
            Each uses synthetic data derived from real clinical patterns seen in Pakistani antenatal clinics.
          </p>
        </FadeIn>

        <div className="space-y-6 sm:space-y-8">
          {CASES.map((c, i) => (
            <FadeIn key={c.id} delay={0.12 * i}>
              <div className="rounded-2xl border border-border/40 bg-bg-card/20 backdrop-blur-sm overflow-hidden">
                {/* Case header */}
                <div className="px-5 sm:px-7 py-4 sm:py-5 border-b border-border/30 flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                      <FileCheck size={18} className="text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-sm sm:text-base text-text">{c.title}</h3>
                      <span className="text-[10px] sm:text-xs text-text-subtle font-mono">Case {c.id} · Synthetic data · Derived from clinical patterns</span>
                    </div>
                  </div>
                  {/* Compact metrics */}
                  <div className="flex gap-3 sm:gap-5">
                    {c.metrics.map((m, j) => (
                      <div key={j} className="text-center">
                        <div className="font-display font-bold text-lg sm:text-xl text-emerald-400">{m.v}</div>
                        <div className="text-[9px] sm:text-[10px] text-text-muted uppercase tracking-wide">{m.l}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Before/After split */}
                <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-border/30">
                  {/* Before */}
                  <div className="p-5 sm:p-7">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-2.5 h-2.5 rounded-full bg-rose-400/60" />
                      <span className="text-[10px] sm:text-xs font-mono text-rose-400/80 uppercase tracking-wider font-bold">Without Materna</span>
                    </div>
                    <div className="rounded-xl bg-rose-500/5 border border-rose-500/10 p-4">
                      <p className="text-xs sm:text-sm text-text-muted leading-relaxed">{c.before}</p>
                    </div>
                  </div>
                  {/* After */}
                  <div className="p-5 sm:p-7">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                      <span className="text-[10px] sm:text-xs font-mono text-emerald-400 uppercase tracking-wider font-bold">With Materna</span>
                    </div>
                    <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-4">
                      <p className="text-xs sm:text-sm text-text-muted leading-relaxed">{c.after}</p>
                    </div>
                  </div>
                </div>

                {/* Outcome footer */}
                <div className="px-5 sm:px-7 py-3 sm:py-4 border-t border-border/30 bg-bg-dark/20">
                  <div className="flex items-center gap-2">
                    <TrendingUp size={14} className="text-emerald-400 flex-shrink-0" />
                    <p className="text-[10px] sm:text-xs text-emerald-400/80 font-medium leading-relaxed">{c.outcome}</p>
                  </div>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
