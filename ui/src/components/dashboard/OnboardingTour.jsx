/**
 * OnboardingTour — 3-step guided overlay for first-time users.
 * Steps: Welcome → Try a demo → Submit & review.
 * Dismissed by completing or clicking "Skip". Persisted to localStorage.
 *
 * claude4.md §7
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, Sparkles } from 'lucide-react';
import GlassPanel from '../ui/glass-panel';

const STEPS = [
  {
    title: 'Welcome to Materna',
    body: 'An AI-powered obstetric safety review system. Four specialist agents review every case. A real doctor — Dr. Saima Javed — holds final authority.',
    icon: Sparkles,
  },
  {
    title: 'Try a demo case',
    body: 'Click any demo button to instantly load a pre-filled case. No typing needed. See how the pipeline works in seconds.',
    icon: ArrowRight,
  },
  {
    title: 'Submit and review',
    body: 'Click "Submit to Review Board" to run all four AI agents. Results appear as cards below. The doctor reviews any flagged cases.',
    icon: Check,
  },
];

export default function OnboardingTour({ onComplete }) {
  const [step, setStep] = useState(0);
  const isLast = step === STEPS.length - 1;
  const current = STEPS[step];

  const next = () => {
    if (isLast) {
      localStorage.setItem('materna_onboarded', 'true');
      onComplete?.();
    } else {
      setStep((s) => s + 1);
    }
  };

  const skip = () => {
    localStorage.setItem('materna_onboarded', 'true');
    onComplete?.();
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[300] flex items-center justify-center bg-black/70 backdrop-blur-md px-4"
      >
        <motion.div
          key={step}
          initial={{ opacity: 0, scale: 0.94, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.94, y: -12 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-md"
        >
          <GlassPanel glow="teal" intensity={0.5} depth="overlay" className="p-8">
            {/* Step indicator */}
            <div className="flex items-center gap-2 mb-6">
              {STEPS.map((_, i) => (
                <div
                  key={i}
                  className={`h-1 rounded-full transition-all duration-300 ${
                    i === step ? 'w-6 bg-teal-400' : i < step ? 'w-3 bg-teal-500/50' : 'w-3 bg-border'
                  }`}
                />
              ))}
            </div>

            {/* Icon */}
            <div className="w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center mb-5">
              <current.icon size={26} className="text-teal-400" />
            </div>

            {/* Content */}
            <h2 className="font-display font-bold text-xl text-text mb-2">{current.title}</h2>
            <p className="text-text-muted text-sm leading-relaxed mb-8">{current.body}</p>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={skip}
                className="text-xs text-text-subtle hover:text-text-muted transition-colors font-medium"
              >
                Skip tour
              </button>
              <button
                onClick={next}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-semibold text-sm transition-all shadow-lg shadow-teal-500/20"
              >
                {isLast ? 'Start Using Materna' : 'Next'}
                <ArrowRight size={15} />
              </button>
            </div>
          </GlassPanel>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
