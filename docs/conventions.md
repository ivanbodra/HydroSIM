# HydroSIM Conventions

Version: 0.1.3

> These conventions define the internal geometric and temporal semantics of HydroSIM. External instrument or software conventions must be converted explicitly at system boundaries; they must not silently alter the internal convention.

## 1. Internal units

HydroSIM uses SI units internally unless a scientific model explicitly requires otherwise.

- Length: metre [m]
- Time: second [s]
- Velocity: metre per second [m/s]
- Acceleration: metre per second squared [m/s²]
- Angles: radians internally; user interfaces may display degrees
- Frequency: hertz [Hz]
- Sound speed: metre per second [m/s]
- Acoustic levels: decibels [dB], with the physical reference explicitly identified where required

## 2. Geodetic coordinates and CRS

Geodetic coordinates and local Cartesian coordinates are distinct concepts and must not be conflated.

When geographic/geodetic coordinates are used, HydroSIM represents them explicitly as:

- latitude
- longitude
- ellipsoidal height, where applicable

Ellipsoidal height is positive upward.

A CRS must be identified explicitly by its definition and axis directions. An EPSG code may identify a CRS, but the internal simulation frame is not inferred from an EPSG code alone.

For example, EPSG:4326 defines a two-dimensional geographic CRS and does not itself define the HydroSIM local NED frame or a vertical axis.

## 3. Local navigation frame (N)

The initial prototype uses a local right-handed North-East-Down navigation frame, identified by the symbol `N`:

- `X_N` = North
- `Y_N` = East
- `Z_N` = Down

Therefore:

`X_N × Y_N = Z_N`

Heading is measured clockwise from North:

- 0° = North
- 90° = East
- 180° = South
- 270° = West

Positive `Z_N` is downward.

## 4. Vessel / body frame (B)

The vessel frame is identified by the symbol `B` and is right-handed:

- `X_B` = Forward
- `Y_B` = Starboard
- `Z_B` = Down

Therefore:

`X_B × Y_B = Z_B`

The permanent origin of the body frame is the Vessel Reference Point (`VRP`). The VRP is a defined geometric reference point and is not assumed to coincide with the centre of gravity, GNSS antenna, IMU/MRU, transducer, waterline, or any other sensor unless explicitly configured.

Other sensors have their own frame origins. HydroSIM does not require these origins to be called reference points (`RP`). Terms such as transducer origin, IMU origin, and GNSS antenna origin may be used directly.

## 5. Sensor frames

Sensors may define their own local frames. Initial frame identifiers are:

- `B` = vessel/body frame
- `N` = local navigation frame
- `T` = transducer frame
- `I` = IMU/MRU frame
- `G` = GNSS antenna frame or antenna origin, where needed

Additional identifiers such as `T1` and `T2` may be used for dual-head systems.

No sensor frame is assumed to be perfectly aligned with the vessel frame.

## 6. Attitude conventions

HydroSIM uses the following positive attitude conventions in the vessel/body frame:

- Positive roll (`φ`): starboard side down
- Positive pitch (`θ`): bow up
- Positive yaw (`ψ`): turn to starboard; clockwise when viewed from above

With the right-handed Forward-Starboard-Down body frame and the active rotation matrices defined below, these signs are obtained directly from the standard right-hand elementary rotations about `+X_B`, `+Y_B`, and `+Z_B` respectively.

Heading and yaw share the same positive rotational sense in the NED convention, but they remain semantically distinct:

- heading describes vessel orientation relative to North;
- yaw is the rotational degree of freedom about the vertical/body `Z` axis.

## 7. Rotation representation and order

HydroSIM uses column vectors and explicitly defined active rotation matrices.

The conceptual Euler rotation sequence is:

`Roll → Pitch → Yaw`

with:

- `φ` = roll
- `θ` = pitch
- `ψ` = yaw / heading angle as applicable

The elementary active right-hand rotation matrices are:

`R_x(φ) = [[1, 0, 0], [0, cosφ, -sinφ], [0, sinφ, cosφ]]`

`R_y(θ) = [[cosθ, 0, sinθ], [0, 1, 0], [-sinθ, 0, cosθ]]`

