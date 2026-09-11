# D16 — Survey Coverage & Acquisition Trade-offs

Status: **Mapped**

**Decision:** `KEEP + REFOCUS AS INTEGRATION / TRADE-OFF LAB`  
**Current:** `web/pedagogical-explorer/src/TradeoffLab.tsx`  
**Scientific contract:** `docs/science/ped_d17_coverage_density_contract.md`

## Purpose

Integrate the earlier Acoustic Lab into an operational acquisition decision: **how do sonar geometry, ping cadence, vessel speed, bottom-detection mode and sampling configuration jointly change physical coverage, sounding density and survey efficiency?**

D16 must not re-teach beamforming, footprint, bottom detection or survey-line planning. It is the place where the learner discovers that several quantities commonly conflated in practice are different:

```text
INSONIFIED COVERAGE
!= SOUNDING DENSITY
!= ACOUSTIC / SPATIAL RESOLUTION
!= SURVEY EFFICIENCY
```

A configuration may improve one of these while degrading another. The learner should therefore compare configurations rather than search for one universally "best" setting.

## Dominant discovery

```text
configured sonar + ping cadence + vessel speed
  -> finite footprints + retained detections + ping-origin spacing
  -> across-track and along-track sampling pattern
  -> covered / gapped insonified support + sounding density
  -> acquisition benefit + cost
  -> defensible operating choice for the survey objective
```

Key causal relationships for the minimum lab:

```text
speed ↑ at fixed ping rate
  -> along-track ping spacing ↑
  -> along-track sampling density ↓
  -> finite-footprint gaps may appear

ping rate ↑ at fixed speed
  -> along-track ping spacing ↓
  -> along-track sampling density ↑

more retained detections / High Density
  -> local sounding spacing may decrease
  -> sounding density may increase
  -> physical parent footprint / instantaneous insonified coverage does NOT widen

beam-count / beam-spacing change
  -> retained centre distribution changes
  -> across-track sounding spacing changes
  -> does NOT by itself imply narrower physical beams or better independent acoustic resolution

finite footprint union
  -> actual idealized insonified coverage
  -> overlaps are merged, gaps remain visible
```

Wider angular coverage, frequency, pulse, beamwidth and multisector choices may be compared only through consequences already provided by the Scientific Core. D16 must not invent an unmodelled relation merely because a control is present in the UI.

## Inputs

### Primary — guided trade-off controls

1. **Vessel speed** `v`;
2. **effective ping rate** `f_p`;
3. **angular sector / swath configuration** supplied to the canonical echosounder geometry;
4. **beam count / beam-spacing mode** (`equiangular` / `equidistant`) as a sampling-distribution control, not a resolution control;
5. **RX beamwidth / registered footprint geometry** where supported by the selected canonical model;
6. **bottom-detection sampling mode**, beginning with conventional retained detections and then comparing additional valid detections / High Density.

The first experiment should use only `speed` and `ping rate`; geometry remains fixed so that the learner sees `v / f_p` directly as a spatial-sampling consequence.

### Secondary

- depth / sonar-to-bottom separation;
- multisector TX sequence/configuration when its effect is already resolved by the canonical D9 geometry;
- ordinary multiple detections;
- baseline/current comparison;
- selected beam or local sampling cell for inspecting one footprint and its neighboring soundings.

### Advanced / comparison-only

- frequency;
- pulse duration;
- TX-sector frequency/timing;
- upstream system modes such as dual-swath-like behavior.

These controls may appear only when their learner-visible consequences are produced by an authoritative Core contract. A manufacturer feature is evidence that such an operational trade-off exists, not authorization to synthesize it in React.

## Outputs / visual response

The lab should be dominated by one connected **survey-strip view** rather than independent metric cards.

### A. Spatial acquisition strip

Show a short sequence of pings in a local survey frame:

- vessel trajectory / ping origins;
- finite footprint support for successive pings;
- retained bottom soundings;
- additional High Density detections, visibly distinguished but inside the same parent acoustic support;
- across-track and along-track gaps;
- merged covered region.

The learner must be able to see whether a number changing actually represents **more illuminated seabed**, **more retained points**, or merely a different distribution of points.

### B. Coverage view

From the canonical footprint union show:

- instantaneous footprint intervals / polygons;
- merged insonified coverage;
- internal gap intervals and widths;
- covered width;
- geometric beam-centre swath extent separately;
- across-track classification `continuous / gapped / unavailable`;
- along-track footprint continuity where the Core supplies along-track footprint length.

Never paint the whole geometric swath as "covered" solely because beam centres span it.

### C. Sampling / density view

Show:

- along-track ping spacing `Δx_ping`;
- along-track ping density when defined;
- actual adjacent across-track sounding spacings from retained bottom positions;
- min / mean / max across-track spacing;
- local geometric sampling-density proxy only where its validity conditions are satisfied;
- ordinary vs retained vs High Density added sounding counts.

A density heatmap or sampling-cell overlay is useful only if calculated from these Core-derived quantities, not from screen pixels.

### D. Baseline × current comparison

Keep one reference configuration and compare only a small number of decision metrics on shared scales:

