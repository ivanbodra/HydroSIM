import { AlertTriangle, CheckCircle2, Eye, LockKeyhole, RotateCcw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

type Family='roll'|'pitch'|'yaw'|'latency';
type Point={coordinate_m:number;vertical_difference_m:number};
type Evidence={evidence_id:string;before_residual:Point[];after_residual:Point[];before_rms_m:number;after_rms_m:number;improvement_fraction:number;structured_fraction:number;opposite_sense:boolean};
type Result={error_family:Family;correction_unit:'degrees'|'milliseconds';candidate_correction:number;assessment:'Adequate'|'Suboptimal'|'Inadequate';reasons:string[];calibration:Evidence;holdout:Evidence;inherited_warnings:string[];submitted:boolean;estimation_error:number|null;estimation_error_semantics:string|null};
type Assessment=Result['assessment'];
const families:Family[]=['roll','pitch','yaw','latency'];

export default function PatchAssessmentLab(){
  const [lang,setLang]=useState<'en'|'pt'>('en');
  const [family,setFamily]=useState<Family>('roll');
  const [candidate,setCandidate]=useState(0);
  const [choice,setChoice]=useState<Assessment|null>(null);
  const [submitted,setSubmitted]=useState(false);
  const [data,setData]=useState<Result|null>(null);
  const [error,setError]=useState(false);
  const pt=lang==='pt', limit=family==='latency'?400:4, step=family==='latency'?5:.1;
  useEffect(()=>{setCandidate(0);setChoice(null);setSubmitted(false)},[family]);
  useEffect(()=>{
    const ac=new AbortController();setError(false);
    fetch('/api/v1/pedagogical/patch-test/assessment',{method:'POST',headers:{'content-type':'application/json'},signal:ac.signal,body:JSON.stringify({error_family:family,candidate_correction:candidate,search_min:-limit,search_max:limit,submitted})})
      .then(r=>{if(!r.ok)throw new Error();return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(true)});
    return()=>ac.abort();
  },[family,candidate,submitted,limit]);
  const all=[...(data?.calibration.before_residual??[]),...(data?.calibration.after_residual??[]),...(data?.holdout.before_residual??[]),...(data?.holdout.after_residual??[])];
  const bounds=useMemo(()=>{
    const xs=all.map(p=>p.coordinate_m), ys=all.map(p=>p.vertical_difference_m), max=Math.max(...ys.map(Math.abs),.01);
    return{x:[Math.min(...xs,0),Math.max(...xs,1)] as const,y:[-max,max] as const};
  },[data]);
  const map=(v:number,[a,b]:readonly[number,number],lo:number,hi:number)=>lo+(v-a)/Math.max(b-a,1e-9)*(hi-lo);
  const path=(points:Point[])=>points.map((p,i)=>`${i?'L':'M'}${map(p.coordinate_m,bounds.x,42,558).toFixed(1)},${map(p.vertical_difference_m,bounds.y,168,18).toFixed(1)}`).join(' ');
  const unit=data?.correction_unit==='milliseconds'?'ms':'°';
  const reasonPt:Record<string,string>={
    'candidate improves calibration and independent holdout evidence without overcorrection':'a candidata melhora a calibração e a evidência independente sem sobrecorreção',
    'candidate does not improve both calibration and independent holdout evidence':'a candidata não melhora simultaneamente a calibração e a evidência independente',
    'candidate introduces an opposite-sense residual consistent with overcorrection':'a candidata introduz resíduo de sentido oposto compatível com sobrecorreção',
    'improvement, residual structure, or conditioning does not meet the configured criterion':'a melhora, a estrutura residual ou o condicionamento não atende ao critério configurado',
    'acquisition evidence does not identify and validate the target parameter':'a aquisição não identifica nem valida o parâmetro-alvo',
  };
  const EvidencePanel=({title,e}:{title:string;e:Evidence})=><section className="p5-evidence">
    <div className="p5-evidence-head"><div><small>{title}</small><strong>{pt?'Antes e depois — mesma escala':'Before and after — same scale'}</strong></div><div className="p5-rms"><span>{e.before_rms_m.toFixed(3)} m</span><b>→</b><strong>{e.after_rms_m.toFixed(3)} m</strong></div></div>
    <svg viewBox="0 0 600 190" role="img" aria-label={title}>
      <line x1="42" y1="93" x2="558" y2="93" className="p5-zero"/>
      <path d={path(e.before_residual)} className="p5-before"/>
      <path d={path(e.after_residual)} className="p5-after"/>
    </svg>
    <div className="p5-metrics"><span>{pt?'Melhora':'Improvement'} <b>{(100*e.improvement_fraction).toFixed(0)}%</b></span><span>{pt?'Estrutura residual':'Residual structure'} <b>{(100*e.structured_fraction).toFixed(0)}%</b></span>{e.opposite_sense&&<span className="bad"><AlertTriangle/> {pt?'sentido oposto':'opposite sense'}</span>}</div>
  </section>;
  return <main className="p5-lab">
    <header><div><span>P5 · {pt?'AVALIAÇÃO E VALIDAÇÃO':'ASSESSMENT & VALIDATION'}</span><h1>{pt?'A candidata melhora evidência independente?':'Does the candidate improve independent evidence?'}</h1></div><button onClick={()=>setLang(v=>v==='en'?'pt':'en')}>{pt?'EN':'PT-BR'}</button></header>
    <div className="p5-layout">
      <aside className="p5-controls">
        <div className="p5-family">{families.map(f=><button key={f} className={family===f?'active':''} onClick={()=>setFamily(f)}>{f==='yaw'?'Yaw / Heading':f}</button>)}</div>
        <label>{pt?'Correção estimada':'Estimated correction'}<output>{candidate.toFixed(family==='latency'?0:1)} {unit}</output><input type="range" min={-limit} max={limit} step={step} value={candidate} onChange={e=>{setCandidate(+e.target.value);setChoice(null);setSubmitted(false)}}/></label>
        <div className="p5-lock"><LockKeyhole/><div><small>OBSERVED</small><strong>{pt?'Linhas bloqueadas':'Locked lines'}</strong></div></div>
        <fieldset className="p5-choice"><legend>{pt?'Sua avaliação':'Your assessment'}</legend>{(['Adequate','Suboptimal','Inadequate'] as Assessment[]).map(v=><button type="button" key={v} className={choice===v?'active':''} onClick={()=>{setChoice(v);setSubmitted(false)}}>{pt?({Adequate:'Adequada',Suboptimal:'Subótima',Inadequate:'Inadequada'} as Record<Assessment,string>)[v]:v}</button>)}</fieldset>
        <button className="p5-reset" onClick={()=>{setCandidate(0);setChoice(null);setSubmitted(false)}}><RotateCcw/>{pt?'Reiniciar':'Reset'}</button>
        <button className="p5-submit" disabled={!choice} onClick={()=>setSubmitted(true)}><Eye/>{pt?'Enviar avaliação':'Submit assessment'}</button>
      </aside>
      <div className="p5-workspace">
        {error?<div className="p5-error"><AlertTriangle/>{pt?'API indisponível':'API unavailable'}</div>:data&&<>
          <div className="p5-legend"><span className="before">{pt?'Antes':'Before'}</span><span className="after">{pt?'Candidata atual':'Current candidate'}</span></div>
          <EvidencePanel title={pt?'PAR DE CALIBRAÇÃO':'CALIBRATION PAIR'} e={data.calibration}/>
          <EvidencePanel title={pt?'HOLDOUT INDEPENDENTE':'INDEPENDENT HOLDOUT'} e={data.holdout}/>
          {!submitted?<div className="p5-gate"><LockKeyhole/><strong>{choice?(pt?'Envie sua avaliação para comparar e revelar Truth':'Submit your assessment to compare and reveal Truth'):(pt?'Classifique pela evidência antes de revelar Truth':'Judge the evidence before revealing Truth')}</strong></div>:<section className={`p5-verdict ${data.assessment.toLowerCase()}`}>
            <div><CheckCircle2/><small>{pt?'SUA ESCOLHA → AVALIAÇÃO DA API':'YOUR CHOICE → API ASSESSMENT'}</small><h2>{choice} → {data.assessment}</h2><p>{pt?(reasonPt[data.reasons[0]]??data.reasons[0]):data.reasons[0]}</p></div>
            <div className="p5-truth"><small>ESTIMATED − TRUTH</small><strong>{data.estimation_error?.toFixed(family==='latency'?1:3)} {unit}</strong><span>{pt?'Diagnóstico após envio; não é RMS nem TPU':'Post-submit diagnostic; not RMS or TPU'}</span></div>
          </section>}
          {!!data.inherited_warnings.length&&<section className="p5-warnings"><AlertTriangle/><div><strong>{pt?'Avisos herdados':'Inherited warnings'}</strong>{data.inherited_warnings.map((w,i)=><p key={i}>{w}</p>)}</div></section>}
        </>}
      </div>
    </div>
  </main>;
}
