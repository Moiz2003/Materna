/**
 * TexturePanel — Compound card component with 4-layer nested borders.
 * Faithfully adapted from nolly-studio/cult-ui: texture-card.tsx.
 *
 * Usage:
 *   <TexturePanel variant="amber">
 *     <TexturePanel.Header>
 *       <TexturePanel.Title>Risk Flags</TexturePanel.Title>
 *       <TexturePanel.Description>3 flags fired</TexturePanel.Description>
 *     </TexturePanel.Header>
 *     <TexturePanel.Content>...</TexturePanel.Content>
 *     <TexturePanel.Footer>...</TexturePanel.Footer>
 *   </TexturePanel>
 */
import React from 'react';
import { cn } from '../../utils/cn';

const variants = {
  default: 'border-teal-500/20',
  amber:   'border-amber-500/20',
  danger:  'border-danger/20',
  success: 'border-success/20',
};

const variantInner = {
  default: 'border-teal-500/15',
  amber:   'border-amber-500/15',
  danger:  'border-red-500/15',
  success: 'border-emerald-500/15',
};

const variantInner2 = {
  default: 'border-teal-500/10',
  amber:   'border-amber-500/10',
  danger:  'border-red-500/10',
  success: 'border-emerald-500/10',
};

const TexturePanel = React.forwardRef(({ variant = 'default', className, children, ...props }, ref) => (
  <div ref={ref} className={cn('rounded-2xl border bg-bg-card backdrop-blur-xl', variants[variant], className)} {...props}>
    <div className={cn('rounded-[15px] border', variantInner[variant])}>
      <div className={cn('rounded-[14px] border', variantInner2[variant])}>
        <div className="rounded-[13px] border border-white/5">
          {children}
        </div>
      </div>
    </div>
  </div>
));
TexturePanel.displayName = 'TexturePanel';

const TexturePanelHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('px-5 pt-5 pb-2', className)} {...props} />
));
TexturePanelHeader.displayName = 'TexturePanelHeader';

const TexturePanelTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn('font-display font-semibold text-sm', className)} {...props} />
));
TexturePanelTitle.displayName = 'TexturePanelTitle';

const TexturePanelDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p ref={ref} className={cn('text-xs text-text-muted mt-0.5', className)} {...props} />
));
TexturePanelDescription.displayName = 'TexturePanelDescription';

const TexturePanelContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('px-5 py-3', className)} {...props} />
));
TexturePanelContent.displayName = 'TexturePanelContent';

const TexturePanelFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('flex items-center px-5 pb-5 pt-1 gap-2', className)} {...props} />
));
TexturePanelFooter.displayName = 'TexturePanelFooter';

export { TexturePanel, TexturePanelHeader, TexturePanelTitle, TexturePanelDescription, TexturePanelContent, TexturePanelFooter };
export default TexturePanel;
