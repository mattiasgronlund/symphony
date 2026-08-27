# Background — 0157 What a re-dispatch tests

## Context

The answer to issue #120 named three sites owing the continue-side check — "Section 8.5 Part B, the
worker's post-turn check in Section 16.6, and `on_retry_timer` in Section 16.7". Decision 0155
reached the first two and recorded the third as found rather than repaired, because saying which
conditions a re-dispatch tests is a decision and not a consequence of the reconciliation one. This
is that decision.

Two defects turn out to live at the same site, and both are against text the document already
carries rather than against a gap in it:

- **A retry timer fire dispatches without testing dispatch eligibility.** Section 8.4's "Retry
  handling behavior" already says a fire dispatches an issue "found and still candidate-eligible";
  Section 16.7's `on_retry_timer` tests membership in the candidate set and the global slot count,
  and nothing else. The prose and the reference algorithm disagree, and the algorithm is the one an
  implementation copies.
- **A fire that reaches `dispatch_issue` and loses the object store strands the claim.** Section
  8.5's claim partition asserts that `dispatch_issue`'s `ensure_object_store` failure "leaves the
  issue unclaimed so a later tick retries it — the case that makes the partition complete rather
  than an exception to it". That is true of the poll tick and false of the retry fire, which enters
  `dispatch_issue` holding the claim.

Both are repaired by one change, and that they share a repair is the reason they share a decision.

## The failure path: a backoff outlives the eligibility that armed it

`on_retry_timer` (Section 16.7) does, in order: match the fire's `generation` against the entry's,
remove the entry, `fetch_candidate_issues()`, `find_by_id(candidates, issue_id)` — releasing the
claim and returning where that is null — `available_slots(state) == 0`, re-arming where it is, and
then `dispatch_issue(issue, state, attempt=retry_entry.attempt)`.

Section 8.2 states nine conditions and says an issue is dispatch-eligible only if all of them hold.
This path tests two: the global slot count, and — implicitly, through the adapter's own filter —
state membership. The other seven are not evaluated at all.

The window they go untested in is the backoff, which is up to `agent.max_retry_backoff_ms`, default
`300000`. An operator or a teammate who removes a required label, unassigns the configured
`tracker.assignee`, or reopens a blocker on a `Todo` issue during those five minutes has done the
thing Section 5.3.1 says stops work — "to dispatch or continue" — and the fire dispatches anyway. A
run starts, provisions a workspace, takes a slot, and grants an agent commit and pull-request
authority in the routed repository, for an issue that no poll tick would have dispatched at that
moment.

Reconciliation does not cover it. Part B stops such a run on the next tick, which is right and is
also late: the workspace is provisioned, the `before_run` hook has run (Section 16.6), and the
agent may have taken a turn. Part B is the check for a condition lost *during* a run; it is not a
substitute for not starting one.

The per-state limit is a second, quieter case of the same shape. `available_slots` is Section 8.3's
**global** computation — `max(max_concurrent_agents - running_count, 0)` — and
`max_concurrent_agents_by_state` is a separate limit beside it. `should_dispatch` tests both, as
two of Section 8.2's nine conditions; `on_retry_timer` tests the global one alone. A deployment that
caps `In Progress` at 2 to bound review load holds that cap on every poll tick and breaks it every
time a retry fires into a full state.

## The stranded claim

`dispatch_issue` has two callers and they hand it different claim states. From `on_tick` the issue
is unclaimed, because `should_dispatch` refused it otherwise. From `on_retry_timer` the issue is
claimed, because `schedule_retry` took the claim when it armed the entry (Section 16.7) and nothing
between there and the call releases it.

