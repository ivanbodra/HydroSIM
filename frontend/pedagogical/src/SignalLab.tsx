import { useMemo } from 'react';

export type SignalParameters = {
  waveform: 'cw' | 'lfm';
  centerFrequencyKhz: number;
  durationMs: number;
  bandwidthKhz: number;
  sweepDirection: 'up' | 'down';
  envelope: 'rectangular' | 'tukey';
};

export type SignalSeries = {
  x: number[];
  y: number[];
};

export type SignalRenderModel = {
  cwPassband: SignalSeries;
  lfmPassband: SignalSeries;
  cwInstantaneousFrequencyKhz: SignalSeries;
  lfmInstantaneousFrequencyKhz: SignalSeries;
  matchedFilter: SignalSeries;
};

type Props = {
  locale: 'en' | 'pt-BR';
  parameters: SignalParameters;
  data: SignalRenderModel | null;
  loading?: boolean;
  onParametersChange: (next: SignalParameters) => void;
  onBack: () => void;
};

const copy = {
  en: {
    back: '← System map',
    kicker: 'PED-D2 · SIGNAL',
    title: 'See one acoustic event become a waveform, a return, and a processed response.',
    subtitle: 'Change the transmitted signal and follow the same event from transmission to processing.',
    controls: 'Signal controls',
    waveform: 'Waveform',
    frequency: 'Centre frequency',
    duration: 'Pulse duration',
    bandwidth: 'LFM bandwidth',
    transmit: '01 · TRANSMIT',
    return: '02 · RETURN',
    process: '03 · PROCESS',
    passband: 'Acoustic passband waveform',
    instant: 'Instantaneous frequency',
    matched: 'Matched-filter response',
    loading: 'Updating scientific model…',
  },
  'pt-BR': {
    back: '← Mapa do sistema',
    kicker: 'PED-D2 · SINAL',
    title: 'Veja um mesmo evento acústico se tornar forma de onda, retorno e resposta processada.',
    subtitle: 'Altere o sinal transmitido e acompanhe o mesmo evento da transmissão ao processamento.',
    controls: 'Controles do sinal',
    waveform: 'Forma de onda',
    frequency: 'Frequência central',
    duration: 'Duração do pulso',
    bandwidth: 'Largura de banda LFM',
    transmit: '01 · TRANSMISSÃO',
    return: '02 · RETORNO',
    process: '03 · PROCESSAMENTO',
    passband: 'Forma de onda acústica em banda passante',
    instant: 'Frequência instantânea',
    matched: 'Resposta do filtro casado',
    loading: 'Atualizando modelo científico…',
  },
} as const;

function path(series: SignalSeries | undefined, width = 720, height = 170): string {
  if (!series || series.x.length < 2 || series.x.length !== series.y.length) return '';
  const minX = Math.min(...series.x);
  const maxX = Math.max(...series.x);
  const minY = Math.min(...series.y);
  const maxY = Math.max(...series.y);
  const dx = maxX - minX || 1;
  const dy = maxY - minY || 1;
  return series.x
    .map((x, i) => {
      const px = ((x - minX) / dx) * width;
      const py = height - ((series.y[i] - minY) / dy) * height;
      return `${i === 0 ? 'M' : 'L'} ${px.toFixed(2)} ${py.toFixed(2)}`;
    })
    .join(' ');
}

function Trace({ series, label }: { series?: SignalSeries; label: string }) {
  const d = useMemo(() => path(series), [series]);
  return (
    <div className="signal-trace">
      <div className="trace-label">{label}</div>
      <svg viewBox="0 0 720 170" preserveAspectRatio="none" role="img" aria-label={label}>
        <path className="trace-axis" d="M 0 85 L 720 85" />
        <path className="trace-line" d={d} />
      </svg>
    </div>
  );
}

export default function SignalLab({
  locale,
  parameters,
  data,
  loading = false,
  onParametersChange,
  onBack,
}: Props) {
  const t = copy[locale];
  const patch = (changes: Partial<SignalParameters>) => onParametersChange({ ...parameters, ...changes });
  const selectedPassband = parameters.waveform === 'cw' ? data?.cwPassband : data?.lfmPassband;
  const selectedFrequency =
    parameters.waveform === 'cw'
      ? data?.cwInstantaneousFrequencyKhz
      : data?.lfmInstantaneousFrequencyKhz;

  return (
    <main className="signal-lab">
      <header className="signal-toolbar">
        <button className="back-button" onClick={onBack}>{t.back}</button>
        <span className="breadcrumb">HydroSIM / {t.kicker}</span>
      </header>

      <section className="signal-question">
        <span>{t.kicker}</span>
        <h1>{t.title}</h1>
        <p>{t.subtitle}</p>
      </section>

      <div className="signal-layout">
        <aside className="signal-controls">
          <strong>{t.controls}</strong>
          <label>
            {t.waveform}
            <div className="segmented">
              <button className={parameters.waveform === 'cw' ? 'active' : ''} onClick={() => patch({ waveform: 'cw' })}>CW</button>
              <button className={parameters.waveform === 'lfm' ? 'active' : ''} onClick={() => patch({ waveform: 'lfm' })}>LFM / Chirp</button>
            </div>
          </label>
          <label>{t.frequency}<output>{parameters.centerFrequencyKhz.toFixed(0)} kHz</output>
            <input type="range" min="50" max="700" step="10" value={parameters.centerFrequencyKhz} onChange={(e) => patch({ centerFrequencyKhz: Number(e.target.value) })} />
          </label>
          <label>{t.duration}<output>{parameters.durationMs.toFixed(1)} ms</output>
            <input type="range" min="0.1" max="5" step="0.1" value={parameters.durationMs} onChange={(e) => patch({ durationMs: Number(e.target.value) })} />
          </label>
          <label className={parameters.waveform === 'cw' ? 'disabled-control' : ''}>{t.bandwidth}<output>{parameters.bandwidthKhz.toFixed(0)} kHz</output>
            <input disabled={parameters.waveform === 'cw'} type="range" min="10" max="300" step="10" value={parameters.bandwidthKhz} onChange={(e) => patch({ bandwidthKhz: Number(e.target.value) })} />
          </label>
          {loading && <div className="loading-chip">{t.loading}</div>}
        </aside>

        <section className="signal-story">
          <div className="flow-strip"><span>TRANSMIT</span><i/><span>RETURN</span><i/><span>PROCESS</span></div>
          <article className="signal-card hero-card">
            <header><small>{t.transmit}</small><strong>{t.passband}</strong><b>{parameters.waveform.toUpperCase()}</b></header>
            <Trace series={selectedPassband} label={t.passband} />
          </article>
          <div className="story-arrow">↓ <span>same event / mesmo evento</span></div>
          <div className="signal-pair">
            <article className="signal-card">
              <header><small>{t.return}</small><strong>{t.instant}</strong></header>
              <Trace series={selectedFrequency} label={t.instant} />
            </article>
            <article className="signal-card">
              <header><small>{t.process}</small><strong>{t.matched}</strong></header>
              <Trace series={data?.matchedFilter} label={t.matched} />
            </article>
          </div>
        </section>
      </div>
    </main>
  );
}
