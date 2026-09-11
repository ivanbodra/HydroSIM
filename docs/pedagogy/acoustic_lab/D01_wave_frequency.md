# D1 — Acoustic Wave & Frequency

Status: **Mapped**

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

## Operational intuition / trade-offs
Frequency controls period and wavelength. The frequency/wavelength relation is reused for absorption/range (D3), aperture/beamwidth (D5) and acquisition trade-offs (D16). Higher frequency does not by itself mean better bathymetric resolution; later labs show the separate propagation, bandwidth and aperture consequences.

Desired learner message: **frequency sets how rapidly the acoustic field oscillates; together with sound speed it sets wavelength, which later affects propagation and array/directivity behaviour.**

## Scientific guardrails
No propagation loss, sonar equation, transducer response or bottom detection. Normalized amplitude is not source level/power. Conceptual wave graphics are not a general wavefield solver.

## Dependencies / forward reuse
This is the acoustic foundation. Passes `f`, `T` and `λ` intuition to D2 signal construction, D3 absorption/propagation trade-offs, D5 aperture-in-wavelength reasoning and D16 acquisition trade-offs.

## Implementation delta
Keep current WaveLab/API. Replace adaptive spatial x-domain with fixed/shared domain; make frequency dominant; retain fixed amplitude axis and period/wavelength outputs.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.1 — Underwater acoustics**: competence anchor for acoustic waves, frequency, wavelength and sound speed: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OpenCourseWare, 2.682 Acoustical Oceanography (James Lynch, Spring 2012)** — first-principles wave/acoustics background: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
