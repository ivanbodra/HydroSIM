import { AlertTriangle, ArrowLeft, Languages, RotateCcw, Radio, Waves } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Lang = 'en' | 'pt';
type Role = 'tx' | 'rx';
type Pattern = { angle_deg:number[]; normalized_power:number[] };
type ElementState = { index:number; position_y_m:number; steering_phase_re_broadside_rad:number; residual_phase_rad:number; contribution_real:number; contribution_imag:number };
type Response = {
  role:Role;
  wavelength_m:number;
  steering_angle_deg:number;
  source_angle_deg:number;
  steering_direction_array_frame:{x:number;y:number;z:number};
  source_direction_array_frame:{x:number;y:number;z:number};
  elements:ElementState[];
  evaluated_array_factor_magnitude:number;
  evaluated_array_factor_power:number;
  evaluated_physical_beam_power:number;
  coherent_sum_real:number;
  coherent_sum_imag:number;
  array_factor_pattern:Pattern;
  physical_beam_pattern:Pattern;
  peak_angle_deg:number;
  peak_normalized_power:number;
  half_power_beamwidth_deg:number|null;
  metadata:Record<string,string|number>;
};

const copy = {
  en:{back:'System map',title:'Steer the array and watch coherence move through space.',sub:'Choose a steering direction, compare it with the source direction, and inspect the canonical residual phases and one-way response returned by the Python Scientific Core.',configured:'Configured',derived:'Derived',frequency:'Frequency',speed:'Sound speed',count:'Element count',spacing:'Element spacing',face:'Element face',steer:'Steering angle',source:'Source angle',role:'Beamformer role',tx:'TX · transmit',rx:'RX · receive',reset:'Reset',loading:'Evaluating canonical beamforming…',retry:'Retry',wavelength:'Wavelength',peak:'Peak angle',beamwidth:'Half-power beamwidth',unavailable:'Unavailable in scan',arrayPower:'Array-factor power',physicalPower:'Physical beam power',coherent:'Coherent sum',elements:'Element coherence',pattern:'Steered one-way response',arrayFactor:'Array factor',physical:'Physical beam',phase:'Residual phase',contribution:'Contribution',port:'Port (+)',starboard:'Starboard (−)',cause:'INPUT → STEERING PHASE → COHERENT SUM → STEERED DIRECTIVITY',boundary:'Ideal static one-way reciprocal narrowband far-field model with uniform unit weights. TX and RX share the same normalized spatial law in this slice. No dynamic focusing, named apodization, calibrated gain or vendor-specific behavior.'},
  pt:{back:'Mapa do sistema',title:'Aponte o arranjo e observe a coerência se mover no espaço.',sub:'Escolha a direção de apontamento, compare-a com a direção da fonte e inspecione as fases residuais canônicas e a resposta unidirecional retornadas pelo núcleo científico em Python.',configured:'Configurado',derived:'Derivado',frequency:'Frequência',speed:'Velocidade do som',count:'Quantidade de elementos',spacing:'Espaçamento entre elementos',face:'Face do elemento',steer:'Ângulo de apontamento',source:'Ângulo da fonte',role:'Papel do beamformer',tx:'TX · transmissão',rx:'RX · recepção',reset:'Redefinir',loading:'Calculando beamforming canônico…',retry:'Tentar novamente',wavelength:'Comprimento de onda',peak:'Ângulo de pico',beamwidth:'Largura de feixe a meia potência',unavailable:'Indisponível na varredura',arrayPower:'Potência do fator de arranjo',physicalPower:'Potência do feixe físico',coherent:'Soma coerente',elements:'Coerência por elemento',pattern:'Resposta unidirecional apontada',arrayFactor:'Fator do arranjo',physical:'Feixe físico',phase:'Fase residual',contribution:'Contribuição',port:'Bombordo (+)',starboard:'Boreste (−)',cause:'ENTRADA → FASE DE APONTAMENTO → SOMA COERENTE → DIRETIVIDADE APONTADA',boundary:'Modelo ideal estático, recíproco, unidirecional, de banda estreita e campo distante, com pesos uniformes. TX e RX usam a mesma lei espacial normalizada neste recorte. Sem focalização dinâmica, apodização nomeada, ganho calibrado ou comportamento específico de fabricante.'}
};

