import { Link } from 'react-router-dom';
import { Shield, Activity, Users, ArrowRight, Stethoscope, FileCheck, Search } from 'lucide-react';
import { motion } from 'framer-motion';

const fadeUp = { hidden: { opacity: 0, y: 24 }, visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.5 } }) };

function PulseWave() {
  return (
    <svg viewBox="0 0 600 80" className="w-full max-w-xl mx-auto opacity-60" aria-hidden="true">
      <defs>
        <linearGradient id="pg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#0D9488" stopOpacity="0.05" />
          <stop offset="45%" stopColor="#2DD4BF" stopOpacity="0.5" />
          <stop offset="55%" stopColor="#F59E0B" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#0D9488" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      <path d="M0 40 L100 40 L130 40 L145 10 L160 70 L175 24 L190 56 L210 40 L600 40" fill="none" stroke="url(#pg)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse-glow" />
    </svg>
  );
}

const agents = [
  { icon: FileCheck, label: 'Intake', desc: 'Normalises case data from any format — handwritten notes, images, structured JSON.', color: 'text-teal-400', bg: 'bg-teal-500/10', border: 'border-teal-500/20' },
  { icon: Activity, label: 'Dating & Risk', desc: 'Computes gestational age, detects discordance, fires risk flags for PE, GDM, anaemia.', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  { icon: Shield, label: 'Guideline', desc: 'Checks against antenatal ruleset. Vetoes if required investigations are missing.', color: 'text-teal-400', bg: 'bg-teal-500/10', border: 'border-teal-500/20' },
  { icon: Search, label: 'Auditor', desc: 'Adversarially challenges the Guideline agent — catches missed flags, questions complacency.', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
];

const features = [
  { icon: Shield, title: 'Deterministic Gate', desc: 'Escalation is a pure function — no LLM can bypass it. 6 hardening tests prove it.' },
  { icon: FileCheck, title: 'SHA-256 Audit Chain', desc: 'Every state transition is cryptographically hashed. Tampering is instantly detectable.' },
  { icon: Search, title: 'Diagnostic Language Filter', desc: 'Imaging is decision-support only. AI output containing diagnostic claims is rejected.' },
  { icon: Stethoscope, title: 'Human Final Authority', desc: 'Dr. Saima Javed, a practicing gynecologist, approves or overrides every flagged case.' },
];

const stats = [
  { value: '186', unit: '/100k', label: 'Maternal mortality rate in Pakistan', source: 'WHO 2023' },
  { value: '5–8%', unit: '', label: 'Pregnancies affected by pre-eclampsia', source: 'ACOG' },
  { value: '25%', unit: '', label: 'GA discordance in LMP-based dating', source: 'Hadlock et al.' },
  { value: '28', unit: '', label: 'Adversarial hardening tests passed', source: 'This project' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-dark text-text">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-border bg-bg-dark/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 font-display font-bold text-lg text-teal-400 no-underline">
            <svg width="28" height="28" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="none" stroke="#2DD4BF" strokeWidth="2"/><circle cx="16" cy="16" r="7" fill="none" stroke="#0D9488" strokeWidth="2" strokeDasharray="4 2"/></svg>
            Antenatal Review Board
          </Link>
          <div className="flex items-center gap-6 text-sm">
            <Link to="/about" className="text-text-muted hover:text-text no-underline transition-colors">About</Link>
            <Link to="/dashboard" className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold no-underline transition-all shadow-lg shadow-teal-500/20">Launch Dashboard →</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-24 pb-16 px-6">
        <div className="absolute inset-0 bg-gradient-to-b from-teal-500/5 via-transparent to-transparent pointer-events-none" />
        <motion.div className="max-w-4xl mx-auto text-center relative z-10" initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.12 } } }}>
          <motion.div variants={fadeUp} custom={0} className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-teal-500/20 bg-teal-500/5 text-teal-400 text-xs font-medium mb-6">
            <Shield size={12} /> Track 3: Regulated & High-Stakes Workflows
          </motion.div>
          <motion.h1 variants={fadeUp} custom={1} className="font-display text-5xl sm:text-6xl font-extrabold leading-tight mb-5 tracking-tight">
            AI-Powered<br /><span className="text-teal-400">Obstetric Safety</span> Review
          </motion.h1>
          <motion.p variants={fadeUp} custom={2} className="text-lg text-text-muted max-w-2xl mx-auto mb-8 leading-relaxed">
            4 specialist AI agents coordinate through <strong className="text-text">Band</strong>. A real gynecologist holds final authority. Every decision is cryptographically sealed in a tamper-evident audit trail.
          </motion.p>
          <motion.div variants={fadeUp} custom={3} className="flex gap-4 justify-center flex-wrap">
            <Link to="/dashboard" className="px-6 py-3 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-semibold text-sm no-underline transition-all shadow-lg shadow-teal-500/20 flex items-center gap-2">
              Launch Dashboard <ArrowRight size={16} />
            </Link>
            <a href="#how-it-works" className="px-6 py-3 border border-border hover:border-text-muted text-text-muted hover:text-text rounded-xl font-medium text-sm no-underline transition-all">
              See How It Works ↓
            </a>
          </motion.div>
          <motion.div variants={fadeUp} custom={4} className="mt-12">
            <PulseWave />
          </motion.div>
        </motion.div>
      </section>

      {/* Trust bar */}
      <section className="border-y border-border">
        <div className="max-w-6xl mx-auto px-6 py-5 grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-xs text-text-muted">
          {stats.map((s, i) => (
            <div key={i}>
              <div className="text-teal-400 font-display font-bold text-xl">{s.value}<span className="text-sm text-text-muted ml-0.5">{s.unit}</span></div>
              <div className="mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div className="text-center mb-14" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="font-display text-3xl font-bold mb-3">How It Works</h2>
            <p className="text-text-muted max-w-xl mx-auto">Four specialist agents collaborate through Band. No agent calls another directly — every handoff traverses the shared Band room.</p>
          </motion.div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {agents.map((a, i) => (
              <motion.div key={i} className={`glass ${a.border} p-5 text-center`} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <div className={`w-10 h-10 mx-auto mb-3 rounded-xl ${a.bg} flex items-center justify-center`}><a.icon size={20} className={a.color} /></div>
                <h3 className="font-display font-semibold text-sm mb-1">{a.label}</h3>
                <p className="text-text-muted text-xs leading-relaxed">{a.desc}</p>
              </motion.div>
            ))}
          </div>
          <motion.div className="mt-6 text-center" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            <div className="inline-flex items-center gap-2 px-5 py-3 glass-amber border-amber-500/30 rounded-xl">
              <Users size={16} className="text-amber-400" />
              <span className="text-sm font-semibold text-amber-400">🩺 Human Gate: Dr. Saima Javed</span>
              <span className="text-text-muted text-xs">— approves or overrides every flagged case</span>
            </div>
          </motion.div>
          <motion.div className="mt-4 text-center" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            <div className="inline-flex items-center gap-2 px-5 py-3 glass-success border-success/30 rounded-xl">
              <FileCheck size={16} className="text-success" />
              <span className="text-sm font-semibold text-success">🔐 SHA-256 Sealed PDF</span>
              <span className="text-text-muted text-xs">— tamper-evident, cryptographically verified</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Safety Architecture */}
      <section className="py-20 px-6 bg-bg-mid/30">
        <div className="max-w-5xl mx-auto">
          <motion.div className="text-center mb-14" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="font-display text-3xl font-bold mb-3">Safety by Construction</h2>
            <p className="text-text-muted max-w-lg mx-auto">Every guardrail is structural, not aspirational. 28 adversarial hardening tests prove each one.</p>
          </motion.div>
          <div className="grid sm:grid-cols-2 gap-4">
            {features.map((f, i) => (
              <motion.div key={i} className="glass p-6 flex gap-4" initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
                <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center flex-shrink-0"><f.icon size={20} className="text-teal-400" /></div>
                <div><h3 className="font-display font-semibold text-sm mb-1">{f.title}</h3><p className="text-text-muted text-xs leading-relaxed">{f.desc}</p></div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <motion.div className="max-w-lg mx-auto" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="font-display text-3xl font-bold mb-3">Ready to see it in action?</h2>
          <p className="text-text-muted mb-8">Submit a case, watch 4 agents coordinate through Band, and download a cryptographically sealed review packet.</p>
          <Link to="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold text-base no-underline transition-all shadow-xl shadow-teal-500/20">
            Launch Dashboard <ArrowRight size={18} />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-6 text-center text-xs text-text-subtle">
        <p>Built for the Band of Agents Hackathon · Track 3: Regulated & High-Stakes Workflows · MIT License · Synthetic data only — no real PHI</p>
        <p className="mt-1">Abdul Moiz Ahmed · Dr. Saima Javed (Reviewing Obstetrician)</p>
      </footer>
    </div>
  );
}
