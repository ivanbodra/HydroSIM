import { ArrowLeft, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Vec={x:number;y:number;z:number;unit:string};
type Response={scenario_id:string;stages:string[];active_stage:string;stage_index:number;ping_index:number;beam_index:number;detection_index:number;detection_method:string;twtt_seconds:number;detected_across_track_angle_rad:number|null;associated_pose_position:Vec;truth_sounding:Vec;reconstructed_sounding:Vec;truth_minus_reconstructed:Vec;reconstruction_basis:string;semantics:Record<string,string>};
const labels:Record<string,{en:string;pt:string}>={
 transmit:{en:'Transmit',pt:'Transmissão'},propagation:{en:'Propagation',pt:'Propagação'},'seabed-interaction':{en:'Seabed interaction',pt:'Interação com o fundo'},receive:{en:'Receive',pt:'Recepção'},'bottom-detection':{en:'Bottom detection',pt:'Detecção do fundo'},'twtt-range':{en:'Travel time / range',pt:'Tempo de percurso / distância'},'beam-angle':{en:'Beam angle',pt:'Ângulo do feixe'},'pose-association':{en:'Vessel pose',pt:'Pose da embarcação'},reconstruction:{en:'3D reconstruction',pt:'Reconstrução 3D'},'truth-observed':{en:'Compare soundings',pt:'Comparar sondagens'}
};
const stageCopy:Record<string,{en:string;pt:string}>={
 transmit:{en:'A ping begins at the transducer.',pt:'Um ping começa no transdutor.'},propagation:{en:'The acoustic pulse travels through the water.',pt:'O pulso acústico percorre a água.'},'seabed-interaction':{en:'Energy reaches the seabed and returns.',pt:'A energia alcança o fundo e retorna.'},receive:{en:'The receiver captures the returning echo.',pt:'O receptor capta o eco de retorno.'},'bottom-detection':{en:'A bottom return is selected from the echo.',pt:'Um retorno do fundo é selecionado no eco.'},'twtt-range':{en:'Travel time constrains the sounding range.',pt:'O tempo de percurso restringe a distância da sondagem.'},'beam-angle':{en:'The detected beam angle sets the across-track direction.',pt:'O ângulo detectado define a direção transversal.'},'pose-association':{en:'The detection is associated with vessel position and attitude.',pt:'A detecção é associada à posição e à atitude da embarcação.'},reconstruction:{en:'Geometry places the sounding in 3D space.',pt:'A geometria posiciona a sondagem no espaço 3D.'},'truth-observed':{en:'Reference and reconstructed positions can now be compared.',pt:'As posições de referência e reconstruída podem agora ser comparadas.'}
};
const fmt=(v:number,d=2)=>Number.isFinite(v)?v.toFixed(d):'—';
export default function SoundingFormationLab({onBack}:{onBack:()=>void}){
 const[lang,setLang]=useState<'en'|'pt'>('en');const[data,setData]=useState<Response|null>(null);const[stage,setStage]=useState('transmit');const[loading,setLoading]=useState(false);const[error,setError]=useState(false);
 useEffect(()=>{const c=new AbortController();setLoading(true);setError(false);fetch('/api/v1/pedagogical/sounding-formation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({active_stage:stage}),signal:c.signal}).then(r=>{if(!r.ok)throw new Error();return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(true)}).finally(()=>setLoading(false));return()=>c.abort()},[stage]);
 const stages=data?.stages??Object.keys(labels);const index=Math.max(0,stages.indexOf(stage));const copy=stageCopy[stage]?.[lang]??stage;const angleDeg=useMemo(()=>data?.detected_across_track_angle_rad==null?null:data.detected_across_track_angle_rad*180/Math.PI,[data]);
 const go=(n:number)=>setStage(stages[Math.max(0,Math.min(stages.length-1,n))]);
 return <main className="sf-lab">
  <header className="sf-top"><button onClick={onBack}><ArrowLeft size={17}/>{lang==='en'?'Learning map':'Mapa'}</button><div><span>PED-D14</span><strong>{lang==='en'?'Sounding Formation':'Formação da Sondagem'}</strong></div><div className="sf-lang"><button className={lang==='en'?'on':''} onClick={()=>setLang('en')}>EN</button><button className={lang==='pt'?'on':''} onClick={()=>setLang('pt')}>PT-BR</button></div></header>
  <section className="sf-head"><span>{lang==='en'?'FROM PING TO 3D SOUNDING':'DO PING À SONDAGEM 3D'}</span><h1>{lang==='en'?'Follow one sounding as it is formed.':'Acompanhe uma sondagem enquanto ela é formada.'}</h1><p>{copy}</p></section>
  <section className="sf-stagebar">{stages.map((s,i)=><button key={s} className={s===stage?'active':i<index?'done':''} onClick={()=>setStage(s)}><i>{i+1}</i><span>{labels[s]?.[lang]??s}</span></button>)}</section>
  <section className="sf-workspace">
   <div className="sf-scene">
    <div className="sf-water"/><div className="sf-vessel">▰</div><div className={`sf-beam stage-${index}`}/><div className="sf-bottom"/>
    <div className={`sf-echo stage-${index}`}/>
    {data&&<><span className="sf-truth" style={{left:`${54+data.truth_sounding.y*.8}%`,top:`${70+data.truth_sounding.z*.25}%`}}/><span className="sf-recon" style={{left:`${54+data.reconstructed_sounding.y*.8}%`,top:`${70+data.reconstructed_sounding.z*.25}%`}}/></>}
    <div className="sf-scene-label"><strong>{labels[stage]?.[lang]}</strong><span>{copy}</span></div>
   </div>
   <aside className="sf-readouts">
    <div><small>Ping</small><strong>{data?.ping_index??'—'}</strong></div><div><small>Beam</small><strong>{data?.beam_index??'—'}</strong></div><div><small>{lang==='en'?'Detection':'Detecção'}</small><strong>{data?.detection_index??'—'}</strong></div>
    <div><small>TWTT</small><strong>{data?fmt(data.twtt_seconds*1000,1):'—'} ms</strong></div><div><small>{lang==='en'?'Beam angle':'Ângulo'}</small><strong>{angleDeg==null?'—':`${fmt(angleDeg,1)}°`}</strong></div>
    <div className="wide"><small>{lang==='en'?'Reference sounding':'Sondagem de referência'}</small><strong>{data?`Y ${fmt(data.truth_sounding.y)} m · Z ${fmt(data.truth_sounding.z)} m`:'—'}</strong></div>
    <div className="wide"><small>{lang==='en'?'Reconstructed sounding':'Sondagem reconstruída'}</small><strong>{data?`Y ${fmt(data.reconstructed_sounding.y)} m · Z ${fmt(data.reconstructed_sounding.z)} m`:'—'}</strong></div>
    <div className="wide accent"><small>{lang==='en'?'Difference':'Diferença'}</small><strong>{data?`ΔY ${fmt(data.truth_minus_reconstructed.y)} m · ΔZ ${fmt(data.truth_minus_reconstructed.z)} m`:'—'}</strong></div>
   </aside>
  </section>
  <footer className="sf-controls"><button onClick={()=>go(index-1)} disabled={index===0}><ChevronLeft size={16}/>{lang==='en'?'Previous':'Anterior'}</button><button className="reset" onClick={()=>setStage('transmit')}><RotateCcw size={15}/>{lang==='en'?'Reset':'Reiniciar'}</button><button onClick={()=>go(index+1)} disabled={index===stages.length-1}>{lang==='en'?'Next stage':'Próxima etapa'}<ChevronRight size={16}/></button></footer>
  {(loading||error)&&<div className={`sf-status ${error?'error':''}`}>{error?(lang==='en'?'Unable to update this view.':'Não foi possível atualizar esta visualização.'):(lang==='en'?'Updating…':'Atualizando…')}</div>}
 </main>
}
