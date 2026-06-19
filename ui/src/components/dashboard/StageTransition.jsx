/**
 * StageTransition — Orchestrated arrival wrapper for result cards.
 * Wraps children with staggered slide-up + fade-in animation.
 * Used by ResultsStage to animate stage cards arriving after processing.
 *
 * claude4.md §4 — "Stage Transition Ceremony"
 */
import { motion } from 'framer-motion';

export default function StageTransition({ children, delay = 0, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.55,
        delay,
        ease: [0.22, 1, 0.36, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
