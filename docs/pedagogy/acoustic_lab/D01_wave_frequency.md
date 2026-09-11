# D1 — Acoustic Wave & Frequency

**Decision:** `KEEP + REFINE`  
**Current:** `web/pedagogical-explorer/src/WaveLab.tsx`

## Purpose
Build the minimum wave intuition reused later.

## Dominant discovery

```text
frequency ↑ -> period ↓
frequency ↑ at fixed c -> wavelength ↓
```

## Inputs
Primary: frequency `f`. Secondary: normalized amplitude, initial phase, sound speed `c`.

Period and wavelength are derived outputs, never independent controls.

## Outputs / visual response

- `p(t)` on fixed time scale;
- `p(x)` on fixed/shared distance scale;
- `T = 1/f`;
- `λ = c/f`;
- wavelength/cycle markers;
- optional baseline/current overlay on identical axes.

## Interaction
Change frequency first; plots and derived values respond immediately. Then use amplitude/phase to distinguish magnitude/phase from frequency. Reveal sound speed only as a secondary `λ=c/f` experiment.

## Operational intuition
Frequency controls period and wavelength. The frequency/wavelength relation is reused for absorption/range (D3), aperture/beamwidth (D5) and acquisition trade-offs (D16).

## Guardrails
No propagation loss, sonar equation, transducer response or bottom detection. Normalized amplitude is not source level/power. Conceptual wave graphics are not a general wavefield solver.

## Implementation delta
Keep current WaveLab/API. Replace adaptive spatial x-domain with fixed/shared domain; make frequency dominant; retain fixed amplitude axis and period/wavelength outputs.

## References
- IHO S-5A Ed. 2.0.0, H2.1 underwater acoustics.
- MIT OCW 2.682 Acoustical Oceanography.
