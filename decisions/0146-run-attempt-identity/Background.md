# Background — 0146 Run-attempt identity and the messages a replaced run keeps sending

## Context

Issue #106, filed by the `symphony-rs` build against `SPEC.md` Section 16.7. `on_worker_exit`
decides whether an exit is owed a retry by testing whether the issue's running entry is **present**:

```text
on_worker_exit(issue_id, reason, state):
  running_entry = state.running.remove(issue_id)
  if missing:
    # The orchestrator terminated this run itself and has already removed the entry …
    return state
```

Section 8.5 establishes the invariant that guard implements: "The terminated worker's own exit then
arrives with no running entry, and a worker exit for an issue with no running entry is a no-op — so
a termination the orchestrator initiated never produces a retry the orchestrator did not ask for."

Section 8.4 states, of the sibling function eleven lines below in the same code block, that testing
presence is **not sufficient**:

> An implementation MUST discard a fire whose `generation` does not equal that of the issue's current
> retry entry, leaving both that entry and its armed timer unchanged (Section 16.7). Testing only
> whether an entry is present does not satisfy this: the entry that a discarded fire must not consume
> is present by construction.

The same construction produces a present-but-wrong entry here, and `on_worker_exit` has nothing to
tell them apart with.

## The failure path

A worker exit is delivered asynchronously, exactly as a timer fire is, and cancellation is not
synchronous with the thing it cancels. So the sequence Section 8.5 rules out is reachable with the
entry **present** rather than missing:

1. Reconciliation terminates run A for issue X — Section 8.5 Part B, or Part A's stall path.
   `terminate_running_issue` removes X's running entry and accounts for its runtime.
2. X is still an active candidate, so a later tick dispatches run B for it. Section 16.4 writes a
   **new** running entry under the same key.
3. Run A's exit — in flight since step 1 — arrives at `on_worker_exit(X, …)`.

The entry is present, so the guard does not fire. `on_worker_exit` removes it, adds run A's runtime
to the totals a second time, and schedules a retry for an issue whose run B is still executing. Run
B's own exit then arrives with no entry and is correctly a no-op — so **the orchestrator has
converted a live run into a queued retry and lost it**, which is the outcome Section 8.5's invariant
exists to prevent.

Section 16.7 also gives `on_worker_exit` no parameter it could decide with. It takes `(issue_id,
reason, state)`. The retry timer's fire was given `generation` for this reason and Section 4.1.7
carries the field; the running entry has no counterpart, and Section 4.1.8's `running` is keyed by
`issue_id` alone.

**The window is not sub-millisecond.** The harmful condition is `exit-delivery latency >
termination→re-dispatch latency`. On the stall path the re-dispatch happens after Section 8.4's
backoff, so the guard fails whenever a killed worker takes longer than one backoff to die — 10 s at
attempt 1, up to `agent.max_retry_backoff_ms` (default `300000`) later in a sequence, plus replay
latency in remote mode.

**Part B is not a live path today, and that is itself a defect.** Step 2 needs X to become a
candidate again, which Section 8.2 refuses while it is in `claimed` — and a run stopped by Part B is
never unclaimed. That is issue #108, decision 0145, and it is why this decision is ordered after it.
The stall path being the only live route today is a property of a bug rather than of the design.

## The guard belongs on the channel, not on the exit callback

The exit is one message. Section 16.6 sends agent events over the same seam, keyed by issue alone:

```text
    on_event=(msg) -> send(orchestrator_channel, {agent_update, issue.id, msg})
```

and Section 7.3's `Agent Update Event` applies them to the running entry — "Update live session
fields, token counters, and rate limits." A late event from run A landing on run B's entry is the
same defect as the late exit, and worse than a double-counted runtime in three ways:

- **`last_timestamp` is Section 8.5 Part A's stall reference.** Section 16.3 reads
  `running_entry.last_timestamp or running_entry.started_at`. A dead run's trailing events keep a
  genuinely stalled replacement alive, and stall detection is the one mechanism that would otherwise
  clean it up. This is the consequence with **no second line of defence** — the mechanism that would
  catch the stalled replacement is the one the stale events defeat — which is why it is listed
  first.
- **`session_id` and `pid` are overwritten**, so Section 13.1's REQUIRED `session_id` context names
  a session that is not the one producing the work.
- **The token deltas are computed between unrelated series.** Section 13.5 says "For absolute
  totals, track deltas relative to last reported totals to avoid double-counting", and the running
  entry holds `last_reported_*` for that. Two runs are two independent cumulative series; mixing
  them in one entry computes a delta between series neither produced. Section 8.8 enforces `Durable`
  budget counters on that number and keys its idempotency on the absolute snapshot — the property
  the mixing breaks.

