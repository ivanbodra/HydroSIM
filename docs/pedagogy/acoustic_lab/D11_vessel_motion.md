# D11 — Vessel Motion

Status: **Mapped**

**Decision:** `KEEP + REFINE + CONNECT TO SCIENTIFIC CORE`

**Current production/concept surface:** `web/pedagogical-explorer/src/MotionLab.tsx`  
**Existing Scientific-Core adapter:** `src/hydrosim/app/motion_lesson.py`

## Purpose

Build physical intuition for how **actual vessel motion changes sonar position, orientation, insonification geometry and the instantaneous location of a sounding**, and why hydrographic systems must measure and compensate/stabilize that motion.

D11 is about **real dynamic vessel motion**, not static installation misalignment. The learner must distinguish:

- the vessel actually moving;
- the motion sensor measuring that state;
- real-time acoustic stabilization that may steer TX/RX geometry to oppose part of the motion;
- downstream geometric motion compensation that uses measured position/attitude/heave when forming soundings.

Static roll/pitch/yaw installation offsets and patch-test calibration are not the core lesson here; timing/latency errors belong to D13.

**Dominant discovery**

```text
vessel motion
  -> sonar position and/or orientation changes
  -> beam / swath geometry moves in Earth/navigation frame
  -> uncompensated bottom locations move with the vessel
  -> measured motion enables stabilization and/or geometric compensation
  -> corrected sounding geometry should remain tied to the seafloor, not to the moving vessel
```

The lab succeeds when the learner can isolate roll, pitch, yaw and heave, predict the geometric consequence before moving the control, and explain why compensation is necessary without confusing motion with calibration error.

## Inputs

### Primary — guided single-DOF experiments

- **roll** `φ`;
- **pitch** `θ`;
- **yaw / heading deviation** `ψ`;
- **heave** `h`;
- compensation/stabilization mode: begin with **Off / Ideal** comparison rather than a wall of subsystem switches.

Use instantaneous values first. The existing Scientific Core already supports deterministic roll, pitch, yaw deviation and heave controls and derives VRP/transducer position, vessel axes and beam direction from them.

### Secondary / advanced

Only after the instantaneous geometry is understood:

- sinusoidal motion amplitude and period for one selected DOF;
- combined motion preset such as calm / moderate sea state, provided it is explicitly pedagogical rather than a claimed vessel-response model;
- real-time beam stabilization components when supported by the integrated core: RX roll stabilization and TX pitch/yaw stabilization as architecture examples;
- lever arm to transducer as a visible dependency from D10, preferably fixed by default;
- heading/mean trajectory only when needed to show Earth-frame geometry.

Do **not** make motion-sensor noise, latency, bias, alignment error or TPU primary D11 controls. Those belong downstream.

## Outputs / visual response

Required synchronized views:

### A. Vessel / reference-frame view

- neutral/baseline vessel ghost;
- current vessel pose;
- explicit vessel forward, starboard and down/up axes;
- VRP and transducer location;
- selected rotation axis or heave direction;
- numerical motion value with units and sign convention.

### B. Acoustic geometry view

Derived from the same Scientific Core state:

- transducer position in navigation/Earth frame;
- current beam or representative swath direction;
- baseline beam/swath ghost;
- seafloor intersection or simplified bottom reference where the registered geometry supports it;
- visible distinction between **vessel motion** and **beam stabilization**.

### C. Sounding-consequence view

For an idealized fixed seabed:

- uncompensated/raw geometric consequence;
- ideal motion-compensated consequence on the same scale;
- current versus baseline sounding/footprint locations;
- a short causal readout naming which motion component created the change.

For heave, explicitly show vertical transducer displacement. For rotations with non-zero lever arms, allow the transducer itself to move as rigid-body geometry dictates rather than rotating a decorative vessel around an arbitrary screen point.

### Recommended temporal view

After the single-state experiments, show one selected motion component versus time together with the corresponding uncompensated geometric response. Keep this deterministic and simple; D11 does not need a sea-state or vessel-response solver.

## Interaction sequence

