/**
 * ModeSwitch — Novice ↔ Expert toggle in the sidebar.
 * Persists to localStorage. Shows tooltip on first interaction.
 */
import { motion } from 'framer-motion';
import { Sparkles, Zap } from 'lucide-react';

export default function ModeSwitch({ isExpert, onToggle }) {
  return (
    <button
      onClick={onToggle}
      className="relative w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-border/50 hover:border-teal-500/30 bg-bg-card/30 hover:bg-bg-card/50 transition-all duration-300 group"
      title={isExpert ? 'Switch to Novice mode' : 'Switch to Expert mode'}
    >
      {/* Toggle pill */}
      <div className="relative w-9 h-5 rounded-full bg-border transition-colors duration-300 flex-shrink-0 group-hover:bg-border/80">
        <motion.div
          className="absolute top-0.5 w-4 h-4 rounded-full flex items-center justify-center"
          style={{ background: isExpert ? '#F59E0B' : '#2DD4BF' }}
          animate={{ left: isExpert ? 'calc(100% - 18px)' : '2px' }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          {isExpert ? (
            <Zap size={10} className="text-bg-dark" />
          ) : (
            <Sparkles size={10} className="text-bg-dark" />
          )}
        </motion.div>
      </div>

      <span className="text-xs font-medium text-text-muted group-hover:text-text transition-colors">
        {isExpert ? 'Expert' : 'Novice'}
      </span>
    </button>
  );
}
