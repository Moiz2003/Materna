/**
 * DashboardPage — Materna / Antenatal Review Board console.
 *
 * Split-pane, progressive-disclosure layout:
 *   [ SidebarNav ] [ main: input + results ] [ LiveOutput: pipeline/Band/audit ]
 *
 * All case-processing logic (submit, polling, decision, extraction) is
 * preserved from the original monolith — the case JSON submitted to /cases is
 * byte-for-byte the same. The novice-facing form is a thin serialization layer
 * on top (see components/dashboard/caseModel.js).
 */
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, X, UploadCloud, Send, Loader2, CheckCircle2, Stethoscope } from 'lucide-react';
import {
  submitCase, getCase, getRoom, submitDecision, getPacketUrl, getAudit,
  extractCase, extractFromImage, getHealth, demoTamper,
} from '../api';

import SidebarNav from '../components/dashboard/SidebarNav';
import SmartPasteInput from '../components/dashboard/SmartPasteInput';
import PatientForm from '../components/dashboard/PatientForm';
import CaseJSONAdvanced from '../components/dashboard/CaseJSONAdvanced';
import ResultsStage from '../components/dashboard/ResultsStage';
import ProcessingTheatre from '../components/dashboard/ProcessingTheatre';
import EmptyState from '../components/dashboard/EmptyState';
import LiveOutput from '../components/output/LiveOutput';
import CommandPalette from '../components/dashboard/CommandPalette';
import OnboardingTour from '../components/dashboard/OnboardingTour';
import Toast from '../components/ui/toast';
import GlassPanel from '../components/ui/glass-panel';
import {
  EMPTY_FORM, buildCase, parseCaseToForm, validateForm,
  isAwaitingDecision, isComplete, DEMO_CASES,
} from '../components/dashboard/caseModel';

