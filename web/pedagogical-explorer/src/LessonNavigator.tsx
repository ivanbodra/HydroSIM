import { ArrowLeft, ArrowRight, Grid3X3, Menu, X } from 'lucide-react';
import { useState } from 'react';

type Lesson={id:string;title:string;route:string;family:'acoustics'|'propagation'|'arrays'|'acquisition'};
const lessons:Lesson[]=[
{id:'D1',title:'Acoustic Wave & Frequency',route:'#wave-lab',family:'acoustics'},
{id:'D2',title:'Pulse & Signal Processing',route:'#signal-lab/pulse',family:'acoustics'},
{id:'D3',title:'Sonar Equation & Propagation Loss',route:'#sonar-equation-lab',family:'propagation'},
{id:'D4',title:'Sound Speed & Refraction',route:'#refraction-lab',family:'propagation'},
{id:'D6',title:'Array Construction',route:'#array-directivity-lab',family:'arrays'},
{id:'D7',title:'Beamforming',route:'#beamforming-lab',family:'arrays'},
{id:'D8',title:'SBES × MBES',route:'#echosounder-lab',family:'acquisition'},
{id:'D9',title:'Bottom Detection',route:'#bottom-detection-lab',family:'acquisition'},
];
export default function LessonNavigator({currentId}:{currentId:string}){
 const[open,setOpen]=useState(false);const index=lessons.findIndex(l=>l.id===currentId);const current=lessons[index];if(!current)return null;
 const go=(lesson?:Lesson)=>{if(!lesson)return;sessionStorage.setItem('hydrosim-lesson-transition',JSON.stringify({from:current.id,to:lesson.id,title:lesson.title,family:lesson.family}));location.hash=lesson.route};
 return <><div className={`lesson-shell family-${current.family}`}>
  <button className="lesson-map-button" onClick={()=>{location.hash=''}} aria-label="System map"><Grid3X3 size={16}/><span>Didactic Explorer</span></button>
  <div className="lesson-location"><small>LESSON</small><strong><span>{current.id}</span>{current.title}</strong></div>
  <div className="lesson-spacer"/>
  <button className="lesson-step" disabled={index===0} onClick={()=>go(lessons[index-1])}><ArrowLeft size={15}/><span>Previous</span></button>
  <button className="lesson-menu-button" onClick={()=>setOpen(v=>!v)}><Menu size={16}/><span>Lessons</span></button>
  <button className="lesson-step next" disabled={index===lessons.length-1} onClick={()=>go(lessons[index+1])}><span>Next</span><ArrowRight size={15}/></button>
 </div>
 {open&&<div className="lesson-drawer-backdrop" onClick={()=>setOpen(false)}><aside className="lesson-drawer" onClick={e=>e.stopPropagation()}><header><div><small>DIDACTIC EXPLORER</small><strong>Lessons</strong></div><button onClick={()=>setOpen(false)}><X size={18}/></button></header><div className="lesson-drawer-list">{lessons.map(l=><button key={l.id} className={`family-${l.family} ${l.id===current.id?'active':''}`} onClick={()=>go(l)}><span>{l.id}</span><div><strong>{l.title}</strong><small>{l.id===current.id?'Current lesson':'Open lesson'}</small></div><ArrowRight size={14}/></button>)}</div></aside></div>}
 </>
}
