/**
 * Toast — Glass toast notification with auto-dismiss.
 * Slides in from top, shows icon + message, auto-dismisses.
 *
 * Props:
 *   show: boolean
 *   message: string
 *   icon: lucide-react icon component
 *   tone: 'teal' | 'amber' | 'emerald' | 'red'
 *   onDismiss: callback
 *   duration: ms before auto-dismiss (default 2500)
 */
import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

const TONES = {
  teal:    'border-teal-500/30 bg-teal-500/5 text-teal-400',
  amber:   'border-amber-500/30 bg-amber-500/5 text-amber-400',
  emerald: 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400',
  red:     'border-red-500/30 bg-red-500/5 text-red-400',
};

export default function Toast({
  show = false,
  message = '',
  icon: Icon,
  tone = 'teal',
  onDismiss,
  duration = 2500,
}) {
  useEffect(() => {
    if (!show) return;
    const t = setTimeout(() => onDismiss?.(), duration);
    return () => clearTimeout(t);
  }, [show, duration, onDismiss]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: -16, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -12, scale: 0.96 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="fixed top-20 left-1/2 -translate-x-1/2 z-[100] pointer-events-none"
        >
          <div
            className={`pointer-events-auto flex items-center gap-3 px-5 py-3 rounded-xl border backdrop-blur-2xl shadow-2xl shadow-black/30 ${TONES[tone] || TONES.teal}`}
            style={{ background: 'rgba(15, 23, 42, 0.85)' }}
          >
            {Icon && <Icon size={16} />}
            <span className="text-sm font-medium">{message}</span>
            <button
              onClick={onDismiss}
              className="ml-2 p-0.5 rounded-lg hover:bg-white/5 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
