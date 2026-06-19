/**
 * StageDecision — Cure MD-grade human-in-the-loop review.
 * Horizontal decision rail with satisfying click feedback.
 * AI recommendation on top, doctor's action on bottom.
 */
import { useState, useEffect, useRef } from 'react';
import {
  Stethoscope, Sparkles, FileText, Activity, FlaskRound,
  Check, RotateCcw, Loader2, ArrowRight, ShieldCheck,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { FadeIn } from '../ui/fade-in';
import GlassPanel from '../ui/glass-panel';

/* ── Ripple effect on click ── */
function RippleButton({ onClick, disabled, children, className = '', variant = 'primary' }) {
  const [ripples, setRipples] = useState([]);
  const [pressed, setPressed] = useState(false);
  const ref = useRef(null);

  const addRipple = (e) => {
    if (disabled) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now();
    setRipples((r) => [...r, { id, x, y }]);
    setTimeout(() => setRipples((r) => r.filter((ri) => ri.id !== id)), 600);
    onClick?.();
  };

  const base =
    variant === 'primary'
      ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20'
      : 'bg-amber-600/10 hover:bg-amber-600/20 border border-amber-500/25 text-amber-400';

  return (
    <motion.button
      ref={ref}
      onClick={addRipple}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      disabled={disabled}
      animate={pressed ? { scale: 0.97 } : { scale: 1 }}
      transition={{ type: 'spring', stiffness: 500, damping: 25 }}
      className={`relative overflow-hidden flex-1 flex items-center justify-center gap-3 py-4 rounded-2xl font-bold text-base transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${base} ${className}`}
    >
      {ripples.map((r) => (
        <span
          key={r.id}
          className="absolute rounded-full bg-white/20 pointer-events-none animate-ripple"
          style={{ left: r.x - 25, top: r.y - 25, width: 50, height: 50 }}
        />
      ))}
      <span className="relative z-10 flex items-center gap-3">{children}</span>
      <style>{`
        .animate-ripple { animation: ripple-out 0.6s ease-out forwards; }
        @keyframes ripple-out { to { transform: scale(6); opacity: 0; } }
      `}</style>
    </motion.button>
  );
}

/* ── Plan loading skeleton (teal theme) ── */
const DRAFT_STEPS = [
  'Analysing risk flags…',
  'Cross-referencing guidelines…',
  'Drafting impression…',
  'Selecting treatments…',
  'Ordering investigations…',
  'Finalising for review…',
];

function PlanSkeleton() {
  const [step, setStep] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setStep((s) => (s + 1) % DRAFT_STEPS.length), 1800);
    return () => clearInterval(t);
  }, []);
  useEffect(() => {
    const t = setInterval(() => setElapsed((e) => parseFloat((e + 0.1).toFixed(1))), 100);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="rounded-2xl border border-teal-500/10 bg-teal-500/[0.02] p-6 relative overflow-hidden">
      <motion.div
        className="absolute left-0 right-0 h-px pointer-events-none"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(45,212,191,0.25), transparent)' }}
        animate={{ top: ['0%', '100%'] }}
        transition={{ duration: 2.8, repeat: Infinity, ease: 'linear' }}
      />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}>
              <Loader2 size={18} className="text-teal-400" />
            </motion.div>
            <span className="text-sm font-bold text-teal-400">AI is drafting your treatment plan</span>
          </div>
          <span className="text-xs font-mono text-teal-400/50 tabular-nums">{elapsed.toFixed(1)}s</span>
        </div>
        <AnimatePresence mode="wait">
          <motion.p key={step} initial={{ opacity: 0, y: 3 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -3 }} transition={{ duration: 0.25 }} className="text-xs text-teal-400/40 mb-5">
            {DRAFT_STEPS[step]}
          </motion.p>
        </AnimatePresence>
        <div className="space-y-4">
          <div><div className="h-3 w-28 rounded bg-teal-500/10 mb-2" /><div className="h-2 rounded bg-teal-500/[0.04] w-full animate-pulse" /><div className="h-2 rounded bg-teal-500/[0.04] w-4/5 mt-1.5 animate-pulse" style={{ animationDelay: '0.2s' }} /></div>
          <div><div className="h-3 w-20 rounded bg-teal-500/10 mb-2" />{[1,2,3].map(n=><div key={n} className="flex items-center gap-2 mt-1.5"><div className="w-1 h-1 rounded-full bg-teal-500/15" /><div className="h-2 rounded bg-teal-500/[0.04] animate-pulse" style={{width:`${70-n*10}%`,animationDelay:`${n*0.2}s`}} /></div>)}</div>
          <div><div className="h-3 w-32 rounded bg-teal-500/10 mb-2" /><div className="flex items-center gap-2 mt-1.5"><div className="w-1 h-1 rounded-full bg-teal-500/15" /><div className="h-2 rounded bg-teal-500/[0.04] w-1/2 animate-pulse" style={{animationDelay:'0.6s'}} /></div></div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════ */

