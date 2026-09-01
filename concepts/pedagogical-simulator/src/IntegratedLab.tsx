import { motion } from 'motion/react';
import { Activity, GitCompare, Layers3, Navigation, Pause, Play, Ship, Sparkles, Target } from 'lucide-react';
import { useState } from 'react';

export default function IntegratedLab({ onBack }: { onBack: () => void }) {
  const [playing, setPlaying] = useState(true);
  const [active, setActive] = useState<'signal'|'beam'|'propagation'|'motion'>('motion');
  const [compare, setCompare] = useState(true);
  const tabs = [
    ['signal','Signal',Activity],['beam','Beam',Target],['propagation','Propagation',Layers3],['motion','Motion',Navigation],
  ] as const;
  return <div className="phenomenon-lab integrated-lab">
    <div className="lab-toolbar"><button className="back-button" onClick={onBack}>← System map</button><div className="lab-breadcrumb"><Sparkles size={17}/><span>Integrated Lab</span><b>/</b><strong>Virtual hydrographic survey</strong></div><div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> integrated concept</span><button onClick={()=>setPlaying(v=>!v)}>{playing?<Pause size={16}/>:<Play size={16}/>} {playing?'Pause':'Run'}</button><button onClick={()=>setCompare(v=>!v)}><GitCompare size={16}/> {compare?'Hide':'Show'} baseline</button></div></div>
    <div className="lab-question integrated-question"><span>06 · INTEGRATED LAB</span><h1>One virtual vessel. One survey. Every phenomenon stays connected.</h1><p>The learner stops switching between lessons and starts running an experiment: vessel, signal, beam, water column, motion and resulting soundings coexist in one navigable scene.</p></div>
    <div className="integrated-layout"><aside className="phenomena-rail"><small>PHENOMENA</small>{tabs.map(([key,label,Icon])=><button key={key} className={active===key?'active':''} onClick={()=>setActive(key)}><Icon size={19}/><span>{label}</span></button>)}<div className="rail-spacer"/><button className="scenario-button"><Sparkles size={18}/><span>Scenario</span></button></aside>
      <section className={`integrated-stage focus-${active}`}><div className="integrated-top"><div><small>LIVE SURVEY SCENE</small><strong>Cause and effect remain spatially linked</strong></div><div className="survey-chip"><span className={playing?'live':''}/>{playing?'RUNNING':'PAUSED'}</div></div><div className="integrated-scene">
        <div className="survey-surface"/><motion.div className="survey-vessel" animate={playing?{x:[-8,8,-8],y:[0,-4,0],rotate:[-1,1,-1]}:{}} transition={{duration:5,repeat:Infinity,ease:'easeInOut'}}><Ship size={64}/><span>survey vessel</span></motion.div>{compare&&<div className="survey-vessel ghost"><Ship size={64}/><span>baseline</span></div>}
        <div className="survey-beam"><i/><i/><i/><i/><i/><i/><i/></div><svg className="survey-rays" viewBox="0 0 1000 540" preserveAspectRatio="none">{[-3,-2,-1,0,1,2,3].map((r,i)=><motion.path key={r} d={`M 505 120 Q ${500+r*34} 300 ${500+r*92} 455`} className={i===3?'main':'secondary'} fill="none" animate={playing?{opacity:[.28,.85,.28]}:{opacity:.58}} transition={{duration:2+i*.12,repeat:playing?Infinity:0}}/>)}</svg>
        <div className="survey-bottom"/><div className="sounding-cloud">{Array.from({length:38}).map((_,i)=><motion.i key={i} style={{left:`${13+i*2}%`,bottom:`${9+(i%5)*1.3}%`}} animate={active==='motion'&&playing?{y:[0,-3,0]}:{}} transition={{duration:1.6+(i%4)*.2,repeat:Infinity}}/>)}</div>
        <div className="cause-lens"><small>FOCUS LENS</small><strong>{active[0].toUpperCase()+active.slice(1)}</strong><span>{active==='signal'?'Pulse behavior highlighted from source to return.':active==='beam'?'Beam fan and illuminated seabed become the visual priority.':active==='propagation'?'Water-column paths and their shape become the visual priority.':'Platform movement, ghost state and sounding consequence become the visual priority.'}</span></div>
        <div className="timeline"><span className="active">TRANSMIT</span><i/><span>PROPAGATE</span><i/><span>INTERACT</span><i/><span>RECEIVE</span><i/><span>RECONSTRUCT</span></div>
      </div><div className="integrated-inspector"><div><small>CURRENT VARIABLE</small><strong>{active==='signal'?'Waveform / pulse':active==='beam'?'Beam geometry':active==='propagation'?'Water-column path':'Platform attitude'}</strong></div><div><small>DOWNSTREAM</small><strong>Scene reacts continuously</strong></div><div><small>COMPARE</small><strong>{compare?'Baseline visible':'Current only'}</strong></div><div><small>NEXT</small><strong>Save as experiment preset</strong></div></div></section>
    </div>
  </div>;
}
