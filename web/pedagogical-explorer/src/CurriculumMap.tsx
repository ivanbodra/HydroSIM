import { motion } from 'motion/react';
import { ArrowRight, Check, FlaskConical, GraduationCap, Layers3, LockKeyhole, Radar } from 'lucide-react';
import { useMemo, useState } from 'react';
import { pedagogicalTracks, type Experience, type TrackKey } from './pedagogical-plan';

type Family='acoustics'|'propagation'|'arrays'|'platform'|'integration';
const trackIcon:Record<TrackKey,typeof GraduationCap>={didactic:GraduationCap,patch:FlaskConical,acquisition:Radar};
const productionRoutes:Record<string,string>={D1:'#wave-lab',D2:'#signal-lab/pulse',D3:'#sonar-equation-lab',D4:'#refraction-lab',D6:'#array-directivity-lab',D7:'#beamforming-lab',D8:'#echosounder-lab',D9:'#bottom-detection-lab',D10:'#multisector-lab',D11:'#vessel-configuration-lab',D12:'#vessel-motion-lab',D14:'#timing-lab',D15:'#sounding-formation-lab',D17:'#tradeoff-lab',D18:'#uncertainty-lab'};
const displayId:Record<string,string>={D1:'D1',D2:'D2',D3:'D3',D4:'D4',D6:'D5',D7:'D6',D8:'D7',D9:'D8',D10:'D9',D11:'D10',D12:'D11',D13:'D12',D14:'D13',D15:'D14',D16:'D15',D17:'D16',D18:'D17'};
const familyById:Record<string,Family>={D1:'acoustics',D2:'acoustics',D3:'propagation',D4:'propagation',D6:'arrays',D7:'arrays',D8:'arrays',D9:'arrays',D10:'arrays',D11:'platform',D12:'platform',D13:'platform',D14:'platform',D15:'platform',D16:'integration',D17:'integration',D18:'integration'};
const familyMeta:Record<Family,{title:string;kicker:string}>={
 acoustics:{title:'Acoustic Signal',kicker:'WAVE → PULSE'},
 propagation:{title:'Propagation',kicker:'LOSS → REFRACTION'},
 arrays:{title:'Sonar & Beam Formation',kicker:'ARRAY → BEAM → DETECTION'},
 platform:{title:'Platform & Integration',kicker:'VESSEL → MOTION → SOUNDING'},
 integration:{title:'Survey Design & Quality',kicker:'PLAN → COVERAGE → UNCERTAINTY'},
};
const didacticFamilies:Family[]=['acoustics','propagation','arrays','platform','integration'];
const visibleDidactic=(experiences:Experience[])=>experiences.filter(e=>e.id!=='D5');

function SurveyVessel(){return <div className="map2-vessel-scene"><motion.div className="map2-vessel" animate={{y:[0,-4,0],rotate:[0,.35,0]}} transition={{duration:5,repeat:Infinity,ease:'easeInOut'}}><svg viewBox="0 0 280 120" role="presentation"><path className="vessel-hull" d="M28 72h225l-24 27H61L28 72Z"/><path className="vessel-deck" d="M83 72V48h91l22 24H83Z"/><path className="vessel-bridge" d="M118 48V28h48l15 20h-63Z"/><path className="vessel-window" d="M128 34h15v9h-15zm21 0h13l7 9h-20z"/><path className="vessel-mast" d="M143 28V10m-12 9h24M143 10l8 9h-16l8-9Z"/><path className="vessel-rail" d="M71 66h135M93 57h-18m136 9h18"/><circle className="vessel-sensor" cx="143" cy="8" r="3"/></svg></motion.div><div className="map2-waterline"/><motion.div className="map2-sonar-beam" animate={{opacity:[.42,.78,.42],scaleX:[.94,1.04,.94]}} transition={{duration:3.4,repeat:Infinity,ease:'easeInOut'}}/><div className="map2-seafloor"><span/><span/><span/><span/><span/><span/></div></div>}

