/**
 * FeaturesSection — Asymmetric bento grid. No uniform cards.
 * Gate + Audit side by side (tall), then 3 shorter cards, then full-width extraction.
 * Per claude3.md §7. Uses inline grid-template, not a loop.
 */
import { FadeIn } from '../../components/ui/fade-in';
import { Shield, FileCheck, Search, Stethoscope, Sparkles, Download } from 'lucide-react';

function BentoCell({ className = '', children, glow = false }) {
  return (
    <div
      className={`group rounded-xl border border-border/50 bg-bg-card/30 backdrop-blur-sm p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-border/70 ${
        glow ? 'hover:shadow-[inset_0_1px_0_0_rgba(45,212,191,0.08),0_4px_24px_-4px_rgba(45,212,191,0.06)]' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}

export default function FeaturesSection() {
  return (
    <section id="features" className="py-12 sm:py-20 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <FadeIn className="mb-8 sm:mb-12">
          <h2 className="font-display text-2xl sm:text-4xl font-bold text-text max-w-2xl">
            Safety by construction,{' '}
            <span className="text-teal-400">not aspiration</span>
          </h2>
          <p className="text-text-muted text-sm sm:text-base mt-2 sm:mt-3 max-w-xl">
            Every guardrail is structural. No AI decides whether a case needs human review.
          </p>
        </FadeIn>

        {/* Bento grid — explicit grid-template, not a loop */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Row 1: Gate (wide) + Audit (tall) */}
          <BentoCell glow className="md:col-span-2">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center flex-shrink-0">
                <Shield size={20} className="text-teal-400" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-base text-text">Deterministic Safety Gate</h3>
                <p className="text-text-muted text-sm mt-1">
                  The escalation decision is a pure function. No LLM can bypass it.
                </p>
              </div>
            </div>
            <pre className="text-xs font-mono text-teal-400/80 bg-bg-dark/60 rounded-lg p-3 overflow-x-auto">
              <code>{`def must_escalate(flags, compliance):
    """Pure function — 13 lines. No LLM."""
    if compliance.veto:
        return True
    return any(f.severity != "low" for f in flags)`}</code>
            </pre>
            <div className="flex items-center gap-2 mt-3 text-xs text-text-subtle">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
              6 adversarial tests prove bypass is impossible
            </div>
          </BentoCell>

          <BentoCell glow>
            <div className="flex items-start gap-3 mb-3">
              <div className="w-9 h-9 rounded-lg bg-teal-500/10 flex items-center justify-center flex-shrink-0">
                <FileCheck size={18} className="text-teal-400" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-sm text-text">SHA-256 Audit Chain</h3>
                <p className="text-text-muted text-xs mt-1 leading-relaxed">
                  Every state transition is hash-chained. Edit one byte → chain breaks at exact position.
                </p>
              </div>
            </div>
            {/* Mini hash chain visualization */}
            <div className="space-y-1.5">
              {['a1b2c3', 'd4e5f6', '78gh90', 'ij12kl'].map((h, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-text-subtle w-6">{i + 1}</span>
                  <div className="flex-1 h-5 rounded bg-teal-500/10 border border-teal-500/20 flex items-center px-2">
                    <span className="text-[10px] font-mono text-teal-400/70">{h}</span>
                  </div>
                  {i < 3 && <span className="text-text-subtle text-[10px]">→</span>}
                </div>
              ))}
            </div>
          </BentoCell>

          {/* Row 2: Filter + Human + PDF */}
          <BentoCell>
            <div className="flex items-center gap-2 mb-2">
              <Search size={16} className="text-teal-400" />
              <h3 className="font-display font-semibold text-sm text-text">Diagnostic Language Filter</h3>
            </div>
            <p className="text-text-muted text-xs leading-relaxed mb-2">
              AI output screened for diagnostic claims before display.
            </p>
            <div className="flex flex-wrap gap-1.5">
              {['"diagnosis"', '"indicates"', '"consistent with"'].map((w) => (
                <span key={w} className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  {w} → BLOCKED
                </span>
              ))}
            </div>
          </BentoCell>

          <BentoCell glow>
            <div className="flex items-center gap-2 mb-2">
              <Stethoscope size={16} className="text-teal-400" />
              <h3 className="font-display font-semibold text-sm text-text">Human Final Authority</h3>
            </div>
            <p className="text-text-muted text-xs leading-relaxed">
              Dr. Saima Javed, practicing gynecologist, holds final say on every flagged case
              through Band's Human API.
            </p>
            <div className="mt-2 flex items-center gap-1.5 text-xs">
              <span className="text-teal-400 font-semibold">SEALED</span>
              <span className="text-text-subtle">only after recorded HumanDecision</span>
            </div>
          </BentoCell>

          <BentoCell>
            <div className="flex items-center gap-2 mb-2">
              <Download size={16} className="text-teal-400" />
              <h3 className="font-display font-semibold text-sm text-text">Sealed PDF Packets</h3>
            </div>
            <p className="text-text-muted text-xs leading-relaxed">
              Tamper-evident clinical PDFs with final SHA-256 hash in footer.
              ReportLab-generated. 6 sections.
            </p>
          </BentoCell>

          {/* Row 3: Full-width extraction */}
          <BentoCell glow className="md:col-span-3">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center flex-shrink-0">
                <Sparkles size={20} className="text-teal-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-display font-semibold text-base text-text">Smart Extraction</h3>
                <p className="text-text-muted text-sm mt-1">
                  Paste clinical notes or upload handwriting. Gemini Vision extracts structured JSON
                  with per-field confidence scoring. English and Urdu supported.
                </p>
                <div className="flex items-center gap-4 mt-3 text-xs font-mono">
                  <span className="flex items-center gap-1.5 text-teal-400">
                    <span className="w-2 h-2 rounded-full bg-teal-400" /> high confidence
                  </span>
                  <span className="flex items-center gap-1.5 text-amber-400">
                    <span className="w-2 h-2 rounded-full bg-amber-400" /> needs review
                  </span>
                  <span className="flex items-center gap-1.5 text-text-subtle">
                    <span className="w-2 h-2 rounded-full bg-border" /> unreadable → stays null
                  </span>
                </div>
              </div>
            </div>
          </BentoCell>
        </div>
      </div>
    </section>
  );
}