1. **Neutral baseline.** Show vessel, VRP, transducer, body axes, beam/swath and fixed seabed. Establish that motion is zero and baseline/current coincide.
2. **Heave only.** Move the vessel vertically. The transducer translates vertically without an attitude change. Show how an uncompensated range/depth geometry would move with the platform, then show ideal heave compensation restoring the seabed relation.
3. **Roll only.** Rotate about the vessel longitudinal axis. Show the swath/receive geometry rotating across-track and emphasize the growing spatial consequence away from nadir. If ideal RX roll stabilization is enabled, show steering opposing the vessel rotation rather than pretending the vessel stopped rolling.
4. **Pitch only.** Rotate about the transverse axis. Show fore-aft change in sonar/transmit geometry and, where the architecture supports it, ideal TX pitch stabilization opposing that component.
5. **Yaw only.** Rotate around the vertical axis / change heading. Show the horizontal orientation of the acoustic geometry moving relative to the seafloor/track. Where the architecture supports it, show sector/TX yaw stabilization as a distinct acoustic action.
6. **Lever-arm consequence.** Reuse one non-zero D10 lever arm and repeat a rotation. The learner should see that rotation can translate a sensor that is not located at the rotation/reference point. Do not turn this into another vessel-configuration lesson.
7. **Compensation comparison.** On the same physical scene, compare `motion present + compensation off` with `motion present + ideal compensation/stabilization`. The vessel continues to move in both cases; only the measurement/acoustic geometry is corrected.
8. **Simple dynamic motion.** Animate one DOF sinusoidally and let the learner follow vessel state -> beam/swath response -> sounding consequence continuously. Combined motion follows only after each DOF is understood independently.

## Operational intuition / trade-offs

| Motion / treatment | Observable consequence | Operational intuition |
|---|---|---|
| Heave | sonar/VRP moves vertically | vertical platform motion must be accounted for in sounding geometry; delayed/advanced heave processing may improve estimates but timing treatment belongs to D13 |
| Roll | swath/beam geometry rotates across-track; outer-beam displacement is especially sensitive | accurate roll measurement and/or RX roll stabilization are critical for wide-swath mapping |
| Pitch | acoustic geometry rotates fore/aft and a non-zero lever arm can move the transducer | pitch compensation/stabilization preserves intended along-track geometry |
| Yaw / heading change | swath/sector orientation rotates horizontally relative to track/seafloor | heading/motion information and, on systems that support it, TX yaw stabilization help preserve intended coverage geometry |
| Larger motion amplitude | larger uncompensated geometric displacement | rougher motion increases reliance on correct motion sensing, rigid-body geometry and stabilization/compensation |
| Active stabilization | keeps acoustic look directions closer to desired Earth/seafloor geometry | stabilization changes beam steering, not the vessel's physical motion |
| Geometric motion compensation | reconstructs sounding geometry using measured vessel state | it corrects the coordinate solution; it is not the same operation as actively steering the acoustic beam |

Desired operator intuition: **“The vessel can move substantially while the desired seabed geometry remains stable only because the system knows the platform state and applies that information correctly. Stabilizing the beam and compensating the sounding are related but different operations.”**

## Scientific guardrails

- Preserve the project's registered coordinate frames, rotation order, angle signs and `positive heave = Up` convention from the Scientific Core. Do not infer them from screen animation.
- Keep **dynamic motion** distinct from **static installation offsets**. A persistent roll/pitch/yaw misalignment is a D10/calibration problem, not vessel motion.
- Keep Truth/Observed/Configured semantics explicit. D11 may use ideal observed motion equal to Truth for the main experiment; sensor errors belong to D12/D17 and timing mismatch to D13.
- Roll, pitch and yaw rotations must use the rigid-body transform owned by the Scientific Core. Do not approximate them as CSS `rotate/skew/x` effects for scientific geometry.
- A non-zero lever arm means angular motion can move the transducer position as well as change its orientation. Preserve this consequence from D10.
- Do not teach that all MBES architectures stabilize all axes in the same way. Modern Kongsberg examples use TX stabilization for pitch/yaw and RX stabilization for roll, but this is architecture evidence, not a universal rule.
- Active stabilization does not eliminate the need to record attitude/heave/heading and use them in final sounding reconstruction.
- Do not double-apply motion correction. If an acoustic direction was stabilized during acquisition, downstream processing must use the system's actual recorded/defined geometry rather than applying an invented second steering correction.
- Heave is reference-point dependent when sensors are separated by lever arms and vessel rotation is present. Remote-heave/monitoring-point treatment must follow the registered geometry; do not translate one heave value naively to every sensor.
- Motion latency, timestamp synchronization and interpolation are D13. Formal motion uncertainty belongs to D17.
- Patch test, static angular mounting offsets and alignment calibration are outside the core D11 interaction even though their data signatures can resemble motion artifacts.

