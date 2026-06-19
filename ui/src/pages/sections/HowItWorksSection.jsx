import { FileCheck, Activity, Shield, Search, Stethoscope, ArrowRight, Check, X, ScanLine } from 'lucide-react';
import AgentCarousel from '../../components/effects/AgentCarousel';
import { FadeIn } from '../../components/ui/fade-in';
import { TexturePanel } from '../../components/ui/texture-panel';

/* ── Per-step schematic diagrams (claude2.md §4 "visuals per step") ── */

function IntakeDiagram() {
  return (
    <div className="flex items-center gap-3">
      <div className="w-20 h-24 rounded-lg border border-teal-500/30 bg-bg-dark/60 p-2 space-y-1.5">
        {[10, 14, 8, 12].map((w, i) => <div key={i} className="h-1.5 rounded-full bg-text-subtle/50" style={{ width: `${w * 4}px` }} />)}
      </div>
      <ArrowRight size={16} className="text-teal-400 flex-shrink-0" />
      <div className="w-20 h-24 rounded-lg border border-teal-500/40 bg-teal-500/5 p-2 space-y-1.5">
        {['age', 'lmp', 'bp', 'hb'].map((k) => (
          <div key={k} className="flex items-center gap-1">
            <span className="text-[13px] font-mono text-teal-400">{k}</span>
            <div className="h-1.5 flex-1 rounded-full bg-teal-400/30" />
          </div>
        ))}
      </div>
    </div>
  );
}

function DatingDiagram() {
  return (
    <div className="flex items-end gap-4 h-24">
      <div className="flex flex-col items-center gap-1">
        <div className="w-7 rounded-t bg-teal-400/70" style={{ height: '72px' }} />
        <span className="text-[13px] font-mono text-text-subtle">LMP</span>
      </div>
      <div className="flex flex-col items-center gap-1">
        <div className="w-7 rounded-t bg-amber-400/70" style={{ height: '46px' }} />
        <span className="text-[13px] font-mono text-text-subtle">USG</span>
      </div>
      <div className="flex flex-col items-start gap-1 pb-5">
        <span className="text-[13px] font-mono text-amber-400 font-bold">Δ 4.4w</span>
        <span className="text-[13px] font-mono text-amber-400/70">discordant</span>
      </div>
    </div>
  );
}

function GuidelineDiagram() {
  const rows = [{ ok: true, t: 'BP recheck' }, { ok: false, t: '24h protein' }, { ok: false, t: 'OGTT' }];
  return (
    <div className="w-44 rounded-lg border border-teal-500/30 bg-bg-dark/60 p-3 space-y-2">
      {rows.map((r) => (
        <div key={r.t} className="flex items-center gap-2">
          {r.ok
            ? <Check size={14} className="text-emerald-400" />
            : <X size={14} className="text-amber-400" />}
          <span className="text-[13px] font-mono text-text-muted">{r.t}</span>
        </div>
      ))}
    </div>
  );
}

function AuditorDiagram() {
  return (
    <div className="relative w-32 h-24 flex items-center justify-center">
      <div className="w-20 h-24 rounded-lg border border-amber-500/30 bg-bg-dark/60 p-2 space-y-1.5">
        {[12, 9, 14].map((w, i) => <div key={i} className="h-1.5 rounded-full bg-text-subtle/40" style={{ width: `${w * 4}px` }} />)}
      </div>
      <div className="absolute -right-1 -bottom-1 w-12 h-12 rounded-full bg-amber-500/15 ring-1 ring-amber-500/40 flex items-center justify-center">
        <Search size={20} className="text-amber-400" />
      </div>
      <span className="absolute -top-2 right-0 text-amber-400 font-mono text-[13px] font-bold">?</span>
    </div>
  );
}

function SealDiagram() {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="w-16 h-16 rounded-full bg-emerald-500/10 ring-1 ring-emerald-500/40 flex items-center justify-center">
        <Stethoscope size={26} className="text-emerald-400" />
      </div>
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/25">
        <Check size={13} className="text-emerald-400" />
        <span className="text-[13px] font-mono text-emerald-400">SEALED</span>
      </div>
    </div>
  );
}

const agents = [
  {
    icon: FileCheck, label: 'Intake', accent: 'teal', color: 'text-teal-400', bg: 'bg-teal-500/10', border: 'border-teal-500/20',
    desc: 'Paste clinical notes or upload an image. The agent extracts and normalises the data from English or Urdu handwriting into a structured case.',
    code: '_local_normalise(raw_case) → StructuredCase',
    diagram: <IntakeDiagram />,
  },
  {
    icon: Activity, label: 'Dating & Risk', accent: 'amber', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20',
    desc: 'Computes gestational age from LMP and ultrasound (Hadlock), detects discordance, and fires pre-eclampsia, GDM, and anaemia flags.',
    code: 'ga_from_ultrasound("BPD", 24.5) → 23.1 wk',
    diagram: <DatingDiagram />,
  },
  {
    icon: Shield, label: 'Guideline', accent: 'teal', color: 'text-teal-400', bg: 'bg-teal-500/10', border: 'border-teal-500/20',
    desc: 'Checks the case against the antenatal ruleset and vetoes when required investigations are missing — listing exactly what still needs doing.',
    code: 'check_schedule(structured) → ComplianceResult',
    diagram: <GuidelineDiagram />,
  },
  {
    icon: Search, label: 'Auditor', accent: 'amber', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20',
    desc: 'Adversarially challenges the Guideline agent — catching missed flags and questioning borderline decisions before anything reaches a human.',
    code: '_should_challenge(flags, compliance) → bool',
    diagram: <AuditorDiagram />,
  },
  {
    icon: Stethoscope, label: 'Human Gate', accent: 'emerald', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20',
    desc: 'Dr. Saima Javed reviews flagged cases through Band, approves or overrides, and only then is the packet cryptographically sealed.',
    code: 'must_escalate(flags, compliance) → True',
    diagram: <SealDiagram />,
  },
];

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-12 sm:py-20 px-4 sm:px-6">
      <div className="max-w-3xl mx-auto">
        <FadeIn className="text-center mb-8 sm:mb-10">
          <span className="text-text-subtle uppercase tracking-widest text-[11px] sm:text-[13px] font-semibold">How It Works</span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold mt-2 mb-3">Five specialist agents. One shared Band room.</h2>
          <p className="text-text-muted text-sm sm:text-base max-w-xl mx-auto">
            No agent calls another directly. Every handoff traverses the Band room —
            visible, auditable, and cryptographically sealed.
          </p>
        </FadeIn>

        <TexturePanel className="p-6">
          <AgentCarousel agents={agents} />
        </TexturePanel>
      </div>
    </section>
  );
}
