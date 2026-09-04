import { motion } from 'motion/react';
import { ArrowRight, Eye, FlaskConical, GraduationCap, Radar, Route, Sparkles } from 'lucide-react';
import { useMemo, useState } from 'react';
import { pedagogicalTracks, type Experience, type TrackKey } from './pedagogical-plan';

const trackIcon: Record<TrackKey, typeof GraduationCap> = { didactic: GraduationCap, patch: FlaskConical, acquisition: Radar };

export default function CurriculumMap({ onOpenLegacy }: { onOpenLegacy: () => void }) {
  const [track, setTrack] = useState<TrackKey>('didactic');
  const [selected, setSelected] = useState<Experience>(pedagogicalTracks[0].experiences[0]);
  const current = useMemo(() => pedagogicalTracks.find((item) => item.key === track)!, [track]);
  const chooseTrack = (key: TrackKey) => { setTrack(key); setSelected(pedagogicalTracks.find((item) => item.key === key)!.experiences[0]); };
  const productionRoute = (experience: Experience) => {
    if (experience.id === 'D1') return '#wave-lab';
    if (experience.id === 'D2') return '#signal-lab/pulse';
    if (experience.id === 'D3') return '#sonar-equation-lab';
    if (experience.id === 'D4') return '#refraction-lab';
    if (experience.id === 'D6') return '#array-directivity-lab';
    if (experience.id === 'D7') return '#beamforming-lab';
    if (experience.id === 'D8') return '#echosounder-lab';
    if (experience.id === 'D9') return '#bottom-detection-lab';
    if (experience.id === 'D12') return '#vessel-motion-lab';
    return experience.route;
  };
  const open = (experience: Experience) => { setSelected(experience); const route = productionRoute(experience); if (route) window.location.hash = route; };
  return <div className={`curriculum-map track-${track}`}>
    <header className="curriculum-head"><div><span>HYDROSIM · PEDAGOGICAL CONCEPT MAP</span><h1>Learn through the acquisition chain.</h1><p>The canonical pedagogical plan drives the learner structure while production experiences connect their visible scientific outputs to the Python Scientific Core.</p></div><button onClick={onOpenLegacy}><Eye size={16}/> Original visual labs</button></header>
    <nav className="track-switcher">{pedagogicalTracks.map((item)=>{const Icon=trackIcon[item.key];return <button key={item.key} className={track===item.key?'active':''} onClick={()=>chooseTrack(item.key)}><Icon size={20}/><span><strong>{item.title}</strong><small>{item.experiences.length} experiences · {item.subtitle}</small></span></button>})}</nav>
    <div className="curriculum-workspace"><section className="experience-list"><div className="track-title"><span>{current.key.toUpperCase()}</span><strong>{current.title}</strong><small>{current.subtitle}</small></div><div className="experience-grid">{current.experiences.map((experience)=><motion.button key={experience.id} className={selected.id===experience.id?'selected':''} onClick={()=>setSelected(experience)} whileHover={{y:-2}}><span>{experience.id}</span><strong>{experience.title}</strong><small>{experience.outputs[0]}</small><ArrowRight size={14}/></motion.button>)}</div></section>
      <aside className="experience-inspector"><div className="experience-id"><span>{selected.id}</span><Sparkles size={16}/></div><h2>{selected.title}</h2><p className="design-cue">{selected.designCue}</p><div className="io-flow"><div><small>INPUTS</small><div className="io-pills">{selected.inputs.map((input)=><span key={input}>{input}</span>)}</div></div><Route size={20}/><div><small>LEARNING OUTPUTS / VISUALIZATIONS</small><div className="io-pills output">{selected.outputs.map((output)=><span key={output}>{output}</span>)}</div></div></div><div className="concept-loop"><small>CONCEPTUAL INTERACTION LOOP</small><div><span>INPUT</span><i>→</i><strong>MANIPULATE</strong><i>→</i><span>SEE CONSEQUENCE</span></div></div>{productionRoute(selected)?<button className="launch-experience" onClick={()=>open(selected)}><FlaskConical size={16}/> Open current visual foundation</button>:<button className="launch-experience future" disabled><FlaskConical size={16}/> Dedicated concept workspace next</button>}<p className="scope-note">Production scientific values are authoritative only where an experience is connected to a canonical Python API; unfinished visual foundations remain conceptual.</p></aside>
    </div>
  </div>;
}
