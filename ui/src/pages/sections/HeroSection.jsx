/**
 * HeroSection — Premium hero with animated background, floating orbs,
 * gradient-shift heading, counter animations, typewriter tagline,
 * and glassmorphism trust bar.
 */
import { useState, useEffect } from 'react';
import { Shield, ArrowRight, FileCheck, Stethoscope, Activity, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GlowButton from '../../components/effects/GlowButton';
import PulseWave from '../../components/effects/PulseWave';
import AnimatedCounter from '../../components/effects/AnimatedCounter';
import { FadeIn, FadeInStagger } from '../../components/ui/fade-in';

/* Typewriter cycling tagline */
function TypewriterText({ phrases, className = '' }) {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % phrases.length), 3500);
    return () => clearInterval(t);
  }, [phrases.length]);
  return (
    <div className={`relative ${className}`}>
      <AnimatePresence mode="wait">
        <motion.p
          key={idx}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.4 }}
        >
          {phrases[idx]}
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, repeatType: 'reverse' }}
            className="text-teal-400 ml-0.5 font-light"
          >
            |
          </motion.span>
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* FloatingOrb — large blurred gradient circle, pure CSS animation    */
/* ------------------------------------------------------------------ */
function FloatingOrb({ className = '' }) {
  return <div className={`absolute rounded-full blur-3xl pointer-events-none ${className}`} />;
}

/* ------------------------------------------------------------------ */
/* DotGrid — subtle radial-dot pattern overlay                        */
/* ------------------------------------------------------------------ */
function DotGrid() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(45,212,191,0.12) 1px, transparent 1px)',
          backgroundSize: '36px 36px',
        }}
      />
      {/* Vignette fade at edges */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,transparent_30%,#020617_90%)]" />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Trust stat data                                                     */
/* ------------------------------------------------------------------ */
const trustStats = [
  { value: '121', label: 'Tests Passing', icon: Shield, numeric: true },
  { value: 'SHA-256', label: 'Cryptographic Audit', icon: FileCheck },
  { value: 'Real OB', label: 'Human in the Loop', icon: Stethoscope },
  { value: '0', label: 'Real PHI Used', icon: Activity, numeric: true },
];

/* ================================================================== */
export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-6 pt-28 pb-16">
      {/* ---- background layers ---- */}
      <DotGrid />

      <FloatingOrb className="w-[700px] h-[700px] -top-40 -right-40 bg-teal-500/[0.07] animate-float-slower" />
      <FloatingOrb className="w-[450px] h-[450px] top-1/4 -left-32 bg-amber-500/[0.05] animate-float-slow" />
      <FloatingOrb className="w-[350px] h-[350px] bottom-32 right-1/4 bg-teal-400/[0.04] animate-float" />

      {/* Top light wash */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[500px] pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 50% 60% at 50% 0%, rgba(45,212,191,0.08) 0%, transparent 70%)',
        }}
      />

      {/* ---- main content ---- */}
      <div className="relative z-10 w-full max-w-4xl mx-auto text-center flex-1 flex flex-col justify-center">
        <FadeInStagger>
          {/* Badge */}
          <FadeIn>
            <span className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-teal-500/20 bg-teal-500/[0.04] backdrop-blur-sm text-teal-400 text-[13px] font-semibold mb-8 animate-border-glow select-none">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping-slow absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-400" />
              </span>
              Band of Agents Hackathon · Track 3: Regulated & High-Stakes
            </span>
          </FadeIn>

          {/* Headline — two-line, gradient top, solid bottom */}
          <FadeIn delay={0.08}>
            <h1 className="font-display font-extrabold tracking-tight leading-[1.08] mb-6">
              <span
                className="block text-[clamp(2.5rem,8vw,5.5rem)] bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-teal-300 to-amber-400 animate-gradient-shift"
                style={{ backgroundSize: '200% 200%' }}
              >
                AI-Powered
              </span>
              <span className="block text-[clamp(2rem,6vw,4.5rem)] text-text">
                Obstetric Safety Review
              </span>
            </h1>
          </FadeIn>

          {/* Subtitle */}
          <FadeIn delay={0.16}>
            <TypewriterText
              phrases={[
                'Four specialist AI agents. One human obstetrician.',
                'Cryptographic proof of every decision.',
                'Zero real patient data. Ever.',
              ]}
              className="text-lg sm:text-xl text-text-muted max-w-xl mx-auto mb-3 leading-relaxed"
            />
            <p className="text-sm sm:text-base text-text-subtle max-w-lg mx-auto mb-10 leading-relaxed">
              Band-coordinated · Hash-chained audit · Synthetic data only
            </p>
          </FadeIn>

          {/* CTAs */}
          <FadeIn delay={0.24}>
            <div className="flex gap-4 justify-center flex-wrap mb-14">
              <GlowButton to="/dashboard" size="lg" glowColor="#2DD4BF">
                Launch Dashboard <ArrowRight size={18} />
              </GlowButton>
              <a
                href="#how-it-works"
                className="group inline-flex items-center gap-2 px-6 py-3.5 border border-border hover:border-teal-500/30 bg-bg-card/40 hover:bg-bg-card/70 text-text-muted hover:text-teal-400 rounded-xl font-medium text-sm no-underline transition-all duration-300 backdrop-blur-sm"
              >
                See How It Works
                <ChevronDown
                  size={15}
                  className="group-hover:translate-y-0.5 transition-transform duration-300"
                />
              </a>
            </div>
          </FadeIn>

          {/* PulseWave */}
          <FadeIn delay={0.32}>
            <PulseWave />
          </FadeIn>
        </FadeInStagger>
      </div>

      {/* ---- trust bar ---- */}
      <div className="relative z-10 w-full max-w-5xl mx-auto mt-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.6 }}
          className="rounded-2xl border border-border/40 bg-bg-card/20 backdrop-blur-2xl shadow-2xl shadow-black/30"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-border/30">
            {trustStats.map((s, i) => (
              <div
                key={i}
                className="px-5 py-5 text-center group hover:bg-bg-card/30 transition-colors duration-300 first:rounded-l-2xl last:rounded-r-2xl"
              >
                <div className="w-9 h-9 rounded-lg bg-teal-500/10 flex items-center justify-center mx-auto mb-2.5 group-hover:bg-teal-500/20 transition-colors duration-300">
                  <s.icon size={16} className="text-teal-400" />
                </div>
                <div className="text-teal-400 font-display font-bold text-2xl tabular-nums tracking-tight">
                  {s.numeric ? <AnimatedCounter value={s.value} /> : s.value}
                </div>
                <div className="text-text-muted text-[12px] mt-0.5 font-medium">{s.label}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* ---- scroll indicator ---- */}
      <motion.div
        className="absolute bottom-6 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 7, 0] }}
        transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <ChevronDown size={18} className="text-text-subtle/40" />
      </motion.div>
    </section>
  );
}
