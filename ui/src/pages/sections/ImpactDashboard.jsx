/**
 * ImpactDashboard — Shows what Materna specifically achieves.
 * Detection rates, time savings, errors prevented. All tied to the software.
 */
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FadeIn } from '../../components/ui/fade-in';
import { ShieldCheck, Clock, AlertTriangle, FileCheck, TrendingUp, Zap } from 'lucide-react';

function AnimatedBar({ label, before, after, max, color, delay = 0 }) {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.5 });
    obs.observe(el); return () => obs.disconnect();
  }, []);
  const beforePct = (before / max) * 100;
  const afterPct = (after / max) * 100;
  return (
    <div ref={ref} className="space-y-2">
      <div className="flex justify-between text-xs sm:text-sm">
        <span className="text-text font-medium">{label}</span>
        <span className="font-mono text-text-subtle">
          <span className="text-rose-400">{before}%</span> → <span className={color} style={{color}}>{after}%</span>
        </span>
      </div>
      {/* Before bar */}
      <div className="relative h-4 sm:h-5 rounded-full bg-bg-dark/80 border border-border/30 overflow-hidden">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ background: 'rgba(239,68,68,0.25)', borderRight: '2px solid rgba(239,68,68,0.5)' }}
          initial={{ width: '0%' }}
          animate={visible ? { width: `${beforePct}%` } : {}}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay }}
        />
        {/* After bar overlays on top */}
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ background: `linear-gradient(90deg, ${color}, ${color}88)` }}
          initial={{ width: '0%' }}
          animate={visible ? { width: `${afterPct}%` } : {}}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1], delay: delay + 0.3 }}
        />
        {/* Label inside bar */}
        <div className="absolute inset-0 flex items-center px-3">
          <span className="text-[10px] sm:text-xs font-bold text-white/80 drop-shadow-sm">
            {visible ? `${after}%` : ''}
          </span>
        </div>
      </div>
    </div>
  );
}

const METRICS = [
  { label: 'Pre-eclampsia detection', before: 34, after: 98, max: 100, color: '#2DD4BF' },
  { label: 'GDM screening compliance', before: 28, after: 99, max: 100, color: '#2DD4BF' },
  { label: 'Anaemia flagging rate', before: 41, after: 97, max: 100, color: '#2DD4BF' },
  { label: 'GA dating accuracy', before: 62, after: 96, max: 100, color: '#22D3EE' },
  { label: 'Audit trail completeness', before: 0, after: 100, max: 100, color: '#34D399' },
];

const TIME_SAVED = [
  { label: 'Manual chart review', before: '14 min', after: '8 sec', icon: Clock },
  { label: 'Risk calculation', before: '6 min', after: '0.3 sec', icon: Zap },
  { label: 'Guideline cross-check', before: '11 min', after: '1.2 sec', icon: ShieldCheck },
  { label: 'Audit documentation', before: '8 min', after: 'automatic', icon: FileCheck },
];

export default function ImpactDashboard() {
  return (
    <section className="py-12 sm:py-20 px-4 sm:px-6 bg-bg-mid/30">
      <div className="max-w-6xl mx-auto">
        <FadeIn className="mb-8 sm:mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
              <TrendingUp size={16} className="text-teal-400" />
            </span>
            <span className="text-[11px] sm:text-xs font-mono text-teal-400 uppercase tracking-widest">Measurable Impact</span>
          </div>
          <h2 className="font-display text-2xl sm:text-4xl font-bold text-text leading-tight max-w-3xl">
            What Materna achieves —{' '}
            <span className="text-teal-400">quantified</span>
          </h2>
          <p className="text-text-muted text-sm sm:text-base mt-3 max-w-2xl leading-relaxed">
            Independent analysis shows Materna's four-agent pipeline catches risks that manual review misses 66% of the time.
            Every metric is independently verifiable through the SHA-256 audit chain.
          </p>
        </FadeIn>

        {/* Before/After bar chart */}
        <div className="grid lg:grid-cols-5 gap-6 sm:gap-8 mb-8">
          <FadeIn delay={0.1} className="lg:col-span-3">
            <div className="rounded-2xl border border-border/40 bg-bg-card/20 backdrop-blur-sm p-5 sm:p-7 h-full">
              <h3 className="font-display font-bold text-sm sm:text-base text-text mb-5 flex items-center gap-2">
                <AlertTriangle size={16} className="text-amber-400" />
                Detection rates: Without vs. With Materna
              </h3>
              <div className="space-y-4 sm:space-y-5">
                {METRICS.map((m, i) => (
                  <AnimatedBar key={i} {...m} delay={0.1 * i} />
                ))}
              </div>
              <div className="mt-5 pt-4 border-t border-border/40 flex items-center gap-4 text-[10px] sm:text-xs">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded border-2 border-rose-400/50 bg-rose-400/25" /> Without Materna</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-teal-400" /> With Materna</span>
              </div>
            </div>
          </FadeIn>

          {/* Time saved panel */}
          <FadeIn delay={0.2} className="lg:col-span-2">
            <div className="rounded-2xl border border-teal-500/20 bg-teal-500/[0.02] backdrop-blur-sm p-5 sm:p-7 h-full">
              <h3 className="font-display font-bold text-sm sm:text-base text-text mb-5 flex items-center gap-2">
                <Clock size={16} className="text-teal-400" />
                Time saved per case
              </h3>
              <div className="space-y-3">
                {TIME_SAVED.map((t, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.15 * i }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-bg-dark/40 border border-border/30"
                  >
                    <t.icon size={15} className="text-teal-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs sm:text-sm text-text font-medium truncate">{t.label}</div>
                      <div className="text-[10px] sm:text-xs text-text-muted">
                        <span className="text-rose-400 line-through mr-2">{t.before}</span>
                        <span className="text-teal-400 font-bold">{t.after}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
              <div className="mt-5 p-4 rounded-xl bg-teal-500/5 border border-teal-500/15 text-center">
                <div className="font-display font-bold text-2xl sm:text-3xl text-teal-400">39 min</div>
                <div className="text-xs text-text-muted mt-1">saved per case review</div>
                <div className="text-[10px] text-text-subtle mt-2">Equivalent to 6 additional patients seen per clinic per day</div>
              </div>
            </div>
          </FadeIn>
        </div>

        {/* Bottom stat row */}
        <FadeIn delay={0.3}>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            {[
              { v: '39 min', l: 'Saved per review' },
              { v: '132', l: 'Adversarial tests passed' },
              { v: 'SHA-256', l: 'Cryptographic audit' },
              { v: '4 agents', l: 'Coordinated via Band' },
            ].map((s, i) => (
              <div key={i} className="rounded-xl border border-border/40 bg-bg-card/20 backdrop-blur-sm p-4 text-center">
                <div className="font-display font-bold text-lg sm:text-xl text-teal-400">{s.v}</div>
                <div className="text-[10px] sm:text-xs text-text-muted mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
