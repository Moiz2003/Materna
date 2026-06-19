import { ArrowRight, BookOpen } from 'lucide-react';
import { FadeIn } from '../../components/ui/fade-in';
import GlowButton from '../../components/effects/GlowButton';

export default function CTASection() {
  return (
    <section className="py-12 sm:py-20 px-4 sm:px-6 text-center">
      <FadeIn className="max-w-lg mx-auto">
        <h2 className="font-display text-2xl sm:text-3xl font-bold mb-3">Ready to see four AI agents review a case?</h2>
        <p className="text-text-muted text-sm sm:text-base mb-6 sm:mb-8">
          Submit a case, watch the pipeline run, and download a cryptographically sealed review packet — all in under 10 seconds.
        </p>
        <div className="flex gap-3 sm:gap-4 justify-center flex-wrap mb-2">
          <GlowButton to="/dashboard" size="lg">
            Launch Dashboard <ArrowRight size={18} />
          </GlowButton>
          <a href="/TECHNICAL_AUDIT.md" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 border border-border hover:border-teal-500/30 text-text-muted hover:text-teal-400 rounded-xl font-medium text-xs sm:text-sm no-underline transition-all">
            <BookOpen size={16} /> Read Technical Audit
          </a>
        </div>
        <p className="text-xs text-text-subtle">10 seconds · No sign-up · Synthetic data only</p>
      </FadeIn>
    </section>
  );
}
