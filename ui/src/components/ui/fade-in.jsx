/**
 * FadeIn / FadeInStagger — Staggered fade-in animations with reduced-motion support.
 * Faithfully adapted from nolly-studio/cult-ui: fade-in.tsx.
 *
 * Usage:
 *   <FadeInStagger>
 *     <FadeIn><Card /></FadeIn>
 *     <FadeIn><Card /></FadeIn>
 *   </FadeInStagger>
 */
import { createContext, useContext } from 'react';
import { motion } from 'framer-motion';

const FadeInStaggerContext = createContext(false);
const viewport = { once: true, margin: '0px 0px -100px' };

export function FadeIn({ className, children, delay = 0, ...props }) {
  const inStagger = useContext(FadeInStaggerContext);
  return (
    <motion.div
      variants={{ hidden: { opacity: 0, y: 24 }, visible: { opacity: 1, y: 0 } }}
      transition={{ duration: 0.5, delay }}
      {...(inStagger ? {} : { initial: 'hidden', whileInView: 'visible', viewport })}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function FadeInStagger({ faster = false, className, children, ...props }) {
  return (
    <FadeInStaggerContext.Provider value={true}>
      <motion.div
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        transition={{ staggerChildren: faster ? 0.1 : 0.15 }}
        className={className}
        {...props}
      >
        {children}
      </motion.div>
    </FadeInStaggerContext.Provider>
  );
}
