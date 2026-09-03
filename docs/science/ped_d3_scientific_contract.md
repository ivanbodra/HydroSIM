# PED-D3 Scientific Contract — Sonar Equation & Propagation Loss

Status: implementation-ready scientific binding for the pedagogical generation.

## Purpose

`PED-D3` answers the learning question:

> How do source level, propagation loss, seabed area backscatter, beam-pattern response, and noise combine to determine received echo level and SNR, and why do range and frequency change the result?

This document does **not** define new sonar physics. It binds the pedagogical-generation identifier `PED-D3` to the already implemented and reviewed canonical contract in `docs/science/sonar_equation_v0_1_contract.md`.

## Canonical model

The scientific source of truth is `docs/science/sonar_equation_v0_1_contract.md` and its referenced Core implementation. The learner-facing experience shall consume the canonical outputs rather than reproduce equations in presentation code.

The level-domain reference chain is:

`RL = SL + G_tx - TL_out + BS - TL_in + G_rx`

and

`SNR = RL - NL`.

For reciprocal equal paths only, `TL_2w = 2 TL_1w`.

One-way propagation loss remains the canonical combination of spherical spreading and absorption. Frequency-dependent seawater absorption uses the already selected Ainslie & McColm (1998) formulation and its documented validity domain.

## State semantics

For the first PED-D3 experience:

- learner-set source level, frequency, range, noise level, and any exposed environmental/reference inputs are **Configured**;
- transmission-loss components, absorption coefficient, received level, SNR, and plotted curves are **Derived**;
- explicit fixed environmental defaults are **Configured**, never Observed;
- the lesson creates no Observed or Estimated state and does not claim environmental Truth.

## Required learner-visible scientific behavior

The experience shall make the following cause→effect relations observable using canonical Core outputs:

1. Increasing range with all other inputs fixed reduces received level because propagation loss increases.
2. Increasing frequency can increase seawater absorption under the configured environment; the resulting effect shall come from the canonical absorption model rather than a UI heuristic.
3. Increasing source level by `Δ dB` increases received level and SNR by the same `Δ dB` when all other terms are fixed.
4. Increasing equivalent receiver noise level by `Δ dB` reduces SNR by `Δ dB` while leaving received echo level unchanged.
5. The contribution breakdown must keep source/backscatter/relative beam terms distinct from outbound and inbound propagation losses.
6. SNR is a level-domain margin (`RL - NL`), not a probability of detection and not a binary detection result.

## First learner slice

The smallest coherent PED-D3 slice should expose only controls needed to demonstrate the contract clearly. Recommended primary controls are frequency, range, source level, and noise level. Temperature, salinity, pH, representative depth, backscatter strength/area, and beam corrections may remain explicit configured context/defaults until exposing them improves the active learning question.

At minimum, learner-visible outputs should support:

- received level versus range;
- SNR versus range;
- frequency-dependent absorption or a directly related loss comparison;
- a compact contribution breakdown sufficient to explain why the result changed.

## Scientific boundaries

PED-D3 must not silently expand into:

- detection probability or thresholding;
- sediment-class prediction of backscatter strength;
- reverberation;
- stochastic noise realization;
- calibrated TVR/receiver-voltage electronics;
- classical directivity index substituted for normalized relative beam response;
- uncertainty propagation;
- multipath or non-reciprocal propagation.

These require separate scientific contracts if later activated.

## Traceability and validation anchors

All equations, units, environmental validity limits, contribution fields, and implementation invariants remain authoritative in `docs/science/sonar_equation_v0_1_contract.md`.

Focused PED-D3 validation should preserve at least these anchors:

- `SNR = RL - NL` exactly;
- reciprocal equal-path `TL_2w = 2 TL_1w`;
- increasing path length must not increase RL with other inputs fixed;
- increasing absorption at fixed range must reduce RL;
- normalized boresight relative beam corrections are 0 dB;
- the canonical area-backscatter result is consumed, not rederived in the learner layer.

## References

See `docs/science/sonar_equation_v0_1_contract.md`, including Ainslie & McColm (1998), Francois & Garrison (1982), and Waite (2002).
