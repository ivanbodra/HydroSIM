# D10 — Vessel & Sensor Configuration

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD ORIENTATION EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/VesselConfigurationLab.tsx`

## Purpose
Teach how a hydrographic platform becomes one integrated measurement system by expressing the positions and orientations of GNSS, IMU/MRU and sonar sensors in a **common vessel reference frame**. The learner must distinguish a physical installation from a mere change of reference, understand lever arms and mounting orientation, and keep vessel-frame vertical geometry separate from hydrographic water-level/datum quantities.

The lab is not a dimensional-control survey simulator. Its purpose is to make the geometry that a dimensional-control survey measures **visible and causally meaningful**.

## Dominant discovery

```text
physical vessel + sensor installation
  -> choose common vessel reference point/frame
  -> express each sensor centre as a lever arm from that reference
  -> express each sensor body's orientation relative to the vessel frame
  -> integrated system knows where each observation was made and how its axes are oriented
```

Two distinctions are central:

```text
MOVE A SENSOR physically
  -> sensor position / pairwise geometry changes

MOVE / REDEFINE THE VRP only
  -> coordinates and lever-arm numbers change
  -> physical sensor positions and pairwise separations do NOT change
```

and

```text
vessel-frame Z / waterline / static draft
  != hydrographic water level relative to datum
