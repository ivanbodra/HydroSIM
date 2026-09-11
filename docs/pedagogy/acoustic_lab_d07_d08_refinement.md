# Acoustic Lab — D7/D8 normative refinement

Status: **implementation-ready pedagogical refinement**  
Scope: D7 Echosounders — SBES vs MBES; D8 Bottom Detection  
Parent contract: `docs/pedagogy/acoustic_lab_specification.md`

This file exists as a concise normative refinement while the parent Acoustic Lab specification remains the curriculum index. Scientific equations, sign conventions, detector algorithms and validity domains remain authoritative only in the Scientific Core / Scientific Registry.

---

# D7 refinement — TX × RX geometry in MBES

## Required conceptual model

The learner must not leave D7 with the simplification “MBES = many identical beams”. The essential MBES geometry is:

```text
one transmitted insonified sector / pulse
        ×
many simultaneously formed receive directions
        ->
many distinct TX×RX observation cells across the swath
```

A receive beam is formed from the same physical RX array data by applying a different delay/phase set for each look direction (D6). Each RX direction intersects the transmitted insonified region at a different geometry. Therefore every beam/sounding has its own slant range, incidence geometry and effective seafloor footprint.

## Dominant discovery to add to D7

```text
TX defines where acoustic energy is placed
RX beamforming defines from which directions the return is coherently observed
TX × RX overlap defines the directional observation cell
obliquity / slant range vary across the fan -> footprint geometry varies across the swath
```

## Required visual interaction

1. Show the physical TX aperture and RX aperture separately.
2. Fire one TX pulse and show the **transmitted insonified sector** first, with RX hidden.
3. Reveal one RX beam and highlight the resulting TX×RX intersection on the bottom.
4. Sweep/select successive RX beams without retransmitting; emphasize that the same received aperture data can be beamformed into multiple directions.
5. Reveal all RX beams and their bottom footprints to form the characteristic fan.
6. Select nadir, mid-swath and outer beam and compare on the same scale:
   - steering/look angle;
   - slant range;
   - incidence angle;
   - along-track footprint dimension;
   - across-track footprint dimension;
   - footprint area/shape when available from the Scientific Core.
7. Change depth and sector while retaining a fixed/shared bottom scale.

## Guardrails

- Do not draw each RX beam as an independent transmitted pencil beam.
- Distinguish **TX insonification**, **RX directional sensitivity**, **two-way TX×RX response**, **footprint**, and **sounding/detection**.
- A footprint must come from the registered two-way/pulse/geometry model; decorative ellipses are not scientific outputs.
- Outer-beam degradation must be attributed to the applicable mechanism: greater slant range, obliquity, projected footprint, array response/SNR and bottom-detection conditions. Do not say that steering itself universally worsens range resolution.
- Preserve the difference between sampling density and independent acoustic resolution.

## D7 implementation delta

The next version should make this TX→RX→TX×RX sequence the principal MBES animation before the SBES/MBES coverage comparison. The existing per-beam endpoint/footprint outputs remain useful, but the learner must see **why** there are multiple directional observations before seeing the finished fan.

---

# D8 — Bottom Detection

**Decision:** `KEEP + REFINE + SPLIT PROGRESSION`  
**Current:** `web/pedagogical-explorer/src/BottomDetectionLab.tsx`

## Purpose

Show how an acoustic return becomes a **bottom detection estimate** and why the selected detection can change with signal quality, detection window, algorithm and beam geometry.

D8 connects the signal-domain labs to bathymetry:

```text
received echo / processed return
        -> candidate bottom return
        -> detection method
        -> estimated TWTT and/or arrival angle
        -> retained detection
        -> input to sounding formation
```

The learner must understand that the sounding is **not the echo itself**. It is a spatial estimate derived downstream from a detected time/range and directional information.

## Dominant discoveries

### A — Amplitude/time detection

