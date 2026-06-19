/**
 * CommandPalette — ⌘K command palette for expert mode.
 * Keyboard-driven command menu with search/filter.
 *
 * Props:
 *   open: boolean
 *   onClose: () => void
 *   commands: Array<{ id, label, shortcut, action }>
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search } from 'lucide-react';

export default function CommandPalette({ open, onClose, commands = [] }) {
  const [query, setQuery] = useState('');
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef(null);

  const filtered = query
    ? commands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()))
    : commands;

  /* Focus input on open */
  useEffect(() => {
    if (open) {
      setQuery('');
      setSelectedIdx(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  /* Keyboard navigation */
  const handleKey = useCallback(
    (e) => {
      if (e.key === 'Escape') { onClose(); return; }
      if (e.key === 'ArrowDown') { e.preventDefault(); setSelectedIdx((i) => Math.min(i + 1, filtered.length - 1)); }
      if (e.key === 'ArrowUp') { e.preventDefault(); setSelectedIdx((i) => Math.max(i - 1, 0)); }
      if (e.key === 'Enter' && filtered[selectedIdx]) {
        filtered[selectedIdx].action();
        onClose();
      }
    },
    [filtered, selectedIdx, onClose],
  );

  useEffect(() => {
    if (!open) return;
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, handleKey]);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-[200] bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Palette */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -10 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="fixed top-[20%] left-1/2 -translate-x-1/2 z-[210] w-full max-w-md"
          >
            <div
              className="rounded-2xl border border-border/60 shadow-2xl shadow-black/50 overflow-hidden"
              style={{ background: 'rgba(15, 23, 42, 0.92)', backdropFilter: 'blur(40px)' }}
            >
              {/* Search input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-border/40">
                <Search size={16} className="text-text-subtle flex-shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => { setQuery(e.target.value); setSelectedIdx(0); }}
                  placeholder="Type a command…"
                  className="flex-1 bg-transparent text-sm text-text placeholder:text-text-subtle/50 outline-none"
                />
                <kbd className="text-[10px] font-mono text-text-subtle/40 px-1.5 py-0.5 rounded border border-border/30">
                  esc
                </kbd>
              </div>

              {/* Command list */}
              <div className="max-h-64 overflow-y-auto py-1">
                {filtered.length === 0 && (
                  <div className="px-4 py-6 text-center text-sm text-text-subtle">
                    No commands found
                  </div>
                )}
                {filtered.map((cmd, i) => (
                  <button
                    key={cmd.id}
                    onClick={() => { cmd.action(); onClose(); }}
                    className={`w-full flex items-center justify-between px-4 py-2.5 text-left transition-colors ${
                      i === selectedIdx
                        ? 'bg-teal-500/10 text-teal-400'
                        : 'text-text-muted hover:bg-white/[0.03]'
                    }`}
                  >
                    <span className="text-sm">{cmd.label}</span>
                    {cmd.shortcut && (
                      <kbd className="text-[10px] font-mono text-text-subtle/50 px-1.5 py-0.5 rounded border border-border/30">
                        {cmd.shortcut}
                      </kbd>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
