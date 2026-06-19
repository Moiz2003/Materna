/**
 * StageSealed — Terminal card for SEALED/AUTO_CLEARED cases.
 * Shows final hash, audit verification, human decision, download & tamper demo.
 */
import { ShieldCheck, Download, Hammer, FileCheck2, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { FadeIn } from '../ui/fade-in';
import GlassPanel from '../ui/glass-panel';

function HashRow({ label, value }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    if (!value) return;
    navigator.clipboard?.writeText(value).then(() => {
      setCopied(true); setTimeout(() => setCopied(false), 1200);
    }).catch(() => {});
  };
  return (
    <div className="flex items-center justify-between gap-3 group">
      <span className="text-text-muted">{label}</span>
      <button onClick={copy} className="inline-flex items-center gap-1.5 font-mono text-xs text-teal-400 hover:text-teal-300 transition-colors">
        {value ? `${value.slice(0, 30)}…` : '—'}
        {value && (copied ? <Check size={12} className="text-success" /> : <Copy size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />)}
      </button>
    </div>
  );
}

export default function StageSealed({ caseData, auditData, decision = {}, packetUrl, onTamper, autoCleared }) {
  const verified = auditData?.verified;
  return (
    <FadeIn>
      <GlassPanel glow="emerald" intensity={0.4} className="p-5 space-y-4">
        <div className="flex items-center gap-2.5">
          <FileCheck2 size={18} className="text-success" />
          <h3 className="font-display font-semibold text-base text-text">
            {autoCleared ? 'Auto-cleared & sealed' : 'Sealed review packet'}
          </h3>
        </div>

        <div className="rounded-xl border border-border bg-bg-dark/30 p-4 space-y-2 text-sm">
          <HashRow label="Final hash" value={caseData?.final_hash} />
          <div className="flex items-center justify-between gap-3">
            <span className="text-text-muted">Audit chain</span>
            <span className={`inline-flex items-center gap-1.5 font-bold ${verified ? 'text-success' : 'text-danger'}`}>
              <ShieldCheck size={14} /> {verified ? 'VERIFIED' : 'TAMPERED'}
            </span>
          </div>
          <div className="flex items-center justify-between gap-3">
            <span className="text-text-muted">Transitions</span>
            <span className="text-text">{(auditData?.entries || []).length} entries</span>
          </div>
          {decision.verdict && (
            <div className="flex items-center justify-between gap-3">
              <span className="text-text-muted">Human decision</span>
              <span className="text-text font-medium">{decision.verdict.toUpperCase()} · {decision.reviewer}</span>
            </div>
          )}
        </div>

        <a
          href={packetUrl}
          target="_blank" rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 py-3 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold text-sm no-underline shadow-lg shadow-teal-500/20 transition-all"
        >
          <Download size={16} /> Download sealed PDF
        </a>

        <button
          onClick={onTamper}
          className="w-full inline-flex items-center justify-center gap-2 py-2 bg-amber-600/15 hover:bg-amber-600/25 border border-amber-500/30 text-amber-400 rounded-lg text-xs font-semibold transition-all"
        >
          <Hammer size={14} /> Tamper audit chain (demo)
        </button>
        <p className="text-xs text-text-subtle text-center">
          Tamper-evident — any alteration breaks the SHA-256 chain and is detected on next verify.
        </p>
      </GlassPanel>
    </FadeIn>
  );
}