`R_z(ψ) = [[cosψ, -sinψ, 0], [sinψ, cosψ, 0], [0, 0, 1]]`

For the Body-to-Navigation transformation, the composite direction-cosine matrix is:

`R_NB = R_z(ψ) R_y(θ) R_x(φ)`

A vector expressed in body coordinates is transformed to navigation coordinates by:

`v_N = R_NB v_B`

Because column vectors are used, the rightmost matrix acts first. Therefore the written product corresponds to the conceptual application order Roll, then Pitch, then Yaw.

The inverse transformation is:

`v_B = R_NB^T v_N`

because a valid rotation matrix is orthogonal:

`R_NB^-1 = R_NB^T`

No implementation may rely on a library's undocumented or default Euler-angle convention.

### Canonical rotation tests

The following cases are mandatory unit-test references.

1. **Zero attitude / heading 0°**
   - input body forward vector: `[1, 0, 0]_B`
   - expected navigation vector: `[1, 0, 0]_N`
   - interpretation: Forward maps to North.

2. **Heading / yaw +90°**
   - input body forward vector: `[1, 0, 0]_B`
   - apply `R_z(+90°)`
   - expected navigation vector: `[0, 1, 0]_N`
   - interpretation: Forward maps to East.

3. **Roll +90°**
   - input body starboard vector: `[0, 1, 0]_B`
   - apply `R_x(+90°)`
   - expected rotated vector: `[0, 0, 1]`
   - interpretation: Starboard rotates toward Down.

4. **Pitch +90°**
   - input body forward vector: `[1, 0, 0]_B`
   - apply `R_y(+90°)`
   - expected rotated vector: `[0, 0, -1]`
   - interpretation: Forward rotates toward Up because positive Z is Down.

In addition to the physical cases above, every implemented rotation matrix must satisfy, within numerical tolerance:

- `R^T R = I`
- `R^-1 = R^T`
- `det(R) = +1`

These tests are normative for the HydroSIM geometry core.

## 8. Heave

Heave uses the hydrographic sign convention:

- Positive heave = upward vessel displacement
- Negative heave = downward vessel displacement

This is intentionally different from the sign of the `Z_N` and `Z_B` coordinates, which are positive downward.

Therefore, for a pure heave displacement:

`ΔZ = -heave`

Heave must never be treated as an alias for a Z coordinate.

## 9. Lever arms

A lever arm is a directed vector from a source reference point or frame origin to a target reference point or frame origin.

Naming convention:

`lever_arm_<source>_to_<target>`

Example:

`lever_arm_vrp_to_transducer`

Components are expressed in the source frame unless explicitly stated otherwise.

For a lever arm from the VRP to the transducer origin expressed in body coordinates:

`p_T^N = p_VRP^N + R_NB l_VRP_to_T^B`

Example interpretation in the body frame:

- `x > 0`: target is forward of the source
- `y > 0`: target is starboard of the source
- `z > 0`: target is below the source

## 10. Sensor alignment

Sensor mounting/alignment angles are fixed installation parameters and are separate from dynamic vessel attitude.

Examples:

- vessel roll = dynamic platform motion
- transducer roll alignment = fixed installation parameter
- IMU-to-vessel misalignment = fixed installation parameter

These values must never be stored as the same variable or silently combined.

Transformations must identify both the source and target frames.

## 11. Beam and transmit-sector angles

Beam and transmit-sector angular conventions are defined independently from the Cartesian signs of the vessel frame.

For a nominal downward-looking transducer:

- zero across-track receive angle corresponds to the nominal transducer normal in the across-track plane;
- positive across-track receive angle points to port;
- negative across-track receive angle points to starboard;
- zero along-track transmit tilt corresponds to the nominal transducer normal in the along-track plane;
- positive along-track transmit tilt points forward;
- negative along-track transmit tilt points aft.

The zero-angle direction is the transducer-frame normal, not necessarily geographic nadir. It coincides with `+Z_B` only when the transducer is perfectly aligned with the vessel frame and no steering is applied.

