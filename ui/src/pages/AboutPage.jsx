import { Link } from 'react-router-dom';
import { Shield, FileCheck, Activity, Users, Code, Eye, Lock, Key } from 'lucide-react';

const rules = [
  { icon: Users, title: 'Band is the coordination layer', desc: 'Agents communicate ONLY via Band rooms — no direct agent-to-agent calls.' },
  { icon: Code, title: 'Deterministic escalation gate', desc: 'must_escalate() is a pure function. An LLM never decides whether to escalate.' },
  { icon: Shield, title: 'Synthetic data only', desc: 'No real PHI ever enters the system. All cases are synthetic or anonymised.' },
  { icon: Eye, title: 'Decision-support framing', desc: 'All imaging output is labelled decision-support — not a diagnosis.' },
  { icon: Activity, title: 'Math & rules are code', desc: 'GA calculation, risk evaluation, guideline checking are deterministic functions.' },
  { icon: FileCheck, title: 'Everything is audited', desc: 'SHA-256 hash chain on every state transition. Tampering is instantly detectable.' },
  { icon: Lock, title: 'Tests gate progress', desc: '28 adversarial hardening tests prove each guardrail cannot be bypassed.' },
  { icon: Key, title: 'Secrets in .env only', desc: 'API keys are never hardcoded, never committed. Enforced by CI hygiene tests.' },
];

export default function AboutPage() {
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
            <Link to="/about" className="text-teal-400 font-semibold no-underline">About</Link>
            <Link to="/dashboard" className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold no-underline transition-all">Launch Dashboard →</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Problem */}
        <section className="mb-16">
          <h1 className="font-display text-4xl font-extrabold mb-4">About the Project</h1>
          <div className="glass border-amber-500/20 p-6 mb-8">
            <h2 className="font-display text-lg font-bold text-amber-400 mb-2">The Problem</h2>
            <p className="text-text-muted leading-relaxed">
              In antenatal clinics across Pakistan and the developing world, handwritten records, overworked staff, 
              and disconnected specialists mean critical pregnancy risks — pre-eclampsia, gestational diabetes, 
              anaemia, dating discordance — go undetected until complications arise. A single missed blood pressure 
              reading or illegible lab value can cascade into a life-threatening emergency.
            </p>
          </div>
          <div className="glass border-teal-500/20 p-6">
            <h2 className="font-display text-lg font-bold text-teal-400 mb-2">The Solution</h2>
            <p className="text-text-muted leading-relaxed">
              4 specialist AI agents — Intake, Dating & Risk, Guideline, and Auditor — coordinate through 
              <strong className="text-text"> Band</strong> to review every antenatal case. A real gynecologist, 
              <strong className="text-text"> Dr. Saima Javed</strong>, holds final authority through Band's Human API. 
              Every decision is sealed in a <strong className="text-text">SHA-256 hash-chained audit log</strong> and 
              emitted as a tamper-evident PDF. No AI makes a clinical decision. No audit entry can be altered without detection.
            </p>
          </div>
        </section>

        {/* Team */}
        <section className="mb-16">
          <h2 className="font-display text-2xl font-bold mb-6">The Team</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="glass p-6">
              <h3 className="font-display font-semibold text-lg mb-1">Abdul Moiz Ahmed</h3>
              <p className="text-teal-400 text-sm font-medium mb-2">Builder & Architect</p>
              <p className="text-text-muted text-sm leading-relaxed">Designed and built the multi-agent system, audit chain, packet generator, and UI. Integrated Band coordination, AI/ML API, and Gemini Vision.</p>
            </div>
            <div className="glass p-6">
              <h3 className="font-display font-semibold text-lg mb-1">Dr. Saima Javed</h3>
              <p className="text-amber-400 text-sm font-medium mb-2">Reviewing Obstetrician</p>
              <p className="text-text-muted text-sm leading-relaxed">Practicing gynecologist serving as the human-in-the-loop gate. Reviews escalated cases through Band's Human API and holds final clinical authority.</p>
            </div>
          </div>
        </section>

        {/* Technology */}
        <section className="mb-16">
          <h2 className="font-display text-2xl font-bold mb-4">Technology Stack</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            {['Band (Coordination)', 'AI/ML API (Models)', 'Gemini Vision', 'FastAPI + Python', 'React + Vite', 'SHA-256 Audit', 'ReportLab PDF', 'Docker Compose'].map((t) => (
              <div key={t} className="glass px-4 py-3 text-center text-text-muted font-medium">{t}</div>
            ))}
          </div>
        </section>

        {/* 8 Golden Rules */}
        <section>
          <h2 className="font-display text-2xl font-bold mb-6">The 8 Golden Rules</h2>
          <div className="grid sm:grid-cols-2 gap-3">
            {rules.map((r, i) => (
              <div key={i} className="glass p-4 flex gap-3">
                <r.icon size={18} className="text-teal-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-display font-semibold text-sm mb-0.5">{r.title}</h3>
                  <p className="text-text-muted text-xs leading-relaxed">{r.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <footer className="border-t border-border py-8 px-6 text-center text-xs text-text-subtle">
        <p>Built for the Band of Agents Hackathon · Track 3: Regulated & High-Stakes Workflows · MIT License</p>
      </footer>
    </div>
  );
}