export default function DashboardPage() {
  // ── case lifecycle state (unchanged contract) ──
  const [caseId, setCaseId] = useState('');
  const [caseData, setCaseData] = useState(null);
  const [roomMessages, setRoomMessages] = useState([]);
  const [bandRoomId, setBandRoomId] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const [error, setError] = useState('');
  const [reprocessing, setReprocessing] = useState(false);
  const [reviewer, setReviewer] = useState('Dr. Saima Javed');
  const [note, setNote] = useState('');

  // ── Mode & UX state ──
  const [isExpert, setIsExpert] = useState(() => localStorage.getItem('materna_expert') === 'true');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('materna_onboarded'));
  const [toast, setToast] = useState({ show: false, message: '', tone: 'teal' });

  // ── input layer ──
  const [form, setForm] = useState(EMPTY_FORM);
  const [caseJson, setCaseJson] = useState(buildCase(EMPTY_FORM, {}));
  const [clinicalNotes, setClinicalNotes] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [usgImage, setUsgImage] = useState(null);
  const [reviewFields, setReviewFields] = useState([]);
  const [submittedForm, setSubmittedForm] = useState(EMPTY_FORM);

  // ── session navigation state ──
  const [history, setHistory] = useState({}); // { caseId: status }
  const [healthOk, setHealthOk] = useState(null);

  const pollRef = useRef(null);
  const auditRef = useRef(null);
  const status = caseData?.status || '';
  const errors = useMemo(() => validateForm(form), [form]);

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  /* ── Mode toggle ── */
  const toggleMode = useCallback(() => {
    setIsExpert((prev) => { const next = !prev; localStorage.setItem('materna_expert', String(next)); return next; });
  }, []);

  // backend health probe for the sidebar
  useEffect(() => {
    let alive = true;
    const ping = () => getHealth().then(() => alive && setHealthOk(true)).catch(() => alive && setHealthOk(false));
    ping();
    const id = setInterval(ping, 15000);
    return () => { alive = false; clearInterval(id); };
  }, []);

  // ── form ⇄ json syncing (explicit, no effect loops) ──
  const parsedJson = () => { try { return JSON.parse(caseJson); } catch { return {}; } };

  const updateForm = (key, value) => {
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      setCaseJson(buildCase(next, parsedJson()));
      return next;
    });
  };

  const applyCaseObject = (obj) => {
    const nextForm = parseCaseToForm(obj);
    setForm(nextForm);
    setCaseJson(JSON.stringify(obj, null, 2));
  };

  const onAdvancedJsonChange = (text) => {
    setCaseJson(text);
    try { setForm(parseCaseToForm(JSON.parse(text))); } catch { /* keep form until valid */ }
  };

  const loadDemo = (demo) => {
    handleNewCase();
    const f = demo.form;
    setForm(f);
    setCaseJson(buildCase(f, {}));
  };

  // ── polling (unchanged) ──
  const startPolling = (cid) => {
    if (pollRef.current) clearInterval(pollRef.current);
    const poll = async () => {
      try {
        const [d, r, a] = await Promise.all([getCase(cid), getRoom(cid), getAudit(cid)]);
        setCaseData(d);
        setRoomMessages(r.messages || []);
        setBandRoomId(r.band_room_id || null);
        setAuditData(a);
        setLoading(false);
        setHistory((h) => ({ ...h, [cid]: d.status }));
        if (d.status === 'SEALED' || d.status === 'QUARANTINED') {
          if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
        }
      } catch (e) { setLoading(false); }
    };
    poll();
    pollRef.current = setInterval(poll, 1200);
  };

  const handleNewCase = () => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    setCaseId(''); setCaseData(null); setRoomMessages([]); setBandRoomId(null);
    setAuditData(null); setLoading(false); setError(''); setStartedAt(null);
    setForm(EMPTY_FORM); setCaseJson(buildCase(EMPTY_FORM, {}));
    setClinicalNotes(''); setUsgImage(null); setReviewFields([]);
    setReprocessing(false); setNote(''); setSubmittedForm(EMPTY_FORM);
  };

  const handleSubmit = async () => {
    setError(''); setLoading(true); setStartedAt(Date.now());
    setCaseData(null); setRoomMessages([]); setBandRoomId(null); setAuditData(null);
    setSubmittedForm(form);
    try {
      const payload = buildCase(form, parsedJson());
      const fd = new FormData();
      fd.append('case', JSON.stringify(payload));
      if (usgImage) fd.append('usg_image', usgImage);
      const r = await submitCase(fd);
      setCaseId(r.case_id);
      setHistory((h) => ({ ...h, [r.case_id]: 'RECEIVED' }));
      startPolling(r.case_id);
    } catch (e) { setError(e.message); setLoading(false); }
  };

  /* ── Command palette + keyboard shortcuts ── */
  const commands = useMemo(() => [
    { id: 'submit', label: 'Submit case', shortcut: '⌘↵', action: handleSubmit },
    { id: 'demo', label: 'Load demo case', shortcut: '⌘D', action: () => loadDemo(DEMO_CASES[0]) },
    { id: 'new', label: 'New case', shortcut: '⌘N', action: handleNewCase },
    { id: 'mode', label: isExpert ? 'Switch to Novice mode' : 'Switch to Expert mode', action: toggleMode },
    { id: 'json', label: 'Toggle JSON editor', shortcut: '⌘E', action: () => setIsExpert((p) => !p) },
  ], [isExpert, toggleMode]);

  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setPaletteOpen((p) => !p); return; }
      if (!isExpert) return;
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); handleSubmit(); }
      if ((e.metaKey || e.ctrlKey) && e.key === 'n') { e.preventDefault(); handleNewCase(); }
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') { e.preventDefault(); loadDemo(DEMO_CASES[0]); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isExpert]);

  /* ── Toast on results arrival ── */
  const prevStatusRef = useRef(status);
  useEffect(() => {
    if (status && status !== 'RECEIVED' && prevStatusRef.current !== status) {
      if (status === 'ESCALATED') setToast({ show: true, message: 'Review complete — awaiting your decision', tone: 'amber' });
      else if (status === 'SEALED' || status === 'AUTO_CLEARED') setToast({ show: true, message: 'Case sealed — packet ready for download', tone: 'emerald' });
      else setToast({ show: true, message: 'Case processed successfully', tone: 'teal' });
    }
    prevStatusRef.current = status;
  }, [status]);

  const handleExtract = async () => {
    if (!clinicalNotes.trim()) return;
    setExtracting(true); setError('');
    try { const r = await extractCase(clinicalNotes); applyCaseObject(r.case); }
    catch (e) { setError('Extraction failed: ' + e.message); }
    setExtracting(false);
  };

  const handleImageExtract = async (file) => {
    if (!file) return;
    setExtracting(true); setError(''); setReviewFields([]);
    try {
      const r = await extractFromImage(file);
      if (r.extracted_data) applyCaseObject(r.extracted_data);
      setReviewFields(r.needs_review || []);
    } catch (e) { setError('Image extraction failed: ' + e.message); }
    setExtracting(false);
  };

  const handleDecision = async (verdict) => {
    if (verdict === 'override' && !note.trim()) { setError('Enter your instruction so the AI can re-process.'); return; }
    try {
      if (verdict === 'override') setReprocessing(true);
      await submitDecision(caseId, { verdict, note, reviewer: reviewer || 'Dr. Saima Javed' });
      const data = await getCase(caseId);
      setCaseData(data);
      setHistory((h) => ({ ...h, [caseId]: data.status }));
    } catch (e) { setError(e.message); }
    finally { setReprocessing(false); }
  };

  const handleDemoTamper = async () => {
    try { await demoTamper(caseId); const d = await getAudit(caseId); setAuditData(d); }
    catch (e) { setError('Tamper demo failed: ' + e.message); }
  };

  const focusAudit = () => auditRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });

  // ── derived counts ──
  const pending = Object.values(history).filter(isAwaitingDecision).length;
  const completed = Object.values(history).filter(isComplete).length;

  const showResults = !!status && status !== 'RECEIVED';
  const showInput = !caseId && !loading;
  const showProcessing = !showResults && (loading || (!!caseId && (!status || status === 'RECEIVED')));

  return (
    <div className="min-h-screen bg-bg-dark text-text flex">
      <SidebarNav
        pending={pending} completed={completed} healthOk={healthOk}
        onNewCase={handleNewCase} onAuditFocus={focusAudit}
        isExpert={isExpert} onToggleMode={toggleMode}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <nav className="sticky top-0 z-50 border-b border-border bg-bg-dark/80 backdrop-blur-xl">
          <div className="px-4 sm:px-6 h-16 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 sm:gap-3 font-display font-bold text-base sm:text-lg text-teal-400 no-underline">
              <svg width="26" height="26" viewBox="0 0 32 32" className="sm:w-7 sm:h-7"><circle cx="16" cy="16" r="14" fill="none" stroke="#2DD4BF" strokeWidth="2" /><circle cx="16" cy="16" r="7" fill="none" stroke="#0D9488" strokeWidth="2" strokeDasharray="4 2" /></svg>
              <span className="hidden sm:inline">Antenatal Review Board</span>
            </Link>
            <div className="flex items-center gap-3 sm:gap-4 text-xs sm:text-sm">
              <span className="hidden sm:inline-flex items-center gap-1.5 text-text-muted text-sm">
                <Stethoscope size={15} className="text-teal-400" /> {reviewer}
              </span>
              <Link to="/about" className="text-text-muted hover:text-text no-underline transition-colors hidden sm:inline">About</Link>
            </div>
          </div>
        </nav>

        {error && (
          <div className="bg-danger/10 border-b border-danger/20 text-danger text-xs sm:text-sm px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
            <span className="flex items-center gap-2"><AlertTriangle size={15} /> {error}</span>
            <button onClick={() => setError('')} className="text-danger hover:text-red-400"><X size={18} /></button>
          </div>
        )}

        {/* Split pane: main | output */}
        <div className="flex-1 px-4 sm:px-6 py-6 grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_400px] gap-6 max-w-[1600px] w-full mx-auto">
          {/* MAIN COLUMN */}
          <div className="space-y-4 min-w-0">
            {showInput && (
              <>
                <SmartPasteInput
                  notes={clinicalNotes}
                  onNotesChange={setClinicalNotes}
                  onExtract={handleExtract}
                  extracting={extracting}
                  onLoadDemo={loadDemo}
                  disabled={loading}
                  isExpert={isExpert}
                />

                {reviewFields.length > 0 && (
                  <GlassPanel glow="amber" intensity={0.4} className="p-5 space-y-3">
                    <h3 className="font-display font-semibold text-base text-amber-400 flex items-center gap-2">
                      <AlertTriangle size={16} /> Confirm uncertain fields ({reviewFields.length})
                    </h3>
                    <p className="text-sm text-amber-400/80">The AI could not read these confidently. Correct them in the form below — the highlighted fields need attention.</p>
                    <div className="flex flex-wrap gap-1.5">
                      {reviewFields.map((rf) => (
                        <span key={rf.field} className="text-xs font-mono px-2 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400">
                          {rf.label || rf.field}{rf.best_guess ? ` ≈ ${rf.best_guess}` : ''}
                        </span>
                      ))}
                    </div>
                  </GlassPanel>
                )}

                <GlassPanel className="p-5 space-y-5">
                  <div className="flex items-center gap-2 text-text-subtle">
                    <span className="text-xs font-semibold uppercase tracking-wide">or fill manually</span>
                    <div className="h-px bg-border flex-1" />
                  </div>

                  <PatientForm form={form} errors={errors} onChange={updateForm} />

                  {/* Ultrasound image */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <UploadCloud size={14} className="text-teal-400" />
                      <span className="text-xs font-semibold uppercase tracking-wide text-text-subtle">Ultrasound image (optional)</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <label className="inline-flex items-center gap-2 px-3 py-2 bg-bg-dark border border-border rounded-lg text-sm text-text-muted hover:text-text hover:border-teal-500/40 cursor-pointer transition-colors">
                        <UploadCloud size={15} /> Choose file
                        <input type="file" accept="image/*" className="hidden"
                          onChange={(e) => { const file = e.target.files[0]; setUsgImage(file); if (file) handleImageExtract(file); }} />
                      </label>
                      {extracting && <span className="inline-flex items-center gap-1.5 text-sm text-teal-400"><Loader2 size={14} className="animate-spin" /> Reading image…</span>}
                      {usgImage && !extracting && <span className="inline-flex items-center gap-1.5 text-sm text-success"><CheckCircle2 size={14} /> {usgImage.name}</span>}
                    </div>
                  </div>

                  <CaseJSONAdvanced value={caseJson} onChange={onAdvancedJsonChange} />

                  <button
                    onClick={handleSubmit}
                    disabled={loading || Object.keys(errors).length > 0}
                    className="w-full inline-flex items-center justify-center gap-2 py-3.5 bg-gradient-to-r from-teal-600 to-teal-500 text-white rounded-xl font-bold text-sm shadow-xl shadow-teal-500/20 hover:brightness-110 transition-all disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed"
                  >
                    {loading ? <><Loader2 size={17} className="animate-spin" /> Submitting…</> : <><Send size={16} /> Submit to Review Board</>}
                  </button>
                  {Object.keys(errors).length > 0 && (
                    <p className="text-xs text-danger text-center -mt-2">Fix the highlighted fields before submitting.</p>
                  )}
                </GlassPanel>
              </>
            )}

            {showProcessing && (
              <ProcessingTheatre status={status} startedAt={startedAt || Date.now()} />
            )}

            {/* Toast */}
            <Toast
              show={toast.show}
              message={toast.message}
              tone={toast.tone}
              icon={CheckCircle2}
              onDismiss={() => setToast({ show: false, message: '', tone: 'teal' })}
            />

            {/* Command palette */}
            <CommandPalette
              open={paletteOpen}
              onClose={() => setPaletteOpen(false)}
              commands={commands}
            />

            {/* Onboarding */}
            {showOnboarding && (
              <OnboardingTour onComplete={() => setShowOnboarding(false)} />
            )}

            {showResults ? (
              <ResultsStage
                caseData={caseData} form={submittedForm} auditData={auditData}
                packetUrl={getPacketUrl(caseId)}
                reviewer={reviewer} note={note} reprocessing={reprocessing}
                onReviewerChange={setReviewer} onNoteChange={setNote}
                onDecision={handleDecision} onTamper={handleDemoTamper}
              />
            ) : (
              showInput && <EmptyState isExpert={isExpert} />
            )}
          </div>

          {/* OUTPUT COLUMN */}
          <div className="min-w-0">
            <div className="xl:sticky xl:top-24">
              <LiveOutput
                status={status} loading={loading}
                roomMessages={roomMessages} bandRoomId={bandRoomId}
                auditData={auditData} auditRef={auditRef} isExpert={isExpert}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