```text
echo structure + detection window + signal threshold/criterion
        -> selected arrival-time estimate
wrong/ambiguous echo selection
        -> wrong TWTT
        -> wrong range downstream
```

### B — Split-aperture phase detection

```text
same echo observed by two RX sub-apertures
        -> differential phase vs time
phase relationship / zero crossing
        -> refined arrival direction/time estimate within the receive beam
```

### C — High Density / extra detections

```text
phase information contains angular variation within one conventional receive-beam footprint
        -> more than one valid bottom estimate may be resolved
        -> sounding density can increase without pretending the physical beam became narrower
```

High Density is an advanced consequence of phase-supported bottom detection; it is not the introductory discovery.

## Inputs / learner controls

### Primary — Stage 1: amplitude/time detection
- return scenario: clear single echo / weak competing echo / two plausible echoes;
- detection window start/end;
- amplitude criterion or normalized threshold **only when it corresponds to the registered pedagogical detector**;
- retain one / retain multiple candidate detections only after single detection is understood.

### Primary — Stage 2: phase detection
- detection method: amplitude vs split-aperture phase;
- steering / receive-beam reference angle;
- controlled phase-ramp quality or SNR scenario, preferably through presets rather than arbitrary noise sliders.

### Advanced — Stage 3: High Density
- conventional vs High Density toggle;
- one controlled phase-support scenario;
- optional target sounding spacing only if this is an explicit parameter of the registered model.

### Move/de-emphasize
- arbitrary TX delay is not a primary D8 teaching control. Keep it only if needed to demonstrate the difference between arrival offset and total TWTT; otherwise move timing/latency emphasis to D13.
- do not make steering a generic “move the sounding” control. Its role here is the reference direction for phase/beam geometry inherited from D6/D7.

## Expected outputs / visual response

### Stage 1 — amplitude/time
Required:
- processed return / matched-filter magnitude versus lag/time on fixed axes;
- highlighted detection window;
- candidate peaks distinctly marked;
- selected/retained detection(s);
- selected lag / arrival offset / TWTT;
- Truth marker only when the exercise explicitly compares `Observed/Estimated` with hidden/revealed Truth;
- true / false / missed classification in controlled teaching scenarios;
- immediate bridge from TWTT error to downstream range error, without fully reconstructing the sounding.

### Stage 2 — phase
Required:
- two sub-aperture receive channels or a schematic showing their separation;
- differential phase versus time/lag (“phase ramp”);
- receive-beam steering/reference angle;
- zero crossing / fitted crossing used by the registered phase detector;
- estimated bottom arrival/range and directional offset;
- same echo shown in amplitude and phase views so the learner compares what each method observes.

### Stage 3 — High Density
Required:
- one conventional receive-beam footprint;
- conventional single/ordinary detection position(s);
- additional phase-supported detections inside the same footprint;
- count and across-track spacing comparison;
- explicit statement/visual that the **receive beam footprint did not become narrower** merely because more soundings were estimated.

Recommended:
- synchronized signal-domain and bottom-domain views: selecting a candidate on the trace highlights the corresponding range/bottom estimate;
- clean, weak/noisy and competing-return presets;
- use D7's selected beam so footprint/incidence context persists rather than creating a disconnected detector demo.

## Interaction contract

### Stage 1 — make a detection
1. Start with one clean return and a generous window. One candidate is selected.
2. Narrow/move the window until the return is excluded: detection becomes missed/no detection.
3. Restore the window and introduce a competing echo. Both candidates become visible.
4. Adjust the registered amplitude criterion: show a weaker candidate being rejected or retained.
5. Enable multiple retention and show that “multiple detection” means multiple accepted candidates, not additional RX beams.
6. Compare selected lag/TWTT with the controlled Truth only after the learner has predicted which echo will be selected.