On the provisioning-failure branch that difference is a leak. `dispatch_issue` logs and returns
before writing a running entry and without arming a retry. Reached from a poll tick the issue is
left unclaimed and Section 14.2's stated recovery — "Keep the service alive and retry on a later
tick" — happens. Reached from a retry fire, the retry entry is already gone, no running entry is
written, and the claim stays. `state.claimed.remove` appears at exactly two places in Section 16
(`terminate_running_issue`, and `on_retry_timer`'s not-a-candidate branch), and neither can be
reached for this issue again. The claim is held for the life of the process, every later tick's
`should_dispatch` refuses the issue as claimed, and the recovery Section 14.2 promises never runs.

The blast radius is one issue per occurrence, and the trigger is not exotic: a repository whose
object store is briefly unreachable while any issue is in backoff. What makes it worth naming is
that Section 8.5 states the opposite as a completeness argument for the claim partition. The
sentence is right about the site and wrong about one of its two callers, and a reader checking the
partition by reading that bullet finds it closed.

## What is being decided

**A retry timer fire is a dispatch, and tests what a dispatch tests.** Section 8.2's conditions are
evaluated at both dispatch sites through one predicate, `should_dispatch`, rather than each site
carrying its own subset.

The one condition that stands in the way is `claimed`-membership: arming a retry takes the claim, so
an issue with a retry entry is claimed by construction and the predicate called whole would refuse
every issue a fire could ask about. The repair is not to except the condition but to release the
claim, once, where the entry it was taken for is consumed:

- `schedule_retry` takes the claim *for the retry entry* — its own comment says so ("Arming a retry
  takes the claim, so a `RetryQueued` issue is claimed by construction"). `on_retry_timer` removes
  that entry. The claim comes off with it, which is the discipline `terminate_running_issue` already
  follows for a running entry: "The claim was held for the run whose entry was just removed, so it
  comes off with it."
- Every branch below the release then acquires afresh — `schedule_retry` when it re-arms,
  `dispatch_issue` when it writes a running entry — or leaves the issue `Released` (Section 7.1).
  The not-a-candidate branch's hand-written `state.claimed.remove` is absorbed: it was writing out
  what the discipline gives.
- `dispatch_issue` is then entered unclaimed from both callers, which is what makes Section 8.5's
  partition bullet true rather than true-of-one-caller.

Two of Section 8.2's conditions are tested *before* the predicate rather than inside it, because
their disposition differs. A concurrency slot is transient: the fire re-arms, keeps counting
attempts, and the issue stays claimed through the new entry. A condition over the record is not
transient in that sense: the fire releases, and a later poll tick dispatches the issue at
`attempt=null` if it becomes eligible again. Section 8.3 gains a name for the pair —
`dispatch_slot_available(issue, state)`, both limits, not the global half — so a dispatch site can
test them together without restating them. Their absence of a shared name is why one site tested one
of the two.

What the fire is *not* asked to do is re-derive routing. `dispatch_issue` computes `repo_of(issue)`
fresh, which is correct for a run that has not started: there is no prior `entry.repository` to
compare against, so the run-side value reconciliation's routing test needs (Sections 8.7, 16.3) does
not exist yet. Both dispatch sites reach routing through the same call, so the fire is no more and
no less exposed to an ambiguous mapping than a poll tick is.

## Options considered

### Except the `claimed` condition and give the fire its own predicate

The shape decision 0155's own recorded finding proposed: state a subset the re-dispatch owes — the
record's conditions and the `Todo` blocker rule — and name a predicate for it beside
`should_dispatch` and `standing_conditions_hold`.

Its real advantage is that it touches no claim lifetime. The fire keeps the claim from arming to
dispatch, there is no interval in which the issue is reserved by nothing, and the diff is confined
to one branch of one function.

It loses on three counts. First, a third eligibility predicate is a third thing to keep in step, and
two predicates drifting is the mechanism that produced this defect — the fire and the tick already
disagree, and the repair should remove the disagreement rather than formalize it. Second, the subset
has to be stated per-condition and every future condition added to Section 8.2 has to be classified
against it, which is a standing tax on a section that has grown twice. Third, and decisively, it
leaves the stranded claim in place: the fire still enters `dispatch_issue` holding the claim, so the
`ensure_object_store` branch still has nowhere to put it, and Section 8.5's partition bullet stays
false for one caller. Repairing that separately would mean releasing the claim anyway — at which
point the exception has bought nothing.

### Release the claim before the candidate fetch rather than after it

Cleaner as a narrative — the claim comes off in the same step as the entry — and it closes a
smaller wart: between removing the entry and reaching `dispatch_issue`, the issue sits in `claimed`
while belonging to neither `running` nor `retry_attempts`, which is the pair Section 4.1.8 says
`claimed` is re-derived from.

Rejected because the fetch is the one I/O the fire performs before it decides, and releasing across
it widens the interval in which the issue is `Unclaimed` (Section 7.1) to include a network round
trip. Section 8.4's own step order holds the claim across the fetch and releases after it, and there
is no reason to differ from it for a state that is not observable: Section 13.3's snapshot returns
running rows and retry rows, not claimed ones, so the derivation gap has no reader. The release
therefore goes immediately after the fetch resolves, where it costs nothing and covers both branches
that follow.

### Release on per-state slot exhaustion instead of re-arming

Would remove the need for `dispatch_slot_available` entirely: call `should_dispatch`, and release on
any refusal including a slot one.

It loses to a check the document already makes. Section 17.4 requires that "Slot exhaustion
requeues retries with explicit error reason", and separately that "A repeatedly failing worker spawn
escalates its backoff toward `agent.max_retry_backoff_ms` rather than restarting at the first
attempt every `polling.interval_ms`". A released issue is re-dispatched by a later tick at
`attempt=null`, which restarts the attempt count and so the backoff — the exact behavior the second
row forbids. Slot exhaustion must re-arm, and re-arming must be reachable without the record
conditions' disposition, which is what forces the two-step test.

### Leave state membership to `fetch_candidate_issues`'s filter

Section 11.1 requires the candidate fetch to "Return all matching issues in the configured active
states", so an issue that `find_by_id` finds in the result is in an active state, implicitly.

Rejected on the same ground the poll tick is not allowed to rely on it: `on_tick` fetches from the
same operation and still tests the condition inside `should_dispatch`. An implicit test couples one
dispatch site to an adapter obligation stated elsewhere and leaves the two sites checking different
things for the same reason again. Testing it explicitly costs a set membership over a value already
in hand.

## A correction to decision 0155's record

Decision 0155's `Background.md`, under "Findings from applying the plan", writes:

> What `on_retry_timer` owes is therefore a stated subset: the record's conditions and the `Todo`
> blocker rule, but not the four orchestrator-state ones, and not routing, which `dispatch_issue`
> re-derives correctly for a run that has not started.

The routing half stands. **"Not the four orchestrator-state ones" does not**, and the reason is that
the four are not alike at a retry fire:

- `claimed`-membership is true by construction, and is the only one of the four the fire cannot
  simply evaluate. It is handled by releasing the claim, not by exception.
- `running`-membership is *false* by construction, so the condition holds and testing it refuses
  nothing. It is false by construction because a retry entry and a running entry never coexist for
  one issue: every caller of `schedule_retry` either removed the running entry first
  (`on_worker_exit`, `reconcile_stalled_runs` via `terminate_running_issue`) or never wrote one
  (`dispatch_issue`'s spawn failure, `on_retry_timer`'s own re-arms), and `dispatch_issue` removes
  any retry entry when it writes one. Including it costs nothing and needs no exception.
- The two concurrency conditions are not only testable but must be tested: one of them already is,
  and the other is the `max_concurrent_agents_by_state` gap above. Carrying 0155's sentence forward
  would have shipped a decision that stops testing a limit the poll path enforces.

Recorded here rather than edited into 0155, per the `decision-record` skill's rule for a review
finding: a decision record states what was true when it was written. The finding was written by the
session that *applied* 0155, so what is being corrected is a record's reasoning about a site it
deliberately did not touch, not a normative clause that landed.

The shape is worth naming because it recurs: the finding classified four conditions by one property
they appeared to share — being about orchestrator state rather than about the issue — and that
property is not the one that decides whether a dispatch site can test them. It is the same
one-site-short-of-the-class shape 0155's own file records for decisions 0140 and 0148, arriving one
level down, in the classification rather than in the reach.

## What was checked

At `cbc6507`, the merge that applied decision 0156:

- Section 16.7's `on_retry_timer` contains no call to `should_dispatch`. `should_dispatch` occurs
  once in `SPEC.md`, at Section 16.2's call site; `standing_conditions_hold` once, at Section
  16.3's. Neither is named in the Section 8 prose that defines it.
- Section 7.3's `Retry Timer Fired` trigger reads, verbatim: "Re-fetch active candidates and
  attempt re-dispatch, or release claim if no longer eligible." That is the *second* site requiring
  what Section 16.7 did not do, and it names the release disposition as well as the test. Two
  normative statements against one reference algorithm is what makes the direction of the repair
  settled rather than chosen.
- Section 8.4's "Retry handling behavior" list reads, verbatim: "4. If found and still
  candidate-eligible: - Dispatch if slots are available. - Otherwise requeue with error `no
  available orchestrator slots`." and "5. If found but no longer active, release claim." Step 5 is
  unreachable as written — `fetch_candidate_issues` returns only active-state issues, so an issue
  step 2 finds is active — which is the trace of an earlier design and is subsumed here.
- `available_slots` is defined in Section 8.3 as the global computation only and is used in Section
  16.7; Section 16.2 spells the same computation `no_available_slots(state)`, a name no section
  defines. Section 8.3's per-state limit has no named test.
- `state.claimed.remove` occurs at exactly two sites in Section 16: `terminate_running_issue` and
  `on_retry_timer`'s not-a-candidate branch. `state.claimed.add` occurs at two: `dispatch_issue`
  after it writes the running entry, and `schedule_retry` after it writes the retry entry. The
  stranded-claim path follows from that enumeration and from `dispatch_issue`'s
  `ensure_object_store` early return, which returns before either `add`.
- Section 8.5's partition bullet reads, verbatim: "Its `ensure_object_store` failure writes no entry
  and arms no retry, and leaves the issue unclaimed so a later tick retries it — the case that makes
  the partition complete rather than an exception to it."
- Section 7.1's `Released` bullet already names two causes — "Issue missing from the candidate set,
  or a retry path that completed without re-dispatch" — and gives a producer for only the first.
  The second gains one here.
- Section 17.4 carries both rows the third option loses to, verbatim: "Slot exhaustion requeues
  retries with explicit error reason", and the escalation row naming `agent.max_retry_backoff_ms`
  and `polling.interval_ms`.
- `conformance/vectors/candidate-eligibility.json` already pins `should_dispatch` over all nine
  conditions with 16 vectors, and records that Section 8.2 "fixes no precedence among its
  conditions", which is why the disposition split here is made by the call order in Section 16.7
  rather than by reading a `refused` value.
- `conformance/vocabulary.json` publishes no group for pseudocode function names or for retry
  dispositions, so `dispatch_slot_available` adds no token. The error string `no available
  orchestrator slots` is unchanged.
- `python3 scripts/validate_spec_consistency.py` and `python3 scripts/validate_workflow_bundle.py`
  both report clean before the change. As decisions 0155 and 0156 recorded, the first is not
  evidence about a Conformance Statement row — its obligation check collapses the template's `8.x`
  citation to `8` — so the absence of an owed row is a checked judgement: this decision adds no
  `Implementation-defined` behavior and no MUST-document clause, it closes a choice the document had
  left two answers for.

## Reconsideration triggers

- **A third dispatch site.** The guarantee here is that every site reaching `dispatch_issue` tests
  Section 8.2 whole. A site added later — an operator-triggered dispatch, a resume path after
  restart — either goes through `should_dispatch` or reopens this.
- **A Section 8.2 condition that a retry fire genuinely cannot evaluate.** The whole-predicate
  design holds because exactly one condition needed handling and releasing the claim handled it
  without an exception. A condition that is true by construction at a fire and cannot be made false
  the way the claim can would force the subset design this decision rejected.
- **The unclaimed interval inside `dispatch_issue` becoming load-bearing.** Between the eligibility
  test and `state.claimed.add`, `dispatch_issue` performs `ensure_object_store` with the issue
  unclaimed. That interval is the poll tick's today and is both sites' after this change; nothing
  here creates it and nothing here closes it. If duplicate dispatch across that interval is ever
  observed, the repair is in `dispatch_issue` or in Section 7.4's serialization rule, once, for both
  callers — not a second claim discipline for the retry path.
- **Per-state limits gaining a second consumer.** `dispatch_slot_available` is introduced to stop
  one site testing one of two limits. A third caller wanting only the global half would be the
  signal that the pair is the wrong unit.

## Findings from applying the plan

Two sites the plan's Scope did not name were reached while applying it.

- **Section 7.3 already required this too, and needs no change.** Its `Retry Timer Fired` transition
  trigger reads "Re-fetch active candidates and attempt re-dispatch, or release claim if no longer
  eligible" — the test *and* the disposition, stated where a reader looks for what a trigger does.
  So Sections 7.3 and 8.4 both required what Section 16.7 did not perform, and the reference
  algorithm disagreed with two normative statements rather than one. It is recorded rather than
  edited because it is already correct: this decision makes it true, and the finding is that the
  document had been telling the reader twice. It also narrows what could have been argued — a
  repair direction that made the prose match the algorithm would have had to overturn two sections,
  not one.
- **Section 14.5 did not say what the same operator edit does to an issue in backoff.** Its bullets
  are what an operator reads to predict an intervention's effect, and its label-and-assignee bullet
  answers only for a running session, "when reconciled". After this decision the same edit against
  an issue queued for retry has an effect too — the fire tests the condition, dispatches nothing,
  and releases the claim — and it arrives at a different time, when the backoff elapses rather than
  on the next tick. The bullet now carries both. This is the same shape decision 0156 found in the
  same section: a disposition argued where it is decided and not stated where the person who lives
  with it is reading.
