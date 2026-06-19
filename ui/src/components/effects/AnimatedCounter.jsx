/**
 * AnimatedCounter — counts up from 0 when scrolled into view.
 * Uses IntersectionObserver + requestAnimationFrame with easeOutCubic.
 */
import { useState, useEffect, useRef } from 'react';

export default function AnimatedCounter({ value, suffix = '', duration = 1800 }) {
  const [display, setDisplay] = useState('0');
  const ref = useRef(null);
  const fired = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const num = parseInt(value, 10);
    if (isNaN(num)) {
      setDisplay(value);
      return;
    }

    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !fired.current) {
          fired.current = true;
          const start = performance.now();
          const tick = (now) => {
            const p = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            setDisplay(Math.floor(eased * num).toString());
            if (p < 1) requestAnimationFrame(tick);
            else setDisplay(num.toString());
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.4 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [value, duration]);

  return (
    <span ref={ref} className="tabular-nums">
      {display}
      {suffix}
    </span>
  );
}