### Stage 2 — understand phase detection
7. Select phase detection on the **same beam/echo scenario**.
8. Reveal the split RX aperture and differential-phase curve.
9. Highlight the phase crossing/fitted estimate. Connect it visually to the selected bottom estimate.
10. Degrade the phase-support/SNR scenario and show increased ambiguity/quality loss; where the registered logic falls back to amplitude detection, expose that decision explicitly rather than silently switching algorithms.
11. Compare near-nadir / small-incidence and oblique cases only through validated scenarios; do not state a universal superiority of one detector.

### Stage 3 — High Density
12. Return to a valid phase-supported case. Enable High Density.
13. Keep the physical RX beam footprint fixed while additional phase-supported bottom estimates appear inside it.
14. Compare ordinary count, High Density count and spacing.
15. Disable High Density and verify the geometry/beam remains unchanged while extra estimates disappear.

## Operational intuition / trade-offs

| Condition / choice | Benefit | Cost / risk / interpretation |
|---|---|---|
| Tight detection window | rejects implausible returns and reduces candidate ambiguity | an incorrectly placed window can miss the true bottom |
| Stronger amplitude criterion | rejects weak/noise-like peaks | may reject a valid weak bottom return |
| Multiple detections | can preserve more than one plausible/real return where supported | requires downstream classification/QC; does not mean more RX beams |
| Phase detection | uses split-aperture phase to estimate the bottom within the receive-beam response; can support fine angular/time estimation | requires coherent phase information and adequate samples/SNR; phase can be noisy/ambiguous |
| Amplitude detection | robust alternative where phase information is insufficient | estimate characteristics/resolution differ from phase-supported detection |
| High Density / extra detections | increases sounding sampling density using additional phase information within a receive footprint | more points are not automatically more independent acoustic resolution; quality remains signal/geometry dependent |

Desired operator intuition: **“the sonar does not measure a ready-made depth point. It receives a return, estimates where the bottom response is in time/direction, and only then passes that detection downstream to become a sounding.”**

## Scope boundaries / scientific guardrails

- D8 is **bottom detection**, not post-processing outlier rejection. Do not use later bathymetric cleaning algorithms as the teaching detector.
- Keep `Truth != Observed != Configured != Estimated != Derived`. Truth echo position may classify the exercise result but must never leak into the detector.
- Amplitude and phase detection are algorithm families, not one universal vendor-independent implementation. Expose only algorithms implemented and validated in the Scientific Core.
- Do not invent a generic normalized threshold and present it as a commercial MBES control. If the current pedagogical threshold is retained, label it as a controlled detector parameter.
- Phase detection must explicitly represent **split/sub-aperture differential phase**. A generic waveform “phase zero crossing” without the receive-aperture context is pedagogically misleading.
- Kongsberg documentation describes phase difference between half-beams, fitting the phase time series and finding the zero crossing for bottom determination; it also documents amplitude detection as an alternative when phase support is insufficient. Treat this as an operational example, not a universal algorithm specification.
- High Density must follow the registered Scientific-Core implementation. Do not model it as arbitrary interpolation or insertion of points inside a footprint.
- High Density increases detections/soundings; it does **not by itself prove improved independent spatial resolution**. Preserve the resolution-vs-uncertainty distinction from Schmidt/Weber/Lurton.
- False/missed classifications are pedagogical exercise states. Real detector quality cannot be reduced to the toy scenario's exact threshold/count logic.
- D8 outputs detection time/range/direction information. Full coordinate transformation into a georeferenced 3-D sounding belongs to D14.

## Dependencies / concepts passed forward

Consumes:
- D2: processed pulse/matched-filter response and bandwidth/range-resolution intuition;
- D3: SNR/detection margin;
- D6: receive beamforming/steering and split-aperture directional context;
- D7: selected receive beam, TX×RX footprint, slant range and incidence geometry.

Passes forward:
- per-beam detection(s) to D9 Multisector MBES;
- TWTT/range and arrival angle to D14 Sounding Formation;
- ordinary vs extra/High-Density detections to D16 coverage/density trade-offs;
- detection quality/geometry as a contributor to D17 uncertainty.

