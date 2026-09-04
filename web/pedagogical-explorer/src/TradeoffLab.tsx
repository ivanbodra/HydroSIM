import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Gauge, Languages, Radar, Waves } from 'lucide-react';
import './tradeoff-lab.css';

type Lang='en'|'pt';
type SpacingMode='equiangular'|'equidistant';
type Beam={endpoint_across_track_m:number;footprint:{effective_across_track_width_m:number}};
type EchoResponse={mbes:{beams:Beam[];adjacent_across_track_spacings_m:number[];geometric_beam_center_swath_width_m:number}};
type Sector={sector_id:string;centre_across_track_deg:number;across_track_min_deg:number;across_track_max_deg:number;frequency_khz:number;pulse_duration_ms:number;tx_delay_ms:number;relative_power:number};
type MultiResponse={sectors:Array<Sector&{wavelength_m:number;tx_time_s:number;tx_end_time_s:number}>;transmit_groups:string[][]};

const copy={
 en:{title:'Acquisition trade-offs',lead:'Change acquisition choices and compare their canonical consequences in one view.',back:'System map',controls:'Linked controls',depth:'Depth',beams:'Beam count',sector:'Angular sector',pulse:'Pulse duration',frequency:'Sector frequency',beamwidth:'RX beamwidth',spacingMode:'Beam spacing',equiangular:'Equiangular',equidistant:'Equidistant',geometry:'Coverage geometry',swath:'Beam-centre swath',spacing:'Mean adjacent spacing',footprint:'Nadir footprint width',signal:'Transmit configuration',wavelength:'Wavelength',groups:'TX groups',window:'TX event span',compare:'What changed?',note:'Beam spacing and RX beamwidth now remain learner-controlled all the way to the canonical D8 geometry. Vessel speed, ping-rate and survey-product trade-offs remain unavailable until their canonical integration contract exists.',port:'Port +',starboard:'Starboard −',loading:'Updating canonical acquisition state…',invalid:'The selected combination is outside a canonical API validity domain.'},
 pt:{title:'Compromissos da aquisição',lead:'Altere escolhas da aquisição e compare suas consequências canônicas em uma única visão.',back:'Mapa do sistema',controls:'Controles vinculados',depth:'Profundidade',beams:'Número de feixes',sector:'Setor angular',pulse:'Duração do pulso',frequency:'Frequência dos setores',beamwidth:'Largura do feixe RX',spacingMode:'Espaçamento dos feixes',equiangular:'Equiangular',equidistant:'Equidistante',geometry:'Geometria de cobertura',swath:'Faixa entre centros de feixe',spacing:'Espaçamento adjacente médio',footprint:'Largura da pegada no nadir',signal:'Configuração de transmissão',wavelength:'Comprimento de onda',groups:'Grupos TX',window:'Janela de eventos TX',compare:'O que mudou?',note:'O espaçamento dos feixes e a largura do feixe RX agora permanecem sob controle do aluno até a geometria canônica de D8. Velocidade da embarcação, taxa de ping e compromissos no produto do levantamento permanecem indisponíveis até existir o respectivo contrato canônico de integração.',port:'Bombordo +',starboard:'Boreste −',loading:'Atualizando estado canônico da aquisição…',invalid:'A combinação selecionada está fora do domínio de validade de uma API canônica.'}
};

