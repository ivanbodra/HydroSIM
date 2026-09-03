import { AlertTriangle, ArrowLeft, Languages, RotateCcw, Target } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Lang = 'en' | 'pt';
type Pattern = { angle_deg:number[]; normalized_power:number[] };
type Response = {
  wavelength_m:number;
  physical_aperture_m:number;
  element_positions_m:number[];
  element_factor:Pattern;
  array_factor:Pattern;
  combined_pattern:Pattern;
  peak_angle_deg:number;
  peak_normalized_power:number;
  half_power_beamwidth_deg:number|null;
  metadata:Record<string,string|number>;
};

const copy = {
  en: {
    back:'System map', title:'Build the aperture and watch the beam emerge.',
    sub:'Frequency, element size, spacing and count change the canonical one-way directivity without any frontend beam equation.',
    configured:'Configured', derived:'Derived', frequency:'Frequency', speed:'Sound speed', count:'Element count', spacing:'Element spacing', face:'Element face',
    reset:'Reset', loading:'Evaluating canonical directivity…', retry:'Retry', wavelength:'Wavelength', aperture:'Physical aperture', beamwidth:'Half-power beamwidth', unavailable:'Unavailable in scan',
    peak:'Peak angle', construction:'Array construction', response:'Normalized one-way power', element:'Element factor', array:'Array factor', combined:'Combined pattern',
    boundary:'Ideal regular centred array, far field, monochromatic/narrowband evaluation, uniform weights and fixed broadside steering. No calibrated gain, mutual coupling or vendor beamformer behavior.',
    cause:'INPUT → ARRAY GEOMETRY / WAVELENGTH → INTERFERENCE + ELEMENT ENVELOPE → DIRECTIVITY', port:'Port', starboard:'Starboard'
  },
  pt: {
    back:'Mapa do sistema', title:'Construa a abertura e observe o feixe surgir.',
    sub:'Frequência, tamanho do elemento, espaçamento e quantidade alteram a diretividade canônica unidirecional sem nenhuma equação de feixe no frontend.',
    configured:'Configurado', derived:'Derivado', frequency:'Frequência', speed:'Velocidade do som', count:'Quantidade de elementos', spacing:'Espaçamento entre elementos', face:'Face do elemento',
    reset:'Redefinir', loading:'Calculando diretividade canônica…', retry:'Tentar novamente', wavelength:'Comprimento de onda', aperture:'Abertura física', beamwidth:'Largura de feixe a meia potência', unavailable:'Indisponível na varredura',
    peak:'Ângulo de pico', construction:'Construção do arranjo', response:'Potência unidirecional normalizada', element:'Fator do elemento', array:'Fator do arranjo', combined:'Padrão combinado',
    boundary:'Arranjo ideal regular e centrado, campo distante, avaliação monocromática/banda estreita, pesos uniformes e apontamento fixo para broadside. Sem ganho calibrado, acoplamento mútuo ou comportamento específico de fabricante.',
    cause:'ENTRADA → GEOMETRIA / COMPRIMENTO DE ONDA → INTERFERÊNCIA + ENVELOPE DO ELEMENTO → DIRETIVIDADE', port:'Bombordo', starboard:'Boreste'
  }
};

