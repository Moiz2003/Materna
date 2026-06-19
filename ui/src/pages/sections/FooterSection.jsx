import { Link } from 'react-router-dom';

export default function FooterSection() {
  return (
    <footer className="border-t border-border py-10 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-6">
          <div className="text-center md:text-left">
            <div className="font-display font-bold text-lg text-teal-400 mb-1">Materna</div>
            <p className="text-text-muted text-sm">AI-Powered Obstetric Safety Review</p>
          </div>
          <div className="flex gap-6 text-sm">
            <Link to="/dashboard" className="text-text-muted hover:text-text no-underline transition-colors">Dashboard</Link>
            <a href="#safety" className="text-text-muted hover:text-text no-underline transition-colors">Safety</a>
            <Link to="/about" className="text-text-muted hover:text-text no-underline transition-colors">About</Link>
            <a href="https://github.com/Moiz2003/Materna" target="_blank" rel="noopener noreferrer" className="text-text-muted hover:text-text no-underline transition-colors">GitHub</a>
            <a href="mailto:moiz.info1010@gmail.com" className="text-text-muted hover:text-text no-underline transition-colors">Contact</a>
          </div>
        </div>
        <div className="border-t border-border pt-5 text-center text-[13px] text-text-subtle space-y-1">
          <p className="font-mono text-text-muted">Band · AI/ML API · Gemini Vision · FastAPI · React</p>
          <p>Built for the Band of Agents Hackathon · Track 3: Regulated &amp; High-Stakes Workflows · June 2026</p>
          <p>Abdul Moiz Ahmed · Dr. Saima Javed (Reviewing Obstetrician) · MIT License</p>
          <p className="text-text-subtle/60">Synthetic data only. Not for clinical use. No real PHI is processed or stored.</p>
        </div>
      </div>
    </footer>
  );
}
