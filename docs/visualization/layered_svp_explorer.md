# Layered SVP Didactic Explorer

Version: 0.1.0

## Purpose

`prepare_layered_svp_explorer_snapshot(...)` is the first vertical integration step toward the HydroSIM didactic explorer. It does not add acoustic physics. It composes the existing layered Truth-versus-processing experiment into one render-ready snapshot.

For each configured across-track beam the snapshot exposes:

- the configured beam angle;
- the Truth refracted ray path;
- the Truth bottom intersection;
- the Truth two-way travel time;
- the reconstructed sounding produced with the processing SVP; and
- calculated-minus-Truth across-track, vertical, and norm errors.

The intent is to let a future UI place the physical ray, true bottom and reconstructed sounding in the same view while the user changes the processing sound-speed profile.

## Controlled first slice

This first explorer deliberately fixes several variables instead of exposing every possible control:

- stationary monostatic reciprocal geometry;
- principal across-track plane;
- flat bottom;
- aligned platform pose;
- ideal sound-speed measurement at the transducer; and
- zero principal-plane array tilt.

The variable of interest is the difference between the Truth SVP and the processing SVP. More controls should be added only when they are needed by a specific teaching or simulation objective.

## Architecture boundary

The visualization layer must not become a second physics implementation. The explorer calls `run_layered_sound_speed_reference_experiment(...)` for each beam and only packages its existing outputs for presentation.

Therefore:

```text
Scientific core
    -> Truth propagation / observation / reconstruction
    -> explorer snapshot
    -> future renderer / interactive UI
```

No Scientific Registry entry is added for this adapter because it does not define a new scientific model, equation, approximation, or uncertainty statement.

## Intended first UI

A minimal interactive view can use the snapshot to show, simultaneously:

1. Truth and processing SVPs;
2. the transducer and flat seabed;
3. Truth refracted rays;
4. Truth bottom points;
5. reconstructed soundings; and
6. beamwise error.

The initial interface should remain small. Beam selection and processing-SVP editing are sufficient to exercise the end-to-end path before additional error sources are exposed.
