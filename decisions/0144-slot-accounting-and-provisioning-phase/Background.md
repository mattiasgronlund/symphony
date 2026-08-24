# Background — 0144 What a concurrency slot counts, and when a run starts occupying one

## Context

Issue #109, split out of #108 because that issue's severity could not be stated without picking one
of two sentences. `SPEC.md` Section 8.3 computes dispatch headroom from `running_count`:

> - `available_slots = max(max_concurrent_agents - running_count, 0)`

`conformance/vectors/available-slots.json` pins that signature — `"given": "{ max_concurrent_agents:
integer, running_count: integer }"`, four vectors, `claimed` nowhere in it. Section 8.5's rationale
paragraph says the opposite in a subordinate clause:

> because `claimed` counts against `available_slots` (Section 8.3) that issue would hold a
> concurrency slot until the retry fired and released it

Section 16.2 and Section 16.7 call `no_available_slots(state)` and `available_slots(state)` over the
whole state, so the pseudocode reads either way and breaks no tie. One of the two sentences is
false, and an implementation that follows the false one fails a pinned vector.

## The reading that loses livelocks a deployment, and Section 16.7 shows it

This is a settlement rather than a coin flip, and the argument is not that one sentence is in a
formula and the other in prose. It is that `claimed`-based accounting deadlocks.

`on_retry_timer` removes the retry entry **before** it tests headroom, and removes the claim only on
the not-a-candidate branch:

```text
  state.retry_attempts.remove(issue_id)
  candidates = tracker.fetch_candidate_issues()
  …
  issue = find_by_id(candidates, issue_id)
  if issue is null:
    state.claimed.remove(issue_id)
    return state

  if available_slots(state) == 0:
    return schedule_retry(state, issue_id, retry_entry.attempt + 1, { … })
  return dispatch_issue(issue, state, attempt=retry_entry.attempt)
```

At that test the issue is still claimed — it has been since `dispatch_issue`, and `schedule_retry`'s
own comment says so: "The issue is already in `state.claimed` from `dispatch_issue` and stays
claimed while it is queued for retry". So a `max_concurrent_agents: 1` deployment with one issue in
backoff computes `1 - |{X}| = 0`, requeues X with `no available orchestrator slots` at `attempt +
1`, and does it again, and again, until the backoff saturates at `agent.max_retry_backoff_ms`
(default `300000`). **X blocks its own re-dispatch, forever, with nothing running.**

The general form is worse than the single-slot case, and it is reached by ordinary operation rather
than by a failure:

- Claims are held across backoff, so once the number of claimed issues reaches the limit every
  remaining candidate starves at `no_available_slots(state)` in Section 16.2's dispatch loop.
- That state is not transient. A **normal** worker exit schedules a continuation retry (`delay_type:
  continuation`, Section 16.7) and keeps its claim, so an issue that finished its turn loop goes on
  spending a slot it is not using. A deployment at its limit therefore stays at its limit after
  every run completes.

## It also contradicts what Section 8.3 says the limit is for

Section 8.3, two paragraphs under the formula:

> Slot accounting is placement-opaque: it counts agent sessions, not where they run.

A `RetryQueued` issue is not an agent session. It holds no workspace, runs no agent, and consumes
nothing the limit exists to bound. Counting it converts a bound on concurrent *work* into a bound on
concurrent *interest* in work, and a five-minute backoff then reserves capacity nothing is using.

And it collapses two conditions Section 8.2 lists separately:

- "It is not already in `claimed`" — may **this** issue be dispatched (duplicate-dispatch
  prevention);
- "Global concurrency slots are available" — may **any** issue be dispatched (capacity).

Summing the first into the second makes each claimed issue spend global capacity in order to prevent
its own duplicate dispatch.

## Decision, part one: the formula stands and Section 8.5's clause is the false one

Section 8.3 and `conformance/vectors/available-slots.json` are unchanged. Section 8.5's clause is
struck, and its **conclusion survives**: Part B still schedules no retry, and the invariant is still
worth stating where it is stated. What changes is the cost the paragraph claims, which is the only
part that depended on the false clause. Under `running_count` accounting what actually follows is a
claim held on that one issue rather than capacity taken from others:

> Without the invariant its worker's abnormal exit would queue one for an issue the tracker has
> already closed; the issue would hold its own claim until the retry fired and released it — up to
> `agent.max_retry_backoff_ms`, default `300000` — so an issue closed and reopened inside that
> window is skipped by every tick in between (Section 8.2). Other issues' dispatch is unaffected:
> `available_slots` counts running agent sessions (Section 8.3), not claims.

