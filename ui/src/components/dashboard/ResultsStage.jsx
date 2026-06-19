/**
 * ResultsStage — progressive results dispatcher. Renders exactly the cards
 * that the case's current pipeline status warrants, top to bottom, each
 * animating in with a staggered arrival ceremony via StageTransition.
 */
import StageStructured from './StageStructured';
import StageAnalyzed from './StageAnalyzed';
import StageChecked from './StageChecked';
import StageDecision from './StageDecision';
import StageSealed from './StageSealed';
import StageTransition from './StageTransition';
import { completedSteps } from './caseModel';

export default function ResultsStage({
  caseData, form, auditData, packetUrl,
  reviewer, note, reprocessing,
  onReviewerChange, onNoteChange, onDecision, onTamper,
}) {
  const status = caseData?.status || '';
  if (!status || status === 'RECEIVED') return null;

  const finding = caseData.finding || {};
  const flags = caseData.flags || [];
  const compliance = caseData.compliance || {};
  const auditor = caseData.auditor || {};
  const decision = caseData.human_decision || {};
  const plan = caseData.proposed_plan;
  const brief = caseData.escalation_brief || {};

  const steps = completedSteps(status);
  const showAnalyzed = steps >= 2 || finding.ga_lmp_weeks != null || flags.length > 0;
  const showChecked = steps >= 3 || compliance.veto !== undefined || auditor.challenged !== undefined;
  const sealed = status === 'SEALED';
  const autoCleared = status === 'AUTO_CLEARED';

  return (
    <div className="space-y-4">
      <StageTransition delay={0}>
        <StageStructured form={form} status={status} />
      </StageTransition>
      {showAnalyzed && (
        <StageTransition delay={0.12}>
          <StageAnalyzed finding={finding} flags={flags} />
        </StageTransition>
      )}
      {showChecked && (
        <StageTransition delay={0.18}>
          <StageChecked compliance={compliance} auditor={auditor} />
        </StageTransition>
      )}

      {/* Human decision lives with findings only while a verdict is pending */}
      {status === 'ESCALATED' && (
        <StageTransition delay={0.24}>
          <StageDecision
            plan={plan} brief={brief} reviewer={reviewer} note={note} reprocessing={reprocessing}
            onReviewerChange={onReviewerChange} onNoteChange={onNoteChange} onDecision={onDecision}
          />
        </StageTransition>
      )}

      {(sealed || autoCleared) && (
        <StageTransition delay={0.24}>
          <StageSealed
            caseData={caseData} auditData={auditData} decision={decision}
            packetUrl={packetUrl} onTamper={onTamper} autoCleared={autoCleared}
          />
        </StageTransition>
      )}
    </div>
  );
}
