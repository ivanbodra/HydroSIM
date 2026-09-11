# D3 — Sonar Equation & Propagation Loss

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/SonarEquationLab.tsx`

## Purpose
Build acoustic-budget intuition: the transmitted signal must survive two-way propagation and bottom interaction and remain sufficiently above noise to support detection.

## Dominant discovery

```text
source level ↑ -> received level / SNR margin ↑
range ↑ -> two-way transmission loss ↑ -> received level / SNR ↓
frequency ↑ -> generally absorption ↑ -> long-range margin ↓
noise ↑ -> SNR ↓ while received signal level is unchanged
```

## Inputs
Primary: range `R`, source level `SL`, frequency `f`, noise level `NL`. Secondary: controlled bottom-return term; model-specific absorption environment; required/reference SNR. `% power` is allowed only through a documented system mapping to source level.

## Outputs / visual response
- RL vs range and SNR vs range on fixed scales;
- shared selected-range marker;
- two-way TL separated into spreading and absorption;
- `SL -> TL -> bottom return -> TL -> RL -> NL -> SNR` contribution budget;
- explicit detection margin relative to a clearly labelled SNR reference;
- same-scale frequency comparison.

## Interaction
Increase range first; then independently vary SL and NL so the learner sees that SL changes RL/SNR while NL changes only SNR. Compare frequencies at fixed geometry/environment. Optionally vary bottom-return strength.

## Operational intuition / trade-offs
Power/SL can recover SNR/range but does not intrinsically improve resolution. Longer/slanted ranges cost SNR. Higher hydrographic frequencies generally sacrifice range through higher absorption. Noise reduces detectability without changing propagation loss.

Desired learner message: **the sonar equation is an energy/detectability budget: range, propagation loss, bottom return and noise determine whether enough signal survives for a detector; source level does not directly create finer resolution.**

## Scientific guardrails
Use registered absorption/spreading models and correct one-/two-way conventions. D3's SNR reference is not D8's detector. Do not turn simplified bottom response into a backscatter module or teach frequency as a single-variable resolution rule.

## Dependencies / forward reuse
Consumes D1 frequency/wavelength and D2 pulse/signal intuition. Passes received-level/SNR context to D7 footprint geometry, D8 detectability and D16 acquisition trade-offs.

## Implementation delta
Retain fixed RL/SNR axes, range marker and frequency comparison. Separate spreading/absorption, add detection margin, make range the first experiment and reduce raw-card emphasis. Bottom scattering and beam gains remain fixed by default.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.1b–d** — transmission loss, absorption, noise and sonar-equation competence: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OpenCourseWare, 2.682 Acoustical Oceanography (James Lynch, Spring 2012)** — propagation, transmission loss and ocean-acoustics foundations: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- **Hughes Clarke, John E. (2017), “Multibeam Echosounders”** — hydrographic MBES acoustic-budget context: <https://scholars.unh.edu/ccom/1370/>
- **Schmidt, Val E.; Weber, Thomas C.; Lurton, Xavier (2013), “Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems”** — SNR, spatial resolution and measurement-uncertainty trade-offs: <https://scholars.unh.edu/ccom/848/>
