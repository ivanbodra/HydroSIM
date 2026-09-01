import { motion, type PanInfo } from 'motion/react';
import { GitCompare, Hand, Pause, Play, RotateCcw, SlidersHorizontal, Sparkles, Target } from 'lucide-react';
import { useMemo, useState } from 'react';

export default function BeamLab({ onBack }: { onBack: () => void }) {
  const [steering, setSteering] = useState(18);
  const [beamwidth, setBeamwidth] = useState(34);
  const [sidelobes, setSidelobes] = useState(28);
  const [playing, setPlaying] = useState(true);
  const [dragging, setDragging] = useState(false);
  const footprint = useMemo(() => Math.max(80, 220 + beamwidth * 5), [beamwidth]);
  const beamRotate = steering * 0.7;
  const steerByDrag = (_: PointerEvent, info: PanInfo) => setSteering(Math.max(-45, Math.min(45, Math.round(info.offset.x / 5))));

  return <div className="beam-lab">
    <div className="lab-toolbar"><button className="back-button" onClick={onBack}>← System map</button><div className="lab-breadcrumb"><Target size={17}/><span>Beam</span><b>/</b><strong>Directivity laboratory</strong></div><div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> illustrative</span><button onClick={()=>setPlaying(v=>!v)}>{playing?<Pause size={16}/>:<Play size={16}/>} {playing?'Pause':'Play'}</button><button><GitCompare size={16}/> Compare</button></div></div>
    <div className="lab-question"><span>02 · BEAM</span><h1>Shape the beam where the phenomenon happens.</h1><p>Drag the beam handle to explore steering. Pull the beam edges to open or close the visual spread; explicit controls remain available as a secondary language.</p></div>
    <div className="beam-layout"><aside className="control-surface beam-controls"><div className="control-title"><SlidersHorizontal size={17}/><strong>Beam controls</strong></div><label>Steering <output>{steering}°</output><input type="range" min="-45" max="45" value={steering} onChange={e=>setSteering(+e.target.value)}/></label><label>Beamwidth <output>{beamwidth}%</output><input type="range" min="10" max="70" value={beamwidth} onChange={e=>setBeamwidth(+e.target.value)}/></label><label>Sidelobe emphasis <output>{sidelobes}%</output><input type="range" min="0" max="70" value={sidelobes} onChange={e=>setSidelobes(+e.target.value)}/></label><div className="control-readouts"><div><small>Mode</small><strong>Steered</strong></div><div><small>Gesture</small><strong>{dragging?'Direct':'Ready'}</strong></div><div><small>Footprint</small><strong>{Math.round(footprint/10)} rel.</strong></div><div><small>State</small><strong>{playing?'Live':'Frozen'}</strong></div></div><button className="reset" onClick={()=>{setSteering(18);setBeamwidth(34);setSidelobes(28)}}><RotateCcw size={15}/> Reset concept</button></aside>
      <section className="beam-stage"><div className="beam-stage-head"><div><small>DIRECT GEOMETRY</small><strong>Touch the beam, not just the controls</strong></div><span>INPUT → RESPONSE</span></div><div className="beam-scene">
          <div className="beam-gesture-hint"><Hand size={14}/> drag handle to steer · drag edge to reshape</div><div className="water-surface"/><div className="transducer-node"><Target size={22}/><span>array</span></div>
          <motion.div className="beam-volume" animate={{rotate:beamRotate, opacity:playing?[.68,.94,.68]:.86}} transition={playing?{opacity:{duration:2.6,repeat:Infinity,ease:'easeInOut'},rotate:{type:'spring',stiffness:120,damping:18}}:{rotate:{type:'spring',stiffness:120,damping:18}}} style={{'--beam-spread':`${beamwidth}%`} as React.CSSProperties}><div className="main-lobe"/><div className="side-lobe left" style={{opacity:sidelobes/100}}/><div className="side-lobe right" style={{opacity:sidelobes/100}}/><motion.button aria-label="Steer beam" className="beam-drag-handle" drag="x" dragMomentum={false} dragElastic={0} onDragStart={()=>setDragging(true)} onDrag={steerByDrag} onDragEnd={()=>setDragging(false)}><Target size={16}/></motion.button><button className="beam-edge-handle left" onPointerDown={()=>setBeamwidth(v=>Math.max(10,v-6))}/><button className="beam-edge-handle right" onPointerDown={()=>setBeamwidth(v=>Math.min(70,v+6))}/></motion.div>
          <div className="depth-guide"><span>water column</span></div><div className="seabed-plane"/><motion.div className="footprint-glow" animate={{width:footprint, x:steering*4}} transition={{type:'spring',stiffness:130,damping:20}}/><div className="reference-axis"><i/><span>nadir reference</span></div>
        </div><div className="beam-bottom-strip"><div><small>TOUCH</small><strong>Grab the beam</strong><span>The geometry itself becomes the primary control surface.</span></div><div><small>SHAPE</small><strong>Open or close</strong><span>Edge handles suggest direct beamwidth manipulation.</span></div><div><small>NOTICE</small><strong>Follow the response</strong><span>Footprint and scene react without leaving the phenomenon.</span></div></div></section></div>
  </div>;
}
