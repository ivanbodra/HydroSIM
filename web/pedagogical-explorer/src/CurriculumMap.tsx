import { motion } from 'motion/react';
import { ArrowRight, Check, FlaskConical, GraduationCap, Layers3, LockKeyhole, Radar } from 'lucide-react';
import { useMemo, useState } from 'react';
import { pedagogicalTracks, type Experience, type TrackKey } from './pedagogical-plan';
import { languageFlag, languageTarget, useHydroLocale } from './language';

type Family='acoustics'|'propagation'|'arrays'|'acquisition'|'platform'|'integration';
const trackIcon:Record<TrackKey,typeof GraduationCap>={didactic:GraduationCap,patch:FlaskConical,acquisition:Radar};
const productionRoutes:Record<string,string>={D1:'#wave-lab',D2:'#signal-lab/pulse',D3:'#sonar-equation-lab',D4:'#refraction-lab',D6:'#array-directivity-lab',D7:'#beamforming-lab',D8:'#echosounder-lab',D9:'#bottom-detection-lab'};
const familyById:Record<string,Family>={D1:'acoustics',D2:'acoustics',D3:'propagation',D4:'propagation',D5:'acquisition',D6:'arrays',D7:'arrays',D8:'acquisition',D9:'acquisition',D10:'arrays',D11:'platform',D12:'platform',D13:'integration',D14:'integration',D15:'integration',D16:'integration',D17:'integration',D18:'integration'};
const didacticFamilies:Family[]=['acoustics','propagation','arrays','acquisition','platform','integration'];

const canonicalTitles:Record<string,{en:string;pt:string}>={
 D1:{en:'Acoustic Wave & Frequency',pt:'Onda Acústica e Frequência'},
 D2:{en:'Pulse & Signal Processing',pt:'Pulso e Processamento de Sinal'},
 D3:{en:'Sonar Equation & Propagation Loss',pt:'Equação Sonar e Perdas de Propagação'},
 D4:{en:'Sound Speed & Refraction',pt:'Velocidade do Som e Refração'},
 D5:{en:'Acoustic Detection Fundamentals',pt:'Fundamentos da Detecção Acústica'},
 D6:{en:'Transducer & Array Construction',pt:'Transdutor e Construção de Arrays'},
 D7:{en:'Beamforming & Electronic Steering',pt:'Beamforming e Apontamento Eletrônico'},
 D8:{en:'Echosounders — SBES vs MBES',pt:'Ecobatímetros — SBES vs MBES'},
 D9:{en:'Bottom Detection',pt:'Detecção do Fundo'},
 D10:{en:'Multisector MBES',pt:'MBES Multissetor'},
 D11:{en:'Vessel & Sensor Configuration',pt:'Configuração da Embarcação e Sensores'},
 D12:{en:'Vessel Motion',pt:'Movimentos da Embarcação'},
 D13:{en:'PU & Sensor Integration',pt:'Integração da PU e Sensores'},
 D14:{en:'Timing, Synchronization & Latency',pt:'Tempo, Sincronização e Latência'},
 D15:{en:'Sounding Formation',pt:'Formação da Sondagem'},
 D16:{en:'Survey Planning',pt:'Planejamento do Levantamento'},
 D17:{en:'Survey Coverage & Acquisition Trade-offs',pt:'Cobertura e Compromissos de Aquisição'},
 D18:{en:'Uncertainty / TPU',pt:'Incerteza / TPU'}
};

const familyMeta:Record<Family,{en:[string,string];pt:[string,string]}>= {
 acoustics:{en:['Signal & Wave','FROM OSCILLATION TO PULSE'],pt:['Sinal e Onda','DA OSCILAÇÃO AO PULSO']},
 propagation:{en:['Propagation','THROUGH THE WATER COLUMN'],pt:['Propagação','ATRAVÉS DA COLUNA D’ÁGUA']},
 arrays:{en:['Arrays & Beams','FROM APERTURE TO DIRECTION'],pt:['Arrays e Feixes','DA ABERTURA À DIREÇÃO']},
 acquisition:{en:['Detection & Echosounders','FROM RETURN TO MEASUREMENT'],pt:['Detecção e Ecobatímetros','DO RETORNO À MEDIÇÃO']},
 platform:{en:['Vessel & Motion','THE MOVING REFERENCE FRAME'],pt:['Embarcação e Movimento','O REFERENCIAL EM MOVIMENTO']},
 integration:{en:['Integrated Survey','BRING THE SYSTEM TOGETHER'],pt:['Levantamento Integrado','REÚNA O SISTEMA']}
};

