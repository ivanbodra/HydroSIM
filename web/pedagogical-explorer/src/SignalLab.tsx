import { Activity, RotateCcw, SlidersHorizontal, Sparkles, Waves } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type PulseType='cw'|'lfm';
type ChirpDirection='up'|'down';
type EnvelopeModel='rectangular'|'tukey';
type Trace={x:number[];y:number[];x_unit:string;y_unit:string};
type SignalResponse={pulse_type:PulseType;waveform:Trace;instantaneous_frequency:Trace;matched_filter:Trace;metadata:Record<string,number|string>};
type Locale='en'|'pt-BR';

type SignalConfig={pulse_type:PulseType;center_frequency_khz:number;duration_ms:number;bandwidth_khz:number;chirp_direction:ChirpDirection;envelope_model:EnvelopeModel};

const API_BASE=(import.meta.env.VITE_HYDROSIM_API_BASE as string|undefined)??'http://127.0.0.1:8000';
const initial:SignalConfig={pulse_type:'lfm',center_frequency_khz:200,duration_ms:1,bandwidth_khz:100,chirp_direction:'up',envelope_model:'rectangular'};

const text={
 en:{back:'← System map',lab:'Signal laboratory',signal:'Signal',focusPulse:'Pulse',focusFrequency:'Frequency',focusCompression:'Compression',focusWaveform:'Waveform',kicker:'PED-D2 · PULSE & SIGNAL PROCESSING',title:'Change the transmitted pulse and watch the same scientific state reshape every visual.',subtitle:'The traces below come from HydroSIM’s canonical Python signal model. React owns interaction and presentation only.',controls:'Signal controls',waveform:'Waveform',frequency:'Centre frequency',duration:'Pulse duration',bandwidth:'LFM bandwidth',direction:'Sweep direction',envelope:'Envelope',up:'Up',down:'Down',rectangular:'Rectangular',tukey:'Tukey',reset:'Reset',transmit:'01 · TRANSMIT',frequencyLens:'02 · FREQUENCY LENS',process:'03 · PROCESS',flowTransmit:'TRANSMIT',flowFrequency:'FREQUENCY',flowProcess:'PROCESS',processingLens:'processing lens',passband:'Acoustic passband waveform',instant:'Instantaneous frequency',matched:'Matched-filter / autocorrelation response',loading:'Updating Python scientific model…',offline:'Scientific API unavailable',retry:'Retry',ready:'Python scientific core',mode:'Mode',cause:'Configured input',effect:'Derived visual response',configured:'Configured',derived:'Derived',intuition:'Physical intuition',inputResponse:'INPUT → RESPONSE',causeBody:'Pulse type, frequency, duration and bandwidth',effectBody:'Waveform, instantaneous frequency and matched-filter response',intuitionBody:'One configuration propagates through every view.'},
 'pt-BR':{back:'← Mapa do sistema',lab:'Laboratório de sinais',signal:'Sinal',focusPulse:'Pulso',focusFrequency:'Frequência',focusCompression:'Compressão',focusWaveform:'Forma de onda',kicker:'PED-D2 · PULSO E PROCESSAMENTO DE SINAL',title:'Altere o pulso transmitido e veja o mesmo estado científico transformar todas as visualizações.',subtitle:'As curvas abaixo vêm do modelo canônico de sinais em Python do HydroSIM. O React cuida apenas da interação e apresentação.',controls:'Controles do sinal',waveform:'Forma de onda',frequency:'Frequência central',duration:'Duração do pulso',bandwidth:'Largura de banda LFM',direction:'Direção da varredura',envelope:'Envoltória',up:'Ascendente',down:'Descendente',rectangular:'Retangular',tukey:'Tukey',reset:'Restaurar',transmit:'01 · TRANSMISSÃO',frequencyLens:'02 · VISÃO DE FREQUÊNCIA',process:'03 · PROCESSAMENTO',flowTransmit:'TRANSMISSÃO',flowFrequency:'FREQUÊNCIA',flowProcess:'PROCESSAMENTO',processingLens:'visão de processamento',passband:'Forma de onda acústica em banda passante',instant:'Frequência instantânea',matched:'Resposta de filtro casado / autocorrelação',loading:'Atualizando o modelo científico em Python…',offline:'API científica indisponível',retry:'Tentar novamente',ready:'Scientific Core em Python',mode:'Modo',cause:'Entrada configurada',effect:'Resposta visual derivada',configured:'Configurado',derived:'Derivado',intuition:'Intuição física',inputResponse:'ENTRADA → RESPOSTA',causeBody:'Tipo de pulso, frequência, duração e largura de banda',effectBody:'Forma de onda, frequência instantânea e resposta do filtro casado',intuitionBody:'Uma configuração se propaga por todas as visualizações.'}
} as const;

