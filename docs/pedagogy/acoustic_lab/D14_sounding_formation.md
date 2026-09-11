# D14 — Sounding Formation

Status: **Mapped**

**Decision:** `KEEP + REFINE + REFOCUS ON DATA FUSION / GEOMETRIC RECONSTRUCTION`  
**Current:** `web/pedagogical-explorer/src/SoundingFormationLab.tsx`  
**Current Scientific-Core adapter:** `src/hydrosim/app/sounding_formation_api.py`

## Purpose

Teach how a valid bottom detection becomes a **spatial hydrographic sounding** only after the acoustic observables are associated with the correct sonar event, sensor geometry, platform pose, propagation model and reference frame.

D8 ends with a detection such as `(t, θ)` or an equivalent observed range/direction pair. D14 must make clear that this is **not yet a georeferenced sounding**. The sounding is formed by combining that observation with the system state that tells us **where the sonar was, how it was oriented, which beam/sector produced the detection, how sound propagated, and which spatial/vertical reference is being used**.

The lab is not a complete bathymetric processing package. It is the pedagogical bridge from **Observed detection** to **Derived 3-D sounding**.

## Dominant discovery

```text
BOTTOM DETECTION
  -> identify the correct ping / TX sector / beam / detection
  -> convert TWTT + propagation model into range/path
  -> combine detected direction with beam / sonar geometry
  -> associate the correct time-matched sensor pose
  -> apply installation geometry / lever arms / mounting orientation
  -> transform sensor-frame observation into vessel/navigation frame
  -> apply the intended vertical/spatial reference
  -> one derived 3-D sounding
```

The central causal message is:

```text
same acoustic detection + different associated pose / geometry / sound-speed model
  -> different reconstructed sounding
```

and conversely:

```text
correct detection + correct association + correct geometry
  -> sounding remains tied to the physical seabed
```

The lab succeeds when the learner can explain why **TWTT and beam angle alone are insufficient to produce a hydrographic sounding**.

## Inputs

Inputs should be revealed progressively. The learner should not begin with every system parameter exposed at once.

### Primary — observation-to-sounding experiment

1. **Selected retained detection** from D8:
   - TWTT `t`;
   - detected/associated direction or across-track angle `θ`;
   - detection method/status as context only;
2. **Associated vessel/sensor pose** at the required event epoch:
   - position;
   - roll, pitch, yaw/heading;
3. **Sound-speed / propagation model** used for reconstruction.

These are the minimum learner controls needed to see one observed acoustic detection become one spatial point.

### Secondary — installation / association

- sonar lever arm from D10;
- sonar mounting orientation from D10 when the Scientific Core supports it;
- ping / beam / detection identity;
- TX sector identity and TX epoch from D9;
- association epoch / timing source from D13;
- selected reference frame / vessel-body axes.

### Advanced / diagnostic

- deliberately wrong pose association;
- deliberately wrong lever arm / mounting orientation;
- deliberately wrong or stale propagation profile;
- wrong parent sector / TX epoch;
- optional hydrographic vertical-reference correction / datum transformation when supported by a registered Scientific-Core model;
- Truth overlay for teaching/validation only.

Do **not** make raw RX-window configuration a primary D14 control. RX timing windows belong to acquisition/timing pedagogy; D14 should consume the already accepted detection and its association metadata.

## Outputs / visual response

All views must be synchronized and derive from one Scientific-Core state.

### A. Observation card — what came from D8

Show clearly:

- ping index;
- sector / beam / detection identity;
- detection method;
- TWTT;
- detected angle/direction;
- association epoch.

Label this explicitly as **Observed acoustic detection**, not as a sounding.

### B. Range / acoustic-path view

Show the registered conversion from observed travel time to the path/range representation used by the current model.

For the current constant-sound-speed first slice:

```text
TWTT + c -> reciprocal one-way range
```

When the full ray-tracing path is used later, the visual must show that D4's propagation model changes both depth and horizontal placement for oblique beams. Do not imply that `R = c t / 2` is the universal final sounding equation in a refracting water column.

### C. Frame / transform chain

Show a connected transform visualization:

```text
DETECTION / BEAM FRAME
        ↓
SONAR / SENSOR FRAME
        ↓ installation transform
VESSEL BODY FRAME
        ↓ time-matched pose
NAVIGATION / EARTH FRAME
        ↓ optional vertical reference
HYDROGRAPHIC SOUNDING
```

Required visual elements:

- sonar origin;
- beam/detection direction vector;
- vessel VRP and lever arm;
- vessel axes and current pose;
- navigation/Earth axes or project frame;
- reconstructed 3-D point.

The learner should be able to see **which transform moved or rotated the observation** when a control changes.

### D. Sounding result

Show:

- reconstructed X/Y/Z or equivalent project coordinates;
- sensor origin used;
- slant/path range used;
- final direction vector in destination frame;
- reference frame / vertical-reference label;
- concise provenance: detection -> pose -> geometry -> propagation model.

### E. Truth / error comparison — teaching only

When Truth is enabled:

