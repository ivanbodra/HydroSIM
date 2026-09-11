# D2 — Pulse & Signal Processing

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/SignalLab.tsx`

## Purpose
Move from continuous-wave intuition to finite sonar transmissions: CW pulses and FM/LFM chirps. Build intuition for pulse duration, bandwidth, signal energy, matched filtering and range resolution.

## Dominant discovery

```text
CW: longer pulse -> more energy but poorer raw range resolution
LFM: long pulse + bandwidth + matched filter -> energetic transmission + compressed response
bandwidth ↑ -> compressed response narrows -> range resolution improves
```

## Inputs
Primary: pulse type CW/LFM, duration `τ`, LFM bandwidth `B`, centre frequency `fc`. Secondary: chirp direction; envelope/window only when its sidelobe consequence is visible.

## Outputs / visual response
- finite TX waveform;
- instantaneous frequency vs time;
- matched-filter/pulse-compressed response;
- visible duration and bandwidth extents;
- Scientific-Core-derived range resolution;
- relative pulse-energy indicator at fixed normalized amplitude;
- optional ideal delayed-return timeline before filtering.

## Interaction
Start with short CW; increase `τ`. Switch to LFM. Increase `τ` at fixed `B`, then increase `B`; compare on fixed/shared axes. Reveal chirp/window controls only after the main relationship is understood.

## Operational intuition / trade-offs
- `τ ↑`: more energy; longer TX occupancy; CW range resolution worsens.
- `B ↑`: narrower compressed response / better range resolution, subject to system bandwidth and processing.
- CW→LFM: permits longer energetic transmission with pulse compression.
- frequency consequences on propagation and array geometry are deferred to D3/D5.

Desired learner message: **pulse duration controls how long energy is transmitted, while signal bandwidth controls the compressed range response; LFM allows energy and range resolution to be traded more independently than a simple CW pulse.**

## Scientific guardrails
Do not teach `pulse length = actual minimum range`, pulse length as sole ping-rate determinant, or centre frequency alone as range resolution. Threshold/detection belongs to D8. Do not duplicate D3 propagation/noise physics merely to decorate the return.

## Dependencies / forward reuse
Consumes D1 wave/frequency intuition. Passes pulse duration, bandwidth, matched-filter response and range-resolution intuition to D3, D7, D8 and D9.

## Implementation delta
Retain existing CW/LFM, frequency, duration, bandwidth, direction, envelope, waveform, instantaneous-frequency and matched-filter elements. Add explicit range-resolution and relative-energy/occupancy outputs; use fixed/shared comparison domains; add delayed-return bridge only if scientifically simple.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.1/H2.2** — acoustic signals, pulse length, bandwidth, matched filtering and echo-sounding principles: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Schock, Steven G.; LeBlanc, Lester R.; Mayer, Larry A. (2000), “The Development of Chirp Sonar Technology and Its Applications”** — FM chirp energy and wideband resolution context: <https://scholars.unh.edu/ccom/541/>
- **Hughes Clarke, John E. (2017), “Multibeam Echosounders”** — hydrographic MBES signal/measurement context: <https://scholars.unh.edu/ccom/1370/>
- **Kongsberg EM 2040 MKII product documentation** — real-system evidence for broadband operation, short pulse lengths, large bandwidth and FM chirp: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040-Mk2/>
