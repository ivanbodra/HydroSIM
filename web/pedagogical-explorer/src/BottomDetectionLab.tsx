import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Languages, LocateFixed, RotateCcw } from 'lucide-react';

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
  unsupported_reason: string | null;
};

const WINDOW_MIN_US = -25;
const WINDOW_MAX_US = 200;

const copy = {
  en: {
    title:'Bottom Detection', module:'ACQUISITION CHAIN', chain:'INPUT → DETECTION → TIMING',
    intro:'Change the detector inputs and watch which echoes are retained, rejected or missed.',
    back:'System Map', lang:'PT-BR', reset:'Reset', scenario:'Echo scenario', clean:'Single clear echo', late:'Later echo', double:'Competing echoes',
    delay:'TX delay', steering:'Steering angle', method:'Detection method', amp:'Amplitude peak', phase:'Phase zero crossing', window:'Detection window',
    windowStart:'Window start', windowEnd:'Window end', windowHint:'Only echoes inside the highlighted time window can be selected.',
    threshold:'Detection threshold', thresholdHint:'Raise the threshold to reject weaker local peaks.', retention:'Retention', single:'Single detection', multiple:'Multiple detections',
    trace:'Matched-filter magnitude', selected:'Selected detection', twtt:'TWTT', arrival:'Arrival offset', angle:'Detected angle', peakLag:'Peak lag',
    unsupported:'This detection method is not available yet', unsupportedDetail:'Phase zero crossing is not yet available in this lesson. Select Amplitude peak to continue exploring the detection.',
    intuition:'Physical intuition', insight:'Threshold decides which local peaks are eligible; retention decides whether one or several eligible echoes continue downstream.',
    relationship:'Detection outcome', transmit:'Transmit reference', echo:'Primary echo', sounding:'Timing passed downstream', noDetection:'No echo selected',
    eligible:'Eligible peaks', retained:'Retained', trueDet:'True', falseDet:'False', missedDet:'Missed', separation:'Detection separation',
    truth:'Known echo', candidate:'candidate', retainedMark:'retained', rejectedMark:'eligible, not retained',
    error:'The detection view could not be updated. Adjust the controls or try again.'
  },
  pt: {
    title:'Detecção do Fundo', module:'CADEIA DE AQUISIÇÃO', chain:'ENTRADA → DETECÇÃO → TEMPO',
    intro:'Altere as entradas do detector e observe quais ecos são retidos, rejeitados ou perdidos.',
    back:'Mapa do Sistema', lang:'EN', reset:'Redefinir', scenario:'Cenário de eco', clean:'Um eco nítido', late:'Eco mais tardio', double:'Ecos concorrentes',
    delay:'Atraso de TX', steering:'Ângulo de steering', method:'Método de detecção', amp:'Pico de amplitude', phase:'Cruzamento de fase por zero', window:'Janela de detecção',
    windowStart:'Início da janela', windowEnd:'Fim da janela', windowHint:'Somente ecos dentro da janela de tempo destacada podem ser selecionados.',
    threshold:'Limiar de detecção', thresholdHint:'Eleve o limiar para rejeitar picos locais mais fracos.', retention:'Retenção', single:'Uma detecção', multiple:'Múltiplas detecções',
    trace:'Magnitude do filtro casado', selected:'Detecção selecionada', twtt:'TWTT', arrival:'Offset de chegada', angle:'Ângulo detectado', peakLag:'Atraso do pico',
    unsupported:'Este método de detecção ainda não está disponível', unsupportedDetail:'O cruzamento de fase por zero ainda não está disponível nesta lição. Selecione Pico de amplitude para continuar explorando a detecção.',
    intuition:'Intuição física', insight:'O limiar decide quais picos locais são elegíveis; a retenção decide se um ou vários ecos elegíveis seguem adiante.',
    relationship:'Resultado da detecção', transmit:'Referência de transmissão', echo:'Eco principal', sounding:'Tempo enviado adiante', noDetection:'Nenhum eco selecionado',
    eligible:'Picos elegíveis', retained:'Retidos', trueDet:'Verdadeiras', falseDet:'Falsas', missedDet:'Perdidas', separation:'Separação entre detecções',
    truth:'Eco conhecido', candidate:'candidato', retainedMark:'retido', rejectedMark:'elegível, não retido',
    error:'Não foi possível atualizar a visualização da detecção. Ajuste os controles ou tente novamente.'
  }
};