```

The lab succeeds when the learner can look at a vessel installation and explain why GNSS, IMU and sonar observations cannot be combined correctly until their origins and axes are related to one common vessel frame.

## Inputs

### Primary — guided progression
1. **Selected vessel reference point / VRP position** in the vessel body frame;
2. **GNSS antenna position / lever arm** relative to the physical vessel installation;
3. **IMU/MRU position / lever arm**;
4. **Sonar/transducer position / lever arm**;
5. **sensor mounting orientation** relative to the vessel frame — roll/pitch/yaw or an equivalent registered orientation representation, introduced after translational offsets are understood.

The UI should expose the project body-frame convention explicitly. Current HydroSIM convention is:

```text
+X Forward
+Y Starboard
+Z Down
```

### Secondary
- waterline Z relative to the selected vessel reference;
- static draft as vessel geometry;
- vessel envelope dimensions for spatial context only;
- hydrographic water level relative to datum, shown as a deliberately separate quantity;
- sensor/body-axis visibility toggle;
- pairwise sensor-distance readouts.

### Advanced / optional
- declared sensor measurement centre / phase-centre representation where the selected system model defines it;
- compare two valid VRP choices for the same rigid installation;
- uncertainty envelopes for measured offsets only when D17 integration is available.

Do **not** make timing/latency a D10 control; D13 owns timing. Do **not** make vessel motion a D10 control; D11 owns dynamic attitude/heave consequences.

## Expected outputs / visual response

Required synchronized views:

### A. Vessel plan / 3-D installation view
- vessel envelope for context;
- visible VRP/origin;
- GNSS antenna, IMU/MRU and sonar/transducer physical centres;
- vessel +X/+Y/+Z axes;
- lever-arm vectors from the selected VRP to each sensor;
- numeric X/Y/Z components with units;
- pairwise sensor separations or an equivalent invariant check.

Changing a **sensor installation position** must physically move that sensor in the common vessel view.

Changing **VRP only** must move the reference marker and change reported VRP→sensor lever arms, while the physical GNSS/IMU/sonar points remain fixed.

### B. Sensor-axis / mounting-orientation view
For each sensor that has orientation:
- vessel axes;
- sensor body axes;
- configured roll/pitch/yaw mounting offset or equivalent orientation parameters;
- clear visual difference between `sensor aligned with vessel` and `sensor physically misaligned / installed at an angle`.

This view establishes the geometry later consumed by D11/D14. It must not yet simulate motion artefacts in detail.

### C. Vertical-reference view
Show on one consistent vertical axis:
- selected VRP;
- physical waterline in the vessel frame;
- transducer vertical position;
- keel/reference-bottom position from static draft;
- transducer depth below waterline.

Show **hydrographic water level relative to datum in a separate visual lane/card**, not on the same body-frame Z axis unless an explicit datum-to-vessel transformation exists.

### D. Configuration snapshot
A concise machine-readable / tabular summary should preserve:
- selected frame convention;
- VRP definition;
- lever arms;
- mounting orientations;
- waterline/static-draft quantities;
- hydrographic water level as a separate quantity.

The summary is secondary evidence, not the main learning experience.

## Interaction contract

1. Start with a simple vessel and **three physical sensor points** already installed: GNSS, IMU/MRU and sonar. Show the vessel axes and one common VRP.
2. Move the **sonar physically** in X, Y, then Z. Its lever arm and common-frame position change together. The learner should predict the sign before moving the control.
3. Move GNSS and IMU in the same way. Emphasize that each sensor measures from a different physical centre unless co-located.
4. Now move **only the VRP**. Freeze the physical vessel/sensor points. Show all VRP→sensor lever-arm numbers changing while pairwise sensor distances remain unchanged. This is the key distinction between **reference change** and **installation change**.
5. Reset to a neutral/reference installation and introduce **sensor body axes**. Keep positions fixed.
6. Rotate one sensor's mounting orientation relative to the vessel frame. Show its body axes rotate while its measurement centre stays fixed. Do not yet turn this into a moving-vessel artefact; hand that consequence to D11/D14.
7. Deliberately create a sign/axis mistake (for example port/starboard or up/down) through a guided preset. Show the configured sensor appearing in the wrong physical place/orientation and ask the learner to diagnose the frame error.
8. Reveal the **vertical-reference view**. Change waterline Z and static draft and show the vessel-frame geometric consequences.
9. Change **hydrographic water level relative to datum**. Sensor positions, VRP, waterline-to-keel geometry and pairwise distances must remain unchanged. The learner should see that datum/water-level information is not a lever arm.
10. Final comparison: show two configuration records that describe the **same physical installation using different VRP choices**. The learner should identify them as geometrically equivalent after transformation.

## Operational intuition / trade-offs

| Configuration / condition | What it enables | Error / risk to retain |
|---|---|---|
| Common vessel frame | combines measurements from physically separated sensors coherently | wrong axis/sign convention corrupts every downstream transform |
| Accurate lever arms | moves GNSS/IMU/sonar observations to a common reference geometry | offset error becomes a systematic spatial error and interacts with motion later |
| Accurate mounting orientation | relates sensor body measurements to vessel axes | angular misalignment can cross-couple axes and create bathymetric artefacts |
| Convenient VRP choice | simplifies configuration and integration | changing VRP is not a physical sensor movement; double-applying offsets is a serious risk |
| Co-located / short lever arms where practical | reduces some motion-coupled displacement sensitivity | installation choice is constrained by vessel, sensor environment and system requirements; shortest lever arm is not universally the only criterion |
| Correct waterline / static-draft geometry | relates transducer and hull vertical references | static geometry must not be confused with heave, dynamic draft, squat or datum water level |
| Hydrographic water level | later relates observations to a vertical datum | it must not move sensors in the vessel body frame |

Desired operator intuition: **“before combining hydrographic sensors, I must know where each measurement centre is and how each sensor's axes are oriented in one common vessel frame. A reference-point change changes coordinates; an installation change changes the physical geometry.”**

## Scientific guardrails

- D10 owns **static installation geometry and reference-frame integration**. D11 owns vessel motion; D13 owns time synchronization/latency; D14 owns full sounding formation; D17 owns formal uncertainty.
- Preserve the exact project frame/sign convention. Do not import a manufacturer's X/Y/Z convention silently; vendors differ.
- A lever arm is a directed vector between defined reference/measurement centres, not merely a positive distance.
- Distinguish **physical sensor centre / phase centre / manufacturer-defined reference point** whenever a specific sensor model requires it. Do not assume all devices use their geometric centre.
- Moving/redefining the VRP must not move the rigid physical installation. Pairwise distances among sensors are invariants under a pure reference translation.
- A sensor mounting-angle correction is not the same as vessel attitude. D10 configures the rigid angular relationship; D11 applies time-varying vessel motion.
- Do not teach that placing the IMU at the vessel centre of gravity is universally mandatory. IHO requires selecting/justifying the location based on vessel design/configuration, and real installations balance lever arms, dynamics and practical constraints.
- Keep `waterline_z_from_vrp_m` / static draft as vessel-frame geometry separate from `water_level_m_relative_to_datum`. Without a defined datum-to-vessel relationship, they cannot be collapsed onto one coordinate axis.
- Vessel envelope length/beam/height are contextual graphics unless a downstream physical model explicitly consumes them. Do not imply hydrostatic behaviour from the current envelope controls.
- Dimensional-control measurements and installation surveys have uncertainty; D10 may acknowledge this, but formal propagation belongs to D17.

## Dependencies / concepts passed forward

Consumes:
- project coordinate/frame conventions;
- D5 distinction between physical transducer/array geometry and installation context;
- D9 sector/transducer identity where relevant.

Passes forward:
- rigid vessel/sensor geometry to D11 Vessel Motion;
- GNSS/IMU/sonar centres and axes to D12 PU & Sensor Integration;
- sensor positions/orientations to D13 timing/latency interpretation where motion couples with delay;
- common-frame positions/orientations to D14 Sounding Formation;
- lever-arm / mounting-alignment uncertainty sources to D17 TPU.

## Current implementation delta

`VesselConfigurationLab.tsx` plus `vessel_api.py` already provide a strong static-geometry slice:
- editable vessel envelope dimensions;
- selected VRP position;
- editable GNSS, IMU and transducer installation positions;
- canonical `+X Forward, +Y Starboard, +Z Down` frame;
- core-derived VRP→sensor lever arms;
- plan-view sensor positions;
- waterline, static draft, keel and transducer-depth relationships;
- hydrographic water level carried separately;
- reset and configuration export;
- a correct **VRP reference-change invariant**: changing VRP changes transformed lever arms while physical sensor positions remain fixed.

Next-version changes:
- make **physical sensor installation vs VRP reference change** the dominant first experience instead of presenting all sliders with equal pedagogical weight;
- reduce vessel length/beam/height to secondary/context controls;
- draw explicit lever-arm vectors and pairwise sensor invariants;
- add **sensor mounting orientation / body axes** through the Scientific Core/API rather than React-only geometry;
- add an aligned ↔ misaligned sensor-orientation experiment without duplicating D11 motion artefacts;
- add a guided axis/sign-error preset for diagnosis;
- visually separate hydrographic water level from body-frame Z geometry more strongly;
- preserve the current authoritative API behavior where VRP translation does not move the physical sensors;
- preserve the deferred Survey Simulator configuration intent recorded in issue #345 as reusable design memory, but do not revive its deleted legacy module wholesale.

## Recognized references

- **IHO S-5A Ed. 2.0.0, H1.1a — Common reference frames for sensors**: common vessel reference point/frame, centres of measurement, sensor offset and alignment measurements; learning outcomes include configuring/reconciling offsets and conducting a vessel sensor-offset survey: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO S-5A Ed. 2.0.0, H1.1b — Integration of reference frames**: sensor body frames and transformations among sensor, vessel and local geodetic frames; identify bathymetric artefacts caused by integration errors: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO S-5A Ed. 2.0.0, H1.3b / H1.4a**: IMU static alignment/location and the effect of transducer location/orientation on sounding determination: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **NOAA Field Procedures Manual, §1.4 Vessel / §1.4.1 Vessel Static Offsets**: static offsets establish a local vessel reference frame; errors translate directly into survey data; documents sonar, GNSS and IMU measurement/reference centres and differing vendor conventions: <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf>
- **IHO International Hydrographic Review 31(2), Survey Systems Verification and Calibration (2025)**: dimensional control, sensor lever arms, SRF alignment and consequences of angular misalignment/cross-coupling: <https://ihr.iho.int/wp-content/uploads/2025/12/IHR-31-2.pdf>
- **Kongsberg EM 2040 MKII Installation Manual**: real-system dimensional-survey example requiring vessel coordinate system/origin, waterline, physical sensor locations, installation angles and transducer orientation to be measured and entered as installation parameters: <https://www.kongsberg.com/globalassets/kongsberg-discovery/commerce/seafloor-mapping/em2040-mkii/472405ab_em2040mk2_installation_manual_en.pdf>
