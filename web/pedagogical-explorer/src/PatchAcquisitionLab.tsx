import {
  CheckCircle2,
  LockKeyhole,
  Pause,
  Play,
  RotateCcw,
  StepForward,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type Family = "roll" | "pitch" | "yaw" | "latency";
type Sample = {
  sample_index: number;
  ping_time_seconds: number;
  measured_x_m: number;
  measured_y_m: number;
  measured_z_m: number;
};
type Sounding = { sample_index: number; x_m: number; y_m: number; z_m: number };
type Run = {
  run_id: string;
  line_id: string;
  heading_deg: number;
  speed_mps: number;
  observation_state: "Observed/locked";
  observed: Sample[];
  derived_soundings: Sounding[];
  configuration_snapshot: Record<string, string | number>;
};
type Result = {
  acquisition_id: string;
  error_family: Family;
  runs: [Run, Run];
  fitness: "usable" | "marginal" | "reacquire";
  fitness_reasons: string[];
  common_support_fraction: number;
  common_support_geometry: {
    axis: "x" | "y";
    interval_m: [number, number] | null;
    bounds: { min_x_m: number; max_x_m: number; min_y_m: number; max_y_m: number } | null;
  };
  residual_axis: "x" | "y";
  residual_preview: { coordinate_m: number; vertical_difference_m: number }[];
  state_semantics: string;
};
const families: Family[] = ["roll", "pitch", "yaw", "latency"];
const reasonPt: Record<string, string> = {
  "target signature is not identifiable in the executed geometry":
    "a assinatura alvo não é identificável na geometria executada",
  "paired runs have no executed common support":
    "as linhas executadas não possuem suporte comum",
  "executed common support is weak": "o suporte comum executado é fraco",
  "line steering error exceeds the planned offset scale":
    "o erro de governo excede a escala do afastamento planejado",
};

export default function PatchAcquisitionLab() {
  const [lang, setLang] = useState<"en" | "pt">("en");
  const [family, setFamily] = useState<Family>("roll");
  const [overlap, setOverlap] = useState(1);
  const [steering, setSteering] = useState(0);
  const [data, setData] = useState<Result | null>(null);
  const [visible, setVisible] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [foreground, setForeground] = useState<0 | 1>(0);
  const [showObserved, setShowObserved] = useState(true);
  const [showDerived, setShowDerived] = useState(true);
  const [showSupport, setShowSupport] = useState(true);
  const [error, setError] = useState(false);
  const pt = lang === "pt";
  useEffect(() => {
    const ac = new AbortController();
    setError(false);
    setPlaying(false);
    setVisible(0);
    fetch("/api/v1/pedagogical/patch-test/acquisition", {
      method: "POST",
      headers: { "content-type": "application/json" },
      signal: ac.signal,
      body: JSON.stringify({
        error_family: family,
        executed_overlap_fraction: overlap,
        steering_error_m: steering,
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
  }, [family, overlap, steering]);
  const total = Math.max(...(data?.runs.map((r) => r.observed.length) ?? [1]));
  useEffect(() => {
    if (!playing) return;
    const id = setInterval(
      () => setVisible((v) => (v >= total ? (setPlaying(false), v) : v + 1)),
      55,
    );
    return () => clearInterval(id);
  }, [playing, total]);
  const points = useMemo(
    () =>
      data?.runs.flatMap((r, ri) =>
        r.observed
          .slice(0, visible)
          .map((p) => ({
            ri,
            p,
            d: r.derived_soundings.find(
              (d) => d.sample_index === p.sample_index,
            ),
          })),
      ) ?? [],
    [data, visible],
  );
  const ext = useMemo(() => {
    const xs = points.flatMap((q) => [
        q.p.measured_x_m,
        q.d?.x_m ?? q.p.measured_x_m,
      ]),
      ys = points.flatMap((q) => [
        q.p.measured_y_m,
        q.d?.y_m ?? q.p.measured_y_m,
      ]),
      zs = points.flatMap((q) => [
        q.p.measured_z_m,
        q.d?.z_m ?? q.p.measured_z_m,
      ]);
    const span = (a: number[]) =>
      [Math.min(...a, 0), Math.max(...a, 1)] as const;
    return { x: span(xs), y: span(ys), z: span(zs) };
  }, [points]);
  const planExt = useMemo(() => {
    const samples = data?.runs.flatMap((r) => r.observed) ?? [];
    const bounds = data?.common_support_geometry.bounds;
    const xs = samples.map((p) => p.measured_x_m).concat(bounds ? [bounds.min_x_m, bounds.max_x_m] : []);
    const ys = samples.map((p) => p.measured_y_m).concat(bounds ? [bounds.min_y_m, bounds.max_y_m] : []);
    const span = (a: number[]) => [Math.min(...a, 0), Math.max(...a, 1)] as const;
    return { x: span(xs), y: span(ys) };
  }, [data]);
  const map = (
    v: number,
    [a, b]: readonly [number, number],
    lo: number,
    hi: number,
  ) => lo + ((v - a) / Math.max(b - a, 1e-6)) * (hi - lo);
  const reset = () => {
    setOverlap(1);
    setSteering(0);
    setVisible(0);
    setPlaying(false);
    setForeground(0);
    setShowObserved(true);
    setShowDerived(true);
    setShowSupport(true);
  };
  return (
    <main className="p3-lab">
      <header>
        <div>
          <span>
            P3 · {pt ? "AQUISIÇÃO SINTÉTICA" : "SYNTHETIC ACQUISITION"}
          </span>
          <h1>
            {pt ? "Adquira a evidência pareada" : "Acquire the paired evidence"}
          </h1>
          <p>
            {pt
              ? "O que foi observado permanece bloqueado para a calibração."
              : "What was observed stays locked for calibration."}
          </p>
        </div>
        <button onClick={() => setLang((v) => (v === "en" ? "pt" : "en"))}>
          {pt ? "EN" : "PT-BR"}
        </button>
      </header>
      <div className="p3-layout">
        <aside className="p3-controls">
          <div className="p3-family">
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
            {pt ? "Sobreposição executada" : "Executed overlap"}
            <output>{(overlap * 100).toFixed(0)}%</output>
            <input
              type="range"
              min="0"
              max="1"
              step=".05"
              value={overlap}
              onChange={(e) => setOverlap(+e.target.value)}
            />
          </label>
          <label>
            {pt ? "Erro de governo" : "Steering error"}
            <output>{steering.toFixed(0)} m</output>
            <input
              type="range"
              min="0"
              max="40"
              step="2"
              value={steering}
              onChange={(e) => setSteering(+e.target.value)}
            />
          </label>
          <div className="p3-toggles">
            <button
              className={showObserved ? "on" : ""}
              onClick={() => setShowObserved((v) => !v)}
            >
              <LockKeyhole size={13} />
              {pt ? "Observado bloqueado" : "Observed locked"}
            </button>
            <button
              className={showDerived ? "on" : ""}
              onClick={() => setShowDerived((v) => !v)}
            >
              {pt ? "Sondagens derivadas" : "Derived soundings"}
            </button>
            <button
              className={showSupport ? "on" : ""}
              onClick={() => setShowSupport((v) => !v)}
            >
              {pt ? "Suporte comum" : "Common support"}
            </button>
          </div>
          <button className="p3-reset" onClick={reset}>
            <RotateCcw size={14} />
            {pt ? "Restaurar aquisição" : "Reset acquisition"}
          </button>
        </aside>
        <section className="p3-instrument">
          <div className="p3-track">
            <div className="p3-title">
              <span>
                {pt ? "PROGRESSO DA AQUISIÇÃO" : "ACQUISITION PROGRESS"}
              </span>
              <strong>
                {visible}/{total} {pt ? "épocas" : "epochs"}
              </strong>
            </div>
            <svg
              viewBox="0 0 760 250"
              role="img"
              aria-label={
                pt
                  ? "Linhas executadas e cobertura"
                  : "Executed lines and coverage"
              }
            >
              {showSupport && data?.common_support_geometry.bounds && (
                <rect
                  className="p3-support"
                  x={map(data.common_support_geometry.bounds.min_x_m, planExt.x, 70, 690)}
                  y={map(data.common_support_geometry.bounds.max_y_m, planExt.y, 215, 35)}
                  width={Math.max(2,map(data.common_support_geometry.bounds.max_x_m, planExt.x, 70, 690)-map(data.common_support_geometry.bounds.min_x_m, planExt.x, 70, 690))}
                  height={Math.max(2,map(data.common_support_geometry.bounds.min_y_m, planExt.y, 215, 35)-map(data.common_support_geometry.bounds.max_y_m, planExt.y, 215, 35))}
                  rx="12"
                />
              )}
              {[0, 1].map((i) => {
                const run = data?.runs[i];
                const acquired=run?.observed??[];
                const shown=acquired.slice(0,visible);
                const vessel=shown.at(-1)??acquired[0];
                const track=acquired.map((p,j)=>`${j?'L':'M'}${map(p.measured_x_m,planExt.x,70,690).toFixed(1)},${map(p.measured_y_m,planExt.y,215,35).toFixed(1)}`).join(' ');
                return (
                  <g
                    key={i}
                    className={foreground === i ? "foreground" : ""}
                    onClick={() => setForeground(i as 0 | 1)}
                  >
                    <path
                      className={`p3-run r${i}`}
                      d={track}
                    />
                    {vessel&&<circle
                      className={`p3-vessel r${i}`}
                      cx={map(vessel.measured_x_m,planExt.x,70,690)}
                      cy={map(vessel.measured_y_m,planExt.y,215,35)}
                      r="10"
                    />}
                    <text x="85" y={25 + i * 18}>
                      {run?.line_id ?? `RUN ${i + 1}`} ·{" "}
                      {run?.speed_mps.toFixed(1) ?? "—"} m/s ·{" "}
                      {run?.heading_deg.toFixed(0) ?? "—"}°
                    </text>
                  </g>
                );
              })}
            </svg>
            <div className="p3-play">
              <button onClick={() => setPlaying((v) => !v)}>
                {playing ? <Pause /> : <Play />}
                {playing
                  ? pt
                    ? "Pausar"
                    : "Pause"
                  : pt
                    ? "Adquirir"
                    : "Acquire"}
              </button>
              <button onClick={() => setVisible((v) => Math.min(v + 1, total))}>
                <StepForward />
                {pt ? "Passo" : "Step"}
              </button>
              <input
                aria-label={pt ? "Progresso" : "Progress"}
                type="range"
                min="0"
                max={total}
                value={visible}
                onChange={(e) => setVisible(+e.target.value)}
              />
            </div>
          </div>
          <div className="p3-evidence">
            <div className="p3-title">
              <span>{pt ? "EVIDÊNCIA ACUMULADA" : "ACCUMULATED EVIDENCE"}</span>
              <strong>
                {pt ? "Observado ≠ Derivado" : "Observed ≠ Derived"}
              </strong>
            </div>
            <svg viewBox="0 0 760 300">
              {points.map(({ ri, p, d }) => (
                <g
                  key={`${ri}-${p.sample_index}`}
                  opacity={foreground === ri ? 1 : 0.32}
                >
                  {showObserved && (
                    <circle
                      className={`p3-observed r${ri}`}
                      cx={map(p.measured_x_m, ext.x, 55, 705)}
                      cy={map(p.measured_z_m, ext.z, 250, 45)}
                      r="2.7"
                    />
                  )}
                  {showDerived && d && (
                    <rect
                      className={`p3-derived r${ri}`}
                      x={map(d.x_m, ext.x, 55, 705) - 2}
                      y={map(d.z_m, ext.z, 250, 45) - 2}
                      width="4"
                      height="4"
                    />
                  )}
                </g>
              ))}
            </svg>
            <div className="p3-legend">
              <span>
                <i className="obs" />
                Observed / locked
              </span>
              <span>
                <i className="drv" />
                Derived / navigation frame
              </span>
            </div>
          </div>
          {data && (
            <div className={`p3-fitness ${data.fitness}`}>
              {data.fitness === "usable" ? <CheckCircle2 /> : <TriangleAlert />}
              <div>
                <small>
                  {pt ? "APTIDÃO PARA CALIBRAÇÃO" : "FITNESS FOR CALIBRATION"}
                </small>
                <strong>
                  {pt
                    ? (
                        {
                          usable: "utilizável",
                          marginal: "marginal",
                          reacquire: "readquirir",
                        } as const
                      )[data.fitness]
                    : data.fitness}
                </strong>
                <p>
                  {data.fitness_reasons.length
                    ? data.fitness_reasons
                        .map((r) => (pt ? (reasonPt[r] ?? r) : r))
                        .join(" · ")
                    : pt
                      ? "Geometria e suporte executados preservados."
                      : "Executed geometry and support preserved."}
                </p>
              </div>
              <b>
                {(data.common_support_fraction * 100).toFixed(0)}%
                <small>{pt ? "suporte comum" : "common support"}</small>
              </b>
            </div>
          )}
          <div className="p3-provenance">
            {data?.runs.map((r, i) => (
              <article
                key={r.run_id}
                className={foreground === i ? "active" : ""}
                onClick={() => setForeground(i as 0 | 1)}
              >
                <LockKeyhole />
                <div>
                  <small>{r.observation_state}</small>
                  <strong>
                    {r.line_id} · {r.run_id}
                  </strong>
                  <span>
                    {String(r.configuration_snapshot.sonar_id)} · Δt{" "}
                    {Number(
                      r.configuration_snapshot.ping_period_seconds,
                    ).toFixed(2)}{" "}
                    s · seed{" "}
                    {String(r.configuration_snapshot.deterministic_seed)}
                  </span>
                </div>
              </article>
            ))}
          </div>
          {error && <div className="p3-error">Core/API unavailable</div>}
        </section>
      </div>
    </main>
  );
}
