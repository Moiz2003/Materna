/**
 * AgentCarousel — interactive step-by-step walkthrough (claude2.md §4).
 *
 * Drives the "How It Works" section: one step at a time, with a STEP n/N
 * counter, a per-step visual diagram, a background tint that shifts with each
 * step's accent (teal → amber → teal → amber → emerald), animated step dots,
 * Previous/Next controls, and 5-second auto-advance that pauses on hover.
 *
 * Each `agents` entry: { icon, label, desc, accent, color, bg, border, diagram }
 *   accent ∈ 'teal' | 'amber' | 'emerald'
 */
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const spring = { type: 'spring', stiffness: 300, damping: 25, mass: 0.5 };

const ACCENT = {
  teal:    { glow: 'rgba(45,212,191,0.10)',  dot: 'bg-teal-400',    text: 'text-teal-400',    ring: 'ring-teal-500/40' },
  amber:   { glow: 'rgba(245,158,11,0.10)',  dot: 'bg-amber-400',   text: 'text-amber-400',   ring: 'ring-amber-500/40' },
  emerald: { glow: 'rgba(5,150,105,0.12)',   dot: 'bg-emerald-400', text: 'text-emerald-400', ring: 'ring-emerald-500/40' },
};

export default function AgentCarousel({ agents, interval = 5000 }) {
  const [step, setStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const n = agents.length;

  const go = useCallback((delta) => setStep((s) => (s + delta + n) % n), [n]);

  useEffect(() => {
    if (paused) return;
    const t = setInterval(() => setStep((s) => (s + 1) % n), interval);
    return () => clearInterval(t);
  }, [paused, n, interval]);

  const a = agents[step];
  const accent = ACCENT[a.accent] || ACCENT.teal;

  return (
    <div
      className="relative w-full"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      {/* Background tint shifts per step */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`bg-${step}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6 }}
          className="pointer-events-none absolute inset-0 rounded-2xl"
          style={{ background: `radial-gradient(120% 90% at 50% 0%, ${accent.glow} 0%, transparent 70%)` }}
        />
      </AnimatePresence>

      {/* Step counter */}
      <div className="relative flex items-center justify-between mb-4">
        <span className={`font-mono text-[13px] font-bold tracking-wider ${accent.text}`}>
          STEP {step + 1}/{n}
        </span>
        <span className="font-mono text-[13px] text-text-subtle uppercase tracking-wider">{a.label}</span>
      </div>

      {/* Animated step card */}
      <div className="relative min-h-[260px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, scale: 0.96, y: 14 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -14 }}
            transition={spring}
            className={`rounded-2xl border ${a.border} bg-bg-card backdrop-blur-xl`}
          >
            <div className="grid sm:grid-cols-[1fr_220px] gap-6 p-6 items-center">
              <div className="text-left">
                <motion.div
                  initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ ...spring, delay: 0.1 }}
                  className={`w-12 h-12 mb-4 rounded-xl ${a.bg} flex items-center justify-center ring-1 ${accent.ring}`}
                >
                  <a.icon size={24} className={a.color} />
                </motion.div>
                <motion.h3
                  initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}
                  className="font-display font-bold text-lg mb-2"
                >
                  {a.label}
                </motion.h3>
                <motion.p
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}
                  className="text-text-muted text-sm leading-relaxed"
                >
                  {a.desc}
                </motion.p>

                {/* Code preview — product substance */}
                {a.code && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
                    className="mt-3"
                  >
                    <pre className="text-[11px] font-mono text-teal-400/70 bg-bg-dark/60 rounded-md px-3 py-2 overflow-x-auto border border-border/30">
                      <code>{a.code}</code>
                    </pre>
                  </motion.div>
                )}
              </div>

              {/* Per-step visual diagram */}
              {a.diagram && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}
                  className="hidden sm:flex items-center justify-center"
                >
                  {a.diagram}
                </motion.div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Controls: Prev · dots · Next */}
      <div className="relative flex items-center justify-between mt-5">
        <button
          onClick={() => go(-1)}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border text-text-muted hover:text-text hover:border-text-subtle transition-all text-[13px] font-medium"
          aria-label="Previous step"
        >
          <ChevronLeft size={15} /> Previous
        </button>

        <div className="flex items-center gap-2">
          {agents.map((ag, i) => {
            const acc = ACCENT[ag.accent] || ACCENT.teal;
            return (
              <button
                key={i}
                onClick={() => setStep(i)}
                aria-label={`Go to step ${i + 1}`}
                className={`h-2 rounded-full transition-all duration-300 ${
                  i === step ? `w-6 ${acc.dot}` : 'w-2 bg-border hover:bg-text-subtle'
                }`}
              />
            );
          })}
        </div>

        <button
          onClick={() => go(1)}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border text-text-muted hover:text-text hover:border-text-subtle transition-all text-[13px] font-medium"
          aria-label="Next step"
        >
          Next <ChevronRight size={15} />
        </button>
      </div>
    </div>
  );
}
