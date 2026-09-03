# React Signal bridge — local development contract

This bridge lets the production pedagogical React frontend consume HydroSIM's Python Scientific Core without reproducing waveform equations in TypeScript.

## Backend

Install the editable project with the web extra:

```powershell
python -m pip install -e ".[web]"
```

Run the local API from the repository root:

```powershell
python -m uvicorn hydrosim.app.signal_api:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

PED-D2 Signal endpoint:

```text
POST http://127.0.0.1:8000/api/v1/pedagogical/signal
```

Example request:

```json
{
  "pulse_type": "lfm",
  "center_frequency_khz": 200,
  "duration_ms": 1,
  "bandwidth_khz": 100,
  "chirp_direction": "up",
  "envelope_model": "rectangular"
}
```

The response exposes application-ready traces and metadata: acoustic/passband waveform, physical instantaneous frequency, normalized matched-filter/autocorrelation response, and explicit units/representation labels.

## Frontend

The production pedagogical frontend lives in `web/pedagogical-explorer/`. The former `concepts/pedagogical-simulator/` tree is retained as a design sandbox and historical visual reference; it is not the production frontend.

`web/pedagogical-explorer/src/SignalLab.tsx` calls the endpoint above and contains interaction and presentation logic only, not waveform physics.

For local development, from the repository root:

```powershell
cd web\pedagogical-explorer
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the product at:

```text
http://127.0.0.1:5173/
```

For direct PED-D2 pulse testing:

```text
http://127.0.0.1:5173/#signal-lab/pulse
```

The frontend API base defaults to `http://127.0.0.1:8000`. Override it with `VITE_HYDROSIM_API_BASE` only when the API is intentionally served elsewhere.

## PED-D2 visual comparison rule

The production plots render values returned by the canonical Python API while preserving stable display domains for learner comparison. In particular, the waveform and instantaneous-frequency views use a fixed 0–5 ms time window so changing pulse duration changes the visible pulse extent instead of rescaling every result to fill the plot.

The pre-scientific Signal concept remains frozen on `archive/pedagogical-concept-pre-science` at commit `10516fea640b3636d3548d690cdb60b36a21345d` for visual and interaction reference.

## Production-path validation

The learner-facing production build is validated from `web/pedagogical-explorer/` with:

```powershell
npm ci
npm run build
```

Focused UI/state validation runs against the built Vite preview with Playwright:

```powershell
npm run preview -- --host 127.0.0.1
npm run test:ui
```

The focused PED-D2 tests validate canonical endpoint wiring, learner pulse controls, fixed-scale display behavior and EN/PT-BR switching. A dedicated CI smoke test starts the real Python API and the React frontend together and verifies the PED-D2 React↔Python path. Scientific/numerical correctness of returned values remains owned by Python Core/API tests.

## Dependency policy

Frontend dependencies are pinned to tested exact versions in `package.json`, and `package-lock.json` is committed. CI installs them reproducibly with `npm ci`.

Python web dependencies remain in the `web` optional dependency group of `pyproject.toml`, so the bridge does not enlarge the default scientific installation.

## Boundary

- Python Scientific Core owns waveform physics and numerical realization.
- The application bridge owns unit conversion and serialization.
- React owns interaction and visual presentation only.
- Baseband processing and acoustic/passband display remain explicitly distinct representations.
