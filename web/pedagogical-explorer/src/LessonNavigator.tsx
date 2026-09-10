import { ArrowLeft, ArrowRight, Grid3X3, Languages, Menu, X } from 'lucide-react';
import { useState } from 'react';

type Family='acoustics'|'propagation'|'arrays'|'platform'|'integration';
type Lang='en'|'pt';
type Lesson={id:string;displayId:string;title:string;titlePt:string;route:string;family:Family};
const lessons:Lesson[]=[
{id:'D1',displayId:'D1',title:'Acoustic Wave & Frequency',titlePt:'Onda Acústica e Frequência',route:'#wave-lab',family:'acoustics'},
{id:'D2',displayId:'D2',title:'Pulse & Signal Processing',titlePt:'Pulso e Processamento de Sinais',route:'#signal-lab/pulse',family:'acoustics'},
{id:'D3',displayId:'D3',title:'Sonar Equation & Propagation Loss',titlePt:'Equação Sonar e Perda de Propagação',route:'#sonar-equation-lab',family:'propagation'},
{id:'D4',displayId:'D4',title:'Sound Speed & Refraction',titlePt:'Velocidade do Som e Refração',route:'#refraction-lab',family:'propagation'},
{id:'D6',displayId:'D5',title:'Array Construction',titlePt:'Construção de Arrays',route:'#array-directivity-lab',family:'arrays'},
{id:'D7',displayId:'D6',title:'Beamforming',titlePt:'Beamforming',route:'#beamforming-lab',family:'arrays'},
{id:'D8',displayId:'D7',title:'SBES × MBES',titlePt:'SBES × MBES',route:'#echosounder-lab',family:'arrays'},
{id:'D9',displayId:'D8',title:'Bottom Detection',titlePt:'Detecção do Fundo',route:'#bottom-detection-lab',family:'arrays'},
{id:'D10',displayId:'D9',title:'Multisector MBES',titlePt:'MBES Multissetorial',route:'#multisector-lab',family:'arrays'},
{id:'D11',displayId:'D10',title:'Vessel & Sensor Configuration',titlePt:'Configuração da Embarcação e Sensores',route:'#vessel-configuration-lab',family:'platform'},
{id:'D12',displayId:'D11',title:'Vessel Motion',titlePt:'Movimento da Embarcação',route:'#vessel-motion-lab',family:'platform'},
{id:'D13',displayId:'D12',title:'PU & Sensor Integration',titlePt:'Integração da PU e Sensores',route:'#pu-sensor-lab',family:'platform'},
{id:'D14',displayId:'D13',title:'Timing & Latency',titlePt:'Tempo e Latência',route:'#timing-lab',family:'platform'},
{id:'D15',displayId:'D14',title:'Sounding Formation',titlePt:'Formação da Sondagem',route:'#sounding-formation-lab',family:'platform'},
{id:'D16',displayId:'D15',title:'Survey Planning',titlePt:'Planejamento do Levantamento',route:'#survey-planning-lab',family:'integration'},
{id:'D17',displayId:'D16',title:'Survey Coverage & Acquisition Trade-offs',titlePt:'Cobertura e Compromissos de Aquisição',route:'#tradeoff-lab',family:'integration'},
{id:'D18',displayId:'D17',title:'Uncertainty & Error Sources',titlePt:'Incerteza e Fontes de Erro',route:'#uncertainty-lab',family:'integration'},
];
const copy={
 en:{lesson:'LAB',previous:'Previous',next:'Next',labs:'Labs',availableLabs:'Available labs',close:'Close labs',current:'Current lab',open:'Open lab',home:'Home',acousticLab:'Acoustic Lab',lang:'PT-BR'},
 pt:{lesson:'LAB',previous:'Anterior',next:'Próximo',labs:'Labs',availableLabs:'Labs disponíveis',close:'Fechar labs',current:'Lab atual',open:'Abrir lab',home:'Home',acousticLab:'Laboratório de Acústica',lang:'EN'}
};
const lessonTitle=(lesson:Lesson,lang:Lang)=>lang==='pt'?lesson.titlePt:lesson.title;
const initialLanguage=():Lang=>sessionStorage.getItem('hydrosim-language')==='pt'?'pt':'en';

export default function LessonNavigator({currentId}:{currentId:string}){
 const[open,setOpen]=useState(false);const[lang,setLang]=useState<Lang>(initialLanguage);const t=copy[lang];const index=lessons.findIndex(l=>l.id===currentId);const current=lessons[index];if(!current)return null;
 const setLanguage=(next:Lang)=>{setLang(next);sessionStorage.setItem('hydrosim-language',next);window.dispatchEvent(new CustomEvent('hydrosim-language-change',{detail:next}))};
 const go=(lesson?:Lesson)=>{if(!lesson)return;sessionStorage.setItem('hydrosim-lesson-transition',JSON.stringify({from:current.displayId,to:lesson.displayId,title:lessonTitle(lesson,lang),family:lesson.family}));location.hash=lesson.route};
 return <><div className={`lesson-shell family-${current.family}`}>
  <button className="lesson-map-button" onClick={()=>{location.hash=''}} aria-label={t.home}><Grid3X3 size={16}/><span>{t.home}</span></button>
  <div className="lesson-location"><small>{t.lesson}</small><strong><span>{current.displayId}</span>{lessonTitle(current,lang)}</strong></div>
  <div className="lesson-spacer"/>
  <button className="lesson-step" disabled={index===0} onClick={()=>go(lessons[index-1])}><ArrowLeft size={15}/><span>{t.previous}</span></button>
  <button className="lesson-menu-button" onClick={()=>setLanguage(lang==='en'?'pt':'en')} aria-label={lang==='en'?'Mudar idioma para português':'Switch language to English'}><Languages size={16}/><span>{t.lang}</span></button>
  <button className="lesson-menu-button" onClick={()=>setOpen(v=>!v)} aria-expanded={open} aria-label={t.labs}><Menu size={16}/><span>{t.labs}</span></button>
  <button className="lesson-step next" disabled={index===lessons.length-1} onClick={()=>go(lessons[index+1])}><span>{t.next}</span><ArrowRight size={15}/></button>
 </div>
 {open&&<div className="lesson-drawer-backdrop" onClick={()=>setOpen(false)}><aside className="lesson-drawer" aria-label={t.availableLabs} onClick={e=>e.stopPropagation()}><header><div><small>{t.acousticLab.toUpperCase()}</small><strong>{t.labs}</strong></div><button onClick={()=>setOpen(false)} aria-label={t.close}><X size={18}/></button></header><div className="lesson-drawer-list">{lessons.map(l=><button key={l.id} className={`family-${l.family} ${l.id===current.id?'active':''}`} onClick={()=>go(l)}><span>{l.displayId}</span><div><strong>{lessonTitle(l,lang)}</strong><small>{l.id===current.id?t.current:t.open}</small></div><ArrowRight size={14}/></button>)}</div></aside></div>}
 </>
}