function chartPoints(pattern:Pattern,width=680,height=230){
  const min=Math.min(...pattern.angle_deg),max=Math.max(...pattern.angle_deg);
  return pattern.angle_deg.map((a,i)=>`${(((a-min)/Math.max(max-min,1))*width).toFixed(1)},${(height-Math.max(0,Math.min(1,pattern.normalized_power[i]??0))*height).toFixed(1)}`).join(' ');
}

export default function BeamformingLab({onBack}:{onBack:()=>void}){
  const[lang,setLang]=useState<Lang>('en');
  const[frequency,setFrequency]=useState(200);const[speed,setSpeed]=useState(1500);const[count,setCount]=useState(16);const[spacingMm,setSpacingMm]=useState(3.75);const[faceMm,setFaceMm]=useState(3);const[steering,setSteering]=useState(20);const[source,setSource]=useState(20);const[role,setRole]=useState<Role>('tx');
  const[data,setData]=useState<Response|null>(null);const[loading,setLoading]=useState(false);const[error,setError]=useState('');const[nonce,setNonce]=useState(0);const t=copy[lang];
  const request=useMemo(()=>({frequency_khz:frequency,sound_speed_mps:speed,element_count:count,element_spacing_m:spacingMm/1000,element_face_m:faceMm/1000,steering_angle_deg:steering,source_angle_deg:source,scan_min_deg:-80,scan_max_deg:80,sample_count:321,role}),[frequency,speed,count,spacingMm,faceMm,steering,source,role]);
  useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');fetch('/api/v1/pedagogical/beamforming',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(request),signal:controller.signal}).then(async r=>{if(!r.ok)throw new Error((await r.json()).detail??`HTTP ${r.status}`);return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(String(e.message??e))}).finally(()=>setLoading(false));return()=>controller.abort()},[request,nonce]);
  const phaseMax=Math.max(...(data?.elements.map(e=>Math.abs(e.residual_phase_rad))??[1]),1e-6);
  return <div className="beamforming-lab"><header className="beamforming-toolbar"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><Radio size={18}/><strong>PED-D7 · Beamforming & Electronic Steering</strong></div><button onClick={()=>setLang(v=>v==='en'?'pt':'en')}><Languages size={16}/>{lang==='en'?'PT-BR':'EN'}</button></header>
    <section className="beamforming-question"><small>PED-D7 · VIRTUAL BEAMFORMER LAB</small><h1>{t.title}</h1><p>{t.sub}</p></section>
    <div className="beamforming-layout"><aside className="beamforming-controls"><div className="state-label">{t.configured}</div>
      <label>{t.role}<select value={role} onChange={e=>setRole(e.target.value as Role)}><option value="tx">{t.tx}</option><option value="rx">{t.rx}</option></select></label>
      <label>{t.frequency}<output>{frequency} kHz</output><input aria-label={t.frequency} type="range" min="50" max="700" step="10" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label>
      <label>{t.speed}<output>{speed} m/s</output><input aria-label={t.speed} type="range" min="1450" max="1550" step="5" value={speed} onChange={e=>setSpeed(+e.target.value)}/></label>
      <label>{t.count}<output>{count}</output><input aria-label={t.count} type="range" min="2" max="64" step="1" value={count} onChange={e=>setCount(+e.target.value)}/></label>
      <label>{t.spacing}<output>{spacingMm.toFixed(2)} mm</output><input aria-label={t.spacing} type="range" min="0.5" max="15" step="0.25" value={spacingMm} onChange={e=>setSpacingMm(+e.target.value)}/></label>
      <label>{t.face}<output>{faceMm.toFixed(2)} mm</output><input aria-label={t.face} type="range" min="0.5" max="15" step="0.25" value={faceMm} onChange={e=>setFaceMm(+e.target.value)}/></label>
      <label>{t.steer}<output>{steering>0?'+':''}{steering}°</output><input aria-label={t.steer} type="range" min="-70" max="70" step="1" value={steering} onChange={e=>setSteering(+e.target.value)}/></label>
      <label>{t.source}<output>{source>0?'+':''}{source}°</output><input aria-label={t.source} type="range" min="-70" max="70" step="1" value={source} onChange={e=>setSource(+e.target.value)}/></label>
      <button className="beamforming-reset" onClick={()=>{setFrequency(200);setSpeed(1500);setCount(16);setSpacingMm(3.75);setFaceMm(3);setSteering(20);setSource(20);setRole('tx')}}><RotateCcw size={15}/>{t.reset}</button><p className="beamforming-boundary">{t.boundary}</p>
    </aside>
    <main className="beamforming-stage"><div className="causal-title">{t.cause}</div>{loading&&!data&&<div className="beamforming-message">{t.loading}</div>}{error&&<div className="beamforming-error"><AlertTriangle size={18}/><span>{error}</span><button onClick={()=>setNonce(v=>v+1)}>{t.retry}</button></div>}{data&&<>
      <section className="steering-scene"><div className="steering-axis"><span>{t.starboard}</span><b>0°</b><span>{t.port}</span></div><div className="steering-rays"><i className="steer-ray" style={{transform:`rotate(${-data.steering_angle_deg}deg)`}}/><i className="source-ray" style={{transform:`rotate(${-data.source_angle_deg}deg)`}}/><span className="steer-label">STEER {data.steering_angle_deg>0?'+':''}{data.steering_angle_deg.toFixed(0)}°</span><span className="source-label">SOURCE {data.source_angle_deg>0?'+':''}{data.source_angle_deg.toFixed(0)}°</span></div></section>
      <div className="beamforming-readouts"><div><small>{t.derived}</small><strong>{t.wavelength}</strong><output>{(data.wavelength_m*1000).toFixed(2)} mm</output></div><div><small>{t.derived}</small><strong>{t.arrayPower}</strong><output>{data.evaluated_array_factor_power.toFixed(3)}</output></div><div><small>{t.derived}</small><strong>{t.physicalPower}</strong><output>{data.evaluated_physical_beam_power.toFixed(3)}</output></div><div><small>{t.derived}</small><strong>{t.peak}</strong><output>{data.peak_angle_deg.toFixed(2)}°</output></div><div><small>{t.derived}</small><strong>{t.beamwidth}</strong><output>{data.half_power_beamwidth_deg==null?t.unavailable:`${data.half_power_beamwidth_deg.toFixed(2)}°`}</output></div><div><small>{t.derived}</small><strong>{t.coherent}</strong><output>{data.coherent_sum_real.toFixed(2)} {data.coherent_sum_imag>=0?'+':'−'} j{Math.abs(data.coherent_sum_imag).toFixed(2)}</output></div></div>
      <section className="element-coherence"><div><small>{t.derived}</small><strong>{t.elements}</strong></div><div className="phase-strip">{data.elements.map(e=><div key={e.index} title={`${t.phase}: ${e.residual_phase_rad.toFixed(3)} rad · ${t.contribution}: ${e.contribution_real.toFixed(3)} + j${e.contribution_imag.toFixed(3)}`}><i style={{height:`${18+42*Math.abs(e.residual_phase_rad)/phaseMax}px`,transform:`rotate(${e.residual_phase_rad*18}deg)`}}/><span>{e.index+1}</span></div>)}</div></section>
      <section className="beamforming-pattern"><div className="beamforming-pattern-head"><div><small>{t.derived}</small><strong>{t.pattern}</strong></div><div><span className="array-factor">{t.arrayFactor}</span><span className="physical">{t.physical}</span></div></div><svg viewBox="0 0 680 230" role="img" aria-label="Canonical steered one-way beam patterns"><line x1="340" y1="0" x2="340" y2="230" className="chart-zero"/><polyline className="pattern array-factor" points={chartPoints(data.array_factor_pattern)}/><polyline className="pattern physical" points={chartPoints(data.physical_beam_pattern)}/></svg><div className="beamforming-angle-axis"><span>−80°</span><span>0°</span><span>+80°</span></div></section>
    </>}</main></div>
  </div>;
}