function tracePath(trace:Trace|undefined,width=760,height=180){
 if(!trace||trace.x.length<2||trace.x.length!==trace.y.length)return '';
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
 for(let i=0;i<trace.x.length;i++){minX=Math.min(minX,trace.x[i]);maxX=Math.max(maxX,trace.x[i]);minY=Math.min(minY,trace.y[i]);maxY=Math.max(maxY,trace.y[i]);}
 const dx=maxX-minX||1,dy=maxY-minY||1;
 return trace.x.map((x,i)=>`${i?'L':'M'} ${(((x-minX)/dx)*width).toFixed(2)} ${(height-((trace.y[i]-minY)/dy)*height).toFixed(2)}`).join(' ');
}

function ScientificTrace({trace,className='wave-path'}:{trace?:Trace;className?:string}){
 const d=useMemo(()=>tracePath(trace),[trace]);
 return <svg viewBox="0 0 760 180" preserveAspectRatio="none"><path className="gridline" d="M0 90H760"/><path className={className} d={d}/></svg>;
}

export default function SignalLab({onBack,focus}:{onBack:()=>void;focus?:string}){
 const[locale,setLocale]=useState<Locale>('en');
 const[config,setConfig]=useState<SignalConfig>(initial);
 const[data,setData]=useState<SignalResponse|null>(null);
 const[loading,setLoading]=useState(true);
 const[error,setError]=useState<string|null>(null);
 const[requestVersion,setRequestVersion]=useState(0);
 const t=text[locale];

 useEffect(()=>{
  const controller=new AbortController();
  const timer=window.setTimeout(async()=>{
   setLoading(true);setError(null);
   try{
    const response=await fetch(`${API_BASE}/api/v1/pedagogical/signal`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config),signal:controller.signal});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    setData(await response.json() as SignalResponse);
   }catch(err){if(!controller.signal.aborted)setError(err instanceof Error?err.message:String(err));}
   finally{if(!controller.signal.aborted)setLoading(false);}
  },90);
  return()=>{window.clearTimeout(timer);controller.abort();};
 },[config,requestVersion]);

 const patch=(next:Partial<SignalConfig>)=>setConfig(current=>({...current,...next}));
 const focusTitle=focus==='pulse'?t.focusPulse:focus==='spectrum'?t.focusFrequency:focus==='compression'?t.focusCompression:t.focusWaveform;
 const metadata=data?.metadata;

 return <div className={`signal-lab signal-focus-${focus??'waveform'}`}>
  <div className="lab-toolbar"><button className="back-button" onClick={onBack}>{t.back}</button><div className="lab-breadcrumb"><Activity size={17}/><span>{t.signal}</span><b>/</b><strong>{focusTitle}</strong></div><div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> {t.ready}</span><button onClick={()=>setLocale(value=>value==='en'?'pt-BR':'en')}>{locale==='en'?'PT-BR':'EN'}</button></div></div>
  <div className="lab-question"><span>{t.kicker}</span><h1>{t.title}</h1><p>{t.subtitle}</p></div>
  <div className="lab-layout"><aside className="control-surface"><div className="control-title"><SlidersHorizontal size={17}/><strong>{t.controls}</strong></div>
   <label>{t.waveform}<div className="segmented"><button className={config.pulse_type==='cw'?'on':''} onClick={()=>patch({pulse_type:'cw'})}>CW</button><button className={config.pulse_type==='lfm'?'on':''} onClick={()=>patch({pulse_type:'lfm'})}>LFM / Chirp</button></div></label>
   <label>{t.frequency} <output>{config.center_frequency_khz.toFixed(0)} kHz</output><input type="range" min="50" max="700" step="10" value={config.center_frequency_khz} onChange={e=>patch({center_frequency_khz:+e.target.value})}/></label>
   <label>{t.duration} <output>{config.duration_ms.toFixed(1)} ms</output><input type="range" min="0.1" max="5" step="0.1" value={config.duration_ms} onChange={e=>patch({duration_ms:+e.target.value})}/></label>
   <label className={config.pulse_type==='cw'?'disabled-control':''}>{t.bandwidth} <output>{config.bandwidth_khz.toFixed(0)} kHz</output><input disabled={config.pulse_type==='cw'} type="range" min="10" max="300" step="10" value={config.bandwidth_khz} onChange={e=>patch({bandwidth_khz:+e.target.value})}/></label>
   <label className={config.pulse_type==='cw'?'disabled-control':''}>{t.direction}<div className="segmented"><button disabled={config.pulse_type==='cw'} className={config.chirp_direction==='up'?'on':''} onClick={()=>patch({chirp_direction:'up'})}>{t.up}</button><button disabled={config.pulse_type==='cw'} className={config.chirp_direction==='down'?'on':''} onClick={()=>patch({chirp_direction:'down'})}>{t.down}</button></div></label>
   <label>{t.envelope}<div className="segmented"><button className={config.envelope_model==='rectangular'?'on':''} onClick={()=>patch({envelope_model:'rectangular'})}>{t.rectangular}</button><button className={config.envelope_model==='tukey'?'on':''} onClick={()=>patch({envelope_model:'tukey'})}>{t.tukey}</button></div></label>
   <div className="control-readouts"><div><small>{t.mode}</small><strong>{config.pulse_type==='lfm'?'LFM':'CW'}</strong></div><div><small>f₀</small><strong>{config.center_frequency_khz.toFixed(0)} kHz</strong></div><div><small>τ</small><strong>{config.duration_ms.toFixed(1)} ms</strong></div><div><small>B</small><strong>{config.pulse_type==='lfm'?`${config.bandwidth_khz.toFixed(0)} kHz`:'—'}</strong></div></div>
   <button className="reset" onClick={()=>setConfig(initial)}><RotateCcw size={15}/> {t.reset}</button>
   {loading&&<div className="scientific-status">{t.loading}</div>}{error&&<div className="scientific-error"><strong>{t.offline}</strong><span>{error}</span><button onClick={()=>setRequestVersion(v=>v+1)}>{t.retry}</button></div>}
  </aside>
  <section className="visual-chain signal-continuous"><div className="signal-flow-label"><span>{t.flowTransmit}</span><i/><span>{t.flowFrequency}</span><i/><span>{t.flowProcess}</span></div>
   <div className="chain-card transmit"><header><div><small>{t.transmit}</small><strong>{t.passband}</strong></div><span>{config.pulse_type==='lfm'?'LFM':'CW'}</span></header><ScientificTrace trace={data?.waveform}/><div className="trace-units"><span>{data?.waveform.x_unit??'ms'}</span><span>{data?.waveform.y_unit??''}</span></div></div>
   <div className="chain-arrow"><span>{t.effect}</span><i>→</i></div>
   <div className="chain-card receive"><header><div><small>{t.frequencyLens}</small><strong>{t.instant}</strong></div><span>{metadata?.chirp_direction??'—'}</span></header><ScientificTrace trace={data?.instantaneous_frequency} className="echo-path"/><div className="trace-units"><span>{data?.instantaneous_frequency.x_unit??'ms'}</span><span>{data?.instantaneous_frequency.y_unit??'kHz'}</span></div></div>
   <div className="chain-arrow"><span>{t.processingLens}</span><i>→</i></div>
   <div className="chain-card compression"><header><div><small>{t.process}</small><strong>{t.matched}</strong></div><span>{t.derived.toUpperCase()}</span></header><ScientificTrace trace={data?.matched_filter}/><div className="trace-units"><span>{data?.matched_filter.x_unit??'us'}</span><span>{data?.matched_filter.y_unit??''}</span></div><div className="insight"><Waves size={18}/><span>{t.intuitionBody}</span></div></div>
  </section></div>
  <div className="causal-strip signal-causal"><div><small>{t.cause}</small><strong>{t.configured}</strong><span>{t.causeBody}</span></div><div><small>{t.effect}</small><strong>{t.derived}</strong><span>{t.effectBody}</span></div><div><small>{t.intuition}</small><strong>{t.inputResponse}</strong><span>{t.intuitionBody}</span></div></div>
 </div>;
}
