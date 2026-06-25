# Plan — 0021 set_state write semantics

## Scope

Adds Section 11.8 "State Transition Write Semantics" specifying the obligations of `set_state` (Section
11.1), and two error categories to Section 11.4 (`tracker_state_unreachable`, `tracker_state_conflict`).
Syncs the Section 17.3 test rows and the Section 18 checklist. No config change; `set_state` and the
transition graph (Section 11.6) are unchanged in shape.

## Steps

1. Ensure a Section 11.8 "State Transition Write Semantics" exists stating that `set_state(issue_id,
   target_state)` MUST be idempotent (already-in-target is a successful no-op and the adapter MUST NOT
   re-apply a transition), fails with `tracker_state_unreachable` when the target is unreachable/unknown,
   fails with `tracker_state_conflict` when the state changed underneath the write, SHOULD verify the
   result where state is applied through eventually-consistent writes, and treats a required transition
   input it cannot express as `Implementation-defined`. Done when Section 11.8 defines these obligations.

2. Ensure Section 11.8 states that a `set_state` failure is logged and does not by itself fail the run, and
   that a `tracker_state_conflict` triggers re-reconciliation (Section 8.5) rather than a blind retry. Done
   when the orchestrator handling is stated.

3. Ensure `tracker_state_unreachable` and `tracker_state_conflict` are listed among the Section 11.4
   RECOMMENDED error categories, each cross-referencing Section 11.8. Done when both appear.

4. Cross-cutting sync of Section 17.3 and Section 18 (see below).

## Cross-cutting sync

- Section 17.3 "Issue Tracker Client": add a row asserting `set_state` is idempotent (already-in-target
  succeeds without re-applying a transition), fails `tracker_state_unreachable` for an unreachable target,
  and `tracker_state_conflict` on a concurrent state change.
- Section 18 checklist: add a bullet that `set_state` is idempotent and surfaces
  `tracker_state_unreachable` / `tracker_state_conflict` rather than silently succeeding, and that a
  transition failure does not fail the run.
- Section 6.4 cheat sheet: no change (no config field).

## Anchor changes

- New anchors: Section 11.8 "State Transition Write Semantics"; the error categories
  `tracker_state_unreachable` and `tracker_state_conflict`.

## Status

Applied to `SPEC.md`.
