/**
 * AgentLadderNode — Single agent node in the vertical processing ladder.
 * Shows icon, label, status text (when active), and completion check.
 *
 * Props:
 *   step: { id, label, icon }
 *   isDone: boolean — completed
 *   isActive: boolean — currently processing
 *   statusText: string | null — cycling status when active
 *   compact: boolean — smaller variant for right panel
 */
import { motion } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';

export default function AgentLadderNode({
  step,
  isDone = false,
  isActive = false,
  statusText = null,
  compact = false,
}) {
  const iconSize = compact ? 16 : 20;
  const nodeSize = compact ? 'w-9 h-9' : 'w-12 h-12';

  return (
    <div className="flex items-center gap-4">
      {/* Node circle */}
      <motion.div
        className={`${nodeSize} rounded-xl border flex items-center justify-center flex-shrink-0 transition-colors duration-500 ${
          isDone
            ? 'bg-teal-500/15 border-teal-500/40'
            : isActive
              ? 'bg-teal-500/10 border-teal-500/50'
              : 'bg-bg-dark/60 border-border'
        }`}
        animate={
          isActive
            ? {
                scale: [1, 1.06, 1],
                boxShadow: [
                  '0 0 0 0 rgba(45,212,191,0)',
                  '0 0 16px 2px rgba(45,212,191,0.15)',
                  '0 0 0 0 rgba(45,212,191,0)',
                ],
              }
            : {}
        }
        transition={
          isActive
            ? { duration: 1.8, repeat: Infinity, ease: 'easeInOut' }
            : {}
        }
      >
        {isDone ? (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 500, damping: 25 }}
          >
            <Check size={iconSize} className="text-teal-400" />
          </motion.div>
        ) : isActive ? (
          <Loader2 size={iconSize} className="text-teal-400 animate-spin" strokeWidth={2} />
        ) : (
          <step.icon size={iconSize} className="text-text-subtle/50" strokeWidth={1.5} />
        )}
      </motion.div>

      {/* Label + status */}
      <div className="flex-1 min-w-0">
        <div
          className={`font-display font-semibold transition-colors duration-500 ${
            compact ? 'text-sm' : 'text-base'
          } ${
            isDone ? 'text-teal-400' : isActive ? 'text-text' : 'text-text-subtle/60'
          }`}
        >
          {step.label}
        </div>
        {!compact && isActive && statusText && (
          <motion.p
            key={statusText}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -3 }}
            transition={{ duration: 0.25 }}
            className="text-xs text-teal-400/60 mt-0.5 font-mono"
          >
            {statusText}
          </motion.p>
        )}
        {!compact && isDone && (
          <p className="text-xs text-teal-400/40 mt-0.5">Complete</p>
        )}
        {!compact && !isDone && !isActive && (
          <p className="text-xs text-text-subtle/30 mt-0.5">Waiting</p>
        )}
      </div>

      {/* Step number */}
      <span
        className={`text-xs font-mono flex-shrink-0 transition-colors duration-500 ${
          isDone ? 'text-teal-400/60' : isActive ? 'text-teal-400/40' : 'text-text-subtle/20'
        }`}
      >
        0{step.idx + 1}
      </span>
    </div>
  );
}
