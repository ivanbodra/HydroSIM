# D6 — Beamforming & Electronic Steering

Status: **Mapped**

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

Desired learner message: **beamforming creates a directional response by coherently combining the same physical element data; steering changes the compensation so that response looks elsewhere, and many compensation sets can form many simultaneous virtual RX directions.**

## Scientific guardrails
Multiple RX beams are processing outputs from shared channels, not separate physical transducers. Use Scientific Core for delays, weights, coherent sum, response, peak, beamwidth and grating-lobe behavior. Follow sign/port-starboard/element-index conventions. Do not claim steering intrinsically changes range resolution. Full footprint belongs to D7.

## Dependencies / forward reuse
Consumes D1 phase/wavelength and D5 2-D array/directivity. Passes multiple RX directions to D7; steering penalties to D7/D16; sector-specific steering to D9; stabilization as time-varying steering correction to D11.

## Implementation delta
Make `beamforming ≠ steering` explicit; RX first; strengthen wavefront/channel alignment; add `same channels -> multiple delay sets -> multiple RX beams`; retain angle/delay modes and broadside/current pattern comparison.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.4** — multibeam arrays, beam characteristics and electronic steering: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OpenCourseWare, 2.682 Acoustical Oceanography, Lecture 11 (James Lynch, Spring 2012)** — time-delay/phase beamforming, steering and grating-lobe fundamentals: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/>
- **Hughes Clarke, John E. (2017), “Multibeam Echosounders”**: <https://scholars.unh.edu/ccom/1370/>
- **de Moustier, Christian; Kraft, Barbara J.; McGillicuddy, Glenn (2008), “Multibeam Sonar Calibration Techniques”** — beamforming gain and steering-angle calibration context: <https://scholars.unh.edu/ccom/610/>
- **Kongsberg EM 304 Installation Manual** — real-system evidence for electronically steered multibeam architecture; use as architecture-specific evidence: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf>