function chartPoints(pattern:Pattern, width=680, height=240){
  const minA=Math.min(...pattern.angle_deg), maxA=Math.max(...pattern.angle_deg);
  return pattern.angle_deg.map((a,i)=>{
    const x=((a-minA)/Math.max(maxA-minA,1))*width;
    const y=height-(Math.max(0,Math.min(1,pattern.normalized_power[i]??0))*height);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
}

export default function ArrayDirectivityLab({onBack}:{onBack:()=>void}){
  const [lang,setLang]=useState<Lang>('en');
  const [frequency,setFrequency]=useState(200);
  const [speed,setSpeed]=useState(1500);
  const [count,setCount]=useState(16);
  const [spacingMm,setSpacingMm]=useState(3.75);
  const [faceMm,setFaceMm]=useState(3);
  const [data,setData]=useState<Response|null>(null);
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);
  const [nonce,setNonce]=useState(0);
  const t=copy[lang];
  const request=useMemo(()=>({frequency_khz:frequency,sound_speed_mps:speed,element_count:count,element_spacing_m:spacingMm/1000,element_face_m:faceMm/1000,scan_min_deg:-80,scan_max_deg:80,sample_count:321}),[frequency,speed,count,spacingMm,faceMm]);
  useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');fetch('/api/v1/pedagogical/array-directivity',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(request),signal:controller.signal}).then(async r=>{if(!r.ok)throw new Error((await r.json()).detail??`HTTP ${r.status}`);return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(String(e.message??e))}).finally(()=>setLoading(false));return()=>controller.abort()},[request,nonce]);
  const extent=Math.max(...(data?.element_positions_m.map(Math.abs)??[1]),0.001);
  return <div className="array-directivity-lab">
    <header className="array-toolbar"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><Target size={18}/><strong>PED-D6 · Transducer & Array Construction</strong></div><button onClick={()=>setLang(v=>v==='en'?'pt':'en')}><Languages size={16}/>{lang==='en'?'PT-BR':'EN'}</button></header>
    <section className="array-question"><small>PED-D6 · VIRTUAL ARRAY LAB</small><h1>{t.title}</h1><p>{t.sub}</p></section>
    <div className="array-layout"><aside className="array-controls"><div className="state-label">{t.configured}</div>
      <label>{t.frequency}<output>{frequency} kHz</output><input aria-label={t.frequency} type="range" min="50" max="700" step="10" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label>
      <label>{t.speed}<output>{speed} m/s</output><input aria-label={t.speed} type="range" min="1450" max="1550" step="5" value={speed} onChange={e=>setSpeed(+e.target.value)}/></label>
      <label>{t.count}<output>{count}</output><input aria-label={t.count} type="range" min="1" max="64" step="1" value={count} onChange={e=>setCount(+e.target.value)}/></label>
      <label>{t.spacing}<output>{spacingMm.toFixed(2)} mm</output><input aria-label={t.spacing} type="range" min="0.5" max="15" step="0.25" value={spacingMm} onChange={e=>setSpacingMm(+e.target.value)}/></label>
      <label>{t.face}<output>{faceMm.toFixed(2)} mm</output><input aria-label={t.face} type="range" min="0.5" max="15" step="0.25" value={faceMm} onChange={e=>setFaceMm(+e.target.value)}/></label>
      <button className="array-reset" onClick={()=>{setFrequency(200);setSpeed(1500);setCount(16);setSpacingMm(3.75);setFaceMm(3)}}><RotateCcw size={15}/>{t.reset}</button><p className="array-boundary">{t.boundary}</p>
    </aside>
    <main className="array-stage"><div className="causal-title">{t.cause}</div>{loading&&!data&&<div className="array-message">{t.loading}</div>}{error&&<div className="array-error"><AlertTriangle size={18}/><span>{error}</span><button onClick={()=>setNonce(v=>v+1)}>{t.retry}</button></div>}{data&&<>
      <section className="array-construction"><div><small>{t.derived}</small><strong>{t.construction}</strong></div><div className="element-row" aria-label="Canonical element positions">{data.element_positions_m.map((p,i)=><i key={`${p}-${i}`} style={{left:`${50+(p/(extent*2))*82}%`}} title={`${p.toFixed(4)} m`}/>)}</div><div className="array-axis"><span>{t.starboard} (−)</span><b>0</b><span>{t.port} (+)</span></div></section>
      <div className="array-readouts"><div><small>{t.derived}</small><strong>{t.wavelength}</strong><output>{(data.wavelength_m*1000).toFixed(2)} mm</output></div><div><small>{t.derived}</small><strong>{t.aperture}</strong><output>{(data.physical_aperture_m*1000).toFixed(2)} mm</output></div><div><small>{t.derived}</small><strong>{t.beamwidth}</strong><output>{data.half_power_beamwidth_deg==null?t.unavailable:`${data.half_power_beamwidth_deg.toFixed(2)}°`}</output></div><div><small>{t.derived}</small><strong>{t.peak}</strong><output>{data.peak_angle_deg.toFixed(2)}°</output></div></div>
      <section className="directivity-panel"><div className="directivity-head"><div><small>{t.derived}</small><strong>{t.response}</strong></div><div className="directivity-legend"><span className="element">{t.element}</span><span className="array">{t.array}</span><span className="combined">{t.combined}</span></div></div><svg viewBox="0 0 680 240" role="img" aria-label="Canonical normalized one-way directivity patterns"><line x1="340" y1="0" x2="340" y2="240" className="chart-zero"/><polyline className="pattern element" points={chartPoints(data.element_factor)}/><polyline className="pattern array" points={chartPoints(data.array_factor)}/><polyline className="pattern combined" points={chartPoints(data.combined_pattern)}/></svg><div className="angle-axis"><span>−80°</span><span>0°</span><span>+80°</span></div></section>
    </>}</main></div>
  </div>;
}
