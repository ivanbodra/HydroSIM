import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Gauge, GitCompare, Languages, Radar, RotateCcw, Waves } from 'lucide-react';
import './tradeoff-lab.css';

type Lang='en'|'pt';
type SpacingMode='equiangular'|'equidistant';
type TxSequence='simultaneous'|'centre-delayed'|'sequential';
type DetectionMode='single'|'multiple';
type Beam={endpoint_across_track_m:number;footprint:{effective_across_track_width_m:number}};
type EchoResponse={mbes:{beams:Beam[];adjacent_across_track_spacings_m:number[];geometric_beam_center_swath_width_m:number}};
type Sector={sector_id:string;centre_across_track_deg:number;across_track_min_deg:number;across_track_max_deg:number;frequency_khz:number;pulse_duration_ms:number;tx_delay_ms:number;relative_power:number};
type MultiResponse={sectors:Array<Sector&{wavelength_m:number;tx_time_s:number;tx_end_time_s:number}>;transmit_groups:string[][]};
type HdDetection={local_bottom_point_m:[number,number,number]};
type DetectionResponse={comparison:{retained_detection_count:number};high_density:{status:string;detections:HdDetection[];comparison:{ordinary_detection_count:number;high_density_detection_count:number;density_multiplier:number;target_spacing_m:number|null}}|null};
type Interval={start_m:number;end_m:number;width_m:number};
type SurveyResponse={
 status:'available'|'partial';
 ping_rate_hz:number;
 ping_period_s:number;
 vessel_speed_knots:number;
 vessel_speed_mps:number;
 along_track_ping_spacing_m:number;
 along_track_ping_density_per_m:number|null;
 across_track:{ordered_positions_m:number[];adjacent_spacing_m:number[];adjacent_linear_density_per_m:Array<number|null>;areal_density_per_m2:Array<number|null>;min_spacing_m:number|null;max_spacing_m:number|null;mean_spacing_m:number|null};
 coverage:{classification:'continuous'|'gapped'|'unavailable';footprint_intervals:Interval[];merged_coverage_intervals:Interval[];internal_gap_intervals:Interval[];total_covered_width_m:number|null;geometric_beam_center_swath_width_m:number|null;along_track_gap_by_beam_m:number[];along_track_classification:'continuous'|'gapped'|'unavailable'};
 ordinary_sounding_count:number;
 retained_sounding_count:number;
 high_density_added_count:number;
};
type Settings={depth:number;beams:number;sector:number;pulse:number;frequency:number;beamwidth:number;spacingMode:SpacingMode;txSequence:TxSequence;detectionMode:DetectionMode;highDensity:boolean;pingRate:number;speed:number};
type Snapshot={echo:EchoResponse;multi:MultiResponse;survey:SurveyResponse;settings:Settings};

const DEFAULT_SETTINGS:Settings={depth:100,beams:15,sector:60,pulse:.5,frequency:300,beamwidth:1,spacingMode:'equiangular',txSequence:'centre-delayed',detectionMode:'single',highDensity:false,pingRate:10,speed:6};
const DETECTION_TRACE=[0,0.04,0.2,0.76,0.45,0.18,0.38,1,0.5,0.08];
const HIGH_DENSITY_PHASE=[1.4547515713804893,0.730154243024546,0,-0.730154243024546,-1.4547515713804893];

