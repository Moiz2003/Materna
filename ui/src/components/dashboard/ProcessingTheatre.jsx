/**
 * ProcessingTheatre — Animated vertical agent ladder replacing the static
 * ProcessingOverlay. Shows elapsed time (100ms ticks), cycling status text,
 * progress bar, and state-driven ambient glow. Never shows a static frame.
 *
 * claude4.md §3 — "Never show a static loading state"
 */
import { useState, useEffect, useMemo } from 'react';
import { FileText, Activity, Scale, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassPanel from '../ui/glass-panel';
import AgentLadderNode from './AgentLadderNode';
import ProgressBar from '../ui/progress-bar';
import { PIPELINE_STEPS, completedSteps } from './caseModel';

const ICONS = { intake: FileText, dating_risk: Activity, guideline: Scale, auditor: Search };

/* ── Status text cycler per agent ── */
const STATUS_CYCLE = {
  intake: [
    'Receiving case data…',
    'Normalising fields…',
    'Extracting demographics…',
    'Validating structure…',
  ],
  dating_risk: [
    'Computing gestational age…',
    'Running Hadlock formula…',
    'Evaluating risk thresholds…',
    'Firing diagnostic flags…',
  ],
  guideline: [
    'Loading antenatal ruleset…',
    'Checking schedule compliance…',
    'Identifying missing investigations…',
    'Determining veto status…',
  ],
  auditor: [
    'Reviewing guideline output…',
    'Cross-checking risk flags…',
    'Searching for contradictions…',
    'Preparing challenge report…',
  ],
};

function getStatusText(agentId, cycleIdx) {
  const texts = STATUS_CYCLE[agentId] || ['Processing…'];
  return texts[cycleIdx % texts.length];
}

export default function ProcessingTheatre({ status, startedAt }) {
  const [elapsed, setElapsed] = useState(0);
  const [cycleIdx, setCycleIdx] = useState(0);

  const done = useMemo(() => completedSteps(status), [status]);

  /* Elapsed counter — ticks every 100ms */
  useEffect(() => {
    const t = setInterval(() => {
      setElapsed(parseFloat(((Date.now() - startedAt) / 1000).toFixed(1)));
    }, 100);
    return () => clearInterval(t);
  }, [startedAt]);

  /* Status text cycler — rotates every 1.5s */
  useEffect(() => {
    const t = setInterval(() => setCycleIdx((c) => c + 1), 1500);
    return () => clearInterval(t);
  }, []);

  /* Build step list with icons and indices */
  const steps = useMemo(
    () =>
      PIPELINE_STEPS.map((s, i) => ({
        ...s,
        icon: ICONS[s.id] || FileText,
        idx: i,
      })),
    [],
  );

  const progressPct =
    PIPELINE_STEPS.length > 0 ? (done / PIPELINE_STEPS.length) * 100 : 0;

  const activeStepId = done < steps.length ? steps[done]?.id : null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      <GlassPanel glow="teal" intensity={0.6} depth="overlay" className="p-8">
        {/* Header row — title + elapsed */}
        <div className="flex items-center justify-between mb-7">
          <div>
            <h3 className="font-display font-semibold text-lg text-text">
              Coordinating the review board
            </h3>
            <p className="text-sm text-text-muted mt-0.5">
              Four specialist agents analysing through Band
            </p>
          </div>
          <div className="text-right">
            <AnimatePresence mode="wait">
              <motion.span
                key={elapsed}
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 4 }}
                transition={{ duration: 0.15 }}
                className="text-xl font-mono font-bold text-teal-400 tabular-nums"
              >
                {elapsed.toFixed(1)}s
              </motion.span>
            </AnimatePresence>
            <div className="text-[10px] text-text-subtle font-mono uppercase tracking-wider">
              Elapsed
            </div>
          </div>
        </div>

        {/* Agent ladder */}
        <div className="space-y-4 mb-6">
          {steps.map((step) => {
            const isDone = step.idx < done;
            const isActive = step.idx === done && done < steps.length;
            return (
              <AgentLadderNode
                key={step.id}
                step={step}
                isDone={isDone}
                isActive={isActive}
                statusText={
                  isActive && activeStepId === step.id
                    ? getStatusText(step.id, cycleIdx)
                    : null
                }
              />
            );
          })}
        </div>

        {/* Progress bar */}
        <ProgressBar value={progressPct} glow />

        {/* Reassurance text */}
        <p className="text-xs text-text-subtle/60 text-center mt-4">
          {done === 0
            ? 'Intake agent normalising your case data…'
            : done < 4
              ? `${steps[done]?.label || 'Agent'} is working — this takes a few seconds`
              : 'Finalising review packet…'}
        </p>
      </GlassPanel>
    </motion.div>
  );
}
