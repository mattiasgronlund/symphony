# Background — 0156 The refresh that returns a state, and the ids it does not answer

## Context

Issue #121, filed from the `symphony-rs` build against `4d610da`, asked where reconciliation's
stop-on-attribute-loss rule lives. Decision 0155 answered that: Section 8.2's record filters and
Section 8.7's routing are standing conditions, Section 8.5 Part B evaluates them, and Section 11.2
gained a Refresh completeness block requiring the refresh to carry the fields those conditions read.

Two things that block leaves open, and both are load-bearing rather than tidy-up:

- **The obligation is scoped to the fields one caller reads.** Reconciliation is not the refresh's
  only consumer. Section 16.6's worker calls the same operation after every turn and renders the
  next continuation prompt from what comes back, and the prompt reads fields no standing condition
  looks at.
- **An id the refresh does not answer for reaches no branch at all.** Decision 0155 named this
  explicitly as left open — "completeness is about what the refresh returns for an id it was given,
  not whether the tracker still has that id to give" — and listed it as a reconsideration trigger.
  It is reopened here because it is not a hypothetical: Sections 8.5 and 16.3 disagree today about
  which collection Part B iterates, so the absent case has two readings and the document does not
  pick one.

## The failure path: an adapter returns `{id, state}` and the next turn's prompt fails to render

Section 11.1 lists the operation and says one thing about it:

> 3. `fetch_issue_states_by_ids(issue_ids)`
>    - Used for active-run reconciliation.

Nothing there constrains the result's shape. Decision 0155's Refresh completeness block adds
`state`, `labels`, `assignees` and the routing fields — the fields the standing conditions read —
and stops there, because that block was written from Part B's needs. So an adapter returning those
and no more is conformant after 0155, and the eleven other fields of Section 4.1.1 are optional.

Two call sites then consume the same result, and only one of them is Part B:

- Section 16.3 writes it into the live snapshot: `state.running[issue.id].issue = issue`, on the
  branch decision 0155 gates behind `standing_conditions_hold`. Whatever the adapter returned is now
  the orchestrator's record of that issue.
- Section 16.6's worker loop, after every turn, does `issue = refreshed_issue[0] or issue` and then
  `build_turn_prompt(workflow_template, issue, attempt, turn_number, max_turns)`.

The second is where the narrow obligation costs a run. Section 12.2 renders with **strict variable
checking** over an `issue` object "whose members are the fields Section 4.1.1 defines", and Section
5.5 makes a name the engine cannot resolve a `template_render_error`. Section 5.5's gating puts that
class on the fail-the-attempt side — "Template errors fail only the affected run attempt" — and
Section 12.4 says the same from the renderer's end. So a repository whose `WORKFLOW.md` names
`{{ issue.title }}` or `{{ issue.description }}` in its continuation guidance renders turn 1 from
the dispatched record and fails turn 2 from the refreshed one, against an adapter that broke no
rule.

The failure is worse than a missing field, because it is a failure the operator cannot attribute.
The run reaches its first turn, does work, and dies at the turn boundary with a template error
naming a variable the template has always had and the workflow author has never changed.

That is what makes the record — not the field list — the right obligation. Section 4.1.1 opens by
saying the record is the one "used by orchestration, prompt rendering, and observability output";
a refresh that satisfies orchestration and not prompt rendering has satisfied one of the three the
section names. Widening the obligation to the whole record costs an adapter nothing it does not
already do for `fetch_candidate_issues`, which returns the same records for the same three
consumers.

## The absent id: no branch, and two decisions that said so without repairing it

Section 8.5 Part B and Section 16.3 iterate different collections, and have since both were written:

- Section 8.5: "For each running issue:" — the ids the orchestrator has in `running`.
- Section 16.3: `for issue in refreshed` — the records the adapter returned.

Under Section 8.5's reading, a running id with no refreshed record reaches the three-way branch with
no state to test. Under Section 16.3's reading it reaches nothing and the run continues. The
document does not say which, and the two readings differ in exactly the case that matters.

This is not a newly noticed defect. It was cited as an *argument* by two decisions, neither of which
repaired it. Decision 0140's `Background.md`:

> Section 16.3's `reconcile_running_issues` iterates `for issue in refreshed`, while Section 8.5
> Part B enumerates three cases (terminal / active / neither) and has **no absent branch at all**.

And decision 0148's, on the sibling half:

> Section 16.3's `reconcile_running_issues` iterates `for issue in refreshed`, while Section 8.5
> Part B enumerates terminal / active / neither and has **no absent branch at all**. An issue moved
> to a different project mid-run is simply absent from a scoped enumeration, reaches none of the
> three branches, and its run continues against a repository the mapping no longer selects.

