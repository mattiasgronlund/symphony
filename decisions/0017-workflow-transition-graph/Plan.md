# Plan — 0017 Workflow transition graph

## Scope

Replaces the flat milestone map with an explicit transition graph in Section 11.6 "Workflow State Machine
and Milestone Signals", and the `tracker.milestones` config key with `tracker.transitions`. Refines, does
not reverse, decision 0008. Touches Section 5.3.1 `tracker` (object), the Section 6.4 cheat sheet, the
Section 5.4 prompt-authority wording, the Section 17.3 test rows, and the Section 18 checklist. Defers
provider-representation of states and tracker write-capability to a later capability decision; Section 11.6
stays silent on representation.

## Steps

1. Retitle Section 11.6 "Workflow State Machine and Milestone Signals" to "Workflow State Machine and
   Transition Triggers" and rewrite its body so the state-machine is a directed graph: nodes are tracker
   workflow-state names; each transition is `{from, on, to}`; Symphony performs `set_state(issue_id, to)`
   (Section 11.1) when, in state `from`, trigger `on` fires; a trigger with no matching `from`-state
   transition performs no transition; the graph MUST be deterministic (at most one transition per
   `(from, on)`; duplicates are a config error); the graph is defined over neutral state names and does not
   specify provider representation. Done when Section 11.6 describes a `{from, on, to}` graph keyed on
   triggers and no longer describes a flat `signal -> state` map.

2. Ensure Section 11.6 defines the closed trigger vocabulary in two groups: **milestone signals**
   (agent-emitted via the broker CLI: `ready-for-review`, `blocked`, `done`) and **run outcomes**
   (orchestrator-observed: `dispatched`, `pull_request_opened`, `run_succeeded`, `run_failed`,
   `retries_exhausted`), each run outcome citing its Section 7.2 terminal reason or Section 7.3 trigger
   origin. State that operators wire triggers to transitions but do not introduce new trigger names. Done
   when both trigger groups are listed with run outcomes cross-referenced to Sections 7.2/7.3.

3. Ensure the Section 11.6 "Process authority" content is preserved: the repository prompt advises which
   milestone signal to emit and cannot grant a trigger a transition the graph does not define; run outcomes
   are orchestrator-emitted and not influenceable by prompt wording; transitions remain operator-owned.
   Done when process authority still forbids prompt wording from widening the transition set.

4. Replace the `tracker.milestones` field (map `signal -> state_name`) in the Section 5.3.1 `tracker`
   object with `tracker.transitions` (a list of `{from, on, to}` entries; `Default: []` meaning no
   policy-driven transitions), cross-referenced to Section 11.6. Done when `tracker.milestones` no longer
   appears in Section 5.3.1 and `tracker.transitions` is documented with `Default: []`.

5. Update the Section 6.4 cheat sheet: replace the `tracker.milestones` row with
   `tracker.transitions`: list of `{from, on, to}`, default `[]` (workflow state-machine, Section 11.6).
   Done when the cheat sheet lists `tracker.transitions` and not `tracker.milestones`.

6. Cross-cutting sync of Section 17.3 and Section 18 (see below). Done when neither still frames the
   mechanism as a flat milestone-signal mapping.

## Cross-cutting sync

- Section 6.4 cheat sheet: handled in Step 5.
- Section 17.3 "Issue Tracker Client": change the milestone row to assert that transitions are driven by a
  deterministic graph keyed on milestone signals and observed run outcomes, an unmatched trigger transitions
  nothing, and a duplicate `(from, on)` is a config error.
- Section 18 checklist: change "Symphony-driven lifecycle via a policy-owned state-machine and agent
  milestone signals" to a transition graph keyed on agent milestone signals and observed run outcomes.

## Anchor changes

- `tracker.milestones` (map `signal -> state_name`) — removed; superseded by `tracker.transitions` (list of
  `{from, on, to}`).
- Section 11.6 "Workflow State Machine and Milestone Signals" — retitled to "Workflow State Machine and
  Transition Triggers".
- New anchors: `tracker.transitions`; the run-outcome triggers `dispatched`, `pull_request_opened`,
  `run_succeeded`, `run_failed`, `retries_exhausted`. The milestone signals (`ready-for-review`, `blocked`,
  `done`) are unchanged, reclassified as one of the two trigger groups.

## Status

Applied to `SPEC.md`.
