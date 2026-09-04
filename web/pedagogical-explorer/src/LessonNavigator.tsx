import { ArrowLeft, ArrowRight, Grid3X3, Menu, X } from 'lucide-react';
import { useState } from 'react';

type Family='acoustics'|'propagation'|'arrays'|'platform'|'integration';
type Lesson={id:string;displayId:string;title:string;route:string;family:Family};
const lessons:Lesson[]=[
{id:'D1',displayId:'D1',title:'Acoustic Wave & Frequency',route:'#wave-lab',family:'acoustics'},
{id:'D2',displayId:'D2',title:'Pulse & Signal Processing',route:'#signal-lab/pulse',family:'acoustics'},
{id:'D3',displayId:'D3',title:'Sonar Equation & Propagation Loss',route:'#sonar-equation-lab',family:'propagation'},
{id:'D4',displayId:'D4',title:'Sound Speed & Refraction',route:'#refraction-lab',family:'propagation'},
{id:'D6',displayId:'D5',title:'Array Construction',route:'#array-directivity-lab',family:'arrays'},
{id:'D7',displayId:'D6',title:'Beamforming',route:'#beamforming-lab',family:'arrays'},
{id:'D8',displayId:'D7',title:'SBES × MBES',route:'#echosounder-lab',family:'arrays'},
{id:'D9',displayId:'D8',title:'Bottom Detection',route:'#bottom-detection-lab',family:'arrays'},
{id:'D10',displayId:'D9',title:'Multisector MBES',route:'#multisector-lab',family:'arrays'},
{id:'D11',displayId:'D10',title:'Vessel & Sensor Configuration',route:'#vessel-configuration-lab',family:'platform'},
{id:'D12',displayId:'D11',title:'Vessel Motion',route:'#vessel-motion-lab',family:'platform'},
{id:'D17',displayId:'D16',title:'Survey Coverage & Acquisition Trade-offs',route:'#tradeoff-lab',family:'integration'},
];
export default function LessonNavigator({currentId}:{currentId:string}){
 const[open,setOpen]=useState(false);const index=lessons.findIndex(l=>l.id===currentId);const current=lessons[index];if(!current)return null;
 const go=(lesson?:Lesson)=>{if(!lesson)return;sessionStorage.setItem('hydrosim-lesson-transition',JSON.stringify({from:current.displayId,to:lesson.displayId,title:lesson.title,family:lesson.family}));location.hash=lesson.route};
 return <><div className={`lesson-shell family-${current.family}`}>
  <button className="lesson-map-button" onClick={()=>{location.hash=''}} aria-label="System map"><Grid3X3 size={16}/><span>Didactic Explorer</span></button>
  <div className="lesson-location"><small>LESSON</small><strong><span>{current.displayId}</span>{current.title}</strong></div>
  <div className="lesson-spacer"/>
  <button className="lesson-step" disabled={index===0} onClick={()=>go(lessons[index-1])}><ArrowLeft size={15}/><span>Previous</span></button>
  <button className="lesson-menu-button" onClick={()=>setOpen(v=>!v)} aria-expanded={open} aria-label="Lessons"><Menu size={16}/><span>Lessons</span></button>
  <button className="lesson-step next" disabled={index===lessons.length-1} onClick={()=>go(lessons[index+1])}><span>Next</span><ArrowRight size={15}/></button>
 </div>
 {open&&<div className="lesson-drawer-backdrop" onClick={()=>setOpen(false)}><aside className="lesson-drawer" aria-label="Available lessons" onClick={e=>e.stopPropagation()}><header><div><small>DIDACTIC EXPLORER</small><strong>Lessons</strong></div><button onClick={()=>setOpen(false)} aria-label="Close lessons"><X size={18}/></button></header><div className="lesson-drawer-list">{lessons.map(l=><button key={l.id} className={`family-${l.family} ${l.id===current.id?'active':''}`} onClick={()=>go(l)}><span>{l.displayId}</span><div><strong>{l.title}</strong><small>{l.id===current.id?'Current lesson':'Open lesson'}</small></div><ArrowRight size={14}/></button>)}</div></aside></div>}
 </>
}