Both used the gap to argue against query-scoped enumeration, and both were right to. Neither closed
it, because in each the absent case was a consequence of a design they were rejecting rather than a
case the accepted design still produced. It still does: an id can go missing from the refresh
because the issue was deleted, because the adapter's own scope moved, or because a backend answered
partially in a way its error path did not catch. Section 16.6 already covers itself against all
three with `refreshed_issue[0] or issue`; Part B does not.

A gap used twice as evidence and repaired neither time is the shape worth recording. The two
citations are why this is settled here rather than left for a third decision to cite.

## The disposition: leave it running, retry next tick

The absent id takes the whole-fetch failure's disposition, and for the same reason. Section 8.5
already says "If state refresh fails, keep workers running and try again on the next tick", and that
rule rests on absence of evidence not being evidence of revocation: a refresh that did not answer is
not a tracker that said no. One id going unanswered is the same claim about a smaller set.

The alternative — stop the run — reads an unanswered id as a deleted issue. It is wrong in every
case where the id is unanswered for a reason other than deletion, and those are the majority: a
transport that dropped part of a batch, an adapter whose scope narrowed, an eventually-consistent
backend mid-propagation. Against a deleted issue, stopping is right but not urgent — the work is
already unwanted, the workspace is already garbage, and the next tick's candidate fetch will not
re-dispatch an issue that no longer exists.

The cost is stated rather than absorbed: an id that is *permanently* absent — a genuinely deleted
issue — leaves a run that reconciliation never stops, tick after tick, until the worker exits on its
own through `agent.max_turns` or a stall. That is a real leak of one slot for the length of one run,
and it is accepted because the alternative leaks correctness on every transient. Part A's stall
detection is the backstop, and it is not a good one: a run whose agent is making progress against a
deleted issue is not stalled.

Reconciling Sections 8.5 and 16.3 on the collection is what makes the branch statable at all. Part B
iterates the running ids — Section 8.5's reading — and the refreshed records are looked up by id
within it, so "no refreshed record for this id" is a case the loop can be in rather than an
iteration that never happens.

## Options considered

### Leave the refresh obligation at the fields the standing conditions read

Decision 0155's answer, kept. It is the smaller ask of an adapter, and it is exactly sufficient for
the caller 0155 was reasoning about. It loses on the second caller: Section 16.6 renders a prompt
from the same result, under strict variable checking, and a field the standing conditions do not
read is still a field a `WORKFLOW.md` may name. The narrow obligation is not wrong about
reconciliation; it is silent about the consumer that turns a missing field into a failed run
attempt.

### Widen Section 12.2 instead — let a template see whatever the refresh returned

Rather than obliging the adapter, oblige the template author less: make an unresolvable `issue.*`
render empty rather than raise. This is the subset reading decision 0154 rejected for Section
4.1.1's membership, and it loses here for the same reason plus one more. Strict variable checking is
a stated rendering rule (Section 12.2) with a REQUIRED error class behind it (Section 5.5), and
relaxing it would silently substitute an empty prompt variable for a missing one — turning a loud
failure at the turn boundary into an agent given a task description that says nothing. The decision
would also be about rendering, not about refresh, and would leave the orchestrator's own snapshot
degraded.

### Rename `fetch_issue_states_by_ids`

Decision 0155 declined this and recorded why: a rename of the adapter contract's surface, decided as
a side effect of repairing a reconciliation branch, is a decision of its own. That reasoning
survives this decision unchanged, and this decision is a stronger case for the rename than 0155 was
— the contract is now unambiguously over the whole record. It is still declined here, on 0155's own
ground and to keep the reach of this change to what it argues for. 0155's trigger for the rename —
"a decision already touching Sections 11.1, 16.3 or 16.6" — has now fired twice without being taken,
and that is recorded so a third occurrence is a pattern rather than a coincidence.

### Stop the run when its id is absent from the refresh

The disposition the issue's reporter would find least surprising, and the one that handles a deleted
issue promptly. Argued in its own terms above and rejected: it reads a transport failure as a
tracker decision, in a document that already refuses that reading for the whole-fetch case one
bullet earlier. A rule that treats a partial failure more harshly than a total one is not a stricter
rule, it is an inconsistent one.

### Give the absent case its own retry rather than leaving the run untouched

