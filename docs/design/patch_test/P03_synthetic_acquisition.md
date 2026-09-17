# P3 — Synthetic Acquisition — Visual Treatment

Pedagogy: `docs/pedagogy/patch_test/P03_synthetic_acquisition.md`  
Science: `docs/science/patch_test_module_scientific_contract.md` §5

## Visual purpose

Turn a valid P2 plan into acquired evidence and make the learner understand that **Observed acquisition becomes immutable** once the run is complete.

Learner question: **What was physically acquired, what metadata belongs to that run, and what remains fixed during later calibration?**

## Dominant composition

Use one acquisition instrument with three linked layers:

1. **Track view** — vessel motion, line identity, direction/speed and progress.
2. **Swath/sounding view** — ping progression and accumulated observations over the shared terrain.
3. **Run provenance strip** — run ID, line identity, speed/direction, timing/configuration snapshot and usability state.

Do not split these into unrelated cards.

## Primary interaction

- select/confirm canonical P2 plan;
- `Acquire run` / `Acquire paired run`;
- play/pause/step where temporal playback is useful;
- choose which paired run is foregrounded;
- toggle swath / soundings / common support.

## Acquisition motion

This is an appropriate place for visible motion:

- vessel traverses the line;
- pings appear in time order;
- swath footprints paint the observed region;
- sounding/profile evidence accumulates progressively.

Use restrained timing and preserve `prefers-reduced-motion` alternatives.

## State treatment

### Truth

Terrain/trajectory Truth may drive the simulation but should not become a learner-facing calibration shortcut.

### Observed

At the end of acquisition, the observations and provenance should visibly become **locked**. Use stable solid point/profile styling and an explicit immutable-run treatment rather than merely text saying “immutable”.

### Configured / Derived

If a current reconstruction is shown, visually separate it from the fixed Observed evidence. P3 must not imply that changing calibration mutates the acquired dataset.

## Fitness for calibration

Show `usable`, `marginal`, or `reacquire` only with a concise geometric/execution reason. Reuse P2 common-support visual language so the learner sees the continuity from planning to execution.

## Visual hierarchy

1. acquisition path and evolving swath;
2. accumulated Observed evidence;
3. paired-run relationship;
4. provenance and fitness state;
5. numeric metadata.

## Acceptance

P3 passes when the learner can visually distinguish the planned geometry, the executed runs, immutable Observed evidence, and the later-reconstructable state without relying on prose.

## Referenced bibliography IDs

`iho_s5a_2_0_0_2026`; `noaa_fpm_2020`; `noaa_ocean_exploration_2010_patch_test`; `noaa_hssd_2022`; `rathnayake_lekkerkerk_2025_survey_systems_verification_calibration`; `jerram_hoy_sowers_baechler_2019_okeanos_shakedown`; `jerram_johnson_ferrini_2019_neil_armstrong_em710`; `johnson_beaudoin_et_al_2014_mbac_three_years`; `hughes_clarke_2003_dynamic_motion_residuals`.

See `99_references_by_submodule.md`.
