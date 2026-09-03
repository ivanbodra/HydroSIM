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

The production pedagogical frontend lives in `concepts/pedagogical-simulator/`. `SignalLab.tsx` calls the endpoint above; it contains interaction and presentation logic, not waveform physics.

For local development:

```powershell
cd concepts\pedagogical-simulator
npm ci
npm run dev
```

Vite normally serves the frontend at `http://127.0.0.1:5173` or `http://localhost:5173`; those origins are admitted by the local HydroSIM API.

The frontend API base defaults to `http://127.0.0.1:8000`. Override it with `VITE_HYDROSIM_API_BASE` only when the API is intentionally served elsewhere.

## Production-path validation

The learner-facing production build is validated with:

```powershell
npm ci
npm run build
```

Focused UI/state validation runs against the built Vite preview with Playwright:

```powershell
npm run preview -- --host 127.0.0.1
npm run test:ui
```

The focused PED-D2 test intercepts only HTTP transport so that React state and interaction can be validated deterministically. It verifies that learner controls are posted to `/api/v1/pedagogical/signal`, CW/LFM presentation state responds correctly, canonical returned traces are rendered, and EN/PT-BR switching remains coherent. Scientific/numerical correctness of those returned values remains owned by Python Core/API tests.

## Dependency policy

Frontend dependencies are pinned to tested exact versions in `package.json`, and `package-lock.json` is committed. CI installs them reproducibly with `npm ci`.

Python web dependencies remain in the `web` optional dependency group of `pyproject.toml`, so the bridge does not enlarge the default scientific installation.

## Boundary

- Python Scientific Core owns waveform physics and numerical realization.
- The application bridge owns unit conversion and serialization.
- React owns interaction and visual presentation only.
- Baseband processing and acoustic/passband display remain explicitly distinct representations.
