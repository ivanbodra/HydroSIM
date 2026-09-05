import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Languages, Rotate3D, RotateCcw, Ship, Waves } from 'lucide-react';

type Lang = 'en' | 'pt';
type Harmonic = { amplitude_deg: number; period_seconds: number; phase_deg: number };
type Sample = { time_seconds: number; north_m: number; east_m: number; down_m: number; roll_deg: number; pitch_deg: number; heading_deg: number; yaw_deviation_deg: number; heave_up_m: number };
type Response = { samples: Sample[]; metadata: Record<string, string> };

const DEFAULTS = {
  heading: 20,
  speed: 3,
  duration: 12,
  roll: { amplitude_deg: 8, period_seconds: 6, phase_deg: 0 },
  pitch: { amplitude_deg: 4, period_seconds: 8, phase_deg: 30 },
  yaw: { amplitude_deg: 6, period_seconds: 10, phase_deg: 0 },
  heaveAmp: 1.2,
  heavePeriod: 7,
};

const copy = {
  en: {
    title: 'Vessel Motion', intro: 'Configure vessel motion and compare trajectory and attitude over time.', back: 'System Map', lang: 'PT-BR', reset: 'Reset',
    heading: 'Heading', speed: 'Speed', duration: 'Duration', roll: 'Roll', pitch: 'Pitch', yaw: 'Yaw', heave: 'Heave', amplitude: 'Amplitude', period: 'Period',
    trajectory: 'Vessel trajectory', attitude: 'Attitude through time', north: 'North', east: 'East', up: 'Up', current: 'Final sample',
    attitudeScale: 'Shared scale: ±20°', heaveScale: 'Scale: ±3 m',
    error: 'The motion view could not be updated. Adjust the controls or try again.',
    help: {
      roll: 'Roll is rotation about the vessel longitudinal axis.',
      pitch: 'Pitch is rotation about the vessel transverse axis.',
      yaw: 'Yaw is angular deviation about the vertical axis; Heading is the vessel direction clockwise from North.',
      heave: 'Heave is vertical translation; HydroSIM reports it positive Up.',
    },
  },
  pt: {
    title: 'Movimento da Embarcação', intro: 'Configure o movimento da embarcação e compare trajetória e atitude ao longo do tempo.', back: 'Mapa do Sistema', lang: 'EN', reset: 'Restaurar',
    heading: 'Heading', speed: 'Velocidade', duration: 'Duração', roll: 'Roll', pitch: 'Pitch', yaw: 'Yaw', heave: 'Heave', amplitude: 'Amplitude', period: 'Período',
    trajectory: 'Trajetória da embarcação', attitude: 'Atitude ao longo do tempo', north: 'Norte', east: 'Leste', up: 'Cima', current: 'Amostra final',
    attitudeScale: 'Escala comum: ±20°', heaveScale: 'Escala: ±3 m',
    error: 'Não foi possível atualizar a visualização do movimento. Ajuste os controles ou tente novamente.',
    help: {
      roll: 'Roll é a rotação em torno do eixo longitudinal da embarcação.',
      pitch: 'Pitch é a rotação em torno do eixo transversal da embarcação.',
      yaw: 'Yaw é o desvio angular em torno do eixo vertical; Heading é a direção da embarcação, medida no sentido horário a partir do Norte.',
      heave: 'Heave é a translação vertical; no HydroSIM é apresentada positiva para cima.',
    },
  },
};

function Term({ label, text }: { label: string; text: string }) {
  const [open, setOpen] = useState(false);
  return <span className="d12-term"><button type="button" onClick={() => setOpen(v => !v)} title={text}>{label} ⓘ</button>{open && <span>{text}</span>}</span>;
}

function fixedSeriesPath(samples: Sample[], key: keyof Sample, min: number, max: number, w = 660, h = 170) {
  if (!samples.length) return '';
  const span = max - min;
  return samples.map((sample, index) => {
    const value = Math.max(min, Math.min(max, Number(sample[key])));
    const x = (index / Math.max(1, samples.length - 1)) * w;
    const y = h - ((value - min) / span) * h;
    return `${index ? 'L' : 'M'}${x},${y}`;
  }).join(' ');
}