const copy={
 en:{title:'Acquisition trade-offs',lesson:'Survey Coverage & Acquisition Trade-offs',module:'Integrated Survey',lead:'Change acquisition choices and compare their visible consequences in one view.',back:'System map',controls:'Linked controls',depth:'Depth',beams:'Beam count',sector:'Angular sector',pulse:'Pulse duration',frequency:'Sector frequency',beamwidth:'RX beamwidth',spacingMode:'Beam spacing',equiangular:'Equiangular',equidistant:'Equidistant',txSequence:'TX sequence',simultaneous:'Simultaneous',centreDelayed:'Centre delayed',sequential:'Port → centre → starboard',detection:'Bottom detection',single:'Single detection',multiple:'Multiple detections',highDensity:'High Density',off:'Off',on:'On',pingRate:'Ping rate',speed:'Vessel speed',geometry:'Coverage geometry',swath:'Beam-centre swath',spacing:'Mean adjacent spacing',footprint:'Nadir footprint width',pattern:'Sounding pattern',patternLead:'Beam-centre soundings and their across-track footprint widths',count:'Soundings per ping',signal:'Transmit configuration',wavelength:'Wavelength',groups:'TX groups',window:'TX event span',density:'Detection density',densityLead:'Compare ordinary retention with phase-based High Density inside one receive-beam footprint.',retained:'Retained echoes',hdPoints:'High Density points',densityGain:'Point-density gain',targetSpacing:'Target spacing',coverage:'Survey coverage',coverageLead:'Ping cadence and vessel speed change along-track spacing while the beam geometry controls across-track coverage.',alongSpacing:'Along-track ping spacing',alongDensity:'Along-track ping density',acrossSpacing:'Across-track mean spacing',coveredWidth:'Covered width',gaps:'Internal gaps',coverageState:'Coverage state',continuous:'Continuous',gapped:'Gapped',unavailable:'Unavailable',retainedSoundings:'Retained soundings',compare:'Baseline × Current',baseline:'Baseline',current:'Current',change:'Change',baselineLead:'Choose a reference, move any control, and read both the new value and its change from that reference.',setBaseline:'Use current as baseline',restoreBaseline:'Restore baseline',reset:'Reset controls',note:'Compare how beam spacing, RX beamwidth, TX sequence, detection choices, ping rate and vessel speed change the acquisition result.',port:'Port +',starboard:'Starboard −',loading:'Updating acquisition state…',invalid:'The selected combination is outside the available validity range.'},
 pt:{title:'Compromissos da aquisição',lesson:'Cobertura do Levantamento e Compromissos da Aquisição',module:'Levantamento Integrado',lead:'Altere escolhas da aquisição e compare suas consequências visíveis em uma única visão.',back:'Mapa do sistema',controls:'Controles vinculados',depth:'Profundidade',beams:'Número de feixes',sector:'Setor angular',pulse:'Duração do pulso',frequency:'Frequência dos setores',beamwidth:'Largura do feixe RX',spacingMode:'Espaçamento dos feixes',equiangular:'Equiangular',equidistant:'Equidistante',txSequence:'Sequência TX',simultaneous:'Simultânea',centreDelayed:'Centro atrasado',sequential:'Bombordo → centro → boreste',detection:'Detecção do fundo',single:'Uma detecção',multiple:'Múltiplas detecções',highDensity:'High Density',off:'Desligado',on:'Ligado',pingRate:'Taxa de ping',speed:'Velocidade do navio',geometry:'Geometria de cobertura',swath:'Faixa entre centros de feixe',spacing:'Espaçamento adjacente médio',footprint:'Largura da pegada no nadir',pattern:'Padrão de sondagens',patternLead:'Sondagens nos centros dos feixes e suas larguras de pegada transversal',count:'Sondagens por ping',signal:'Configuração de transmissão',wavelength:'Comprimento de onda',groups:'Grupos TX',window:'Janela de eventos TX',density:'Densidade da detecção',densityLead:'Compare a retenção convencional com o High Density baseado em fase dentro da pegada de um feixe de recepção.',retained:'Ecos retidos',hdPoints:'Pontos High Density',densityGain:'Ganho de densidade',targetSpacing:'Espaçamento-alvo',coverage:'Cobertura do levantamento',coverageLead:'A cadência de ping e a velocidade do navio alteram o espaçamento longitudinal, enquanto a geometria dos feixes controla a cobertura transversal.',alongSpacing:'Espaçamento longitudinal entre pings',alongDensity:'Densidade longitudinal de pings',acrossSpacing:'Espaçamento transversal médio',coveredWidth:'Largura coberta',gaps:'Lacunas internas',coverageState:'Estado da cobertura',continuous:'Contínua',gapped:'Com lacunas',unavailable:'Indisponível',retainedSoundings:'Sondagens retidas',compare:'Baseline × Atual',baseline:'Baseline',current:'Atual',change:'Variação',baselineLead:'Escolha uma referência, mova qualquer controle e leia tanto o novo valor quanto sua variação em relação à referência.',setBaseline:'Usar atual como baseline',restoreBaseline:'Restaurar baseline',reset:'Restaurar controles',note:'Compare como o espaçamento dos feixes, a largura do feixe RX, a sequência TX, a detecção, a taxa de ping e a velocidade alteram o resultado da aquisição.',port:'Bombordo +',starboard:'Boreste −',loading:'Atualizando estado da aquisição…',invalid:'A combinação selecionada está fora da faixa de validade disponível.'}
};

