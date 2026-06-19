/**
 * ProgressBar — Animated gradient progress bar with ambient glow.
 * Used in ProcessingTheatre to show pipeline completion percentage.
 *
 * Props:
 *   value: 0-100
 *   glow: boolean — enable ambient glow behind the bar
 *   className: additional classes
 */
import { motion } from 'framer-motion';

export default function ProgressBar({ value = 0, glow = true, className = '' }) {
  const pct = Math.min(Math.max(value, 0), 100);

  return (
    <div className={`relative ${className}`}>
      {/* Glow behind the bar */}
      {glow && (
        <div
          className="absolute -inset-2 rounded-full blur-md transition-opacity duration-500 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse 100% 100% at 50% 50%, rgba(45,212,191,0.15) 0%, transparent 70%)',
            opacity: pct > 0 ? 1 : 0,
          }}
        />
      )}

      {/* Track */}
      <div className="relative h-1.5 rounded-full bg-border/50 overflow-hidden">
        {/* Fill */}
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            background: 'linear-gradient(90deg, #0D9488 0%, #2DD4BF 40%, #14B8A6 100%)',
          }}
          initial={{ width: '0%' }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        />

        {/* Shine streak */}
        {pct > 0 && (
          <div
            className="absolute inset-y-0 w-8 rounded-full animate-shine"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              left: `${pct - 5}%`,
            }}
          />
        )}
      </div>

      {/* Percentage label */}
      <div className="flex justify-between mt-1.5">
        <span className="text-[10px] font-mono text-text-subtle/50">
          {pct < 100 ? 'Processing' : 'Complete'}
        </span>
        <span className="text-[10px] font-mono text-teal-400/70 tabular-nums">
          {Math.round(pct)}%
        </span>
      </div>

      <style>{`
        @keyframes shine {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .animate-shine {
          animation: shine 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
