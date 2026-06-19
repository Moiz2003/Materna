/**
 * GlassPanel — Foundational glass-morphism surface.
 * Apple 2026 depth aesthetic: backdrop-blur, subtle border, inset highlight,
 * and state-driven ambient glow. Replaces TexturePanel in the dashboard.
 *
 * Props:
 *   glow: 'teal' | 'amber' | 'emerald' | 'red' | null
 *   intensity: 0-1 (controls glow opacity)
 *   depth: 'surface' | 'overlay' | 'elevated'
 *   className: additional classes
 */
import { cn } from '../../utils/cn';

const GLOW_COLORS = {
  teal:    'rgba(45, 212, 191, 0.08)',
  amber:   'rgba(245, 158, 11, 0.10)',
  emerald: 'rgba(5, 150, 105, 0.08)',
  red:     'rgba(220, 38, 38, 0.10)',
};

const DEPTH = {
  surface:  'bg-bg-card/50 backdrop-blur-xl border-border/40 shadow-lg shadow-black/20',
  overlay:  'bg-bg-card/70 backdrop-blur-2xl border-border/50 shadow-2xl shadow-black/40',
  elevated: 'bg-bg-elevated/60 backdrop-blur-3xl border-border/60 shadow-xl shadow-black/30',
};

export default function GlassPanel({
  glow = null,
  intensity = 0.4,
  depth = 'surface',
  className = '',
  children,
  ...props
}) {
  return (
    <div
      className={cn(
        'relative rounded-2xl border overflow-hidden transition-all duration-700',
        DEPTH[depth] || DEPTH.surface,
        className,
      )}
      {...props}
    >
      {/* Ambient glow layer */}
      {glow && GLOW_COLORS[glow] && (
        <div
          className="pointer-events-none absolute inset-0 transition-opacity duration-700"
          style={{
            background: `radial-gradient(ellipse 80% 60% at 50% 0%, ${GLOW_COLORS[glow]} 0%, transparent 70%)`,
            opacity: intensity,
          }}
        />
      )}

      {/* Top edge highlight — glass reflection */}
      <div
        className="pointer-events-none absolute top-0 left-4 right-4 h-px"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.04) 20%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.04) 80%, transparent 100%)',
        }}
      />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
