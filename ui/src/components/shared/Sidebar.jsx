/**
 * Sidebar — Collapsible sidebar with smooth spring transitions.
 * Adapted from cult-ui dock + docs-sidebar patterns.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, FileCheck, Activity, Shield, Search, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';

const navItems = [
  { icon: FileCheck, label: 'Enter Data', id: 'nav-enter' },
  { icon: Activity, label: 'Findings', id: 'nav-findings' },
  { icon: Shield, label: 'Compliance', id: 'nav-compliance' },
  { icon: Search, label: 'Auditor', id: 'nav-auditor' },
  { icon: Settings, label: 'Pipeline', id: 'nav-pipeline' },
];

const springConfig = { type: 'spring', stiffness: 300, damping: 30, mass: 0.8 };

export default function Sidebar({ caseStatus }) {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <motion.aside
      animate={{ width: collapsed ? 56 : 220 }}
      transition={springConfig}
      className="hidden lg:flex flex-col border-r border-border bg-bg-dark/60 backdrop-blur-xl h-full overflow-hidden"
    >
      {/* Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-12 border-b border-border hover:bg-teal-500/10 transition-colors"
      >
        {collapsed ? <ChevronRight size={18} className="text-teal-400" /> : <ChevronLeft size={18} className="text-teal-400" />}
      </button>

      {/* Nav items */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-text-muted hover:text-text hover:bg-teal-500/10 transition-colors text-xs"
          >
            <item.icon size={18} className="text-teal-400 flex-shrink-0" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ duration: 0.15 }}
                  className="font-medium whitespace-nowrap"
                >
                  {item.label}
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        ))}
      </nav>

      {/* Status indicator */}
      <div className="border-t border-border p-3">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${caseStatus === 'SEALED' ? 'bg-success' : caseStatus === 'ESCALATED' ? 'bg-danger' : 'bg-teal-400'} animate-pulse`} />
          {!collapsed && <span className="text-xs text-text-muted font-mono">{caseStatus || 'Idle'}</span>}
        </div>
      </div>

      {/* Back to home */}
      <div className="border-t border-border p-2">
        <Link to="/" className="flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-text-subtle hover:text-teal-400 hover:bg-teal-500/5 transition-colors text-xs">
          <ChevronLeft size={14} />
          {!collapsed && <span>Home</span>}
        </Link>
      </div>
    </motion.aside>
  );
}