Section 8.3 also gains the statement that makes the tie unbreakable in future: `running_count` is
the number of entries in `running`, and `claimed` does not enter the computation. Today a reader
establishes that from a vector rather than from the section.

### Review finding against decision 0138

Decision 0138's `DECISIONS.md` chapter records the same magnitude the false clause states —
"`available_slots` counts against `claimed`, so closing an issue whose worker is running costs a
concurrency slot for up to `agent.max_retry_backoff_ms`, default five minutes, per closure" — and
that sentence entered `SPEC.md` with `87abf10`, the same commit as the repair. **0138's repair is
correct on its other grounds** and nothing about it is reopened: a retry queued for a closed issue
is wrong, the double-schedule race is real, and the ownership rule fixes both. What is wrong is the
cost it measured. `CLAUDE.md` routes this through the `decision-record` procedure as a logged review
finding rather than a silent rewrite of an accepted chapter's reasoning, so the finding is appended
to that decision's `Background.md`, its chapter's magnitude sentence is corrected in place naming
this decision, and its **State** carries the parenthetical `DECISIONS.md`'s legend provides for a
decision revisited in part without being replaced.

**It has spread to three artifacts, and the third was found mechanically rather than by reading.**
`conformance/README.md`'s decision-0138 entry carries the same claim — a retry queued for a closed
issue "holds a claim, and therefore a concurrency slot, for up to `agent.max_retry_backoff_ms`". An
earlier draft of this decision's `Plan.md` named only `SPEC.md` and `DECISIONS.md`; `python3
scripts/check_plan_anchors.py` reported the README as a site carrying the quoted phrase that the
plan did not name. That is the reach check doing exactly the job it exists for, and it is worth
recording rather than absorbing quietly: a false claim in a decision's chapter propagates into the
derived artifacts that summarize it, and correcting the chapter alone would have left the corpus
README asserting it.

The finding's shape is worth naming, because it is the same one 0138 itself recorded one step over:
a claim about a consequence, correct in the reasoning that reached it and false against an artifact
that mechanizes the thing it quantifies over. 0138 checked the pseudocode and the prose; the vector
corpus is where the answer already was.

### And it settles #108's severity

The claim leak reported in issue #108 — a run stopped by reconciliation never released from
`claimed` — starves that one issue permanently and grows `claimed` without bound. It costs **no**
concurrency slot. That is recorded in decision 0145 as a withdrawn consequence rather than left to
be re-derived.

## Decision, part two: a dispatched run occupies `running` from dispatch until it ends

The settlement exposes a second edge, and it fails in the opposite direction — over-dispatch rather
than starvation, and unbounded.

Section 7.1 state 3 and Section 9.11 both say a remote dispatch in the `Provisioning` window holds a
slot:

> Acquiring a node is asynchronous: while a node is requested and the executor is brought up, the
> issue is in the `Provisioning` orchestration state (Section 7.1). It holds a dispatch slot but is
> not yet `Running`, so a slow acquire does not block the poll tick.

Under `running_count` that is true only if a provisioning run is **in the `running` map**. Section
7.1 state 4 defines `Running` as "Worker task exists and the issue is tracked in `running` map", so
"not yet `Running`" reads as "not yet in the map" — and a run that is not in the map is not counted.
Acquisition is asynchronous, so every tick sees the same headroom, dispatches again, and requests
another node. Nothing bounds that.

The mechanism to say so already exists. Section 16.4 writes `state.running[issue.id] = { … }`
immediately after `spawn_worker` returns, and node acquisition happens **inside** the worker — the
only reading compatible with Section 17.4's "dispatch to a remote executor moves the issue through
the `Provisioning` state without blocking the poll tick", and with Section 16.6's
`run_agent_attempt` being the executor's run. So the entry does exist during acquisition. What is
missing is the sentence: **a dispatched run occupies `running` from dispatch until it ends, and
`Provisioning` and `Running` are phases of one running entry rather than membership tests against
the map.**

That the sentence decides a data structure rather than a wording is the `symphony-rs` report's
contribution, and it is the reason to state it in those terms. That build's `RunningEntry`
(`crates/symphony-orchestrator/src/state.rs:48-100`) carries no phase field. Read Section 7.1 state
4 on its own and Section 9.11's claim is a membership test that fails, so the natural implementation
is a **second collection** for provisioning runs — which Section 8.3's formula then does not count.
The unbounded over-dispatch is reached by building exactly what the two sentences say. Stated as a
phase of one entry, Section 16.4's existing write is the whole mechanism, Section 9.11's claim is
true under the formula this decision settles on, and no second counter and no second map exist to
disagree.

It also removes a special case from decision 0145: a provisioning run that never reached an agent
has a running entry, so `terminate_running_issue` releases its claim with no extra clause.

## Options considered

### State the formula over `claimed` and regenerate the vector

The steelman is real and is not "the prose is older". A single set that answers both of Section
8.2's questions is a simpler object than two: `claimed` is exactly the set of issues the
orchestrator has committed to, and bounding *commitments* rather than *sessions* is what keeps a
deployment from promising more work than it can start. It would make Section 8.2's `claimed` test
redundant with the capacity test rather than orthogonal to it, which is a smaller specification.

It loses on the livelock above, which is not a corner: `max_concurrent_agents` has no lower bound in
Section 5.3.5 and a single-slot deployment is the ordinary shape of a small one. It loses again on
Section 8.3's own statement of what the count is for. And it would require regenerating a pinned
vector that four cases and every artifact that mechanizes the formula already agree with — the
`symphony-rs` build's `available_slots(max_concurrent_agents, running_count)` takes no `claimed` and
is green on all four. The rule would have to be paid for by every consumer to buy a property the
document does not claim.

### Leave both sentences and let implementations pick

The status quo. It loses on evidence rather than on principle: an implementation that follows
Section 8.5 fails `conformance/vectors/available-slots.json` today, so the corpus already refuses
one of the two readings and the document has not noticed.

### Give provisioning its own counter

Answers the second edge without touching `running`: count provisioning runs separately and subtract
both. It loses twice. Section 8.3 states the accounting as placement-opaque and counting agent
sessions, and a second counter is a second thing to keep in step with the first — the failure mode
being precisely the over-dispatch it was added to prevent, one refactor later. And it makes
`Provisioning` a state the orchestrator holds outside the entry that represents the run, so a
provisioning run that dies has two removals to get right instead of one.

## What was checked

At `22b5194`, against the working tree:

- `conformance/vectors/available-slots.json` declares `"given": "{ max_concurrent_agents: integer,
  running_count: integer }"` and carries four vectors (`headroom`, `exactly-full`,
  `over-subscribed-clamped`, `single-slot-idle`). `claimed` does not appear in the file.
