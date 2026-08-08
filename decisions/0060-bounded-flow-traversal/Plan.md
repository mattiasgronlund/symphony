# Plan — 0060 A conforming executor bounds the flow, and an exhausted bound is `needs_caller`

## Scope

`VCSX-SPEC.md`: a new Section 5.6 "Flow Bound and Termination" appended to the action-policy machine,
plus edits to Sections 8.2 "Result Envelope", 8.4 "Escalation Payload", 12.2 "`ship` Sequence", 13.1
"Test Matrix", 13.2 "Implementation Checklist", and 13.3 "Conformance Statement".
`conformance/vcsx/vocabulary.json` and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follow the new `need`
token and the new `Implementation-defined` value.

A new subsection at the end of Section 5 renumbers nothing: Section 5.6 is free, and Sections 6 onward
are unaffected.

No `VCSX-CONTRACT.md` edit: it enumerates no `need` tokens, defers "the engine invocation contract
(result envelope, exit codes, escalation payload)" and "the engine's internal algorithms" to
`VCSX-SPEC.md` (its Section 11), and its Section 5.4 "Unmatched Policy" states the fail-safe rule this
decision does not touch. The bound is an internal algorithm whose outcome is invocation-contract
surface, and both are on the deferred side of that line.

No `SPEC.md` edit: Symphony "names the machine's vocabulary and defers its schema to the engine
contract" (its Section 9.12), and its summary carries the triggers, actions, classes, matching ladder,
unmatched-policy rules and abstract `escalate` — not the invocation statuses, the envelope fields, or
the `need` vocabulary. The bound is neither a trigger nor an action, so it adds no vocabulary to
mirror. Its `Engine Invocation Failures` class (Section 12.1) already carves out "only failures in which
the policy never ran", so an exhausted flow correctly falls to the action-policy machine instead.

No vector change: the corpus asserts pure functions over their inputs, and a flow bound is a property of
a traversal over a policy and a sequence of operation results, which is the "front-end sequences" bucket
`conformance/vcsx/README.md` already defers as needing a real repository and forge. `exit_code_for_status`
gains no vector because the decision adds no invocation status.

## Steps

1. **Section 5 gains a termination subsection.** Ensure `VCSX-SPEC.md` carries a subsection titled
   `Flow Bound and Termination`, numbered 5.6, after `Escalation Binding`. Done when Section 5 answers
   whether an executor may run forever without the reader consulting Section 12.
2. **`run_op` is named as the only re-entering action.** Ensure Section 5.6 records why a count of
   `run_op` dispatches bounds every loop the schema can express: `run` reaches the machine through the
   gated operation's reason (`<op>:blocked` / `<op>:failed`, Section 6.6) and an `after`/result-triggered
   hook does not block; `create_task`, `set_state` and `notify` are consumer-effected intents emitted
   once; `escalate`, `park` and `fail` are terminal. Done when the choice of unit is derivable from the
   action list rather than asserted.
3. **The bound is REQUIRED, its value is `Implementation-defined`, and it has a floor.** Ensure Section
   5.6 states that a conforming executor MUST bound one invocation's flow by a count of `run_op`
   dispatches; that the value is `Implementation-defined` and MUST be documented (Section 13.3); and
   that it MUST admit at least 64 dispatches, with the floor's purpose recorded — a policy portable
   between two engines is not cut short by the stricter of the two. Ensure a configurable bound is held
   to the same floor. Done when two engines can be checked for agreement on any policy that terminates
   within 64 dispatches.
4. **A count, not a cycle detector.** Ensure Section 5.6 states that the bound is a count and that a
   repeated `(trigger, edge)` pair is ordinary rather than pathological, naming
   `push:non_fast_forward → integrate → push` (Section 12.2) as the built-in routing a base branch that
   moved twice produces twice. Done when an implementer cannot read Section 5.6 as licensing a static or
   runtime cycle check.
5. **Exhaustion has one stated outcome.** Ensure Section 5.6 states that a flow reaching its bound ends
   the invocation at `needs_caller` carrying the `flow_exhausted` need (Sections 8.2, 8.4), that the
   pending `run_op` is not dispatched and the operations already run stand, and that it is a hold rather
   than a request. Done when the exit code of an exhausted flow is the same on any conforming engine.
6. **Further bounds share the disposition.** Ensure Section 5.6 states that an engine MAY impose further
   bounds — a wall-clock deadline, for example — that a flow stopped by any of them reaches the same
   result, and that each imposed bound MUST be documented (Section 13.3). Done when the envelope does
   not reveal which bound fired.
7. **`status` covers an exhausted flow.** Ensure Section 8.2's `status` bullet states that a flow the
   executor stopped at its bound (Section 5.6) is `needs_caller`, on the reasoning already applied to a
   parked flow: the entry's intended effect was not reached, and no operation failed — the executor
   declined to dispatch the next one. Done when each of the four statuses has at least one stated
   condition and an exhausted flow matches exactly one.
8. **The null triple admits the third case.** Ensure Section 8.2's `op` / `reason` / `class` bullet lists
   a flow stopped at its bound alongside a clean `ok` with no operation and a parked flow as the cases
   where all three are null, keeping the existing statement that `class` is the class `status` reports
   where they are non-null. Done when the exhausted envelope follows from the bullet rather than being
   asserted elsewhere.
