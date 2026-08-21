# Plan — 0138 The function five call sites named and no section defined

## Scope

- `SPEC.md` — Section 7.3 (Transition Triggers), Section 8.5 (Active Run Reconciliation), Section 16.3
  (Reconcile Active Runs), Section
  16.7 (Worker Exit and Retry Handling), Section 17.4 (Orchestrator Dispatch, Reconciliation, and
  Retry), Section 18.1.3 (Daemon Conformance).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. The decision fixes behaviour the document had
  left to chance; it adds no `Implementation-defined` behaviour and no "MUST document" obligation, so
  no row is owed (`CLAUDE.md`, decision 0128).
- `conformance/vocabulary.json` — **no change**. `schedule_retry` and `terminate_running_issue` are
  reference-algorithm function names, and no vocabulary group publishes those.
- `conformance/vectors/` — **no change**. Both repairs are about which of several state transitions
  happens and in what order, not about a value computed from inputs; the eight existing files are
  one-shot pure functions and there is no sequenced vector shape to express an ordering in. This is
  the same bound that ruled out decision 0136's due-scan option, and it is recorded here so a later
  reader does not read the absence as an oversight.
- `SPEC.md` Section 6.4 — **no change**. No configuration key is involved.
- `SPEC.md` Section 8.4 — **no change**. Its Retry-entry-creation bullets are the normative source
  `schedule_retry`'s body is written *from*; decision 0136 edits them, this decision does not.

## Ordering against decisions 0136 and 0137

Apply this decision **before** 0136's Section 16.7 steps. 0136 changes `on_retry_timer`'s shape from
`pop`-then-test to get-compare-remove, and states that `schedule_retry` assigns the generation — a
claim about a function body that only exists once step 1 below has run. Applying 0136 first leaves
its central clause pointing at nothing. This decision is independent of 0137.

## The test used to classify a gap

A name Section 16 calls and does not define is a **gap** if a reader cannot supply its body without
changing behaviour the specification states elsewhere; it is a **primitive** otherwise. Reproduce
the call/define inventory with:

```text
python3 - <<'PY'
import re
s = open('SPEC.md').read()
sec = s[s.index('## 16.'):s.index('\n## 17.')]
called  = set(re.findall(r'(?<![\w.])([a-z_][a-z0-9_]{3,})\(', sec))
defined = set(re.findall(r'^\s*(?:function\s+)?([a-z_][a-z0-9_]*)\(.*\)\s*:\s*$', sec, re.M))
print(sorted(called - defined - {'if','for','while','return','and','or','not','format'}))
PY
```

At `cbc7d8a` that is 8 defined and 43 called-but-undefined. Of the 43, three (`available_slots`,
`sort_for_dispatch`, `normalize_state`) are pinned by `conformance/vectors/` and are therefore not
gaps; `schedule_retry`, `terminate_running_issue` and `reconcile_stalled_runs` are the three this
decision closes. The remainder
are primitives under the test above and are deliberately left unwritten. Re-running the inventory
after this decision should report three fewer called-but-undefined names and three more definitions.

## Steps

1. **`SPEC.md` Section 16.7 (Worker Exit and Retry Handling) — `schedule_retry` has a body.** Ensure
   a `text` block defines `schedule_retry(state, issue_id, attempt, opts)` performing what Section
   8.4 requires in prose and nothing beyond it: cancel any timer already armed for `issue_id`,
   compute the delay from `opts.delay_type` (the fixed `1000` ms continuation delay, else
   `min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)`), store `attempt`, `identifier`,
   `error`, `due_at_ms` and the new timer handle into `state.retry_attempts[issue_id]`, and arm the
   timer. Place it before `on_worker_exit`, since both later functions call it. Use the neutral
   `snake_case` pseudocode register the section already uses. *Done when:* Section 16.7 defines
   `schedule_retry`, its body states nothing Section 8.4 does not, and all five existing call sites
   type-check against its parameter list unchanged.
2. **`SPEC.md` Section 16.3 (Reconcile Active Runs) — `terminate_running_issue` has a body, and it
   owns the removal.** Ensure a `text` block defines
   `terminate_running_issue(state, issue_id, cleanup_workspace)` that removes the entry from
   `state.running`, adds that run's runtime seconds to `state.agent_totals` before discarding it,
   terminates the worker, cleans the workspace when `cleanup_workspace` is true, and schedules no
   retry. *Done when:* Section 16.3 defines it, the two existing call sites are unchanged, and the
   accounting that `on_worker_exit` performs for an ordinary exit is performed here for a terminated
   one — so no run's runtime seconds are lost and none is counted twice.
3. **`SPEC.md` Section 16.3 (Reconcile Active Runs) — `reconcile_stalled_runs` has a body, and it
   is where Part A's retry is queued.** Ensure a `text` block defines `reconcile_stalled_runs(state)`
   that returns `state` unchanged when `codex.stall_timeout_ms <= 0`, and otherwise, for each
   running issue whose `elapsed_ms` since `last_timestamp` — or `started_at` where no event has been
   seen — exceeds it, calls `terminate_running_issue(state, issue_id, cleanup_workspace=false)` and
   then `schedule_retry` for that issue. The workspace is kept because Section 9.1 reuses workspaces
   "across runs for the same issue" and the retry is a further run of the same issue. *Done when:*
   Section 16.3 defines it, the call site at `reconcile_running_issues`'s first line is unchanged,
   and Section 8.5 Part A's "terminate the worker and queue a retry" has exactly one producer.
