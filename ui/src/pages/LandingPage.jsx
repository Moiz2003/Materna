import { Link } from 'react-router-dom';
import HeroSection from './sections/HeroSection';
import ProblemSection from './sections/ProblemSection';
import PipelineFlow from '../components/effects/PipelineFlow';
import HowItWorksSection from './sections/HowItWorksSection';
import FeaturesSection from './sections/FeaturesSection';
import SafetySection from './sections/SafetySection';
import PrivacySection from './sections/PrivacySection';
import CTASection from './sections/CTASection';
import FooterSection from './sections/FooterSection';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-dark text-text">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-border bg-bg-dark/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 font-display font-bold text-lg text-teal-400 no-underline">
            <svg width="28" height="28" viewBox="0 0 32 32">
              <circle cx="16" cy="16" r="14" fill="none" stroke="#2DD4BF" strokeWidth="2" />
              <circle cx="16" cy="16" r="7" fill="none" stroke="#0D9488" strokeWidth="2" strokeDasharray="4 2" />
            </svg>
            Materna
          </Link>
          <div className="flex items-center gap-6 text-sm">
            <a href="#features" className="text-text-muted hover:text-text no-underline transition-colors">Features</a>
            <a href="#safety" className="text-text-muted hover:text-text no-underline transition-colors">Safety</a>
            <Link to="/about" className="text-text-muted hover:text-text no-underline transition-colors">About</Link>
            <Link to="/dashboard" className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold text-sm no-underline transition-all shadow-lg shadow-teal-500/20">
              Launch App
            </Link>
          </div>
        </div>
      </nav>

      <HeroSection />
      <ProblemSection />
      <PipelineFlow />
      <HowItWorksSection />
      <div id="features"><FeaturesSection /></div>
      <div id="safety"><SafetySection /></div>
      <PrivacySection />
      <CTASection />
      <FooterSection />
    </div>
  );
}
