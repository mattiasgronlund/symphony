# Plan — 0136 A timer fire that could not name the arming it came from

## Scope

- `SPEC.md` — Section 4.1.7 (Retry Entry), Section 8.4 (Retry and Backoff), Section 16.7 (Worker
  Exit and Retry Handling), Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry), Section
  18.1.3 (Daemon Conformance).
- `conformance/vectors/retry-fire-disposition.json` — new file, three vectors.
- `conformance/README.md` — one row in the behavior-vector table and one "Surfaced findings" entry.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. The decision states a behaviour the document
  had left unstated and adds no `Implementation-defined` behaviour and no "MUST document"
  obligation, so no row is owed (`CLAUDE.md`, decision 0128). It deliberately declines the
  due-time option partly *because* that one would have owed a row for its clock slack.
- `conformance/vocabulary.json` — **no change**. `runtime_state_fields` publishes Section 4.1.8's
  fields; `generation` is a Section 4.1.7 field and there is no group for those.
- `SPEC.md` Section 6.4 — **no change**. No configuration key is involved.

## Dependency

The non-reuse clause in step 2 relies on the orchestrator holding a generation counter that outlives
a `RetryEntry`, which is Core-introduced runtime state with no Section 4.1.8 field. Decision 0137
widens Section 14.3 to admit exactly that. This plan does not add a field for the counter and does
not restate the recovery-class rule; if 0137 is not applied, step 2 leaves state that Section 14.3
as it stands does not admit, and that is the coupling to check before landing this alone.

## Steps

1. **`SPEC.md` Section 4.1.7 (Retry Entry) — the entry carries a generation.** Ensure the field list
   retains `issue_id`, `identifier`, `attempt`, `due_at_ms`, `timer_handle` and `error`, and gains
   `generation` (integer) with a parenthetical naming it as the identity of the arming this entry
   owns, so a fire from a cancelled arming is distinguishable from one from the live arming. Place
   it next to `attempt`, per the report's ask. *Done when:* Section 4.1.7 lists seven fields and
   `generation` is one of them.
2. **`SPEC.md` Section 8.4 (Retry and Backoff) — creation assigns a generation and the value is not
   reused.** Ensure the Retry entry creation bullets retain "Cancel any existing retry timer for the
   same issue." and extend the storage bullet so `generation` is stored with `attempt`,
   `identifier`, `error`, `due_at_ms` and the timer handle, and so the armed timer carries the same
   value back on its fire. Ensure a clause states that a generation value MUST NOT be reused for an
   issue for as long as the orchestrator process lives, and that this holds across the removal of an
   entry, so a counter derived only from an entry that has been removed does not satisfy it. *Done
   when:* Section 8.4 states both that the fire carries the generation and that values are not
   reused, and neither existing bullet is removed.
3. **`SPEC.md` Section 8.4 (Retry and Backoff) — a `Note:` records why identity rather than time.**
   Ensure a note states that the continuation delay is a fixed `1000` ms, so two continuation
   schedules taken at the same instant produce entries a due-time comparison cannot separate, which
   is why the fire is matched on identity rather than on being due. Follow the aside label set the
   document already uses. *Done when:* Section 8.4 carries one `Note:` naming the fixed continuation
   delay as the reason, and introduces no `Implementation-defined` behaviour.
4. **`SPEC.md` Section 16.7 (Worker Exit and Retry Handling) — `on_retry_timer` takes the generation
   and does not remove a live entry.** Ensure `on_retry_timer` takes `(issue_id, generation, state)`
   and reads the entry without removing it, returns `state` unchanged when no entry is present,
   returns `state` unchanged when `generation` does not equal the entry's `generation`, and only
   then removes the entry and proceeds into the existing candidate fetch, `find_by_id`,
   `available_slots` and `dispatch_issue` flow unchanged. The `pop`-then-test shape MUST NOT
   survive: a stale fire must leave both the live entry and its live timer as it found them. *Done
   when:* the function's first statement is a non-removing read, there are two distinct early
   returns before any removal, and the tail from `candidates = tracker.fetch_candidate_issues()`
   onward is unchanged.
5. **`SPEC.md` Section 16.7 — the four `schedule_retry` call sites in this section stay
   consistent.** Ensure the calls in `on_worker_exit` and `on_retry_timer` are unchanged in
   argument shape by this decision; the generation is assigned inside `schedule_retry`, not passed
   by its callers. *Done when:* no call site gains a generation argument, and the only signature
   this decision changes is `on_retry_timer`'s.
6. **`SPEC.md` Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry) — the matrix carries
   the stale-fire check.** Ensure a `Daemon Conformance` bullet sits with the retry bullets, the
   first of which is "Normal worker exit schedules a short continuation retry (attempt 1)",
   asserting that a timer fire whose generation does not match the current entry's is discarded
   without dispatching and without disturbing the entry, and that a fire arriving with no entry
   present is likewise a no-op. *Done when:* Section 17.4 carries the bullet with its
   `Daemon Conformance` marker and no existing retry bullet is removed.
