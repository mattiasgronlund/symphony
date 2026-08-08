# Plan — 0059 A parked flow is `needs_caller` with the `intervention` need

## Scope

`VCSX-SPEC.md` Sections 5.2 "Actions", 5.5 "Escalation Binding", 8.2 "Result Envelope", 8.4 "Escalation
Payload", and 13.1 "Test Matrix". `conformance/vcsx/vocabulary.json` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follow the new `need` token.

No `VCSX-CONTRACT.md` edit: its Section 5.2 defines `park` at the same altitude this decision leaves it
("stop the flow and hold for intervention, without failing it"), and its Section 11 defers the invocation
envelope, exit codes and escalation payload to `VCSX-SPEC.md` — which is the surface this decision
changes. Its Section 5.6 claim that `escalate` is the single point of front-end divergence stays true,
and Step 2 is what keeps it true.

No `SPEC.md` edit: Symphony "names the machine's vocabulary and defers its schema to the engine
contract", and its vocabulary summary carries the actions and the proto classes but not the invocation
statuses, the envelope fields, or the `need` vocabulary — `usage_or_config` does not appear in it either.

No vector change: `exit_code_for_status` maps a status to a code and `park` adds no status, so no
existing vector file has a slot for this. Asserting the parked envelope would need a new function over
terminal policy actions, which cannot be authored while `fail`'s envelope is unspecified (see "Out of
scope").

## Steps

1. **`park` states its invocation outcome.** Ensure Section 5.2's `park` bullet records that the
   invocation ends at `needs_caller` carrying the `intervention` need, cross-referencing Sections 8.2
   and 8.4, in the one-line bullet shape its neighbours use (compare the `escalate` bullet's
   "(Section 5.5)"). Done when the action list answers what a park returns without the reader
   consulting Section 8.
2. **Section 5.5 keeps its single-divergence-point claim true.** Ensure Section 5.5 records, after
   "`escalate` is the single point at which their behavior legitimately differs", that `park` also ends
   an invocation at `needs_caller` and is not a second divergence point, because `intervention` names a
   hold rather than a request: no resolver is bound and neither front-end resumes. Done when a reader
   who has just learned that a park escalates cannot conclude that a driver may resolve one.
3. **`status` covers a parked flow.** Ensure Section 8.2's `status` bullet states that a flow the policy
   stopped with `park` (Section 5.2) is `needs_caller`, with the elimination that gets there — not `ok`
   because the entry's intended effect was not reached, not `error` because `park` does not fail the
   flow. Done when each of the four statuses has at least one stated condition and a parked flow matches
   exactly one.
4. **`class` agrees with `status`, and a parked flow has no decisive result.** Ensure Section 8.2's
   `op` / `reason` / `class` bullet states that where the three are non-null, `class` is the class
   `status` reports (`done` under `ok`, the same token under `needs_caller` and `error`), and that all
   three are null where the run has no decisive operation result — a clean `ok` with no operation, and a
   parked flow, which the policy stopped rather than an operation. Keep the existing `usage_or_config`
   sentence. Done when the parked envelope is derivable from the bullet rather than argued from it.
5. **The escalation rule stays total.** Ensure Section 8.2's `escalation` bullet still reads as "present
   exactly when `status == "needs_caller"`" and records that a parked flow is included. Done when the
   rule has no exception to enumerate.
6. **`intervention` joins the `need` vocabulary.** Ensure Section 8.4 lists `intervention` among the
   named `need` tokens and states what separates it: it is raised by `park`, it names a hold rather than
   a request, a front-end MUST NOT bind a resolver to it and MUST NOT resume the flow on it, and the hold
   is released out of band by a new invocation. Done when a front-end author can implement resolver
   binding from Section 8.4 alone and get the parked case right.
7. **Escalation's `op` is nullable.** Ensure Section 8.4 states that the `op` that produced the
   escalation is null where no operation produced it, naming the two cases — at a signal, and at a
   lifecycle position, where the gated operation has not run (Section 5.1). Done when every trigger kind
   an `escalate` or `park` edge can be written on has a stated `op` value.
8. **The test matrix covers the parked envelope.** Ensure Section 13.1's `Invocation contract` bullet
   includes that a parked flow is `needs_caller` with the `intervention` need and null
   `op`/`reason`/`class`, alongside the existing "escalation is present exactly for `needs_caller`"
   check. Done when the behavior this decision fixes is a testable line in the matrix.
9. **The vocabulary registry carries the token.** Ensure `conformance/vcsx/vocabulary.json`'s `needs`
   group contains `intervention` and records, per entry, the action that raises the need (`escalate` or
   `park`) and whether a front-end resolves it — the properties Section 8.4 now fixes, in the shape the
   `actions` group's `effected_by` already uses. Done when the registry distinguishes `intervention` from
   the other four by data rather than by prose.
10. **The Conformance Statement template has a row for it.** Ensure
    `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s "`need` Vocabulary Emitted" table lists `intervention`
    alongside the four registry-named needs, and that its "Emitted by" column admits an action and not
    only an `op` or a position. Done when an engine filling in the template records `intervention`
    without needing the `<other>` row.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 9) and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 10).
Section 8.5 needs no edit: it already makes the `need` vocabulary major-stable while permitting a `MINOR`
to introduce new `need` tokens, which is exactly what `intervention` is. Section 8.3 needs no edit: a
parked flow is `needs_caller`, so it takes exit `10` through the existing mapping. Section 13.2's
checklist already carries "The invocation contract: result envelope, exit codes, escalation payload".

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` (the config cheat sheet, test matrix, and
implementation checklist) are not touched: this decision changes `VCSX-SPEC.md`, whose counterparts are
Sections 13.1 and 13.2, handled in Step 8.

## Anchor changes

None. `intervention` is a new `need` token; no existing anchor is renamed or removed.

## Out of scope

- **`fail`'s envelope.** An explicit `do = "fail"` on a `done`-class trigger yields `status == "error"`
  with no `error`-class result to report, the mirror image of the parked case. Settling it needs a prior
  answer to what `fail(reason)`'s argument is — a Section 4.3 reason token, a Section 6.10 configuration
  reason, or free text — which Section 5.2 does not say. The class-agreement invariant added in Step 4
  constrains the answer without picking it. Recorded here and in `DECISIONS.md` rather than resolved.
- **Issue #4's bounded traversal.** A budget exhausted after `push:ok` ends a flow with nothing decisive
  to report, so it lands on the invariant this decision states, but what bounds a traversal and what
  status an exhausted bound carries are its own questions.
- **A behavior vector for the parked envelope.** Deferred with `fail`'s envelope: a `terminal_envelope`
  function that covered `park` and `escalate` but not `fail` would ship a corpus function with a known
  hole in it.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.2, 5.5, 8.2, 8.4, 13.1), `conformance/vcsx/vocabulary.json`, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
