import { ArrowLeft, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Vec={x:number;y:number;z:number;unit:string};
type Response={scenario_id:string;stages:string[];active_stage:string;stage_index:number;ping_index:number;beam_index:number;detection_index:number;detection_method:string;twtt_seconds:number;reconstructed_range_m:number;detected_across_track_angle_rad:number|null;associated_pose_position:Vec;truth_sounding:Vec;reconstructed_sounding:Vec;truth_minus_reconstructed:Vec;reconstruction_basis:string;semantics:Record<string,string>};
type Axis3={x:number;y:number;z:number};
type Attitude={roll:number;pitch:number;yaw:number};
const labels:Record<string,{en:string;pt:string}>={
 transmit:{en:'Transmit',pt:'Transmissão'},propagation:{en:'Propagation',pt:'Propagação'},'seabed-interaction':{en:'Seabed interaction',pt:'Interação com o fundo'},receive:{en:'Receive',pt:'Recepção'},'bottom-detection':{en:'Bottom detection',pt:'Detecção do fundo'},'twtt-range':{en:'Travel time / range',pt:'Tempo de percurso / distância'},'beam-angle':{en:'Beam angle',pt:'Ângulo do feixe'},'pose-association':{en:'Vessel pose',pt:'Pose da embarcação'},reconstruction:{en:'3D reconstruction',pt:'Reconstrução 3D'},'truth-observed':{en:'Compare soundings',pt:'Comparar sondagens'}
};
const stageCopy:Record<string,{en:string;pt:string}>={
 transmit:{en:'A ping begins at the transducer.',pt:'Um ping começa no transdutor.'},propagation:{en:'The acoustic pulse travels through the water.',pt:'O pulso acústico percorre a água.'},'seabed-interaction':{en:'Energy reaches the seabed and returns.',pt:'A energia alcança o fundo e retorna.'},receive:{en:'The receiver captures the returning echo.',pt:'O receptor capta o eco de retorno.'},'bottom-detection':{en:'A bottom return is selected from the echo.',pt:'Um retorno do fundo é selecionado no eco.'},'twtt-range':{en:'Travel time constrains the sounding range.',pt:'O tempo de percurso restringe a distância da sondagem.'},'beam-angle':{en:'The detected beam angle sets the across-track direction.',pt:'O ângulo detectado define a direção transversal.'},'pose-association':{en:'The detection is associated with vessel position and attitude.',pt:'A detecção é associada à posição e à atitude da embarcação.'},reconstruction:{en:'The sounding is placed in 3D space.',pt:'A sondagem é posicionada no espaço 3D.'},'truth-observed':{en:'Reference and reconstructed positions can now be compared.',pt:'As posições de referência e reconstruída podem agora ser comparadas.'}
};
const fmt=(v:number,d=2)=>Number.isFinite(v)?v.toFixed(d):'—';
const defaults={twttMs:40,angleDeg:17.46,position:{x:0,y:0,z:0} as Axis3,attitude:{roll:0,pitch:0,yaw:0} as Attitude,lever:{x:0,y:0,z:0} as Axis3,soundSpeed:1565,pingIndex:12,rxStartMs:10,rxEndMs:100};

function AxisInputs({value,onChange,step=0.1}:{value:Axis3;onChange:(v:Axis3)=>void;step?:number}){
 return <div className="sf-axis3">{(['x','y','z'] as const).map(k=><label key={k}><span>{k.toUpperCase()}</span><input type="number" step={step} value={value[k]} onChange={e=>onChange({...value,[k]:Number(e.target.value)})}/></label>)}</div>
}
function AttitudeInputs({value,onChange}:{value:Attitude;onChange:(v:Attitude)=>void}){
 return <div className="sf-axis3">{(['roll','pitch','yaw'] as const).map(k=><label key={k}><span>{k[0].toUpperCase()}</span><input type="number" step="0.5" value={value[k]} onChange={e=>onChange({...value,[k]:Number(e.target.value)})}/></label>)}</div>
}

export default function SoundingFormationLab({onBack}:{onBack:()=>void}){
 const[lang,setLang]=useState<'en'|'pt'>('en');const[data,setData]=useState<Response|null>(null);const[stage,setStage]=useState('transmit');const[loading,setLoading]=useState(false);const[error,setError]=useState(false);
 const[twttMs,setTwttMs]=useState(defaults.twttMs);const[angleDeg,setAngleDeg]=useState(defaults.angleDeg);const[position,setPosition]=useState<Axis3>(defaults.position);const[attitude,setAttitude]=useState<Attitude>(defaults.attitude);const[lever,setLever]=useState<Axis3>(defaults.lever);const[soundSpeed,setSoundSpeed]=useState(defaults.soundSpeed);const[pingIndex,setPingIndex]=useState(defaults.pingIndex);const[rxStartMs,setRxStartMs]=useState(defaults.rxStartMs);const[rxEndMs,setRxEndMs]=useState(defaults.rxEndMs);
 const request=useMemo(()=>({active_stage:stage,twtt_seconds:twttMs/1000,detected_across_track_angle_rad:angleDeg*Math.PI/180,position_x_m:position.x,position_y_m:position.y,position_z_m:position.z,roll_deg:attitude.roll,pitch_deg:attitude.pitch,yaw_deg:attitude.yaw,lever_arm_x_m:lever.x,lever_arm_y_m:lever.y,lever_arm_z_m:lever.z,sound_speed_mps:soundSpeed,ping_index:pingIndex,trigger_time_seconds:0,tx_time_seconds:0,rx_start_time_seconds:rxStartMs/1000,rx_end_time_seconds:Math.max(rxEndMs,rxStartMs+1)/1000}),[stage,twttMs,angleDeg,position,attitude,lever,soundSpeed,pingIndex,rxStartMs,rxEndMs]);
 useEffect(()=>{const c=new AbortController();const timer=window.setTimeout(()=>{setLoading(true);setError(false);fetch('/api/v1/pedagogical/sounding-formation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal:c.signal}).then(r=>{if(!r.ok)throw new Error();return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(true)}).finally(()=>setLoading(false))},70);return()=>{window.clearTimeout(timer);c.abort()}},[request]);
 const stages=data?.stages??Object.keys(labels);const index=Math.max(0,stages.indexOf(stage));const copy=stageCopy[stage]?.[lang]??stage;const returnedAngleDeg=useMemo(()=>data?.detected_across_track_angle_rad==null?null:data.detected_across_track_angle_rad*180/Math.PI,[data]);
 const go=(n:number)=>setStage(stages[Math.max(0,Math.min(stages.length-1,n))]);
 const reset=()=>{setStage('transmit');setTwttMs(defaults.twttMs);setAngleDeg(defaults.angleDeg);setPosition({...defaults.position});setAttitude({...defaults.attitude});setLever({...defaults.lever});setSoundSpeed(defaults.soundSpeed);setPingIndex(defaults.pingIndex);setRxStartMs(defaults.rxStartMs);setRxEndMs(defaults.rxEndMs)};
 const posPct=(v:number)=>Math.max(8,Math.min(92,50+v*.8));
 return <main className="sf-lab">
  <header className="sf-top"><button onClick={onBack}><ArrowLeft size={17}/>{lang==='en'?'Learning map':'Mapa'}</button><div><span>PED-D15</span><strong>{lang==='en'?'Sounding Formation':'Formação da Sondagem'}</strong></div><div className="sf-lang"><button className={lang==='en'?'on':''} onClick={()=>setLang('en')}>EN</button><button className={lang==='pt'?'on':''} onClick={()=>setLang('pt')}>PT-BR</button></div></header>
  <section className="sf-head"><span>{lang==='en'?'FROM PING TO 3D SOUNDING':'DO PING À SONDAGEM 3D'}</span><h1>{lang==='en'?'Change the inputs. Follow the sounding.':'Altere as entradas. Acompanhe a sondagem.'}</h1><p>{copy}</p></section>
  <section className="sf-stagebar">{stages.map((s,i)=><button key={s} className={s===stage?'active':i<index?'done':''} onClick={()=>setStage(s)}><i>{i+1}</i><span>{labels[s]?.[lang]??s}</span></button>)}</section>
  <section className="sf-layout">
   <aside className="sf-inputs">
    <div className="sf-control"><label><span>TWTT</span><strong>{fmt(twttMs,0)} ms</strong></label><input type="range" min="15" max="100" step="1" value={twttMs} onChange={e=>setTwttMs(Number(e.target.value))}/></div>
    <div className="sf-control"><label><span>{lang==='en'?'Beam angle':'Ângulo do feixe'}</span><strong>{fmt(angleDeg,1)}°</strong></label><input type="range" min="-60" max="60" step="0.5" value={angleDeg} onChange={e=>setAngleDeg(Number(e.target.value))}/></div>
    <div className="sf-group"><label>{lang==='en'?'Vessel position (m)':'Posição da embarcação (m)'}</label><AxisInputs value={position} onChange={setPosition}/></div>
    <div className="sf-group"><label title={lang==='pt'?'Roll: balanço; Pitch: arfagem; Yaw: guinada/Heading.':'Vessel attitude angles.'}>{lang==='en'?'Attitude (deg)':'Atitude (graus)'}</label><AttitudeInputs value={attitude} onChange={setAttitude}/><small>{lang==='pt'?'Roll = balanço · Pitch = arfagem · Yaw = guinada':'Roll · Pitch · Yaw'}</small></div>
    <div className="sf-group"><label>{lang==='en'?'Sensor lever arm (m)':'Lever arm do sensor (m)'}</label><AxisInputs value={lever} onChange={setLever}/></div>
    <div className="sf-control"><label><span>{lang==='en'?'Sound speed':'Velocidade do som'}</span><strong>{soundSpeed} m/s</strong></label><input type="range" min="1450" max="1600" step="1" value={soundSpeed} onChange={e=>setSoundSpeed(Number(e.target.value))}/></div>
    <div className="sf-config-row"><label><span>Ping</span><input type="number" min="0" step="1" value={pingIndex} onChange={e=>setPingIndex(Math.max(0,Number(e.target.value)))}/></label><label><span>RX {lang==='en'?'start':'início'}</span><input type="number" min="0" max={rxEndMs-1} step="1" value={rxStartMs} onChange={e=>setRxStartMs(Number(e.target.value))}/><i>ms</i></label><label><span>RX {lang==='en'?'end':'fim'}</span><input type="number" min={rxStartMs+1} step="1" value={rxEndMs} onChange={e=>setRxEndMs(Number(e.target.value))}/><i>ms</i></label></div>
   </aside>
   <div className="sf-maincol">
    <div className="sf-workspace">
     <div className="sf-scene">
      <div className="sf-water"/><div className="sf-vessel" style={{left:`${posPct(data?.associated_pose_position.y??0)}%`}}>▰</div><div className={`sf-beam stage-${index}`} style={{left:`${posPct(data?.associated_pose_position.y??0)}%`,transform:`translateX(-50%) rotate(${Math.max(-55,Math.min(55,returnedAngleDeg??0))*.28}deg)`}}/><div className="sf-bottom"/><div className={`sf-echo stage-${index}`} style={{left:`${posPct(data?.reconstructed_sounding.y??0)}%`}}/>
      {data&&<><span className="sf-truth" style={{left:`${posPct(data.truth_sounding.y)}%`}}/><span className="sf-recon" style={{left:`${posPct(data.reconstructed_sounding.y)}%`}}/></>}
      <div className="sf-scene-label"><strong>{labels[stage]?.[lang]}</strong><span>{copy}</span></div>
     </div>
     <aside className="sf-readouts">
      <div><small>Ping</small><strong>{data?.ping_index??'—'}</strong></div><div><small>Beam</small><strong>{data?.beam_index??'—'}</strong></div><div><small>TWTT</small><strong>{data?`${fmt(data.twtt_seconds*1000,1)} ms`:'—'}</strong></div><div><small>{lang==='en'?'Range':'Distância'}</small><strong>{data?`${fmt(data.reconstructed_range_m,2)} m`:'—'}</strong></div><div><small>{lang==='en'?'Beam angle':'Ângulo'}</small><strong>{returnedAngleDeg==null?'—':`${fmt(returnedAngleDeg,1)}°`}</strong></div><div><small>{lang==='en'?'Sensor Y':'Sensor Y'}</small><strong>{data?`${fmt(data.associated_pose_position.y)} m`:'—'}</strong></div>
      <div className="wide"><small>{lang==='en'?'Reference sounding':'Sondagem de referência'}</small><strong>{data?`X ${fmt(data.truth_sounding.x)} · Y ${fmt(data.truth_sounding.y)} · Z ${fmt(data.truth_sounding.z)} m`:'—'}</strong></div>
      <div className="wide"><small>{lang==='en'?'Reconstructed sounding':'Sondagem reconstruída'}</small><strong>{data?`X ${fmt(data.reconstructed_sounding.x)} · Y ${fmt(data.reconstructed_sounding.y)} · Z ${fmt(data.reconstructed_sounding.z)} m`:'—'}</strong></div>
      <div className="wide accent"><small>{lang==='en'?'Difference':'Diferença'}</small><strong>{data?`ΔX ${fmt(data.truth_minus_reconstructed.x)} · ΔY ${fmt(data.truth_minus_reconstructed.y)} · ΔZ ${fmt(data.truth_minus_reconstructed.z)} m`:'—'}</strong></div>
      <div className="wide timing"><small>{lang==='en'?'Receive window':'Janela de recepção'}</small><div className="sf-mini-timeline"><span style={{left:`${Math.min(90,rxStartMs/1.2)}%`,width:`${Math.max(3,(rxEndMs-rxStartMs)/1.2)}%`}}/></div><strong>{rxStartMs}–{rxEndMs} ms</strong></div>
     </aside>
    </div>
    <footer className="sf-controls"><button onClick={()=>go(index-1)} disabled={index===0}><ChevronLeft size={16}/>{lang==='en'?'Previous':'Anterior'}</button><button className="reset" onClick={reset}><RotateCcw size={15}/>{lang==='en'?'Reset':'Reiniciar'}</button><button onClick={()=>go(index+1)} disabled={index===stages.length-1}>{lang==='en'?'Next stage':'Próxima etapa'}<ChevronRight size={16}/></button></footer>
   </div>
  </section>
  {(loading||error)&&<div className={`sf-status ${error?'error':''}`}>{error?(lang==='en'?'Unable to update this view.':'Não foi possível atualizar esta visualização.'):(lang==='en'?'Updating…':'Atualizando…')}</div>}
 </main>
}