7. **`SPEC.md` Section 18.1.3 (Daemon Conformance) — the checklist item covers the discard.** Ensure
   the item that reads "Exponential retry queue with continuation retries after normal exit" also
   requires a retry timer fire to be matched to its arming by `generation` and discarded when it
   does not match, citing Section 8.4. *Done when:* the bullet names both behaviours and no second
   bullet is added for it.
8. **`conformance/vectors/retry-fire-disposition.json` — the disposition is pinned.** New file for
   `retry_fire_disposition`, profile `Daemon`, `spec_refs` naming Sections 8.4 and 16.7, following
   the `{function, profile, spec_refs, description, given, expect, vectors}` shape the other eight
   files use. `given` is the current entry (or `null`) and the arriving fire's generation; `expect`
   is `dispatch` or `discard`. Three vectors: `fire-generation-matches` → `dispatch`;
   `fire-generation-stale` → `discard`, with a description recording that the entry MUST still be
   present afterwards, which is the half a `pop`-first implementation fails; `fire-with-no-entry` →
   `discard`. *Done when:* the file parses, carries exactly those three ids, and reads no clock in
   any `given`.
9. **`conformance/README.md` — the new file is registered and the finding recorded.** Ensure the
   behavior-vector table gains a row `| `vectors/retry-fire-disposition.json` |
   `retry_fire_disposition` | Daemon | Sections 8.4, 16.7 |` beside the existing
   `vectors/retry-backoff.json` row, and that a "Surfaced findings" entry states the gap in the
   terms the corpus meets it: Section 8.4 required cancel-on-replace, Section 16.7 identified a fire
   by `issue_id` alone, and `if missing` tested presence rather than identity. *Done when:* the
   entry names decision 0136, issue #95, and the three vector ids.

## Anchor reach

`scripts/check_plan_anchors.py --rev cbc7d8a` reported three sites carrying wording this plan
quotes. Each is dispositioned rather than left open:

- `SPEC.md:1552` (Section 9.1) carries "for the same issue" in "Workspaces are reused across runs for
  the same issue." **No change.** A different sentence about a different subject; the match is the
  four-word window, not the claim.
- `SPEC.md:1081` (Section 7.1) carries "schedules a short continuation retry (about 1 second)".
  **No change.** Section 7.1 states *when* a continuation retry is scheduled; this decision changes
  how an arriving fire is identified, which Section 7.1 does not describe.
- `SPEC.md:1121` (Section 7.3) carries "Schedule continuation retry (attempt `1`)" under
  `Worker Exit (normal)`. **Changed, by decision 0138, not by this one.** Section 7.3's worker-exit
  triggers are reached by 0138's invariant about which exits act, and that decision's plan names the
  section. Recorded here because this plan's quotation is what surfaced it.

## Why the `if missing` branch is kept

Step 4 retains an early return for a fire arriving with no entry, and the corpus keeps a vector for
it, so a later reader does not remove either as unreachable. Under first-in-first-out delivery it
*is* unreachable — an entry is removed only by a matching fire, and every earlier arming's fire was
enqueued earlier and so dequeued earlier. Its producer is the same one the non-reuse clause in step
2 exists for: the document states no delivery-ordering property, so a branch that depends on there
being one is not a branch this specification can drop.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change; no configuration key is involved.
- `SPEC.md` Section 17 (test matrix) — step 6, one bullet in Section 17.4.
- `SPEC.md` Section 18 (implementation checklist) — step 7, one existing bullet in Section 18.1.3
  extended rather than a new one added.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed and none added; see Scope.
- `conformance/vocabulary.json` — unchanged; see Scope.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. Retry
  scheduling is the orchestrator's, not the engine's.

## Anchor changes

- **Added:** `generation`, a field of `Retry Entry` (Section 4.1.7).
- **Changed:** `on_retry_timer`'s signature, from `(issue_id, state)` to
  `(issue_id, generation, state)`. The function name is unchanged.
- **Added:** `retry_fire_disposition`, a conformance-vector function name, and the vector ids
  `fire-generation-matches`, `fire-generation-stale` and `fire-with-no-entry`.

Nothing is renamed or removed. `attempt`, `due_at_ms`, `timer_handle`, `error`, `identifier`,
`issue_id`, `schedule_retry`, `on_worker_exit` and `dispatch_issue` all keep their spelling.

## Status

Applied to `SPEC.md` (Sections 4.1.7, 8.4, 16.7, 17.4, 18.1.3),
`conformance/vectors/retry-fire-disposition.json` and `conformance/README.md`. Issue #95.