- covered width / gap state;
- along-track spacing;
- across-track spacing distribution;
- retained sounding count / density;
- optionally an acquisition-efficiency proxy only if the Core defines it.

The comparison should name the **benefit and cost**, not merely display arrows.

## Interaction sequence

1. **Establish the four different concepts.** Start with fixed geometry, one conventional detection per beam, moderate speed and ping rate. Identify separately: footprint coverage, sounding positions, spacing/density and survey progression.
2. **Speed experiment.** Increase speed while holding ping rate and sonar geometry fixed. Ping origins separate; retained sounding rows separate; along-track density decreases. If spacing exceeds the canonical along-track footprint, a visible gap appears.
3. **Ping-rate experiment.** Restore speed, then increase ping rate. Show the reciprocal effect on along-track spacing. Do not claim that an arbitrary requested rate is physically achievable by every sonar/range condition.
4. **Beam-count / spacing experiment.** At fixed physical beamwidth and sector, increase formed beam count or change equiangular/equidistant spacing. Sounding centres redistribute / become denser; make explicit that this did not automatically narrow the beam or shrink its footprint.
5. **Footprint continuity experiment.** Change the registered beamwidth/geometry so finite footprints separate or overlap. Compare beam-centre swath, covered width and gap state. This is the key demonstration that `beam centres across a swath` are not themselves coverage.
6. **High Density experiment.** Freeze the acoustic geometry and enable valid enhanced phase / High Density detections. Additional points appear within existing support; sounding density increases while the footprint union remains unchanged.
7. **Depth / sector comparison.** Compare a narrower and wider/deeper geometry on fixed scales using the upstream D7 consequences. Let the learner see coverage gain together with changed spacing / footprint geometry; recall rather than re-teach outer-swath SNR/refraction/uncertainty costs.
8. **Final acquisition decision.** Present two or three valid configurations for the same local strip. Ask which is preferable for (a) efficient broad-area mapping and (b) dense sampling of a critical area, then reveal the measurable benefit/cost of each rather than a universal winner.

## Operational intuition / trade-offs

| Change | Benefit that may occur | Cost / limitation to retain |
|---|---|---|
| Speed ↑ at fixed ping rate | greater distance traversed per unit time | larger along-track spacing, lower spatial sampling density, possible footprint gaps |
| Ping rate ↑ at fixed speed | denser along-track sampling | achievable rate depends on sonar/range/processing architecture; configured rate is not universally attainable |
| Wider usable swath / sector | more across-track area per line | outer geometry can carry larger range, footprint, SNR, refraction, motion and uncertainty costs learned earlier |
| More formed beams | more directional samples / potentially smaller centre spacing | does not intrinsically reduce physical beamwidth or guarantee independent resolution |
| Equidistant spacing | can regularize seabed-centre spacing over a reference geometry | it is a beam-placement strategy, not a change in physical beamwidth |
| Larger / overlapping footprints | may close idealized insonification gaps | greater footprint does not mean finer spatial resolution |
| High Density / extra valid detections | denser retained sampling of already supported seabed | does not create extra physical beams or widen instantaneous insonified coverage |
| Higher frequency | may support narrower beams / finer system resolution in suitable arrays | generally increases absorption and can reduce useful range; consequence must come from upstream canonical models |
| Dual-/multi-swath architectures | can sustain higher along-track sounding density at survey speed in systems that implement them | architecture-specific; must not be generalized to every MBES |

## Desired learner message / intuition

**“Coverage, density, resolution and efficiency answer different questions. I should change a survey setting only after predicting which of those quantities it actually changes, inspect the physical sampling pattern, and accept the cost that comes with the benefit.”**

A second required takeaway is:

**“More soundings do not necessarily mean more seabed was insonified, and more insonified area does not necessarily mean finer resolution.”**

## Scientific guardrails

- Preserve the authoritative distinction in `ped_d17_coverage_density_contract.md`: **insonified coverage is not sounding density**.
- Compute coverage from the union of canonical finite footprints, not from beam-centre extent, point count or a filled UI polygon.
- Compute across-track spacing from actual retained bottom positions. Never substitute `swath width / beam count` unless the canonical geometry genuinely produces equal spacing.
- At `v = 0`, ping-origin spacing is zero but spatial density per travelled metre is undefined; do not display infinite useful density.
- `ρ_A = 1/(Δx Δy)` is only the defined geometric sampling-density proxy for the regular reference strip. It is not statistical independence, probability of detection, IHO feature-detection compliance or a quality score.
- High Density and generic multiple detections may add retained points without changing their parent acoustic footprint. Do not redraw them as extra beams or wider coverage.
- Beam count and sounding count are not acoustic resolution. Retain D2/D5/D7 distinctions among range resolution, beamwidth, footprint, point spacing and terrain resolvability.
- A wider configured angular sector is not automatically **usable** coverage. D3/D4/D11/D17 constraints on SNR, refraction, motion and uncertainty still apply even when the minimum reference strip does not recalculate all of them.
- Do not silently make ping rate a function of depth/range, pulse duration or TX sequence unless a canonical model explicitly provides that coupling. The current D16 density adapter accepts effective ping rate as a configured input.
- Manufacturer claims such as dual-swath maintaining density at higher vessel speed are architecture examples, not universal sonar laws.
- D15 owns line layout, adjacent-line overlap and total planned survey effort. D16 owns within-strip acquisition sampling consequences and trade-offs.
- D17 owns formal uncertainty / TPU. D16 may remind the learner that outer-swath geometry has uncertainty costs but must not generate a substitute TPU score.