## Dependencies / forward reuse

Consumes:
- D6 beam steering/stabilization intuition;
- D7 beam/swath and seafloor-footprint geometry;
- D9 sector-specific TX geometry where yaw/pitch stabilization is demonstrated;
- D10 VRP, sensor position, lever arms and vessel/sensor frames.

Passes forward:
- time-varying platform pose and transducer geometry to D12 PU & Sensor Integration;
- motion timestamps and dynamic-state synchronization requirements to D13;
- corrected platform/beam state to D14 Sounding Formation;
- motion/sea-state implications for coverage efficiency to D15/D16;
- attitude/heave uncertainty contributions to D17 TPU.

## Current implementation delta

`src/hydrosim/app/motion_lesson.py` is already a useful authoritative first slice. It sends configured instantaneous roll, pitch, yaw deviation and heave through the existing `VesselMotionModel`, then derives transducer position, vessel axes and beam direction using the existing rigid-body transforms. Preserve and extend this path rather than creating frontend motion physics.

`web/pedagogical-explorer/src/MotionLab.tsx` currently provides strong visual affordances — baseline ghost, direct manipulation, individual roll/pitch/yaw/heave focus and a sounding-impact view — but its scientific geometry is still explicitly conceptual. Its CSS/animation mapping (`rotate`, `x`, `y`, `skewX`) and synthetic sounding trail must not become the scientific model.

Next version must:

- consume the Python motion snapshot/API for vessel axes, transducer position and beam direction;
- make heave units physical (`m`) rather than `rel.`;
- show VRP/transducer and vessel axes explicitly;
- isolate each DOF before combined motion;
- replace decorative beam/sounding displacement with core-derived geometry;
- add uncompensated versus ideal-compensated comparison on the same fixed scale;
- distinguish **beam stabilization** from **sounding motion compensation**;
- reuse the D10 lever arm so rotational motion visibly translates an offset transducer;
- add a simple deterministic time-varying motion experiment only after the instantaneous slice is correct;
- keep sensor noise, latency, misalignment and TPU out of the primary D11 controls.

## Recognized references

- **IHO S-5A Ed. 2.0.0 (Aug 2026)** — hydrographic positioning/attitude, integrated survey-system geometry and swath-system competence; use as the curriculum/competence authority: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO International Hydrographic Review (2025), “Survey systems verification and calibration in the hydrospatial domain”** — describes six-DOF IMU motion, vessel/SRF alignment, lever-arm effects and motion compensation context: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- **NOAA Hydrographic Surveys Specifications and Deliverables 2026** — identifies heave, roll and pitch among the uncertainty/correction components of hydrographic sounding measurement: <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf>
- **NOAA Field Procedures Manual, motion/remote-heave processing guidance** — documents vertical transducer displacement caused by roll/pitch acting over non-zero moment arms and cautions against double-applying roll/pitch when acquisition steering already compensated them: <https://www.nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/2014-fpm-final.pdf>
- **Kongsberg EM 304 MKII / EM 124 / EM 712 current product documentation** — real-system examples of TX yaw/pitch stabilization and RX roll stabilization; architecture evidence, not universal law: <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em304-mkii/> ; <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em124/> ; <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em712/>
- **Kongsberg MRU 5** — authoritative manufacturer evidence for roll, pitch, heave and motion-compensatory use in multibeam systems, including configurable monitoring points/lever arms: <https://www.kongsberg.com/what-we-do/ocean-space/inertial-solutions/mru/mru-5/>
- **Kongsberg Seapath 385** — real-system evidence for six-degree-of-freedom output and motion values at multiple monitoring points: <https://www.kongsberg.com/what-we-do/ocean-space/inertial-solutions/seapath/seapath-385/>
