import { motion } from 'motion/react';
import { Compass, GitCompare, Rotate3D, RotateCcw, SlidersHorizontal, Sparkles, Waves } from 'lucide-react';
import { useState } from 'react';

export default function MotionLab({ onBack }: { onBack: () => void }) {
  const [roll, setRoll] = useState(8);
  const [pitch, setPitch] = useState(-4);
  const [yaw, setYaw] = useState(12);
  const [heave, setHeave] = useState(18);
  return <div className="phenomenon-lab motion-lab">
    <div className="lab-toolbar"><button className="back-button" onClick={onBack}>← System map</button><div className="lab-breadcrumb"><Rotate3D size={17}/><span>Motion</span><b>/</b><strong>Platform motion laboratory</strong></div><div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> exaggerated</span><button><GitCompare size={16}/> Baseline × Current</button></div></div>
    <div className="lab-question"><span>05 · MOTION</span><h1>Move the vessel and watch the whole measurement geometry react.</h1><p>Roll, pitch, yaw and heave are direct visual gestures rather than abstract numbers. A ghost vessel preserves the baseline for immediate comparison.</p></div>
    <div className="phenomenon-layout">
      <aside className="control-surface"><div className="control-title"><SlidersHorizontal size={17}/><strong>Motion controls</strong></div><label>Roll <output>{roll}°</output><input type="range" min="-20" max="20" value={roll} onChange={e=>setRoll(+e.target.value)}/></label><label>Pitch <output>{pitch}°</output><input type="range" min="-15" max="15" value={pitch} onChange={e=>setPitch(+e.target.value)}/></label><label>Yaw <output>{yaw}°</output><input type="range" min="-30" max="30" value={yaw} onChange={e=>setYaw(+e.target.value)}/></label><label>Heave <output>{heave} rel.</output><input type="range" min="-35" max="35" value={heave} onChange={e=>setHeave(+e.target.value)}/></label><button className="reset" onClick={()=>{setRoll(0);setPitch(0);setYaw(0);setHeave(0)}}><RotateCcw size={15}/> Zero motion</button></aside>
      <section className="phenomenon-stage motion-stage"><div className="stage-kicker"><div><small>DIRECT MANIPULATION</small><strong>Baseline ghost + current platform</strong></div><span>MOVE → SEE CONSEQUENCE</span></div><div className="motion-scene">
        <div className="horizon-line"/><div className="ghost-vessel"><div className="motion-hull"/><span>baseline</span></div><motion.div className="current-vessel" animate={{rotate:roll,y:heave,x:yaw*.8,skewX:pitch*.35}} transition={{type:'spring',stiffness:90,damping:16}}><div className="motion-hull"/><div className="motion-bridge"/><div className="motion-axis roll"><Rotate3D size={18}/><span>roll</span></div><div className="motion-axis yaw"><Compass size={18}/><span>yaw</span></div><div className="motion-beam"><i/><i/><i/><i/><i/></div></motion.div>
        <div className="motion-seabed"><span/><span/><span/><span/><span/><span/></div><div className="sounding-trail">{Array.from({length:18}).map((_,i)=><motion.i key={i} animate={{x:roll*(i-9)*.28+yaw*.5,y:Math.abs(pitch)*(i%3)*.7}} transition={{type:'spring',stiffness:80,damping:18}}/> )}</div><div className="heave-ruler"><Waves size={16}/><span>heave</span><b style={{transform:`translateY(${heave}px)`}}/></div><div className="motion-readout"><small>VISUAL AMPLIFICATION</small><strong>Motion is exaggerated for learning</strong><span>Baseline remains visible so direction and consequence can be read without memorizing conventions.</span></div>
      </div><div className="causal-strip"><div><small>1 · MOVE</small><strong>Manipulate the platform</strong><span>Use sliders now; direct drag/rotation is the intended interaction language.</span></div><div><small>2 · COMPARE</small><strong>Keep the ghost state</strong><span>The neutral vessel never disappears.</span></div><div><small>3 · FOLLOW</small><strong>Watch beam and soundings</strong><span>Downstream visual elements react in the same scene.</span></div></div></section>
    </div>
  </div>;
}
