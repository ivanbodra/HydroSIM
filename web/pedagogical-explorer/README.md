# HydroSIM Pedagogical Explorer — Production React Frontend

This directory is the learner-facing React/TypeScript frontend for the HydroSIM pedagogical product.

It is intentionally separate from `concepts/pedagogical-simulator/`.

## Architecture boundary

- `web/pedagogical-explorer/` owns learner interaction, information architecture, visualization and bilingual presentation.
- `src/hydrosim/` owns the canonical Python Scientific Core and application/API bridge.
- `concepts/pedagogical-simulator/` remains a design sandbox and historical visual reference. It is not the production scientific source of truth.

The production rule is:

`React presentation -> application/API bridge -> Python Scientific Core`

Scientific equations and numerical models must not be reimplemented in TypeScript.

## Concept preservation

The pre-scientific Signal design is additionally frozen on branch:

`archive/pedagogical-concept-pre-science`

at commit `10516fea640b3636d3548d690cdb60b36a21345d`.

That snapshot preserves the original interaction language, animated graph styling and visual experiments before canonical Python traces replaced illustrative frontend-generated curves.

## Local run

```bash
npm ci
npm run dev
```

Run the Python pedagogical API separately according to `docs/development/react_signal_bridge.md`.

## Build and tests

```bash
npm run build
npm run test:ui
```

Use the test layer that matches the change:

- Python/Core/API tests protect scientific calculations, units, frames and request/response contracts.
- Playwright lab tests protect learner actions and their visible consequences. Prefer semantic roles and observable behavior; do not depend on DOM nesting, CSS classes or superseded copy unless those are explicit requirements.
- Visual review owns layout and presentation details that are not behavioral contracts.
- React↔Python smoke tests are reserved for effects that cross the HTTP boundary and must use the Python API rather than a mocked route.

During UX work, run the affected lab's Playwright test first. Run the broader UI suite before handoff. Use the React↔Python smoke when the change depends on API integration; CI remains the final integration check.

Production CI should run from this directory. Changes to the concept sandbox must not silently alter the production frontend.