const ui={
 en:{product:'Pedagogical Explorer',available:'available',map:'LEARNING MAP · HYDROGRAPHIC ACQUISITION',heroA:'See where you are.',heroB:'Choose what to explore next.',heroP:'Each lesson is part of one continuous acquisition story. Colors identify subject families; available learning slices open directly into the simulator.',availableLessons:'available lessons',didacticLessons:'didactic lessons',experiences:'experiences in this module',didactic:'DIDACTIC EXPLORER',journey:'Acquisition, one idea at a time.',availableNow:'Available now',planned:'Planned',lesson:'lesson',lessons:'lessons',live:'LIVE',open:'OPEN LESSON',calibration:'CALIBRATION WORKSPACE',survey:'SURVEY WORKSPACE',defined:'Structure defined · dedicated experiences will appear here as they become available.',plannedExperience:'PLANNED EXPERIENCE',input:'INPUT',explore:'EXPLORE',understand:'UNDERSTAND'},
 'pt-BR':{product:'Explorador Didático',available:'disponíveis',map:'MAPA DE APRENDIZAGEM · AQUISIÇÃO HIDROGRÁFICA',heroA:'Veja onde você está.',heroB:'Escolha o próximo conceito.',heroP:'Cada lição faz parte de uma única história de aquisição. As cores identificam famílias de assuntos; as lições disponíveis abrem diretamente no simulador.',availableLessons:'lições disponíveis',didacticLessons:'lições didáticas',experiences:'experiências neste módulo',didactic:'EXPLORADOR DIDÁTICO',journey:'Aquisição, uma ideia de cada vez.',availableNow:'Disponível agora',planned:'Planejado',lesson:'lição',lessons:'lições',live:'ATIVO',open:'ABRIR LIÇÃO',calibration:'AMBIENTE DE CALIBRAÇÃO',survey:'AMBIENTE DE LEVANTAMENTO',defined:'Estrutura definida · experiências dedicadas aparecerão aqui à medida que forem disponibilizadas.',plannedExperience:'EXPERIÊNCIA PLANEJADA',input:'ENTRADA',explore:'EXPLORE',understand:'COMPREENDA'}
} as const;

function SurveyBoat({labels}:{labels:{input:string;explore:string;understand:string}}){return <div className="map2-vessel-scene" aria-hidden="true"><div className="vessel-glow"/><svg className="map2-vessel" viewBox="0 0 520 250"><defs><linearGradient id="hull" x1="0" x2="1"><stop offset="0" stopColor="#17384a"/><stop offset=".55" stopColor="#2b6074"/><stop offset="1" stopColor="#12303f"/></linearGradient><linearGradient id="glass" x1="0" x2="1"><stop offset="0" stopColor="#4bd8ee" stopOpacity=".2"/><stop offset="1" stopColor="#7ef0ff" stopOpacity=".6"/></linearGradient></defs><path className="vessel-water" d="M36 190 C105 179 163 201 230 190 S362 178 486 190"/><path className="vessel-hull" fill="url(#hull)" d="M86 142 L425 142 L388 190 Q243 218 111 186 Z"/><path className="vessel-rubrail" d="M91 145 L422 145"/><path className="vessel-deck" d="M151 140 L185 102 L343 102 L385 140 Z"/><path className="vessel-cabin" d="M216 102 L238 66 L326 66 L344 102 Z"/><path className="vessel-window" fill="url(#glass)" d="M246 73 L278 73 L278 95 L237 95 Z M285 73 L318 73 L331 95 L285 95 Z"/><path className="vessel-mast" d="M285 66 L285 33 M273 44 L298 44 M285 32 L299 24"/><circle className="vessel-radar" cx="304" cy="24" r="5"/><path className="vessel-bow" d="M388 190 Q427 181 447 160"/><path className="vessel-sonar" d="M245 195 L245 214 M232 214 L258 214"/></svg><div className="vessel-beam"><i/><i/><i/><i/><i/></div><div className="vessel-seafloor"/><div className="vessel-flow"><span>{labels.input}</span><b>→</b><span>{labels.explore}</span><b>→</b><span>{labels.understand}</span></div></div>}

