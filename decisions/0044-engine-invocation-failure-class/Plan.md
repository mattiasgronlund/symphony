# Plan — 0044 Engine invocation failure class

## Scope

`SPEC.md` Sections 14.1 (a new core failure class), 14.2 (its recovery behavior), 17.4 (a test-matrix
check), and 18.1.4 (a checklist item in the VCS Engine group). `VCSX-SPEC.md` and `VCSX-CONTRACT.md`
are unchanged — the engine side of this contract is already specified (`VCSX-SPEC.md` Sections 8.3
and 8.5); this decision adds only the consumer side.

## Steps

1. **Add the failure class.** In Section 14.1 "Failure Classes", ensure a core class
   `Engine Invocation Failures` exists, positioned after `Observability Failures` and before the
   OPTIONAL remote classes so the core classes stay contiguous. It covers exactly the cases in which
   the policy did not run:
   - The engine is unavailable — not installed, not executable, or not resolvable at the pinned
     version.
   - The engine does not conform to the invocation contract (an unreadable or malformed result
     envelope).
   - The engine refuses below the repository's `version_floor` (`VCSX-SPEC.md` Section 8.5).
   - The engine returns a usage or configuration result in which the policy did not run
     (`VCSX-SPEC.md` Section 8.3, exit `2`) — for example an invalid `repo.policy.toml`.
   Ensure the class states its own boundary: outcomes of operations that *did* run are owned by the
   action-policy machine (Section 9.12) and are not this class. Done when the class exists with those
   four cases and the boundary sentence, and no case overlaps Section 9.12.

2. **Renumber the OPTIONAL classes.** Ensure `Node Provisioning Failures` and
   `Executor Bring-up Failures` follow the new class, and that the note beginning "an OPTIONAL
   extension MAY define additional failure categories" refers to them by their new numbers. Done when
   the core classes are contiguous, the OPTIONAL ones are last, and no stale number remains.

3. **Add the recovery behavior.** In Section 14.2 "Recovery Behavior", ensure an
   `Engine invocation failures` entry states: skip new dispatches for the affected repository, because
   the `version_floor` and the operation flow are declared in that repository's `repo.policy.toml`, so
   the failure is repository-scoped rather than a single worker's; keep the service alive and retry on
   a later tick; do not convert to a per-worker backoff retry; and an unavailable or non-conforming
   engine skips dispatch for every repository that requires one. Ensure persistent cases MAY be parked
   rather than retried indefinitely, with the choice `Implementation-defined` and documented, matching
   the clause the repository-provisioning and node-provisioning entries already carry. Done when the
   entry exists and reads consistently with those neighbours.

4. **Add a test-matrix check.** In Section 17.4 "Orchestrator Dispatch, Reconciliation, and Retry",
   ensure a check that a below-`version_floor` or usage/configuration engine result skips that
   repository's dispatches for the tick and is retried later, leaving other repositories and running
   workers untouched, and is not converted to a per-worker backoff retry. Done when the check exists
   alongside the `Repository Provisioning Failures` check it mirrors.

5. **Add the checklist item.** In Section 18.1.4 "VCS Engine", ensure an item requiring that the
   deployment declare a `version_floor` and classify a below-floor refusal, an unavailable or
   non-conforming engine, and a usage/configuration result as `Engine Invocation Failures`, recovered
   per Section 14.2. Done when the item exists in the VCS Engine group and names the class.

## Cross-cutting sync

- Section 6.4 "Core Config Fields Summary (Cheat Sheet)": no change. `version_floor` is a
  `repo.policy.toml` field whose schema Section 5.6 defers to the engine contract; the cheat sheet
  covers operator policy config fields.
- Section 14.3 "State Recovery Classes": no change. The new class introduces no runtime state.
- Section 17: changed by step 4. Section 18: changed by step 5.

## Anchor changes

Added — `Engine Invocation Failures` (failure class, Section 14.1).

Renumbered — the OPTIONAL failure classes `Node Provisioning Failures` and `Executor Bring-up
Failures` shift by one position as the new core class is inserted ahead of them. Both are referenced
by name elsewhere; the ordinals are incidental, and the only positional reference is the note at the
end of Section 14.1, updated in step 2.

Removed — none. Renamed — none.

## Status

Applied to `SPEC.md`, as planned and with no deviations. `Engine Invocation Failures` is core class
7; `Node Provisioning Failures` and `Executor Bring-up Failures` shifted to 8 and 9, and the closing
note of Section 14.1 now reads "classes 8 and 9". The class carries an `Important boundary:` aside
naming Section 9.12 as the owner of outcomes for operations that did run, so the two mechanisms stay
disjoint.
