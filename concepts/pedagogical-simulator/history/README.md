# Concept Design History

This directory records superseded HydroSIM Concept Lab milestones that remain useful for understanding the evolution of the design.

## Pre-curriculum system map — preserved milestone

The first mature concept organized the experience around six visual laboratories:

1. Signal
2. Beam
3. Propagation
4. Vessel & Sensors
5. Motion
6. Integrated Lab

This organization is superseded as the primary pedagogical navigation by the canonical D1–D18 / P1–P6 / A1–A7 plan. It remains valuable for interaction patterns, panel design, visual metaphors and design history.

### Executable legacy route

The legacy system map remains available in the concept runtime at `#legacy`; its implementation remains in `src/App.tsx`.

### Preserved visual evidence

The repository screenshots produced during that phase remain under `assets/screenshots/`, including the system map and the six laboratory screenshots.

## Pre-scientific Signal laboratory — frozen source snapshot

The last Signal concept before the learner-facing lab was connected to the canonical Python Scientific Core is permanently preserved on branch:

`archive/pedagogical-concept-pre-science`

at commit:

`10516fea640b3636d3548d690cdb60b36a21345d`

That snapshot preserves the original animated waveform treatment, pulse-stretch interaction, spectrum bars, response-compression visual and overall Concept visual language. Those curves were intentionally illustrative and frontend-generated; they must not be confused with scientific output.

## Production separation

The canonical learner-facing React application now evolves under:

`web/pedagogical-explorer/`

The `concepts/pedagogical-simulator/` tree remains a design/reference space. Production work must preserve the Concept's interaction intent where useful while sourcing scientific values through the Python application/API bridge.

### Preservation rule

Future conceptual redesigns should preserve meaningful superseded milestones rather than silently overwrite them. Prefer keeping:

- an executable legacy route when practical;
- screenshots that document the visual state;
- a frozen branch or commit for major design milestones;
- a short note explaining why the architecture changed;
- Git history for exact source recovery.

The purpose is to make HydroSIM's design evolution inspectable without forcing obsolete scientific assumptions or architecture into the current product.