## Dependencies / forward reuse

Consumes:

- D2 pulse / range-resolution distinctions;
- D3 range, frequency and SNR trade-offs;
- D4 refraction sensitivity with obliquity;
- D5 beamwidth / aperture / resolution distinctions;
- D7 finite TX×RX footprint, beam spacing and swath geometry;
- D8 retained conventional / enhanced bottom detections;
- D9 multisector identity/timing where used;
- D11 motion/stabilization consequences;
- D15 planned line/swath context.

Passes forward:

- concrete sampling geometry and gap/density consequences to D17 uncertainty interpretation;
- operational understanding needed later by the Acquisition Simulator, where changing speed, ping cadence and sonar configuration should produce acquisition-pattern consequences without duplicating these equations in the UI.

## Current implementation delta

`TradeoffLab.tsx` already assembles several strong canonical slices: D7-style echosounder geometry, D9 multisector configuration, D8 bottom detection / High Density and the `survey-density` API. The Python adapter already derives:

- speed conversion and `v / f_p` along-track spacing;
- along-track ping density;
- actual retained across-track spacings and local density summaries;
- finite-footprint union;
- internal gaps / continuous-vs-gapped classification;
- covered width separately from geometric beam-centre swath;
- along-track gap by beam when footprint length is available;
- ordinary, retained and High Density-added counts;
- the explicit invariant `high_density_widens_coverage = False`.

Preserve that Scientific-Core path.

Next-version pedagogical changes:

- replace the present wall of approximately equal-weight linked controls with a guided progression: `speed -> ping rate -> beam distribution -> footprint continuity -> High Density -> integrated comparison`;
- make the spatial acquisition strip the dominant output; metric cards become supporting evidence;
- explicitly label **coverage**, **density**, **resolution** and **efficiency** as different quantities;
- show footprint union and retained soundings in the same spatial view so High Density can visibly increase points without widening coverage;
- keep baseline/current fixed-scale comparison, but annotate the benefit/cost responsible for each change;
- de-emphasize pulse, frequency and TX-sequence controls unless a visible consequence is backed by an upstream canonical response;
- do not imply that the current configured `ping_rate_hz` is an achievable-rate solver; it is an effective acquisition cadence supplied by the learner;
- avoid React-derived scientific summaries when the Python API already exposes canonical spacing/coverage results; presentation-only arithmetic should not become a second scientific contract;
- preserve the current local survey-frame declaration (`+x` along-track, `+y` Starboard) and do not mix it with D8/D9 beam-angle sign conventions.

## Recognized references

- **International Hydrographic Organization (IHO), S-5A Ed. 2.0.0 (2026), H4.2d — Multi beam and phase-measuring bathymetric system operations.** Explicitly includes swath coverage and resolution, object detection, survey speed in relation to system parameters, swath planning, on-line monitoring and uncertainty models: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **NOAA Office of Coast Survey, Hydrographic Surveys Specifications and Deliverables, Version 2026.0.00 (2026).** Defines coverage and feature-detection assessments and distinguishes actual bathymetric/seafloor coverage from line-spacing-only acquisition: <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf>
- **NOAA Office of Coast Survey, “Hydrographic Survey Equipment — Multibeam Sonars” (current institutional guidance, accessed 2026).** Describes MBES swath acquisition for full/partial bottom coverage and notes that seafloor coverage depends strongly on water depth: <https://nauticalcharts.noaa.gov/learn/hydrographic-survey-equipment.html>
- **Hughes Clarke, J. E. (2017), “Multibeam Echosounders,” in _Submarine Geomorphology_, Springer.** Describes the corridor/swath nature of MBES acquisition and the dependence of practical spatial resolution on bandwidth, projected beamwidth, spacing, stabilization and platform altitude: <https://scholars.unh.edu/ccom/1370/> ; DOI: <https://doi.org/10.1007/978-3-319-57852-1_3>
- **Kongsberg Discovery, EM 2040 MKII — current product documentation (accessed 2026).** Architecture-specific evidence for wide-swath/high-resolution modes, High Density / Ultra High Density beam patterns and dual-swath operation; the manufacturer explicitly describes dual swath as a means of maintaining sounding density at useful vessel speed: <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/>
- **Kongsberg, EM 2040 MKII Data Sheet.** Provides concrete system limits/examples including frequency range, maximum ping rate, angular swath, beam counts and beam-spacing modes; use only as system evidence, not universal operating laws: <https://www.kongsberg.com/globalassets/kongsberg/1.-what-we-do/2.-ocean-space/5.-seafloor-mapping/em-multibeams/em2040/em-2040---mkii-data-sheet.pdf>
