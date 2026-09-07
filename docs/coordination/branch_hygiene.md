# HydroSIM Branch Hygiene

## Purpose

HydroSIM uses short-lived branches to isolate concrete work without allowing branch history to become a second project-management system.

The objective is simple: every non-archive branch must have a current reason to exist, and completed or abandoned work must not accumulate as remote branch residue.

## Branch states

GitHub does not provide native branch labels, so HydroSIM uses these coordination states:

- **KEEP-ACTIVE** — branch is tied to an open PR or an explicitly active short-lived task.
- **KEEP-ARCHIVE** — branch is intentionally retained as historical reference and uses the `archive/` prefix.
- **REVIEW** — branch has no open PR and may contain unique work; compare it with `main` before deleting it.
- **DELETE-CANDIDATE** — branch is operational residue or clearly superseded; delete after confirming it contains no unique unmerged effect.

## Permanent operating rules

1. **One branch per active effect/PR.** Do not create parallel branches for the same intended outcome.
2. **Search before branching.** Before creating a branch, inspect current `main`, open PRs, and nearby active branches to avoid duplicate work.
3. **Branches are short-lived.** A production or integration branch should normally have an associated open PR or a clearly documented active task.
4. **Merge or abandonment ends branch lifetime.** Once the intended effect is integrated or explicitly dropped, delete the remote branch.
5. **Operational branches are disposable.** Screenshot, capture, rebase, diagnostic, and temporary branches must not become long-lived repository state.
6. **Do not version branch names as workflow.** Avoid `v2`, `v3`, `final`, `final2`, `mainline`, `rebased`, `temp`, and similar successor branches when the same active branch can be updated safely.
7. **Use `archive/` only deliberately.** Historical branches that genuinely preserve a useful project milestone may remain, but archival intent must be explicit.
8. **Do not infer activity from existence.** A branch without an open PR or documented active task is not automatically active.
9. **Prefer updating an active branch over creating a new one.** Create a replacement branch only for a concrete technical reason such as irreconcilable history or a deliberately separate effect.
10. **Agents own cleanup of their own branches.** A specialist that creates a branch is responsible for keeping it current and removing it after merge/abandonment when tooling permits.
11. **Do not preserve useful knowledge only in a branch.** Before deleting unique deferred work, move the durable intent/contract/behavior into an Issue or canonical document, then delete the obsolete branch.
12. **Branch count is a hygiene signal, not a product metric.** Growth should trigger inspection, not incentives to create or retain branches.

## Normal repository baseline

The expected steady state is:

- `main`;
- explicitly intentional `archive/*` branches;
- a small set of short-lived branches corresponding to genuinely active PRs/tasks.

There is no fixed hard cap because parallel work varies, but branch growth must remain explainable. As an operational trigger, the Coordination Secretary should inspect the branch set when either condition becomes true:

- more than **10 non-archive remote branches** exist; or
- **3 or more non-archive branches have no open PR or explicit active-task reason**.

These thresholds trigger review only. They do not authorize automatic deletion.

## Agent workflow

Before meaningful implementation work:

1. fetch or inspect current `main`;
2. inspect open PRs relevant to the same subsystem;
3. reuse the existing active branch when the intended effect is the same;
4. create a new branch only for a distinct effect;
5. use a role-oriented prefix such as `ux/`, `software-engineering/`, `visual/`, `qa/`, `science/`, or `coord/` where appropriate;
6. open or update one focused PR rather than creating successor branches;
7. after integration or abandonment, remove the obsolete remote branch when tooling/permissions allow.

If a replacement branch is genuinely necessary, the old branch must be closed out explicitly: merged, deleted, or documented as REVIEW/PRESERVE until its unique effect is resolved.

## Coordination Secretary responsibility

The Coordination Secretary performs lightweight branch hygiene as part of normal coordination, not as a broad recurring audit.

A review is warranted when triggered by branch growth, a recently merged/closed PR, a branch-cleanup event, duplicate branch naming, or an apparently orphan branch.

When triggered, the Secretary should:

1. list current remote branches;
2. preserve `main` and deliberate `archive/*` branches;
3. identify each other branch's open PR or explicit active-task reason;
4. flag duplicate/successor branch families and orphan branches;
5. close the coordination loop after merges by ensuring obsolete branches are removed or have a concrete retained reason;
6. never delete a REVIEW branch merely from age or naming; verify that no unique unmerged effect would be lost;
7. avoid creating a permanent cleanup registry during healthy steady-state operation.

If the branch set is small and every non-archive branch has a clear active owner/effect, no coordination action is warranted.

## Current steady state after 2026-09-06 cleanup

The large legacy branch cleanup is complete. Issue #317 served as the temporary cleanup registry and is closed.

At steady state, historical cleanup lists are not authoritative. Current branch existence, open PR/task ownership, and this policy govern branch hygiene.

Branch cleanup is coordination work, not product work. It should remain lightweight and must not distract specialists from active scientific, engineering, UX, validation, or visual delivery.
