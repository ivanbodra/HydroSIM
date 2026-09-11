# D6 — Beamforming & Electronic Steering

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/BeamformingLab.tsx`

## Purpose
Build first-principles intuition for beamforming as coherent spatial combination and beam steering as the specific act of changing the formed beam's look direction electronically. Then show how one physical RX array can form many simultaneous virtual receive directions from the same element-channel data.

## Dominant discovery

```text
oblique wavefront -> different arrival time / phase at each element
beamforming: compensate + weight + sum channels -> directional sensitivity
beam steering: change compensation pattern -> move sensitivity direction
same RX element data + many delay/weight sets -> many simultaneous RX beams
```

The learner must not leave treating beamforming and steering as synonyms.

## Inputs
Primary: arrival/source angle `θsource`; steering angle `θsteer` or equivalent delay gradient; RX first, then TX reciprocal view. Keep array geometry/frequency fixed in core experiment.

Secondary/advanced: delay-gradient vs angle; aperture weighting; number of simultaneous RX directions; phase-only vs true-time-delay only if supported; near-field/dynamic focusing only as advanced validated material.

## Outputs / visual response
- fixed physical array and incoming wavefront;
- per-channel arrival offsets;
- applied compensation delays/phases and residuals;
- aligned/misaligned channel traces before summation;
- coherent summed response;
- directional beam pattern with requested/effective peak;
- broadside/current overlay and steering penalty where computed;
- bridge mode: same captured RX channel data -> several parallel beamforming paths -> different virtual receive directions.

## Interaction
1. RX broadside baseline.
2. Move source with steering fixed; residuals appear and coherent response falls.
3. Steer to source; residuals close and coherent sum recovers.
4. Mis-steer deliberately.
5. Increase steering magnitude and show pattern/gain/shape changes.
6. Duplicate same RX snapshot into multiple delay sets; display several simultaneous virtual RX beams.
7. Then show TX reciprocity.

## Operational intuition / trade-offs
Beamforming creates directional sensitivity; steering moves it. Multiple RX beamformers provide many look directions from one physical aperture but add processing and different downstream geometry. Steering may alter gain/shape away from broadside. Taper lowers sidelobes at beamwidth/gain cost.

## Guardrails
Multiple RX beams are processing outputs from shared channels, not separate physical transducers. Use Scientific Core for delays, weights, coherent sum, response, peak, beamwidth and grating-lobe behavior. Follow sign/port-starboard/element-index conventions. Do not claim steering intrinsically changes range resolution. Full footprint belongs to D7.

## Dependencies / forward reuse
Consumes D1 phase/wavelength and D5 2-D array/directivity. Passes multiple RX directions to D7; steering penalties to D7/D16; sector-specific steering to D9; stabilization as time-varying steering correction to D11.

## Implementation delta
Make `beamforming ≠ steering` explicit; RX first; strengthen wavefront/channel alignment; add `same channels -> multiple delay sets -> multiple RX beams`; retain angle/delay modes and broadside/current pattern comparison.

## References
- IHO S-5A Ed. 2.0.0 H2.4.
- MIT OCW 2.682 Lecture 11.
- Hughes Clarke (2017), *Multibeam Echosounders*.
- de Moustier et al. (2008), *Multibeam Sonar Calibration Techniques*.
- Kongsberg EM 304 documentation.
