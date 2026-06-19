/**
 * EmptyState — Demo play cards showing exactly how to run a case.
 * 3 connected cards with step numbers, arrows to UI elements,
 * and estimated times. Prominent in the results area before any case.
 */
import { Sparkles, MousePointerClick, ArrowRight, ArrowDown, Play, Clock } from 'lucide-react';
import GlassPanel from '../ui/glass-panel';

const STEPS = [
  {
    num: 1,
    title: 'Load a demo case',
    time: '1 second',
    desc: 'Click any demo badge above. The form fills instantly with real clinical data — no typing needed.',
    pointsTo: 'demo badges in Smart Paste',
    icon: MousePointerClick,
    arrow: '↑ Look above in Smart Paste',
  },
  {
    num: 2,
    title: 'Submit to Review Board',
    time: '5–8 seconds',
    desc: 'Click the teal "Submit to Review Board" button. Four AI agents analyse the case through Band. Watch the animated pipeline track progress live.',
    pointsTo: 'Submit to Review Board button',
    icon: Play,
    arrow: '↑ Click the teal submit button above',
  },
  {
    num: 3,
    title: 'Review findings & approve',
    time: '30 seconds',
    desc: 'Results appear as cards below. Expand risk flags to see clinical evidence. If the case is escalated, Dr. Saima Javed reviews and approves or overrides the AI treatment plan.',
    pointsTo: 'results cards & decision panel',
    icon: Sparkles,
    arrow: '↓ Results appear here',
  },
];

export default function EmptyState({ isExpert = false }) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <GlassPanel glow="teal" intensity={0.4} className="p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
            <Play size={22} className="text-teal-400" />
          </div>
          <div>
            <h3 className="font-display font-bold text-lg text-text">
              Run your first review in 30 seconds
            </h3>
            <p className="text-sm text-text-muted mt-1 leading-relaxed">
              {isExpert
                ? 'Press ⌘D to load a demo, then ⌘↵ to submit. Results stream in below.'
                : 'Follow the three steps below. No account needed. Synthetic data only.'}
            </p>
          </div>
        </div>
      </GlassPanel>

      {/* Play cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        {STEPS.map((step, i) => (
          <div key={i} className="relative">
            <GlassPanel glow="teal" intensity={0.2} className="p-5 flex flex-col h-full">
              {/* Step number + time */}
              <div className="flex items-center justify-between mb-3">
                <span className="w-8 h-8 rounded-xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-sm font-bold font-display text-teal-400">
                  {step.num}
                </span>
                <span className="flex items-center gap-1 text-xs text-text-dim">
                  <Clock size={11} />
                  {step.time}
                </span>
              </div>

              {/* Icon + content */}
              <div className="flex-1">
                <div className="w-9 h-9 rounded-lg bg-teal-500/10 flex items-center justify-center mb-2.5">
                  <step.icon size={17} className="text-teal-400" />
                </div>
                <h4 className="font-display font-bold text-sm text-text mb-1.5">{step.title}</h4>
                <p className="text-xs text-text-muted leading-relaxed mb-3">{step.desc}</p>
              </div>

              {/* Arrow to UI element */}
              <div className="mt-auto pt-3 border-t border-border/50">
                <div className="flex items-start gap-2">
                  {i === 2 ? (
                    <ArrowDown size={14} className="text-teal-400 flex-shrink-0 mt-0.5" />
                  ) : (
                    <ArrowRight size={14} className="text-teal-400 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-teal-400">
                      {step.pointsTo}
                    </span>
                    <p className="text-[10px] text-text-dim mt-0.5">{step.arrow}</p>
                  </div>
                </div>
              </div>
            </GlassPanel>

            {/* Connector arrow between cards (desktop only) */}
            {i < STEPS.length - 1 && (
              <div className="hidden sm:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-teal-500/10 border border-teal-500/20 items-center justify-center">
                <ArrowRight size={12} className="text-teal-400" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick-start CTA */}
      <GlassPanel glow="teal" intensity={0.25} className="p-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center">
              <Play size={15} className="text-teal-400" />
            </div>
            <div>
              <span className="text-sm font-semibold text-text">Want to see it instantly?</span>
              <p className="text-xs text-text-muted">
                Click any demo badge above (C-0001 or C-0002) and press Submit — the whole pipeline runs in under 10 seconds.
              </p>
            </div>
          </div>
          <span className="text-xs text-text-dim font-mono">
            {isExpert ? '⌘D then ⌘↵' : 'Click demo → Click Submit'}
          </span>
        </div>
      </GlassPanel>
    </div>
  );
}