const scenarios = {
  clean:[0,0.02,0.08,0.2,0.72,1,0.55,0.18,0.05,0.01],
  late:[0,0.01,0.03,0.06,0.11,0.22,0.48,0.92,1,0.4],
  double:[0,0.04,0.2,0.76,0.45,0.18,0.38,1,0.5,0.08]
};

const scenarioTruth: Record<keyof typeof scenarios, number[]> = {
  clean:[4],
  late:[7],
  double:[2,6]
};

export default function BottomDetectionLab({onBack}:{onBack:()=>void}) {
  const [language,setLanguage]=useState<Language>('en');
  const [scenario,setScenario]=useState<keyof typeof scenarios>('clean');
  const [txDelay,setTxDelay]=useState(0.2);
  const [steering,setSteering]=useState(0);
  const [method,setMethod]=useState<Method>('amplitude_peak');
  const [windowStartUs,setWindowStartUs]=useState(WINDOW_MIN_US);
  const [windowEndUs,setWindowEndUs]=useState(WINDOW_MAX_US);
  const [threshold,setThreshold]=useState(0.5);
  const [multipleDetection,setMultipleDetection]=useState(false);
  const [data,setData]=useState<Response|null>(null);
  const [error,setError]=useState(false);
  const t=copy[language];

  useEffect(()=>{
    const controller=new AbortController();
    setError(false);
    fetch('/api/v1/pedagogical/bottom-detection',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({
      correlation_real:scenarios[scenario],reference_sample_count:2,sample_rate_hz:40000,tx_delay_ms:txDelay,
      steering_across_track_angle_deg:steering,detection_method:method,detection_window_start_ms:windowStartUs/1000,
      detection_window_end_ms:windowEndUs/1000,threshold,multiple_detection:multipleDetection,
      truth_echo_lag_samples:scenarioTruth[scenario],truth_match_tolerance_samples:0
    })})
      .then(async r=>{if(!r.ok) throw new Error('detection request rejected'); return r.json() as Promise<Response>})
      .then(setData).catch(e=>{if(e.name!=='AbortError')setError(true)});
    return()=>controller.abort();
  },[scenario,txDelay,steering,method,windowStartUs,windowEndUs,threshold,multipleDetection]);

  const reset=()=>{
    setScenario('clean');setTxDelay(0.2);setSteering(0);setMethod('amplitude_peak');
    setWindowStartUs(WINDOW_MIN_US);setWindowEndUs(WINDOW_MAX_US);setThreshold(0.5);setMultipleDetection(false);
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

  return <div className="d9-lab">
    <header className="d9-head"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><span>PED-D9 · {t.module}</span><h1>{t.title}</h1><p>{t.intro}</p></div><button onClick={()=>setLanguage(language==='en'?'pt':'en')}><Languages size={16}/>{t.lang}</button></header>
    <main className="d9-layout">
      <aside className="d9-controls">
        <button type="button" onClick={reset}><RotateCcw size={16}/>{t.reset}</button>
        <label>{t.scenario}<select value={scenario} onChange={e=>setScenario(e.target.value as keyof typeof scenarios)}><option value="clean">{t.clean}</option><option value="late">{t.late}</option><option value="double">{t.double}</option></select></label>
        <label>{t.delay}<strong>{txDelay.toFixed(2)} ms</strong><input type="range" min="0" max="2" step="0.05" value={txDelay} onChange={e=>setTxDelay(Number(e.target.value))}/></label>
        <label>{t.steering}<strong>{steering.toFixed(0)}°</strong><input type="range" min="-60" max="60" step="5" value={steering} onChange={e=>setSteering(Number(e.target.value))}/></label>
        <label>{t.method}<select value={method} onChange={e=>setMethod(e.target.value as Method)}><option value="amplitude_peak">{t.amp}</option><option value="phase_zero_crossing">{t.phase}</option></select></label>
        <section aria-label={t.window}>
          <strong>{t.window}</strong>
          <label>{t.windowStart}<strong>{windowStartUs.toFixed(0)} µs</strong><input type="range" min={WINDOW_MIN_US} max={windowEndUs} step="25" value={windowStartUs} onChange={e=>setWindowStartUs(Number(e.target.value))}/></label>
          <label>{t.windowEnd}<strong>{windowEndUs.toFixed(0)} µs</strong><input type="range" min={windowStartUs} max={WINDOW_MAX_US} step="25" value={windowEndUs} onChange={e=>setWindowEndUs(Number(e.target.value))}/></label>
          <small>{t.windowHint}</small>
        </section>
        <section aria-label={t.threshold}>
          <strong>{t.threshold}</strong>
          <label>{t.threshold}<strong>{threshold.toFixed(2)}</strong><input type="range" min="0" max="1" step="0.05" value={threshold} onChange={e=>setThreshold(Number(e.target.value))}/></label>
          <small>{t.thresholdHint}</small>
        </section>
        <label>{t.retention}<select value={multipleDetection?'multiple':'single'} onChange={e=>setMultipleDetection(e.target.value==='multiple')}><option value="single">{t.single}</option><option value="multiple">{t.multiple}</option></select></label>
      </aside>
      <section className="d9-stage">
        <div className="d9-stage-title"><div><small>{t.trace}</small><strong>{t.chain}</strong></div>{detection&&<div className="d9-selected"><LocateFixed size={16}/>{t.selected}</div>}</div>
        {error?<div className="d9-message" role="status">{t.error}</div>:data?.status==='unsupported'?<div className="d9-message"><strong>{t.unsupported}</strong><span>{t.unsupportedDetail}</span></div>:<div className="d9-chart" aria-label={t.trace}>{data?.correlation.magnitude.map((m,i)=>{
          const lag=data.correlation.lag_us[i];
          const active=detection?.peak_index===i;
          const eligible=data.eligible_candidates.some(item=>item.peak_index===i);
          const retained=data.retained_detections.some(item=>item.peak_index===i);
          const inWindow=lag>=windowStartUs&&lag<=windowEndUs;
          const normalized=data.correlation.normalized_magnitude[i]??m/maxMag;
          const aboveThreshold=normalized>=threshold;
          const marker=retained?t.retainedMark:eligible?t.rejectedMark:aboveThreshold?t.candidate:'';
          return <div key={i} className={`d9-sample ${active?'active':''}`} style={{height:`${8+82*m/maxMag}%`,opacity:inWindow?(eligible?1:aboveThreshold?0.72:0.34):0.16,outline:retained?'2px solid currentColor':eligible?'1px dashed currentColor':'none',outlineOffset:'1px'}} title={`${lag.toFixed(0)} µs · ${normalized.toFixed(2)}${marker?' · '+marker:''}`} aria-label={`${lag.toFixed(0)} µs · ${normalized.toFixed(2)}${marker?' · '+marker:''}`}><span>{retained?'▲':eligible?'•':''}</span></div>
        })}<div className="d9-axis">{data?.correlation.lag_us.map((lag,i)=><span key={i}>{i%2===0?`${lag.toFixed(0)} µs`:''}</span>)}</div></div>}
        <div className="d9-readouts"><div><small>{t.eligible}</small><strong>{data?.comparison.eligible_candidate_count??'—'}</strong></div><div><small>{t.retained}</small><strong>{data?.comparison.retained_detection_count??'—'}</strong></div><div><small>{t.trueDet}</small><strong>{data?classificationCounts.true_detection:'—'}</strong></div><div><small>{t.falseDet}</small><strong>{data?classificationCounts.false_detection:'—'}</strong></div><div><small>{t.missedDet}</small><strong>{data?classificationCounts.missed_detection:'—'}</strong></div><div><small>{t.separation}</small><strong>{separation!=null?`${separation.toFixed(3)} ms`:'—'}</strong></div></div>
        <div className="d9-readouts"><div><small>{t.twtt}</small><strong>{detection?`${detection.twtt_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.arrival}</small><strong>{detection?`${detection.arrival_offset_ms.toFixed(3)} ms`:'—'}</strong></div><div><small>{t.angle}</small><strong>{detection?.detected_across_track_angle_deg!=null?`${detection.detected_across_track_angle_deg.toFixed(0)}°`:'—'}</strong></div><div><small>{t.peakLag}</small><strong>{selectedLag!=null?`${selectedLag.toFixed(0)} µs`:'—'}</strong></div></div>
        <div className="d9-intuition"><small>{t.relationship}</small><div className="d9-readouts"><div><small>{t.transmit}</small><strong>{detection?`${detection.tx_delay_ms.toFixed(3)} ms`:`${txDelay.toFixed(3)} ms`}</strong></div><div><small>{t.echo}</small><strong>{detection?`${detection.arrival_offset_ms.toFixed(3)} ms`:t.noDetection}</strong></div><div><small>{t.sounding}</small><strong>{detection?`${detection.twtt_ms.toFixed(3)} ms`:t.noDetection}</strong></div></div></div>
        <div className="d9-intuition"><small>{t.intuition}</small><p>{t.insight}</p></div>
      </section>
    </main>
  </div>;
}