The asymmetry inside that last point is the argument for guarding the **channel** rather than
hardening the fields: in the `symphony-rs` build `RateLimits::observe` orders by `fetched_at` rather
than by arrival (`crates/symphony-obs/src/ratelimit.rs:37-52`), so the rate-limit field already
survives a crossed delivery on its own, while `usage` is a high-water mark and `last_reported` is
what was last sent onward (`state.rs:69-72`) — a high-water mark across two independent cumulative
series is not a value either series produced. One field on the entry is idempotent under mixing and
the other is silently wrong. A per-field repair would have to be re-derived for every field added.

So the rule is one rule over the channel: **a worker-lifecycle message whose `run_id` does not equal
the `run_id` of the issue's current running entry MUST be discarded, leaving that entry and its
worker untouched** — phrased as Section 8.4 phrases its sibling, with the same second sentence, that
testing only whether a running entry is present does not satisfy it. The existing `if missing` case
is then subsumed: no entry means no match, and the no-op Section 8.5 relies on still follows.

## The identifier is one already owed in four places

Not a new `run_generation`. Three places already assume a run-attempt identifier exists and none
defines one:

- **Section 13.1 REQUIREs `origin_run_id`** of every session-lifecycle log record — "the run attempt
  whose failure produced this one", and the field is stated to be always present, never null. It
  names a run attempt; Section 4.1.5 lists `issue_id`, `issue_identifier`, `attempt`,
  `workspace_path`, `started_at`, `status`, `error`, and no id.
- **Section 9.11 calls `lookup_by_run_id(run_id)` and `signal_done(run_id)`** across the scheduler
  adapter, and Section 14.4's remote run registry is keyed by run.
- This guard is the fourth.

The `symphony-rs` report makes the argument sharper than the derivation does, and it belongs ahead
of it: `symphony-obs`'s `SessionRef` carries `origin_run_id` as a non-optional `String`
(`crates/symphony-obs/src/event.rs:148-151`) with a doc saying why it is there and what is missing —
"`SPEC §13.1` says it is never null … what is missing is the orchestrator that schedules a retry and
therefore knows the value". The observable cost today is that a runtime snapshot's running row
**reports no session at all**, because a `SessionRef` cannot be constructed without a value Section
4.1.5 does not define. So defining `run_id` on Section 4.1.5 does not add a fourth identity for one
thing; it retires a placeholder that has been typed and unpopulatable since the observability seam
landed.

**Its uniqueness requirement is wider than Section 8.4's `generation`, and the difference matters.**
The timer generation is compared only in memory, so Section 8.4's "MUST NOT be reused for an issue
for as long as the orchestrator process lives" is enough and an integer counter satisfies it. A
`run_id` is written to durable logs (Section 13.1) and handed to an external node-scheduler (Section
9.11), where a per-process counter restarting at 1 collides with the previous process's records.

## Review finding: which of the two identifiers the guard compares

Raised on the implementation reply to PR #114, against the compression of the section above rather
than against its content. "The identifier is one already owed in four places, not a fourth identity"
is true of the **definition** and says nothing about the **comparison**, and read as licence it
points at the wrong field. `origin_run_id` names the origin of a retry sequence rather than the
immediate predecessor — Section 13.1 states that "every attempt in the sequence carries one value",
which is the property that makes a sequence a group rather than a linked list — so an entry carrying
`origin_run_id` and a guard comparing against it fail in **exactly** the case this decision is
about: reconciliation terminates run A, a retry re-dispatches run B in the same sequence, both carry
one `origin_run_id`, and the stale exit matches.

So the two are one field's worth of definition and two fields' worth of use, and the repair is one
sentence in Section 4.1.5 rather than a caveat anywhere else (Plan step 1): a retried attempt
carries its own `run_id` and its origin's, `origin_run_id` being the `run_id` of the attempt the
sequence began at. That sentence also gives `origin_run_id` the type it has never had — Section 13.1
REQUIREs the field and states it is never null, and says nothing about what kind of value it is,
which is why the two could be conflated without contradicting anything written.

The same reply confirms the two claims step 2 turns on, from the build's side: the Section 16.1
process identity arrives at a sans-io orchestrator as an injected input rather than as something the
core reads, and the per-process counter behind `run_id` joins that build's existing retry-generation
counter under Section 14.3's not-closed rule — so the layering step 2 describes costs it no new
seam.

## Where the uniqueness comes from, and why it needs a stated source

This is the one part of the repair that does not fall out of the existing precedent, and leaving it
implicit would make the requirement unsatisfiable by the layer Section 16 puts the assignment in.

