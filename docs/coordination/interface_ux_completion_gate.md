# Interface & UX Completion Gate

This gate prevents stale visual evidence and avoids rework in HydroSIM interface work.

A Didactic Explorer lesson is **not complete** because code exists, tests pass, or a PNG exists.

For each interface lesson, `interface-ux` must complete the following sequence:

1. Reuse the already integrated scientific/core implementation; do not reopen validated physics unless a concrete UI-blocking inconsistency is found.
2. Implement the real PySide6 lesson and the intended interaction/visual hierarchy.
3. Run focused UX/state tests.
4. Generate a **lesson-specific runtime capture from the exact implementation head being evaluated**.
5. Verify that the capture belongs to that head and is not a stale file from another branch/run.
6. Visually inspect the capture for the intended interaction result and known visual regressions before reporting completion.
7. Publish the fresh lesson-specific image under `docs/images/` only after the visual inspection passes.
8. After integration, verify on `main` that both the implementation and the corresponding fresh image are present.

## Evidence rule

A screenshot is valid completion evidence only when all of the following are true:

- it was generated from the exact code head being evaluated;
- it is lesson-specific (`signal`, `beam`, `propagation`, `vessel`, etc.);
- its file/hash is confirmed to be fresh rather than inherited from an older capture;
- it has been visually inspected by `interface-ux`;
- the final version is present on `main` after merge.

If any condition fails, the lesson remains incomplete.

## Reporting rule

When reporting interface completion, state separately:

- implementation status;
- test status;
- runtime capture status;
- visual inspection status;
- integration-to-`main` status.

Do not infer one status from another.
