# QA Manual Activation

The `qa-scientific-validation` role currently has no dedicated polling automation because the project automation capacity is limited.

The Coordination Secretary monitors the shared handoff queue. When a concrete open handoff requires independent QA / scientific validation, the Secretary must surface that specific request to the project owner with its Issue number, context, requested action, completion condition, and sources. The project owner can then forward it to the QA conversation. The Secretary must not perform the QA work itself.

## Manual activation template

When QA action is required, the Coordination Secretary should provide the project owner a ready-to-forward prompt in this form:

> Act as HydroSIM `qa-scientific-validation`. Address GitHub Issue #<NUMBER> in `ivanbodra/HydroSIM`: <TITLE>. Read `docs/coordination/agent_handoffs.md`, the full Issue, and its cited sources. The requested QA action is: <ACTION>. The completion condition is: <COMPLETION CONDITION>. Independently validate the relevant scientific/computational claim or implementation within your defined QA role. Perform independent checks where appropriate and reply in the same GitHub Issue with findings and evidence. Close the Issue only when its completion condition is satisfied. If the validation exposes a concrete dependency on another HydroSIM specialist, create the corresponding handoff with explicit FROM/TO. Do not make Scientific Lead model-selection decisions or Software Engineering implementation decisions on their behalf.

No recurring automation should be created for QA while the automation-slot constraint remains in effect.
