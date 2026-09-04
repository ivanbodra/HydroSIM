import { RotateCcw, SlidersHorizontal } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type PulseType='cw'|'lfm';
type ChirpDirection='up'|'down';
type EnvelopeModel='rectangular'|'tukey';
type Trace={x:number[];y:number[];x_unit:string;y_unit:string};
type SignalResponse={pulse_type:PulseType;waveform:Trace;instantaneous_frequency:Trace;matched_filter:Trace;metadata:Record<string,number|string>};
type Locale='en'|'pt-BR';
type Domain={min:number;max:number};
type SignalConfig={pulse_type:PulseType;center_frequency_khz:number;duration_ms:number;bandwidth_khz:number;chirp_direction:ChirpDirection;envelope_model:EnvelopeModel};

const API_BASE=(import.meta.env.VITE_HYDROSIM_API_BASE as string|undefined)??'http://127.0.0.1:8000';
const initial:SignalConfig={pulse_type:'lfm',center_frequency_khz:200,duration_ms:1,bandwidth_khz:100,chirp_direction:'up',envelope_model:'rectangular'};
const TIME_DOMAIN:Domain={min:0,max:5};
const WAVE_DOMAIN:Domain={min:-1.05,max:1.05};
const FREQUENCY_DOMAIN:Domain={min:0,max:850};
const MATCHED_LAG_DOMAIN:Domain={min:-5000,max:5000};
const MATCHED_DOMAIN:Domain={min:-1.05,max:1.05};

const text={
 en:{back:'← System map',signal:'Signal',focusPulse:'Pulse',focusFrequency:'Frequency',focusCompression:'Compression',focusWaveform:'Waveform',kicker:'PED-D2 · PULSE & SIGNAL PROCESSING',title:'Change the transmitted pulse and observe the signal response.',controls:'Signal controls',waveform:'Waveform',frequency:'Centre frequency',duration:'Pulse duration',bandwidth:'LFM bandwidth',direction:'Sweep direction',envelope:'Envelope',up:'Up',down:'Down',rectangular:'Rectangular',tukey:'Tukey',reset:'Reset',passband:'Acoustic waveform',instant:'Instantaneous frequency',matched:'Matched-filter response',loading:'Updating…',offline:'Signal response unavailable',retry:'Retry',mode:'Mode',timeAxis:'Time (ms)',amplitudeAxis:'Normalized amplitude',frequencyAxis:'Frequency (kHz)',lagAxis:'Lag (µs)'},
 'pt-BR':{back:'← Mapa do sistema',signal:'Sinal',focusPulse:'Pulso',focusFrequency:'Frequência',focusCompression:'Compressão',focusWaveform:'Forma de onda',kicker:'PED-D2 · PULSO E PROCESSAMENTO DE SINAL',title:'Altere o pulso transmitido e observe a resposta do sinal.',controls:'Controles do sinal',waveform:'Forma de onda',frequency:'Frequência central',duration:'Duração do pulso',bandwidth:'Largura de banda LFM',direction:'Direção da varredura',envelope:'Envoltória',up:'Ascendente',down:'Descendente',rectangular:'Retangular',tukey:'Tukey',reset:'Restaurar',passband:'Forma de onda acústica',instant:'Frequência instantânea',matched:'Resposta do filtro casado',loading:'Atualizando…',offline:'Resposta do sinal indisponível',retry:'Tentar novamente',mode:'Modo',timeAxis:'Tempo (ms)',amplitudeAxis:'Amplitude normalizada',frequencyAxis:'Frequência (kHz)',lagAxis:'Atraso (µs)'}
} as const;

function tracePath(trace:Trace|undefined,xDomain:Domain,yDomain:Domain,width=760,height=180){
 if(!trace||trace.x.length<2||trace.x.length!==trace.y.length)return '';
 const dx=xDomain.max-xDomain.min||1,dy=yDomain.max-yDomain.min||1;
 return trace.x.map((x,i)=>{
  const px=((x-xDomain.min)/dx)*width;
  const py=height-((trace.y[i]-yDomain.min)/dy)*height;
  return `${i?'L':'M'} ${px.toFixed(2)} ${py.toFixed(2)}`;
 }).join(' ');
}

