# PED-D10 — Multisector MBES scientific contract

Status: authoritative minimum contract for the first pedagogical vertical slice  
Language: English (canonical)

## Purpose

PED-D10 teaches that a multisector MBES transmit event is composed of distinct transmit sectors with explicit geometry, identity and timing. It does not simulate a particular manufacturer.

This contract reuses `docs/science/sonar_system_geometry_contracts.md` and the canonical HydroSIM ping-time semantics. No parallel beam or propagation physics is introduced.

## Scientific state

Configured per sector:
- `sector_id` (stable within a configured system state);
- sector centre orientation / angular support in an explicit head/transducer frame;
- `frequency_hz` when the configured example uses sector-dependent frequency;
- `pulse_duration_s` when exposed;
- `sector_tx_delay_s`, defined relative to the ping transmit epoch;
- optional relative transmit-power setting only when explicitly represented as a configured relative quantity, not calibrated source level.

Derived:
- `sector_tx_time = tx_time + sector_tx_delay`;
- sector transmit order obtained from configured delays (ties represent simultaneous transmission, not an arbitrary order);
- sector wavelength `lambda = c / f` when sound speed and sector frequency are configured;
- geometric sector coverage and its union;
- footprint/swath geometry only through existing canonical geometry/footprint models.

`tx_time`, `trigger_time`, physical trigger-to-transmit delay and configured sector delay remain distinct timing concepts.

## Geometry and signs

Reuse canonical HydroSIM conventions: +X Forward, +Y Starboard, +Z Down. Across-track steering is zero at the nominal transducer normal, positive Port and negative Starboard. TX sectors remain distinct from RX beams. A sounding may reference both; PED-D10 must not collapse them into one generic beam angle.

Sector coverage may meet, overlap or contain gaps. Perfect tiling is not a physical invariant. Total configured transmit coverage is Derived from the sector set.

## Timing behavior

The authoritative relation is:

`sector_tx_time = tx_time + sector_tx_delay`

with seconds as the internal unit. `sector_tx_delay >= 0` for the first pedagogical slice. The learner-visible temporal sequence must be derived from these delays rather than hard-coded sector labels.

Changing sector delay changes transmit epoch/order but does not by itself change sector pointing geometry. Changing sector geometry does not by itself imply a timing change.

## Frequency and pulse duration

Sector frequency is a Configured acoustic parameter. If sectors use different frequencies, wavelength and any downstream frequency-dependent effects must be computed by existing canonical models; the UI must not invent frequency effects.

Pulse duration is Configured. PED-D10 may display the transmit interval `[sector_tx_time, sector_tx_time + pulse_duration]`. Pulse overlap in time is permitted by the generic contract and must not automatically be labelled invalid; manufacturer-specific scheduling constraints are outside this slice.

A relative power control, if retained, is Configured presentation/system state only unless connected to the canonical sonar-equation source-level model. It must not be converted into received level, SNR or detectability without that explicit scientific connection.

## First-slice analytical anchors

For `tx_time = 10.000 s` and delays `[0, 0.002, 0.005] s`, sector transmit epochs are `[10.000, 10.002, 10.005] s` and the order follows those epochs.

For equal delays, sectors are simultaneous for this model; stable `sector_id` may be used for display ordering but must not be interpreted as physical sequencing.

At fixed sound speed, doubling sector frequency halves wavelength. No claim about footprint, attenuation or detectability follows unless the corresponding canonical model is explicitly evaluated.

## Validity / fidelity boundary

Included: vendor-neutral sector identity, configured sector geometry, frequency, pulse duration and relative timing; derived sequence/epochs; composition of sector coverage; reuse of canonical footprint/swath models where already supported.

Excluded unless separately sourced and modelled: proprietary sector scheduling, adaptive sectorization, manufacturer power limits, calibrated source level per sector, frequency-dependent source response, dynamic swath optimization, receive-beam scheduling, seabed response and detection probability.

The lesson must not imply that all real multisector systems use different frequencies, delays or powers between sectors; these are configurable examples, not defining properties.

## State semantics

The learner controls above are `Configured`. Sector timing/ordering, wavelength and composed geometry are `Derived`. This first slice introduces no new `Observed`, `Estimated` or hidden `Truth` quantity.

## References / traceability

- `docs/science/sonar_system_geometry_contracts.md` — canonical multisector geometry and TX/RX distinction.
- HydroSIM canonical timing convention — `sector_tx_time = tx_time + sector_tx_delay`.
- `docs/pedagogy/hydrosim_pedagogical_plan.md` — PED-D10 learning intent.

Manufacturer-specific behavior requires a separate authoritative source before it can become canonical HydroSIM physics.