HydroSIM should preserve the distinction between receive-beam angle and transmit-sector tilt. A multibeam sounding may therefore reference both an `RxBeam` and a `TxSector` rather than storing a single undifferentiated beam angle.

These signs are chosen to remain compatible with common Kongsberg multibeam usage. External datagram conventions must still be validated explicitly when adapters are implemented.

## 12. Range, slant range, and travel time

HydroSIM distinguishes the following quantities:

- `range`: length of the actual acoustic propagation path between transducer and target along the ray trajectory;
- `slant_range`: straight-line Euclidean distance between transducer and target;
- `twtt`: two-way acoustic travel time.

For acoustic path `Γ`:

`range = ∫_Γ ds`

and:

`slant_range = ||p_target - p_transducer||`

In a homogeneous medium with a straight ray:

`range = slant_range`

With refraction, the acoustic path may be curved and normally:

`range >= slant_range`

For spatially varying sound speed:

`t_oneway = ∫_Γ ds / c(r)`

For the simplified reciprocal case in which the return follows the same path:

`twtt = 2 ∫_Γ ds / c(r)`

HydroSIM must not generally replace this relationship with `range = c * twtt / 2` unless the assumed constant or effective sound speed and propagation model make that approximation valid.

## 13. Time and multi-sensor synchronization

Time is a shared infrastructure across all HydroSIM sensors. Sensor streams may operate at different update rates, temporal resolutions, latencies, and clock characteristics.

Internal simulation time is expressed as seconds from the simulation epoch and is the deterministic master time used by the simulator.

UTC timestamps may additionally be stored when needed.

HydroSIM distinguishes at least:

- `measurement_time`: physical time to which a measurement refers;
- `timestamp`: time value encoded or reported by the sensor/system;
- `reception_time`: time at which the measurement becomes available to the collector;
- `use_time` or `processing_time`: time at which the measurement is used by acquisition or processing;
- `sample_rate` / `update_rate`: native rate of a sensor stream;
- `time_resolution`: temporal quantization/resolution of the reported time;
- `latency`: delay between the physical measurement and the availability/use of that information;
- `clock_bias` / `timestamp_error`: time-tag error, modelled separately from latency;
- `interpolation_method`: method used to obtain a sensor state at a requested time between samples.

HydroSIM defines positive latency as a delayed observation/state:

`state_used(t) = state_true(t - Δt)` for `Δt > 0`

Example:

- requested/ping time = 10.000 s
- latency = +0.100 s
- state available for use corresponds to 9.900 s

Different sensor streams must not be assumed to have identical timestamps or update rates. A ping references time; sensor states used for that ping are obtained from their independent streams by the explicitly configured temporal model.

The precise physical event represented by `ping_time` (for example transmission start or another transmit epoch) remains to be defined before acoustic ping implementation.

## 14. Vertical references and vessel geometry

Within NED and body frames, positive Z is downward.

HydroSIM distinguishes vessel geometry, transducer installation geometry, vessel motion, and hydrographic water-level correction.

### 14.1 Waterline relative to the VRP

`waterline` is a configured vertical reference relative to the vessel reference point (`VRP`). It may be entered or changed by the user during acquisition and may also be corrected or replaced during processing.

Because the configured waterline may change over time, HydroSIM must support waterline as a time-varying configured value or configuration-event history rather than assuming it is a single immutable session constant.

The sign and exact stored representation must be explicit in implementation. In the NED body geometry, vertical offsets follow positive-down convention.

The configured vessel waterline must be kept distinct from a geodetic or tidal `water_level` relative to a vertical datum. These are different concepts even when acquisition software uses similar user-facing terminology.

### 14.2 Transducer vertical position

The transducer vertical position relative to the VRP is defined by its lever arm. The vertical relationship between the transducer and the configured waterline follows from the VRP-to-transducer lever arm and the configured waterline.

HydroSIM should not require the user to recalculate a transducer vertical offset from fore/aft draft, trim, list, pitch, roll, or heave when those effects are already represented by vessel geometry or sensor/motion streams.

