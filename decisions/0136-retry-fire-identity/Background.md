# Background — 0136 A timer fire that could not name the arming it came from

## Context

Issue #95 was filed by the `symphony-rs` build against phase D2, which is planned rather than
built: the report arrived before the code it describes, so nothing downstream has to be unwound to
adopt an answer. It names `SPEC.md` Section 8.4 and Section 16.7 and asks for a monotonically
increasing generation per issue, stored beside `attempt` in Section 4.1.7 and carried by both the
arm and the fire.

Section 8.4's Retry entry creation is two bullets:

- Cancel any existing retry timer for the same issue.
- Store `attempt`, `identifier`, `error`, `due_at_ms`, and new timer handle.

The first bullet is what makes cancel-then-replace in-contract rather than an implementation's
invention; without it the clause is dead text. Section 16.7 then identifies an arriving fire by
`issue_id` alone:

```text
on_retry_timer(issue_id, state):
  retry_entry = state.retry_attempts.pop(issue_id)
  if missing:
    return state
```

A cancellation that loses the race leaves a fire in flight for a timer that no longer has an entry
behind it. The `if missing` guard catches the fire whose entry was *popped*. It does not catch the
fire whose entry was *replaced*, because a replaced entry is present.

### The failure path

The reachable double-schedule is a stall, and both schedule points are in the document:

1. Section 8.5 Part A: "If `elapsed_ms > codex.stall_timeout_ms`, terminate the worker and queue a
   retry." That is a `schedule_retry` — an entry at attempt *n* with `due_at_ms` a backoff away, and
   a timer armed.
2. The worker that Part A terminated exits, abnormally, and reaches `on_worker_exit`, whose `else`
   branch calls `schedule_retry` again (Section 16.7). Nothing in the document orders these two or
   suppresses the second.
3. Section 8.4's first bullet cancels the armed timer and the entry is replaced. If that timer had
   already expired, the cancel does not unsend what is already in flight.
4. The stale fire arrives. An entry is present, so `if missing` does not fire; `pop` takes the
   *new* entry and `dispatch_issue(issue, state, attempt=retry_entry.attempt)` runs immediately.

What ships broken is the backoff itself. The retry that Section 8.4 says waits
`min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)` runs at once, and the `due_at_ms` that
was supposed to hold it is discarded unread. The live timer that was armed in step 3 later fires
into an empty slot and returns on `if missing`, so the issue is dispatched once — but early, and on
exactly the path that had just produced two failure signals in a row. Backoff collapses to zero
precisely where it was doing work.

### The report's worked example is not reachable, and the gap is real anyway

#95 illustrates the race with reconciliation observing a stall for an issue whose worker has already
exited. That cannot happen. `on_worker_exit` begins `state.running.remove(issue_id)` and Section
8.5 Part A iterates running issues ("For each running issue, compute `elapsed_ms`"), so an exited
worker is no longer a stall candidate. This is recorded rather than dropped because a later reader
re-checking the report should not conclude from one bad example that the whole finding was
imaginary: the same collision arrives through step 2 above, which the report does not name.

## What was checked

Read against `SPEC.md` at `cbc7d8a` rather than taken from the report.

- Section 8.4's two Retry-entry-creation bullets are quoted above and are the whole of what the
  document says about creating an entry. There is no `schedule_retry` function body anywhere; see
  decision 0138, which is where that gap is repaired.
- Section 4.1.7 already carries `due_at_ms` (monotonic clock timestamp) and `timer_handle`
  (runtime-specific timer reference). A generation is an addition beside them, not a new pair — the
  sheet's framing that it introduces a second time-like field was wrong.
- `on_retry_timer`'s signature is `(issue_id, state)`. Adding the generation changes a signature in
  Section 16.7, which is the one anchor change this decision makes.
- `schedule_retry` has **five** call sites, not the four first counted: `dispatch_issue` once
  (`SPEC.md:3947`), `on_worker_exit` twice (`:4095`, `:4100`), `on_retry_timer` twice (`:4117`,
  `:4128`). The miscount mattered: the pair it missed is in `on_worker_exit`, the function the
  reachable failure path runs through. Recorded because the correction came from the reviewer, not
  from the drafting.

## Options considered

### Carry a generation — chosen

`RetryEntry` gains `generation`. `schedule_retry` assigns a value for the issue, arms the timer with
it, and the fire carries it back. `on_retry_timer` reads the entry without removing it, compares,
and returns untouched when the generation does not match — so a stale fire leaves the live entry and
its live timer exactly as it found them.

The shape change matters as much as the field. `pop`-then-test cannot be repaired by adding a
comparison, because by the time the comparison fails the entry the fire should not have touched is
already out of the map. The repair is get, compare, then remove.

### Guard on the due time, with no new field

On a fire, compare `now_ms` against `retry_entry.due_at_ms`; if the entry is not yet due, re-arm for
the remainder instead of dispatching. Its case is strong. `due_at_ms` is already in Section 4.1.7,
so no field is added and no anchor changes; the predicate is two integers; it is robust to any
number of stale fires rather than to one; and it repairs a fire that arrives early for any reason,
not only for a lost cancellation race. The threading cost the decision sheet attributed to it is
nil — a sans-io step reads no clock, so `now_ms` is already on every input.

