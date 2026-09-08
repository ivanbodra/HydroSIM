import { useEffect, useMemo, useState } from 'react';
import { LocateFixed, RotateCcw } from 'lucide-react';

type Language = 'en' | 'pt';
type Method = 'amplitude_peak' | 'phase_zero_crossing';
type Candidate = {
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
type Classification = {
  classification: 'true_detection' | 'false_detection' | 'missed_detection';
  detection_lag_samples: number | null;
  truth_lag_samples: number | null;
};
type HighDensityDetection = {
  detection_index: number;
  detected_across_track_angle_deg: number;
  local_bottom_point_m: [number, number, number];
};
type HighDensityResponse = {
  status: 'disabled' | 'available' | 'unavailable';
  candidate_count: number;
  detections: HighDensityDetection[];
  comparison: {
    ordinary_detection_count: number;
    high_density_detection_count: number;
    density_multiplier: number;
    target_spacing_m: number | null;
    adjacent_spacing_m: number[];
  };
  unavailable_reason: string | null;
};
type Response = {
  status: 'detected' | 'unsupported';
  correlation: { lag_us: number[]; magnitude: number[]; normalized_magnitude: number[] };
  candidates: Candidate[];
  eligible_candidates: Candidate[];
  retained_detections: Candidate[];
  selected_detection: Candidate | null;
  classifications: Classification[];
  comparison: {
    eligible_candidate_count: number;
    single_detection_count: number;
    multiple_detection_count: number;
    retained_detection_count: number;
    detection_separation_samples: number[];
    detection_separation_ms: number[];
  };
  high_density: HighDensityResponse | null;
  unsupported_reason: string | null;
};

const WINDOW_MIN_US = -25;
const WINDOW_MAX_US = 200;
const HIGH_DENSITY_PHASE = [1.4547515713804893,0.730154243024546,0,-0.730154243024546,-1.4547515713804893];

const copy = {
  en: {
    chain:'INPUT → DETECTION → TIMING', reset:'Reset', scenario:'Echo scenario', clean:'Single clear echo', late:'Later echo', double:'Competing echoes',
    delay:'TX delay', steering:'Steering angle', method:'Detection method', amp:'Amplitude peak', phase:'Phase zero crossing', window:'Detection window',
    windowStart:'Window start', windowEnd:'Window end', windowHint:'Only echoes inside the highlighted time window can be selected.',
    threshold:'Detection threshold', thresholdHint:'Raise the threshold to reject weaker local peaks.', retention:'Retention', single:'Single detection', multiple:'Multiple detections',
    highDensity:'High Density', off:'Off', on:'On', highDensityHint:'Use phase information inside one receive-beam footprint to resolve additional bottom points.',
    hdComparison:'Ordinary × High Density', ordinaryPoints:'Ordinary points', hdPoints:'High Density points', densityGain:'Point-density gain', targetSpacing:'Target spacing',
    hdUnavailable:'High Density is unavailable for this phase support.', acrossTrack:'Across-track bottom points',
    trace:'Matched-filter magnitude', selected:'Selected detection', twtt:'TWTT', arrival:'Arrival offset', angle:'Detected angle', peakLag:'Peak lag',
    unsupported:'This detection method is not available yet', unsupportedDetail:'Phase zero crossing is not yet available in this lesson. Select Amplitude peak to continue exploring the detection.',
    relationship:'Detection outcome', transmit:'Transmit reference', echo:'Primary echo', sounding:'Timing passed downstream', noDetection:'No echo selected',
    eligible:'Eligible peaks', retained:'Retained', trueDet:'True', falseDet:'False', missedDet:'Missed', separation:'Detection separation',
    candidate:'candidate', retainedMark:'retained', rejectedMark:'eligible, not retained',
    error:'The detection view could not be updated. Adjust the controls or try again.'
  },
  pt: {
    chain:'ENTRADA → DETECÇÃO → TEMPO', reset:'Redefinir', scenario:'Cenário de eco', clean:'Um eco nítido', late:'Eco mais tardio', double:'Ecos concorrentes',
    delay:'Atraso de TX', steering:'Ângulo de steering', method:'Método de detecção', amp:'Pico de amplitude', phase:'Cruzamento de fase por zero', window:'Janela de detecção',
    windowStart:'Início da janela', windowEnd:'Fim da janela', windowHint:'Somente ecos dentro da janela de tempo destacada podem ser selecionados.',
    threshold:'Limiar de detecção', thresholdHint:'Eleve o limiar para rejeitar picos locais mais fracos.', retention:'Retenção', single:'Uma detecção', multiple:'Múltiplas detecções',
    highDensity:'High Density', off:'Desligado', on:'Ligado', highDensityHint:'Usa informação de fase dentro da pegada de um feixe de recepção para resolver pontos adicionais no fundo.',
    hdComparison:'Convencional × High Density', ordinaryPoints:'Pontos convencionais', hdPoints:'Pontos High Density', densityGain:'Ganho de densidade', targetSpacing:'Espaçamento-alvo',
    hdUnavailable:'High Density não está disponível para este suporte de fase.', acrossTrack:'Pontos do fundo na direção transversal',
    trace:'Magnitude do filtro casado', selected:'Detecção selecionada', twtt:'TWTT', arrival:'Offset de chegada', angle:'Ângulo detectado', peakLag:'Atraso do pico',
    unsupported:'Este método de detecção ainda não está disponível', unsupportedDetail:'O cruzamento de fase por zero ainda não está disponível nesta lição. Selecione Pico de amplitude para continuar explorando a detecção.',
    relationship:'Resultado da detecção', transmit:'Referência de transmissão', echo:'Eco principal', sounding:'Tempo enviado adiante', noDetection:'Nenhum eco selecionado',
    eligible:'Picos elegíveis', retained:'Retidos', trueDet:'Verdadeiras', falseDet:'Falsas', missedDet:'Perdidas', separation:'Separação entre detecções',
    candidate:'candidato', retainedMark:'retido', rejectedMark:'elegível, não retido',
    error:'Não foi possível atualizar a visualização da detecção. Ajuste os controles ou tente novamente.'
  }
};

const scenarios = {
  clean:[0,0.02,0.08,0.2,0.72,1,0.55,0.18,0.05,0.01],
  late:[0,0.01,0.03,0.06,0.11,0.22,0.48,0.92,1,0.4],
  double:[0,0.04,0.2,0.76,0.45,0.18,0.38,1,0.5,0.08]
};
const scenarioTruth: Record<keyof typeof scenarios, number[]> = {clean:[4],late:[7],double:[2,6]};
const initialLanguage=():Language=>sessionStorage.getItem('hydrosim-language')==='pt'?'pt':'en';

export default function BottomDetectionLab({onBack:_onBack}:{onBack:()=>void}) {
  const [language,setLanguage]=useState<Language>(initialLanguage);
  const [scenario,setScenario]=useState<keyof typeof scenarios>('clean');
  const [txDelay,setTxDelay]=useState(0.2);
  const [steering,setSteering]=useState(0);
  const [method,setMethod]=useState<Method>('amplitude_peak');
  const [windowStartUs,setWindowStartUs]=useState(WINDOW_MIN_US);
  const [windowEndUs,setWindowEndUs]=useState(WINDOW_MAX_US);
  const [threshold,setThreshold]=useState(0.5);
  const [multipleDetection,setMultipleDetection]=useState(false);
  const [highDensity,setHighDensity]=useState(false);
  const [data,setData]=useState<Response|null>(null);
  const [error,setError]=useState(false);
  const t=copy[language];

  useEffect(()=>{const sync=(event:Event)=>setLanguage((event as CustomEvent<string>).detail==='pt'?'pt':'en');window.addEventListener('hydrosim-language-change',sync);return()=>window.removeEventListener('hydrosim-language-change',sync)},[]);
  useEffect(()=>{
    const controller=new AbortController();
    setError(false);
    fetch('/api/v1/pedagogical/bottom-detection',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({
      correlation_real:scenarios[scenario],reference_sample_count:2,sample_rate_hz:40000,tx_delay_ms:txDelay,
      steering_across_track_angle_deg:steering,detection_method:method,detection_window_start_ms:windowStartUs/1000,
      detection_window_end_ms:windowEndUs/1000,threshold,multiple_detection:multipleDetection,
      truth_echo_lag_samples:scenarioTruth[scenario],truth_match_tolerance_samples:0,
      high_density:{
        high_density_enabled:highDensity,
        phase_sample_time_ms:[100,100.5,101,101.5,102],differential_phase_rad:HIGH_DENSITY_PHASE,support_magnitude:[1,1,1,1,1],
        steering_across_track_angle_deg:0,support_min_angle_deg:-15,support_max_angle_deg:15,split_aperture_baseline_m:[0,0.01,0],
        frequency_khz:200,sound_speed_mps:1500,reference_footprint_width_m:4,tx_delay_ms:0
      }
    })})
      .then(async r=>{if(!r.ok) throw new Error('detection request rejected'); return r.json() as Promise<Response>})
      .then(setData).catch(e=>{if(e.name!=='AbortError')setError(true)});
    return()=>controller.abort();
  },[scenario,txDelay,steering,method,windowStartUs,windowEndUs,threshold,multipleDetection,highDensity]);

  const reset=()=>{
    setScenario('clean');setTxDelay(0.2);setSteering(0);setMethod('amplitude_peak');setWindowStartUs(WINDOW_MIN_US);setWindowEndUs(WINDOW_MAX_US);
    setThreshold(0.5);setMultipleDetection(false);setHighDensity(false);
  };
  const maxMag=useMemo(()=>Math.max(...(data?.correlation.magnitude??[1]),1e-9),[data]);
  const detection=data?.selected_detection;
  const selectedLag=detection?.peak_index!=null?data?.correlation.lag_us[detection.peak_index]??null:null;
  const classificationCounts=useMemo(()=>{
    const counts={true_detection:0,false_detection:0,missed_detection:0};
    data?.classifications.forEach(item=>{counts[item.classification]+=1});
    return counts;
  },[data]);
  const separation=data?.comparison.detection_separation_ms[0]??null;
  const hd=data?.high_density;
  const hdPoints=hd?.detections??[];
  const hdExtent=useMemo(()=>Math.max(1,...hdPoints.map(p=>Math.abs(p.local_bottom_point_m[1]))),[hdPoints]);

  return <div className="d9-lab">
    <main className="d9-layout">
      <aside className="d9-controls">
        <button type="button" onClick={reset}><RotateCcw size={16}/>{t.reset}</button>
        <label>{t.scenario}<select value={scenario} onChange={e=>setScenario(e.target.value as keyof typeof scenarios)}><option value="clean">{t.clean}</option><option value="late">{t.late}</option><option value="double">{t.double}</option></select></label>
        <label>{t.delay}<strong>{txDelay.toFixed(2)} ms</strong><input type="range" min="0" max="2" step="0.05" value={txDelay} onChange={e=>setTxDelay(Number(e.target.value))}/></label>
        <label>{t.steering}<strong>{steering.toFixed(0)}°</strong><input type="range" min="-60" max="60" step="5" value={steering} onChange={e=>setSteering(Number(e.target.value))}/></label>
        <label>{t.method}<select value={method} onChange={e=>setMethod(e.target.value as Method)}><option value="amplitude_peak">{t.amp}</option><option value="phase_zero_crossing">{t.phase}</option></select></label>
        <section aria-label={t.window}><strong>{t.window}</strong>
          <label>{t.windowStart}<strong>{windowStartUs.toFixed(0)} µs</strong><input type="range" min={WINDOW_MIN_US} max={windowEndUs} step="25" value={windowStartUs} onChange={e=>setWindowStartUs(Number(e.target.value))}/></label>
          <label>{t.windowEnd}<strong>{windowEndUs.toFixed(0)} µs</strong><input type="range" min={windowStartUs} max={WINDOW_MAX_US} step="25" value={windowEndUs} onChange={e=>setWindowEndUs(Number(e.target.value))}/></label><small>{t.windowHint}</small>
        </section>
        <section aria-label={t.threshold}><strong>{t.threshold}</strong><label>{t.threshold}<strong>{threshold.toFixed(2)}</strong><input type="range" min="0" max="1" step="0.05" value={threshold} onChange={e=>setThreshold(Number(e.target.value))}/></label><small>{t.thresholdHint}</small></section>
        <label>{t.retention}<select value={multipleDetection?'multiple':'single'} onChange={e=>setMultipleDetection(e.target.value==='multiple')}><option value="single">{t.single}</option><option value="multiple">{t.multiple}</option></select></label>
        <section aria-label={t.highDensity}><strong>{t.highDensity}</strong><label>{t.highDensity}<select value={highDensity?'on':'off'} onChange={e=>setHighDensity(e.target.value==='on')}><option value="off">{t.off}</option><option value="on">{t.on}</option></select></label><small>{t.highDensityHint}</small></section>
      </aside>
      <section className="d9-stage">
        <div className="d9-stage-title"><div><small>{t.trace}</small><strong>{t.chain}</strong></div>{detection&&<div className="d9-selected"><LocateFixed size={16}/>{t.selected}</div>}</div>
        {error?<div className="d9-message" role="status">{t.error}</div>:data?.status==='unsupported'?<div className="d9-message"><strong>{t.unsupported}</strong><span>{t.unsupportedDetail}</span></div>:<div className="d9-chart" aria-label={t.trace}>{data?.correlation.magnitude.map((m,i)=>{
          const lag=data.correlation.lag_us[i]; const active=detection?.peak_index===i; const eligible=data.eligible_candidates.some(item=>item.peak_index===i); const retained=data.retained_detections.some(item=>item.peak_index===i);
          const inWindow=lag>=windowStartUs&&lag<=windowEndUs; const normalized=data.correlation.normalized_magnitude[i]??m/maxMag; const aboveThreshold=normalized>=threshold;
          const marker=retained?t.retainedMark:eligible?t.rejectedMark:aboveThreshold?t.candidate:'';
          return <div key={i} className={`d9-sample ${active?'active':''}`} style={{height:`${8+82*m/maxMag}%`,opacity:inWindow?(eligible?1:aboveThreshold?0.72:0.34):0.16,outline:retained?'2px solid currentColor':eligible?'1px dashed currentColor':'none',outlineOffset:'1px'}} title={`${lag.toFixed(0)} µs · ${normalized.toFixed(2)}${marker?' · '+marker:''}`} aria-label={`${lag.toFixed(0)} µs · ${normalized.toFixed(2)}${marker?' · '+marker:''}`}><span>{retained?'▲':eligible?'•':''}</span></div>
        })}<div className="d9-axis">{data?.correlation.lag_us.map((lag,i)=><span key={i}>{i%2===0?`${lag.toFixed(0)} µs`:''}</span>)}</div></div>}
        <div className="d9-readouts"><div><small>{t.eligible}</small><strong>{data?.comparison.eligible_candidate_count??'—'}</strong></div><div><small>{t.retained}</small><strong>{data?.comparison.retained_detection_count??'—'}</strong></div><div><small>{t.trueDet}</small><strong>{data?classificationCounts.true_detection:'—'}</strong></div><div><small>{t.falseDet}</small><strong>{data?classificationCounts.false_detection:'—'}</strong></div><div><small>{t.missedDet}</small><strong>{data?classificationCounts.missed_detection:'—'}</strong></div><div><small>{t.separation}</small><strong>{separation!=null?`${separation.toFixed(3)} ms`:'—'}</strong></div></div>
        <div className="d9-readouts"><div><small>{t.twtt}</small><strong>{detection?`${detection.twtt_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.arrival}</small><strong>{detection?`${detection.arrival_offset_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.angle}</small><strong>{detection?.detected_across_track_angle_deg!=null?`${detection.detected_across_track_angle_deg.toFixed(0)}°`:'—'}</strong></div><div><small>{t.peakLag}</small><strong>{selectedLag!=null?`${selectedLag.toFixed(0)} µs`:'—'}</strong></div></div>
        <div className="d9-intuition"><small>{t.hdComparison}</small>{highDensity&&hd?.status==='available'?<><div className="d9-readouts"><div><small>{t.ordinaryPoints}</small><strong>{hd.comparison.ordinary_detection_count}</strong></div><div><small>{t.hdPoints}</small><strong>{hd.comparison.high_density_detection_count}</strong></div><div><small>{t.densityGain}</small><strong>{hd.comparison.density_multiplier.toFixed(1)}×</strong></div><div><small>{t.targetSpacing}</small><strong>{hd.comparison.target_spacing_m!=null?`${hd.comparison.target_spacing_m.toFixed(2)} m`:'—'}</strong></div></div><svg viewBox="0 0 600 120" role="img" aria-label={t.acrossTrack} style={{width:'100%',height:'120px'}}><line x1="40" y1="78" x2="560" y2="78" stroke="currentColor" opacity="0.35"/><circle cx="300" cy="78" r="8" fill="none" stroke="currentColor" strokeWidth="2"/><text x="300" y="108" textAnchor="middle" fill="currentColor" fontSize="12">{t.ordinaryPoints}</text>{hdPoints.map(point=>{const y=point.local_bottom_point_m[1];const x=300+(y/hdExtent)*230;return <circle key={point.detection_index} cx={x} cy="48" r="6" fill="currentColor"><title>{`${point.detected_across_track_angle_deg.toFixed(1)}° · y ${y.toFixed(2)} m`}</title></circle>})}</svg></>:highDensity?<div className="d9-message" role="status">{t.hdUnavailable}</div>:<div className="d9-readouts"><div><small>{t.ordinaryPoints}</small><strong>1</strong></div><div><small>{t.hdPoints}</small><strong>—</strong></div><div><small>{t.densityGain}</small><strong>—</strong></div></div>}</div>
        <div className="d9-intuition"><small>{t.relationship}</small><div className="d9-readouts"><div><small>{t.transmit}</small><strong>{detection?`${detection.tx_delay_ms.toFixed(3)} ms`:`${txDelay.toFixed(3)} ms`}</strong></div><div><small>{t.echo}</small><strong>{detection?`${detection.arrival_offset_ms.toFixed(3)} ms`:t.noDetection}</strong></div><div><small>{t.sounding}</small><strong>{detection?`${detection.twtt_ms.toFixed(3)} ms`:t.noDetection}</strong></div></div></div>
      </section>
    </main>
  </div>;
}