Stop the worker, arm a retry, let the next dispatch decide. It loses on Section 8.5's claim
partition: arming a retry hands the claim on, so the issue stays claimed through a backoff for a
condition that may be a dropped packet, and Section 8.4's backoff escalates across ticks while the
issue is repeatedly absent. Leaving the run untouched costs nothing per tick and needs no new site
in the partition.

## What was checked

At `bbc2398`, the merge that applied decision 0155:

- Section 11.1's entry for `fetch_issue_states_by_ids` is two lines and says only "Used for
  active-run reconciliation." Verbatim as quoted.
- Section 16.3 writes the refreshed record into the snapshot with
  `state.running[issue.id].issue = issue`; Section 16.6 reads it with `issue = refreshed_issue[0] or
  issue` and passes it to `build_turn_prompt`. Both verbatim.
- Section 12.2 states "Render with strict variable checking." and fixes the governed maps as "the
  `issue` object, whose members are the fields Section 4.1.1 defines, and `metadata`". Section 5.5
  defines `template_render_error` as "the body is well formed and names something the engine cannot
  resolve: an unknown variable, an unknown filter, or an invalid interpolation", and its gating
  bullet reads "Template errors fail only the affected run attempt." Section 12.4: "Fail the run
  attempt immediately." All verbatim.
- Section 4.1.1 defines sixteen fields and opens by naming its three consumers — "used by
  orchestration, prompt rendering, and observability output".
- Section 8.5 Part B iterates "For each running issue:"; Section 16.3 iterates `for issue in
  refreshed`. Both verbatim, and they disagree.
- The "no absent branch at all" passages are verbatim in
  `decisions/0140-assignee-routing-condition/Background.md` and
  `decisions/0148-issue-routing-substrate/Background.md`, in both cases as an argument against
  query-scoped enumeration rather than as a defect either repaired.
- `conformance/vocabulary.json` publishes no group for reconciliation stop causes, and
  `runtime_state_fields` enumerates Section 4.1.8's nine top-level fields rather than a running
  entry's members — so nothing here adds, renames, or removes a published token.
- Of the thirteen vector files present before this decision, `worker-exit-disposition.json` is the
  only one citing Section 8.5 in its `spec_refs`, and its subject is `run_id` matching on an
  arriving message, which Part B's branch count does not touch. `standing-conditions.json` cites
  Section 16.3 for the predicate, not for the loop. Neither needs re-deriving.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings before and after.
  As decision 0155 recorded, that is not evidence about a Conformance Statement row: the obligation
  check collapses an `8.x` citation to `8`. The absence of an owed obligation is the evidence, and
  this decision adds no `Implementation-defined` behavior and no MUST-document clause.

## Reconsideration triggers

- **A tracker backend whose refresh genuinely cannot return the whole record** — one whose
  by-id endpoint is a projection with no full-record equivalent. The obligation would then need an
  `Implementation-defined` escape with a MUST-document clause and a Conformance Statement row, which
  is a different decision from this one and should not be smuggled in as a relaxation.
- **Permanent absence becoming a live failure mode** — a deployment where issues are deleted rather
  than closed. The one-slot leak this decision accepts is bounded by how often that happens; if it
  becomes routine, the absent branch needs a bound of its own (a consecutive-absence count, say)
  rather than a reversal of the disposition.
- **A third decision citing `fetch_issue_states_by_ids`'s name against its contract.** Decision
  0155 declined the rename and named the trigger; this decision declined it again on the same
  ground. A third is the point at which declining costs more than doing it.
- **Section 4.1.1 gaining a field an adapter cannot supply on a by-id read.** The whole-record
  obligation is affordable because the candidate fetch already returns the same records; a field
  only the candidate path can populate would break that symmetry and reopen which record the refresh
  owes.

## Findings from applying the plan

Two sites the plan's Scope did not name were reached while applying it, and are repaired in the same
change.

- **Section 11.2's completeness clause did not cite the record it names.** Sections 17.3 and 18.1.3
  both write "the complete normalized record (Section 4.1.1)"; the clause the two are derived from
  wrote it without the citation, so the one sentence that states the obligation was the one place a
  reader could not follow it to the field list. The citation is added.
- **Section 14.5 did not say what deleting an issue does.** Its bullets are what an operator reads
  to predict the effect of an intervention, and this decision's disposition makes deletion the one
  intervention whose effect is *nothing*: the run continues to `agent.max_turns` because an
  unanswered id is not a revocation. That is the disposition's cost stated where the person who
  pays it is reading, rather than only in Section 8.5 where it is argued. Section 14.5 now carries
  it, and names moving the issue to a terminal state as the intervention that does stop the run.
  This is the same cost the section above records; what is added is the operator-facing half, not a
  second rule.
