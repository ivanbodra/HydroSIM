import { AlertTriangle, ArrowDown, Eye, EyeOff, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
type Family = "roll" | "pitch" | "yaw" | "latency" | "confounded";
type Lang = "en" | "pt";
type Point = {
  true_x_m: number;
  true_y_m: number;
  true_z_m: number;
  configured_x_m: number;
  configured_y_m: number;
  configured_z_m: number;
  horizontal_residual_m: number;
  vertical_residual_m: number;
};
type Run = {
  id: string;
  heading_deg: number;
  speed_mps: number;
  points: Point[];
};
type Response = {
  error_family: Family;
  likely_classification: Family;
  evidence_sufficient: boolean;
  comparison_region: "outer_swath" | "near_nadir" | "common_outer_swath";
  geometry_description: string;
  runs: Run[];
};
const API_BASE =
  (import.meta.env.VITE_HYDROSIM_API_BASE as string | undefined) ??
  "http://127.0.0.1:8000";
const families: Family[] = ["roll", "pitch", "yaw", "latency"];
const copy = {
  en: {
    fundamentals: "FUNDAMENTALS",
    alongTrack: "along-track x",
    acrossTrack: "across-track y",
    depth: "depth z",
    description: {
      roll: "reciprocal coincident lines over a flat seabed",
      pitch: "reciprocal coincident lines over an along-track slope",
      yaw: "same-direction offset parallel lines over a cross-track feature or slope",
      latency:
        "same-direction lines at different speeds over an along-track slope",
      confounded: "reciprocal lines with combined angular residuals",
    },
    title: "Patch Test · Error signatures",
    question:
      "Which residual creates this disagreement—and does the geometry support that diagnosis?",
    geometry: "SURVEY GEOMETRY",
    signature: "RECONSTRUCTED SIGNATURE",
    support: "Show common support",
    reference: "Teaching reference",
    paired: "Paired runs",
    magnitude: "Hidden mismatch",
    slope: "Terrain slope",
    slow: "Slow run",
    fast: "Fast run",
    combined: "Combined case",
    reset: "Reset",
    updating: "Updating from Scientific Core…",
    retry: "Core unavailable · retry",
    adequate: "Evidence supports this diagnosis",
    insufficient: "Evidence is insufficient or confounded",
    compare: {
      outer_swath: "Compare outer swath",
      near_nadir: "Compare near nadir",
      common_outer_swath: "Compare common outer-swath overlap",
    },
    family: {
      roll: "Roll",
      pitch: "Pitch",
      yaw: "Yaw / Heading",
      latency: "Latency",
      confounded: "Combined",
    },
    run: "Run",
    residual: "maximum disagreement",
  },
  pt: {
    fundamentals: "FUNDAMENTOS",
    alongTrack: "x longitudinal",
    acrossTrack: "y transversal",
    depth: "profundidade z",
    description: {
      roll: "linhas recíprocas coincidentes sobre fundo plano",
      pitch: "linhas recíprocas coincidentes sobre declive longitudinal",
      yaw: "linhas paralelas afastadas e no mesmo sentido sobre feição ou declive transversal",
      latency:
        "linhas no mesmo sentido com velocidades diferentes sobre declive longitudinal",
      confounded: "linhas recíprocas com resíduos angulares combinados",
    },
    title: "Patch Test · Assinaturas de erro",
    question:
      "Qual resíduo cria esta discordância — e a geometria sustenta esse diagnóstico?",
    geometry: "GEOMETRIA DO LEVANTAMENTO",
    signature: "ASSINATURA RECONSTRUÍDA",
    support: "Mostrar suporte comum",
    reference: "Referência didática",
    paired: "Linhas pareadas",
    magnitude: "Desajuste oculto",
    slope: "Inclinação do terreno",
    slow: "Linha lenta",
    fast: "Linha rápida",
    combined: "Caso combinado",
    reset: "Restaurar",
    updating: "Atualizando pelo Núcleo Científico…",
    retry: "Núcleo indisponível · tentar novamente",
    adequate: "A evidência sustenta este diagnóstico",
    insufficient: "A evidência é insuficiente ou está confundida",
    compare: {
      outer_swath: "Comparar faixa externa",
      near_nadir: "Comparar próximo ao nadir",
      common_outer_swath: "Comparar sobreposição externa comum",
    },
    family: {
      roll: "Roll",
      pitch: "Pitch",
      yaw: "Yaw / Proa",
      latency: "Latência",
      confounded: "Combinado",
    },
    run: "Linha",
    residual: "discordância máxima",
  },
};
const range = (v: number[]) => {
  const lo = Math.min(...v),
    hi = Math.max(...v),
    s = Math.max(hi - lo, 1);
  return [lo - s * 0.08, hi + s * 0.08] as const;
};
function Geometry({
  data,
  paired,
  t,
}: {
  data: Response;
  paired: boolean;
  t: typeof copy.en;
}) {
  const runs = paired ? data.runs : data.runs.slice(0, 1),
    yaw = data.error_family === "yaw";
  return (
    <svg
      className="patch-geometry"
      viewBox="0 0 720 360"
      role="img"
      aria-label={t.description[data.error_family]}
    >
      <defs>
        <marker
          id="patch-arrow"
          markerWidth="8"
          markerHeight="8"
          refX="6"
          refY="3"
          orient="auto"
        >
          <path d="M0,0 L0,6 L7,3 z" />
        </marker>
      </defs>
      <path
        className="patch-feature"
        d={
          yaw
            ? "M90 252 C230 205 320 282 445 220 S620 215 680 188"
            : "M55 267 L210 267 L355 226 L680 226"
        }
      />
      {data.comparison_region === "outer_swath" && (
        <>
          <rect
            className="patch-support"
            x="52"
            y="85"
            width="172"
            height="190"
          />
          <rect
            className="patch-support"
            x="496"
            y="85"
            width="172"
            height="190"
          />
        </>
      )}
      {data.comparison_region === "near_nadir" && (
        <rect
          className="patch-support"
          x="303"
          y="76"
          width="114"
          height="196"
        />
      )}
      {data.comparison_region === "common_outer_swath" && (
        <rect
          className="patch-support"
          x="286"
          y="72"
          width="148"
          height="206"
        />
      )}
      {runs.map((run, i) => {
        const yy = yaw ? 118 + i * 94 : 118 + i * 80,
          reverse = run.heading_deg > 90 && run.heading_deg < 270;
        return (
          <g key={run.id} className={`patch-run run-${i}`}>
            <line
              x1={reverse ? 635 : 85}
              y1={yy}
              x2={reverse ? 85 : 635}
              y2={yy}
              markerEnd="url(#patch-arrow)"
            />
            <circle cx={reverse ? 550 : 170} cy={yy} r="13" />
            <text x={reverse ? 510 : 190} y={yy - 14}>
              {t.run} {run.id}
            </text>
            <text x={reverse ? 510 : 190} y={yy + 25}>
              {run.heading_deg.toFixed(0)}° · {run.speed_mps.toFixed(1)} m/s
            </text>
          </g>
        );
      })}
      <text className="patch-region-label" x="360" y="330" textAnchor="middle">
        {t.compare[data.comparison_region]}
      </text>
    </svg>
  );
}
function Signature({
  data,
  paired,
  showTruth,
  t,
}: {
  data: Response;
  paired: boolean;
  showTruth: boolean;
  t: typeof copy.en;
}) {
  const runs = paired ? data.runs : data.runs.slice(0, 1),
    points = runs.flatMap((r) => r.points),
    profile = data.error_family === "pitch" || data.error_family === "latency",
    x = (p: Point, truth = false) =>
      profile
        ? truth
          ? p.true_x_m
          : p.configured_x_m
        : truth
          ? p.true_y_m
          : p.configured_y_m,
    z = (p: Point, truth = false) => (truth ? p.true_z_m : p.configured_z_m),
    [x0, x1] = range(points.flatMap((p) => [x(p), x(p, true)])),
    [z0, z1] = range(points.flatMap((p) => [z(p), z(p, true)])),
    sx = (v: number) => 55 + ((v - x0) / (x1 - x0)) * 610,
    sy = (v: number) => 48 + ((v - z0) / (z1 - z0)) * 242,
    path = (run: Run, truth = false) =>
      run.points
        .map(
          (p, i) =>
            `${i ? "L" : "M"} ${sx(x(p, truth)).toFixed(1)} ${sy(z(p, truth)).toFixed(1)}`,
        )
        .join(" "),
    max = Math.max(
      ...points.map((p) =>
        Math.hypot(p.horizontal_residual_m, p.vertical_residual_m),
      ),
    );
  return (
    <div className="patch-signature-wrap">
      <svg
        className="patch-signature"
        viewBox="0 0 720 340"
        role="img"
        aria-label={`${t.residual}: ${max.toFixed(2)} m`}
      >
        {[0, 1, 2, 3].map((i) => (
          <line
            key={i}
            className="patch-grid"
            x1="55"
            x2="665"
            y1={48 + i * 80}
            y2={48 + i * 80}
          />
        ))}
        {showTruth &&
          runs.map((r) => (
            <path key={`t-${r.id}`} className="patch-truth" d={path(r, true)} />
          ))}
        {runs.map((r, i) => (
          <path
            key={r.id}
            className={`patch-configured run-${i}`}
            d={path(r)}
          />
        ))}
        <text x="58" y="28">
          {profile ? t.alongTrack : t.acrossTrack} (m)
        </text>
        <text transform="translate(20 210) rotate(-90)">{t.depth} (m)</text>
      </svg>
      <div className="patch-residual">
        <span>Δ</span>
        <div>
          <small>{t.residual}</small>
          <strong>{max.toFixed(2)} m</strong>
        </div>
      </div>
    </div>
  );
}
export default function PatchSignatureLab() {
  const [lang, setLang] = useState<Lang>("en"),
    [family, setFamily] = useState<Family>("roll"),
    [angle, setAngle] = useState(1),
    [latency, setLatency] = useState(100),
    [slope, setSlope] = useState(15),
    [slow, setSlow] = useState(2),
    [fast, setFast] = useState(6),
    [paired, setPaired] = useState(true),
    [showSupport, setShowSupport] = useState(true),
    [showTruth, setShowTruth] = useState(false),
    [data, setData] = useState<Response | null>(null),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(false),
    [nonce, setNonce] = useState(0);
  const t = copy[lang];
  useEffect(() => {
    const f = (e: Event) => {
      const n = (e as CustomEvent<Lang>).detail;
      if (n === "en" || n === "pt") setLang(n);
    };
    window.addEventListener("hydrosim-language-change", f);
    return () => window.removeEventListener("hydrosim-language-change", f);
  }, []);
  const request = useMemo(
    () => ({
      error_family: family,
      angular_residual_deg: angle,
      latency_residual_ms: latency,
      water_depth_m: 50,
      terrain_slope_deg: slope,
      slow_speed_mps: slow,
      fast_speed_mps: fast,
      line_offset_m: 15,
      sample_count: 41,
      beam_count: 31,
      swath_angle_deg: 100,
    }),
    [family, angle, latency, slope, slow, fast],
  );
  useEffect(() => {
    const c = new AbortController(),
      timer = window.setTimeout(() => {
        setLoading(true);
        setError(false);
        fetch(`${API_BASE}/api/v1/pedagogical/patch-test/signatures`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(request),
          signal: c.signal,
        })
          .then(async (r) => {
            if (!r.ok) throw new Error(String(r.status));
            return r.json() as Promise<Response>;
          })
          .then(setData)
          .catch((e) => {
            if (e.name !== "AbortError") setError(true);
          })
          .finally(() => setLoading(false));
      }, 70);
    return () => {
      c.abort();
      clearTimeout(timer);
    };
  }, [request, nonce]);
  const reset = () => {
    setFamily("roll");
    setAngle(1);
    setLatency(100);
    setSlope(15);
    setSlow(2);
    setFast(6);
    setPaired(true);
    setShowSupport(true);
    setShowTruth(false);
  };
  return (
    <main className="patch-lab">
      <header className="patch-header">
        <div>
          <span>P1 · {t.fundamentals}</span>
          <h1>{t.title}</h1>
          <p>{t.question}</p>
        </div>
        <button
          className="patch-language"
          onClick={() => setLang((v) => (v === "en" ? "pt" : "en"))}
        >
          {lang === "en" ? "PT-BR" : "EN"}
        </button>
      </header>
      <div className="patch-layout">
        <aside className="patch-controls">
          <div className="patch-family">
            {families.map((f) => (
              <button
                key={f}
                className={family === f ? "active" : ""}
                onClick={() => setFamily(f)}
              >
                {t.family[f]}
              </button>
            ))}
          </div>
          <label>
            {t.magnitude}
            <output>
              {family === "latency" ? `${latency} ms` : `${angle.toFixed(1)}°`}
            </output>
            <input
              aria-label={t.magnitude}
              type="range"
              min={family === "latency" ? -300 : -3}
              max={family === "latency" ? 300 : 3}
              step={family === "latency" ? 10 : 0.1}
              value={family === "latency" ? latency : angle}
              onChange={(e) =>
                family === "latency"
                  ? setLatency(+e.target.value)
                  : setAngle(+e.target.value)
              }
            />
          </label>
          {(family === "pitch" || family === "yaw" || family === "latency") && (
            <label>
              {t.slope}
              <output>{slope}°</output>
              <input
                aria-label={t.slope}
                type="range"
                min="0"
                max="30"
                value={slope}
                onChange={(e) => setSlope(+e.target.value)}
              />
            </label>
          )}
          {family === "latency" && (
            <>
              <label>
                {t.slow}
                <output>{slow.toFixed(1)} m/s</output>
                <input
                  aria-label={t.slow}
                  type="range"
                  min="1"
                  max="8"
                  step=".5"
                  value={slow}
                  onChange={(e) => setSlow(+e.target.value)}
                />
              </label>
              <label>
                {t.fast}
                <output>{fast.toFixed(1)} m/s</output>
                <input
                  aria-label={t.fast}
                  type="range"
                  min="1"
                  max="10"
                  step=".5"
                  value={fast}
                  onChange={(e) => setFast(+e.target.value)}
                />
              </label>
            </>
          )}
          <div className="patch-toggles">
            <button
              className={paired ? "active" : ""}
              onClick={() => setPaired((v) => !v)}
            >
              {paired ? <Eye size={15} /> : <EyeOff size={15} />} {t.paired}
            </button>
            <button
              className={showSupport ? "active" : ""}
              onClick={() => setShowSupport((v) => !v)}
            >
              {showSupport ? <Eye size={15} /> : <EyeOff size={15} />}{" "}
              {t.support}
            </button>
            <button
              className={showTruth ? "active" : ""}
              onClick={() => setShowTruth((v) => !v)}
            >
              {showTruth ? <Eye size={15} /> : <EyeOff size={15} />}{" "}
              {t.reference}
            </button>
          </div>
          <button
            className="patch-combined"
            onClick={() => setFamily("confounded")}
          >
            <AlertTriangle size={15} />
            {t.combined}
          </button>
          <button className="patch-reset" onClick={reset}>
            <RotateCcw size={15} />
            {t.reset}
          </button>
        </aside>
        <section
          className={`patch-instrument ${showSupport ? "show-support" : "hide-support"}`}
        >
          {error && (
            <button
              className="patch-error"
              onClick={() => setNonce((v) => v + 1)}
            >
              {t.retry}
            </button>
          )}
          {data && (
            <>
              <div className="patch-panel">
                <div className="patch-panel-title">
                  <span>01</span>
                  <strong>{t.geometry}</strong>
                  <small>{t.description[data.error_family]}</small>
                </div>
                <Geometry data={data} paired={paired} t={t} />
              </div>
              <div className="patch-causal">
                <ArrowDown size={20} />
              </div>
              <div className="patch-panel">
                <div className="patch-panel-title">
                  <span>02</span>
                  <strong>{t.signature}</strong>
                  <small>{t.compare[data.comparison_region]}</small>
                </div>
                <Signature
                  data={data}
                  paired={paired}
                  showTruth={showTruth}
                  t={t}
                />
              </div>
              <div
                className={`patch-diagnosis ${data.evidence_sufficient ? "adequate" : "insufficient"}`}
              >
                <span>{data.evidence_sufficient ? "✓" : "!"}</span>
                <div>
                  <small>
                    {data.evidence_sufficient ? t.adequate : t.insufficient}
                  </small>
                  <strong>{t.family[data.likely_classification]}</strong>
                </div>
              </div>
            </>
          )}
          {loading && <div className="patch-loading">{t.updating}</div>}
        </section>
      </div>
    </main>
  );
}
