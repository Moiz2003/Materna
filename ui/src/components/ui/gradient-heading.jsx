/**
 * GradientHeading — Animated gradient text heading.
 * Faithfully adapted from nolly-studio/cult-ui: gradient-heading.tsx.
 *
 * Usage:
 *   <GradientHeading size="xl" variant="teal-amber">
 *     Obstetric Safety Review
 *   </GradientHeading>
 */
import React from 'react';
import { cn } from '../../utils/cn';

const sizeClasses = {
  sm:  'text-xl sm:text-2xl lg:text-3xl',
  md:  'text-2xl sm:text-3xl lg:text-4xl',
  lg:  'text-3xl sm:text-4xl lg:text-5xl',
  xl:  'text-4xl sm:text-5xl lg:text-6xl',
  xxl: 'text-5xl sm:text-6xl lg:text-[6rem]',
};

const variantClasses = {
  'teal':       'bg-gradient-to-r from-teal-400 to-teal-600',
  'amber':      'bg-gradient-to-r from-amber-400 to-amber-600',
  'teal-amber': 'bg-gradient-to-r from-teal-400 via-teal-300 to-amber-400',
  'light':      'bg-gradient-to-r from-text to-text-muted',
};

const GradientHeading = React.forwardRef(({ size = 'md', variant = 'teal', weight = 'bold', className, children, ...props }, ref) => {
  const Comp = props.as || 'h2';
  return (
    <Comp ref={ref} className={cn('tracking-tight', className)} {...props}>
      <span className={cn('bg-clip-text text-transparent', sizeClasses[size], variantClasses[variant], `font-${weight}`)}>
        {children}
      </span>
    </Comp>
  );
});
GradientHeading.displayName = 'GradientHeading';

export { GradientHeading };
export default GradientHeading;
