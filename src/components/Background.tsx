import type {CSSProperties, ReactNode} from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const palette = {
  ink: '#07110f',
  panel: 'rgba(14, 31, 28, 0.78)',
  line: 'rgba(148, 255, 190, 0.16)',
  mint: '#9affbd',
  cyan: '#65e9ff',
  warm: '#ffbb8d',
  text: '#f4fff8',
  muted: '#9db7ab',
};

export const colors = palette;

export const Background: React.FC<{children: ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill style={{backgroundColor: palette.ink, color: palette.text, fontFamily: 'Arial, Helvetica, sans-serif', overflow: 'hidden'}}>
      <AbsoluteFill style={{opacity: 0.34, backgroundImage: 'linear-gradient(rgba(154,255,189,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(154,255,189,0.07) 1px, transparent 1px)', backgroundSize: '64px 64px', translate: `${interpolate(frame, [0, durationInFrames], [0, 64], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.linear})}px ${interpolate(frame, [0, durationInFrames], [0, 32], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.linear})}px`}} />
      <div style={{position:'absolute',width:740,height:740,left:-210,top:-260,borderRadius:'50%',background:'radial-gradient(circle, rgba(63,255,147,0.22), transparent 68%)',translate:`${interpolate(frame,[0,durationInFrames],[0,190],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)})}px 0px`}} />
      <div style={{position:'absolute',width:900,height:900,right:-360,bottom:-520,borderRadius:'50%',background:'radial-gradient(circle, rgba(69,217,255,0.17), transparent 69%)',translate:`${interpolate(frame,[0,durationInFrames],[0,-140],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)})}px 0px`}} />
      {children}
    </AbsoluteFill>
  );
};

export const SceneChrome: React.FC<{chapter:string; index:number; total?:number; children:ReactNode}> = ({chapter,index,total=6,children}) => {
  const frame=useCurrentFrame();
  const {durationInFrames}=useVideoConfig();
  return <Background>
    <div style={{position:'absolute',top:54,left:88,right:88,display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:22,fontWeight:700,letterSpacing:3.2,color:palette.muted}}>
      <div style={{display:'flex',alignItems:'center',gap:14}}><div style={{width:12,height:12,borderRadius:999,backgroundColor:palette.mint,boxShadow:'0 0 26px rgba(154,255,189,0.8)'}}/>FLOWCASE / AI COMMERCE</div>
      <div>{String(index).padStart(2,'0')} / {String(total).padStart(2,'0')} · <span style={{color:palette.text}}>{chapter}</span></div>
    </div>
    {children}
    <div style={{position:'absolute',left:88,right:88,bottom:52,height:4,backgroundColor:'rgba(255,255,255,0.08)',overflow:'hidden',borderRadius:99}}><div style={{height:'100%',width:`${interpolate(frame,[0,durationInFrames-1],[4,100],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.linear})}%`,background:`linear-gradient(90deg, ${palette.mint}, ${palette.cyan})`,borderRadius:99}}/></div>
  </Background>;
};

export const GlassPanel: React.FC<{children:ReactNode; style?:CSSProperties; accent?:'mint'|'cyan'|'warm'}> = ({children,style,accent='mint'}) => {
  const accents={mint:'rgba(154,255,189,0.26)',cyan:'rgba(101,233,255,0.25)',warm:'rgba(255,187,141,0.24)'};
  return <div style={{background:palette.panel,border:`1px solid ${accents[accent]}`,borderRadius:28,boxShadow:'0 28px 90px rgba(0,0,0,0.24)',backdropFilter:'blur(22px)',...style}}>{children}</div>;
};

export const Pill: React.FC<{children:ReactNode; tone?:'mint'|'cyan'|'warm'|'muted'}> = ({children,tone='mint'}) => {
  const tones={mint:{background:'rgba(154,255,189,0.12)',color:palette.mint},cyan:{background:'rgba(101,233,255,0.12)',color:palette.cyan},warm:{background:'rgba(255,187,141,0.12)',color:palette.warm},muted:{background:'rgba(255,255,255,0.07)',color:palette.muted}};
  return <div style={{display:'inline-flex',alignItems:'center',gap:10,padding:'10px 16px',borderRadius:999,fontWeight:800,fontSize:22,letterSpacing:1.2,...tones[tone]}}>{children}</div>;
};

export const Reveal: React.FC<{children:ReactNode; delay?:number; distance?:number; style?:CSSProperties}> = ({children,delay=0,distance=34,style}) => {
  const frame=useCurrentFrame();
  return <div style={{opacity:interpolate(frame,[delay,delay+18],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)}),translate:`0px ${interpolate(frame,[delay,delay+22],[distance,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)})}px`,...style}}>{children}</div>;
};

export const Dot: React.FC<{tone?:'mint'|'cyan'|'warm';size?:number}> = ({tone='mint',size=10}) => <span style={{width:size,height:size,borderRadius:999,display:'inline-block',backgroundColor:tone==='mint'?palette.mint:tone==='cyan'?palette.cyan:palette.warm,boxShadow:tone==='mint'?'0 0 16px rgba(154,255,189,0.8)':tone==='cyan'?'0 0 16px rgba(101,233,255,0.8)':'0 0 16px rgba(255,187,141,0.8)'}}/>;
