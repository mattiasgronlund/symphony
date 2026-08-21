# Background — 0138 The function five call sites named and no section defined

## Context

Neither #95 nor #96 reports this. It was found checking #95's claims against the corpus, and it is
recorded as its own decision because the repair is not what either issue asked for, and because the
`symphony-rs` build implements Section 16.7 directly at phase D2d — every function that section
calls and does not define is a resolution that build has to invent, and a dated record of what was
resolved is worth more than the edit.

Section 16 defines eight functions and calls forty-three it does not. Most of those are primitives a
reader supplies without changing observable behaviour — `log_debug`, `now_utc`, `spawn_worker`,
`find_by_id` — and three more (`available_slots`, `sort_for_dispatch`, `normalize_state`) are
undefined in Section 16 but pinned by files in `conformance/vectors/`, so they are not gaps either.
Three are.

`schedule_retry` is called five times — `dispatch_issue` once (`SPEC.md:3947`), `on_worker_exit`
twice (`:4095`, `:4100`), `on_retry_timer` twice (`:4117`, `:4128`) — and its only definition
anywhere is Section 8.4's two prose bullets. That split is plausibly why #95's defect went unnoticed
for as long as it did: the function whose body decides what a fire means has no body to look at.

`terminate_running_issue` is called twice by `reconcile_running_issues` (`:3915`, `:3919`) with
`cleanup_workspace=true` and `false`, and defined nowhere. It is the seam this decision turns out to
be about.

`reconcile_stalled_runs` is called once (`:3899`) and defined nowhere, and it is the third gap — a
gap this decision *creates* as much as inherits, which is the review finding recorded at the end.

### The failure path

`on_worker_exit` opens without a guard, where its sibling `on_retry_timer` has one:

```text
on_worker_exit(issue_id, reason, state):
  running_entry = state.running.remove(issue_id)
  state = add_runtime_seconds_to_totals(state, running_entry)
```

Two reachable paths deliver an exit for an issue that is no longer running.

**The stall.** Section 8.5 Part A: "If `elapsed_ms > codex.stall_timeout_ms`, terminate the worker
and queue a retry." The termination is the orchestrator's; the worker's own exit still arrives
afterwards. If reconciliation removed the running entry when it terminated, `running.remove` returns
nothing and `add_runtime_seconds_to_totals` and `next_attempt_from` read fields off it. If
reconciliation did not remove it, `on_worker_exit` takes its `else` branch and schedules a *second*
retry for an issue Part A has already queued one for — which is the double-schedule decision 0136's
race needs in order to happen at all. The document says neither, so both defects are live and an
implementation picks one by accident.

**The terminal issue, and this one is worse in kind.** Section 8.5 Part B: "If tracker state is
terminal: terminate worker and clean workspace." That worker reaches `on_worker_exit` with an
abnormal reason, takes the `else` branch, and unconditionally calls `schedule_retry`. A retry is now
queued for an issue the tracker has closed.

It self-cancels, one backoff later: `on_retry_timer` fetches candidates, `find_by_id` returns null,
and `state.claimed.remove(issue_id)` releases the claim (`:4123`). So the cost is a wasted timer and
a claim held rather than corruption — but a claim held is a slot not offered, because
`available_slots` counts against `claimed`. A repository whose issues are closed while their workers
run loses a concurrency slot for up to `agent.max_retry_backoff_ms`, default `300000`, per closure.
Closing three issues costs three slots for five minutes, on an orchestrator whose default
`max_concurrent_agents` is small.

Both paths are the shape #95 reports: a message arriving for state that has moved, and pseudocode
written as though it had not.

## What was checked

Read against `SPEC.md` at `cbc7d8a`.

- The defined-versus-called count was measured, not estimated: eight function definitions in Section
  16, forty-three distinct names called without one. The measurement is reproducible from the
  `Plan.md`, which records the test used to classify a name as a gap rather than a primitive.
- `on_retry_timer` has `if missing: return state`; `on_worker_exit` has no equivalent. Both are in
  Section 16.7, eleven lines apart.
- The self-cancel path was traced through `on_retry_timer` to `claimed.remove`, and
  `available_slots` counting against `claimed` was confirmed rather than assumed.
- Section 8.5 Part A queues a retry as part of terminating; Part B does not, for either of its two
  termination branches. That asymmetry is real and the repair has to preserve it.

## Options considered

### Give reconciliation its terminations, and let the guard mean something — chosen

