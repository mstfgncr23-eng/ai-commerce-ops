import {Composition} from 'remotion';
import {AiCommerceWorkflow} from './AiCommerceWorkflow';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="AiCommerceWorkflow"
      component={AiCommerceWorkflow}
      durationInFrames={1515}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        candidateName: 'Mustafa Gencer',
        contactLine: 'github.com/mstfgncr23-eng',
        portfolioUrl: 'linkedin.com/in/mustafa-gencer-dev',
        projectName: 'AI Commerce Ops',
        roleName: 'AI & E-TİCARET DEVELOPER',
      }}
    />
  );
};
