import { AlertTriangle, LockKeyhole, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
type Family = "roll" | "pitch" | "yaw" | "latency";
type Point = {
  coordinate_m: number;
  run_a_z_m: number;
  run_b_z_m: number;
  vertical_difference_m: number;
};
type Curve = { correction: number; rms_m: number };
type Run = {
  run_id: string;
  line_id: string;
  observation_state: string;
  observed: {
    sample_index: number;
    ping_time_seconds: number;
    measured_x_m: number;
    measured_y_m: number;
    measured_z_m: number;
  }[];
};
type Result = {
  acquisition_id: string;
  error_family: Family;
  correction_unit: "degrees" | "milliseconds";
  configured_value: number;
  candidate_correction: number;
  candidate_value: number;
  runs: [Run, Run];
  residual_axis: "x" | "y";
  spatial_residual: Point[];
  objective_rms_m: number;
  objective_curve: Curve[];
  estimated_correction: number | null;
  estimate_status: "determined" | "weak_or_flat" | "boundary_minimum";
  estimate_reasons: string[];
  state_semantics: string;
};
const families: Family[] = ["roll", "pitch", "yaw", "latency"];
const reasonPt: Record<string, string> = {
  "acquisition geometry does not identify this parameter":
    "a geometria de aquisição não identifica este parâmetro",
  "objective minimum lies on the declared search boundary":
    "o mínimo está no limite declarado da busca",
  "objective is flat over the declared search interval":
    "o objetivo é plano no intervalo declarado",
};
export default function PatchCalibrationLab() {
  const [lang, setLang] = useState<"en" | "pt">("en"),
    [family, setFamily] = useState<Family>("roll"),
    [candidate, setCandidate] = useState(0),
    [data, setData] = useState<Result | null>(null),
    [error, setError] = useState(false),
    [view, setView] = useState<"current" | "residual" | "compare">("compare");
  const pt = lang === "pt",
    limit = family === "latency" ? 400 : 4,
    step = family === "latency" ? 5 : 0.1;
  useEffect(() => setCandidate(0), [family]);
  useEffect(() => {
    const ac = new AbortController();
    setError(false);
    fetch("/api/v1/pedagogical/patch-test/manual-calibration", {
      method: "POST",
      headers: { "content-type": "application/json" },
      signal: ac.signal,
      body: JSON.stringify({
        error_family: family,
        candidate_correction: candidate,
        search_min: -limit,
        search_max: limit,
      }),
    })
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setError(true);
      });
    return () => ac.abort();
  }, [family, candidate, limit]);
  const curve = data?.objective_curve ?? [],
    res = data?.spatial_residual ?? [];
  const bounds = useMemo(() => {
    const cs = curve.map((p) => p.correction),
      rs = curve.map((p) => p.rms_m),
      xs = res.map((p) => p.coordinate_m),
      zs = res.flatMap((p) => [p.run_a_z_m, p.run_b_z_m]);
    const span = (a: number[]) =>
      [Math.min(...a, 0), Math.max(...a, 1)] as const;
    return { c: span(cs), r: span(rs), x: span(xs), z: span(zs) };
  }, [curve, res]);
  const map = (
    v: number,
    [a, b]: readonly [number, number],
    lo: number,
    hi: number,
  ) => lo + ((v - a) / Math.max(b - a, 1e-9)) * (hi - lo);
  const path = (values: { x: number; y: number }[]) =>
    values
      .map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)},${p.y.toFixed(1)}`)
      .join(" ");
  const unit = data?.correction_unit === "milliseconds" ? "ms" : "°";
  return (
    <main className="p4-lab">
      <header>
        <div>
          <span>P4 · {pt ? "CALIBRAÇÃO MANUAL" : "MANUAL CALIBRATION"}</span>
          <h1>
            {pt
              ? "Feche o resíduo, não procure a resposta"
              : "Close the residual, not the answer"}
          </h1>
          <p>
            {pt
              ? "Reconstrua a mesma observação com uma correção candidata."
              : "Reconstruct the same observation with a candidate correction."}
          </p>
        </div>
        <button onClick={() => setLang((v) => (v === "en" ? "pt" : "en"))}>
          {pt ? "EN" : "PT-BR"}
        </button>
      </header>
      <div className="p4-layout">
        <aside className="p4-controls">
          <div className="p4-family">
            {families.map((f) => (
              <button
                key={f}
                className={family === f ? "active" : ""}
                onClick={() => setFamily(f)}
              >
                {f === "yaw" ? "Yaw / Heading" : f}
              </button>
            ))}
          </div>
          <label>
            {pt ? "Correção candidata" : "Candidate correction"}
            <output>
              {candidate.toFixed(family === "latency" ? 0 : 1)} {unit}
            </output>
            <input
              type="range"
              min={-limit}
              max={limit}
              step={step}
              value={candidate}
              onChange={(e) => setCandidate(+e.target.value)}
            />
            <input
              className="p4-number"
              type="number"
              min={-limit}
              max={limit}
              step={step}
              value={candidate}
              onChange={(e) =>
                setCandidate(Math.max(-limit, Math.min(limit, +e.target.value)))
              }
            />
          </label>
          <div className="p4-equation">
            <small>CONFIGURED + ESTIMATED</small>
            <strong>
              {data?.configured_value.toFixed(1) ?? "0.0"} +{" "}
              {candidate.toFixed(family === "latency" ? 0 : 1)} ={" "}
              {data?.candidate_value.toFixed(family === "latency" ? 0 : 1) ??
                "—"}{" "}
              {unit}
            </strong>
          </div>
          <div className="p4-views">
            {(["current", "residual", "compare"] as const).map((v) => (
              <button
                key={v}
                className={view === v ? "active" : ""}
                onClick={() => setView(v)}
              >
                {pt
                  ? (
                      {
                        current: "Atual",
                        residual: "Resíduo",
                        compare: "Comparar",
                      } as const
                    )[v]
                  : v}
              </button>
            ))}
          </div>
          <button className="p4-reset" onClick={() => setCandidate(0)}>
            <RotateCcw />
            {pt ? "Estado configurado" : "Configured state"}
          </button>
        </aside>
        <section className="p4-instrument">
          <div className="p4-spatial">
            <div className="p4-title">
              <span>
                {pt
                  ? "SUPORTE COMUM · MESMA ESCALA"
                  : "COMMON SUPPORT · SAME SCALE"}
              </span>
              <strong>{data?.residual_axis.toUpperCase() ?? "—"} / Z</strong>
            </div>
            <svg viewBox="0 0 760 330">
              {[0, 1, 2, 3, 4].map((i) => (
                <line
                  key={i}
                  className="p4-grid"
                  x1="55"
                  x2="715"
                  y1={55 + i * 55}
                  y2={55 + i * 55}
                />
              ))}
              {(view === "current" || view === "compare") && (
                <>
                  <path
                    className="p4-before a"
                    d={path(
                      res.map((p) => ({
                        x: map(p.coordinate_m, bounds.x, 55, 715),
                        y: map(
                          p.run_a_z_m - p.vertical_difference_m,
                          bounds.z,
                          275,
                          40,
                        ),
                      })),
                    )}
                  />
                  <path
                    className="p4-before b"
                    d={path(
                      res.map((p) => ({
                        x: map(p.coordinate_m, bounds.x, 55, 715),
                        y: map(
                          p.run_b_z_m + p.vertical_difference_m,
                          bounds.z,
                          275,
                          40,
                        ),
                      })),
                    )}
                  />
                  <path
                    className="p4-current a"
                    d={path(
                      res.map((p) => ({
                        x: map(p.coordinate_m, bounds.x, 55, 715),
                        y: map(p.run_a_z_m, bounds.z, 275, 40),
                      })),
                    )}
                  />
                  <path
                    className="p4-current b"
                    d={path(
                      res.map((p) => ({
                        x: map(p.coordinate_m, bounds.x, 55, 715),
                        y: map(p.run_b_z_m, bounds.z, 275, 40),
                      })),
                    )}
                  />
                </>
              )}
              {(view === "residual" || view === "compare") && (
                <path
                  className="p4-residual"
                  d={path(
                    res.map((p) => ({
                      x: map(p.coordinate_m, bounds.x, 55, 715),
                      y: 165 - p.vertical_difference_m * 32,
                    })),
                  )}
                />
              )}
            </svg>
            <div className="p4-legend">
              <span className="before">
                {pt ? "Configurado / antes" : "Configured / before"}
              </span>
              <span className="current">
                {pt ? "Candidato / atual" : "Candidate / current"}
              </span>
              <span className="residual">
                {pt ? "Resíduo espacial" : "Spatial residual"}
              </span>
            </div>
          </div>
          <div className="p4-objective">
            <div className="p4-title">
              <span>J(Δq) · RMS</span>
              <strong>{data?.objective_rms_m.toFixed(3) ?? "—"} m</strong>
            </div>
            <svg viewBox="0 0 400 240">
              <path
                className="p4-curve"
                d={path(
                  curve.map((p) => ({
                    x: map(p.correction, bounds.c, 38, 370),
                    y: map(p.rms_m, bounds.r, 205, 30),
                  })),
                )}
              />
              {data && (
                <>
                  <line
                    className="p4-cursor"
                    x1={map(candidate, bounds.c, 38, 370)}
                    x2={map(candidate, bounds.c, 38, 370)}
                    y1="25"
                    y2="210"
                  />
                  <circle
                    className="p4-dot"
                    cx={map(candidate, bounds.c, 38, 370)}
                    cy={map(data.objective_rms_m, bounds.r, 205, 30)}
                    r="6"
                  />
                </>
              )}
            </svg>
            <div className={`p4-status ${data?.estimate_status}`}>
              {data?.estimate_status !== "determined" && <AlertTriangle />}
              <div>
                <small>{pt ? "IDENTIFICABILIDADE" : "IDENTIFIABILITY"}</small>
                <strong>
                  {data?.estimate_status.replaceAll("_", " ") ?? "—"}
                </strong>
                <p>
                  {data?.estimate_reasons
                    .map((r) => (pt ? (reasonPt[r] ?? r) : r))
                    .join(" · ")}
                </p>
              </div>
            </div>
          </div>
          <div className="p4-locked">
            {data?.runs.map((r) => (
              <article key={r.run_id}>
                <LockKeyhole />
                <div>
                  <small>{r.observation_state}</small>
                  <strong>
                    {r.line_id} · {r.run_id}
                  </strong>
                  <span>
                    {r.observed.length}{" "}
                    {pt ? "épocas imutáveis" : "immutable epochs"}
                  </span>
                </div>
              </article>
            ))}
          </div>
          {error && <div className="p4-error">Core/API unavailable</div>}
        </section>
      </div>
    </main>
  );
}
