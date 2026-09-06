# HydroSIM limbo-code harvest inventory

Status date: 2026-09-06

Purpose: prevent loss of useful implementation while reducing stale branch sprawl. Effect-level disposition takes precedence over raw Git ancestry because HydroSIM commonly uses squash merges.

## HARVESTED TO `main`

### `ux/ped-d8-synchronized-comparison` — old PR #227
Unique still-useful effect: synchronized SBES × MBES learner comparison from the same canonical API response.

Recovered through PR #320 without restoring the stale historical file wholesale; newer D8 footprint-field behavior was preserved.

Harvest source commit: `dcc9a4c48489c8e73a9c2be570a96f8091420280`.
PR #320 merged to `main` as `1080aa709df529155c168d678d8afc832ec7444d` after `tests` and `pedagogical-frontend` passed.

Cleanup-ready now:
- `ux/ped-d8-synchronized-comparison`
- `integration/limbo-harvest`

## PRESERVE SOURCE — DO NOT DELETE

### `software-engineering/pitch-patch-test-adapter` — PR #89
Head: `93000aa207b1e953b53bcff2394c1d03e013937d`

Unique source:
- `src/hydrosim/scenarios/pitch_calibration.py`
- `tests/test_pitch_calibration_scenario.py`
- scenario exports

Disposition: SCIENTIFIC REVIEW via #321. Preserve until Scientific Lead classifies validity and identifies reusable algorithm/contracts/tests or confirms supersession.

### `ux/patch-roll-submodule` — PR #70
Head: `c1bd3284c57072a1412a8a65894cc1f46a5668ec`

Unique source:
- `src/hydrosim/app/patch_roll_lesson.py`
- `tests/test_patch_roll_lesson.py`

Disposition: PRESERVE FOR FUTURE until Patch Test work resumes or useful application-state logic is migrated durably.

### `ux/survey-vessel-configuration` — PR #72
Head: `4271567415af2b4b73e53711bb526f23ee1334a5`

Unique source:
- `src/hydrosim/app/survey_vessel_configuration.py`
- `tests/test_survey_vessel_configuration.py`

Disposition: PRESERVE FOR FUTURE until Survey Simulator work resumes or useful application-state logic is migrated durably.

## CLEANUP-READY — EFFECT ALREADY ON `main`

These branches are not preservation sources merely because squash merges left unique SHAs:
- `concept/vessel-footprint-showcase` — PR #299
- `visual/d11-spatial-configuration` — PR #298
- `visual/d9-bottom-detection-spatial` — PR #295
- `visual/d18-uncertainty-responsive-spatial` — PR #292
- `visual/d10-sector-spatial-polish` — PR #290
- `visual/d7-spatial-beamforming` — PR #282
- `concept/d14-timeline-polish` — PR #279
- `concept/d8-footprint-field` — PR #276
- `concept/array-directivity-depth` — PR #311
- `concept/map-vessel-refinement` — PR #307
- `ux/d11-reference-dimensions` — PR #316
- `concept/map-calm-reconciled` @ `d3ea05855641339a2a4503d3244e17db9395a032` — its `curriculum-map-calm.css` blob is identical on current `main`, and the import is present on `main`; no effect needs harvesting.
- `concept/visual-reconcile-main` @ `a352589d7706cfa476d5a7f085c4d082f1d89248` — its D12 presentation delta is present on current `main`, which additionally contains later D12 refinements; preserve the newer main version.
- `concept/full-didactic-module` @ `e892ce299e25424336b5472fb83a0146416a1092` — branch is an ancestor of current `main` (`ahead_by: 0`).
- `concept/full-didactic-module-v2` @ `e892ce299e25424336b5472fb83a0146416a1092` — exact alias of the ancestor branch above.
- `concept/full-didactic-module-v3` @ `e892ce299e25424336b5472fb83a0146416a1092` — exact alias of the ancestor branch above.

## CLEANUP-READY — SUPERSEDED / DUPLICATE / NO UNIQUE VALUE

- `ux/ped-d9-signal-sounding-link`
- `ux/ped-d9-signal-sounding-link-v2`
- `ux/ped-d9-signal-sounding-link-v3`
- `ux/ped-d9-bottom-detection`
- `ux/ped-d9-bottom-detection-v2`
- `ux/reconcile-d10-d12`
- `ux/ped-d10-multisector`
- `ux/ped-d12-vessel-motion`
- `ux/ped-d18-uncertainty-first-slice`
- `ux/ped-d18-uncertainty-first-slice-v2`
- `ux/ped-d11-configuration-snapshot`
- `ux/ped-d11-vessel-production`
- `ux/ped-d6-production-array`
- `ux/ped-d1-wave-lab`
- `ux/ped-d1-final`
- `ux/react-signal-production`
- `software-engineering/ped-d4-react-bridge`
- `software-engineering/ped-d6-react-bridge`
- `software-engineering/fix-d7-sector-sign`
- `ux/sounding-formation-state`
- `ux/motion-mainline`
- `ux/vessel-d5-completion`
- `ux/vessel-vertical-reference`
- `concept/map-calm-hierarchy`

### `concept/general-menu-v2`
PR #261 was closed unmerged, but its major intended effects were subsequently absorbed through narrower current-main changes (#307, #310, #282, #276/#299, #268/#299 and later UX work). Do not preserve the mixed 22-commit branch as a development line. If a concrete missing visual effect is later demonstrated, recover only that exact effect from history.

Disposition: CLEANUP-READY.

## CLEANUP-READY — OPERATIONAL RESIDUE

- all `capture-ui-screenshot*`
- `ui-shot`
- `ui-shot2`
- `ui-shot3`
- confirmed transient `*-temp` branches with no active PR and no unique product code

## KEEP

- `main`
- intentional `archive/pedagogical-concept-pre-science`
- intentional `archive/v0.0.1-prototype`
- any branch attached to genuinely active WIP discovered after this inventory update

## Morning target

KEEP:
- `main`
- intentional archives
- genuinely active WIP only

PRESERVE-SOURCE:
- `software-engineering/pitch-patch-test-adapter` @ `93000aa207b1e953b53bcff2394c1d03e013937d`
- `ux/patch-roll-submodule` @ `c1bd3284c57072a1412a8a65894cc1f46a5668ec`
- `ux/survey-vessel-configuration` @ `4271567415af2b4b73e53711bb526f23ee1334a5`

CLEANUP-READY:
- every branch explicitly listed in the cleanup sections above, including `integration/limbo-harvest` now that #320 is merged.