## Current implementation assessment

`BottomDetectionLab.tsx` already contains useful components:
- clean / later / competing-echo presets;
- detection window;
- normalized threshold;
- single / multiple retention;
- candidate/eligible/retained distinction;
- true/false/missed exercise classifications;
- TWTT/arrival/detected-angle readouts;
- High Density comparison and additional across-track bottom points.

However, its current **phase-zero-crossing option is explicitly unsupported**, while the UI text describes High Density phase behavior. This creates a pedagogical discontinuity: the advanced phase-based consequence exists before the learner can see the underlying split-aperture phase detector.

## Next-version implementation delta

1. Preserve the current amplitude/time detector as **Stage 1** and simplify the first view to return → window/criterion → candidate → selected TWTT.
2. Implement/validate the phase detector in the Scientific Core **before** exposing it as a functional learner control.
3. Replace the generic phrase `phase zero crossing` with a visible split-aperture causal model: two RX half-apertures → differential-phase time series → fitted/registered crossing → detection.
4. Do not silently fall back from phase to amplitude; expose `phase unavailable / amplitude fallback` if the registered model does so.
5. Move High Density behind the phase-detection stage. Keep its physical beam/footprint unchanged while additional detections appear.
6. Keep the ordinary-vs-High-Density count/spacing comparison, but add a strong visual distinction between **point density** and **physical footprint/resolution**.
7. Reuse the selected D7 beam/footprint context where practical so the learner sees one continuous acquisition chain.
8. De-emphasize `txDelay` as a learner-facing detector control; timing/latency belongs mainly to D13.
9. Keep threshold/window controls only as documented pedagogical detector parameters, not as claimed universal commercial MBES settings.
10. Preserve Truth solely for assessment/classification and never feed it into candidate selection.

## Recognized references

- **IHO S-5A Ed. 2.0.0** — hydrographic acoustics, echo sounding and MBES competence anchor; use the current S-5A learning outcomes for acoustic measurement principles and system operation: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Kraft & de Moustier (2004), “Variable Bandwidth Filter for Multibeam Echo-sounding Bottom Detection”** — bottom detection quality depends on estimating arrival time/angle and on appropriate filtering across operational environments: <https://scholars.unh.edu/ccom/312/>
- **Hamel (2020), CCOM/UNH, “Effects of Transmission Side Lobe Interference on Multibeam Echosounder Phase Ramps”** — split-aperture correlation, differential phase and zero-crossing interpretation in MBES bottom detection: <https://scholars.unh.edu/ccom_seminars/325/>
- **Araujo (2020), CCOM/UNH, “Potential for Non-Conventional Use of Split-Beam Phase Data in Bottom Detection”** — phase information and alternative time/angle-series bottom-detection approaches: <https://scholars.unh.edu/ccom_seminars/311/>
- **Schmidt, Weber & Lurton (2012), “Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems”** — distinguishes sounding density/resolution/uncertainty and prevents equating more detections with unlimited independent resolution: <https://scholars.unh.edu/ccom/848/>
- **Kongsberg EM 2040 System Overview / Instruction Manual — Bottom detection** — operational example of half-beam differential phase, phase-curve zero crossing, amplitude fallback and High Density multiple detections: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/346210_em2040_instruction_manual.pdf>
- **Kongsberg EM 2040 MkII** — current product evidence for Extra Detections / high-resolution hydrographic operation: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>

---

## Canonical merge instruction

When editing `acoustic_lab_specification.md`, merge the D7 refinement into its D7 purpose/output/interaction/guardrail sections, mark **D8 = Mapped**, insert the D8 specification above, and advance the review queue to **D9 — Multisector MBES**. Do not duplicate this text indefinitely once the parent is updated; the parent remains the canonical curriculum contract.
