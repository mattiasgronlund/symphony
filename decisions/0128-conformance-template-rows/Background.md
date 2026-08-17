# Background — 0128 A table that is complete against itself is where a missing obligation hides

## Context

Issue #67, filed by a downstream implementation while re-pinning from `4fbf183` to `170b8af`.
Decisions 0106, 0107 and 0109 each added an `Implementation-defined` answer to `VCSX-SPEC.md` Section
13.3's list of what a Conformance Statement MUST record, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`
Section 3 gained a row for none of them:

- the default `network_bound_ms` and any per-capability values the engine applies (Sections 8.1, 9);
- where a forge backend declares conditional-read support, the mechanism it realizes the validator
  with (Section 9.2);
- which budget buckets each forge backend observes and where it reads them from (Section 9.2).

Verified against the artifact rather than taken from the report: Section 3's table carries sixteen
rows and none of the three, while every other obligation on Section 13.3's bullet list has one — the
flow bound, the hook bound, the `forge_parameters` keys, where a backend writes bookkeeping state, and
the rest.

## What the defect does, in the reporter's terms

The two documents have different readers, and that is what makes the gap silent.

Section 13.3 is prose an implementer reads once. The template's Section 3 table is what a **generator**
reads. The reporting implementation's `xtask statement` parses that table, requires an answer for every
row it finds, and fails the build on a row left unresolved — which is the mechanism that keeps a
published Statement from going stale.

So an engine that implements conditional reads, the budget snapshot and the network bound, and
generates its Statement from the template, publishes a Statement silent about all three, and every
check designed to catch that silence reports green — because the table is complete against itself. The
document a consumer was told to rely on is the one place the omission lands.

That argument is the report's and it is correct. It is worth recording that this is a defect in the
*repository's own release discipline* rather than in either document's content: three decisions each
edited Section 13.3 and none edited the table that mirrors it, so the failure is that the two are
synchronized by hand with nothing checking.

## Why it is a decision rather than a sync

The repository's rule is that reasoning is captured before a spec change, and the temptation here is
to treat missing rows as bookkeeping. Two things make that wrong.

The rows are not mechanical. The conditional-read row applies only to a backend that declares the
support, and no other per-backend row in the table carries a condition — so the row's shape is a
question the report raises explicitly and does not settle. And after decisions 0123 and 0124 the same
bullet list carries two more answers, one of which (the validator mechanism) is the very row being
added, now covering two validators rather than one. A row written for `pr_state` alone would be wrong
within this same pull request.

## Decision

Add the three rows the report names, plus the two this batch introduces, and state the condition on a
conditional row explicitly in the resolution column rather than in a new column.

`not supported` as a resolution reads correctly for a backend that declares nothing, and it keeps the
table's shape — one obligation, one section, one resolution — which is what the generator parses. A
condition column would be a schema change to a table other implementations already parse, for one row.

The validator row is written over **both** validators (decision 0124), and the resume token's form
joins as its own row (decision 0123).

## The recurrence, which is the more useful finding

This is the second time the same shape has been recorded: a change that edits a normative list and
not the artifact that mirrors it. `CLAUDE.md`'s working agreements already name the cross-cutting
sections that must stay in sync after a substantive change — "the config cheat sheet (Section 6.4),
test matrix (Section 17), and implementation checklist (Section 18)" — and that list is `SPEC.md`'s.
Neither `VCSX-SPEC.md` Section 13.3 nor the two Conformance Statement templates are on it, which is
why three decisions in a row could each miss the same table without anything catching it.

Extending that list is the repair that stops the recurrence, and it is in scope here because the
alternative is to fix the rows and leave the mechanism that dropped them.

## Options considered

**Fix the rows and stop.** Steelmanned: it closes the reported gap, it is the smallest change, and the
list in `CLAUDE.md` is guidance rather than a checked artifact, so extending it may catch nothing. It
loses on the evidence in front of us — three decisions missed the same table, and the guidance an
agent reads at the start of a session is the only thing in this repository that would have caught it,
`scripts/validate_workflow_bundle.py` validating the workflow bundle's scaffolding rather than the
spec.

**Make the template generated from Section 13.3.** Steelmanned: it removes the hand-synchronization
entirely and is the only repair that cannot regress. It loses on scope and on ownership — the template
is a RECOMMENDED shape a downstream generator parses, and turning it into a build artifact of this
repository is a tooling decision with its own consequences for the implementations that already
consume it. Recorded as the reconsideration trigger rather than taken.

## Reconsideration trigger

Reconsider generating the template from Section 13.3 if a fourth decision lands a Section 13.3
obligation without its row. Two more data points and the hand-sync is demonstrably not holding, at
which point the tooling cost is the cheaper side.

## Relationship to other decisions

It repairs the release discipline of 0106, 0107 and 0109 rather than their content, and carries the
template rows for 0123 and 0124 in the same pass so this pull request does not reproduce the defect it
is fixing.
