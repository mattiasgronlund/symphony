# Plan — 0087 A resume re-enters the point that raised the need, and re-reads

## Scope

`VCSX-SPEC.md`: Sections 5.5 "Escalation Binding", 5.6 "Flow Bound and Termination", 8.4 "Escalation
Payload", 13.1 "Test Matrix", 13.2 "Implementation Checklist".

No `VCSX-CONTRACT.md` change: `VCSX-CONTRACT.md` Section 5.6 states that the front-end binds the
resolver and does not describe a resume, so no token or clause it carries is affected.

## Steps

1. **The resume point (Section 5.5)** — ensure the section states where a resumed flow carries on:
   a resume re-enters the point that raised the need. Where an operation result raised it, the resume
   re-dispatches that operation, which runs its `before:<op>` position first as any dispatch does
   (Section 5.2); where an edge at a lifecycle position raised it — the escalation whose `op` is null
   (Section 8.4) — the resume re-enters that position. Ensure the paragraph states that a gate is
   therefore re-run rather than bypassed, and that this holds identically for `<op>:blocked` and
   `<op>:hook_unanswered`, so neither yields a pass the hook did not give (Section 6.6).
   *Done when* Section 5.5 names the resume point for both shapes and states the gate is re-run.

2. **A resume re-reads (Section 5.5)** — ensure the section states that nothing a position established
   carries across a resume: the state a position inspected is read again, so an operation conditioned
   on an inspected identity — `expected_worktree`, `expected_head` (Section 6.6) — is conditioned on
   what the re-entered position saw. Ensure the prose names the failure it forecloses: an engine
   carrying the earlier expectation forward hands an operation state no position has inspected since,
   which is the condition Sections 4.3 and 6.6 exist to report rather than to produce.
   *Done when* the re-read requirement is stated over the position's reads and names both identities.

3. **Re-entry counts against the bound (Section 5.5)** — ensure the section states that any re-entry a
   resume causes counts against the flow bound (Section 5.6), quantified over **re-entry** rather than
   over dispatch, because a resume into a lifecycle position re-enters a position inside a dispatch
   whose count is already spent. Ensure the prose states the consequence: both shapes converge on
   `flow_exhausted` rather than looping where a resolver always resolves.
   *Done when* the clause is stated over re-entry and names `flow_exhausted` as where an
   always-resolving resolver ends.

4. **The bound admits the second re-entry (Section 5.6)** — ensure the ending-actions bullet no longer
   reads as though `escalate` unconditionally ends the invocation: `escalate`, `park` and `fail` end
   the flow, and a front-end that resumes an `escalate` (Section 5.5) re-enters at the point that
   raised the need. Ensure the paragraph that derives the bound counts resume re-entries alongside
   `run_op` dispatches, and ensure the normative sentence bounding an invocation's flow is stated over
   both. *Done when* Section 5.6's bound is a count of `run_op` dispatches **and** resume re-entries,
   and the ending-actions bullet names the resume exception.

5. **A default-raised need is resolvable (Section 8.4)** — ensure the section states that a need the
   built-in default raised (Section 5.4) is resolvable like one an `escalate` action named, and carries
   the reason's default need (Section 4.3); only the two holds are unresolvable. This closes the
   related edge the report offers: Section 8.4 names two needs no front-end may resume and says nothing
   about a need a front-end **may** resume that no `escalate` action named, which is every need the
   built-in default produces.
   *Done when* Section 8.4 states that a default-raised need is resolvable and cites Section 4.3 for
   which need it is.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Front-ends" — a resumed escalation re-enters the point that
  raised the need: an operation-result escalation re-dispatches the operation and re-runs its position,
  and a lifecycle-position escalation re-enters the position; the position's reads happen again, so an
  operation conditioned on an inspected identity is conditioned on the re-read one rather than on the
  identity taken before the escalation; every re-entry counts against the flow bound, so a resolver
  that always resolves ends at `needs_caller` with the `flow_exhausted` need rather than looping.
- **Implementation checklist (Section 13.2)** — extend the action-policy-machine line so the bounded
  flow covers resume re-entries, and the front-end line so the resume point is part of the
  embedded-driver contract.
- **Conformance Statement (Section 13.3)** — no new row: the resume point and the re-read are fixed
  rather than `Implementation-defined`, and the bound's value is already enumerated there
  (Section 5.6).
- **`conformance/vcsx/vocabulary.json`** — no new token. The `needs` group's `resolvable` field
  already distinguishes the two holds from every other need, and this decision changes what resolving
  one does rather than which are resolvable.

## Anchor changes

None. No code token is added, renamed or removed; Sections 5.5, 5.6 and 8.4 keep their titles.

## Status

Applied to `VCSX-SPEC.md`.
