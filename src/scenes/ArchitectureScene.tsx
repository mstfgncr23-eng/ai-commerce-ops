import {Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {Dot, GlassPanel, Pill, Reveal, SceneChrome, colors} from '../components/Background';

const NodeCard: React.FC<{
  x: number;
  y: number;
  width: number;
  label: string;
  detail: string;
  badge: string;
  tone?: 'mint' | 'cyan' | 'warm';
  delay: number;
}> = ({x, y, width, label, detail, badge, tone = 'mint', delay}) => (
  <Reveal delay={delay} style={{position: 'absolute', left: x, top: y, width}}>
    <GlassPanel accent={tone} style={{padding: '25px 26px', minHeight: 142, display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}><Pill tone={tone}>{badge}</Pill><Dot tone={tone} size={12} /></div>
      <div style={{marginTop: 20}}><div style={{fontSize: 31, fontWeight: 900, letterSpacing: -0.8}}>{label}</div><div style={{fontSize: 21, color: colors.muted, marginTop: 7}}>{detail}</div></div>
    </GlassPanel>
  </Reveal>
);

export const ArchitectureScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <SceneChrome chapter="MİMARİ" index={3}>
      <div style={{position: 'absolute', left: 88, right: 88, top: 134}}><Reveal delay={3}><Pill>N8N × LANGCHAIN</Pill></Reveal><Interactive.Div name="Mimari başlığı" style={{fontSize:88,fontWeight:900,lineHeight:1,letterSpacing:-4,marginTop:20,opacity:interpolate(frame,[8,28],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)}),translate:`0px ${interpolate(frame,[8,30],[36,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(0.16,1,0.3,1)})}px`}}>Tek akış. Net sorumluluklar.</Interactive.Div></div>
      <div style={{position: 'absolute', left: 88, top: 330, width: 1744, height: 610}}>
        <svg width="1744" height="610" viewBox="0 0 1744 610" style={{position:'absolute',inset:0,overflow:'visible'}}><defs><linearGradient id="flow" x1="0" x2="1"><stop offset="0" stopColor={colors.mint} stopOpacity="0.65"/><stop offset="1" stopColor={colors.cyan} stopOpacity="0.75"/></linearGradient></defs><path d="M 296 248 L 412 248" fill="none" stroke="url(#flow)" strokeWidth="4" strokeDasharray="12 14" strokeDashoffset={-frame*3}/><path d="M 750 248 L 866 248" fill="none" stroke="url(#flow)" strokeWidth="4" strokeDasharray="12 14" strokeDashoffset={-frame*3}/><path d="M 1238 248 C 1320 248, 1290 82, 1398 82" fill="none" stroke="url(#flow)" strokeWidth="4" strokeDasharray="12 14" strokeDashoffset={-frame*3}/><path d="M 1238 248 L 1398 248" fill="none" stroke="url(#flow)" strokeWidth="4" strokeDasharray="12 14" strokeDashoffset={-frame*3}/><path d="M 1238 248 C 1320 248, 1290 414, 1398 414" fill="none" stroke="url(#flow)" strokeWidth="4" strokeDasharray="12 14" strokeDashoffset={-frame*3}/></svg>
        <NodeCard x={0} y={176} width={296} label="Ürün formu" detail="Webhook + dosya" badge="TRIGGER" delay={24}/><NodeCard x={412} y={157} width={338} label="n8n orkestrasyonu" detail="Doğrula · yönlendir · retry" badge="WORKFLOW" delay={54}/><NodeCard x={866} y={148} width={372} label="LangChain agent" detail="Sınıflandır · zenginleştir · karar ver" badge="AI LAYER" tone="cyan" delay={84}/><NodeCard x={1398} y={0} width={346} label="Shopify API" detail="Taslak ürün kaydı" badge="COMMERCE" delay={120}/><NodeCard x={1398} y={166} width={346} label="PostgreSQL" detail="Durum + audit log" badge="DATA" tone="cyan" delay={132}/><NodeCard x={1398} y={332} width={346} label="İnsan onayı" detail="Slack / e-posta" badge="HITL" tone="warm" delay={144}/>
        <Reveal delay={178} style={{position:'absolute',left:412,top:510,right:0,display:'flex',gap:18}}>{['Idempotency key','3× retry','Structured output','Audit trail'].map((item,index)=><div key={item} style={{padding:'13px 20px',borderRadius:999,border:'1px solid rgba(255,255,255,0.12)',backgroundColor:'rgba(255,255,255,0.05)',color:index===3?colors.cyan:colors.muted,fontSize:22,fontWeight:800}}>{item}</div>)}</Reveal>
      </div>
    </SceneChrome>
  );
};
