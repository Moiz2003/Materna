/**
 * BeforeAfter — Horizontal comparison reveal.
 * "Before" panel slides left to reveal "After" panel on scroll.
 * Used in ProblemSection to show handwritten note → structured JSON.
 */
import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function BeforeAfter({ className = '' }) {
  const [reveal, setReveal] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !reveal) setReveal(true);
      },
      { threshold: 0.4 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [reveal]);

  return (
    <div ref={ref} className={`relative ${className}`}>
      <div className="relative rounded-xl border border-border/50 bg-bg-dark/60 overflow-hidden">
        {/* BEFORE — slides left to reveal AFTER */}
        <motion.div
          className="p-5"
          initial={{ x: 0, opacity: 1 }}
          animate={reveal ? { x: '-110%', opacity: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400/60" />
            <span className="text-xs font-mono text-amber-400/70 uppercase tracking-wider">Before</span>
          </div>
          <div className="rounded-lg bg-amber-500/5 border border-amber-500/15 p-4">
            <div className="space-y-2 font-mono text-sm text-text-muted leading-relaxed">
              <div className="text-amber-400/50 text-[11px] uppercase tracking-wider mb-1">Handwritten Note</div>
              <div className="opacity-70">Patient: 28 yrs, G2P1</div>
              <div className="opacity-50">BP: 150/98, urine: ++</div>
              <div className="opacity-40">Hb: 10.2, sugar: ???</div>
              <div className="opacity-30">LMP: ~Jan 2026? (unclear)</div>
              <div className="opacity-25">...illegible handwriting...</div>
            </div>
          </div>
        </motion.div>

        {/* AFTER — revealed behind */}
        <motion.div
          className="absolute inset-0 p-5"
          initial={{ opacity: 0 }}
          animate={reveal ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2.5 h-2.5 rounded-full bg-teal-400" />
            <span className="text-xs font-mono text-teal-400 uppercase tracking-wider">After</span>
          </div>
          <div className="rounded-lg bg-teal-500/5 border border-teal-500/20 p-4">
            <div className="text-teal-400 text-[11px] uppercase tracking-wider mb-2 font-mono">
              Structured JSON · 98% confidence
            </div>
            <pre className="text-xs font-mono text-text leading-relaxed overflow-x-auto">
              <code>
                {`{
  "demographics": {"age": 28, "parity": "G2P1"},
  "vitals": {"bp_systolic": 150, "bp_diastolic": 98},
  "labs": {"urine_protein": "2+", "hb_g_dl": 10.2},
  "lmp_date": "2026-01-15",
  "validation": {"confidence": "high"}
}`}
              </code>
            </pre>
          </div>
          <div className="flex items-center gap-3 mt-3">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-teal-400" />
              <span className="text-[11px] font-mono text-teal-400/70">BP ≥140/90 → FLAG</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-[11px] font-mono text-amber-400/70">{'Hb < 11.0 → FLAG'}</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Extracted in < 3 seconds badge */}
      <motion.div
        className="flex items-center gap-2 mt-3 text-xs text-text-subtle"
        initial={{ opacity: 0 }}
        animate={reveal ? { opacity: 1 } : {}}
        transition={{ delay: 1 }}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse-glow" />
        Extracted in under 3 seconds · English & Urdu handwriting supported
      </motion.div>
    </div>
  );
}
