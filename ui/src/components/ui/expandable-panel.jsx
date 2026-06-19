/**
 * ExpandablePanel — Context-driven expand/collapse with spring height animation.
 * Faithfully adapted from nolly-studio/cult-ui: expandable-card.tsx (reduced from 16.5KB to ~4KB).
 *
 * Usage:
 *   <ExpandablePanel>
 *     <ExpandablePanel.Trigger>
 *       <TexturePanel.Title>Risk Flags (3) ▼</TexturePanel.Title>
 *     </ExpandablePanel.Trigger>
 *     <ExpandablePanel.Content>
 *       <p>PE-001 HIGH — BP 150/98, protein 2+</p>
 *       <p>GDM-002 MODERATE — glucose 104</p>
 *     </ExpandablePanel.Content>
 *   </ExpandablePanel>
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion';
import { cn } from '../../utils/cn';

const springConfig = { stiffness: 200, damping: 20, bounce: 0.2 };
const ExpandableContext = createContext({ isExpanded: false, toggleExpand: () => {} });
const useExpandable = () => useContext(ExpandableContext);

function ExpandablePanel({ defaultExpanded = false, className, children, ...props }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  return (
    <ExpandableContext.Provider value={{ isExpanded, toggleExpand: () => setIsExpanded(p => !p) }}>
      <div className={className} {...props}>{children}</div>
    </ExpandableContext.Provider>
  );
}

const ExpandableTrigger = React.forwardRef(({ className, children, ...props }, ref) => {
  const { toggleExpand, isExpanded } = useExpandable();
  return (
    <div ref={ref} onClick={toggleExpand} role="button" tabIndex={0} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleExpand(); } }}
      className={cn('cursor-pointer select-none', className)} {...props}>
      {typeof children === 'function' ? children({ isExpanded }) : children}
    </div>
  );
});
ExpandableTrigger.displayName = 'ExpandableTrigger';

const ExpandableContent = React.forwardRef(({ className, children, ...props }, ref) => {
  const { isExpanded } = useExpandable();
  const [height, setHeight] = useState(0);
  const animatedHeight = useMotionValue(0);
  const smoothHeight = useSpring(animatedHeight, springConfig);
  const measureRef = React.useCallback(node => { if (node) setHeight(node.scrollHeight); }, []);

  useEffect(() => { animatedHeight.set(isExpanded ? height : 0); }, [isExpanded, height, animatedHeight]);

  return (
    <motion.div ref={ref} style={{ height: smoothHeight, overflow: 'hidden' }} className={className} {...props}>
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div ref={measureRef} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
ExpandableContent.displayName = 'ExpandableContent';

export { ExpandablePanel, ExpandableTrigger, ExpandableContent, useExpandable };
