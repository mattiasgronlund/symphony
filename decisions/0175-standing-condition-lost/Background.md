# Background — 0175 A report the specification requires and does not name

## Context

Reported from `symphony-rs` as issue #153, against `5a4fdf7`, found while building the slice that
implements decision 0155 (their roadmap D2g) and recorded there as decision 0011 R86.

Section 8.5 Part B requires a report and fixes its shape by reference:

> A stop for a standing-condition loss is reported to the operator naming the condition that failed,
> in the shape Section 8.7 already uses for a reported routing ambiguity.

The shape is fixed. The token is not — not in Section 8.5, not in Section 8.7, and not in decision
0155.

## The mechanism

**A required report whose token is unfixed is the exact case Section 14.1 opens by ruling out.**

> The token spellings are REQUIRED: two implementations reporting the same condition MUST report the
> same token, so an operator or a Conformance Statement reader can compare them without knowing
> which implementation produced the record.

Two conforming implementations will report a lost `tracker.required_labels` under different tokens,
and both will be right.

**None of Section 14.1's nine describes it, because nothing failed.** The report's walk is correct
and class 5 is the cleanest disposal: `tracker_failures` names transport errors, non-200 status,
GraphQL errors and malformed payloads, and the refresh **succeeded** — that is how the loss was
observed at all. Classes 1 through 4 and 6 through 9 each name a component that failed, and here
none did. A required label was removed, an assignee reassigned, or a mapping edited, and the run is
being deliberately stopped because the conditions it was dispatched under stopped holding.

**The nearest candidate carries a disposition, and both of its dispositions are wrong.** This is the
finding that makes the gap worth a decision rather than a note, and it holds exactly as reported.
`workflow_config_failures` takes two dispositions in Section 14.2. Section 8.5 Part B says the
branch owing this report will "terminate the worker without workspace cleanup, release the claim,
and **schedule no retry**". Section 14.2's workflow-file disposition says "convert to a retry with
exponential backoff" — the direct opposite. Its operator-configuration disposition says "Skip new
dispatches", which read literally means a third party removing one label from one issue skips new
dispatches for every repository the instance manages.

`symphony-rs` reports that this does not bite their build, and is precise about why: their
standing-condition stop disposes of itself at the Section 8.5 site and never consults the
class-to-disposition table. They are right that this is their choice rather than something the text
forces — an implementation that routed the class through Section 14.2, which is what Section 14.2 is
for, would retry a stop Section 8.5 says not to retry and would conform to every sentence either
section contains.

**Section 14.2 already holds the answer, twice, and nobody looked there.** The issue offers three
readings and each presupposes the report carries a Section 14.1 class. There is a fourth position:

> An exhausted wait for required checks (`await_checks:still_pending`, `await_checks:budget_floor`;
> Sections 8.11, 9.10) is **parked**, not retried and not failed. **It is not a failure class**,
> being an operation result the action-policy machine routes (Section 9.12), and it is listed here
> **because its disposition is the one this section governs**.

A token, a disposition Section 14.2 states, and an explicit disclaimer that it is not a Section 14.1
class. `token_budget_exceeded` sits on the same footing. So the specification already knows how to
give a non-failure a stable token and a disposition without enlarging the failure taxonomy — this
condition simply was not given one.

`symphony-rs` conceded the framing rather than the preference when this was put to them: "the issue
asked 'which class does this carry' and offered three answers, all of which presupposed that it
carries one."

**A shared shape need not include the class**, which is what dissolves the report's strongest
constraint. Its reading 3 was rejected in the issue for a cost — Section 8.5 names Section 8.7's
shape by reference, so re-shaping one re-shapes both — and that cost is only incurred if the class
is part of the shape. A shape is the report's fields: the condition named, the reason token, the
operator-facing surface. The classification travels beside it. `symphony-rs` accepted this as the
load-bearing distinction they had not made.

And the two conditions differ in kind. A Section 8.7 routing ambiguity is an operator's mapping
defect: wrong, and wrong until edited. A Section 8.5 standing-condition loss is the system correctly
noticing a legitimate change — Section 8.5's own Note calls it "reversible besides — a label
re-added, an assignment restored, a mapping edit corrected", and declines to clean the workspace for
that reason.

## Options considered

