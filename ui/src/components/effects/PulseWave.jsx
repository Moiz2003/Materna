/**
 * PulseWave — Dual-trace ECG/Doppler wave for the hero section.
 * Two layered paths (main trace + echo) with animated dash offset
 * creating a scanning effect. Teal → amber gradient echo.
 */
export default function PulseWave({ className = '' }) {
  return (
    <div className={`relative w-full max-w-xl mx-auto ${className}`} aria-hidden="true">
      {/* Ambient glow behind the trace */}
      <div className="absolute left-1/4 right-1/4 top-1/2 -translate-y-1/2 h-20 bg-gradient-to-r from-teal-500/0 via-teal-400/15 to-amber-400/0 blur-3xl pointer-events-none" />

      <svg viewBox="0 0 600 80" className="w-full" fill="none">
        <defs>
          <linearGradient id="pw-main" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#0D9488" stopOpacity="0.1" />
            <stop offset="40%" stopColor="#2DD4BF" stopOpacity="0.9" />
            <stop offset="55%" stopColor="#F59E0B" stopOpacity="0.7" />
            <stop offset="70%" stopColor="#2DD4BF" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#0D9488" stopOpacity="0.1" />
          </linearGradient>

          <linearGradient id="pw-echo" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#0D9488" stopOpacity="0" />
            <stop offset="45%" stopColor="#2DD4BF" stopOpacity="0.2" />
            <stop offset="55%" stopColor="#F59E0B" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#0D9488" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Echo trace — thicker, more blurred, scans */}
        <path
          d="M0 40 L100 40 L130 40 L145 12 L160 68 L175 26 L190 54 L210 40 L600 40"
          stroke="url(#pw-echo)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="animate-pulse-glow"
          strokeDasharray="600"
          strokeDashoffset="0"
          style={{ animation: 'pulse-glow 3s ease-in-out infinite, dash-scan 4s linear infinite' }}
        />

        {/* Main trace — sharp, bright */}
        <path
          d="M0 40 L100 40 L130 40 L145 12 L160 68 L175 26 L190 54 L210 40 L600 40"
          stroke="url(#pw-main)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="animate-pulse-glow"
        />

        {/* Pulse dot that travels along the wave */}
        <circle r="4" fill="#2DD4BF" opacity="0.9" className="animate-pulse-glow">
          <animateMotion
            dur="4s"
            repeatCount="indefinite"
            path="M0 40 L100 40 L130 40 L145 12 L160 68 L175 26 L190 54 L210 40 L600 40"
          />
        </circle>
      </svg>

      <style>{`
        @keyframes dash-scan {
          0% { stroke-dashoffset: 600; }
          100% { stroke-dashoffset: -600; }
        }
      `}</style>
    </div>
  );
}