- Truth sounding;
- reconstructed sounding;
- error vector `ΔX, ΔY, ΔZ`;
- same physical scale and fixed axes.

Truth must never be presented as data available to an operational processor.

### F. Association integrity view

Recommended small provenance strip:

```text
PING 12
  └─ TX sector 2 @ t_tx
      └─ RX beam 47
          └─ detection 1
              └─ pose sample / interpolated state @ required epoch
                  └─ reconstructed sounding
```

This makes D9/D13 consequences visible without turning D14 into another timing lesson.

## Interaction sequence

1. **Detection is not yet a point.** Start with a retained D8 detection: TWTT + direction. Show it in the sonar frame with no navigation pose applied. Ask: *Where is this on Earth / in the survey frame?* The correct answer is: not enough information yet.
2. **Range from time.** Apply the registered propagation model. The detection now has a range/path but still lacks a georeferenced location.
3. **Direction + range in the sonar frame.** Form a local observation vector from range/path and detected direction. Show the resulting point relative to the transducer.
4. **Installation transform.** Apply D10 lever arm and mounting orientation. Show sonar-frame geometry move into the vessel frame. Deliberately change a lever arm so the learner sees a systematic shift without changing the acoustic detection itself.
5. **Pose association.** Apply the D11/D13 time-matched vessel position and attitude. The point moves/rotates into the navigation frame. Change roll or heading while holding the acoustic detection fixed; show the spatial consequence.
6. **Wrong-time experiment.** Keep the physical event fixed but associate a stale/wrong pose sample. The reconstructed point must move. This demonstrates why D13 synchronization/latency matters to sounding formation.
7. **Propagation mismatch.** Hold detection and pose fixed; change only the processing sound-speed model/profile. Show the reconstructed point move while the Truth seabed remains fixed. This reconnects D4 without re-teaching refraction.
8. **Sector / beam identity check.** Where the core supports multisector association, deliberately attach the detection to the wrong TX sector/epoch or beam direction and show the resulting inconsistency. Do not invent sector physics in the frontend.
9. **Vertical/spatial reference.** Reveal the final project/hydrographic reference as a separate last transformation. Changing reference must change coordinates/reference labels according to the registered transform, not move the physical seabed Truth.
10. **Final integrated reconstruction.** Reset all associations/models to correct values. Step through `Observed -> Configured -> Derived` and show the reconstructed sounding converge on Truth within the limits of the simplified model.

## Operational intuition / trade-offs

| Component | What it contributes | Failure consequence to retain |
|---|---|---|
| TWTT / detected range observable | distance/path information from acoustic return | wrong detection time shifts the sounding along the acoustic path |
| Detected beam/direction | angular direction of the return | wrong beam/phase-angle association displaces the sounding laterally/vertically |
| Sound-speed / ray model | converts travel time and steering geometry into acoustic path | mismatch distorts range and, for oblique rays, horizontal position as well as depth |
| Lever arm / mounting orientation | relates sonar measurement centre/axes to vessel reference | systematic position/orientation error propagates into every sounding |
| Time-matched position / attitude | places the sonar observation in navigation/Earth frame | stale or mis-timed pose creates motion-correlated displacement |
| Sector / ping identity | links detection to the correct transmit event and geometry | wrong epoch/sector breaks range/direction association |
| Vertical / spatial reference | expresses the point in the intended hydrographic reference | wrong datum/reference can make a geometrically consistent point operationally wrong |

Desired learner intuition: **“A sounding is not the echo and not the detection. It is the result of correctly associating an acoustic observation with propagation, installation geometry, platform state, time and reference frames.”**

## Scientific guardrails

- Preserve `Truth != Observed != Configured != Estimated != Derived` explicitly. D8's `BottomDetection` is Observed; installation/processing pose and model choices are Configured; the spatial sounding is Derived/Estimated according to the Scientific Core contract.
- D14 must consume the **retained detection**, not re-run bottom detection in the UI.
- Do not reduce a refracted-water-column solution to a decorative straight ray. The current first slice is explicitly a **stationary reciprocal constant-sound-speed reconstruction**. A layered/SVP experience must use D4's registered ray tracer or another Scientific-Core model.
- TWTT, one-way range, slant range and geometric depth are different quantities. Label each one explicitly.
- Use the exact project coordinate frames, rotation order, axis signs, lever-arm direction and angle conventions from the Scientific Core.
- A vessel pose must be associated at a defined event epoch. Do not silently use “current pose” when the correct measurement epoch differs.
- Where TX and RX geometry/epochs differ, do not assume a monostatic/concentric observation unless the selected model explicitly makes that approximation.
- Do not double-apply attitude, stabilization or lever-arm corrections already represented in the authoritative sonar/system geometry.
- Sensor installation and reference changes must preserve D10 invariants: redefining VRP does not physically move sensors.
- Motion compensation must preserve D11 semantics: corrected sounding geometry does not mean the vessel stopped moving.
- Timing consequences belong to D13; D14 demonstrates their spatial effect but does not redefine timing logic.
- Formal uncertainty propagation belongs to D17. A Truth-error vector in D14 is a deterministic teaching diagnostic, not TPU.
- A hydrographic water-level/datum transform is distinct from vessel-frame `Z` geometry. Only show it when a defined transform exists.
- Do not imply that a single vendor's output datagram is the universal raw-data model. Manufacturer formats are evidence for real system integration only.