4. **`SPEC.md` Section 16.7 — `on_worker_exit` guards on a missing entry.** Ensure the function
   returns `state` unchanged when `state.running` holds no entry for `issue_id`, before
   `add_runtime_seconds_to_totals` or any `schedule_retry` call is reached. *Done when:* the guard is
   the first statement after the removal, it matches `on_retry_timer`'s existing `if missing` in
   register, and neither the `normal` nor the `else` branch is otherwise changed.
5. **`SPEC.md` Section 8.5 (Active Run Reconciliation) — the invariant is stated in prose, not left
   to the pseudocode.** Ensure Section 8.5 states that reconciliation which terminates a worker
   removes that issue's running entry and accounts for its runtime at the point of termination, and
   that a worker exit for an issue with no running entry is a no-op — so a termination the
   orchestrator initiated never produces a retry the orchestrator did not ask for. Ensure Part A
   still queues its retry and Part B still queues none. *Done when:* Section 8.5 carries the
   invariant, both parts keep their existing retry behaviour, and the `Important:` or `Note:` aside
   label used is one the document already uses.
6. **`SPEC.md` Section 7.3 (Transition Triggers) — the two worker-exit triggers agree with the
   invariant.** Ensure `Worker Exit (normal)` and `Worker Exit (abnormal)` record that their steps —
   "Remove running entry", "Update aggregate runtime totals" and the retry — apply to an exit the
   orchestrator did not initiate, and that an exit for an issue with no running entry triggers
   nothing, because reconciliation has already removed the entry and accounted for the run. Ensure
   `Stall Timeout` still reads as killing the worker and scheduling a retry, and that
   `Reconciliation State Refresh` records that stopping a run whose issue went terminal schedules no
   retry. *Done when:* Section 7.3's triggers and Section 8.5's invariant state the same thing, and
   no trigger name is added or removed.
7. **`SPEC.md` Section 8.5 — the two consequences are named where a reader will look for them.**
   Ensure the section records that a stalled run therefore queues exactly one retry rather than two,
   and that an issue whose tracker state went terminal queues none — the second being why a closed
   issue does not hold a claim, and a slot, until a backoff elapses. *Done when:* both consequences
   are stated, and the second names `claimed` and `available_slots` so the cost is traceable to
   Section 8.3.
8. **`SPEC.md` Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry) — the matrix carries
   both.** Ensure a `Daemon Conformance` bullet sits with the reconciliation bullets, the relevant
   one of which is "Stall detection kills stalled sessions and schedules retry", asserting that a
   stalled run schedules exactly one retry and that a run terminated because its issue went terminal
   schedules none and releases its claim without waiting for a backoff. *Done when:* Section 17.4
   carries the bullet with its marker and no existing bullet is removed.
9. **`SPEC.md` Section 18.1.3 (Daemon Conformance) — the checklist covers the invariant.** Ensure the
   item that reads "Exponential retry queue with continuation retries after normal exit" — or the
   reconciliation item beside it, whichever reads more naturally once decision 0136 has extended the
   first — also requires that an orchestrator-initiated termination not produce a second retry,
   citing Section 8.5. *Done when:* the behaviour appears once in Section 18.1.3 and no duplicate
   bullet is introduced.
10. **`conformance/README.md` — the finding is recorded.** Ensure a "Surfaced findings" entry states
   the gap in the terms the corpus meets it: `schedule_retry` had five call sites and no body,
   `on_worker_exit` had no `if missing` guard where its eleven-lines-distant sibling did, and the
   two reachable paths that reach it with the entry already gone. Record that no vector is owed and
   why. *Done when:* the entry names decision 0138, records that it came from checking #95 rather
   than from an issue, and states the claim-and-slot cost of the terminal-issue path.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change; see Scope.
- `SPEC.md` Section 17 (test matrix) — step 8, one bullet in Section 17.4.
- `SPEC.md` Section 18 (implementation checklist) — step 9, one existing bullet extended rather than
  a new one added.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed and none added; see Scope.
- `conformance/vocabulary.json` — unchanged; see Scope.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. Worker
  lifecycle and retry scheduling are the orchestrator's, not the engine's.

## Anchor changes

- **Added:** `schedule_retry` as a defined function in Section 16.7, and `terminate_running_issue`
  and `reconcile_stalled_runs` as defined functions in Section 16.3. All three names already existed
  as call sites; none is renamed.

Nothing is renamed or removed. `on_worker_exit`, `on_retry_timer`, `reconcile_running_issues`,
`reconcile_stalled_runs`, `add_runtime_seconds_to_totals`, `next_attempt_from`, `running`, `claimed`
and `agent_totals` all keep their spelling.

## Status

Proposed. Found while checking issue #95; reported by neither issue.