9. **The escalation rule stays total.** Ensure Section 8.2's `escalation` bullet still reads as "present
   exactly when `status == "needs_caller"`" and names the exhausted flow alongside the parked one as
   included. Done when the rule has no exception to enumerate.
10. **`flow_exhausted` joins the `need` vocabulary.** Ensure Section 8.4 lists `flow_exhausted` among the
    named `need` tokens and restates the hold rule over the pair: `intervention` and `flow_exhausted`
    name a hold rather than a request, a front-end MUST NOT bind a resolver to either and MUST NOT
    resume the flow on either, and each hold is released out of band by a new invocation. Ensure what
    separates them is stated — the policy asked for a park; the executor imposed a bound. Done when a
    front-end author can implement resolver binding from Section 8.4 alone and get both holds right.
11. **Escalation's `op` covers the bound.** Ensure Section 8.4's nullable-`op` sentence names the bound
    alongside the signal and the lifecycle position as a case where no operation produced the
    escalation. Done when every way an escalation can arise has a stated `op` value.
12. **Section 12.2's loop is visibly bounded.** Ensure the `ship` pseudocode guards its `loop:` against
    the flow bound and returns the exhausted result, and that the prose after the block records that the
    bound is not the loop's own step count — every `run_op` counts against it wherever it is dispatched,
    so a `push`/`integrate` pair that never converges ends at `needs_caller` with `flow_exhausted`. Done
    when the algorithm the issue quotes no longer reads as unbounded.
13. **The test matrix covers termination.** Ensure Section 13.1 carries a `Termination` check: a policy
    whose `run_op` results route back to an earlier operation stops at the flow bound and yields
    `needs_caller` with the `flow_exhausted` need and null `op`/`reason`/`class`, while a flow that
    converges within the bound is unaffected. Done when the behavior this decision fixes is a testable
    line in the matrix.
14. **The checklist names the bound.** Ensure Section 13.2's action-policy-machine bullet lists a bounded
    flow alongside the `#class` fallback, fail-safe-on-unmatched-outcome, no-op-on-unmatched-signal and
    determinism. Done when the definition of done includes termination.
15. **The Conformance Statement publishes the bound.** Ensure Section 13.3's enumeration of
    `Implementation-defined` behaviors includes the flow bound's value and any further bound the engine
    imposes (Section 5.6), in the section order the list already uses. Done when a consumer can read an
    engine's bound without reading its source.
16. **The vocabulary registry carries the token.** Ensure `conformance/vcsx/vocabulary.json`'s `needs`
    group contains `flow_exhausted` with `resolvable: false`, and that the group's `raised_by` note
    admits a raiser that is not an action, since the executor raises this one and no policy can write
    it. Done when the registry distinguishes the two holds from the three requests by data.
17. **The Conformance Statement template has rows for both.** Ensure
    `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` lists the flow bound in its `Implementation-defined`
    resolutions table (Section 5.6, in section order) and `flow_exhausted` in its "`need` Vocabulary
    Emitted" table, that the table's "Emitted by" column admits a bound, and that the note below it
    covers both unresolvable needs. Done when an engine filling in the template records both without
    needing the `<other>` row.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 16) and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 17).

Section 8.3 needs no edit: an exhausted flow is `needs_caller`, so it takes exit `10` through the
existing mapping, which is the point of choosing an existing status. Section 8.5 needs no edit: it
already makes the `need` vocabulary major-stable while permitting a `MINOR` to introduce new `need`
tokens. Section 6.10 needs no edit: non-termination is not statically detectable, so no configuration
reason is added.

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` (the config cheat sheet, test matrix, and
implementation checklist) are not touched: this decision changes `VCSX-SPEC.md`, whose counterparts are
Sections 13.1 and 13.2, handled in Steps 13 and 14.

## Anchor changes

None removed or renamed. Added: Section 5.6 "Flow Bound and Termination" (a new section title) and the
`flow_exhausted` `need` token.

Decision 0059's Section 8.4 phrasing "the one need no front-end resolves" is widened to cover two needs.
The `intervention` token, its meaning, and its MUST NOT are unchanged; only the claim of uniqueness is.

## Out of scope

- **A repository-configurable bound** (`[engine] max_operations` or similar). The bound doubles as the
  only cap on `push`/`integrate` retries, and retry appetite is repository-dependent, but that is a
  retry-policy question rather than the termination question issue #4 asks. Recorded in `Background.md`
  as the surface it would land on.
- **`fail`'s envelope.** Still open from decision 0059: an explicit `do = "fail"` on a `done`-class
  trigger yields `status == "error"` with no `error`-class result to report, and settling it needs a
  prior answer to what `fail(reason)`'s argument is.
- **A behavior vector for the exhausted envelope.** A flow bound is a property of a traversal, not a
  pure function over vector inputs; it belongs with the front-end sequences `conformance/vcsx/README.md`
  already defers.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.6, 8.2, 8.4, 12.2, 13.1, 13.2, 13.3),
`conformance/vcsx/vocabulary.json`, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
