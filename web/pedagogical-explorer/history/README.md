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

This organization is now superseded as the primary pedagogical navigation by the canonical D1–D18 / P1–P6 / A1–A7 plan. It is intentionally preserved because it contains useful interaction patterns, panel designs, visual metaphors and evidence of the project's design evolution.

### How to view it

The executable legacy system map remains available in the current concept runtime at:

`#legacy`

Its implementation remains in `src/App.tsx`; it has not been deleted or replaced.

### Preserved visual evidence

The repository screenshots produced during that phase remain under:

`assets/screenshots/`

including the system map and the six laboratory screenshots.

### Status

**Historical / obsolete as pedagogical architecture.**

This status does not mean the design is discarded. Individual panels, interactions and visual concepts may be reused or adapted in the curriculum-aligned prototype.

### Preservation rule

Future conceptual redesigns should preserve meaningful superseded milestones rather than silently overwrite them. Prefer keeping:

- an executable legacy route when practical;
- screenshots that document the visual state;
- a short note explaining why the architecture changed;
- Git history for exact source recovery.

The purpose is to make HydroSIM's design evolution inspectable over time without forcing obsolete architecture into the current product direction.
