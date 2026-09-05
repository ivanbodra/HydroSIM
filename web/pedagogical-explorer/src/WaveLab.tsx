import { Activity, RotateCcw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Locale='en'|'pt-BR';
type TraceSeries={x:number[];y:number[];x_unit:string;y_unit:string};
type WaveResponse={period_seconds:number;wavelength_m:number;temporal_waveform:TraceSeries;spatial_waveform:TraceSeries;range_offset_m:number|null;metadata:Record<string,number|string>};
type Domain={min:number;max:number};

const API_BASE=(import.meta.env.VITE_HYDROSIM_API_BASE as string|undefined)??'http://127.0.0.1:8000';
const TIME_DOMAIN:Domain={min:0,max:.014};
const SPACE_DOMAIN:Domain={min:0,max:.04};
const AMP_DOMAIN:Domain={min:-1.05,max:1.05};
const copy={
 en:{back:'← System map',kicker:'PED-D1 · ACOUSTIC WAVE & FREQUENCY',frequency:'Frequency',soundSpeed:'Sound speed',phase:'Initial phase',amplitude:'Normalized amplitude',time:'Wave in time',space:'Wave in space',period:'Period',wavelength:'Wavelength',reset:'Reset',updating:'Updating…',unavailable:'Scientific API unavailable',retry:'Retry',timeAxis:'Time (ms)',spaceAxis:'Distance (m)',amplitudeAxis:'Normalized amplitude',relation:'Wave relations'},
 'pt-BR':{back:'← Mapa do sistema',kicker:'PED-D1 · ONDA ACÚSTICA E FREQUÊNCIA',frequency:'Frequência',soundSpeed:'Velocidade do som',phase:'Fase inicial',amplitude:'Amplitude normalizada',time:'Onda no tempo',space:'Onda no espaço',period:'Período',wavelength:'Comprimento de onda',reset:'Redefinir',updating:'Atualizando…',unavailable:'API científica indisponível',retry:'Tentar novamente',timeAxis:'Tempo (ms)',spaceAxis:'Distância (m)',amplitudeAxis:'Amplitude normalizada',relation:'Relações da onda'}
} as const;

function tracePath(series:TraceSeries|undefined,xDomain:Domain,width=760,height=190){
 if(!series||series.x.length<2||series.x.length!==series.y.length)return'';
 const dx=xDomain.max-xDomain.min,dy=AMP_DOMAIN.max-AMP_DOMAIN.min;
 return series.x.map((x,i)=>`${i?'L':'M'} ${(((x-xDomain.min)/dx)*width).toFixed(2)} ${(height-((series.y[i]-AMP_DOMAIN.min)/dy)*height).toFixed(2)}`).join(' ')
}
function Trace({series,label,xDomain,xTicks,xAxis,amplitudeAxis}:{series?:TraceSeries;label:string;xDomain:Domain;xTicks:string[];xAxis:string;amplitudeAxis:string}){
 const d=useMemo(()=>tracePath(series,xDomain),[series,xDomain.min,xDomain.max]);
 return <div className="wave-trace"><div><strong>{label}</strong></div><div className="wave-chart-frame"><span className="wave-y-label">{amplitudeAxis}</span><svg viewBox="0 0 760 220" preserveAspectRatio="none" role="img" aria-label={`${label}. ${xAxis}; ${amplitudeAxis}.`}><path className="wave-axis" d="M0 95H760"/><path className="wave-line" d={d}/>{xTicks.map((tick,i)=><text key={tick} x={i===0?0:i===xTicks.length-1?710:350} y="214" className="wave-tick">{tick}</text>)}</svg><span className="wave-x-label">{xAxis}</span></div></div>
}

export default function WaveLab({onBack}:{onBack:()=>void}){
 const[locale,setLocale]=useState<Locale>('en');const[frequency,setFrequency]=useState(200);const[soundSpeed,setSoundSpeed]=useState(1500);const[phase,setPhase]=useState(0);const[amplitude,setAmplitude]=useState(1);const[data,setData]=useState<WaveResponse|null>(null);const[loading,setLoading]=useState(false);const[error,setError]=useState(false);const[retryNonce,setRetryNonce]=useState(0);const t=copy[locale];
 useEffect(()=>{const controller=new AbortController();const timer=window.setTimeout(async()=>{setLoading(true);setError(false);try{const displayCycles=frequency*TIME_DOMAIN.max;const r=await fetch(`${API_BASE}/api/v1/pedagogical/wave-kinematics`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({frequency_khz:frequency,sound_speed_mps:soundSpeed,normalized_amplitude:amplitude,initial_phase_rad:phase,sample_count:900,display_cycles:displayCycles,snapshot_time_fraction_of_period:0}),signal:controller.signal});if(!r.ok)throw new Error(String(r.status));setData(await r.json())}catch(e){if((e as Error).name!=='AbortError')setError(true)}finally{setLoading(false)}},80);return()=>{controller.abort();window.clearTimeout(timer)}},[frequency,soundSpeed,phase,amplitude,retryNonce]);
 const reset=()=>{setFrequency(200);setSoundSpeed(1500);setPhase(0);setAmplitude(1)};
 return <main className="wave-lab"><header className="wave-toolbar"><button onClick={onBack}>{t.back}</button><span>HydroSIM / PED-D1</span><div><button className={locale==='en'?'active':''} onClick={()=>setLocale('en')}>EN</button><button className={locale==='pt-BR'?'active':''} onClick={()=>setLocale('pt-BR')}>PT-BR</button></div></header><section className="wave-question"><span>{t.kicker}</span></section><div className="wave-layout"><aside className="wave-controls"><div className="wave-control-title"><Activity size={17}/><strong>{t.relation}</strong></div><label>{t.frequency}<output>{frequency} kHz</output><input type="range" min="20" max="700" step="10" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label><label>{t.soundSpeed}<output>{soundSpeed} m/s</output><input type="range" min="1400" max="1600" step="5" value={soundSpeed} onChange={e=>setSoundSpeed(+e.target.value)}/></label><label>{t.amplitude}<output>{amplitude.toFixed(1)}</output><input type="range" min="0" max="1" step="0.1" value={amplitude} onChange={e=>setAmplitude(+e.target.value)}/></label><label>{t.phase}<output>{phase.toFixed(2)} rad</output><input type="range" min="-3.14" max="3.14" step="0.1" value={phase} onChange={e=>setPhase(+e.target.value)}/></label><div className="wave-equations"><strong>c = fλ</strong><span>λ = c/f</span><span>p(x,t) = p₀e<sup>i(kx−ωt+φ)</sup></span><div><small>{t.period}</small><b>{data?(data.period_seconds*1e6).toFixed(2):'—'} µs</b><small>{t.wavelength}</small><b>{data?data.wavelength_m.toFixed(4):'—'} m</b></div></div><button className="wave-reset" onClick={reset}><RotateCcw size={15}/>{t.reset}</button>{loading&&<small className="wave-status">{t.updating}</small>}{error&&<button className="wave-error" onClick={()=>setRetryNonce(v=>v+1)}>{t.unavailable} · {t.retry}</button>}</aside><section className="wave-stage"><div className="wave-canvas"><Trace series={data?.temporal_waveform} label={t.time} xDomain={TIME_DOMAIN} xTicks={['0','0.007','0.014']} xAxis={t.timeAxis} amplitudeAxis={t.amplitudeAxis}/><Trace series={data?.spatial_waveform} label={t.space} xDomain={SPACE_DOMAIN} xTicks={['0','0.020','0.040']} xAxis={t.spaceAxis} amplitudeAxis={t.amplitudeAxis}/></div></section></div></main>
}
