# HydroSIM Pedagogical Simulator — Concept Sandbox

This directory is an independent visual-design sandbox for the HydroSIM Concept Simulator Designer.

It is **not** the production HydroSIM interface and must not be treated as scientifically validated output. Values, visual responses and interactions may be illustrative placeholders created to explore a desirable pedagogical experience.

## Current prototype

The first macro-level prototype presents the complete learning environment as one navigable system. Six concept areas are exposed through an expandable module menu and interactive cards:

1. Signal — Waveform, Pulse, Spectrum, Compression
2. Beam — Beam Pattern, Steering, Beamwidth, Footprint
3. Propagation — Sound Speed, Refraction, Attenuation, Bottom Interaction
4. Vessel & Sensors — Vessel, Transducer, GNSS, IMU, Lever Arms, Vertical References
5. Motion — Heave, Roll, Pitch, Yaw, Motion Viewer, Sounding Impact
6. Integrated Lab — Survey Setup, Realtime View, Sounding Generation, Uncertainty, Comparison, Experiment Presets

The prototype uses React + TypeScript + Vite, Motion for subtle transitions and Lucide for scalable interface icons.

## Run locally

```bash
cd concepts/pedagogical-simulator
npm install
npm run dev
```

Build check:

```bash
npm run build
```

## Design intent

The macro shell establishes the visual hierarchy before individual experiments are designed. Selecting a submodule changes the contextual hero surface and prepares the pattern for later dedicated interactive experiments.

Primary interaction principle:

> INPUT → IMMEDIATE VISUAL RESPONSE → PHYSICAL INTUITION

## Boundary

Do not move this prototype into `src/hydrosim/` or replace official interface assets without explicit Technical Lead direction. The `interface-ux` agent remains responsible for deciding whether and how concepts are translated into the production interface.