One rule: reconciliation that terminates a worker removes the running entry and performs that run's
accounting at the point of termination; `on_worker_exit` is authoritative only for exits the
orchestrator did not cause, and returns `state` unchanged when the entry is gone. `schedule_retry`
and `terminate_running_issue` both get bodies, and Part A's "queue a retry" stays where Section 8.5
puts it — in reconciliation, after the termination — while Part B keeps queueing nothing.

It fixes both paths with the same sentence. The stall's second retry does not happen because the
entry is already gone; the terminal issue's retry does not happen for the same reason. The guard
stops being defensive and starts being the mechanism.

The cost is honest and is stated in the spec rather than discovered later: the runtime-seconds
accounting moves to `terminate_running_issue` for terminated runs, and if it did not, every
reconciliation-terminated run would drop out of `agent_totals`.

### Guard `on_worker_exit` and stop there

Add `if missing: return state` to match `on_retry_timer`. It is the smallest change, it closes the
crash, and it is the first thing a reviewer would write.

It loses because it does not settle the race it hides. Whether the entry is missing still depends on
whether reconciliation removed it, which the document still does not say — so the guard converts a
crash into a coin flip between "one retry queued" and "two retries queued", decided by an
implementation detail. A guard that makes a failure quieter without making the outcome determinate
is worse than the crash it replaces, because the crash gets reported and the coin flip does not.

### Suppress the retry by exit reason rather than by state

Have Part A and Part B terminate with a reason `on_worker_exit` recognises — `terminated_by_orchestrator`
— and branch on that instead of on the entry's presence. Its case is real: accounting stays in one
place, so nothing moves to reconciliation, and the intent is explicit at the branch rather than
implicit in a map lookup.

It loses on what it trusts. The reason has to survive the host's process-exit path faithfully, and a
worker killed hard reports whatever the operating system says rather than what the orchestrator
meant — so the branch is only as reliable as a signal the specification does not control. It also
does not fix the crash: a reason-based branch still reads `running_entry` before it reaches the
branch. State the orchestrator wrote is checkable by the orchestrator; a reason handed back across
the process boundary is not.

### Define every function Section 16 calls

Not offered on the decision sheet. The completionist answer, and it loses on altitude: Section 16 is
a reference algorithm, and `log_debug`, `now_utc` and `spawn_worker` are deliberately unwritten. The
test this decision uses instead — can a reader supply the body without changing observable
behaviour — puts `schedule_retry` and `terminate_running_issue` on one side and the primitives on
the other, and it is written down in `Plan.md` so a later reader can re-run it rather than take the
classification on trust.

## Reconsideration triggers

- **A remote executor whose termination is not observable.** The rule assumes the orchestrator knows
  it terminated the worker. Section 9.11's seam forwards a terminal decision to the executor while
  it is connected; a disconnected executor finalizing on its own is the case where the orchestrator
  might learn of an exit it caused and did not record, and the reason-based option would be back on
  the table.
- **A third path delivering an exit for a removed entry.** Two are known. A third would mean the
  invariant belongs somewhere more central than two call sites in reconciliation.
- **Runtime-seconds totals that do not add up.** The accounting split is the price of this option
  and the first place to look if `agent_totals` is ever wrong.
- **A reconciliation-initiated termination that must retry other than Part A's.** The rule reads
  "entry gone means the orchestrator has already decided what happens next". A new termination site
  that wanted the exit handler to decide would break it rather than extend it.

## Review findings

**The repair removed the only producer of a consequence it promised to keep.** The plan's first
draft said Part A "still queues its retry", and simultaneously stopped `on_worker_exit` from queueing
anything for a terminated run. The only other place that retry could come from is
`reconcile_stalled_runs`, which Section 16 calls and does not define — so as drafted, a stalled run
would have been terminated and never retried, silently, and Section 8.5 Part A's "terminate the
worker and queue a retry" would have had no producer at all. This is worse than the double-schedule
it was repairing: two retries is a wasted timer, none is a dropped issue.

It was caught by the premise-and-consequence lens of the `plan-review` skill rather than by
`scripts/check_plan_anchors.py`, which reported nothing for this plan — 0 findings from 4 quoted
spans. That is worth recording as its own observation: the mechanical checks scale with how much a
plan *quotes*, and this plan quoted least of the three because it is mostly about pseudocode rather
than prose. A plan can be quietly under-checked by being written in a register the script has little
purchase on.

The repair is a body for `reconcile_stalled_runs` that terminates and then schedules, which makes
the count of gaps three rather than two and puts the retry in one place. The defect was introduced
by this decision's own repair for a previous one, which is the recurrence the `decision-record` skill
asks be counted rather than smoothed over: the first repair moved a responsibility without moving
the work, and the second had to name where the work went.
