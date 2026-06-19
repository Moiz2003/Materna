/**
 * GlowButton — Mouse-tracking radial gradient glow button.
 * Adapted from nolly-studio/cult-ui: registry/default/ui/glow-button.tsx
 */
import { useRef, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';

export default function GlowButton({ to, href, children, glowColor = '#2DD4BF', className = '', size = 'md' }) {
  const [hovering, setHovering] = useState(false);
  const [glowX, setGlowX] = useState(50);
  const ref = useRef(null);

  const handleMove = useCallback((e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setGlowX(((e.clientX - rect.left) / rect.width) * 100);
  }, []);

  const sizes = { md: 'px-6 py-3 text-sm', lg: 'px-8 py-4 text-base' };
  const isExternal = !!href;

  const btn = (
    <span
      ref={ref}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      onMouseMove={handleMove}
      className={`relative inline-flex items-center justify-center gap-2 rounded-xl font-semibold overflow-hidden transition-colors duration-200 ${sizes[size]} bg-teal-600 hover:bg-teal-500 text-white no-underline ${className}`}
    >
      {/* Glow spotlight */}
      <span
        className="absolute pointer-events-none transition-opacity duration-200"
        style={{
          opacity: hovering ? 1 : 0,
          left: `${glowX}%`,
          top: '50%',
          transform: 'translate(-50%, -50%)',
          width: '180px',
          height: '120px',
          background: `radial-gradient(50% 50% at 50% 50%, ${glowColor}44 0%, ${glowColor}22 30%, transparent 70%)`,
          filter: 'blur(8px)',
          zIndex: 0,
        }}
      />
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </span>
  );

  if (isExternal) return <a href={href} className="no-underline">{btn}</a>;
  return <Link to={to} className="no-underline">{btn}</Link>;
}