An earlier claim that this option depends on the backoff constants is also wrong, and is corrected
here rather than left standing: re-arming for the remainder is correct at any delay, including the
fixed `1000` ms continuation delay.

It loses on what it decides with. It answers "is it time yet", not "is this the arming that is
live", and the two come apart when two arms share a due time. Section 8.4 gives continuation retries
a *fixed* `1000` ms delay, so two continuation schedules taken in the same millisecond produce
entries a due-time guard cannot distinguish — it will dispatch on the stale fire and call it due,
because it is. It also converts an identity question into a timing tolerance: an implementation must
pick a slack for clock granularity, and the specification would then owe either a value or an
`Implementation-defined` row and its Conformance Statement line. The generation costs a field and
buys a predicate over two integers with no clock in it, which is the shape Section 17's existing
vector corpus can check.

### Treat the fire as a wakeup and let a due-scan be the authority

The fire carries nothing; on any fire the orchestrator scans `retry_attempts` for entries with
`due_at_ms <= now_ms` and dispatches those. Stale fires become harmless by construction, since a
fire for a cancelled entry simply finds nothing due, and no identity is needed at all. It is the
shape most real schedulers converge on, and it deserved the hearing it got.

It loses on reach. A scan needs a dispatch order over the due set, and a rule for `available_slots`
running out partway through it — neither of which the document has, because today one fire
dispatches exactly one issue and requeues at `attempt + 1` with error `no available orchestrator
slots` (Section 16.7). A scan finding three due entries with one slot free would inflate two
backoffs for issues that never got a chance at it, which is a behaviour change well past the
reported defect. Its vector is `entries_due(map, now_ms) -> [issue_id]`, not expressible until that
order is pinned; all eight files in `conformance/vectors/` are one-shot pure functions with a
`given` and an `expect`, and there is no sequenced vector shape to write it in. Vector cost ranks
generation ≤ due-time < due-scan, and the last one is blocked on a clause that does not exist.

### Require the cancellation to be observed before the entry is replaced

#95's own alternative, and not offered on the decision sheet. It removes the race by forbidding the
window: `schedule_retry` may not install a new entry until the old timer's cancellation has been
acknowledged.

It loses because it puts the requirement on the wrong side of the seam. This is a liveness
obligation on the host's timer facility, not on orchestrator state, so conformance would depend on a
primitive the specification does not define — `schedule_tick` and `send` are themselves called and
never defined in Section 16. It is also unexpressible in the reference algorithms without inventing
a second message and a state in which the orchestrator is waiting for it, which is a larger
structural change than the defect warrants. A sans-io core can check a comparison; it cannot check
that something else has finished cancelling.

## The value, and where the counter lives

Storing the generation in the entry — the report's ask — leaves one question the report does not
reach: `on_retry_timer` removes the entry, so a later `schedule_retry` for the same issue finds
nothing to derive the next value from, and the obvious reading restarts at 1. That reuses a value.

Under first-in-first-out delivery the reuse is unreachable, and this was traced rather than assumed.
A stale fire enqueued at *T* is dequeued before every message enqueued after *T*. For a fresh entry
to be present at generation 1 while a generation-1 fire is still queued, that fire's entry must have
been popped and a new one created in the window — and popping it requires handling a fire for the
same issue enqueued *before* *T*, which cannot be, since Section 8.4 keeps at most one timer armed
per issue and the second arm's fire is necessarily enqueued later.

So the guarantee would hold, resting on an ordering property the document never states, over
primitives (`send`, `event_loop`, `schedule_tick`) it never defines. The clause is stated instead:
a generation value MUST NOT be reused for an issue while the orchestrator process lives. It is one
sentence, it is checkable without knowing the transport, and an implementation satisfies it with a
counter that outlives the entry or with a single process-wide counter.

That counter is itself Core-introduced runtime state with no field in Section 4.1.8 — the same
shape issue #96 reports, arriving from the other direction. It is admitted by the Section 14.3
widening decision 0137 makes, and this decision does not add a field for it: the container is free
(one integer, per issue or per process), and mandating one would over-specify a choice with no
observable consequence. That dependency is real and is recorded in this decision's `Plan.md`.

## Reconsideration triggers

- **The document fixes an ordering property for orchestrator messages.** The non-reuse clause exists
  only because delivery order is unstated. If a later decision pins it, the clause becomes derivable
  and should be re-argued rather than kept out of habit.
- **`retry_attempts` stops being `Ephemeral`.** Section 4.1.8 classes it `Ephemeral` today, so no
  fire survives a restart and the non-reuse clause needs no more than the process lifetime. A
  budgeting-style class change to `Durable` would widen the scope the value must be unique over, and
  the clause's wording would have to move with it.
- **A due-scan arrives for an unrelated reason** — batched dispatch, or a single timer replacing
  per-issue timers. The generation stays correct under it, but the option rejected above would then
  be paying its dispatch-order cost for other work, and the comparison changes.
- **A second arm becomes possible per issue.** The whole analysis rests on Section 8.4 cancelling
  before it replaces. A decision that allowed two live timers for one issue would invalidate the
  ordering argument above, not just complicate it.
