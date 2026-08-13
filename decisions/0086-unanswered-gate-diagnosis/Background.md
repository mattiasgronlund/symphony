# Background — 0086 An unanswered gate's condition is named, and the three conditions are tokens

## Context

Resolves issue #42. Decision 0081 gave a hook a bound and split what exceeding it produces into a
routing half and a diagnosis half. The routing half is `<op>:hook_unanswered`, a Section 4.3 reason
with a fixed class. The diagnosis half is which of three conditions occurred — the bound elapsed, the
unit could not be started, or its answer could not be read — and Section 4.3 sends it to `outputs`:

> Which of the three conditions produced `hook_unanswered` is diagnosis rather than routing, and is
> reported in `outputs` (Section 8.2) rather than in a token, because the repair is the same shape in
> each case.

Section 8.2 then does that for one half of Section 6.6's division and not the other. The non-gating
half gets a name, a field list and an absent-or-empty rule — `unfinished_hooks`, "each naming the
hook, the trigger that ran it, and which condition occurred". The gating half gets a clause:

> a `before:*` hook is not reported there, because the gated operation reports it as that reason
> (Section 4.3), and `outputs` carries which condition occurred for it too, since the reason routes
> and the condition diagnoses.

**That sentence names no key, no shape and no field**, while requiring the report. It is the only
fact in Section 8.2 that is REQUIRED and unnamed: `unperformed_intents` and `unfinished_hooks` are
both named, shaped and given an absent-or-empty rule, and Section 8.5 makes the envelope's fields
major-stable.

## What the defect does

A consumer that wants to tell a gate that hung from a unit that is not there — a genuinely different
repair, which is why 0081 kept all three conditions reportable rather than collapsing them — must
read a key whose name it cannot know. Two engines both satisfy the sentence, put the condition in
different keys, and neither's consumer reads the other's. The failure is silent in the direction that
matters: the consumer finds no key, concludes no gate failed, and reports a run whose diagnosis it
never saw.

The report was found implementing Sections 6.6, 4.3 and 8.2 against `b9310967` — the first slice that
reports an unanswered hook rather than ending the invocation outside the envelope.

There is a second level to it, and it is the one the issue's second ask names. The three conditions
are **prose** in both Section 6.6 and Section 8.2 — "the bound elapsed, the unit could not be
started, or its answer could not be read". So `unfinished_hooks`, which has a named key and a named
`condition` field, carries values every engine invents. Naming the gating half's key alone would move
the defect one field deeper rather than closing it: the consumer's branch would still be over strings
no registry fixes.

## Why this is decision 0081's own argument one level below a token

0081 refused to let each engine mint its own reason for a bounded hook, on the reasoning that "the
token would be chosen independently by every engine" — the same reasoning that kept issue #2 waiting.
A key in `outputs` is in exactly that position now, and so are the condition values inside it. What
0081 settled was *whether* the three conditions are reportable; what it left is *how they are
spelled*, and the second question is the one a consumer's code is written against.

The asymmetry also reads as an oversight rather than a choice. The review that landed on issue #35
noticed that the `after` half covered one condition where the gate half covered three, and widened
both to "gave the engine no usable answer". That pass equalized *which* conditions are reported and
left *where* asymmetric — which is the shape of an edit that did not finish, not of a decision.

## Options

**A — Name `unanswered_gates`, and fix the three condition tokens for both halves (chosen).**
`outputs.unanswered_gates`, an array, each entry naming the `hook`, the `position` that ran it, the
`condition`, and an `Implementation-defined` `detail`; absent or empty where every gate answered. The
conditions become three tokens — `bound_elapsed`, `not_started`, `answer_unreadable` — defined once in
Section 6.6 and used by `unanswered_gates` and `unfinished_hooks` alike.

An array rather than a single entry because the result re-enters the machine: a repository binding
`commit:hook_unanswered` to anything that does not end the flow can reach `before:push` on the same
traversal, and Section 5.6 defends exactly that routing rather than refusing it.

**B — One key for both halves (rejected).** Widen `unfinished_hooks` to every hook that gave the
engine no usable answer, gating and non-gating, distinguished by a field. In its own terms this is
the better shape for a consumer that asks "which hooks broke": one array, one branch, no
join. It loses on what the existing key means. `unfinished_hooks` is today exactly the set nothing
else reports — Section 8.2 calls it "the non-gating half's mirror of `hook_unanswered`" — and a gate's
failure is already carried by a routed reason a repository can bind. Widening it makes the key a
superset whose gating members duplicate a reason the envelope states in `reason`, so a consumer that
read it as "the failures that were not routed" starts filtering, and the property that made the key
worth naming is gone. The split the document draws is real: one half is routed and diagnosed, the
other is only reported.

**C — `Implementation-defined`, documented under Section 13.3 (rejected).** One sentence, no new
surface, and it makes the fact findable rather than guessable — which is more than the document
manages today, and is the honest minimum. It loses because it concedes at the `outputs` level exactly
what 0081 refused at the token level, on a surface Section 8.5 calls major-stable, and because the
Conformance Statement is where a *choice* is recorded rather than where a shared fact is defined. A
consumer reading two engines' Statements to learn two spellings of one condition is doing the work the
registry exists to remove.

## Verification

- The claim that `entry`-style field lists exist for the two neighbours and not for the gating half
  was checked against `VCSX-SPEC.md` at `e00ebb1`: Section 8.2's `outputs` bullet names
  `unperformed_intents` and `unfinished_hooks` with their fields and their absent-or-empty rules, and
  carries the gating half in the trailing clause quoted above with no key.
- The claim that the three conditions are nowhere tokenized was checked by searching the document for
  each candidate spelling: `bound_elapsed`, `not_started` and `answer_unreadable` appear nowhere in
  `VCSX-SPEC.md`, `VCSX-CONTRACT.md` or `conformance/vcsx/vocabulary.json` at `e00ebb1`.
- `conformance/vcsx/vocabulary.json` at `e00ebb1` carries no `output_keys` group at all: its
  `envelope_fields` entry is a flat list of the nine envelope field names, and the keys inside
  `outputs` are in no registry. Adding the group is therefore new surface rather than an edit to an
  existing one.

## Reconsideration trigger

Reopen if a second key inside `outputs` is added whose members overlap `unanswered_gates` — a report
of every hook the engine ran, say, rather than only those that failed. At that point the two-key split
starts costing a join for a consumer that wants one view of hook health, and option B's argument
becomes stronger than the "mirror of `hook_unanswered`" property that defeats it here.

Reopen also if a fourth condition appears. The three are exhaustive over *how the engine failed to get
an answer*, and a fourth would mean the division in Section 6.6 is over something else — at which
point whether the condition belongs in `outputs` at all is back on the table, not just its spelling.

## Relates to

0081 (the bound and the routing/diagnosis split this completes), 0071 and 0051 (the token vocabulary
as data, which the new tokens join), 0059 (the envelope invariants the new key is stated against).