export default function StageDecision({
  plan, brief = {}, reviewer, note, reprocessing,
  onReviewerChange, onNoteChange, onDecision,
}) {
  const planLoading = !plan;
  const reasons = brief.reason || [];

  return (
    <FadeIn>
      <div className="space-y-4">
        {/* ── Escalation notice (clean, minimal) ── */}
        <div className="flex items-center gap-3 px-4 py-3 rounded-2xl border border-amber-500/15 bg-amber-500/[0.03]">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse-glow flex-shrink-0" />
          <p className="text-sm text-text-muted">
            <span className="text-amber-400 font-bold">Attention required.</span>
            {' '}This case was escalated for human review. Your decision will be cryptographically recorded.
          </p>
        </div>

        {/* ── AI Recommendation Card ── */}
        <GlassPanel glow="teal" intensity={0.25} className="p-6">
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-9 h-9 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
              <Sparkles size={17} className="text-teal-400" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base text-text">AI Recommendation</h3>
              <p className="text-xs text-text-dim">
                Generated from {reasons.length} escalation reason{reasons.length !== 1 ? 's' : ''}
                {plan && <> · {plan.source === 'ai' ? 'AI-drafted' : 'Rule-based'}{plan.iteration > 1 ? ` · ${plan.iteration - 1} revision${plan.iteration > 2 ? 's' : ''}` : ''}</>}
              </p>
            </div>
          </div>

          {planLoading ? (
            <PlanSkeleton />
          ) : plan && (
            <div className="space-y-5">
              {/* Impression */}
              {plan.impression && (
                <div className="p-4 rounded-xl bg-teal-500/[0.03] border border-teal-500/10">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-400 mb-2 block">Clinical Impression</span>
                  <p className="text-sm text-text-muted leading-relaxed">{plan.impression}</p>
                </div>
              )}

              {/* Treatment + Investigations side by side on desktop */}
              <div className="grid sm:grid-cols-2 gap-4">
                {(plan.treatment || []).length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2.5">
                      <Activity size={14} className="text-teal-400" />
                      <span className="text-sm font-bold text-text">Treatment</span>
                    </div>
                    <ol className="space-y-1.5">
                      {plan.treatment.map((t, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-text-muted">
                          <span className="text-xs font-bold text-teal-400 font-mono mt-0.5 flex-shrink-0">{i + 1}.</span>
                          <span className="leading-relaxed">{t}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
                {(plan.investigations || []).length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2.5">
                      <FlaskRound size={14} className="text-teal-400" />
                      <span className="text-sm font-bold text-text">Investigations</span>
                    </div>
                    <ul className="space-y-1.5">
                      {plan.investigations.map((x, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-text-muted">
                          <span className="w-1 h-1 rounded-full bg-teal-400/60 mt-1.5 flex-shrink-0" />
                          <span className="leading-relaxed">{x}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </GlassPanel>

        {/* ── Reprocessing notice ── */}
        {reprocessing && (
          <div className="flex items-center gap-3 px-4 py-3 rounded-2xl border border-amber-500/20 bg-amber-500/5">
            <Loader2 size={16} className="text-amber-400 animate-spin" />
            <span className="text-sm text-amber-400 font-medium">AI re-drafting the plan with your instruction…</span>
          </div>
        )}

        {/* ── Decision bar (horizontal) ── */}
        <GlassPanel glow="amber" intensity={0.2} className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <Stethoscope size={17} className="text-amber-400" />
            <span className="font-display font-bold text-base text-text">Your Decision</span>
          </div>

          {/* Inputs — compact horizontal on desktop */}
          <div className="grid sm:grid-cols-2 gap-4 mb-5">
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-bold text-text-muted uppercase tracking-wider">Reviewing Obstetrician</span>
              <input
                value={reviewer}
                onChange={(e) => onReviewerChange(e.target.value)}
                placeholder="Dr. Saima Javed"
                className="bg-white/[0.06] border border-border rounded-xl px-3.5 py-3 text-sm text-text font-semibold placeholder:text-text-muted focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/20"
              />
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-bold text-text-muted uppercase tracking-wider">Clinical Instruction <span className="text-text-dim font-normal normal-case">(to override)</span></span>
              <input
                value={note}
                onChange={(e) => onNoteChange(e.target.value)}
                placeholder="e.g. Start methyldopa 250 mg BD; repeat BP in 4h"
                className="bg-white/[0.06] border border-border rounded-xl px-3.5 py-3 text-sm text-text font-semibold placeholder:text-text-muted focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/20"
              />
            </label>
          </div>

          {/* Horizontal action buttons */}
          <div className="flex gap-4">
            <RippleButton
              variant="primary"
              onClick={() => onDecision('approve')}
              disabled={reprocessing || planLoading}
            >
              <Check size={22} />
              <span>Approve & Seal</span>
            </RippleButton>

            <RippleButton
              variant="secondary"
              onClick={() => onDecision('override')}
              disabled={reprocessing || planLoading || !note.trim()}
            >
              <RotateCcw size={22} />
              <span>Override & Re-process</span>
            </RippleButton>
          </div>

          <p className="text-xs text-text-dim text-center mt-4">
            <ShieldCheck size={11} className="inline mr-1" />
            Your decision seals the case. SHA-256 audit chain. Synthetic data only.
          </p>
        </GlassPanel>
      </div>
    </FadeIn>
  );
}