Section 8.4's generation is mintable inside a core that sees no world: it is a counter, so it is a
function of state. A `run_id` required not to be reused **across restarts** is not. Nothing inside
the orchestrator's own state distinguishes this process from the last one, so "non-reuse across
restarts, generation scheme `Implementation-defined`" reads as satisfiable by a counter until you
try to write one where the process boundary is invisible.

The specification cannot answer this by naming a host: `SPEC.md` is language- and framework-neutral
and has no host in it, and importing one to describe a layering would be picking an implementation.
It does not need to. **Section 16.1 is already the function that touches the world before the loop
starts** — `configure_logging()`, `start_observability_outputs()`, `start_workflow_watch(...)`,
`restore_cached_and_durable_state(state)` — so the value has a home in the document as it stands:

- Section 16.1 establishes a **process identity** once, before `event_loop(state)`, distinct from
  that of any previous process of the same deployment. How it is derived is `Implementation-defined`
  and MUST be documented — a persisted counter, a boot identifier, a start timestamp, a random
  value. The specification states the distinction the value must make and leaves the mechanism,
  exactly as `VCSX-SPEC.md` Section 9.1 does for `worktree_revision()`.
- Section 16.4's `dispatch_issue` composes `run_id` from that identity and a per-process counter.
- The guarantee is stated over what a consumer can check rather than over the scheme: **no two run
  attempts in one deployment share a `run_id`**, including across restarts. Section 13.1's
  `origin_run_id` and Section 9.11's `lookup_by_run_id` are the two places that falsify it.

That keeps the comparison inside the core and the mint out of the dispatch path, and makes the
non-reuse a property of a composition rather than an obligation with no stated source.

**The rejected shape: the host mints the whole id and reports it back.** Then the running entry
carries no id between dispatch and the first message, and the guard has a window in which it cannot
decide — which is the window this issue is about, relocated rather than closed. Section 16.4 writes
the entry immediately at dispatch and Section 16.6 keys every message off it, so an entry with no id
is an entry no message can be judged against.

**And the distinction is the guarantee, not a side effect of it.** Section 8.4's generation is safe
to reset at restart for a reason that is written down in the `symphony-rs` build: `next_retry_
generation` returns to zero in `after_restart`, and the reset is sound **only** because Section 14.4
restores no timer, so a fire from the previous process cannot arrive carrying a generation the new
counter could match (`crates/symphony-orchestrator/src/state.rs:453-459`). The run-id guard has no
such argument available to it. Its safety comes entirely from the identity *differing* across
processes — so a build whose simulated restart reuses the identity has a guard that is never
exercised and a suite that is green. That is the reason to phrase the requirement over the
distinction the value MUST make rather than over a scheme: "non-reuse across restarts, scheme
`Implementation-defined`" reads as satisfiable by a constant until the first test that needs it to
differ.

## The shape, not only the field

Decision 0136 changed `on_retry_timer` from pop-then-test to **get-compare-remove**, "because a
comparison that fails after the pop has already taken the entry the fire should not have touched".
`on_worker_exit`, eleven lines above it in the same code block, still opens with `running_entry =
state.running.remove(issue_id)` — so a mismatched exit removes run B's entry before it discovers it
should not have. The sibling repair changed two things and `on_worker_exit` inherited neither. Both
are owed here.

## What it costs, stated

This touches a Core entity (Section 4.1.5) and the worker→orchestrator message shape (Section 16.6),
which is a wider blast radius than a guard inside one function. It is offset by `origin_run_id` and
`lookup_by_run_id` already needing the identifier it defines, and by the timing on the
implementation side: the wider scope lands in an unbuilt slice there rather than widening a merged
one.

It adds one `Implementation-defined` + MUST-document obligation — the process identity — so
`CONFORMANCE-STATEMENT-TEMPLATE.md` owes it a row and `SPEC.md` Section 19 owes it a line. That is
`CLAUDE.md`'s rule and decision 0128's lesson, and it is named here so the decision carries it from
the start rather than picking it up downstream.

## Options considered

### Say that a terminated run's exit can never overlap a re-dispatch

The smaller edit: state in Section 8.5, beside the existing invariant, that Section 16 requires the
exit to be reaped before the issue can be a candidate again, and no new field is needed. It is the
same shape as issue #95's own alternative, which decision 0136 recorded and rejected "for putting a
liveness obligation on the host's timer facility, which a sans-io core cannot check". Here it is the
host's *process* facility, and it is worse on two counts:

- `terminate_worker` is not synchronous with the process dying, and the path that reaches this race
  is the stall path — a worker that has already stopped producing events, which is the case selected
  for being slow to die. Making dispatch wait for the exit means blocking the poll tick on an
  unbounded wait, which Sections 16.2 and 16.3 avoid everywhere else (a failed state refresh keeps
  workers running and tries the next tick rather than waiting).
- In remote mode (Section 9.11) the exit crosses a network seam whose events are buffered and
  replayed on reconnect **by design** (Section 14.4). The orchestrator cannot bound its arrival at
  all, so the constraint is not stateable for a conforming remote deployment.

Every containment that actually works needs an identifier — a tombstone set of terminated runs, a
per-run reply channel, keying `running` by run — so the choice is not "identifier versus no
identifier" but "identifier versus an ordering guarantee the document cannot make".

### A new `run_generation` on the running entry, mirroring Section 8.4 exactly

The narrowest field: an in-memory integer per running entry, compared like the timer generation,
with Section 8.4's process-lifetime uniqueness. It fixes the exit race and nothing else, and it is
genuinely cheaper — no durable requirement, no process identity, no Section 19 row.

It loses because it is a **fourth** identity for a thing three places already name, and the three
that name it need the wider uniqueness the narrow one cannot give: an `origin_run_id` written to a
log and a `run_id` handed to a node-scheduler both outlive the process. Shipping both would mean an
orchestrator holding two ids per run whose relationship no section states.

### Guard the exit callback alone, leaving `agent_update` unguarded

Half the edit, and it closes the reported defect. It loses on `last_timestamp`: a dead run's
trailing events keeping a stalled replacement alive is a liveness bug with no second line of
defence, and it is reachable by the same construction with no exit involved at all.

## What was checked

At `22b5194`, against the working tree:

- Section 16.7's `on_worker_exit(issue_id, reason, state)` takes three parameters and opens with
  `state.running.remove(issue_id)`; `on_retry_timer(issue_id, generation, state)` takes four and
  opens with `state.retry_attempts.get(issue_id)` followed by the generation comparison and only
  then the removal.
- Section 4.1.5 lists seven fields and no identifier; Section 4.1.7 lists `generation` with the
  wording quoted above; Section 4.1.8's `running` is a map `issue_id -> running entry`.
- Section 13.1's `origin_run_id` bullet says "The first attempt of a run is its own origin, so the
  field is always present — a nullable one would invite a consumer to branch on an absence that
  names no condition."
- Section 9.11 defines `lookup_by_run_id(run_id) -> endpoint` and `signal_done(run_id)`; Section
  14.4 keys the remote run registry by run and calls `lookup_by_run_id` on restart.
- Section 16.6's event send is `send(orchestrator_channel, {agent_update, issue.id, msg})`, keyed by
  issue; Section 7.3's `Agent Update Event` applies it to live session fields, token counters and
  rate limits.
- Section 16.3's stall reference is `running_entry.last_timestamp or running_entry.started_at`.
- Section 13.5 requires deltas relative to last reported totals; the running entry in Section 16.4
  carries `last_reported_input_tokens`, `last_reported_output_tokens`, `last_reported_total_tokens`.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## On vectors

`conformance/vectors/worker-exit-disposition.json`, mirroring `retry-fire-disposition.json`: the
same one-shot pure-function shape, `{ entry: { run_id, … } | null, exit_run_id }` → `{ disposition:
'account' | 'discard', entry_retained: boolean }`. The `entry_retained` flag is part of the answer
rather than the caller's business, for the reason the sibling already carries: returning whether the
entry survived is what makes get-compare-remove the only implementation the signature admits, and
`entry_retained: true` on the stale case is the half a remove-first implementation fails. In the
`symphony-rs` build the mirror is a transcription of an existing signature
(`crates/symphony-orchestrator/src/fire.rs:34-88`), which is the cheapest possible form for it.

## Reconsideration triggers

- **A second worker→orchestrator message that is not run-scoped.** The rule is stated over
  worker-lifecycle messages; a message about the issue rather than the run would need to say so
  rather than be discarded by a guard that cannot tell the difference.
- **A deployment where the process identity cannot be made distinct** — an environment with no
  persistence, no clock and no entropy at startup. The requirement is stated over the distinction
  rather than the scheme precisely so such an environment has to declare its degradation rather than
  satisfy the clause with a constant; if one arrives, the `UNKNOWN`-shaped answer is a documented
  degradation, not a weakened guarantee.
- **`running` being re-keyed by run rather than by issue.** That would make the guard structural
  rather than a comparison, and would reopen whether the field belongs on the entry at all — but it
  changes Section 8.2's `running` test and every reader of the map, so it is a larger decision than
  this one.