export default function CurriculumMap({onOpenLegacy:_onOpenLegacy}:{onOpenLegacy:()=>void}){
 const[track,setTrack]=useState<TrackKey>('didactic');
 const[locale,setLocale]=useHydroLocale();
 const t=ui[locale];
 const current=useMemo(()=>pedagogicalTracks.find(item=>item.key===track)!,[track]);
 const available=current.experiences.filter(e=>productionRoutes[e.id]).length;
 const open=(e:Experience)=>{const route=productionRoutes[e.id];if(route)location.hash=route};
 const title=(e:Experience)=>canonicalTitles[e.id]?.[locale==='en'?'en':'pt']??e.title;
 return <div className={`curriculum-map-v2 track-${track}`}>
  <header className="map2-topbar"><div className="map2-brand"><span className="map2-mark" aria-hidden="true">H</span><div><strong>HydroSIM</strong><small>{t.product}</small></div></div><div className="map2-actions" aria-label="HydroSIM learning map"><span>{available} {t.available}</span><button className="map2-language hydrosim-language-toggle" onClick={()=>setLocale(languageTarget(locale))}><span aria-hidden="true">{languageFlag(locale)}</span>{languageTarget(locale)==='pt-BR'?'PT-BR':'EN'}</button></div></header>
  <main className="map2-main">
   <section className="map2-hero"><div className="map2-hero-copy"><span>{t.map}</span><h1>{t.heroA}<br/><em>{t.heroB}</em></h1><p>{t.heroP}</p><div className="map2-status"><div><strong>{available}</strong><span>{t.availableLessons}</span></div><i/><div><strong>{current.experiences.length}</strong><span>{track==='didactic'?t.didacticLessons:t.experiences}</span></div></div></div><SurveyBoat labels={{input:t.input,explore:t.explore,understand:t.understand}}/></section>
   <nav className="map2-track-switcher" aria-label="HydroSIM modules">{pedagogicalTracks.map(item=>{const Icon=trackIcon[item.key];const active=track===item.key;const translated=item.key==='didactic'?(locale==='en'?'Didactic Module':'Módulo Didático'):item.key==='patch'?(locale==='en'?'Patch Test Module':'Módulo Patch Test'):(locale==='en'?'Acquisition Simulator':'Simulador de Aquisição');const subtitle=item.key==='didactic'?(locale==='en'?'Understand the acquisition physics':'Compreenda a física da aquisição'):item.key==='patch'?(locale==='en'?'Calibrate through evidence':'Calibre a partir das evidências'):(locale==='en'?'Build an integrated survey':'Construa um levantamento integrado');return <button key={item.key} type="button" aria-pressed={active} className={active?'active':''} onClick={()=>setTrack(item.key)}><Icon size={19}/><div><small>{item.key==='didactic'?'01':item.key==='patch'?'02':'03'}</small><strong>{translated}</strong><span>{subtitle}</span></div><ArrowRight size={15}/></button>})}</nav>
   {track==='didactic'?<section className="map2-journey"><header><div><span>{t.didactic}</span><h2>{t.journey}</h2></div><div className="map2-key" aria-label="Lesson availability legend"><span><i className="available-dot"/>{t.availableNow}</span><span><i className="planned-dot"/>{t.planned}</span></div></header><div className="family-stack">{didacticFamilies.map(family=>{const lessons=current.experiences.filter(e=>familyById[e.id]===family);if(!lessons.length)return null;const meta=familyMeta[family][locale==='en'?'en':'pt'];return <section key={family} className={`family-lane family-${family}`}><div className="family-label"><small>{meta[1]}</small><strong>{meta[0]}</strong><span>{lessons.length} {lessons.length===1?t.lesson:t.lessons}</span></div><div className="family-path">{lessons.map((e,index)=>{const ready=Boolean(productionRoutes[e.id]);return <motion.button key={e.id} type="button" aria-disabled={!ready} className={`lesson-node ${ready?'ready':'planned'}`} onClick={()=>ready&&open(e)} whileHover={ready?{y:-3}:undefined}><div className="lesson-node-head"><span>{e.id}</span>{ready?<i className="ready-badge"><Check size={11}/>{t.live}</i>:<i className="planned-badge"><LockKeyhole size={10}/>{t.planned.toUpperCase()}</i>}</div><strong>{title(e)}</strong><small>{e.outputs[0]}</small>{ready&&<div className="lesson-open">{t.open} <ArrowRight size={12}/></div>}{index<lessons.length-1&&<span className="node-connector" aria-hidden="true"/>}</motion.button>})}</div></section>})}</div></section>:<section className="map2-chapter"><div className="chapter-intro"><span>{track==='patch'?t.calibration:t.survey}</span><h2>{current.title}</h2><p>{current.subtitle}</p><div className="chapter-state"><Layers3 size={17}/><span>{t.defined}</span></div></div><div className="chapter-grid">{current.experiences.map((e,index)=><motion.article key={e.id} whileHover={{y:-2}}><div><span>{String(index+1).padStart(2,'0')}</span><strong>{e.id}</strong></div><h3>{title(e)}</h3><p>{e.designCue}</p><small>{t.plannedExperience}</small></motion.article>)}</div></section>}
  </main>
 </div>
}