function Plot({trace,xDomain,yDomain,xTicks,yTicks,xLabel,yLabel,className='wave-path',pulseEnd}:{trace?:Trace;xDomain:Domain;yDomain:Domain;xTicks:string[];yTicks:string[];xLabel:string;yLabel:string;className?:string;pulseEnd?:number}){
 const d=useMemo(()=>tracePath(trace,xDomain,yDomain),[trace,xDomain.min,xDomain.max,yDomain.min,yDomain.max]);
 const pulsePosition=pulseEnd===undefined?null:Math.max(0,Math.min(100,((pulseEnd-xDomain.min)/(xDomain.max-xDomain.min))*100));
 return <div className="scientific-plot clean-plot">
  <div className="plot-y-label">{yLabel}</div>
  <div className="plot-y-ticks"><span>{yTicks[0]}</span><span>{yTicks[1]}</span><span>{yTicks[2]}</span></div>
  <svg viewBox="0 0 760 180" preserveAspectRatio="none" aria-hidden="true">
   <path className="plot-grid" d="M0 45H760 M0 90H760 M0 135H760 M190 0V180 M380 0V180 M570 0V180"/>
   <path className="gridline" d="M0 90H760"/>
   <path className={className} d={d}/>
  </svg>
  {pulsePosition!==null&&pulseEnd!==undefined&&pulseEnd<=xDomain.max&&<div className="pulse-duration-marker" style={{left:`${pulsePosition}%`}}><i/><span>{pulseEnd.toFixed(1)} ms</span></div>}
  <div className="fixed-axis">{xTicks.map(v=><span key={v}>{v}</span>)}</div>
  <div className="plot-x-label">{xLabel}</div>
 </div>;
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
   try{const response=await fetch(`${API_BASE}/api/v1/pedagogical/signal`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config),signal:controller.signal});if(!response.ok)throw new Error(`HTTP ${response.status}`);setData(await response.json() as SignalResponse)}
   catch(err){if(!controller.signal.aborted)setError(err instanceof Error?err.message:String(err))}
   finally{if(!controller.signal.aborted)setLoading(false)}
  },90);
  return()=>{window.clearTimeout(timer);controller.abort()};
 },[config,requestVersion]);
 const patch=(next:Partial<SignalConfig>)=>setConfig(current=>({...current,...next}));
 const focusTitle=focus==='pulse'?t.focusPulse:focus==='spectrum'?t.focusFrequency:focus==='compression'?t.focusCompression:t.focusWaveform;
 return <div className={`signal-lab signal-focus-${focus??'waveform'}`}>
  <div className="lab-toolbar"><button className="back-button" onClick={onBack}>{t.back}</button><div className="lab-breadcrumb"><span>{t.signal}</span><b>/</b><strong>{focusTitle}</strong></div><div className="lab-toolbar-actions"><button onClick={()=>setLocale(value=>value==='en'?'pt-BR':'en')}>{locale==='en'?'PT-BR':'EN'}</button></div></div>
  <div className="lab-question"><span>{t.kicker}</span><h1>{t.title}</h1></div>
  <div className="lab-layout"><aside className="control-surface"><div className="control-title"><SlidersHorizontal size={17}/><strong>{t.controls}</strong></div>
   <label>{t.waveform}<div className="segmented"><button className={config.pulse_type==='cw'?'on':''} onClick={()=>patch({pulse_type:'cw'})}>CW</button><button className={config.pulse_type==='lfm'?'on':''} onClick={()=>patch({pulse_type:'lfm'})}>LFM / Chirp</button></div></label>
   <label>{t.frequency} <output>{config.center_frequency_khz.toFixed(0)} kHz</output><input type="range" min="50" max="700" step="10" value={config.center_frequency_khz} onChange={e=>patch({center_frequency_khz:+e.target.value})}/></label>
   <label>{t.duration} <output>{config.duration_ms.toFixed(1)} ms</output><input type="range" min="0.1" max="5" step="0.1" value={config.duration_ms} onChange={e=>patch({duration_ms:+e.target.value})}/></label>
   <label className={config.pulse_type==='cw'?'disabled-control':''}>{t.bandwidth} <output>{config.bandwidth_khz.toFixed(0)} kHz</output><input disabled={config.pulse_type==='cw'} type="range" min="10" max="300" step="10" value={config.bandwidth_khz} onChange={e=>patch({bandwidth_khz:+e.target.value})}/></label>
   <label className={config.pulse_type==='cw'?'disabled-control':''}>{t.direction}<div className="segmented"><button disabled={config.pulse_type==='cw'} className={config.chirp_direction==='up'?'on':''} onClick={()=>patch({chirp_direction:'up'})}>{t.up}</button><button disabled={config.pulse_type==='cw'} className={config.chirp_direction==='down'?'on':''} onClick={()=>patch({chirp_direction:'down'})}>{t.down}</button></div></label>
   <label>{t.envelope}<div className="segmented"><button className={config.envelope_model==='rectangular'?'on':''} onClick={()=>patch({envelope_model:'rectangular'})}>{t.rectangular}</button><button className={config.envelope_model==='tukey'?'on':''} onClick={()=>patch({envelope_model:'tukey'})}>{t.tukey}</button></div></label>
   <div className="control-readouts"><div><small>{t.mode}</small><strong>{config.pulse_type==='lfm'?'LFM':'CW'}</strong></div><div><small>f₀</small><strong>{config.center_frequency_khz.toFixed(0)} kHz</strong></div><div><small>τ</small><strong>{config.duration_ms.toFixed(1)} ms</strong></div><div><small>B</small><strong>{config.pulse_type==='lfm'?`${config.bandwidth_khz.toFixed(0)} kHz`:'—'}</strong></div></div>
   <button className="reset" onClick={()=>setConfig(initial)}><RotateCcw size={15}/> {t.reset}</button>
   {loading&&<div className="scientific-status">{t.loading}</div>}{error&&<div className="scientific-error"><strong>{t.offline}</strong><button onClick={()=>setRequestVersion(v=>v+1)}>{t.retry}</button></div>}
  </aside>
  <section className="visual-chain signal-continuous clean-signal-plots">
   <div className="chain-card transmit"><header><div><strong>{t.passband}</strong></div><span>{config.pulse_type==='lfm'?'LFM':'CW'}</span></header><Plot trace={data?.waveform} xDomain={TIME_DOMAIN} yDomain={WAVE_DOMAIN} pulseEnd={config.duration_ms} xTicks={['0','2.5','5']} yTicks={['+1','0','−1']} xLabel={t.timeAxis} yLabel={t.amplitudeAxis}/></div>
   <div className="chain-card receive"><header><div><strong>{t.instant}</strong></div><span>{config.pulse_type==='lfm'?config.chirp_direction.toUpperCase():'CW'}</span></header><Plot trace={data?.instantaneous_frequency} xDomain={TIME_DOMAIN} yDomain={FREQUENCY_DOMAIN} pulseEnd={config.duration_ms} className="echo-path" xTicks={['0','2.5','5']} yTicks={['850','425','0']} xLabel={t.timeAxis} yLabel={t.frequencyAxis}/></div>
   <div className="chain-card compression"><header><div><strong>{t.matched}</strong></div></header><Plot trace={data?.matched_filter} xDomain={MATCHED_LAG_DOMAIN} yDomain={MATCHED_DOMAIN} xTicks={['−5000','0','+5000']} yTicks={['+1','0','−1']} xLabel={t.lagAxis} yLabel={t.amplitudeAxis}/></div>
  </section></div>
 </div>;
}
