import { motion } from 'motion/react';
import { Activity, GitCompare, Pause, Play, RotateCcw, SlidersHorizontal, Sparkles, Waves } from 'lucide-react';
import { useMemo, useState } from 'react';

function wavePath(chirp: boolean, phase = 0) {
  const pts: string[] = [];
  for (let x = 0; x <= 760; x += 4) {
    const t = x / 760;
    const cycles = chirp ? 4 + 13 * t : 8;
    const y = 90 + Math.sin((t * cycles * Math.PI * 2) + phase) * 48 * Math.sin(Math.PI * t);
    pts.push(`${x},${y.toFixed(1)}`);
  }
  return `M ${pts.join(' L ')}`;
}

export default function SignalLab({ onBack }: { onBack: () => void }) {
  const [chirp, setChirp] = useState(true);
  const [bandwidth, setBandwidth] = useState(72);
  const [duration, setDuration] = useState(58);
  const [playing, setPlaying] = useState(true);
  const tx = useMemo(() => wavePath(chirp), [chirp]);
  const echo = useMemo(() => wavePath(chirp, .7), [chirp]);
  const compressed = Math.max(9, 72 - bandwidth * .63);

  return <div className="signal-lab">
    <div className="lab-toolbar">
      <button className="back-button" onClick={onBack}>← System map</button>
      <div className="lab-breadcrumb"><Activity size={17}/><span>Signal</span><b>/</b><strong>Waveform laboratory</strong></div>
      <div className="lab-toolbar-actions"><span className="concept-chip"><Sparkles size={13}/> illustrative</span><button onClick={() => setPlaying(v=>!v)}>{playing ? <Pause size={16}/> : <Play size={16}/>} {playing ? 'Pause' : 'Play'}</button><button><GitCompare size={16}/> Compare</button></div>
    </div>

    <div className="lab-question"><span>01 · SIGNAL</span><h1>What changes when the pulse becomes a chirp?</h1><p>Manipulate the signal. The visual chain responds immediately.</p></div>

    <div className="lab-layout">
      <aside className="control-surface">
        <div className="control-title"><SlidersHorizontal size={17}/><strong>Signal controls</strong></div>
        <label>Waveform<div className="segmented"><button className={!chirp?'on':''} onClick={()=>setChirp(false)}>CW</button><button className={chirp?'on':''} onClick={()=>setChirp(true)}>Chirp</button></div></label>
        <label>Bandwidth <output>{bandwidth}%</output><input type="range" min="10" max="100" value={bandwidth} onChange={e=>setBandwidth(+e.target.value)}/></label>
        <label>Pulse duration <output>{duration}%</output><input type="range" min="10" max="100" value={duration} onChange={e=>setDuration(+e.target.value)}/></label>
        <div className="control-readouts"><div><small>Start</small><strong>200 kHz</strong></div><div><small>End</small><strong>{chirp?'400':'200'} kHz</strong></div><div><small>Envelope</small><strong>{duration} μs</strong></div><div><small>Mode</small><strong>{chirp?'FM':'CW'}</strong></div></div>
        <button className="reset" onClick={()=>{setChirp(true);setBandwidth(72);setDuration(58)}}><RotateCcw size={15}/> Reset concept</button>
      </aside>

      <section className="visual-chain">
        <div className="chain-card transmit"><header><div><small>01 · TRANSMIT</small><strong>Outgoing waveform</strong></div><span>{chirp?'CHIRP':'CW'}</span></header><svg viewBox="0 0 760 180" preserveAspectRatio="none"><path className="gridline" d="M0 90H760"/><motion.path className="wave-path" d={tx} animate={playing?{pathLength:[0,1]}:{pathLength:1}} transition={{duration:1.6,repeat:playing?Infinity:0,ease:'linear'}}/></svg><div className="axis"><span>time →</span><span>frequency {chirp?'increases →':'constant →'}</span></div></div>
        <div className="chain-arrow"><span>water column</span><i>→</i></div>
        <div className="chain-card receive"><header><div><small>02 · RECEIVE</small><strong>Returned echo</strong></div><span>DELAYED</span></header><svg viewBox="0 0 760 180" preserveAspectRatio="none"><path className="gridline" d="M0 90H760"/><path className="echo-path" d={echo}/></svg><div className="echo-marker" style={{left:`${26+duration*.18}%`}}><i/><span>echo arrival</span></div></div>
        <div className="chain-arrow"><span>matched filter</span><i>→</i></div>
        <div className="chain-card compression"><header><div><small>03 · COMPRESS</small><strong>Resolution becomes visible</strong></div><span>OUTPUT</span></header><div className="compression-plot"><div className="ghost-peak"/><motion.div className="live-peak" animate={{width:`${compressed}%`}}/><div className="resolution-bracket" style={{width:`${compressed+8}%`}}><span>effective pulse width</span></div></div><div className="insight"><Waves size={18}/><span>{chirp?'More bandwidth → visually narrower compressed response':'CW keeps a broader illustrative response'}</span></div></div>
      </section>
    </div>
  </div>;
}
