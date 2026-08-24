# Background — 0145 The claim nothing released

## Context

Issue #108, filed by the `symphony-rs` build against `SPEC.md` Sections 16.3 and 7.1. Section 7.1
defines a claim state reached when a run is stopped:

> 6. `Released`
>    - Claim removed because issue is terminal, non-active, missing, or retry path completed without
>      re-dispatch.

and Section 17.4 requires that release to happen without a backoff elapsing first:

> - A run stopped because its issue reached a terminal or non-active state schedules no retry, and
>   its claim is released without waiting for a backoff to elapse

Section 16 mutates `claimed` in exactly two places: `state.claimed.add(issue.id)` in
`dispatch_issue`, and `state.claimed.remove(issue_id)` in `on_retry_timer`, on the branch where the
issue is no longer a candidate. `terminate_running_issue` — the function both branches of Section
8.5 Part B call, and the one Part A's stall path calls — removes the running entry, accounts for the
runtime, terminates the worker, optionally cleans the workspace, and **does not touch `claimed`**.
Section 8.5 Part B schedules no retry, by design (decision 0138).

So the release is reachable only through a retry entry, and the path that most needs it creates
none.

## The release was a side effect of the retry decision 0138 correctly removed

Before 0138, Part B's terminated worker reached `on_worker_exit` and unconditionally scheduled a
retry. 0138 records what that retry did: "It self-cancels one backoff later via `find_by_id -> null
-> claimed.remove`, so the cost is a wasted timer and a held claim rather than corruption". That
self-cancel was the **only producer** of the release. `git log -S"claim is released without
waiting"` and `git log -S"function terminate_running_issue"` both return `87abf10` — the commit that
removed the retry is also the commit that added the Section 17.4 row asserting the release.

This is the shape of 0138's own recorded review finding, one step over. That one kept Part A's retry
while removing its only producer; this one keeps a **release** whose only producer it removed. The
premise was "a retry for a closed issue is waste"; the consequence that did not survive it is "the
claim comes off when the retry fires".

## What it costs, and what it does not

**The issue is permanently un-dispatchable.** Section 8.2 tests "It is not already in `claimed`", so
a ticket closed while its worker was running and later reopened is a candidate the orchestrator
fetches every tick and skips every tick. `claimed` is `Reconstructable` and Section 16.1 starts it
empty, so a restart clears it — which makes the symptom "reopened tickets are ignored until Symphony
is restarted", a shape that reads as a tracker-adapter problem rather than a scheduler one.

**`claimed` grows monotonically** for the life of the process: one entry per issue closed or moved
non-active while its worker was running, never reclaimed.

**It costs no concurrency slot, and the claim that it did is withdrawn.** The issue as filed drew a
third consequence conditioned on which of two contradictory statements is believed, and issue #109
settled that: `available_slots = max(max_concurrent_agents - running_count, 0)`, pinned by four
vectors, and Section 8.5's "because `claimed` counts against `available_slots`" is the false
sentence. Decision 0144 carries that settlement. Under it, a claimed-but-not-running issue holds no
slot at all, and the earlier statement on this thread that the leak "permanently consumes a
concurrency slot" is withdrawn rather than merely unstated. The two consequences above do not depend
on the contradiction and were stated correctly.

## A second edge in the same place

Section 16.4's spawn-failure path arms a retry for an issue it never claimed:

```text
  if worker spawn failed:
    return schedule_retry(state, issue.id, next_attempt(attempt), {
      identifier: issue.identifier,
      error: "failed to spawn agent"
    })

  state.running[issue.id] = { … }
  state.claimed.add(issue.id)
```

`claimed.add` is below the early return, so on that path Section 16.7's comment ("The issue is
already in `state.claimed` from `dispatch_issue` and stays claimed while it is queued for retry") is
false, and nothing in Section 8.2 tests `retry_attempts`. The next tick re-dispatches the issue
while its retry is still armed, and because a tick dispatches with `attempt=null` the attempt count
restarts — so a repeatedly failing spawn retries every `polling.interval_ms` (default `30000`)
indefinitely instead of escalating toward `agent.max_retry_backoff_ms` (default `300000`).

No double dispatch results: `dispatch_issue`'s success path removes the retry entry, and after
decision 0136 the orphaned fire is discarded. **What is lost is the backoff, on the path whose whole
purpose is to back off.**

## Decision: state the invariant, not the two edits

The two clauses are the right edits:

- `terminate_running_issue` releases the claim when it removes the running entry — it is removing
  the thing the claim was held for;
- `schedule_retry` takes the claim (`state.claimed.add(issue_id)`), so `RetryQueued` is claimed by
  construction rather than by inheritance from `dispatch_issue`.

But read as two rules, a later reader has to check for themselves that they cover everything. They
do, and the reason is checkable, so the specification should say it as a **partition**: after the
two clauses, every site that removes a running entry either releases the claim or hands it to a
retry entry, and there is no third.

