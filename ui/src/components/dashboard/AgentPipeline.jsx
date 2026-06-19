/**
 * AgentPipeline — the four specialist agents rendered as a coordination rail.
 * Each node lights up as the case advances through the pipeline; the active
 * node pulses, completed nodes show a check. Used compactly in the live output
 * panel and at full size inside ProcessingOverlay.
 */
import { motion } from 'framer-motion';
import { FileText, Activity, Scale, Search, Check } from 'lucide-react';
import { PIPELINE_STEPS, completedSteps } from './caseModel';

const ICONS = { intake: FileText, dating_risk: Activity, guideline: Scale, auditor: Search };

export default function AgentPipeline({ status, active = true, compact = false }) {
  const done = completedSteps(status);
  // Active node = the first not-yet-complete step, while the case is still running.
  const running = active && !['SEALED', 'AUTO_CLEARED', 'QUARANTINED'].includes(status);
  const activeIdx = running ? Math.min(done, PIPELINE_STEPS.length - 1) : -1;

  return (
    <div className={`flex items-center ${compact ? 'gap-1.5' : 'gap-2'}`}>
      {PIPELINE_STEPS.map((step, i) => {
        const Icon = ICONS[step.id] || Activity;
        const isDone = i < done;
        const isActive = i === activeIdx && running;
        const size = compact ? 'w-8 h-8' : 'w-11 h-11';
        const tone = isDone
          ? 'bg-teal-500/15 border-teal-500/40 text-teal-400'
          : isActive
            ? 'bg-amber-500/15 border-amber-500/50 text-amber-400'
            : 'bg-bg-dark border-border text-text-subtle';
        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <motion.div
                animate={isActive ? { scale: [1, 1.08, 1] } : { scale: 1 }}
                transition={isActive ? { duration: 1.2, repeat: Infinity } : {}}
                className={`${size} rounded-xl border flex items-center justify-center ${tone} transition-colors`}
              >
                {isDone ? <Check size={compact ? 15 : 18} /> : <Icon size={compact ? 15 : 18} />}
              </motion.div>
              {!compact && (
                <div className="text-center">
                  <div className={`text-xs font-semibold ${isDone ? 'text-teal-400' : isActive ? 'text-amber-400' : 'text-text-subtle'}`}>
                    {step.label}
                  </div>
                  <div className="text-xs text-text-subtle">{step.sub}</div>
                </div>
              )}
            </div>
            {i < PIPELINE_STEPS.length - 1 && (
              <div className={`${compact ? 'w-3' : 'w-6'} h-px mx-0.5 ${i < done ? 'bg-teal-500/40' : 'bg-border'} ${!compact ? 'mb-6' : ''}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
