# Background — 0127 The section whose job is the vocabulary is the one where a missing member is the failure

## Context

Issue #75. `SPEC.md` Section 9.12 opens by fixing its own job — "This specification names the
machine's vocabulary and defers its schema to the engine contract (`VCSX-CONTRACT.md`)" — and then
names a vocabulary with members missing.

Its typed-result bullet says the operations are `commit`, `integrate`, `push`, `create_pr` and
`merge`. `VCSX-SPEC.md` Section 4.1 defines eleven. And its trigger list names task-state events
only, while its own unmatched-policy bullet three lines below names "an agent milestone or task-state
event".

## What the defect does

Section 9.10, four pages earlier in the same document, instructs a repository to bind a trigger
Section 9.12 does not list:

> No `checks:*` trigger vocabulary is defined. The engine's outcomes are `<op>:<reason>` results, so
> the action-policy machine (Section 9.12) already routes them through the same matching and `#class`
> fallback it applies to every other operation result, and **a repository binds `await_checks:*` as it
> binds `merge:*`**.

So a reader following the cross-reference lands on a list that does not contain the thing they were
sent to find, and concludes either that Section 9.10 names something undefined or that Section 9.12 is
not the vocabulary it says it is. Both readings are wrong and both are reasonable.

Two of the omissions are correct and must survive the repair. `provision` and `load_policy` raise no
`<op>:<reason>` trigger by construction — the edges that would route them are in the document they
exist to obtain — so a list that named them would be wrong in the other direction. That is what makes
this worth doing carefully rather than by replacing five names with eleven: the right list is nine,
and the two exclusions have a reason that should be stated where the list is, because a later reader
will otherwise "fix" it.

## Why an enumeration at all

The alternative reading is that Section 9.12 should not enumerate — it defers the schema, so it could
defer the operation set too and name only the trigger *kinds*.

That is tempting and it is wrong for this section, because naming the vocabulary is what Section 9.12
exists to do. `SPEC.md` Section 3.4 splits the two documents by having Symphony own orchestration
semantics and the engine own its schema; the machine's token vocabulary is what a Symphony reader
needs in order to follow Sections 9.10, 11.6 and 8.10, none of which would be readable if the
vocabulary lived only in the engine spec. An enumeration that is deferred is a section that has
stopped doing its job; an enumeration that is wrong is one that is doing it badly. The repair is to do
it correctly and to state the two exclusions, so the list is self-maintaining against the next
operation.

## The signal half is decision 0122's

`VCSX-SPEC.md` removes the signal trigger kind (decision 0122). That settles the second contradiction
by deletion rather than by reconciliation: Section 9.12's trigger list and its unmatched-policy bullet
both lose their signal clauses, and the milestone tokens survive in `SPEC.md` Section 11.6 as tracker
transition triggers, which is where they are actually evaluated.

This decision is therefore sequenced after 0122 and carries the `SPEC.md` half of it. Splitting them
that way keeps each document's change in the decision that argues for it: 0122 argues the removal from
the engine's side, and this one repairs the consumer document's vocabulary section, which was already
wrong about the operations before signals came into it.

## Options considered

**Fold this into 0122.** One decision covering both documents. Steelmanned: the signal half is a
single change across two documents and splitting it means two records for one edit. It loses because
the operation-list half is independent — it was wrong before 0122 and would be wrong if 0122 were
reversed — and a decision that bundles an independent defect with a dependent one leaves the
independent one with no record of its own to re-evaluate.

**Replace the enumeration with a cross-reference.** "The operations are those `VCSX-SPEC.md` Section
4.1 defines." Steelmanned: it cannot drift, which is the whole defect. It loses on what Section 9.12
is for, above, and on a smaller point that matters in practice — the two exclusions are Symphony-visible
facts (`provision` is the operation Section 9.7 dispatches and classifies itself), so a bare
cross-reference would send a reader to a list of eleven with no indication that two of them never
reach the machine.

## Reconsideration trigger

Reconsider the enumeration if the engine's operation set starts changing between releases. It is
enumerable here because Section 4.1's required set has been stable and additions are `MINOR` and rare;
a set that moved often would make this list drift again, and the cross-reference option would then be
the lesser evil.

## Relationship to other decisions

It depends on 0122 for the signal half and stands alone for the operation half. It changes no engine
surface: every token it adds to `SPEC.md` is one `VCSX-SPEC.md` Sections 4.1 and 4.3 already define.
