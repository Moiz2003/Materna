import { useEffect, useRef } from 'react';
import { FileCheck, Activity, Shield, Search, Settings, User } from 'lucide-react';

const AGENT_ICONS = { intake: FileCheck, dating_risk: Activity, guideline: Shield, auditor: Search, orchestrator: Settings, human: User };
const AGENT_COLORS = { intake: 'text-teal-400', dating_risk: 'text-amber-400', guideline: 'text-teal-400', auditor: 'text-amber-400', orchestrator: 'text-text-muted', human: 'text-amber-400' };
const AGENT_LABELS = { intake: 'Intake', dating_risk: 'Dating & Risk', guideline: 'Guideline', auditor: 'Auditor', orchestrator: 'Orchestrator', human: 'Human OB' };

export default function BandRoom({ messages = [], loading, roomId }) {
  const scrollRef = useRef(null);
  useEffect(() => { scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight); }, [messages]);

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">💬 Band Room {loading && <span className="text-teal-400 animate-pulse">● LIVE</span>}</h3>
      </div>
      {roomId ? (
        <div className="text-xs text-teal-400 bg-teal-500/5 border border-teal-500/20 rounded-lg px-3 py-2 mb-3 font-mono flex items-center gap-2">
          🟢 Live Band room · <code className="text-teal-400">{roomId.slice(0, 12)}…</code>
          <span className="text-text-subtle ml-auto">agents coordinating via Band</span>
        </div>
      ) : messages.length > 0 ? (
        <div className="text-xs text-text-muted border border-border rounded-lg px-3 py-2 mb-3">
          ⚪ Local coordination · Band offline
        </div>
      ) : null}
      <div ref={scrollRef} className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-text-subtle text-xs italic text-center py-8">Awaiting agent messages…</p>
        )}
        {messages.map((m, i) => {
          const actor = m.actor || m.from_agent || '?';
          const action = m.action || m.intent || 'post';
          const Icon = AGENT_ICONS[actor] || Settings;
          const colorClass = AGENT_COLORS[actor] || 'text-text-muted';
          const label = AGENT_LABELS[actor] || actor;
          return (
            <div key={i} className="flex gap-2.5 py-2 border-b border-border/50 last:border-0">
              <Icon size={16} className={`${colorClass} mt-0.5 flex-shrink-0`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="font-semibold text-xs text-text">{label}</span>
                  <span className="text-[10px] text-text-subtle bg-border/50 px-1.5 py-0.5 rounded">{action}</span>
                  <span className="text-[10px] text-text-subtle ml-auto font-mono">{m.ts ? new Date(m.ts).toLocaleTimeString() : ''}</span>
                </div>
                {m.payload_hash && <code className="text-[10px] text-text-subtle font-mono block truncate">{m.this_hash?.slice(0, 24)}…</code>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