- `terminate_running_issue` — releases. Section 8.5 Part A's stall path and both Part B branches
  reach it.
- `on_worker_exit` — removes the entry directly and arms a retry, which takes the claim under the
  second clause. (Under decision 0146's get-compare-remove it removes nothing on a mismatched exit,
  so that path needs no claim rule at all.)
- Section 16.4's spawn-failure early return — the second edge above. Today it arms a retry for an
  issue it never claimed; under the second clause the retry takes the claim, which is what makes
  Section 16.7's existing comment true on that path rather than on all-but-one.

Stated as a partition, Section 7.1's `Released` state becomes **derivable from Section 16** rather
than asserted beside it, and the next site added has to say which side it is on. Stated as two
edits, a third removal site added later is a new leak with no rule against it — which is exactly the
shape this defect has, since 0138 removed the only producer of a release the document kept
asserting.

Section 16.4's other early return — the `ensure_object_store` failure — needs no clause and is worth
naming so the partition is seen to be complete: it returns before any entry is written and its own
comment already says the issue is left unclaimed so a later tick retries it.

## The alternative that loses, and the reason is `Provisioning`

**State `claimed` as a derived view** — `keys(running) ∪ keys(retry_attempts)` — and delete both
mutation sites. This is the first thing a reader reaches for, and Section 4.1.8 already describes
exactly that derivation for restart: `claimed` is `Reconstructable`, "re-derived from `running` and
`retry_attempts`". It would make the release **unfalsifiable** rather than merely required, which is
strictly stronger than a partition an implementation has to maintain. It is also one fewer field.

It loses on `Provisioning` (Section 7.1 state 3, Section 9.11). A remote dispatch that has requested
a node and brought up no executor is a run the orchestrator has committed to; under decision 0144 it
holds a running entry, so the derivation covers it — but the derivation's soundness then depends
entirely on that decision's phase reading, and the explicit set is what holds the property while the
entry's existence is being argued about. More decisively: the derived view makes duplicate-dispatch
prevention a *consequence* of two other collections' contents rather than a claim the orchestrator
takes. Section 8.2's `claimed` condition is the only thing standing between a slow acquire and a
second dispatch of the same issue, and deriving it means any future path that writes a run without a
`running` entry silently reopens duplicate dispatch, with no rule violated. The explicit set is
load-bearing for remote mode, which is why the answer is to maintain it rather than to derive it.

The two decisions agree and it is worth them saying so: 0144 settles when the running entry exists,
this one settles what its removal releases. Together, a provisioning run that never reached an agent
is released by `terminate_running_issue` with no extra clause.

## What was checked

At `22b5194`, against the working tree:

- `claimed` appears in `SPEC.md` at fifteen places; the two mutations in Section 16 are
  `SPEC.md:4076` (`dispatch_issue`) and `SPEC.md:4274` (`on_retry_timer`). `terminate_running_issue`
  (Section 16.3) does not name it.
- Section 16.4's spawn-failure `return schedule_retry(...)` precedes both `state.running[issue.id] =
  { … }` and `state.claimed.add(issue.id)`; the `ensure_object_store` failure returns earlier still,
  with the comment "leave the issue unclaimed so a later tick retries it".
- Section 16.2 dispatches with `attempt=null`; `schedule_retry`'s backoff is `min(10000 * 2^(attempt
  - 1), config.agent.max_retry_backoff_ms)`, so a restarted attempt count restarts the backoff at
  `10000`, under `polling.interval_ms`'s default of `30000`.
- Section 4.1.8 classes `claimed` as `Reconstructable` "re-derived from `running` and
  `retry_attempts`"; Section 16.1 initializes it as `set()`.
- Section 17.4 carries the release row verbatim as quoted above.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

Reported from the `symphony-rs` side, and it changes the sequencing rather than the diagnosis:
`claimed` is `Reconstructable<BTreeSet<String>>` and comes back empty after a restart
(`crates/symphony-orchestrator/src/state.rs:171`, `:414`), and **nothing mutates it yet** — the
dispatch tick that would is unbuilt. So the leak has no site to occur at, and the lifetime rule
lands before the mutation sites are written rather than after.

## Reconsideration triggers

- **A fourth site that removes a running entry.** The partition is stated over the sites that exist;
  a new one is not covered by analogy, and the rule is written so that adding one forces the
  question rather than admitting a silent third case.
- **A claim held for something that is not a run** — a reservation taken before dispatch, a
  cross-instance lease. `claimed` today means "this orchestrator has committed to this issue", and
  every clause here assumes a running entry or a retry entry is what the commitment is for.
- **`running` ceasing to cover the provisioning window.** That is decision 0144's phase reading; if
  it is reversed, the derived-view alternative should be re-read, because the argument against it
  above rests partly on the entry existing during acquisition.