export default function VesselMotionLab({ onBack }: { onBack: () => void }) {
  const [lang, setLang] = useState<Lang>('en');
  const [heading, setHeading] = useState(DEFAULTS.heading);
  const [speed, setSpeed] = useState(DEFAULTS.speed);
  const [duration, setDuration] = useState(DEFAULTS.duration);
  const [roll, setRoll] = useState<Harmonic>({ ...DEFAULTS.roll });
  const [pitch, setPitch] = useState<Harmonic>({ ...DEFAULTS.pitch });
  const [yaw, setYaw] = useState<Harmonic>({ ...DEFAULTS.yaw });
  const [heaveAmp, setHeaveAmp] = useState(DEFAULTS.heaveAmp);
  const [heavePeriod, setHeavePeriod] = useState(DEFAULTS.heavePeriod);
  const [data, setData] = useState<Response | null>(null);
  const [error, setError] = useState(false);
  const t = copy[lang];

  useEffect(() => {
    const ac = new AbortController();
    setError(false);
    fetch('/api/v1/pedagogical/vessel-motion', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: ac.signal,
      body: JSON.stringify({
        heading_deg: heading, speed_mps: speed, start_north_m: 0, start_east_m: 0, start_down_m: 0,
        duration_seconds: duration, sample_count: 121, roll, pitch, yaw_deviation: yaw,
        heave: { amplitude_m: heaveAmp, period_seconds: heavePeriod, phase_deg: 0 },
      }),
    }).then(async r => {
      if (!r.ok) throw new Error('motion request rejected');
      return r.json() as Promise<Response>;
    }).then(setData).catch(e => { if (e.name !== 'AbortError') setError(true); });
    return () => ac.abort();
  }, [heading, speed, duration, roll, pitch, yaw, heaveAmp, heavePeriod]);

  const path = useMemo(() => {
    const samples = data?.samples ?? [];
    if (!samples.length) return [];
    const ns = samples.map(x => x.north_m), es = samples.map(x => x.east_m);
    const n0 = Math.min(...ns), n1 = Math.max(...ns), e0 = Math.min(...es), e1 = Math.max(...es);
    const dn = Math.max(1e-9, n1 - n0), de = Math.max(1e-9, e1 - e0);
    return samples.map(x => ({ x: 8 + 84 * (x.east_m - e0) / de, y: 92 - 84 * (x.north_m - n0) / dn }));
  }, [data]);

  const last = data?.samples.at(-1);
  const reset = () => {
    setHeading(DEFAULTS.heading); setSpeed(DEFAULTS.speed); setDuration(DEFAULTS.duration);
    setRoll({ ...DEFAULTS.roll }); setPitch({ ...DEFAULTS.pitch }); setYaw({ ...DEFAULTS.yaw });
    setHeaveAmp(DEFAULTS.heaveAmp); setHeavePeriod(DEFAULTS.heavePeriod);
  };
  const harmonic = (label: string, value: Harmonic, setter: (v: Harmonic) => void, help: string) => <section>
    <h3><Term label={label} text={help} /></h3>
    <label>{t.amplitude}<strong>{value.amplitude_deg.toFixed(0)}°</strong><input type="range" min="0" max="20" step="1" value={value.amplitude_deg} onChange={e => setter({ ...value, amplitude_deg: +e.target.value })} /></label>
    <label>{t.period}<strong>{value.period_seconds.toFixed(1)} s</strong><input type="range" min="2" max="16" step="0.5" value={value.period_seconds} onChange={e => setter({ ...value, period_seconds: +e.target.value })} /></label>
  </section>;

  return <div className="d12-lab">
    <header>
      <button onClick={onBack}><ArrowLeft size={16} />{t.back}</button>
      <div><span>PED-D12 · VESSEL MOTION</span><h1>{t.title}</h1><p>{t.intro}</p></div>
      <button onClick={() => setLang(lang === 'en' ? 'pt' : 'en')}><Languages size={16} />{t.lang}</button>
    </header>
    <main>
      <aside>
        <label>{t.heading}<strong>{heading.toFixed(0)}°</strong><input type="range" min="0" max="359" value={heading} onChange={e => setHeading(+e.target.value)} /></label>
        <label>{t.speed}<strong>{speed.toFixed(1)} m/s</strong><input type="range" min="0" max="8" step="0.25" value={speed} onChange={e => setSpeed(+e.target.value)} /></label>
        <label>{t.duration}<strong>{duration.toFixed(0)} s</strong><input type="range" min="4" max="30" step="1" value={duration} onChange={e => setDuration(+e.target.value)} /></label>
        {harmonic(t.roll, roll, setRoll, t.help.roll)}
        {harmonic(t.pitch, pitch, setPitch, t.help.pitch)}
        {harmonic(t.yaw, yaw, setYaw, t.help.yaw)}
        <section>
          <h3><Term label={t.heave} text={t.help.heave} /></h3>
          <label>{t.amplitude}<strong>{heaveAmp.toFixed(1)} m</strong><input type="range" min="0" max="3" step="0.1" value={heaveAmp} onChange={e => setHeaveAmp(+e.target.value)} /></label>
          <label>{t.period}<strong>{heavePeriod.toFixed(1)} s</strong><input type="range" min="2" max="16" step="0.5" value={heavePeriod} onChange={e => setHeavePeriod(+e.target.value)} /></label>
        </section>
        <button type="button" onClick={reset}><RotateCcw size={16} />{t.reset}</button>
      </aside>
      <section className="d12-stage">
        {error ? <div className="d12-error" role="status">{t.error}</div> : <>
          <div className="d12-panels">
            <article>
              <div className="d12-title"><Ship size={17} /><span>{t.trajectory}</span></div>
              <div className="d12-map"><i className="north">N</i><svg viewBox="0 0 100 100">{path.length > 1 && <polyline points={path.map(p => `${p.x},${p.y}`).join(' ')} />}{path.length > 0 && <circle cx={path.at(-1)!.x} cy={path.at(-1)!.y} r="2.2" />}</svg></div>
              <div className="d12-read"><span>{t.north}<strong>{last?.north_m.toFixed(1) ?? '—'} m</strong></span><span>{t.east}<strong>{last?.east_m.toFixed(1) ?? '—'} m</strong></span></div>
            </article>
            <article>
              <div className="d12-title"><Rotate3D size={17} /><span>{t.attitude}</span></div>
              <svg className="d12-series" viewBox="0 0 660 170" role="img" aria-label={t.attitudeScale}>
                <line x1="0" y1="85" x2="660" y2="85" stroke="currentColor" strokeOpacity="0.14" />
                <path className="roll" d={fixedSeriesPath(data?.samples ?? [], 'roll_deg', -20, 20)} />
                <path className="pitch" d={fixedSeriesPath(data?.samples ?? [], 'pitch_deg', -20, 20)} />
                <path className="yaw" d={fixedSeriesPath(data?.samples ?? [], 'yaw_deviation_deg', -20, 20)} />
              </svg>
              <div className="d12-legend"><span className="roll">Roll</span><span className="pitch">Pitch</span><span className="yaw">Yaw</span><span>{t.attitudeScale}</span></div>
            </article>
          </div>
          <article className="d12-heave">
            <div className="d12-title"><Waves size={17} /><span><Term label={t.heave} text={t.help.heave} /></span></div>
            <svg className="d12-series" viewBox="0 0 660 120" role="img" aria-label={t.heaveScale}>
              <line x1="0" y1="60" x2="660" y2="60" stroke="currentColor" strokeOpacity="0.14" />
              <path className="heave" d={fixedSeriesPath(data?.samples ?? [], 'heave_up_m', -3, 3, 660, 120)} />
            </svg>
            <div className="d12-read"><span>{t.current}<strong>{last?.heading_deg.toFixed(1) ?? '—'}° Heading</strong></span><span>{t.up}<strong>{last?.heave_up_m.toFixed(2) ?? '—'} m</strong></span><span>{t.heaveScale}</span></div>
          </article>
        </>}
      </section>
    </main>
  </div>;
}
