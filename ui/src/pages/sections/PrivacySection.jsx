/**
 * PrivacySection — Vertical timeline layout.
 * Numbered steps on a single line with expanding content.
 * Clean, minimal — per claude3.md §9.
 */
import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STEPS = [
  {
    title: 'Input',
    body: 'You paste clinical notes or upload an ultrasound image. The system accepts synthetic and anonymized data only. No real Protected Health Information (PHI) is ever accepted.',
  },
  {
    title: 'Processing',
    body: 'Data is sent to AI/ML API (via OpenRouter) for structured extraction and analysis. The model provider does not store data beyond the duration of the API call. Zero training on submitted data.',
  },
  {
    title: 'Storage',
    body: 'Case state is stored in server memory and on the local filesystem under data/state/ and audit_log/. This is not a production database. No cloud storage. No off-site backup.',
  },
  {
    title: 'Audit',
    body: 'Every state transition is recorded in a SHA-256 hash-chained JSONL file. The chain is append-only and tamper-evident — any modification to any entry is detected at the exact sequence number.',
  },
  {
    title: 'Deletion',
    body: 'Remove the corresponding files from data/state/ and audit_log/ to permanently delete a case. No cloud backup exists. No trace remains after file deletion.',
  },
];

export default function PrivacySection() {
  const [active, setActive] = useState(0);
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !visible) {
          setVisible(true);
          STEPS.forEach((_, i) => {
            setTimeout(() => setActive((prev) => prev + 1), 400 * (i + 1));
          });
        }
      },
      { threshold: 0.2 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [visible]);

  return (
    <section ref={ref} className="py-20 px-6 bg-bg-mid/30">
      <div className="max-w-3xl mx-auto">
        <div className="mb-12">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-text max-w-xl">
            Your data, step by step
          </h2>
          <p className="text-text-muted text-base mt-3 max-w-lg leading-relaxed">
            Plain English. No legalese. Here is exactly what happens with the information you submit.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative pl-10">
          {/* Vertical line */}
          <div className="absolute left-[15px] top-2 bottom-2 w-px bg-border" />
          {/* Active line fill */}
          <motion.div
            className="absolute left-[15px] top-2 w-px bg-teal-400/60"
            initial={{ height: 0 }}
            animate={{ height: `${(active / STEPS.length) * 100}%` }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          />

          <div className="space-y-8">
            {STEPS.map((step, i) => {
              const isActive = i < active;
              return (
                <div key={i} className="relative">
                  {/* Circle on the line */}
                  <motion.div
                    className="absolute -left-10 top-1 w-[10px] h-[10px] rounded-full border-2"
                    style={{
                      borderColor: isActive ? '#2DD4BF' : '#334155',
                      background: isActive ? '#2DD4BF' : '#0F172A',
                    }}
                    initial={{ scale: 0 }}
                    animate={isActive ? { scale: 1 } : {}}
                    transition={{ duration: 0.3, ease: 'easeOut' }}
                  />
                  {/* Content */}
                  <motion.div
                    initial={{ opacity: 0, x: -12 }}
                    animate={isActive ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.4, delay: 0.1 }}
                  >
                    <h3
                      className="font-display font-bold text-lg"
                      style={{ color: isActive ? '#F1F5F9' : '#64748B' }}
                    >
                      <span className="font-mono text-sm mr-2" style={{ color: isActive ? '#2DD4BF' : '#475569' }}>
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      {step.title}
                    </h3>
                    <AnimatePresence>
                      {isActive && (
                        <motion.p
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                          className="text-text-muted text-sm leading-relaxed mt-1.5 ml-9"
                        >
                          {step.body}
                        </motion.p>
                      )}
                    </AnimatePresence>
                  </motion.div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Contact */}
        <div className="mt-10 pt-6 border-t border-border/50 text-center">
          <p className="text-sm text-text-muted">
            Questions?{' '}
            <a href="mailto:moiz.info1010@gmail.com" className="text-teal-400 hover:text-teal-300 transition-colors no-underline font-medium">
              moiz.info1010@gmail.com
            </a>
          </p>
          <p className="text-xs text-text-subtle mt-2">
            This is a hackathon project. No real PHI is processed or stored. Not HIPAA certified.
          </p>
        </div>
      </div>
    </section>
  );
}
