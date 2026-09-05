import { motion } from 'motion/react';
import { ArrowRight, Check, FlaskConical, GraduationCap, Layers3, LockKeyhole, Radar } from 'lucide-react';
import { useMemo, useState } from 'react';
import { pedagogicalTracks, type Experience, type TrackKey } from './pedagogical-plan';
import './map-vessel-refinement.css';

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

function SurveyVessel(){
 return <div className="map2-vessel-scene map2-vessel-refined">
  <motion.div className="map2-vessel map2-vessel-platform" animate={{y:[0,-3,0],rotate:[-.28,.28,-.28]}} transition={{duration:6.2,repeat:Infinity,ease:'easeInOut'}}>
   <svg viewBox="0 0 340 190" role="presentation">
    <defs>
     <linearGradient id="mapHull" x1="0" x2="1"><stop offset="0" stopColor="#173645"/><stop offset=".52" stopColor="#244d5e"/><stop offset="1" stopColor="#102b38"/></linearGradient>
     <linearGradient id="mapDeck" x1="0" x2="1"><stop offset="0" stopColor="#d8e7ec" stopOpacity=".76"/><stop offset="1" stopColor="#7da4b2" stopOpacity=".42"/></linearGradient>
     <linearGradient id="mapGlass" x1="0" x2="1"><stop offset="0" stopColor="#70dfee" stopOpacity=".35"/><stop offset="1" stopColor="#baf4ff" stopOpacity=".78"/></linearGradient>
    </defs>
    <path className="map-vessel-shadow" d="M31 102 C70 88 236 77 310 92 C323 96 326 103 310 108 C227 129 84 132 33 116 C20 112 19 107 31 102Z"/>
    <path className="map-vessel-hull" fill="url(#mapHull)" d="M35 98 L276 81 L322 99 L279 119 L67 128 L27 112 Z"/>
    <path className="map-vessel-keel" d="M45 116 C115 127 230 122 286 111"/>
    <path className="map-vessel-deck" fill="url(#mapDeck)" d="M79 96 L237 85 L281 99 L236 110 L81 116 L49 107 Z"/>
    <path className="map-vessel-foredeck" d="M239 88 L283 99 L238 108 Z"/>
    <path className="map-vessel-cabin" d="M124 90 L190 83 L219 92 L196 101 L126 106 L103 99 Z"/>
    <path className="map-vessel-bridge" d="M145 82 L188 77 L207 85 L193 92 L144 97 L129 90 Z"/>
    <path className="map-vessel-window" fill="url(#mapGlass)" d="M149 83 L171 81 L171 89 L145 92 Z M176 80 L188 79 L200 85 L177 89 Z"/>
    <path className="map-vessel-aft" d="M75 96 L107 92 L118 101 L82 108 L57 105 Z"/>
    <path className="map-vessel-rail" d="M63 98 L235 85 M72 116 L235 108 M244 86 L282 97"/>
    <path className="map-vessel-mast" d="M171 79 L169 57 M158 66 L181 64 M169 57 L178 51"/>
    <path className="map-vessel-boom" d="M104 91 L89 75 L72 72 M89 75 L96 91"/>
    <circle className="map-vessel-radar" cx="181" cy="51" r="4"/>
    <circle className="map-vessel-sensor" cx="169" cy="56" r="3"/>
    <path className="map-vessel-transducer" d="M170 116 L171 125 M161 126 L181 124"/>
    <path className="map-vessel-wake" d="M31 107 C6 107 -2 114 -21 120 M36 115 C9 119 -3 129 -23 139"/>
   </svg>
  </motion.div>
  <motion.div className="map2-cross-track-swath" animate={{opacity:[.28,.66,.28]}} transition={{duration:3.8,repeat:Infinity,ease:'easeInOut'}} aria-hidden="true">
   <i/><i/><i/><i/><i/><i/><i/>
  </motion.div>
  <div className="map2-cross-track-label" aria-hidden="true">cross-track swath</div>
  <div className="map2-seafloor map2-seafloor-refined"><span/><span/><span/><span/><span/><span/></div>
 </div>
}

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
