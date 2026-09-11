# D15 — Survey Planning

Status: **Mapped**

**Decision:** `KEEP + REFINE + MAKE NOMINAL-VS-ACHIEVED COVERAGE EXPLICIT`  
**Current:** `web/pedagogical-explorer/src/SurveyPlanningLab.tsx`  
**Scientific contract:** `docs/science/ped_d16_survey_planning_contract.md`

## Purpose

Teach how a hydrographer turns a survey objective and an expected sonar swath into a defensible first-order acquisition plan: survey-line direction, spacing/overlap, number of lines, nominal coverage and on-line acquisition effort.

The lab is deliberately a **reference planner**, not a full mission-planning or compliance engine. Its main pedagogical role is to connect the acoustic/geometric understanding built in D1–D14 to the operational decision: **where should the vessel run, and why?**

## Dominant discovery

```text
survey area + expected usable swath
  -> choose line direction
  -> choose spacing / overlap
  -> place finite survey lines
  -> predict nominal strips of coverage
  -> inspect gaps / overlap
  -> line count + total on-line distance
  -> first-order acquisition time
```

The central distinction is:

```text
PLANNED / NOMINAL COVERAGE
  !=
ACHIEVED / VERIFIED COVERAGE
```

A line plan is a prediction built from expected geometry and operating assumptions. Actual usable swath can change with depth, bottom reflectivity/topography, sound-speed structure, weather, vessel motion, noise, aeration and system settings. D15 must therefore teach planning margin and adaptation, not present the map as a guarantee.

## Inputs

### Primary — guided first-order planning

1. **Survey-area dimensions** — rectangular reference area length and width;
2. **reference depth / sonar configuration**, consumed through the canonical upstream swath model;
3. **line direction** `α`;
4. **spacing mode**:
   - required nominal overlap, or
   - explicit centreline spacing;
5. **overlap percentage or requested line spacing**, according to the selected mode.

### Secondary

- **vessel survey speed**, used only for idealized on-line time in the current Scientific Core;
- sonar angular sector / coverage setting when it changes the canonical upstream usable swath;
- baseline/current comparison for evaluating alternative plans.

### Advanced / later extension

Only when supported by an explicit Scientific-Core contract:

- non-rectangular survey polygons and exclusion areas;
- depth-varying or terrain-aware usable swath;
- expected bottom reflectivity / detection range effects;
- current/wind and maneuvering constraints;
- run-in/run-out and turn geometry;
- cross-lines / check lines;
- safety buffers and no-go areas;
- calibration lines and sound-speed-profile stations;
- multi-platform / USV mission allocation.

**Beam count is not a primary D15 planning control.** More formed beams can change sounding density but do not, by themselves, widen the usable acoustic swath. Keep it fixed or secondary unless the registered upstream sonar model makes it causally relevant to usable swath width.

## Outputs / visual response

### A. Survey-plan map — primary view

On one fixed local-metre map show:

- survey-area boundary;
- line direction / heading reference;
- planned line centrelines in traversal order;
- nominal coverage strip for each line;
- visual overlap between strips;
- uncovered internal gaps when present;
- first/last strip relation to the survey-area edges.

Changing direction, swath or spacing must visibly rearrange the plan rather than only change numeric cards.

### B. Geometry / coverage readouts

Required derived outputs from the Scientific Core:

- canonical usable swath width `W`;
- requested spacing `S_req`;
- actual spacing `S_actual` where multiple lines exist;
- projected cross-line span;
- line count;
- coverage classification: `continuous`, `overlapping`, `touching`, or `gapped`;
- nominal overlap width or gap width.

The learner must be able to see why requested overlap and actual overlap can differ when the planner tightens spacing to anchor coverage at both edges.

### C. Effort consequence

Show:

- total planned **on-line** length;
- idealized on-line acquisition time at configured speed;
- explicit note/visual boundary that turns, transits, run-ins/run-outs, cross-lines and delays are excluded.

### D. Baseline vs current comparison

Compare at least:

- swath width;
- actual spacing;
- line count;
- total on-line length;
- idealized on-line time;
- coverage state.

This comparison should support a planning decision, not just display numbers.

## Interaction sequence

