# QA Manual Activation

The `qa-scientific-validation` role currently has no dedicated polling automation because the project automation capacity is limited.

The Coordination Secretary monitors the shared handoff queue. When a concrete open handoff requires independent QA / scientific validation, the Secretary must surface that request to the project owner for manual forwarding to the QA conversation. The Secretary must not perform the QA work itself.

## Manual activation prompt

Paste the following into the HydroSIM QA & Scientific Validation conversation when QA action is required:

> Act as HydroSIM `qa-scientific-validation`. Review the GitHub repository `ivanbodra/HydroSIM` and read `docs/coordination/agent_handoffs.md`. Check the open handoff Issue(s) addressed to `qa-scientific-validation` that I am forwarding to you. Independently validate the relevant scientific/computational claim or implementation within your defined QA role. Read the cited source material, perform independent checks where appropriate, and reply in the same GitHub Issue with findings and evidence. Close the Issue only when its completion condition is satisfied. If the validation exposes a concrete dependency on another HydroSIM specialist, create the corresponding handoff with explicit FROM/TO. Do not make Scientific Lead model-selection decisions or Software Engineering implementation decisions on their behalf.

No recurring automation should be created for QA while the automation-slot constraint remains in effect.
