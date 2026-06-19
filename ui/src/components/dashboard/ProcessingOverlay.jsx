/**
 * ProcessingOverlay — shown in the main column immediately after submit, while
 * the four agents coordinate through Band and before the first results arrive.
 * Replaces the old "⏳ Processing…" pulse with a real animated pipeline.
 */
import { FadeIn } from '../ui/fade-in';
import { TexturePanel } from '../ui/texture-panel';
import AgentPipeline from './AgentPipeline';

export default function ProcessingOverlay({ status }) {
  return (
    <FadeIn>
      <TexturePanel className="p-8">
        <div className="flex flex-col items-center text-center gap-5">
          <div>
            <h3 className="font-display font-semibold text-base text-text">Coordinating the review board</h3>
            <p className="text-sm text-text-muted mt-1">
              Four specialist agents are analyzing this case through Band. This takes a few seconds.
            </p>
          </div>
          <AgentPipeline status={status} active />
        </div>
      </TexturePanel>
    </FadeIn>
  );
}
