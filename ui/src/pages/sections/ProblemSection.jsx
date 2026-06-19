/**
 * ProblemSection — Split-screen: stats + narrative left, Before/After right.
 * No card grid. No FadeInStagger. Unique layout per claude3.md §4.
 */
import { FadeIn } from '../../components/ui/fade-in';
import BeforeAfter from '../../components/effects/BeforeAfter';

const STATS = [
  { value: '186', unit: '/100k', label: 'Maternal mortality', src: 'Pakistan, WHO 2023' },
  { value: '5', unit: '–8%', label: 'Pre-eclampsia prevalence', src: 'ACOG' },
  { value: '25', unit: '%', label: 'GA discordance rate', src: 'LMP-based dating, Hadlock' },
];

export default function ProblemSection() {
  return (
    <section className="py-12 sm:py-20 px-4 sm:px-6 bg-bg-mid/30">
      <div className="max-w-6xl mx-auto">
        {/* Section header — no uppercase tracking-widest label */}
        <FadeIn className="mb-10 sm:mb-14">
          <h2 className="font-display text-2xl sm:text-4xl font-bold text-text leading-tight max-w-3xl">
            Every 2 minutes, a woman dies from{' '}
            <span className="text-amber-400">preventable</span> pregnancy complications.
          </h2>
          <p className="text-text-muted text-sm sm:text-base mt-3 sm:mt-4 max-w-2xl leading-relaxed">
            In antenatal clinics across Pakistan, handwritten records, overworked staff, and
            disconnected specialists mean critical risks — pre-eclampsia, gestational diabetes,
            anaemia, dating errors — go undetected until it is too late.
          </p>
        </FadeIn>

        {/* Split layout */}
        <div className="grid lg:grid-cols-2 gap-6 sm:gap-10 lg:gap-16 items-start">
          {/* LEFT — Stats */}
          <div className="space-y-4 sm:space-y-6">
            {STATS.map((s, i) => (
              <FadeIn key={i} delay={i * 0.12}>
                <div className="flex items-baseline gap-3 group">
                  <div className="font-display font-extrabold text-4xl sm:text-6xl text-amber-400 tabular-nums leading-none">
                    {s.value}
                    <span className="text-2xl text-text-muted">{s.unit}</span>
                  </div>
                  <div className="flex-1 border-b border-border/40 pb-3">
                    <div className="text-sm font-semibold text-text">{s.label}</div>
                    <div className="text-xs text-text-subtle mt-0.5">{s.src}</div>
                  </div>
                </div>
              </FadeIn>
            ))}

            <FadeIn delay={0.4}>
              <div className="rounded-lg border border-amber-500/15 bg-amber-500/5 p-4 mt-4">
                <p className="text-sm text-text-muted leading-relaxed">
                  <span className="text-amber-400 font-semibold">These are not abstract statistics.</span>
                  {' '}They represent real outcomes in clinics where a single missed blood pressure
                  reading or illegible lab value cascades into a life-threatening emergency.
                </p>
              </div>
            </FadeIn>
          </div>

          {/* RIGHT — Before/After */}
          <FadeIn delay={0.2}>
            <BeforeAfter />
          </FadeIn>
        </div>
      </div>
    </section>
  );
}
