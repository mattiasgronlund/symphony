# Plan — 0112 The wait becomes an operation, and the non-goal it tests gets written down

## Scope

`VCSX-SPEC.md`: Section 2.2 "Non-Goals" (the unwritten boundary, and the bounded exception), Section
4.1 "Operation Set" (`await_checks`), Section 4.3 "Reason-Token Registry" (four reasons), Section 7
"Front-Ends" (`land --await`), Section 8.1 (the four arguments and the entry point), Section 9.2
(`checks_state`), Sections 5.6, 13.1, 13.2, 13.3.

`VCSX-CONTRACT.md`: Section 3 "Executor and Front-Ends" (the entry point) and Section 6 "Engine
Operations and Typed Results" (the operation). Both are names the two documents share, so this is a
contract change under its Section 12.

`conformance/vcsx/vocabulary.json`: the operation, the entry point, and the four reasons with their
classes and default needs.

## Steps

1. **Section 2.2 — the non-goal that was assumed.** Ensure Non-Goals states that deciding when to
   retry, how long to back off, and what a budget is worth are the consumer's. Done-condition: the
   claim 0107 and 0109 cite is readable in the section they cite.

2. **Section 2.2 — the bounded exception.** Ensure the same entry states that `await_checks`
   (Section 4.1) executes a wait the consumer parameterizes and decides none of the three, so the
   non-goal bounds what the engine *decides* rather than whether it ever waits. Done-condition: a
   reader can tell why a bounded poll loop is not a repeal of the bullet above it.

3. **Section 9.2 — `checks_state`.** Ensure the capability exists with the four answers decision
   0106 fixed for `pr_state`: the aggregate state of the pull request's required checks, none where
   the forge reports none required, `unchanged` against a presented validator, or undetermined —
   with the same prohibition on answering `unchanged` without having asked. Done-condition: check
   state is readable without dispatching a `merge`.

4. **Section 4.1 — the operation.** Ensure `await_checks` is in the operation set, gated at no fixed
   lifecycle position (the category `integrate` and `pull` occupy), described as reading
   `checks_state` until one of its four terminal conditions holds. Ensure it is marked Read-only
   against the three things Section 4.1 quantifies that term over. Done-condition: no lifecycle
   position is implied for it and the entry states what ends the loop.

5. **Section 5.6 — one dispatch.** Ensure the flow bound's text states that `await_checks` counts as
   one `run_op` dispatch however many reads it makes, its reads being bounded by its own arguments.
   Done-condition: a policy's flow budget does not depend on how long a CI run took.

6. **Section 8.1 — the arguments.** Ensure four OPTIONAL arguments exist: an overall bound, a read
   count bound, a minimum interval between reads, and a budget floor naming a bucket and a minimum
   remaining. Ensure the text states they are the consumer's on the same footing as the access
   parameters, that the engine compares against numbers it was handed and chooses none, and that an
   invocation supplying none makes a single read rather than an unbounded loop. Done-condition: an
   `await_checks` with no arguments cannot loop.

7. **Section 8.1 — the entry point.** Ensure `await_checks` joins the entry-point list, and that
   `pr_state_validator`'s entry accounts for a second validated read. Done-condition: the entry
   list and the operation set agree.

8. **Section 7 — `land --await`.** Ensure `land`'s entry states the await composition — the
   `await_checks` operation followed by the `merge` it already runs — as a composition rather than a
   second mechanism. Done-condition: no new sequencing rule is introduced for it.

9. **Section 4.3 — the four reasons.** Ensure `await_checks:ok` (`done`), `checks_failed` (`error`),
   `still_pending` (`needs_caller`, default need `await_checks`) and `budget_floor`
   (`needs_caller`, default need `retry_after`) exist, and that prose states why the last two are
   separate: one is met by waiting longer and the other by waiting for a bucket to refill.
   Done-condition: a consumer can tell which bound it should raise.

10. **Section 4.3 — the shared name.** Ensure prose states that the `await_checks` need and the
    `await_checks` operation share a spelling deliberately, needs and operations being separate
    namespaces, so the need now names the operation that meets it. Done-condition: the collision
    reads as intended rather than as an error.

11. **`VCSX-CONTRACT.md`.** Ensure Section 3's entry points and Section 6's named operations carry
    `await_checks`, per its Section 12's rule that a token added here is a contract change reflected
    in both documents. Done-condition: no name exists in one document and not the other.

12. **Sections 13.1, 13.2, 13.3.** Ensure the test matrix checks that the loop exits at each of its
    four terminal conditions; that reads honour the interval floor; that a validator is presented on
    each read after the first; that `await_checks` counts once against the flow bound; and that an
    invocation supplying no bound makes exactly one read. Ensure the checklist and Conformance
    Statement account for the operation and its arguments. Done-condition: each of steps 4, 5, 6 and
    9 has a check that would fail if the step were reverted.

13. **`conformance/vcsx/vocabulary.json`.** Ensure `operations` carries `await_checks` with
    `lifecycle_position: null`, `entry_points` carries it as an operation, and `reasons` carries the
    four with their classes and default needs. Done-condition: the registry and Section 4.3 agree.

## Cross-cutting sync

No `repo.policy.toml` key changes: every argument is the consumer's. `SPEC.md` is untouched by this
decision — Symphony's use of the operation is the sibling decision on the orchestrator side.

## Anchor changes

New anchors: operation and entry point `await_checks`; reasons `await_checks:ok`,
`await_checks:checks_failed`, `await_checks:still_pending`, `await_checks:budget_floor`; forge
capability `checks_state`; four invocation arguments; the `land` await argument. No anchor is renamed
or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 2.2, 4.1, 4.3, 5.6, 7.2, 8.1, 9.2, 13.1, 13.2),
`VCSX-CONTRACT.md` (Sections 3, 6) and `conformance/vcsx/vocabulary.json`.

Application widened one anchor beyond this plan: `await_checks` is a forge-touching operation, so
Section 4.3's `(any forge)` scope — written by decision 0108 as `push`, `create_pr` and `merge` —
gains it, and the registry gains the two transient reasons for it.
