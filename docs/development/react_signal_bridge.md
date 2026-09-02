# React Signal bridge — local development contract

This bridge exists to let the pedagogical React frontend consume HydroSIM's Python Scientific Core without reproducing waveform equations in TypeScript.

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

The response exposes only application-ready traces and metadata: acoustic/passband waveform, physical instantaneous frequency, normalized matched-filter response, and explicit units/representation labels.

## Frontend

The existing concept lives in `concepts/pedagogical-simulator/` and uses Vite/React. During the production migration, replace the illustrative waveform calculations in `SignalLab.tsx` with calls to the endpoint above; do not translate the Python scientific equations into TypeScript.

For local development:

```powershell
cd concepts\pedagogical-simulator
npm install
npm run dev
```

Vite normally serves the concept at `http://127.0.0.1:5173` or `http://localhost:5173`; those origins are the only CORS origins admitted by the local HydroSIM API.

## Dependency policy

Python web dependencies are pinned in the `web` optional dependency group of `pyproject.toml` so the bridge does not enlarge the default scientific installation.

The concept `package.json` currently uses `latest` ranges. Before it becomes the production frontend package, Interface/UX (or the frontend implementation owner) should replace those ranges with tested exact versions and commit a lockfile. Software Engineering should review the resulting dependency set; this bridge does not silently select React/Vite versions on behalf of the frontend owner.

## Boundary

- Python Scientific Core owns waveform physics and numerical realization.
- The application bridge owns unit conversion and serialization.
- React owns interaction and visual presentation only.
- Baseband processing and acoustic/passband display remain explicitly distinct representations.
