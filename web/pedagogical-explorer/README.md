# HydroSIM Pedagogical Simulator — Design Sandbox

This directory is an independent conceptual design sandbox for the HydroSIM Didactic Explorer. It is intentionally separated from the production interface and from the Scientific Core.

The current executable concept uses React + TypeScript + Vite, Motion for fluid interaction, Lucide for iconography, SVG/CSS for scientific visual language, and Playwright only for reproducible runtime screenshots in CI.

## Current conceptual laboratories

- **Signal** — waveform, pulse, spectrum and compression as a transmit → receive → compress chain.
- **Beam** — directivity, steering, beamwidth, sidelobes and footprint in one water-column scene.
- **Propagation** — profile lens, layered water column, ray paths, illustrative loss and seabed interaction.
- **Vessel & Sensors** — transparent vessel, GNSS, IMU, transducer, VRP, lever arms and vertical references.
- **Motion** — roll, pitch, yaw and heave with baseline ghost, beam field and sounding consequence.
- **Integrated Lab** — one virtual hydrographic survey where Signal, Beam, Propagation and Motion become focus lenses inside the same experiment.

The system map is the discovery surface. Each module has an **Enter laboratory** action. Submodules describe intended focus modes inside each laboratory rather than requiring a separate disconnected screen.

## Run locally

```bash
npm install
npm run dev
```

Direct routes:

- `#signal-lab`
- `#beam-lab`
- `#propagation-lab`
- `#vessel-lab`
- `#motion-lab`
- `#integrated-lab`

## Build and capture

```bash
npm run build
npm run capture
```

The GitHub workflow `.github/workflows/concept-screenshot.yml` builds the real prototype, opens it in headless Chromium, captures the system map and all laboratories, verifies the PNG files, uploads them as a CI artifact, and persists changed screenshots in `assets/screenshots/`.

## Scientific status

This sandbox is **not scientifically validated output**. Values, ranges, geometry, motion amplification, trajectories, energy cues and scenarios may be illustrative placeholders. Their purpose is to expose interaction and visualization ideas for downstream Interface/UX and scientific validation.

## Handoff

See `HANDOFF_INTERFACE_UX.md` for the five-part concept handoff — IDEA, WHY, IMPORTANT INTERACTION, INPUTS expected, OUTPUTS visualized — for all six modules, plus navigation and scenario language.

Interface/UX owns selection, adaptation and production translation. Do not move these concepts into production UI or the Scientific Core without the appropriate project handoff and review.