1. **Establish the objective.** Start with one rectangular area, constant reference depth, one MBES configuration and a safe nominal overlap. Show the resulting parallel lines and coverage strips.
2. **Overlap experiment.** Increase overlap while keeping area, direction and swath fixed. Observe spacing decrease, line count/length/time generally increase, and nominal coverage margin increase.
3. **Intentional gap.** Switch to explicit-spacing mode and set spacing larger than the usable swath. The plan must remain valid but visibly show the internal gap. The learner diagnoses why the plan is inadequate for continuous nominal coverage.
4. **Swath experiment.** Change reference depth or angular coverage through the upstream canonical sonar model. A wider usable swath permits wider line spacing/fewer lines in the idealized model; a narrower swath does the opposite.
5. **Direction experiment.** Rotate the line family within the same rectangular area. Show how projected cross-line span, clipped line lengths and therefore line count/total distance can change. `α` and `α + 180°` should preserve the same geometric line family while reversing traversal sense.
6. **Speed experiment.** Change vessel speed. In the current slice, geometry and coverage remain unchanged; only idealized on-line time changes. Make this limitation explicit.
7. **Nominal vs achieved transition.** Freeze the plan and reveal a short warning/bridge: the plan assumes constant usable swath. Ask which field conditions could reduce actual coverage. Point forward to D16 for acquisition trade-offs and D17 for uncertainty, without simulating unsupported effects here.
8. **Final planning decision.** Compare two candidate plans on the same area — for example lower-overlap/fewer-lines versus higher-overlap/more-lines — and require the learner to justify the preferred plan in terms of coverage margin and acquisition effort.

## Operational intuition / trade-offs

| Planning choice | Benefit | Cost / risk |
|---|---|---|
| More overlap | greater nominal margin against line-to-line loss of usable coverage | smaller spacing, usually more lines and more acquisition effort |
| Less overlap | fewer lines / shorter on-line time | less resilience to real swath reduction or line-keeping error |
| Explicit spacing > usable swath | useful as a deliberate failure/trackline scenario | nominal internal gaps; not continuous full-swath coverage |
| Wider expected usable swath | fewer lines can cover the same area | usable swath is condition-dependent; theoretical angular extent is not a guarantee of valid outer-beam detections |
| Change line direction | can reduce cross-line span or suit topography/operations | may increase total line length or conflict with slope, currents, safety or vessel handling |
| Higher speed in current D15 model | lower idealized on-line time | **no quality/density effect is modeled here**; real survey speed can interact with sounding density, bottom tracking, noise and platform dynamics and belongs to a richer acquisition model |
| More formed beams | may increase sampling density within the swath | does not automatically widen usable swath or justify wider line spacing |

**Desired learner message:** **“A survey plan is an operational hypothesis: I choose line direction and spacing from expected usable coverage, then trade acquisition effort against coverage margin. I must still verify and adapt to the coverage actually achieved.”**

## Scientific guardrails

- D15 owns **first-order line planning**, not proof of final survey compliance.
- Use only canonical upstream swath geometry. React must not calculate swath width, line placement, clipping, gaps/overlap, line count or survey time independently.
- Keep **theoretical/angular sonar sector** distinct from **usable swath**. Real usable swath is limited by valid detection performance and operating conditions.
- Planned coverage strips are nominal deterministic geometry, not probabilistic detection assurance.
- Do not claim that a fixed overlap percentage (for example 10% or 20%) is universally sufficient. Manufacturer guidance may describe typical practice but project requirements and conditions govern the actual margin.
- More beams / High Density / extra detections can increase sampling density without increasing swath width. Do not use sounding count as a line-spacing proxy.
- In the current Core, vessel speed changes idealized on-line time only. Do not visually imply a density, SNR, bottom-tracking or uncertainty consequence that is not modeled.
- Current first slice assumes a rectangular local planar area, constant reference swath across all lines and no terrain-following adaptation.
- Do not silently add turn distance/time, run-in/run-out, cross-lines, transits, safety margins, weather delays or current compensation to the current `idealized_on_line_time_s`.
- A gapped explicit-spacing plan is pedagogically valid and must be shown as a poor configuration rather than rejected.
- Survey-line direction is a planning choice, not merely the shortest-route solution. Topography, currents, coastline, safety, platform handling and acoustic performance may dominate real-world orientation decisions.
- Formal survey standards/coverage compliance, uncertainty and feature-detection assurance must not be inferred from this simplified planner. D17 owns TPU/uncertainty; project-specific specifications govern acceptance.