export default function CurriculumMap({onOpenLegacy:_onOpenLegacy}:{onOpenLegacy:()=>void}){
 const[track,setTrack]=useState<TrackKey>('didactic');
 const current=useMemo(()=>pedagogicalTracks.find(item=>item.key===track)!,[track]);
 const experiences=track==='didactic'?visibleDidactic(current.experiences):current.experiences;
 const available=experiences.filter(e=>productionRoutes[e.id]).length;
 const open=(e:Experience)=>{const route=productionRoutes[e.id];if(route)location.hash=route};
 return <div className={`curriculum-map-v2 track-${track}`}>
  <header className="map2-topbar"><div className="map2-brand"><span className="map2-mark" aria-hidden="true">H</span><div><strong>HydroSIM</strong><small>Pedagogical Explorer</small></div></div><div className="map2-actions" aria-label="HydroSIM learning map"><span>{available} available</span></div></header>
  <main className="map2-main">
   <section className="map2-hero"><div className="map2-hero-copy"><span>LEARNING MAP · HYDROGRAPHIC ACQUISITION</span><h1>See where you are.<br/><em>Choose what to explore next.</em></h1><p>Lessons follow the acquisition chain from acoustic signal to survey quality. Colors mark related stages of that sequence.</p><div className="map2-status"><div><strong>{available}</strong><span>available lessons</span></div><i/><div><strong>{experiences.length}</strong><span>{track==='didactic'?'didactic lessons':'experiences in this module'}</span></div></div></div><div className="map2-orbit" aria-hidden="true"><SurveyVessel/><div className="orbit-ring ring-a"/><div className="orbit-ring ring-b"/></div></section>
   <nav className="map2-track-switcher" aria-label="HydroSIM modules">{pedagogicalTracks.map(item=>{const Icon=trackIcon[item.key];const active=track===item.key;return <button key={item.key} type="button" aria-pressed={active} className={active?'active':''} onClick={()=>setTrack(item.key)}><Icon size={19}/><div><small>{item.key==='didactic'?'01':item.key==='patch'?'02':'03'}</small><strong>{item.title}</strong><span>{item.subtitle}</span></div><ArrowRight size={15}/></button>})}</nav>
   {track==='didactic'?<section className="map2-journey"><header><div><span>DIDACTIC EXPLORER</span><h2>Didactic lessons</h2></div><div className="map2-key" aria-label="Lesson availability legend"><span><i className="available-dot"/>Available now</span><span><i className="planned-dot"/>Planned</span></div></header><div className="family-stack">{didacticFamilies.map(family=>{const lessons=experiences.filter(e=>familyById[e.id]===family);if(!lessons.length)return null;const meta=familyMeta[family];return <section key={family} className={`family-lane family-${family}`}><div className="family-label"><small>{meta.kicker}</small><strong>{meta.title}</strong><span>{lessons.length} {lessons.length===1?'lesson':'lessons'}</span></div><div className="family-path">{lessons.map((e,index)=>{const ready=Boolean(productionRoutes[e.id]);return <motion.button key={e.id} type="button" aria-disabled={!ready} className={`lesson-node ${ready?'ready':'planned'}`} onClick={()=>ready&&open(e)} whileHover={ready?{y:-3}:undefined}><div className="lesson-node-head"><span>{displayId[e.id]}</span>{ready?<i className="ready-badge"><Check size={11}/>LIVE</i>:<i className="planned-badge"><LockKeyhole size={10}/>PLANNED</i>}</div><strong>{e.title}</strong><small>{e.outputs[0]}</small>{ready&&<div className="lesson-open">OPEN LESSON <ArrowRight size={12}/></div>}{index<lessons.length-1&&<span className="node-connector" aria-hidden="true"/>}</motion.button>})}</div></section>})}</div></section>:<section className="map2-chapter"><div className="chapter-intro"><span>{track==='patch'?'CALIBRATION WORKSPACE':'SURVEY WORKSPACE'}</span><h2>{current.title}</h2><p>{current.subtitle}</p><div className="chapter-state"><Layers3 size={17}/><span>Structure defined · dedicated experiences will appear here as they become available.</span></div></div><div className="chapter-grid">{current.experiences.map((e,index)=><motion.article key={e.id} whileHover={{y:-2}}><div><span>{String(index+1).padStart(2,'0')}</span><strong>{e.id}</strong></div><h3>{e.title}</h3><p>{e.designCue}</p><small>PLANNED EXPERIENCE</small></motion.article>)}</div></section>}
  </main>
 </div>
}
