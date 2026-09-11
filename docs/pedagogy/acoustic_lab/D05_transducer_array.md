# D5 — Transducer & Array Construction

**Decision:** `KEEP + REFINE + MOVE + ADD 2-D EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/ArrayDirectivityLab.tsx`

## Purpose
Build physical intuition for how wavelength, aperture, element distribution and weighting in two physical axes create a three-dimensional directional response. The learner must understand that a sonar beam has both along-track and across-track beamwidths rooted in corresponding physical/effective apertures.

## Dominant discovery

```text
larger aperture in one array axis -> narrower beam in that angular plane
frequency ↑ at fixed physical aperture -> aperture/λ ↑ -> beam narrows
longitudinal and transverse aperture can differ -> anisotropic 3-D beam
poor / excessive element spacing -> unwanted / ambiguous lobes
aperture weighting -> lower sidelobes ↔ broader main lobe / changed gain
```

## Inputs
Primary guided progression: frequency `f`; linear-array `N` and spacing `d`; then independent longitudinal and transverse aperture (`L_along`, `L_across`) or equivalent counts/spacings. Always expose `L/λ` and `d/λ` per relevant axis.

Secondary/advanced: element factor; aperture weighting/shading; rectangular 2-D grid; orthogonal TX/RX or Mills-Cross-like example.

Move out: TX↔RX eccentricity/lever arms -> D10; learner steering/delay/phase -> D6.

## Outputs / visual response
- plan-view element layout on fixed spatial scale;
- explicit vessel along-track/across-track axes;
- wavelength and spacing in metres and wavelengths;
- physical/effective aperture in both axes;
- synchronized directivity cuts in both orthogonal planes;
- 3-D or pseudo-3-D main-lobe visualization from the same Scientific Core;
- −3 dB beamwidth in both planes;
- sidelobes and grating lobes identified from computed response.

Recommended: physically reshape the array while the 3-D beam reshapes immediately; baseline/current overlay; conceptual bottom plane only as a preview of anisotropic footprint.

## Interaction
1. Simple broadside linear array: establish `aperture/λ -> beamwidth`.
2. Introduce rectangular 2-D array with independent along/across apertures.
3. Increase longitudinal aperture only; corresponding angular cut narrows.
4. Reset; increase transverse aperture only; orthogonal cut changes.
5. Make apertures strongly unequal; observe non-symmetric beam.
6. Change frequency at fixed physical geometry.
7. Change spacing to expose sidelobe/grating-lobe consequences.
8. Compare weighting only after aperture intuition.
9. Advanced: orthogonal TX/RX / Mills-Cross-like construction as bridge to D7.

## Operational intuition / trade-offs
- larger aperture in one axis -> narrower response in associated plane, at installation/complexity cost;
- unequal apertures -> unequal beamwidths and anisotropic footprint;
- higher frequency at fixed geometry -> narrower response but higher absorption (D3);
- more elements matter through resulting aperture, not `N` alone;
- larger spacing can create grating/ambiguous lobes;
- taper lowers sidelobes at cost of broader main lobe/changed gain.

## Guardrails
D5 is array construction/directivity, not steering. Use Scientific-Core element factor, array factor and weighting. Preserve physical aperture vs effective aperture vs beamwidth vs final seafloor resolution. `beamwidth ≈ λ/L` is intuition, not a universal exact formula. Follow project frame conventions. Typical MBES complementary TX/RX apertures are examples, not universal architecture. Distinguish one-way TX/RX directivity from two-way combination in D7.

## Dependencies / forward reuse
Consumes D1 wavelength and D3 frequency/range trade-off. Passes 2-D geometry/directivity to D6; distinct TX/RX patterns to D7; beamwidth/footprint contributors to D16.

## Implementation delta
Keep the linear array as first experiment, then make independent along/across aperture a required 2-D experiment. Label vessel axes unambiguously. Synchronize plan-view geometry, orthogonal cuts and 3-D response. Preserve fixed scales. Remove installation eccentricity from D5.

## References
- IHO S-5A Ed. 2.0.0 H2.1a/H2.4a.
- MIT OCW 2.682 Lecture 11.
- Hughes Clarke (2017), *Multibeam Echosounders*.
- de Moustier, Kraft & McGillicuddy (2008), *Multibeam Sonar Calibration Techniques*.
- Lanzoni & Weber (2010), *High Resolution Calibration of a Multibeam Echo Sounder*.
- Kongsberg EM 2040 MkII documentation.