function metrics(echo:EchoResponse,multi:MultiResponse){
 const spacing=echo.mbes.adjacent_across_track_spacings_m;
 const meanSpacing=spacing.length?spacing.reduce((a,b)=>a+Math.abs(b),0)/spacing.length:0;
 const nadir=echo.mbes.beams[Math.floor(echo.mbes.beams.length/2)];
 const centre=multi.sectors[1];
 const txSpan=multi.sectors.length?(Math.max(...multi.sectors.map(x=>x.tx_end_time_s))-Math.min(...multi.sectors.map(x=>x.tx_time_s)))*1000:0;
 return {swath:echo.mbes.geometric_beam_center_swath_width_m,spacing:meanSpacing,footprint:nadir?.footprint.effective_across_track_width_m??0,wavelength:centre?.wavelength_m??0,groups:multi.transmit_groups.length,window:txSpan};
}

export default function TradeoffLab({onBack}:{onBack:()=>void}){
 const[lang,setLang]=useState<Lang>('en');
 const[depth,setDepth]=useState(DEFAULT_SETTINGS.depth);
 const[beams,setBeams]=useState(DEFAULT_SETTINGS.beams);
 const[sector,setSector]=useState(DEFAULT_SETTINGS.sector);
 const[pulse,setPulse]=useState(DEFAULT_SETTINGS.pulse);
 const[frequency,setFrequency]=useState(DEFAULT_SETTINGS.frequency);
 const[beamwidth,setBeamwidth]=useState(DEFAULT_SETTINGS.beamwidth);
 const[spacingMode,setSpacingMode]=useState<SpacingMode>(DEFAULT_SETTINGS.spacingMode);
 const[txSequence,setTxSequence]=useState<TxSequence>(DEFAULT_SETTINGS.txSequence);
 const[detectionMode,setDetectionMode]=useState<DetectionMode>(DEFAULT_SETTINGS.detectionMode);
 const[highDensity,setHighDensity]=useState(DEFAULT_SETTINGS.highDensity);
 const[pingRate,setPingRate]=useState(DEFAULT_SETTINGS.pingRate);
 const[speed,setSpeed]=useState(DEFAULT_SETTINGS.speed);
 const[echo,setEcho]=useState<EchoResponse|null>(null);
 const[multi,setMulti]=useState<MultiResponse|null>(null);
 const[detection,setDetection]=useState<DetectionResponse|null>(null);
 const[survey,setSurvey]=useState<SurveyResponse|null>(null);
 const[baseline,setBaseline]=useState<Snapshot|null>(null);
 const[error,setError]=useState(false);
 const t=copy[lang];

 const settings:Settings={depth,beams,sector,pulse,frequency,beamwidth,spacingMode,txSequence,detectionMode,highDensity,pingRate,speed};
 const applySettings=(next:Settings)=>{setDepth(next.depth);setBeams(next.beams);setSector(next.sector);setPulse(next.pulse);setFrequency(next.frequency);setBeamwidth(next.beamwidth);setSpacingMode(next.spacingMode);setTxSequence(next.txSequence);setDetectionMode(next.detectionMode);setHighDensity(next.highDensity);setPingRate(next.pingRate);setSpeed(next.speed)};
 const echosounderRequest={selected_system:'mbes',vertical_separation_m:depth,start_depth_m:0,sound_speed_mps:1500,pulse_duration_ms:pulse,transmit_along_track_beamwidth_deg:2,receive_across_track_beamwidth_deg:beamwidth,mbes_beam_count:beams,minimum_angle_deg:-sector,maximum_angle_deg:sector,spacing_method:spacingMode};

 useEffect(()=>{
  const ac=new AbortController();
  setError(false);
  const delays=txSequence==='simultaneous'?[0,0,0]:txSequence==='sequential'?[0,.35,.7]:[0,.35,0];
  const sectors:Sector[]=[{sector_id:'port',centre_across_track_deg:sector*.58,across_track_min_deg:sector*.18,across_track_max_deg:sector,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:delays[0],relative_power:.85},{sector_id:'centre',centre_across_track_deg:0,across_track_min_deg:-sector*.2,across_track_max_deg:sector*.2,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:delays[1],relative_power:1},{sector_id:'starboard',centre_across_track_deg:-sector*.58,across_track_min_deg:-sector,across_track_max_deg:-sector*.18,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:delays[2],relative_power:.85}];
  const post=(url:string,body:unknown)=>fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},signal:ac.signal,body:JSON.stringify(body)});
  Promise.all([
   post('/api/v1/pedagogical/echosounders',echosounderRequest),
   post('/api/v1/pedagogical/multisector',{tx_time_s:10,sound_speed_mps:1500,sectors}),
   post('/api/v1/pedagogical/bottom-detection',{correlation_real:DETECTION_TRACE,reference_sample_count:2,sample_rate_hz:40000,tx_delay_ms:0,steering_across_track_angle_deg:0,detection_method:'amplitude_peak',detection_window_start_ms:-0.025,detection_window_end_ms:0.2,threshold:.35,multiple_detection:detectionMode==='multiple',truth_echo_lag_samples:[2,6],truth_match_tolerance_samples:0,high_density:{high_density_enabled:highDensity,phase_sample_time_ms:[100,100.5,101,101.5,102],differential_phase_rad:HIGH_DENSITY_PHASE,support_magnitude:[1,1,1,1,1],steering_across_track_angle_deg:0,support_min_angle_deg:-15,support_max_angle_deg:15,split_aperture_baseline_m:[0,0.01,0],frequency_khz:200,sound_speed_mps:1500,reference_footprint_width_m:4,tx_delay_ms:0}})
  ]).then(async([a,b,c])=>{
    if(!a.ok||!b.ok||!c.ok)throw new Error('configuration rejected');
    const nextEcho=await a.json() as EchoResponse;
    const nextMulti=await b.json() as MultiResponse;
    const nextDetection=await c.json() as DetectionResponse;
    const hdPoints=highDensity?(nextDetection.high_density?.detections??[]).map(item=>item.local_bottom_point_m):[];
    const s=await post('/api/v1/pedagogical/survey-density',{ping_rate_hz:pingRate,vessel_speed_knots:speed,echosounder:echosounderRequest,high_density_bottom_points_m:hdPoints});
    if(!s.ok)throw new Error('survey configuration rejected');
    const nextSurvey=await s.json() as SurveyResponse;
    setEcho(nextEcho);setMulti(nextMulti);setDetection(nextDetection);setSurvey(nextSurvey);
    setBaseline(v=>v??{echo:nextEcho,multi:nextMulti,survey:nextSurvey,settings:{...settings}});
  }).catch(e=>{if(e.name!=='AbortError'){setEcho(null);setMulti(null);setDetection(null);setSurvey(null);setError(true)}});
  return()=>ac.abort();
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[depth,beams,sector,pulse,frequency,beamwidth,spacingMode,txSequence,detectionMode,highDensity,pingRate,speed]);

 const mbes=echo?.mbes;
 const current=useMemo(()=>echo&&multi?metrics(echo,multi):null,[echo,multi]);
 const base=useMemo(()=>baseline?metrics(baseline.echo,baseline.multi):null,[baseline]);
 const referenceBeams=baseline?.echo.mbes.beams??mbes?.beams??[];
 const extent=Math.max(1,...referenceBeams.map(b=>Math.abs(b.endpoint_across_track_m)));
 const value=(v:number|null|undefined,unit:string,digits=1)=><strong>{v==null?'—':`${v.toFixed(digits)} ${unit}`}</strong>;
 const delta=(currentValue:number,baseValue:number,unit:string,digits=1)=>{const d=currentValue-baseValue;const threshold=Math.pow(10,-digits)/2;const shown=Math.abs(d)<threshold?0:d;const arrow=shown>0?'↑':shown<0?'↓':'→';return <strong>{arrow} {shown>0?'+':''}{shown.toFixed(digits)} {unit}</strong>};
 const sequenceLabel=(v:TxSequence)=>v==='simultaneous'?t.simultaneous:v==='sequential'?t.sequential:t.centreDelayed;
 const detectionLabel=(v:DetectionMode)=>v==='multiple'?t.multiple:t.single;
 const coverageLabel=(v:SurveyResponse['coverage']['classification'])=>v==='continuous'?t.continuous:v==='gapped'?t.gapped:t.unavailable;
 const hd=detection?.high_density;
 const hdComparison=hd?.comparison;
 const captureBaseline=()=>{if(echo&&multi&&survey)setBaseline({echo,multi,survey,settings:{...settings}})};
 const restoreBaseline=()=>{if(baseline)applySettings(baseline.settings)};
 const resetControls=()=>applySettings(DEFAULT_SETTINGS);
 const coverageIntervals=survey?.coverage.merged_coverage_intervals??[];
 const coverageMin=coverageIntervals.length?Math.min(...coverageIntervals.map(x=>x.start_m)):-1;
 const coverageMax=coverageIntervals.length?Math.max(...coverageIntervals.map(x=>x.end_m)):1;
 const coverageSpan=Math.max(1e-6,coverageMax-coverageMin);

 return <div className="d17-lab">
  <header className="d17-toolbar"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><Gauge size={18}/><strong>PED-D17 · {t.lesson}</strong></div><button onClick={()=>setLang(v=>v==='en'?'pt':'en')}><Languages size={16}/>{lang==='en'?'PT-BR':'EN'}</button></header>
  <section className="d17-question"><span>17 · {t.module.toUpperCase()}</span><h1>{t.title}</h1><p>{t.lead}</p></section>
  <main className="d17-grid">
   <aside className="d17-controls">
    <h2>{t.controls}</h2>
    <label>{t.depth}<output>{depth} m</output><input type="range" min="20" max="300" step="10" value={depth} onChange={e=>setDepth(+e.target.value)}/></label>
    <label>{t.beams}<output>{beams}</output><input type="range" min="3" max="31" step="2" value={beams} onChange={e=>setBeams(+e.target.value)}/></label>
    <label>{t.sector}<output>±{sector}°</output><input type="range" min="20" max="70" step="5" value={sector} onChange={e=>setSector(+e.target.value)}/></label>
    <label>{t.beamwidth}<output>{beamwidth.toFixed(1)}°</output><input type="range" min="0.5" max="4" step="0.5" value={beamwidth} onChange={e=>setBeamwidth(+e.target.value)}/></label>
    <label>{t.spacingMode}<select value={spacingMode} onChange={e=>setSpacingMode(e.target.value as SpacingMode)}><option value="equiangular">{t.equiangular}</option><option value="equidistant">{t.equidistant}</option></select></label>
    <label>{t.txSequence}<select value={txSequence} onChange={e=>setTxSequence(e.target.value as TxSequence)}><option value="simultaneous">{t.simultaneous}</option><option value="centre-delayed">{t.centreDelayed}</option><option value="sequential">{t.sequential}</option></select></label>
    <label>{t.detection}<select value={detectionMode} onChange={e=>setDetectionMode(e.target.value as DetectionMode)}><option value="single">{t.single}</option><option value="multiple">{t.multiple}</option></select></label>
    <label>{t.highDensity}<select value={highDensity?'on':'off'} onChange={e=>setHighDensity(e.target.value==='on')}><option value="off">{t.off}</option><option value="on">{t.on}</option></select></label>
    <label>{t.pingRate}<output>{pingRate.toFixed(1)} Hz</output><input type="range" min="1" max="30" step="1" value={pingRate} onChange={e=>setPingRate(+e.target.value)}/></label>
    <label>{t.speed}<output>{speed.toFixed(1)} kn</output><input type="range" min="0" max="15" step="0.5" value={speed} onChange={e=>setSpeed(+e.target.value)}/></label>
    <label>{t.pulse}<output>{pulse.toFixed(2)} ms</output><input type="range" min="0.1" max="1.5" step="0.1" value={pulse} onChange={e=>setPulse(+e.target.value)}/></label>
    <label>{t.frequency}<output>{frequency} kHz</output><input type="range" min="100" max="500" step="25" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label>
    <button type="button" onClick={resetControls}><RotateCcw size={15}/>{t.reset}</button>
   </aside>
   <section className="d17-stage">
    {error?<div className="d17-state">{t.invalid}</div>:!echo||!multi||!detection||!survey||!current?<div className="d17-state">{t.loading}</div>:<>
     <section className="d17-panel"><header><Radar size={18}/><div><small>{t.geometry}</small><strong>{t.port} ← NADIR → {t.starboard}</strong></div></header><div className="d17-swath"><i className="centre"/>{mbes?.beams.map((b,i)=><i key={i} className="beam" style={{left:`${50-(b.endpoint_across_track_m/extent)*44}%`}}/>)}</div><div className="d17-readouts"><div><small>{t.swath}</small>{value(current.swath,'m')}</div><div><small>{t.spacing}</small>{value(current.spacing,'m')}</div><div><small>{t.footprint}</small>{value(current.footprint,'m',2)}</div></div></section>
     <section className="d17-panel"><header><Radar size={18}/><div><small>{t.pattern}</small><strong>{t.patternLead}</strong></div></header><div className="d17-pattern"><i className="centre"/>{mbes?.beams.map((b,i)=>{const width=Math.max(3,Math.min(15,(b.footprint.effective_across_track_width_m/(extent*2))*88));return <span key={i} className="sounding" style={{left:`${50-(b.endpoint_across_track_m/extent)*44}%`,width:`${width}%`}}><i/></span>})}</div><div className="d17-readouts"><div><small>{t.count}</small><strong>{mbes?.beams.length??0}</strong></div><div><small>{t.spacing}</small>{value(current.spacing,'m')}</div><div><small>{t.footprint}</small>{value(current.footprint,'m',2)}</div></div></section>
     <section className="d17-panel"><header><Waves size={18}/><div><small>{t.signal}</small><strong>{sequenceLabel(txSequence)} · {frequency} kHz · {pulse.toFixed(2)} ms</strong></div></header><div className="d17-signal"><div><small>{t.wavelength}</small>{value(current.wavelength*1000,'mm',2)}</div><div><small>{t.groups}</small><strong>{current.groups}</strong></div><div><small>{t.window}</small>{value(current.window,'ms',2)}</div></div></section>
     <section className="d17-panel"><header><Radar size={18}/><div><small>{t.density}</small><strong>{detectionLabel(detectionMode)} · {t.highDensity}: {highDensity?t.on:t.off}{hdComparison?.target_spacing_m!=null?` · ${t.targetSpacing}: ${hdComparison.target_spacing_m.toFixed(2)} m`:''}</strong></div></header><p>{t.densityLead}</p><div className="d17-readouts"><div><small>{t.retained}</small><strong>{detection.comparison.retained_detection_count}</strong></div><div><small>{t.hdPoints}</small><strong>{hdComparison?.high_density_detection_count??0}</strong></div><div><small>{t.densityGain}</small><strong>{hdComparison?`${hdComparison.density_multiplier.toFixed(1)}×`:'—'}</strong></div></div></section>
     <section className="d17-panel"><header><Radar size={18}/><div><small>{t.coverage}</small><strong>{coverageLabel(survey.coverage.classification)} · {pingRate.toFixed(0)} Hz · {speed.toFixed(1)} kn</strong></div></header><p>{t.coverageLead}</p><div className="d17-pattern" aria-label={t.coverage}>{coverageIntervals.map((item,i)=>{const left=((item.start_m-coverageMin)/coverageSpan)*100;const width=(item.width_m/coverageSpan)*100;return <span key={i} className="sounding" style={{left:`${left}%`,width:`${width}%`,maxWidth:'none',minWidth:2,height:28,bottom:42,transform:'none'}}><i style={{width:'100%',height:'100%',borderRadius:999}}/></span>})}</div><div className="d17-readouts"><div><small>{t.alongSpacing}</small>{value(survey.along_track_ping_spacing_m,'m',2)}</div><div><small>{t.alongDensity}</small>{value(survey.along_track_ping_density_per_m,'/m',2)}</div><div><small>{t.acrossSpacing}</small>{value(survey.across_track.mean_spacing_m,'m',2)}</div><div><small>{t.coveredWidth}</small>{value(survey.coverage.total_covered_width_m,'m',1)}</div><div><small>{t.gaps}</small><strong>{survey.coverage.internal_gap_intervals.length}</strong></div><div><small>{t.retainedSoundings}</small><strong>{survey.retained_sounding_count}</strong></div></div></section>
     {base&&baseline&&<section className="d17-panel d17-compare"><header><GitCompare size={18}/><div><small>{t.compare}</small><strong>{t.baseline} → {t.current}</strong></div></header><p>{t.baselineLead}</p><div className="d17-compare-actions"><button onClick={captureBaseline}><GitCompare size={14}/>{t.setBaseline}</button><button onClick={restoreBaseline}><RotateCcw size={14}/>{t.restoreBaseline}</button></div><div className="d17-compare-grid"><div className="d17-compare-head"/><div className="d17-compare-head">{t.baseline}</div><div className="d17-compare-head">{t.current}</div><div className="d17-compare-head">{t.change}</div><small>{t.swath}</small>{value(base.swath,'m')}{value(current.swath,'m')}{delta(current.swath,base.swath,'m')}<small>{t.alongSpacing}</small>{value(baseline.survey.along_track_ping_spacing_m,'m',2)}{value(survey.along_track_ping_spacing_m,'m',2)}{delta(survey.along_track_ping_spacing_m,baseline.survey.along_track_ping_spacing_m,'m',2)}<small>{t.acrossSpacing}</small>{value(baseline.survey.across_track.mean_spacing_m,'m',2)}{value(survey.across_track.mean_spacing_m,'m',2)}{baseline.survey.across_track.mean_spacing_m!=null&&survey.across_track.mean_spacing_m!=null?delta(survey.across_track.mean_spacing_m,baseline.survey.across_track.mean_spacing_m,'m',2):<strong>—</strong>}<small>{t.coveredWidth}</small>{value(baseline.survey.coverage.total_covered_width_m,'m',1)}{value(survey.coverage.total_covered_width_m,'m',1)}{baseline.survey.coverage.total_covered_width_m!=null&&survey.coverage.total_covered_width_m!=null?delta(survey.coverage.total_covered_width_m,baseline.survey.coverage.total_covered_width_m,'m',1):<strong>—</strong>}<small>{t.coverageState}</small><strong>{coverageLabel(baseline.survey.coverage.classification)}</strong><strong>{coverageLabel(survey.coverage.classification)}</strong><strong>{baseline.survey.coverage.classification===survey.coverage.classification?'→':'↔'}</strong><small>{t.detection}</small><strong>{detectionLabel(baseline.settings.detectionMode)}</strong><strong>{detectionLabel(detectionMode)}</strong><strong>{baseline.settings.detectionMode===detectionMode?'→':'↔'}</strong><small>{t.highDensity}</small><strong>{baseline.settings.highDensity?t.on:t.off}</strong><strong>{highDensity?t.on:t.off}</strong><strong>{baseline.settings.highDensity===highDensity?'→':'↔'}</strong></div></section>}
     <section className="d17-insight"><small>{t.compare}</small><p>{t.note}</p></section>
    </>}
   </section>
  </main>
 </div>;
}
