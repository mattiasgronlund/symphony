# Background — 0008 Tracker abstraction and writes

## Context

Points 4, 6: Symphony owns all issue-tracker interaction — reads *and* writes — across at least Linear
and Forgejo, with the agent supplying content. This deliberately reverses the spec's current
"scheduler and tracker reader" boundary (Sections 1, 2.2, 11.5), where ticket writes were the agent's
job via `linear_graphql` (now retired, 0003).

## Options considered

### Write initiative

- **Pure relay / relay + minimal lifecycle / Symphony-driven lifecycle (chosen).** Symphony owns state
  transitions via a workflow state-machine; the agent supplies free-text content only. This gives
  consistent process enforcement at the cost of agent flexibility and a state-machine to specify.

### Where the state-machine lives

- **`WORKFLOW.md` proposes / split / policy config (chosen).** Because transitions are privileged
  tracker writes executed outside the sandbox, the in-sandbox-only rule (0005) places the
  state-machine in operator policy config. Operators own process; repos do not.

### How the agent signals progress

- **Outcome-driven only / agent requests explicit states / milestone signals mapped (chosen).** The
  agent emits semantic milestone signals (`ready-for-review`, `blocked`, `done`, ...) via the CLI; the
  policy state-machine maps each to the actual tracker transition. The agent expresses intent;
  operators control the resulting states.

## Decision and reasoning

A tracker adapter (Linear, Forgejo) supports reads and writes. Symphony drives ticket lifecycle via a
policy-defined state-machine; the agent supplies content and emits milestone signals that the
state-machine maps to transitions.

Problems to watch: this reverses a load-bearing boundary repeated in several sections, so the inversion
must be applied consistently (Sections 1, 2.2, 11.5, and the failure/security material in 14–15); and
putting the state-machine in policy removes process control from repo authors, which is intended but a
real change in who owns workflow.