- `SPEC.md:1215` is the formula; `SPEC.md:1322` is the false clause; they are 107 lines apart in one
  document.
- `claimed` is mutated in exactly two places in Section 16 — `state.claimed.add(issue.id)` in
  `dispatch_issue` (`SPEC.md:4076`) and `state.claimed.remove(issue_id)` in `on_retry_timer`
  (`SPEC.md:4274`) — and `on_retry_timer` removes the retry entry before the headroom test, with the
  claim still held.
- Section 16.7's `on_worker_exit` normal branch schedules a continuation retry, so a completed run
  keeps its claim.
- Section 7.1 state 4 reads "Worker task exists and the issue is tracked in `running` map"; the
  `Provisioning` slot sentence appears twice, at `SPEC.md:1065` (Section 7.1) and `SPEC.md:2176`
  (Section 9.11).
- Section 16.4 writes `state.running[issue.id]` immediately after `spawn_worker` returns, and
  `state.claimed.add(issue.id)` two lines later.
- Decision 0138's `DECISIONS.md` chapter carries the magnitude sentence in bold, and
  `conformance/README.md:435-436` restates it in that file's decision-0138 entry.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.
- `python3 scripts/check_plan_anchors.py decisions/0144-slot-accounting-and-provisioning-phase/
  Plan.md --rev 22b5194` against an earlier draft reported the `conformance/README.md` sites as
  reach findings; the plan's step 10 exists because of that run.

## Reconsideration triggers

- **A deployment wanting to bound commitments rather than sessions.** That is a real want — it keeps
  a queue of claimed-but-unstarted issues from growing — and it is a *second* bound rather than a
  redefinition of this one. If it arrives, it arrives as its own configured limit over `claimed`,
  and the argument above says why it must not be folded into `max_concurrent_agents`.
- **A `Provisioning` window long enough to be worth admitting to at a different price.** The phase
  sentence makes a slow acquire spend a full slot. If a deployment wants provisioning runs to be
  cheaper than running ones, the answer is a weight rather than a second map, and the enumeration in
  Section 8.3 would have to say so.
- **Any future state in which a run exists without a `running` entry.** The phase reading is what
  makes Section 9.11's claim true; a lifecycle that dispatches without writing the entry reopens
  both halves of this decision at once.
