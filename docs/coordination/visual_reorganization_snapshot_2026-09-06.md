# HydroSIM visual reorganization snapshot — 2026-09-06

This file freezes the current coordination state before branch cleanup and visual code consolidation. It is a snapshot, not a permanent roadmap.

## Current objective

Convert previously conceptualized and partially implemented visual work into the production HydroSIM `main` branch while reducing branch sprawl and avoiding further parallel implementations.

Operating principle:

> Integrate first. Reuse an existing active branch when possible. Create a new branch only for a genuinely distinct effect, and remove it after merge or abandonment.

## Already integrated into `main`

### Canonical HydroSIM vessel on System Map

Source PR: #307 — `concept/map-vessel-refinement`

Status: merged into `main`.

Effect:
- uses the user-authored HydroSIM SVG vessel as the canonical vessel identity on the System Map;
- exact vessel geometry is preserved;
- transducer and restrained transverse MBES fan are retained;
- terrain/DTM work remains deliberately deferred.

The source branch is cleanup-ready after verification.

### Array Directivity visual depth

Source PR: #311 — `concept/array-directivity-depth`

Status: merged into `main`.

Effect:
- stronger spatial depth and grid context;
- clearer TX/RX Mills-cross presentation;
- stronger readout/plot hierarchy;
- better focus, touch and responsive behaviour;
- no scientific/API change.

The source branch is cleanup-ready after verification.

### System Map EN/PT-BR localization

Source PR: #310 — `ux/system-map-localization`

Status: its reconciled content was applied directly to `main`; PR #310 was closed as absorbed rather than creating another replacement branch.

Effect:
- language toggle on the System Map;
- localized map chrome, status labels, family labels and navigation copy;
- canonical vessel from #307 retained.

The source branch is cleanup-ready after verification.

## Currently active functional branch

### `ux/d11-reference-dimensions`

PR: #316 — UX: complete PED-D11 vessel envelope and VRP controls.

Status: active, not ready to merge.

Current validation state:
- repository tests: success;
- production frontend build: success;
- focused learner UI tests: failure.

Known failure:
- PED-D11 UI test expects `transducer_lever_arm_m.x = 6` after the configured interaction but receives `2`.

Disposition:
- keep this branch active until the functional contract/test is corrected;
- do not hide the failure with presentation-only work;
- once stable, align its visual identity with the canonical HydroSIM vessel without redefining geometry semantics.

## Branches to keep permanently or deliberately

- `main`
- `archive/pedagogical-concept-pre-science`
- `archive/v0.0.1-prototype`

The two `archive/*` branches are deliberate historical references, not active development branches.

## Temporary SOURCE / TO HARVEST branches

These branches contain visual implementation that is still unique relative to the current `main`. They must not be deleted until their useful content is either integrated, reworked into the current implementation, or explicitly rejected.

### `concept/vessel-footprint-showcase`

Current unique content relative to `main`:
- 2 commits ahead;
- changes in `vessel-motion-lab.css`;
- changes in `echosounder-lab.css`.

Use:
- source material for the final Vessel Motion visual implementation and possibly Echosounder presentation.

### `visual/d7-spatial-beamforming`

Current unique content:
- 1 commit ahead;
- `beamforming-lab.css`.

Use:
- source material for the planned Beamforming spatial refinement.

### `visual/d9-bottom-detection-spatial`

Current unique content:
- 1 commit ahead;
- `bottom-detection-lab.css`.

Use:
- source material for Bottom Detection spatial presentation.

### `visual/d10-sector-spatial-polish`

Current unique content:
- 1 commit ahead;
- `multisector-lab.css`.

Use:
- source material for Multi-sector visual refinement.

### `visual/d11-spatial-configuration`

Current unique content:
- 1 commit ahead;
- `vessel-configuration-lab.css`.

Use:
- source material only after the active D11 functional slice (#316) becomes stable.

### `visual/d18-uncertainty-responsive-spatial`

Current unique content:
- 1 commit ahead;
- `uncertainty-lab.css`.

Use:
- source material for Uncertainty spatial/responsive presentation.

### `concept/d14-timeline-polish`

Current unique content:
- 1 commit ahead;
- `timing-lab.css`.

Use:
- source material for Timing timeline polish.

### `visual/map-calm-hierarchy-v2`

Current unique content:
- 1 commit ahead;
- adds `curriculum-map-calm.css` with 38 lines.

Use:
- review only. The System Map has already evolved substantially through #307 and #310, so useful ideas must be selectively adapted rather than merged blindly.

## Example branch already shown to be safe to discard after cleanup review

### `concept/full-didactic-module-v3`

Comparison with current `main`:
- 0 commits ahead;
- 278 commits behind.

Disposition:
- no unique branch history is required for the current implementation;
- branch can be treated as a deletion candidate after the cleanup audit.

## Proposed visual harvest procedure

Create at most one temporary consolidation branch, recommended name:

`integration/visual-harvest`

Purpose:
- rescue useful implementation from the SOURCE / TO HARVEST branches;
- adapt it to the current `main` rather than merge obsolete histories;
- keep one commit per module/source for traceability;
- open one consolidation PR;
- classify every harvested source as `APPLY`, `REWORK`, or `DROP`;
- once each source is dispositioned, mark its old branch as cleanup-ready;
- after the consolidation PR is merged, delete `integration/visual-harvest` as well.

Do not create `v2`, `v3`, `final`, `rebased`, `mainline`, `temp`, screenshot, capture or other successor branches during this process.

## Visual direction to preserve

- The user-authored HydroSIM vessel is the canonical vessel identity. Do not redraw an alternative vessel.
- MBES fan must remain transverse/across-track, not a radar-like angular sweep.
- Animation should be restrained and technically meaningful.
- Preserve INPUT → IMMEDIATE VISUAL RESPONSE → PHYSICAL INTUITION.
- Prefer spatial hierarchy, depth and scientific meaning over decorative effects.
- Keep user-facing navigation bilingual EN/PT-BR.
- Do not alter scientific contracts, frames, units, API behaviour or canonical pedagogy during visual consolidation.
- Terrain/DTM remains outside the current visual harvest scope.

## Coordination records

- #317 — Branch hygiene audit and cleanup registry.
- #318 — Technical Lead handoff for overnight branch cleanup and visual integration.
- `docs/coordination/branch_hygiene.md` — permanent branch hygiene policy.

## Desired end state after harvest

The repository should no longer use old visual branches as informal storage.

Expected steady state:
- `main`;
- a very small number of genuinely active branches, normally around 1–5;
- deliberate `archive/*` branches;
- no lingering screenshot/capture/temp/rebase/version-suffix branches;
- no visual implementation left stranded solely in obsolete branches.

## Snapshot boundary

This document records the state immediately before beginning the visual-harvest consolidation. Future changes should update the canonical coordination records rather than retroactively rewriting this snapshot.