export default function TradeoffLab({onBack}:{onBack:()=>void}){
 const[lang,setLang]=useState<Lang>('en');
 const[depth,setDepth]=useState(100);
 const[beams,setBeams]=useState(15);
 const[sector,setSector]=useState(60);
 const[pulse,setPulse]=useState(.5);
 const[frequency,setFrequency]=useState(300);
 const[beamwidth,setBeamwidth]=useState(1);
 const[spacingMode,setSpacingMode]=useState<SpacingMode>('equiangular');
 const[echo,setEcho]=useState<EchoResponse|null>(null);
 const[multi,setMulti]=useState<MultiResponse|null>(null);
 const[error,setError]=useState(false);
 const t=copy[lang];

 useEffect(()=>{
  const ac=new AbortController();setError(false);
  const sectors:Sector[]=[
   {sector_id:'port',centre_across_track_deg:sector*.58,across_track_min_deg:sector*.18,across_track_max_deg:sector,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:0,relative_power:.85},
   {sector_id:'centre',centre_across_track_deg:0,across_track_min_deg:-sector*.2,across_track_max_deg:sector*.2,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:.35,relative_power:1},
   {sector_id:'starboard',centre_across_track_deg:-sector*.58,across_track_min_deg:-sector,across_track_max_deg:-sector*.18,frequency_khz:frequency,pulse_duration_ms:pulse,tx_delay_ms:0,relative_power:.85}
  ];
  Promise.all([
   fetch('/api/v1/pedagogical/echosounders',{method:'POST',headers:{'Content-Type':'application/json'},signal:ac.signal,body:JSON.stringify({selected_system:'mbes',vertical_separation_m:depth,start_depth_m:0,sound_speed_mps:1500,pulse_duration_ms:pulse,transmit_along_track_beamwidth_deg:2,receive_across_track_beamwidth_deg:beamwidth,mbes_beam_count:beams,minimum_angle_deg:-sector,maximum_angle_deg:sector,spacing_method:spacingMode})}),
   fetch('/api/v1/pedagogical/multisector',{method:'POST',headers:{'Content-Type':'application/json'},signal:ac.signal,body:JSON.stringify({tx_time_s:10,sound_speed_mps:1500,sectors})})
  ]).then(async([a,b])=>{if(!a.ok||!b.ok)throw new Error('canonical API rejected configuration');setEcho(await a.json());setMulti(await b.json())}).catch(e=>{if(e.name!=='AbortError'){setEcho(null);setMulti(null);setError(true)}});
  return()=>ac.abort()
 },[depth,beams,sector,pulse,frequency,beamwidth,spacingMode]);

 const mbes=echo?.mbes;
 const meanSpacing=useMemo(()=>{const x=mbes?.adjacent_across_track_spacings_m??[];return x.length?x.reduce((a,b)=>a+Math.abs(b),0)/x.length:0},[mbes]);
 const nadir=mbes?.beams[Math.floor((mbes?.beams.length??1)/2)];
 const wavelength=multi?.sectors[1]?.wavelength_m??0;
 const txSpan=useMemo(()=>{const s=multi?.sectors??[];return s.length?(Math.max(...s.map(x=>x.tx_end_time_s))-Math.min(...s.map(x=>x.tx_time_s)))*1000:0},[multi]);
 const extent=Math.max(1,...(mbes?.beams.map(b=>Math.abs(b.endpoint_across_track_m))??[1]));

 return <div className="d17-lab"><header className="d17-toolbar"><button onClick={onBack}><ArrowLeft size={16}/>{t.back}</button><div><Gauge size={18}/><strong>PED-D17 · Survey Coverage & Acquisition Trade-offs</strong></div><button onClick={()=>setLang(v=>v==='en'?'pt':'en')}><Languages size={16}/>{lang==='en'?'PT-BR':'EN'}</button></header><section className="d17-question"><span>17 · INTEGRATED SURVEY</span><h1>{t.title}</h1><p>{t.lead}</p></section><main className="d17-grid"><aside className="d17-controls"><h2>{t.controls}</h2><label>{t.depth}<output>{depth} m</output><input type="range" min="20" max="300" step="10" value={depth} onChange={e=>setDepth(+e.target.value)}/></label><label>{t.beams}<output>{beams}</output><input type="range" min="3" max="31" step="2" value={beams} onChange={e=>setBeams(+e.target.value)}/></label><label>{t.sector}<output>±{sector}°</output><input type="range" min="20" max="70" step="5" value={sector} onChange={e=>setSector(+e.target.value)}/></label><label>{t.beamwidth}<output>{beamwidth.toFixed(1)}°</output><input type="range" min="0.5" max="4" step="0.5" value={beamwidth} onChange={e=>setBeamwidth(+e.target.value)}/></label><label>{t.spacingMode}<select value={spacingMode} onChange={e=>setSpacingMode(e.target.value as SpacingMode)}><option value="equiangular">{t.equiangular}</option><option value="equidistant">{t.equidistant}</option></select></label><label>{t.pulse}<output>{pulse.toFixed(2)} ms</output><input type="range" min="0.1" max="1.5" step="0.1" value={pulse} onChange={e=>setPulse(+e.target.value)}/></label><label>{t.frequency}<output>{frequency} kHz</output><input type="range" min="100" max="500" step="25" value={frequency} onChange={e=>setFrequency(+e.target.value)}/></label></aside><section className="d17-stage">{error?<div className="d17-state">{t.invalid}</div>:!echo||!multi?<div className="d17-state">{t.loading}</div>:<><section className="d17-panel"><header><Radar size={18}/><div><small>{t.geometry}</small><strong>{t.port} ← NADIR → {t.starboard}</strong></div></header><div className="d17-swath"><i className="centre"/>{mbes?.beams.map((b,i)=><i key={i} className="beam" style={{left:`${50-(b.endpoint_across_track_m/extent)*44}%`}}/>)}</div><div className="d17-readouts"><div><small>{t.swath}</small><strong>{mbes?.geometric_beam_center_swath_width_m.toFixed(1)} m</strong></div><div><small>{t.spacing}</small><strong>{meanSpacing.toFixed(1)} m</strong></div><div><small>{t.footprint}</small><strong>{nadir?.footprint.effective_across_track_width_m.toFixed(2)} m</strong></div></div></section><section className="d17-panel"><header><Waves size={18}/><div><small>{t.signal}</small><strong>{frequency} kHz · {pulse.toFixed(2)} ms</strong></div></header><div className="d17-signal"><div><small>{t.wavelength}</small><strong>{(wavelength*1000).toFixed(2)} mm</strong></div><div><small>{t.groups}</small><strong>{multi.transmit_groups.length}</strong></div><div><small>{t.window}</small><strong>{txSpan.toFixed(2)} ms</strong></div></div></section><section className="d17-insight"><small>{t.compare}</small><p>{t.note}</p></section></>}</section></main></div>
}