- **Option A — a token and a Section 14.2 bullet on the `await_checks` model.**
  `standing_condition_lost`, with a reason token naming which condition failed, and a Section 14.2
  entry stating it is not a Section 14.1 failure class and citing Section 8.5 for the stop.

  Trade-offs: Section 14.2 grows a third non-failure entry, so a reader must learn that the section
  lists two kinds of thing. That is already true of it.

- **Option B — name an existing class in Section 8.5** (the report's reading 1), stating that
  Section 8.5 Part B already gave the disposition so the class here is a label rather than a routing
  key.

  Trade-offs: it is the smallest edit that closes the reporting gap, and it is what the only
  implementation assumed. It loses because the label it attaches is one Section 14.2 actively
  disposes of, in two ways, neither of which is what Section 8.5 says to do. An implementation is
  then required to know that this one use of the class does not route through the table — an
  exception carried in prose, against a section whose entire purpose is that the class routes.

- **Option C — a tenth Section 14.1 class** (the report's reading 2).

  Trade-offs: it removes the contradiction rather than annotating around it, which is a real
  advantage over Option B. It loses on Section 14.1's own terms: the nine "partition where a failure
  arose", and nothing arose. Enlarging the failure taxonomy to hold a correct event makes the
  taxonomy's opening paragraph false about its own membership.

- **Option D — declare it not a fault report at all** (the report's reading 3), with a second
  reporting channel carrying its own token discipline.

  Trade-offs: it is the reading the surrounding prose leans toward, and the report is right about
  that. It loses to Option A on cost alone once the shape/class distinction is made: Option A
  achieves the same separation — a non-failure with its own token and its own disposition — without
  a second channel, and without moving Section 8.7.

## Decision and reasoning

**Option A.**

**On not restating the disposition**, which `symphony-rs` asked for and which is right. Section 8.5
Part B already states the stop inline — terminate without workspace cleanup, release the claim,
schedule no retry. A Section 14.2 bullet restating all three clauses is two sites that must agree.
The `await_checks` bullet's own treatment is the model: it states the disposition at the level
Section 14.2 speaks at — parked, not retried, not failed — and cites Sections 8.11 and 9.10 for the
conditions rather than restating them. The new bullet does the same: it says the disposition is not
a retry and not a failure, says it is not a Section 14.1 class, and cites Section 8.5 for the stop's
mechanics. Section 8.5 stays the single site for those.

**On the registry.** `standing_condition_lost` is not added to `conformance/vocabulary.json`, and
the precedent is exact: neither of Section 14.2's existing non-failure tokens is published there
either. `await_checks:still_pending` and `await_checks:budget_floor` appear in no group, and
`token_budget_exceeded` appears only inside the `failure_classes` note as the example of a token
that is *not* one of the nine. A group for the section's non-failure tokens would be a coherent
thing to add, and adding one member of that set alone would not be. The trigger is below.

**What this does not fix, and it is the same defect one section over.** Section 8.7's own report —
"the condition is reported to the operator" — names no token either. So after this decision, of the
two reports that share a shape on Section 8.5's instruction, one carries a REQUIRED spelling and the
other does not, and Section 14.1's comparability sentence is satisfied for one of them.

That is left rather than fixed because Section 8.7's report is a different kind of thing and the
answer for it is not the answer here. A routing ambiguity is an operator's configuration defect, so
it may genuinely belong to a failure class; deciding which requires answering what Section 14.2
disposition it takes, and Section 14.2's operator-configuration disposition ("Skip new dispatches")
has the same instance-wide over-reach for one ambiguous issue that it has here. Deciding that inside
a decision about a non-failure would mean guessing at a failure's disposition to finish tidying a
non-failure's token. It is recorded and given its own trigger.

## Reconsideration trigger

Reopen if Section 8.7's routing-ambiguity report is observed being compared across implementations
and found to carry different tokens — the same defect this decision fixes for its neighbour. The
answer there is likely a failure class with a stated Section 14.2 disposition rather than a
non-failure token, which is why it is a separate decision and not an extension of this one.

A second trigger: a fourth non-failure token appearing in Section 14.2. Three is where a set starts
to want publishing, and at that point `standing_condition_lost`, `token_budget_exceeded` and the two
`await_checks:*` reasons want a registry group together rather than one at a time — which is the
form the registry's own `failure_classes` note already anticipates by naming `token_budget_exceeded`
as the thing outside the nine.
