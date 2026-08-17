# Plan — 0115 Observing the budget is free; spending on it is not

## Scope

`SPEC.md`: a new Section 8.11 "Forge API Budget" (the Core recording half and the OPTIONAL guard
half), Section 8.5 or 9.7 (dispatching `await_checks` and disposing of its four outcomes), Section
9.10 (awaiting is not authority to merge), Section 6.4 (cheat sheet), Section 13.5 (what is
recorded), Section 14.2 (the park disposition), Sections 17, 18.

`conformance/vocabulary.json`: the `forge_budget.*` configuration namespace joins the namespace set.

## Steps

1. **New section — Forge API Budget.** Ensure a section exists stating that the budget snapshot
   arrives in the engine's result envelope on every forge-touching operation (Section 9.7,
   `VCSX-CONTRACT.md`), that **recording it is Core**, and that acting on it is an OPTIONAL
   extension. Done-condition: the two halves are separated in the text, each with its requirement
   level stated.

2. **New section — why recording is Core.** Ensure the text argues it from cost: the figure arrives
   unbidden with a call Symphony already made, so a deployment that discards it has thrown away the
   only evidence that would explain a drain afterwards and paid nothing for it. Done-condition: the
   requirement level is argued, not asserted.

3. **New section — the OPTIONAL guard.** Ensure the extension owns its configuration under a
   `forge_budget.*` namespace with `enabled` (Default: `false`), a warn threshold, and a floor below
   which a mutating call is not made; and that it states a pre-emptive check before a **mutating**
   call rather than only a dispatch gate, because the expensive moment for a forge budget is the
   write. Done-condition: the extension declares the layer profile it extends and Core requires none
   of its fields.

4. **New section — why not Section 8.9.** Ensure the text states that Section 8.9 governs the
   coding-agent provider's account — a different account, credential, and accounting unit — and
   inherits that section's own rule that one account's quota is never summed into another's; and
   that this section carries no staleness machinery because the figure arrives with the call that
   spent it rather than from a poller. Done-condition: a reader can tell why there is no
   `stale_after_ms` or `UNKNOWN` here.

5. **Awaiting — when Symphony dispatches it.** Ensure the text states that on `merge:checks_pending`
   Symphony dispatches `await_checks` with bounds it supplies, rather than looping itself, and that
   Symphony writes no loop of its own over an operation that already loops. Done-condition: exactly
   one bound governs the wait.

6. **Awaiting — the four outcomes.** Ensure each of `await_checks:ok`, `checks_failed`,
   `still_pending` and `budget_floor` has a stated disposition, with `still_pending` and
   `budget_floor` **parked** rather than retried or failed. Ensure the reasoning is stated: retry is
   wrong because Section 8.4's schedule is for transient failures and a running check is not
   failing — a retry re-enters a wait that exhausts the same bound and holds a worker slot each time
   — and failure is wrong because nothing failed. Done-condition: the disposition matches
   `token_budget_exceeded`'s, which is the closest analogue (an operator bound, reached).

7. **Awaiting — no new trigger vocabulary.** Ensure the text states that the engine's
   `await_checks:*` results are already action-policy-machine triggers (Section 9.12), so no
   `checks:*` trigger set is defined. Done-condition: no second spelling exists for an outcome the
   machine already carries.

8. **Section 9.10 — awaiting is not authority to merge.** Ensure the text states that a successful
   `await_checks` reports that the checks passed for the head **it** read, and that the merge still
   conditions on the head it reads itself (`expected_head`, Section 9.7) and re-verifies the
   pull-request identity (Section 9.10). Done-condition: an implementation cannot treat
   `await_checks:ok` as licensing an unconditioned merge.

9. **Configuration.** Ensure the await bounds are operator configuration under the existing `vcs.*`
   namespace, since they are engine invocation arguments Symphony supplies, and the guard's keys are
   under `forge_budget.*`. Ensure Section 6.4's cheat sheet carries both. Done-condition: every new
   key appears in the cheat sheet with its default.

10. **Sections 13.5, 14.2, 17, 18.** Ensure the recorded snapshot is named where session metrics are
    (Section 13.5); the park disposition appears in Section 14.2; the test matrix checks that a
    `still_pending` parks rather than retries, that the recorded snapshot survives to the run record,
    and that a successful await does not bypass the merge's head condition; and the checklist carries
    the Core recording half. Done-condition: each of steps 1, 6 and 8 has a check.

## Cross-cutting sync

Section 6.4 (step 9), Sections 17 and 18 (step 10). Section 19's Conformance Statement gains the
extension's enablement, as the other OPTIONAL extensions' do.

## Anchor changes

New anchors: the `forge_budget.*` configuration namespace and its keys; the `vcs.*` await-bound keys;
one new section title. No anchor is renamed or removed. Section numbering: the new section is added
after Section 8.10 so no existing section is renumbered.

## Status

Applied to `SPEC.md` (Sections 6.4, 8.11, 9.10, 13.5, 14.2, 17.4, 18.1, 18.2) and
`conformance/vocabulary.json`.

One application note: step 10's checks were first written into Section 17.9 (`Concurrency Stress`)
and moved to Section 17.4. They are deterministic and need no concurrency, so placing them in the
environment-dependent profile would have made a Core requirement checkable only under a profile that
MAY be skipped.
