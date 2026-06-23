# Plan — 0008 Tracker abstraction and writes

## Scope

Adds tracker writes and a tracker adapter, generalizing the Issue Tracker Integration Contract
(Section 11) beyond Linear; reverses the reader-only boundary (Sections 1, 2.2, 11.5); adds the
policy-owned workflow state-machine and the milestone-signal mapping; defines the broker CLI's tracker
verbs and milestone signals. Depends on 0003 (broker), 0005 (policy config), and the neutral CLI verb
surface (0007).

## Steps

1. Ensure a tracker adapter abstraction exists with reads and writes for at least Linear and Forgejo,
   producing the normalized issue model (Section 4.1.1). Done when the adapter's required read and
   write operations are specified.
2. Ensure the "tracker reader only" boundary is reversed wherever it appears (Sections 1, 2.2, 11.5)
   to "Symphony owns all tracker interaction; the agent supplies content." Done when no normative text
   still describes Symphony as write-abstaining.
3. Ensure a policy-owned workflow state-machine drives ticket state transitions. Done when the
   state-machine is defined as a policy-config artifact.
4. Ensure the agent communicates progress via semantic milestone signals (for example
   `ready-for-review`, `blocked`, `done`) that the state-machine maps to transitions. Done when the
   milestone-signal set and mapping are specified.

## Cross-cutting sync

Config cheat sheet (6.4): tracker write/auth and state-machine keys in policy config. Test matrix (17)
and checklist (18): tracker-write, state-machine, and milestone-mapping rows; remove the
tracker-writes-via-agent framing.

## Anchor changes

- Section 11 "Issue Tracker Integration Contract (Linear-Compatible)" — retitled to "Issue Tracker
  Integration Contract"; Section 11.2 "Query Semantics (Linear)" — retitled to "Adapter Semantics".
  The Section 1 / 11.5 reader boundary was already reversed in 0003; this decision adds the adapter
  writes and the state-machine.
- New anchors: Section 11.6 "Workflow State Machine and Milestone Signals"; the tracker adapter
  read/write operations (`add_comment`, `set_state`, `link_pull_request`); the `tracker.milestones`
  key; the workflow state-machine (policy-owned); and the milestone signals (`ready-for-review`,
  `blocked`, `done`). `tracker.kind` gains `forgejo`.
- Removed the Section 18.2 TODOs for first-class tracker writes and pluggable tracker adapters (now
  done).

## Status

Applied to `SPEC.md` on branch `broker-rearchitecture-0003-0009`.
