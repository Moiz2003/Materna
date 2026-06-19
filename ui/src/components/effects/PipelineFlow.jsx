/**
 * PipelineFlow — Animated 5-node agent pipeline with flowing SVG connectors.
 * Each node illuminates sequentially on scroll. Below: Band Room message bus.
 * Non-generic layout — no cards, no icon+title+desc pattern.
 */
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FileCheck, Activity, Shield, Search, Lock, ArrowRight } from 'lucide-react';

const NODES = [
  { icon: FileCheck, label: 'Intake', sub: 'Extract + normalise', code: '_local_normalise()', accent: 'teal' },
  { icon: Activity, label: 'Dating', sub: 'GA calc + risk flags', code: 'evaluate_all()', accent: 'amber' },
  { icon: Shield, label: 'Guideline', sub: 'Check rules + veto', code: 'check_schedule()', accent: 'teal' },
  { icon: Search, label: 'Auditor', sub: 'Adversarial review', code: '_should_challenge()', accent: 'amber' },
  { icon: Lock, label: 'Seal', sub: 'Hash chain + PDF', code: 'compute_hash()', accent: 'emerald' },
];

const ACCENT_COLORS = {
  teal:    { ring: '#2DD4BF', bg: 'rgba(45,212,191,0.08)', glow: 'rgba(45,212,191,0.20)' },
  amber:   { ring: '#F59E0B', bg: 'rgba(245,158,11,0.08)',  glow: 'rgba(245,158,11,0.18)' },
  emerald: { ring: '#059669', bg: 'rgba(5,150,105,0.08)',   glow: 'rgba(5,150,105,0.22)' },
};

/* Simple connecting line between two nodes */
function Connector({ active, color = '#1E293B' }) {
  return (
    <div className="flex items-center flex-shrink-0 mx-1 sm:mx-2">
      <div className="hidden sm:flex items-center w-10 sm:w-16 h-[2px] relative">
        <div className="absolute inset-0 bg-border rounded-full" />
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: '0%' }}
          animate={{ width: active ? '100%' : '0%' }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
        />
        {/* Flowing dot */}
        {active && (
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 w-[6px] h-[6px] rounded-full"
            style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}
            initial={{ left: '0%' }}
            animate={{ left: ['0%', '100%'] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear', delay: 0.8 }}
          />
        )}
      </div>
      {/* Arrow for mobile */}
      <ArrowRight size={14} className="sm:hidden text-border" />
    </div>
  );
}

export default function PipelineFlow({ className = '' }) {
  const [visible, setVisible] = useState(false);
  const [activeNodes, setActiveNodes] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !visible) {
          setVisible(true);
          // Illuminate nodes sequentially
          NODES.forEach((_, i) => {
            setTimeout(() => setActiveNodes((prev) => prev + 1), 350 * (i + 1));
          });
        }
      },
      { threshold: 0.3 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [visible]);

  return (
    <section ref={ref} className={`py-20 px-6 ${className}`}>
      <div className="max-w-5xl mx-auto">
        {/* Header — deliberately different from other section headers */}
        <div className="mb-12">
          <div className="flex items-center gap-2 text-teal-400 font-mono text-xs tracking-widest mb-3">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse-glow" />
            PIPELINE
          </div>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-text leading-tight max-w-2xl">
            How a case flows through Materna
          </h2>
          <p className="text-text-muted text-base mt-3 max-w-xl">
            Five agents coordinate through Band. Every handoff is visible, auditable, and
            hash-chained. No agent calls another directly.
          </p>
        </div>

        {/* Pipeline nodes — horizontal row */}
        <div className="flex items-start justify-center flex-wrap gap-y-6 mb-10">
          {NODES.map((node, i) => {
            const c = ACCENT_COLORS[node.accent];
            const isActive = i < activeNodes;
            return (
              <div key={i} className="flex items-center">
                {/* Node */}
                <motion.div
                  className="flex flex-col items-center gap-2"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={isActive ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                >
                  {/* Circle */}
                  <motion.div
                    className="relative w-16 h-16 rounded-full flex items-center justify-center"
                    style={{
                      background: isActive ? c.bg : 'rgba(15,23,42,0.6)',
                      border: `2px solid ${isActive ? c.ring : '#1E293B'}`,
                      boxShadow: isActive ? `0 0 24px ${c.glow}, inset 0 0 12px ${c.glow}` : 'none',
                    }}
                    animate={isActive ? { scale: [1, 1.05, 1] } : {}}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: i * 0.1 }}
                  >
                    <node.icon
                      size={24}
                      style={{ color: isActive ? c.ring : '#475569' }}
                      strokeWidth={1.8}
                    />
                    {/* Step number */}
                    <span
                      className="absolute -top-2 -right-2 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold font-mono"
                      style={{
                        background: isActive ? c.ring : '#1E293B',
                        color: isActive ? '#020617' : '#64748B',
                      }}
                    >
                      {i + 1}
                    </span>
                  </motion.div>

                  {/* Labels */}
                  <div className="text-center">
                    <div
                      className="font-display font-bold text-sm"
                      style={{ color: isActive ? c.ring : '#64748B' }}
                    >
                      {node.label}
                    </div>
                    <div className="text-[11px] text-text-subtle mt-0.5 font-mono">
                      {node.sub}
                    </div>
                    {/* Code reference — product substance */}
                    {isActive && (
                      <motion.div
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="mt-1.5 px-2 py-0.5 rounded-md bg-bg-dark/80 border border-border/50"
                      >
                        <code className="text-[10px] font-mono text-teal-400 tracking-tight">
                          {node.code}
                        </code>
                      </motion.div>
                    )}
                  </div>
                </motion.div>

                {/* Connector (not after last) */}
                {i < NODES.length - 1 && (
                  <Connector active={i < activeNodes - 1} color={c.ring} />
                )}
              </div>
            );
          })}
        </div>

        {/* Band Room bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={visible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 2.2 }}
          className="relative rounded-xl border border-border/60 bg-bg-card/30 backdrop-blur-sm px-5 py-4"
        >
          {/* Subtle top glow line */}
          <div className="absolute top-0 left-8 right-8 h-px bg-gradient-to-r from-transparent via-teal-400/40 to-transparent" />

          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="1" y="1" width="14" height="14" rx="3" stroke="#2DD4BF" strokeWidth="1.5" />
                  <path d="M5 8h6M8 5v6" stroke="#2DD4BF" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </div>
              <div>
                <div className="text-sm font-semibold text-text">Band Room</div>
                <div className="text-xs text-text-subtle">
                  Shared message bus — every handoff visible & auditable
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono text-text-subtle">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-teal-400" />
                SHA-256 chain
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                Tamper-evident
              </span>
            </div>
          </div>
        </motion.div>

        {/* Demo CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={visible ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 2.6 }}
          className="text-center mt-8"
        >
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300 font-medium transition-colors no-underline group"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping-slow absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-400" />
            </span>
            Run a live demo
            <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
          </a>
        </motion.div>
      </div>
    </section>
  );
}
