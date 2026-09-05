import { ArrowLeft, ArrowRight, Grid3X3, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useHydroLocale } from './language';

type Lesson={id:string;titleEn:string;titlePt:string;route:string;family:'acoustics'|'propagation'|'arrays'|'acquisition'};
const lessons:Lesson[]=[
{id:'D1',titleEn:'Acoustic Wave & Frequency',titlePt:'Onda Acústica e Frequência',route:'#wave-lab',family:'acoustics'},
{id:'D2',titleEn:'Pulse & Signal Processing',titlePt:'Pulso e Processamento de Sinal',route:'#signal-lab/pulse',family:'acoustics'},
{id:'D3',titleEn:'Sonar Equation & Propagation Loss',titlePt:'Equação Sonar e Perdas de Propagação',route:'#sonar-equation-lab',family:'propagation'},
{id:'D4',titleEn:'Sound Speed & Refraction',titlePt:'Velocidade do Som e Refração',route:'#refraction-lab',family:'propagation'},
{id:'D6',titleEn:'Transducer & Array Construction',titlePt:'Transdutor e Construção de Arrays',route:'#array-directivity-lab',family:'arrays'},
{id:'D7',titleEn:'Beamforming & Electronic Steering',titlePt:'Beamforming e Apontamento Eletrônico',route:'#beamforming-lab',family:'arrays'},
{id:'D8',titleEn:'Echosounders — SBES vs MBES',titlePt:'Ecobatímetros — SBES vs MBES',route:'#echosounder-lab',family:'acquisition'},
{id:'D9',titleEn:'Bottom Detection',titlePt:'Detecção do Fundo',route:'#bottom-detection-lab',family:'acquisition'},
];

const ui={
 en:{map:'Didactic Explorer',lesson:'LESSON',previous:'Previous',lessons:'Lessons',next:'Next',current:'Current lesson',open:'Open lesson',drawer:'DIDACTIC EXPLORER'},
 'pt-BR':{map:'Explorador Didático',lesson:'LIÇÃO',previous:'Anterior',lessons:'Lições',next:'Próxima',current:'Lição atual',open:'Abrir lição',drawer:'EXPLORADOR DIDÁTICO'}
} as const;

export default function LessonNavigator({currentId}:{currentId:string}){
 const[open,setOpen]=useState(false);const[locale]=useHydroLocale();const t=ui[locale];const index=lessons.findIndex(l=>l.id===currentId);const current=lessons[index];if(!current)return null;
 const title=(lesson:Lesson)=>locale==='en'?lesson.titleEn:lesson.titlePt;
 const go=(lesson?:Lesson)=>{if(!lesson)return;sessionStorage.setItem('hydrosim-lesson-transition',JSON.stringify({from:current.id,to:lesson.id,title:title(lesson),family:lesson.family}));location.hash=lesson.route};
 return <><div className={`lesson-shell family-${current.family}`}>
  <button className="lesson-map-button" onClick={()=>{location.hash=''}} aria-label={t.map}><Grid3X3 size={16}/><span>{t.map}</span></button>
  <div className="lesson-location"><small>{t.lesson}</small><strong><span>{current.id}</span>{title(current)}</strong></div>
  <div className="lesson-spacer"/>
  <button className="lesson-step" disabled={index===0} onClick={()=>go(lessons[index-1])}><ArrowLeft size={15}/><span>{t.previous}</span></button>
  <button className="lesson-menu-button" onClick={()=>setOpen(v=>!v)}><Menu size={16}/><span>{t.lessons}</span></button>
  <button className="lesson-step next" disabled={index===lessons.length-1} onClick={()=>go(lessons[index+1])}><span>{t.next}</span><ArrowRight size={15}/></button>
 </div>
 {open&&<div className="lesson-drawer-backdrop" onClick={()=>setOpen(false)}><aside className="lesson-drawer" onClick={e=>e.stopPropagation()}><header><div><small>{t.drawer}</small><strong>{t.lessons}</strong></div><button onClick={()=>setOpen(false)}><X size={18}/></button></header><div className="lesson-drawer-list">{lessons.map(l=><button key={l.id} className={`family-${l.family} ${l.id===current.id?'active':''}`} onClick={()=>go(l)}><span>{l.id}</span><div><strong>{title(l)}</strong><small>{l.id===current.id?t.current:t.open}</small></div><ArrowRight size={14}/></button>)}</div></aside></div>}
 </>
}
