# HydroSIM Module Identifier Policy

Status: canonical coordination policy

## Purpose

HydroSIM has two valid but different Didactic Explorer decompositions in its history:

1. the frozen v0.1.0 release inventory established through Issue #46 and used by Technical Lead completion tracking; and
2. the expanded pedagogical curriculum in `docs/pedagogy/hydrosim_pedagogical_plan.md`.

Both previously used bare `D<number>` identifiers. Because their sequences are not equivalent, bare identifiers such as `D7` and `D8` became ambiguous. This policy removes that ambiguity without rewriting historical Issues, PRs, commits, scientific contracts, or validation evidence.

## Canonical namespaces

From this policy forward, references MUST use a namespace when an identifier is needed:

- `V01-D1` ... `V01-D8` — frozen Didactic Explorer submodules from the v0.1.0 release inventory in Issue #46.
- `PED-D1` ... `PED-D18` — learning-sequence identifiers from `docs/pedagogy/hydrosim_pedagogical_plan.md`.

Do not create new bare `D<number>` references in Issues, handoffs, scientific contracts, implementation identifiers, or coordination documents.

Semantic names remain mandatory where practical. An identifier never replaces the submodule name.

## v0.1.0 release inventory

The Technical Lead completion indicator defined by Issues #28/#46 remains frozen for v0.1.0:

| Canonical ID | Submodule |
|---|---|
| `V01-D1` | Signal |
| `V01-D2` | Beam Pattern |
| `V01-D3` | Sonar Equation / Acoustic Losses |
| `V01-D4` | Sound Velocity & Refraction |
| `V01-D5` | Vessel / Sensors / Vertical References |
| `V01-D6` | Motion |
| `V01-D7` | Sonar Systems & Geometry |
| `V01-D8` | Sounding Formation / Detection Chain |

This namespace is a release-tracking taxonomy. It is not a claim that the expanded pedagogical curriculum must contain exactly eight learning experiences.

## Expanded pedagogical curriculum

Identifiers in `docs/pedagogy/hydrosim_pedagogical_plan.md` are interpreted canonically as `PED-D1` ... `PED-D18` even where the table still displays the shorter `D1` ... `D18` notation.

Important collision examples:

- pedagogical-plan `D7` = `PED-D7` Beamforming & Electronic Steering;
- pedagogical-plan `D8` = `PED-D8` Echosounders — SBES vs MBES;
- pedagogical-plan `D15` = `PED-D15` Sounding Formation.

These are distinct from historical/integrated `V01-D7` Sonar Systems & Geometry and `V01-D8` Sounding Formation / Detection Chain.

The pedagogical curriculum may decompose one v0.1.0 release submodule into several learning experiences. Therefore no forced one-to-one numerical mapping between `V01-D*` and `PED-D*` is implied.

## Historical references

Existing bare identifiers are preserved as historical aliases; they must not be mass-renamed because that would damage traceability.

Interpretation rule:

- references tied to Issue #46, v0.1.0 completion tracking, pre-policy scientific contracts, PR #104, PR #106, and their associated QA handoffs retain their original v0.1.0 meaning;
- references inside the expanded pedagogical plan introduced in commit `ae653473acad478e2cb0bdba2da4b0b5a2e8dc33` refer to the pedagogical sequence;
- new cross-references to historical material should write both namespace and semantic name, for example `V01-D7 Sonar Systems & Geometry`.

## Scientific and implementation references

Scientific contracts should primarily be identified by semantic contract/file name. When a module identifier is included for traceability, use the appropriate namespaced form.

Examples:

- `V01-D7 Sonar Systems & Geometry` → `docs/science/sonar_system_geometry_contracts.md`;
- `V01-D8 Sounding Formation / Detection Chain` → `docs/science/d8_observation_state_contract.md`;
- a future Beamforming contract serving the expanded curriculum should be referenced as `PED-D7 Beamforming & Electronic Steering`, not bare `D7`.

Implementation code does not need renaming solely for this policy. Rename only when an actively modified identifier would otherwise remain ambiguous.

## Progress accounting

Until HydroSIM v0.1.0 is released, the mandatory Technical Lead progress denominator remains the eight `V01-D*` submodules from #46. Expansion of the pedagogical curriculum to `PED-D1` ... `PED-D18` does not retroactively change the v0.1.0 denominator and must not reduce or inflate recorded v0.1.0 completion.

After v0.1.0, a new milestone may explicitly adopt a different denominator based on the expanded pedagogical curriculum.