Manual incorporation of a motion or trim correction into a static installation value can create double counting when the same effect is subsequently applied from the MRU or processing chain. HydroSIM should be able to represent this as a configuration error in training scenarios.

### 14.3 Draft and vessel drawing

`draft` is retained primarily as a vessel-geometry and visualization quantity, for example to draw the hull relative to the configured waterline.

Optional `draft_fore` and `draft_aft` values may be used to represent the vessel geometry and static trim condition, but they are not the primary vertical reference for acoustic sounding calculations.

### 14.4 Motion and dynamic immersion

Roll, pitch, and heave are obtained from the motion model or MRU stream and remain distinct from static installation geometry.

`dynamic_draft` and `squat` are separate optional effects. They may alter the dynamic vertical position and, in more advanced models, may also produce a dynamic trim component. They must not be silently inferred from static draft values.

### 14.5 Hydrographic water level relative to datum

A hydrographic `water_level(t)` relative to a defined vertical datum is a separate environmental/processing quantity. It may originate from observations, zoning, models, or other sources and may be applied during acquisition or processing depending on the workflow.

`waterline` relative to the vessel VRP and `water_level` relative to a geodetic/hydrographic datum must never be treated as synonyms.

Depth, Z coordinate, elevation, ellipsoidal height, draft, waterline, water level, transducer vertical position, dynamic draft, squat, and heave are distinct quantities and must not be used interchangeably.

## 15. State categories

Relevant quantities must be semantically associated with one of the following categories:

- `Truth`: physical value used by the simulator
- `Observed`: value delivered by a simulated sensor
- `Configured`: value supplied to the processing/acquisition system
- `Estimated`: value inferred by a student or algorithm
- `Derived`: value calculated from other states

A state category is semantic, not a requirement to duplicate every field into five copies. Data structures should group values by state where appropriate.

## 16. Reproducibility

Every stochastic simulation must receive an explicit random seed.

A reproducible simulation must identify at least:

- scenario ID and version
- HydroSIM software version
- scientific model set and versions
- random seed
- configuration/event history

## 17. External conventions

HydroSIM uses the conventions defined in this document internally. Manufacturer, acquisition-software, processing-software, or survey-organization conventions may differ.

Adapters must explicitly convert external conventions into HydroSIM internal conventions.

Future mappings may include, as needed:

- Kongsberg
- HYPACK/HYSWEEP
- POS MV / Applanix
- CARIS
- NOAA workflows
- other hydrographic systems

No external convention may be assumed to match HydroSIM merely because it uses the terms roll, pitch, yaw, heave, X, Y, Z, range, waterline, or water level.

## 18. Reference and standards context

The initial conventions were selected for internal consistency and interoperability with common hydrographic practice, while keeping external conventions explicitly convertible.

Relevant references for later traceability include:

- NOAA Office of Coast Survey, Hydrographic Survey Specifications and Deliverables, Version 2026.0.02
- NOAA Office of Coast Survey Field Procedures Manual
- IHO S-44 and related hydrographic guidance
- ISO 19111 / OGC WKT coordinate-reference-system concepts
- EPSG Geodetic Parameter Dataset
- Kongsberg multibeam installation and datagram documentation
- manufacturer documentation for supported sonar and positioning systems

The NOAA HSSD is treated primarily as a survey-data specification. Detailed sensor-axis, beam-angle, Euler-angle, time-tag, and vertical-reference conventions must be verified against the relevant field-procedure or manufacturer documentation before external adapters are implemented.

## 19. Remaining items before Issue #1 is closed

The following internal conventions are now approved and documented:

- NED navigation frame and FSD vessel frame;
- `VRP` as the permanent vessel/body-frame origin;
- attitude signs, rotation matrices, and canonical rotation tests;
- heave sign;
- directed lever arms and sensor-frame origins;
- beam/sector angle convention;
- range, slant-range, and TWTT distinction;
- multi-sensor temporal model and positive-latency sign;
- separation of vessel waterline, hydrographic water level, transducer geometry, draft, motion, dynamic draft, and squat.

Before Issue #1 is closed, the remaining item is:

1. define the precise event represented by `ping_time` before acoustic ping implementation begins.
