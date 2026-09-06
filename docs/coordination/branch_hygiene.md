# HydroSIM Branch Hygiene

## Purpose

HydroSIM uses short-lived branches to isolate concrete work without allowing branch history to become a second project-management system.

The repository has accumulated substantial branch sprawl. This policy makes branch lifetime and ownership explicit for every agent.

## Branch states

GitHub does not provide native branch labels, so HydroSIM uses these coordination states:

- **KEEP-ACTIVE** — branch is tied to an open PR or an explicitly active short-lived task.
- **KEEP-ARCHIVE** — branch is intentionally retained as historical reference and uses the `archive/` prefix.
- **REVIEW** — branch has no open PR and may contain unique work; compare it with `main` before deleting it.
- **DELETE-CANDIDATE** — branch is operational residue or is clearly superseded; delete after confirming it contains no unique unmerged effect.

The temporary audit registry is tracked in GitHub issue #317.

## Permanent operating rules

1. **One branch per active effect/PR.** Do not create parallel branches for the same intended outcome.
2. **Search before branching.** Before creating a branch, inspect current `main`, open PRs, and nearby active branches to avoid duplicate work.
3. **Branches are short-lived.** A production or integration branch should normally have an associated open PR or a clearly documented short-lived reason.
4. **Merge or abandonment ends branch lifetime.** Once the effect is integrated or explicitly dropped, the branch should be deleted.
5. **Operational branches are disposable.** Screenshot, capture, rebase, diagnostic, and temporary branches must not become long-lived repository state.
6. **Do not version branch names as workflow.** Avoid `v2`, `v3`, `final`, `final2`, `mainline`, `rebased`, `temp`, and similar successor branches when the same active branch can be updated safely.
7. **Use `archive/` only deliberately.** Historical branches that genuinely preserve a useful project milestone may remain, but their archival intent must be explicit.
8. **Do not infer activity from existence.** A branch without an open PR or documented active task is not automatically active.
9. **Prefer updating an active branch over creating a new one.** Create a replacement branch only when there is a concrete technical reason such as irreconcilable history or a deliberately separate effect.
10. **Agents are responsible for branch hygiene.** Every specialist should avoid leaving orphan branches behind. The coordination secretary audits for duplicates, stale branches, and operational residue.

## Current cleanup classification

### KEEP-ACTIVE

- `main`
- `concept/map-vessel-refinement` — PR #307
- the active branch associated with PR #310
- the active branch associated with PR #311
- the active branch associated with PR #316

### KEEP-ARCHIVE

- `archive/pedagogical-concept-pre-science`
- `archive/v0.0.1-prototype`

### DELETE-CANDIDATE families

After confirming no unique unmerged effect remains:

- `capture-ui-screenshot*`
- `ui-shot*`
- obvious transient branches containing markers such as `-temp`, `-rebased`, `rebase-`, `-final2`, `-run`, `-use`, or `-work` when a successor or merged PR already exists

### REVIEW families

All remaining branches without an open PR under these prefixes must be compared with `main` before deletion:

- `concept/`
- `ux/`
- `interface-ux/`
- `eng/`
- `software/`
- `software-engineering/`
- `feature/`
- `fix/`
- `integration/`
- `visual/`
- `qa/`

## Agent workflow

Before meaningful implementation work:

1. fetch or inspect current `main`;
2. inspect open PRs relevant to the same subsystem;
3. reuse the existing active branch when the effect is the same;
4. create a new branch only for a distinct effect;
5. open or update one focused PR;
6. after integration, remove the now-obsolete branch when tooling/permissions allow.

## Coordination secretary responsibility

The coordination secretary should periodically:

- identify branches with no open PR and no explicit archival role;
- flag duplicated/superseded branch families;
- maintain issue #317 only while cleanup is active;
- avoid creating new cleanup issues when the existing registry is sufficient;
- close the registry once all legacy branches have been classified and the repository returns to normal branch hygiene.

Branch cleanup is coordination work, not product work. It should be performed efficiently and should not distract specialists from active scientific, engineering, UX, validation, or visual tasks.