## Dependencies / forward reuse

Consumes:

- D3 acoustic range/detectability intuition;
- D4 sound-speed/environment sensitivity;
- D7 usable swath / finite footprint geometry;
- D9 sector/coverage architecture where relevant;
- D11 vessel-motion operational sensitivity;
- D14 concept of valid georeferenced soundings.

Passes forward:

- planned line geometry, nominal strips and overlap/gap state to D16 Survey Coverage & Acquisition Trade-offs;
- line direction, spacing, expected swath and acquisition effort as context for D17 uncertainty / quality decisions;
- a clear planned-vs-achieved distinction for later Acquisition Simulator work.

## Current implementation delta

`SurveyPlanningLab.tsx` and `survey_planning_api.py` already provide a strong first-order vertical slice:

- configurable rectangular survey area;
- canonical upstream MBES swath from the echosounder model;
- overlap mode and explicit-spacing mode;
- line-direction control;
- Scientific-Core-derived parallel-line geometry and clipping;
- edge-anchored line placement;
- requested versus actual spacing;
- coverage strips and `continuous / overlapping / touching / gapped` classification;
- line count and total on-line length;
- idealized on-line time from vessel speed;
- baseline/current plan comparison.

Required pedagogical refinements:

- make **planned nominal coverage ≠ achieved field coverage** explicit and persistent;
- prioritize area, line direction and spacing/overlap; demote `beam count` because it does not independently define planning swath;
- explain requested versus actual spacing when edge anchoring produces extra overlap;
- make the intentional-gapped-plan experiment a required experience;
- retain vessel speed but label its current consequence as **time only**;
- avoid implying that the existing constant-depth/constant-swath strips include slope, reflectivity, sound-speed, weather or motion degradation;
- add a concise end-state planning comparison where the learner must justify coverage margin versus acquisition effort;
- preserve all plan geometry and calculations in the Scientific Core/API.

No new scientific blocker is required for the minimum D15 mapping. A future higher-fidelity planner would need new Scientific-Core contracts for depth-varying usable swath, non-rectangular/exclusion-zone geometry and maneuver/environment effects before UX exposes those controls.

## Recognized references

- **International Hydrographic Organization (IHO), Publication S-5A, Standards of Competence for Category “A” Hydrographic Surveyors, Ed. 2.0.0, Aug 2026 — H4.2a Survey planning**: sensor/platform selection; planning for depth, bottom character, water-column variability, weather, currents, tides, coastal features and safety; design and justification of survey lines and schedules. <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO S-5A Ed. 2.0.0 — H4.2d Multibeam and phase-measuring bathymetric system operations**: swath coverage/resolution, survey speed, swath planning, calibration, online monitoring and uncertainty as operational considerations. <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **NOAA Office of Coast Survey, Hydrographic Survey Specifications and Deliverables, Version 2026.0.00 (2026)**: authoritative example of project-specific coverage, quality-control, junction/overlap and survey acceptance requirements; supports the boundary that nominal line geometry alone is not proof of achieved coverage/compliance. <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf>
- **Kongsberg Discovery, “Multibeam survey planning — The key to success,” EM Technical Note (current download, accessed Sep 2026)**: operational planning factors including geography, depth/topography, sound speed, weather, coverage capability, overlap and line direction; states that achievable coverage and required overlap are normally used to determine line spacing and that coverage capability varies with operating conditions. <https://www.kongsberg.com/globalassets/kongsberg-discovery/commerce/seafloor-mapping/em2040-mkii/em-technical-note-multibeam-survey-planning-the-key-to-success.pdf>
- **Kongsberg Discovery, EM 2040 MKII product/documentation portal (current, accessed Sep 2026)**: real-system evidence that sounding-density features such as Dual Swath can support density at speed without redefining the basic distinction between sounding density and swath-width planning. <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040-Mk2/>
- **NOAA Office of Coast Survey, “Hydrographic Survey Equipment — Multibeam Echo Sounders” (current, accessed Sep 2026)**: institutional explanation that MBES acquires a swath of soundings for area coverage and that seafloor coverage depends on water depth and system/operating geometry. <https://nauticalcharts.noaa.gov/learn/hydrographic-survey-equipment.html>
