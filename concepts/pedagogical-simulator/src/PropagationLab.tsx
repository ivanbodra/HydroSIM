import { motion } from 'motion/react';
import { GitCompare, Layers3, Pause, Play, RotateCcw, SlidersHorizontal, Sparkles, Waves } from 'lucide-react';
import { useMemo, useState } from 'react';

export default function PropagationLab({ onBack }: { onBack: () => void }) {
  const [gradient, setGradient] = useState(56);
  const [range, setRange] = useState(68);
  const [frequency, setFrequency] = useState(44);
  const [playing, setPlaying] = useState(true);
  const bend = useMemo(() => (gradient - 50) * 2.2, [gradient]);
  const rays = [-2,-1,0,1,2];
  return <div className="phenomenon-lab propagation-lab">
    <div className="lab-toolbar"><button className="back-button" onClick={onBack}>← System map</button><div className="lab-breadcrumb"><Layers3 size={17}/><span>Propagation</span><b>/</b><strong>Water-column laboratory</strong></div><div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> illustrative</span><button onClick={()=>setPlaying(v=>!v)}>{playing?<Pause size={16}/>:<Play size={16}/>} {playing?'Pause':'Play'}</button><button><GitCompare size={16}/> Compare</button></div></div>
    <div className="lab-question"><span>03 · PROPAGATION</span><h1>Watch the acoustic path change inside the water column.</h1><p>Shape the environment and follow the same emission through layers, refraction, loss and seabed interaction.</p></div>
    <div className="phenomenon-layout">
      <aside className="control-surface"><div className="control-title"><SlidersHorizontal size={17}/><strong>Environment controls</strong></div><label>Profile curvature <output>{gradient}%</output><input type="range" min="15" max="85" value={gradient} onChange={e=>setGradient(+e.target.value)}/></label><label>Range <output>{range}%</output><input type="range" min="25" max="100" value={range} onChange={e=>setRange(+e.target.value)}/></label><label>Frequency emphasis <output>{frequency}%</output><input type="range" min="10" max="90" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label><div className="control-readouts"><div><small>Scene</small><strong>Layered water</strong></div><div><small>Path</small><strong>{bend>0?'Down-curved':'Up-curved'}</strong></div><div><small>Range</small><strong>{range} rel.</strong></div><div><small>Loss</small><strong>{frequency>55?'High':'Moderate'}</strong></div></div><button className="reset" onClick={()=>{setGradient(56);setRange(68);setFrequency(44)}}><RotateCcw size={15}/> Reset concept</button></aside>
      <section className="phenomenon-stage propagation-stage"><div className="stage-kicker"><div><small>CONTINUOUS SCENE</small><strong>Source → water column → seabed → return</strong></div><span>FOLLOW THE PATH</span></div><div className="prop-scene">
        <div className="prop-surface"/><div className="source-pod"><Waves size={20}/><span>source</span></div>
        {[0,1,2,3].map(i=><div key={i} className="water-layer" style={{top:`${18+i*17}%`,opacity:.16+i*.04}}><span>layer {i+1}</span></div>)}
        <svg className="ray-field" viewBox="0 0 1000 520" preserveAspectRatio="none">{rays.map((r,i)=>{const start=500+r*18;const end=500+r*80+(range-60)*3;const control=500+r*50+bend;return <motion.path key={r} d={`M ${start} 72 Q ${control} 260 ${end} 455`} fill="none" strokeWidth={i===2?4:2} className={i===2?'ray-primary':'ray-secondary'} animate={playing?{pathLength:[0,1],opacity:[.35,.9,.35]}:{pathLength:1,opacity:.75}} transition={{duration:2.2+i*.2,repeat:playing?Infinity:0,ease:'easeInOut'}}/>})}</svg>
        <div className="prop-seabed"/><div className="return-halo" style={{left:`${50+(range-60)*.28}%`}}/><div className="loss-meter"><small>ILLUSTRATIVE ENERGY</small><div><i style={{width:`${Math.max(18,100-frequency*.72)}%`}}/></div><span>source</span><span>return</span></div>
        <div className="profile-ribbon"><small>PROFILE LENS</small><svg viewBox="0 0 100 260" preserveAspectRatio="none"><path d={`M20 10 Q ${25+gradient*.65} 130 25 250`} fill="none"/></svg><strong>drag the profile →</strong></div>
      </div><div className="causal-strip"><div><small>1 · SHAPE</small><strong>Change the column</strong><span>Make environmental structure visible before discussing equations.</span></div><div><small>2 · FOLLOW</small><strong>Trace the path</strong><span>The same emission bends through the scene as one continuous event.</span></div><div><small>3 · NOTICE</small><strong>See what reaches bottom</strong><span>Return strength and arrival region react visually.</span></div></div></section>
    </div>
  </div>;
}
