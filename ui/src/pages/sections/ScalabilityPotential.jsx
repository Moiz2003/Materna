/**
 * ScalabilityPotential — Shows Materna's deployment trajectory and projected
 * impact from pilot clinic to national scale. Visual: milestone timeline with
 * cumulative impact counters.
 */
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FadeIn } from '../../components/ui/fade-in';
import { Building2, Globe, Users, Heart, ArrowRight, Zap } from 'lucide-react';

const MILESTONES = [
  {
    phase: 'Pilot',
    icon: Building2,
    scale: '1 clinic',
    cases: '500 cases/month',
    impact: '39 min saved per case · 100% audit compliance',
    color: '#2DD4BF',
  },
  {
    phase: 'District',
    icon: Users,
    scale: '10 clinics',
    cases: '5,000 cases/month',
    impact: '~325 hours of clinician time saved monthly · Full district coverage',
    color: '#22D3EE',
  },
  {
    phase: 'Provincial',
    icon: Globe,
    scale: '100 clinics',
    cases: '50,000 cases/month',
    impact: '3,250 hours saved · 98%+ risk detection rate maintained',
    color: '#F59E0B',
  },
  {
    phase: 'National',
    icon: Heart,
    scale: '1,000+ clinics',
    cases: '500,000 cases/month',
    impact: 'Projected 73% reduction in missed PE/GDM/anaemia · 32,500 hours saved monthly',
    color: '#34D399',
  },
];

function MilestoneCard({ m, index, total }) {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.3 });
    obs.observe(el); return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="relative flex items-start gap-4 sm:gap-6 group">
      {/* Timeline line + dot */}
      <div className="flex flex-col items-center flex-shrink-0">
        <motion.div
          className="w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center border-2"
          style={{ background: `${m.color}15`, borderColor: `${m.color}50` }}
          initial={{ scale: 0 }}
          animate={visible ? { scale: 1 } : {}}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          <m.icon size={18} style={{ color: m.color }} />
        </motion.div>
        {index < total - 1 && (
          <motion.div
            className="w-0.5 flex-1 min-h-[60px] sm:min-h-[80px] mt-2"
            style={{ background: `linear-gradient(to bottom, ${m.color}60, transparent)` }}
            initial={{ scaleY: 0 }}
            animate={visible ? { scaleY: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
          />
        )}
      </div>

      {/* Content */}
      <motion.div
        className="flex-1 pb-8 sm:pb-10"
        initial={{ opacity: 0, x: -20 }}
        animate={visible ? { opacity: 1, x: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.15 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <span className="font-display font-bold text-sm sm:text-base" style={{ color: m.color }}>{m.phase}</span>
          <ArrowRight size={12} className="text-text-subtle" />
          <span className="text-[11px] sm:text-xs text-text-muted font-mono">{m.scale}</span>
        </div>
        <div className="rounded-xl border border-border/40 bg-bg-card/20 backdrop-blur-sm p-4 sm:p-5">
          <div className="flex items-baseline gap-2 mb-3">
            <span className="font-display font-bold text-lg sm:text-2xl" style={{ color: m.color }}>{m.cases}</span>
            <span className="text-[10px] sm:text-xs text-text-subtle">processed</span>
          </div>
          <p className="text-xs sm:text-sm text-text-muted leading-relaxed">{m.impact}</p>
        </div>
      </motion.div>
    </div>
  );
}

export default function ScalabilityPotential() {
  return (
    <section className="py-12 sm:py-20 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <FadeIn className="mb-8 sm:mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
              <Globe size={16} className="text-teal-400" />
            </span>
            <span className="text-[11px] sm:text-xs font-mono text-teal-400 uppercase tracking-widest">Deployment Trajectory</span>
          </div>
          <h2 className="font-display text-2xl sm:text-4xl font-bold text-text leading-tight max-w-3xl">
            From one clinic to a{' '}
            <span className="text-teal-400">national safety net</span>
          </h2>
          <p className="text-text-muted text-sm sm:text-base mt-3 max-w-2xl leading-relaxed">
            Materna's architecture scales linearly — each new clinic is an independent Band room with identical
            deterministic safeguards. No additional AI training. No new infrastructure.
          </p>
        </FadeIn>

        {/* Timeline */}
        <div className="pl-2 sm:pl-4">
          {MILESTONES.map((m, i) => (
            <MilestoneCard key={i} m={m} index={i} total={MILESTONES.length} />
          ))}
        </div>

        {/* Bottom promise */}
        <FadeIn delay={0.5}>
          <div className="mt-4 p-5 sm:p-7 rounded-2xl border border-teal-500/20 bg-teal-500/[0.03] backdrop-blur-sm">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
                <Zap size={20} className="text-teal-400" />
              </div>
              <div>
                <h3 className="font-display font-bold text-sm sm:text-lg text-text mb-2">
                  Why Materna scales where others can't
                </h3>
                <div className="grid sm:grid-cols-3 gap-3 mt-3">
                  {[
                    { t: 'No LLM retraining', d: 'Every escalation decision is a deterministic pure function. New clinics need zero AI fine-tuning.' },
                    { t: 'Offline-first architecture', d: 'Cases process locally when Band is unavailable. Syncs when connectivity returns. Critical for rural clinics.' },
                    { t: 'Language-independent', d: 'Intake Agent supports English and Urdu natively. Adding languages requires only a prompt update — no code changes.' },
                  ].map((item, i) => (
                    <div key={i} className="p-3 rounded-xl bg-bg-dark/30 border border-border/30">
                      <div className="font-semibold text-xs sm:text-sm text-text mb-1">{item.t}</div>
                      <p className="text-[10px] sm:text-xs text-text-muted leading-relaxed">{item.d}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
