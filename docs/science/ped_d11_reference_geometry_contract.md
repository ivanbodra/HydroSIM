# PED-D11 Scientific Contract — Vessel Dimensions and Reference Geometry

Status: authoritative pedagogical-generation contract  
Experience: `PED-D11`  
Scope: minimum vessel-dimensions/reference-point semantics needed by the production learner slice

## Purpose

PED-D11 teaches that sensor installation coordinates are meaningful only relative to a declared vessel-fixed reference point. This contract extends the existing canonical VRP-relative lever-arm model without changing its frame or vertical-reference physics.

## Canonical frame

Use HydroSIM body frame `B`: `+X` Forward, `+Y` Starboard, `+Z` Down. All positions and lever arms below are metres in `B` unless explicitly transformed.

The **Vessel Reference Point (VRP)** remains the computational origin used by the existing vessel geometry Core. It is a configured reference, not a physical sensor and not automatically the centre of gravity, centre of rotation, waterline, keel, GNSS antenna, IMU or transducer.

## Vessel dimensions

The minimum PED-D11 learner model exposes three positive configured geometric envelope dimensions:

- `vessel_length_m` — fore-aft extent used by the learner vessel representation;
- `vessel_beam_m` — port-starboard extent;
- `vessel_height_m` — vertical extent used by the learner vessel representation.

These are **Configured geometric envelope dimensions** for the didactic vessel, not inferred hydrostatic particulars. In particular, `vessel_height_m` must not be relabelled as moulded depth, draft or freeboard. Static draft and waterline remain the existing separate canonical quantities.

The dimensions do not alter sensor lever arms, acoustic propagation, attitude, draft or water level by themselves. Their first-slice scientific role is to provide a scale/context envelope in which the VRP and sensors can be located.

## Reference-point semantics

PED-D11-I02 means the learner-configurable **location of the VRP relative to the vessel geometric envelope**, expressed as a configured vector

`r_center_to_vrp^B = [x, y, z]` [m],

where `center` is the geometric centre of the configured didactic envelope. The envelope centre is only a visualization/geometric datum; it is not a navigation or hydrographic state.

The default may be `[0, 0, 0]`. The learner may move the VRP within the configured envelope. Named alternatives such as CRP/COG must not be introduced unless separately defined; PED-D11 needs only one explicit VRP with a configurable position.

## Lever-arm invariant when the VRP changes

Canonical sensor lever arms retain source→target semantics:

`l_vrp_to_sensor^B = r_sensor^B - r_vrp^B`.

Changing the chosen VRP location is a **change of reference**, not physical motion of installed sensors. Therefore the physical sensor positions relative to the vessel envelope must remain invariant.

If the VRP is translated by `Delta r^B`,

`r_vrp,new^B = r_vrp,old^B + Delta r^B`,

then every existing VRP→sensor lever arm must transform as

`l_vrp_to_sensor,new^B = l_vrp_to_sensor,old^B - Delta r^B`.

Thus

`r_sensor^B = r_vrp^B + l_vrp_to_sensor^B`

is invariant for GNSS, IMU, transducer and any other rigidly installed sensor. Reinterpreting unchanged numerical lever arms after moving the VRP would instead move the sensors physically and is not the PED-D11 reference-change operation.

Waterline position expressed relative to VRP is likewise a coordinate relative to the chosen reference. If the VRP Z coordinate changes while the physical waterline is to remain fixed relative to the vessel, its VRP-relative Z value must be transformed consistently. Hydrographic `water_level_m_relative_to_datum` is a separate quantity and is not changed by a vessel-frame reference translation.

## State semantics

Configured:
- vessel envelope dimensions;
- VRP position relative to envelope centre;
- physical installation geometry represented through VRP-relative lever arms;
- waterline/static-draft configuration already owned by the existing Core.

Derived:
- sensor positions in the selected common vessel frame;
- transformed lever arms after a pure reference-point change;
- geometric relationships displayed between envelope, VRP, sensors, waterline and keel.

No Observed, Estimated or environmental Truth state is created by this contract.

## Acceptance anchors

1. Moving VRP by `[1,0,0] m` while preserving installation must subtract `[1,0,0] m` from every VRP→sensor lever arm.
2. `r_vrp + l_vrp_to_sensor` must be unchanged before/after a pure VRP reference translation.
3. A common VRP translation must not change pairwise sensor separations, e.g. `r_transducer - r_imu`.
4. Changing only vessel envelope dimensions must not change canonical sensor coordinates or vertical-reference quantities.
5. Changing VRP reference must not change hydrographic water level relative to datum.

## Fidelity boundary

This first slice is rigid-body installation geometry. It does not model hull form, centre of gravity, centre of flotation, dynamic draft/squat, structural flexure, sensor motion relative to the hull, or hydrostatics. The configured envelope is pedagogical spatial context, not a naval-architecture hull model.

## Traceability

This contract reuses:
- canonical HydroSIM body-frame and source→target lever-arm conventions;
- `VesselVerticalReferenceConfiguration` and its VRP-relative GNSS/IMU/transducer geometry;
- `docs/science/sonar_system_geometry_contracts.md` for common-reference rigid installation semantics.

No new acoustic or motion equation is introduced.