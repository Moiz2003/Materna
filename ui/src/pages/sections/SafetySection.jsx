import { Shield, AlertTriangle, Lock, Stethoscope } from 'lucide-react';
import { FadeIn, FadeInStagger } from '../../components/ui/fade-in';
import { TexturePanel } from '../../components/ui/texture-panel';

/* Three positive compliance pillars in a grid, then a full-width honest
   disclaimer banner — a deliberately different layout from the Features
   single-column list (claude2.md rule #4: no repeating card stacks). */
const pillars = [
  {
    icon: Shield, title: 'Synthetic Data Only',
    body: 'Fabricated and anonymized data only. Zero real Protected Health Information (PHI) ever enters the system. Every demo case is synthetic.',
  },
  {
    icon: Stethoscope, title: 'Decision-Support, Not Diagnostic',
    body: 'All AI output is labeled "decision-support only." The human obstetrician holds final authority on every flagged case — no autonomous clinical decisions.',
  },
  {
    icon: Lock, title: 'Tamper-Evident by Design',
    body: 'SHA-256 hash chain on every state transition. Sealed PDF packets. Secrets in .env, never committed. 132 unit and adversarial tests running in CI.',
  },
];

export default function SafetySection() {
  return (
    <section className="py-20 px-6 bg-bg-mid/30">
      <div className="max-w-5xl mx-auto">
        <FadeIn className="text-center mb-12">
          <span className="text-text-subtle uppercase tracking-widest text-[13px] font-semibold">Safety &amp; Compliance</span>
          <h2 className="font-display text-3xl font-bold mt-2 mb-3">We take safety seriously.</h2>
          <p className="text-text-muted text-base max-w-xl mx-auto">
            Every design decision was made with patient safety first. Here is exactly how the system handles data.
          </p>
        </FadeIn>

        <FadeInStagger className="grid md:grid-cols-3 gap-4 mb-4">
          {pillars.map((p, i) => (
            <FadeIn key={i}>
              <TexturePanel className="p-5 h-full">
                <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center mb-3">
                  <p.icon size={20} className="text-teal-400" />
                </div>
                <h3 className="font-display font-semibold text-base mb-1.5">{p.title}</h3>
                <p className="text-text-muted text-sm leading-relaxed">{p.body}</p>
              </TexturePanel>
            </FadeIn>
          ))}
        </FadeInStagger>

        {/* Honest, prominent disclaimer — full width, amber, border glow */}
        <FadeIn>
          <TexturePanel variant="amber" className="p-5 animate-border-glow">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                <AlertTriangle size={20} className="text-amber-400" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-base text-amber-400 mb-1">Not HIPAA Certified — Hackathon Project</h3>
                <p className="text-text-muted text-sm leading-relaxed">
                  This is a hackathon demonstration. It has <span className="text-text font-medium">not</span> undergone HIPAA
                  certification, FDA review, or any regulatory approval. Do <span className="text-text font-medium">not</span> use
                  it with real patient data. For demonstration only.
                </p>
              </div>
            </div>
          </TexturePanel>
        </FadeIn>
      </div>
    </section>
  );
}
