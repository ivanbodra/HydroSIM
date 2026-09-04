import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Languages, LocateFixed } from 'lucide-react';

type Language = 'en' | 'pt';
type Method = 'amplitude_peak' | 'phase_zero_crossing';
type Response = {
  status: 'detected' | 'unsupported';
  correlation: { lag_us: number[]; magnitude: number[] };
  selected_detection: null | {
    detection_method: Method;
    peak_index: number | null;
    peak_lag_samples: number | null;
    arrival_offset_ms: number;
    tx_delay_ms: number;
    twtt_ms: number;
    detected_across_track_angle_deg: number | null;
    normalized_amplitude: number | null;
    quality: number | null;
  };
  unsupported_reason: string | null;
};

const copy = {
  en: { title:'Bottom Detection', intro:'Change the detector inputs and watch the selected echo move on the matched-filter trace.', back:'System Map', lang:'PT-BR', scenario:'Echo scenario', clean:'Single clear echo', late:'Later echo', double:'Competing echoes', delay:'TX delay', steering:'Steering angle', method:'Detection method', amp:'Amplitude peak', phase:'Phase zero crossing', trace:'Matched-filter magnitude', selected:'Selected detection', twtt:'TWTT', arrival:'Arrival offset', angle:'Detected angle', unsupported:'Not available in the canonical detector yet', intuition:'Physical intuition', insight:'The detector does not create a sounding; it selects a candidate echo and converts its lag into timing information.' },
  pt: { title:'Detecção do Fundo', intro:'Altere as entradas do detector e observe o eco selecionado se deslocar no traço do filtro casado.', back:'Mapa do Sistema', lang:'EN', scenario:'Cenário de eco', clean:'Um eco nítido', late:'Eco mais tardio', double:'Ecos concorrentes', delay:'Atraso de TX', steering:'Ângulo de steering', method:'Método de detecção', amp:'Pico de amplitude', phase:'Cruzamento de fase por zero', trace:'Magnitude do filtro casado', selected:'Detecção selecionada', twtt:'TWTT', arrival:'Offset de chegada', angle:'Ângulo detectado', unsupported:'Ainda não disponível no detector canônico', intuition:'Intuição física', insight:'O detector não cria uma sondagem; ele seleciona um eco candidato e converte seu atraso em informação temporal.' }
};

const scenarios = {
  clean:[0,0.02,0.08,0.2,0.72,1,0.55,0.18,0.05,0.01],
  late:[0,0.01,0.03,0.06,0.11,0.22,0.48,0.92,1,0.4],
  double:[0,0.04,0.2,0.76,0.45,0.18,0.38,1,0.5,0.08]
};

export default function BottomDetectionLab({onBack}:{onBack:()=>void}) {
  const [language,setLanguage]=useState<Language>('en');
  const [scenario,setScenario]=useState<keyof typeof scenarios>('clean');
  const [txDelay,setTxDelay]=useState(0.2);
  const [steering,setSteering]=useState(0);
  const [method,setMethod]=useState<Method>('amplitude_peak');
  const [data,setData]=useState<Response|null>(null);
  const [error,setError]=useState('');
  const t=copy[language];
  useEffect(()=>{
    const controller=new AbortController();
    setError('');
    fetch('/api/v1/pedagogical/bottom-detection',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({correlation_real:scenarios[scenario],reference_sample_count:2,sample_rate_hz:40000,tx_delay_ms:txDelay,steering_across_track_angle_deg:steering,detection_method:method})})
      .then(async r=>{if(!r.ok) throw new Error(await r.text()); return r.json() as Promise<Response>})
      .then(setData).catch(e=>{if(e.name!=='AbortError')setError(String(e))});
    return()=>controller.abort();
  },[scenario,txDelay,steering,method]);
  const maxMag=useMemo(()=>Math.max(...(data?.correlation.magnitude??[1]),1e-9),[data]);
  const selectedLag=data?.selected_detection?.peak_index!=null?data.correlation.lag_us[data.selected_detection.peak_index]:null;
  return <div className="d9-lab">
    <header className="d9-head"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><span>PED-D9 · ACQUISITION CHAIN</span><h1>{t.title}</h1><p>{t.intro}</p></div><button onClick={()=>setLanguage(language==='en'?'pt':'en')}><Languages size={16}/>{t.lang}</button></header>
    <main className="d9-layout">
      <aside className="d9-controls">
        <label>{t.scenario}<select value={scenario} onChange={e=>setScenario(e.target.value as keyof typeof scenarios)}><option value="clean">{t.clean}</option><option value="late">{t.late}</option><option value="double">{t.double}</option></select></label>
        <label>{t.delay}<strong>{txDelay.toFixed(2)} ms</strong><input type="range" min="0" max="2" step="0.05" value={txDelay} onChange={e=>setTxDelay(Number(e.target.value))}/></label>
        <label>{t.steering}<strong>{steering.toFixed(0)}°</strong><input type="range" min="-60" max="60" step="5" value={steering} onChange={e=>setSteering(Number(e.target.value))}/></label>
        <label>{t.method}<select value={method} onChange={e=>setMethod(e.target.value as Method)}><option value="amplitude_peak">{t.amp}</option><option value="phase_zero_crossing">{t.phase}</option></select></label>
      </aside>
      <section className="d9-stage">
        <div className="d9-stage-title"><div><small>{t.trace}</small><strong>INPUT → DETECTION → TIMING</strong></div>{data?.selected_detection&&<div className="d9-selected"><LocateFixed size={16}/>{t.selected}</div>}</div>
        {error?<div className="d9-message">{error}</div>:data?.status==='unsupported'?<div className="d9-message"><strong>{t.unsupported}</strong><span>{data.unsupported_reason}</span></div>:<div className="d9-chart" aria-label={t.trace}>{data?.correlation.magnitude.map((m,i)=>{const active=data.selected_detection?.peak_index===i;return <div key={i} className={`d9-sample ${active?'active':''}`} style={{height:`${8+82*m/maxMag}%`}}><span>{active?'▲':''}</span></div>})}<div className="d9-axis">{data?.correlation.lag_us.map((lag,i)=><span key={i}>{i%2===0?`${lag.toFixed(0)} µs`:''}</span>)}</div></div>}
        <div className="d9-readouts"><div><small>{t.twtt}</small><strong>{data?.selected_detection?`${data.selected_detection.twtt_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.arrival}</small><strong>{data?.selected_detection?`${data.selected_detection.arrival_offset_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.angle}</small><strong>{data?.selected_detection?.detected_across_track_angle_deg!=null?`${data.selected_detection.detected_across_track_angle_deg.toFixed(0)}°`:'—'}</strong></div><div><small>Peak lag</small><strong>{selectedLag!=null?`${selectedLag.toFixed(0)} µs`:'—'}</strong></div></div>
        <div className="d9-intuition"><small>{t.intuition}</small><p>{t.insight}</p></div>
      </section>
    </main>
  </div>;
}
