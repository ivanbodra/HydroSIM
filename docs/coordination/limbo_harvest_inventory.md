# HydroSIM limbo-code harvest inventory

Status date: 2026-09-06

Purpose: prevent rework by distinguishing code that is already integrated, code that was superseded, and code that still contains unique implementation worth recovering before branch deletion.

## Operating rule

Do not use Git ancestry alone to decide whether a branch contains missing product value. HydroSIM commonly used squash merges, so an old branch can still appear `ahead` even when its effect is already present on `main`. PR disposition and current-main behavior take precedence.

## HARVESTED INTO `integration/limbo-harvest`

### `ux/ped-d8-synchronized-comparison` — PR #227

Unique effect that had not been integrated: synchronized SBES × MBES learner comparison from the same canonical API response.

Recovered on current `main` instead of restoring the stale file wholesale. The newer D8 footprint-field visualization remains intact.

Harvest commit: `dcc9a4c48489c8e73a9c2be570a96f8091420280`.

After this harvest is validated/merged, `ux/ped-d8-synchronized-comparison` is cleanup-ready.

## UNIQUE BUT INTENTIONALLY DEFERRED — DO NOT DELETE YET

These branches contain substantive code absent from `main`, but they belong to future product slices or scientific/application work and should not be silently merged as part of a visual cleanup.

### `software-engineering/pitch-patch-test-adapter` — PR #89

Head: `93000aa207b1e953b53bcff2394c1d03e013937d`

Unique files relative to current `main`:
- `src/hydrosim/scenarios/pitch_calibration.py` (+239 lines)
- `tests/test_pitch_calibration_scenario.py` (+54 lines)
- scenario exports

Disposition: specialist review required. This is a real deterministic pitch patch-test implementation, not branch noise.

### `ux/patch-roll-submodule` — PR #70

Head: `c1bd3284c57072a1412a8a65894cc1f46a5668ec`

Unique files:
- `src/hydrosim/app/patch_roll_lesson.py` (+89 lines)
- `tests/test_patch_roll_lesson.py` (+66 lines)
- product-structure tests

Disposition: preserve until Patch Test work is deliberately resumed or the reusable application state is migrated to current architecture.

### `ux/survey-vessel-configuration` — PR #72

Head: `4271567415af2b4b73e53711bb526f23ee1334a5`

Unique files:
- `src/hydrosim/app/survey_vessel_configuration.py` (+82 lines)
- `tests/test_survey_vessel_configuration.py` (+55 lines)
- product-structure tests

Disposition: preserve until Survey Simulator work is deliberately resumed or the reusable application state is migrated.

## STALE SOURCE BRANCHES WHOSE EFFECT IS ALREADY IN `main`

These should not be kept merely because Git compare reports unique SHAs. Their PRs were merged, usually by squash, and current-main already contains the intended effect.

Examples directly relevant to the recent visual audit:
- `concept/vessel-footprint-showcase` — PR #299 merged
- `visual/d11-spatial-configuration` — PR #298 merged
- `visual/d9-bottom-detection-spatial` — PR #295 merged
- `visual/d18-uncertainty-responsive-spatial` — PR #292 merged
- `visual/d10-sector-spatial-polish` — PR #290 merged
- `visual/d7-spatial-beamforming` — PR #282 merged
- `concept/d14-timeline-polish` — PR #279 merged
- `concept/d8-footprint-field` — PR #276 merged
- `concept/array-directivity-depth` — PR #311 merged
- `concept/map-vessel-refinement` — PR #307 merged
- `ux/d11-reference-dimensions` — PR #316 merged

These branches are cleanup-ready.

## SUPERSEDED / DUPLICATE BRANCHES — NO HARVEST NEEDED

The PR history explicitly records a later replacement or an already-integrated equivalent. These branches should not be treated as hidden treasure unless a new concrete missing effect is demonstrated.

- `ux/ped-d9-signal-sounding-link` → superseded by #283/#285/#287
- `ux/ped-d9-signal-sounding-link-v2` → superseded by #285/#287
- `ux/ped-d9-signal-sounding-link-v3` → superseded by #287
- `ux/ped-d9-bottom-detection` → superseded by #206/#211
- `ux/ped-d9-bottom-detection-v2` → superseded by #211
- `ux/reconcile-d10-d12` → superseded by #221
- `ux/ped-d10-multisector` → superseded by integrated D10/D12 work
- `ux/ped-d12-vessel-motion` → superseded by integrated D12 work
- `ux/ped-d18-uncertainty-first-slice` → superseded by #250/#252
- `ux/ped-d18-uncertainty-first-slice-v2` → superseded by #252
- `ux/ped-d11-configuration-snapshot` → superseded by #239 and later D11 work
- `ux/ped-d11-vessel-production` → superseded by merged D11 production evolution
- `ux/ped-d6-production-array` → superseded by #197
- `ux/ped-d1-wave-lab` / `ux/ped-d1-final` → superseded by later integrated D1 revisions
- `ux/react-signal-production` → superseded by integrated/rebased D2 production
- `software-engineering/ped-d4-react-bridge` → superseded by merged D4 API bridge
- `software-engineering/ped-d6-react-bridge` → superseded by merged D6 API bridge
- `software-engineering/fix-d7-sector-sign` → superseded by merged #185
- `ux/sounding-formation-state` → superseded by merged #84
- `ux/motion-mainline` → superseded by merged #59
- `ux/vessel-d5-completion` → superseded by merged #57
- `ux/vessel-vertical-reference` → superseded by merged #45
- `concept/map-calm-hierarchy` → superseded by merged #286

## LARGE MIXED BRANCH: `concept/general-menu-v2`

PR #261 was closed without merge and contains 22 historical commits, but its major intended effects were subsequently integrated through narrower current-main changes:
- general learning-map architecture/history is already in `main`;
- bilingual map navigation was absorbed from #310;
- canonical user-authored vessel was integrated by #307;
- D7 spatial refinement by #282;
- D8 footprint field by #276/#299;
- D12 visual depth by #268/#299;
- later reset/localization work landed through dedicated UX PRs.

`web/pedagogical-explorer/history/CurriculumMap.v1.tsx` also already exists on `main`.

Disposition: do not merge or preserve this 22-commit mixed branch as a source branch. If a future concrete visual effect is shown missing, recover that specific effect from the commit history, not the whole branch.

## OBVIOUS OPERATIONAL BRANCHES — DELETE

No product code should depend on screenshot/capture branch history:
- all `capture-ui-screenshot*`
- `ui-shot`
- `ui-shot2`
- `ui-shot3`
- branches explicitly named `*-temp` when no open PR depends on them

## Current target state

During harvest:
- `main`
- `integration/limbo-harvest`
- the three unique deferred source branches above
- intentional `archive/*` branches

After harvest validation and specialist disposition of deferred code:
- `main`
- only genuinely active task branches
- intentional `archive/*` references

The harvest branch itself must be deleted after its PR is merged.
