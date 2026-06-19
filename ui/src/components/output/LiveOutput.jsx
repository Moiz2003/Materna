/**
 * LiveOutput — Context-aware right panel.
 * Shows tips during input, agent pipeline during processing,
 * Band Room + Audit during results. Uses GlassPanel.
 *
 * claude4.md §9
 */
import { Radio, ShieldCheck, ShieldAlert, Lightbulb, Keyboard } from 'lucide-react';
import GlassPanel from '../ui/glass-panel';
import BandRoom from '../band/BandRoom';
import AgentPipeline from '../dashboard/AgentPipeline';
import { statusMeta } from '../dashboard/caseModel';

const toneClasses = {
  teal:    'bg-teal-500/10 text-teal-400 border-teal-500/20',
  amber:   'bg-amber-500/10 text-amber-400 border-amber-500/20',
  danger:  'bg-danger/10 text-danger border-danger/20',
  success: 'bg-success/10 text-success border-success/20',
};

export default function LiveOutput({
  status, loading, roomMessages, bandRoomId, auditData, auditRef, isExpert = false,
}) {
  const meta = statusMeta(status);
  const hasCase = !!status || loading;
  const showResults = hasCase && !loading && status !== 'RECEIVED';

  return (
    <div className="space-y-4">
      {/* ---- No case: tips ---- */}
      {!hasCase && (
        <GlassPanel className="p-5">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb size={15} className="text-teal-400" />
            <span className="text-xs font-semibold uppercase tracking-wide text-text-subtle">Quick Tips</span>
          </div>
          <div className="space-y-2.5 text-xs text-text-muted leading-relaxed">
            <p>Paste clinical notes into <span className="text-text font-medium">Smart Paste</span> or load a demo case.</p>
            <p>Click <span className="text-teal-400 font-semibold">Submit to Review Board</span> to run all four AI agents.</p>
            <p>Results appear as cards — the doctor reviews flagged cases.</p>
          </div>
          {isExpert && (
            <div className="mt-4 pt-3 border-t border-border/40">
              <div className="flex items-center gap-2 mb-2">
                <Keyboard size={13} className="text-text-subtle" />
                <span className="text-[10px] font-mono text-text-subtle uppercase tracking-wider">Shortcuts</span>
              </div>
              <div className="space-y-1 text-[10px] font-mono text-text-subtle">
                <p><kbd className="px-1 py-0.5 rounded border border-border/30 text-text-muted">⌘K</kbd> Command palette</p>
                <p><kbd className="px-1 py-0.5 rounded border border-border/30 text-text-muted">⌘↵</kbd> Submit case</p>
                <p><kbd className="px-1 py-0.5 rounded border border-border/30 text-text-muted">⌘D</kbd> Load demo</p>
                <p><kbd className="px-1 py-0.5 rounded border border-border/30 text-text-muted">⌘N</kbd> New case</p>
              </div>
            </div>
          )}
        </GlassPanel>
      )}

      {/* ---- Pipeline + status ---- */}
      <GlassPanel glow={loading ? 'teal' : showResults ? 'emerald' : null} intensity={0.4} className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Radio size={15} className="text-teal-400" />
            <span className="text-xs font-semibold uppercase tracking-wide text-text-subtle">Pipeline</span>
          </div>
          {hasCase && (
            <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${toneClasses[meta.tone]}`}>
              {meta.label}
            </span>
          )}
        </div>
        <div className="flex justify-center py-1">
          <AgentPipeline
            status={status}
            active={
              loading ||
              (!!status && !['SEALED', 'AUTO_CLEARED', 'QUARANTINED'].includes(status))
            }
          />
        </div>
        {!hasCase && (
          <p className="text-[10px] text-text-subtle/50 text-center mt-2">
            Pipeline status will appear here after submission
          </p>
        )}
      </GlassPanel>

      {/* ---- Band Room ---- */}
      <GlassPanel className="p-4">
        <BandRoom messages={roomMessages} loading={loading} roomId={bandRoomId} />
      </GlassPanel>

      {/* ---- Audit trail ---- */}
      {auditData && (
        <GlassPanel className="p-4" ref={auditRef} glow={auditData.verified ? 'emerald' : 'red'} intensity={0.3}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {auditData.verified
                ? <ShieldCheck size={15} className="text-success" />
                : <ShieldAlert size={15} className="text-danger" />}
              <span className="text-xs font-semibold uppercase tracking-wide text-text-subtle">
                SHA-256 Audit Trail
              </span>
            </div>
            <span className={`text-xs font-bold ${auditData.verified ? 'text-success' : 'text-danger'}`}>
              {auditData.verified ? 'VERIFIED' : 'BROKEN'}
            </span>
          </div>
          <div className="space-y-0.5 max-h-72 overflow-y-auto pr-1">
            {(auditData.entries || []).map((e, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs py-1.5 border-b border-border/40 last:border-0"
              >
                <span className="text-teal-400 font-mono font-bold w-7 flex-shrink-0">#{e.seq}</span>
                <span className="text-text-muted w-20 truncate flex-shrink-0">{e.actor}</span>
                <span className="text-text-subtle flex-1 truncate">{e.action}</span>
                <code className="font-mono text-text-subtle flex-shrink-0">
                  {e.this_hash?.slice(7, 17)}…
                </code>
              </div>
            ))}
          </div>
        </GlassPanel>
      )}
    </div>
  );
}
