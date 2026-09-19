import { AlertTriangle, CheckCircle2, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
type Family = "roll" | "pitch" | "yaw" | "latency";
type Terrain = "flat" | "slope" | "feature";
type Result = {
  target_family: Family;
  adequacy: "Adequate" | "Suboptimal" | "Inadequate";
  reasons: string[];
  comparison_region: string;
  metrics: {
    swath_half_width_m: number;
    common_support_m: number;
    common_support_fraction: number;
    heading_difference_deg: number;
    speed_contrast_mps: number;
    line_offset_m: number;
    common_support_interval_m: [number, number] | null;
  };
};
const families: Family[] = ["roll", "pitch", "yaw", "latency"];
const api =
  (import.meta.env.VITE_HYDROSIM_API_BASE as string | undefined) ??
  "http://127.0.0.1:8000";
const presets: Record<
  Family,
  {
    a: number;
    b: number;
    sa: number;
    sb: number;
    offset: number;
    terrain: Terrain;
  }
> = {
  roll: { a: 0, b: 180, sa: 4, sb: 4, offset: 0, terrain: "flat" },
  pitch: { a: 0, b: 180, sa: 4, sb: 4, offset: 0, terrain: "slope" },
  yaw: { a: 0, b: 0, sa: 4, sb: 4, offset: 45, terrain: "feature" },
  latency: { a: 0, b: 0, sa: 2, sb: 6, offset: 0, terrain: "slope" },
};
const reasonPt: Record<string, string> = {
  "no common physical seabed support": "sem fundo físico comum",
  "common support is weaker than the configured scenario preference":
    "suporte comum menor que a preferência do cenário",
  "roll requires reciprocal line directions": "roll exige linhas recíprocas",
  "roll requires the same nominal line": "roll exige a mesma linha nominal",
  "non-flat terrain weakens roll isolation":
    "terreno não plano enfraquece o isolamento de roll",
  "pitch requires reciprocal line directions": "pitch exige linhas recíprocas",
  "pitch requires the same nominal line": "pitch exige a mesma linha nominal",
  "pitch requires a distinct along-track slope or feature":
    "pitch exige declive ou feição longitudinal",
  "yaw requires parallel same-direction lines":
    "yaw exige linhas paralelas no mesmo sentido",
  "yaw requires laterally offset lines":
    "yaw exige linhas afastadas lateralmente",
  "yaw requires a distinct feature or slope in common support":
    "yaw exige feição ou declive no suporte comum",
  "latency requires same-direction lines":
    "latência exige linhas no mesmo sentido",
  "latency requires the same nominal line":
    "latência exige a mesma linha nominal",
  "latency requires a distinct along-track slope or feature":
    "latência exige declive ou feição longitudinal",
  "latency requires nonzero speed contrast":
    "latência exige diferença de velocidade",
  "speed contrast is weaker than the configured scenario preference":
    "diferença de velocidade menor que a preferência do cenário",
  "required geometry and common support are present":
    "geometria necessária e suporte comum presentes",
};
export default function PatchPlanningLab() {
  const [lang, setLang] = useState<"en" | "pt">("en"),
    [family, setFamily] = useState<Family>("roll"),
    [headingB, setHeadingB] = useState(180),
    [speedA, setSpeedA] = useState(4),
    [speedB, setSpeedB] = useState(4),
    [offset, setOffset] = useState(0),
    [terrain, setTerrain] = useState<Terrain>("flat"),
    [depth, setDepth] = useState(50),
    [swath, setSwath] = useState(100),
    [data, setData] = useState<Result | null>(null),
    [error, setError] = useState(false);
  const apply = (f: Family) => {
    const p = presets[f];
    setFamily(f);
    setHeadingB(p.b);
    setSpeedA(p.sa);
    setSpeedB(p.sb);
    setOffset(p.offset);
    setTerrain(p.terrain);
  };
  const request = useMemo(
    () => ({
      target_family: family,
      heading_a_deg: 0,
      heading_b_deg: headingB,
      speed_a_mps: speedA,
      speed_b_mps: speedB,
      line_offset_m: offset,
      water_depth_m: depth,
      swath_angle_deg: swath,
      terrain_cross_extent_m: 300,
      terrain_along_extent_m: 500,
      terrain_kind: terrain,
      heading_tolerance_deg: 5,
      same_line_tolerance_m: 2,
      preferred_common_support_m: 25,
      preferred_speed_contrast_mps: 2,
    }),
    [family, headingB, speedA, speedB, offset, terrain, depth, swath],
  );
  useEffect(() => {
    const c = new AbortController(),
      id = setTimeout(
        () =>
          fetch(`${api}/api/v1/pedagogical/patch-test/planning`, {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify(request),
            signal: c.signal,
          })
            .then((r) => {
              if (!r.ok) throw new Error();
              return r.json();
            })
            .then(setData)
            .catch((e) => {
              if (e.name !== "AbortError") setError(true);
            }),
        70,
      );
    return () => {
      clearTimeout(id);
      c.abort();
    };
  }, [request]);
  const half = data?.metrics.swath_half_width_m ?? 60,
    scale = 2.15,
    center = 300,
    xa = center - half * scale,
    xb = center + offset * scale - half * scale,
    w = Math.min(half * 2 * scale, 520),
    support = data?.metrics.common_support_interval_m,
    sx = (v: number) => center + v * scale;
  const pt = lang === "pt";
  return (
    <main className="p2-lab">
      <header>
        <div>
          <span>P2 · {pt ? "PLANEJAMENTO" : "PLANNING"}</span>
          <h1>
            {pt ? "Planeje antes de adquirir" : "Design before acquisition"}
          </h1>
          <p>
            {pt
              ? "A geometria observará o mesmo fundo e isolará o parâmetro escolhido?"
              : "Will the geometry observe the same seabed and isolate the chosen parameter?"}
          </p>
        </div>
        <button onClick={() => setLang((v) => (v === "en" ? "pt" : "en"))}>
          {pt ? "EN" : "PT-BR"}
        </button>
      </header>
      <div className="p2-layout">
        <aside className="p2-controls">
          <div className="p2-family">
            {families.map((f) => (
              <button
                className={family === f ? "active" : ""}
                onClick={() => apply(f)}
                key={f}
              >
                {f === "yaw" ? "Yaw / Heading" : f}
              </button>
            ))}
          </div>
          <label>
            {pt ? "Proa da linha B" : "Run B heading"}
            <output>{headingB}°</output>
            <input
              type="range"
              min="0"
              max="180"
              step="5"
              value={headingB}
              onChange={(e) => setHeadingB(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Afastamento lateral" : "Line offset"}
            <output>{offset} m</output>
            <input
              type="range"
              min="0"
              max="140"
              step="5"
              value={offset}
              onChange={(e) => setOffset(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Velocidade A" : "Run A speed"}
            <output>{speedA} m/s</output>
            <input
              type="range"
              min="1"
              max="8"
              step=".5"
              value={speedA}
              onChange={(e) => setSpeedA(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Velocidade B" : "Run B speed"}
            <output>{speedB} m/s</output>
            <input
              type="range"
              min="1"
              max="8"
              step=".5"
              value={speedB}
              onChange={(e) => setSpeedB(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Terreno" : "Terrain"}
            <select
              value={terrain}
              onChange={(e) => setTerrain(e.target.value as Terrain)}
            >
              <option value="flat">{pt ? "Plano" : "Flat"}</option>
              <option value="slope">{pt ? "Declive" : "Slope"}</option>
              <option value="feature">{pt ? "Feição" : "Feature"}</option>
            </select>
          </label>
          <label>
            {pt ? "Profundidade" : "Depth"}
            <output>{depth} m</output>
            <input
              type="range"
              min="20"
              max="100"
              step="5"
              value={depth}
              onChange={(e) => setDepth(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Abertura do setor" : "Swath angle"}
            <output>{swath}°</output>
            <input
              type="range"
              min="40"
              max="140"
              step="5"
              value={swath}
              onChange={(e) => setSwath(+e.target.value)}
            />
          </label>
          <button className="p2-reset" onClick={() => apply(family)}>
            <RotateCcw size={14} />
            {pt ? "Plano canônico" : "Canonical plan"}
          </button>
        </aside>
        <section className="p2-stage">
          <div className="p2-map">
            <svg
              viewBox="0 0 720 430"
              role="img"
              aria-label={
                pt
                  ? "Mapa do planejamento e suporte comum"
                  : "Planning map and common support"
              }
            >
              <defs>
                <marker
                  id="p2-arrow"
                  markerWidth="8"
                  markerHeight="8"
                  refX="6"
                  refY="3"
                  orient="auto"
                >
                  <path d="M0 0L0 6L7 3z" />
                </marker>
              </defs>
              <rect
                className="p2-terrain"
                x="55"
                y="35"
                width="610"
                height="350"
                rx="12"
              />
              <path
                className={`p2-bottom ${terrain}`}
                d={
                  terrain === "flat"
                    ? "M55 315H665"
                    : terrain === "slope"
                      ? "M55 345L665 255"
                      : "M55 320Q250 245 360 315T665 270"
                }
              />
              <rect
                className="p2-swath a"
                x={xa}
                y="70"
                width={w}
                height="275"
              />
              <rect
                className="p2-swath b"
                x={xb}
                y="70"
                width={w}
                height="275"
              />
              {support && (
                <rect
                  className="p2-support"
                  x={sx(support[0])}
                  y="70"
                  width={Math.max((support[1] - support[0]) * scale, 2)}
                  height="275"
                />
              )}
              <line
                className="p2-line a"
                x1={center}
                y1="350"
                x2={center}
                y2="80"
                markerEnd="url(#p2-arrow)"
              />
              <line
                className="p2-line b"
                x1={center + offset * scale}
                y1={headingB > 90 ? 80 : 350}
                x2={center + offset * scale}
                y2={headingB > 90 ? 350 : 80}
                markerEnd="url(#p2-arrow)"
              />
              <text x="70" y="60">
                {pt ? "FUNDO DISPONÍVEL" : "AVAILABLE SEABED"}
              </text>
              {support && (
                <text
                  className="p2-support-label"
                  x={sx((support[0] + support[1]) / 2)}
                  y="100"
                  textAnchor="middle"
                >
                  {pt ? "SUPORTE COMUM" : "COMMON SUPPORT"}
                </text>
              )}
            </svg>
          </div>
          {data && (
            <div className={`p2-result ${data.adequacy.toLowerCase()}`}>
              <div>
                {data.adequacy === "Adequate" ? (
                  <CheckCircle2 />
                ) : (
                  <AlertTriangle />
                )}
                <span>
                  <small>{pt ? "OBSERVABILIDADE" : "OBSERVABILITY"}</small>
                  <strong>
                    {pt
                      ? (
                          {
                            Adequate: "Adequado",
                            Suboptimal: "Subótimo",
                            Inadequate: "Inadequado",
                          } as const
                        )[data.adequacy]
                      : data.adequacy}
                  </strong>
                </span>
              </div>
              <ul>
                {data.reasons.map((r) => (
                  <li key={r}>{pt ? (reasonPt[r] ?? r) : r}</li>
                ))}
              </ul>
              <aside>
                <span>
                  <small>{pt ? "Suporte comum" : "Common support"}</small>
                  <b>{data.metrics.common_support_m.toFixed(1)} m</b>
                </span>
                <span>
                  <small>{pt ? "Cobertura comum" : "Support fraction"}</small>
                  <b>
                    {(data.metrics.common_support_fraction * 100).toFixed(0)}%
                  </b>
                </span>
                <span>
                  <small>{pt ? "Diferença de proa" : "Heading contrast"}</small>
                  <b>{data.metrics.heading_difference_deg.toFixed(0)}°</b>
                </span>
                <span>
                  <small>
                    {pt ? "Diferença de velocidade" : "Speed contrast"}
                  </small>
                  <b>{data.metrics.speed_contrast_mps.toFixed(1)} m/s</b>
                </span>
              </aside>
            </div>
          )}
          {error && <div className="p2-error">Core/API unavailable</div>}
        </section>
      </div>
    </main>
  );
}