## Dependencies / forward reuse

Consumes:

- D4 sound-speed / refraction model;
- D7 beam/footprint geometry;
- D8 retained detection `(t, θ)` / equivalent observation;
- D9 ping/sector identity and TX epoch;
- D10 sensor positions, lever arms, mounting axes and vessel frame;
- D11 platform pose / motion state;
- D12 accepted ancillary-sensor streams;
- D13 time synchronization, latency and sample/pose association.

Passes forward:

- georeferenced / project-frame sounding positions to D15 Survey Planning comparisons and D16 coverage/density consequences;
- deterministic residual/error mechanisms and component sensitivities to D17 Uncertainty / TPU;
- the same sounding-formation chain as the conceptual bridge to the future Acquisition Simulator raw-like data pipeline.

## Current implementation delta

The current Scientific-Core/API already provides an unusually useful first vertical slice:

- a staged `transmit -> propagation -> seabed interaction -> receive -> bottom detection -> TWTT/range -> beam angle -> pose association -> reconstruction -> Truth comparison` chain;
- canonical `BottomDetection` -> acoustic observation conversion;
- a configurable TWTT and detected across-track angle;
- vessel position and roll/pitch/yaw;
- VRP-to-sensor lever arm;
- sensor pose derived through canonical geometry transforms;
- constant-sound-speed reciprocal reconstruction;
- Truth vs reconstructed point and error vector;
- ping/beam/detection identity.

`SoundingFormationLab.tsx` already exposes these values, but currently gives too many inputs equal visual priority and mixes upstream timing-window controls into the same panel.

Next version should:

- make **one retained detection -> one reconstructed 3-D sounding** the dominant experience;
- use progressive disclosure rather than showing TWTT, beam angle, vessel XYZ, attitude, lever arm, sound speed, ping index and RX window simultaneously;
- make the frame/transform chain visible instead of relying mostly on numeric cards;
- show the sonar origin, VRP, lever-arm vector, body frame and navigation frame explicitly;
- replace the current decorative beam rotation with Scientific-Core-derived direction vectors;
- move RX start/end controls out of the primary interaction; retain only association/provenance metadata needed to explain the selected detection;
- add a deliberate **wrong pose epoch / stale state** diagnostic using D13 outputs rather than local timing arithmetic;
- later replace the constant-`c` reconstruction with the registered D4 ray-tracing path for the advanced propagation-mismatch experiment;
- add mounting-orientation support when D10 Scientific Core provides it;
- add sector/TX-epoch provenance from D9 when the API supports it;
- keep Truth comparison optional/teaching-only;
- add a final vertical/spatial-reference step only after an authoritative datum/water-level transformation contract exists.

## Recognized references

- **International Hydrographic Organization (IHO), S-5A Edition 2.0.0, August 2026 — H2.4c/H2.4d Multibeam systems and multibeam data processing**: identifies positioning, motion/attitude, reference level and sound-speed measurements as system components; H2.4d explicitly requires combining beam/travel-time data, IMU/INS, positioning, time stamping, sensor offsets and sound-speed profile to produce georeferenced soundings: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **John E. Hughes Clarke (2017), “Multibeam Echosounders,” in *Submarine Geomorphology*** — slant ranges and angles define seabed elevation/geometry while achievable accuracy depends on position/orientation integration, bottom detection and the sound-speed field: <https://scholars.unh.edu/ccom/1370/>
- **NOAA Office of Coast Survey, Hydrographic Surveys Specifications and Deliverables, Version 2026.0.00, §5.6 Corrections** — requires accurate 3-D positioning and identifies installation offsets/alignment, draft/dynamic draft, sound speed, attitude and datum corrections as contributors to corrected hydrographic points: <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf>
- **Kongsberg Maritime, EM multibeam output datagram format, document 160692** — architecture-specific evidence that operational sounding data carry depth, across-track/along-track distance, beam angles and one-way travel-time/range information, with heave/roll/pitch and sound-speed/ray-bending processing conventions explicitly documented: <https://www.kongsberg.com/globalassets/kongsberg-discovery/seafloor-mapping/em-multibeams/documents/160692_em_datagram_formats.pdf>
- **Christian de Moustier (2001), “Field Evaluation of Sounding Accuracy in Deep Water Multibeam Swath Bathymetry,” MTS/IEEE OCEANS** — demonstrates sensitivity of wide-swath sounding accuracy to motion-sensor integration and synchronization: <https://scholars.unh.edu/ccom/218/>
- **Brandon Maingot, John E. Hughes Clarke & Brian R. Calder (2019), “High Frequency Motion Residuals in Multibeam Data: Identification and Estimation”** — integration errors in orientation, space, sound speed or time generate systematic, predictable bathymetric residuals: <https://scholars.unh.edu/ccom/1683/>
