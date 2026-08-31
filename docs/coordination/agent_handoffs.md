# HydroSIM Agent Handoff Protocol

## Purpose

HydroSIM agents use GitHub Issues as the shared communication queue for cross-agent requests, decisions, reviews, dependencies, and responses.

The goal is to prevent relevant information from becoming isolated inside one specialist conversation while keeping coordination lightweight and traceable.

This mechanism is for concrete cross-agent needs only. It must not become a second project-management system or a place for routine conversation.

## Canonical agent identifiers

Use these identifiers in handoff issues:

- `technical-lead` — project-level technical integration, sequencing across specialist outputs, integration readiness, dependency resolution, and deciding when work is ready to advance to the next vertical slice. The Technical Lead does not replace specialist ownership of scientific models, software implementation, independent validation, or interface/UX decisions.
- `scientific-lead` — scientific model ownership, equations, assumptions, fidelity, references and scientific choices.
- `software-engineering` — implementation architecture, code quality, APIs, numerical/computational robustness, testing, packaging, CI and performance.
- `qa-scientific-validation` — independent scientific and computational validation, invariants, units, signs, frames, limits and reference-vs-implementation checks.
- `interface-ux` — Didactic Explorer / Survey Simulator interaction design, information architecture, visualization behaviour and bilingual user-facing interface.
- `coordination-secretary` — cross-agent routing, queue hygiene and detection of unaddressed dependencies.

New specialist agents may be added later, but their identifier must be documented here before use.

## Transport

Each cross-agent request is a GitHub Issue.

### Required title format

```text
[HANDOFF][TO:<recipient>][FROM:<origin>] <short subject>
```

Example:

```text
[HANDOFF][TO:qa-scientific-validation][FROM:software-engineering] Validate heave sign propagation in renderer adapter
```

For a request addressed to more than one agent, create separate issues unless the agents genuinely need to work on the same decision. This keeps ownership explicit.

## Required issue body

Every handoff must contain:

```markdown
## From
<origin agent id>

## To
<recipient agent id>

## Context
<minimum context needed to understand the request>

## Requested action
<what the recipient should evaluate, decide, implement, validate, or answer>

## Source
<GitHub file / issue / PR / commit / project-conversation reference when available>

## Priority
normal | urgent

## Completion condition
<what must be true for this handoff to be considered resolved>
```

Use `urgent` only when continuing without the answer could cause scientific error, incompatible implementation, data loss, or substantial rework.

## Recipient workflow

Every HydroSIM agent must periodically search open Issues addressed to its canonical identifier.

For each relevant handoff:

1. Read the complete issue and linked source material needed to understand it.
2. Take the requested action within the agent's own responsibility.
3. If another specialist is required, create a new handoff rather than silently expanding scope.
4. Reply in the issue with the result, decision, evidence, implementation reference, or blocking question.
5. Close the issue when the completion condition is satisfied.
6. Leave it open when action is still pending, explicitly stating the blocker or next required action.

A recipient must not close a handoff merely because it has been read.

## Origin-agent workflow

Before finishing meaningful HydroSIM work, each agent should ask:

> Does another HydroSIM agent need information or action from this work to make progress or avoid a concrete risk?

If yes, create a handoff issue immediately.

Do not create handoffs for:

- routine status updates;
- acknowledgements;
- duplicated information already recorded and routed;
- speculative work with no concrete dependency;
- requests that belong entirely inside the current agent's responsibility.

## Response format

Replies should be concise and actionable. Recommended structure:

```markdown
## Response
<answer / result / decision>

## Evidence or implementation
<references to files, tests, equations, PRs, commits or validation results>

## Follow-up
none | <explicit next action and owner>
```

If the response creates a new cross-agent dependency, open a new handoff issue and link it.

## Queue state

GitHub Issue state is the authoritative queue state:

- **Open** — action, answer, validation, or acknowledgement is still required.
- **Closed** — completion condition was satisfied.

Do not maintain a separate manual status ledger unless a concrete need emerges.

## Search convention

Agents should search open issues using both the title marker and their canonical identifier, for example:

```text
repo:ivanbodra/HydroSIM is:issue is:open "[HANDOFF]" "TO:software-engineering"
```

The coordination secretary should search all open handoff issues and identify stale, misrouted, unanswered, or blocked items.

## Polling policy

- Each specialist agent performs a handoff check every 2 hours when an automation slot is allocated to that specialist.
- Specialists without a dedicated automation slot, such as QA when automation capacity is constrained, are activated manually by the project owner when a concrete handoff requires their attention.
- The coordination secretary performs an independent queue-health check every 4 hours and must surface actionable handoffs for manually activated specialists to the project owner rather than attempting the specialist work itself.
- Polling is a safety net. Agents should create and answer handoffs immediately when they are already active and the dependency is known.

## Coordination secretary responsibilities

The coordination secretary does not replace specialist ownership. Its periodic review should:

1. list open handoff issues;
2. verify that `FROM` and `TO` are valid and explicit;
3. detect unanswered or apparently abandoned handoffs;
4. detect requests sent to the wrong specialist when this is clear from project governance;
5. flag blockers that require a new handoff;
6. surface pending handoffs for specialists without an active polling automation to the project owner for manual forwarding;
7. avoid duplicating issues that already exist;
8. leave scientific, engineering, validation and interface decisions to the responsible specialist.

When no intervention is needed, the secretary should make no repository changes.

## Project governance

This protocol inherits HydroSIM governance:

- GitHub is the shared technical memory.
- Repository content is canonical in English.
- User-facing software supports English and Portuguese.
- Scientific decisions remain traceable to references and validation.
- Agents must respect specialist boundaries and avoid parallel specifications.
- Coordination work must reduce a concrete project risk or enable progress; coordination for its own sake is not a project objective.
