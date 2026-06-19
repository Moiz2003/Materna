/**
 * SidebarNav — purpose-driven navigation rail (replaces the decorative
 * Sidebar). Collapsible. Shows a primary "New Case" action, live session
 * counters for cases awaiting review and completed, a jump-to-audit action,
 * and a backend health indicator. Counts are real session state — there is no
 * list endpoint, so they reflect cases processed in this session.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft, ChevronRight, FilePlus2, Clock, CheckCircle2,
  ScrollText, Home, Circle,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ModeSwitch from './ModeSwitch';

const spring = { type: 'spring', stiffness: 300, damping: 30, mass: 0.8 };

function NavButton({ icon: Icon, label, count, collapsed, onClick, accent = 'teal', primary }) {
  const accentText = accent === 'amber' ? 'text-amber-400' : accent === 'success' ? 'text-success' : 'text-teal-400';
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm transition-colors ${
        primary
          ? 'bg-teal-600 hover:bg-teal-500 text-white font-semibold'
          : 'text-text-muted hover:text-text hover:bg-teal-500/10'
      }`}
    >
      <Icon size={18} className={`flex-shrink-0 ${primary ? 'text-white' : accentText}`} />
      <AnimatePresence>
        {!collapsed && (
          <motion.span
            initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
            transition={{ duration: 0.15 }} className="font-medium whitespace-nowrap flex-1 text-left"
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>
      {count != null && count > 0 && (
        <span className={`text-xs font-bold rounded-full min-w-5 h-5 px-1.5 flex items-center justify-center ${
          collapsed ? 'absolute ml-7 -mt-5' : ''
        } ${accent === 'amber' ? 'bg-amber-500/20 text-amber-400' : 'bg-teal-500/20 text-teal-400'}`}>
          {count}
        </span>
      )}
    </button>
  );
}

export default function SidebarNav({
  pending = 0, completed = 0, healthOk = null, onNewCase, onAuditFocus,
  isExpert = false, onToggleMode,
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 232 }}
      transition={spring}
      className="hidden lg:flex flex-col border-r border-border bg-bg-dark/60 backdrop-blur-xl sticky top-0 h-screen overflow-hidden flex-shrink-0"
    >
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex items-center justify-center h-14 border-b border-border hover:bg-teal-500/10 transition-colors flex-shrink-0"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={18} className="text-teal-400" /> : <ChevronLeft size={18} className="text-teal-400" />}
      </button>

      <nav className="flex-1 py-4 space-y-1 px-2.5">
        <NavButton icon={FilePlus2} label="New Case" collapsed={collapsed} onClick={onNewCase} primary />
        <div className="h-px bg-border my-2 mx-1" />
        <NavButton icon={Clock} label="Awaiting review" count={pending} collapsed={collapsed} accent="amber" onClick={onAuditFocus} />
        <NavButton icon={CheckCircle2} label="Completed" count={completed} collapsed={collapsed} accent="success" onClick={onAuditFocus} />
        <div className="h-px bg-border my-2 mx-1" />
        <NavButton icon={ScrollText} label="Audit Logs" collapsed={collapsed} onClick={onAuditFocus} />

        <div className="h-px bg-border my-2 mx-1" />
        <div className="px-1">
          <ModeSwitch isExpert={isExpert} onToggle={onToggleMode} />
        </div>
      </nav>

      <div className="border-t border-border p-3 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Circle
            size={9}
            className={`flex-shrink-0 ${healthOk === false ? 'text-danger' : healthOk ? 'text-success' : 'text-text-subtle'} ${healthOk == null ? 'animate-pulse' : ''}`}
            fill="currentColor"
          />
          {!collapsed && (
            <span className="text-xs text-text-muted font-mono">
              {healthOk === false ? 'Backend offline' : healthOk ? 'System OK' : 'Checking…'}
            </span>
          )}
        </div>
      </div>

      <div className="border-t border-border p-2 flex-shrink-0">
        <Link to="/" className="flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-text-subtle hover:text-teal-400 hover:bg-teal-500/5 transition-colors text-xs no-underline">
          <Home size={14} /> {!collapsed && <span>Home</span>}
        </Link>
      </div>
    </motion.aside>
  );
}
