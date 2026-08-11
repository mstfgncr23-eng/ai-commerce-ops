import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {AgentScene} from './scenes/AgentScene';
import {ArchitectureScene} from './scenes/ArchitectureScene';
import {ChallengeScene} from './scenes/ChallengeScene';
import {ProofScene} from './scenes/ProofScene';
import {ReliabilityScene} from './scenes/ReliabilityScene';
import {RequirementScene} from './scenes/RequirementScene';
import type {ShowcaseProps} from './types';

export const AiCommerceWorkflow: React.FC<ShowcaseProps> = (props) => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={180} name="01 · Proje Özeti">
        <RequirementScene projectName={props.projectName} roleName={props.roleName} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 18})} />

      <TransitionSeries.Sequence durationInFrames={225} name="02 · Vaka">
        <ChallengeScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 18})} />

      <TransitionSeries.Sequence durationInFrames={360} name="03 · Mimari">
        <ArchitectureScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 18})} />

      <TransitionSeries.Sequence durationInFrames={330} name="04 · Karar Katmanı">
        <AgentScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 18})} />

      <TransitionSeries.Sequence durationInFrames={270} name="05 · İşletilebilirlik">
        <ReliabilityScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 18})} />

      <TransitionSeries.Sequence durationInFrames={240} name="06 · Sonuç">
        <ProofScene {...props} />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
