import { useState } from 'react';
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
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="min-h-screen bg-bg-dark text-text">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-border bg-bg-dark/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 sm:gap-3 font-display font-bold text-base sm:text-lg text-teal-400 no-underline">
            <svg width="26" height="26" viewBox="0 0 32 32" className="sm:w-7 sm:h-7">
              <circle cx="16" cy="16" r="14" fill="none" stroke="#2DD4BF" strokeWidth="2" />
              <circle cx="16" cy="16" r="7" fill="none" stroke="#0D9488" strokeWidth="2" strokeDasharray="4 2" />
            </svg>
            Materna
          </Link>
          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6 text-sm">
            <a href="#features" className="text-text-muted hover:text-text no-underline transition-colors">Features</a>
            <a href="#safety" className="text-text-muted hover:text-text no-underline transition-colors">Safety</a>
            <Link to="/about" className="text-text-muted hover:text-text no-underline transition-colors">About</Link>
            <Link to="/dashboard" className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold text-sm no-underline transition-all shadow-lg shadow-teal-500/20">
              Launch App
            </Link>
          </div>
          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden flex flex-col gap-1.5 p-2 -mr-2"
            aria-label="Toggle menu"
          >
            <span className={`block w-5 h-0.5 bg-text transition-all ${menuOpen ? 'rotate-45 translate-y-1' : ''}`} />
            <span className={`block w-5 h-0.5 bg-text transition-all ${menuOpen ? 'opacity-0' : ''}`} />
            <span className={`block w-5 h-0.5 bg-text transition-all ${menuOpen ? '-rotate-45 -translate-y-1' : ''}`} />
          </button>
        </div>
        {/* Mobile menu drawer */}
        {menuOpen && (
          <div className="md:hidden border-t border-border bg-bg-dark/95 backdrop-blur-xl px-4 py-4 space-y-3">
            <a href="#features" onClick={() => setMenuOpen(false)} className="block text-text-muted hover:text-text no-underline transition-colors text-sm py-2">Features</a>
            <a href="#safety" onClick={() => setMenuOpen(false)} className="block text-text-muted hover:text-text no-underline transition-colors text-sm py-2">Safety</a>
            <Link to="/about" onClick={() => setMenuOpen(false)} className="block text-text-muted hover:text-text no-underline transition-colors text-sm py-2">About</Link>
            <Link to="/dashboard" onClick={() => setMenuOpen(false)} className="block w-full text-center px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold text-sm no-underline transition-all shadow-lg shadow-teal-500/20">
              Launch App
            </Link>
          </div>
        )}
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
