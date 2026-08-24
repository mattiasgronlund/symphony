# Plan — 0146 Run-attempt identity and the messages a replaced run keeps sending

## Scope

- `SPEC.md` — Section 4.1.5 (Run Attempt), Section 4.1.8 (Orchestrator Runtime State), Section 8.5
  (Reconciliation), Section 16.1 (Service Startup), Section 16.4 (`dispatch_issue`), Section 16.6
  (Worker Attempt), Section 16.7 (`on_worker_exit`), Section 7.3 (Transition Triggers), Section 17.4
  (test matrix), Section 18.1.3 (implementation checklist), Section 19 (Conformance Statement).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 4.1, one new row.
- `conformance/vectors/worker-exit-disposition.json` — new.

## Steps

1. **`SPEC.md` Section 4.1.5 — the run attempt gains `run_id`.** Ensure the entity carries an
   identifier for the run attempt, stated with the property a consumer can check: no two run
   attempts in one deployment share a `run_id`, including across process restarts. Ensure the
   derivation is `Implementation-defined` and MUST be documented, and that the section names the two
   places that falsify the property — Section 13.1's `origin_run_id` and Section 9.11's
   `lookup_by_run_id`. Ensure the field is not optional and has no null value. Ensure the section
   states the relation between the two identifiers in Section 13.1's own terms: a retried attempt
   carries its own `run_id` **and** its origin's, `origin_run_id` being the `run_id` of the attempt
   the sequence began at — which is also the type `origin_run_id` has never been given. *Done when:*
   `origin_run_id`, `lookup_by_run_id`, `signal_done` and the guard below all name a field this
   section defines, the uniqueness clause is stated over the distinction rather than over a
   generation scheme, and no reader can take `origin_run_id` for the value step 7's guard compares —
   every attempt in one retry sequence carries the same one.
2. **`SPEC.md` Section 16.1 — a process identity, established before the loop.** Ensure
   `start_service()` establishes an identity for this process, distinct from that of any previous
   process of the same deployment, before `event_loop(state)`, alongside the other functions that
   touch the world there. Ensure its derivation is `Implementation-defined` and MUST be documented
   (Section 19), stated on the `worktree_revision()` precedent — the specification fixes the
   distinction the value must make and leaves the mechanism. Ensure no host, runtime or framework is
   named. *Done when:* `run_id`'s across-restart uniqueness has a stated source inside Section 16,
   and an implementation whose orchestrator state alone cannot see the process boundary can still
   satisfy it.
3. **`SPEC.md` Section 16.4 — `dispatch_issue` composes and records the `run_id`.** Ensure the
   running entry written at dispatch carries the `run_id`, composed from the process identity of
   step 2 and a per-process counter, so the entry can be judged from its first message. Ensure the
   entry carries it from the moment it is written rather than from a value reported back later.
   *Done when:* no window exists between writing the entry and its first message in which a message
   cannot be decided.
4. **`SPEC.md` Section 4.1.8 — the running entry's description names it.** Ensure the `running`
   map's entry is described as carrying the run attempt's `run_id`, so the map's key (the issue) and
   the entry's identity (the run) are visibly different things. *Done when:* the field's presence is
   readable from the runtime-state enumeration and not only from Section 16.4's algorithm.
5. **`SPEC.md` Section 16.6 — the message shape carries it.** Ensure the worker→orchestrator sends
   carry the run attempt's `run_id` — the `agent_update` send quoted as `send(orchestrator_channel,
   {agent_update, issue.id, msg})` and the worker-exit notification alike — so every
   worker-lifecycle message is judgeable. *Done when:* no worker-lifecycle message reaches the
   orchestrator keyed by issue alone.
6. **`SPEC.md` Section 16.7 — `on_worker_exit` takes the identity and uses get-compare-remove.**
   Ensure the callback's signature carries the exiting run's `run_id`, and that its body reads the
   entry, compares, and only then removes — the shape decision 0136 gave `on_retry_timer`, so a
   mismatched exit removes nothing. Ensure the existing `if missing` case is retained as the case
   where no entry means no match. *Done when:* a mismatched exit leaves the entry and its worker
   untouched, and the function no longer opens with a removal.
7. **`SPEC.md` Section 8.5 — the invariant is restated over identity.** Ensure the paragraph quoted
   as "a worker exit for an issue with no running entry is a no-op" states the whole rule: a
   worker-lifecycle message whose `run_id` does not equal the `run_id` of the issue's current
   running entry MUST be discarded, leaving that entry and its worker untouched — with Section 8.4's
   second sentence in the same shape, that testing only whether a running entry is present does not
   satisfy this, because after a reconciliation-initiated termination and a re-dispatch the entry a
   stale message must not consume is present by construction. Ensure the existing sentence stays
   true and stops being the whole rule. Ensure the rule is stated over the **channel** rather than
   over the exit alone, and that the reason is given: a late `agent_update` writes `last_timestamp`,
   which is Part A's own stall reference (Section 16.3), so a dead run's trailing events keep a
   stalled replacement alive. *Done when:* the rule covers exits and agent updates in one sentence,
   and the `if missing` case follows from it rather than sitting beside it.
8. **`SPEC.md` Section 7.3 — the two `Worker Exit` triggers get the note the timer trigger got.**
   Ensure both trigger descriptions state that a message whose run identity does not match the
   current running entry's fires nothing, mirroring the existing note that an exit arriving with no
   running entry triggers nothing. Ensure `Agent Update Event` carries the same condition. *Done
   when:* no trigger in Section 7.3 reads as firing on issue identity alone.
9. **`SPEC.md` Section 17.4 — a row mirroring the existing `generation` row.** Ensure the matrix
   covers a worker-lifecycle message whose `run_id` does not match the current running entry's being
   discarded without accounting, without scheduling a retry, and leaving that entry and its worker
   in place — and that the row names an agent update as well as an exit, since the stall-reference
   consequence is the one with no second line of defence. *Done when:* the row fails a remove-first
   implementation and one that guards the exit alone.
10. **`SPEC.md` Section 18.1.3 — a checklist item beside the existing one.** Ensure the checklist
    covers deciding every worker-lifecycle message against the current running entry's run identity.
    *Done when:* the item exists and does not restate Section 17.4's wording.
11. **`SPEC.md` Section 19 and `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 — the new obligation
    gets its row.** Ensure Section 19's list of documented resolutions covers how the process
    identity of step 2 is derived, and that the template's Core table carries a matching row citing
    Section 16.1. *Done when:* `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0
    warnings, and no `Implementation-defined` sentence added by this decision lacks a row
    (`CLAUDE.md`, decision 0128).
12. **`conformance/vectors/worker-exit-disposition.json` — the mirror vector.** Ensure a file exists
    mirroring `retry-fire-disposition.json`'s one-shot pure-function shape: `given` is `{ entry: {
    run_id, … } | null, exit_run_id }` and `expect` is `{ disposition: 'account' | 'discard',
    entry_retained: boolean }`. Ensure it carries at least the matching case, the stale case with
    `entry_retained: true`, and the no-entry case. *Done when:* the stale case's `entry_retained:
    true` is the assertion a remove-first implementation fails, and the file needs no live
    invocation.

## Cross-cutting sync

- `SPEC.md` Sections 17.4, 18.1.3 and 19: steps 9, 10 and 11.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1: step 11. **A row is owed** — the process identity
  is a new `Implementation-defined` + MUST-document obligation. This is the case decision 0128
  records three decisions in a row missing.
- `SPEC.md` Section 6.4 (config cheat sheet): no change — no configuration key is added.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 (recovery classes): the per-process counter behind
  `run_id` is Core state that `SPEC.md` Section 4.1.8 does not enumerate, and `SPEC.md` Section
  14.3's "not closed" note already governs such state; ensure the counter is covered in the
  template's Section 5 table the way Section 8.4's generation counter is, rather than by a second
  rule.
- `conformance/README.md`: its decision-0138 entry restates Section 8.5's invariant as "an exit for
  an issue with no running entry is a no-op". Step 7 makes that sentence narrower rather than false
  — no entry still means no match — so the entry should be brought into step with the restated rule
  rather than left asserting the whole of it.

## Ordering

- **After decision 0145.** Section 8.5 Part B is not reachable as a re-dispatch path while the issue
  it terminated is never unclaimed, so this race has one live route today instead of three. The
  guard is owed either way; the ordering is what makes the reachability analysis in `Background.md`
  true rather than conditional.
- Independent of decision 0144, though that decision's phase reading is what makes a `Provisioning`
  run's entry — and therefore its `run_id` — exist during acquisition.

## Anchor changes

- **Added:** `run_id` on Section 4.1.5 and on the running entry; a process identity in Section 16.1;
  `worker-exit-disposition.json`.
- **Changed:** `on_worker_exit`'s signature gains a parameter and its body changes shape; Section
  16.6's send shape gains the identity; Section 8.5's invariant paragraph is restated over identity;
  Section 7.3's two `Worker Exit` triggers and `Agent Update Event` gain the condition.
- **Removed:** nothing. Section 8.5's existing sentence about an exit with no running entry stays
  true and is subsumed.

## Status

Applied to `SPEC.md` (Sections 4.1.5, 4.1.8, 7.3, 8.5, 13.1, 14.3, 16.1, 16.4, 16.6, 16.7,
17.4, 18.1.3, 19), `CONFORMANCE-STATEMENT-TEMPLATE.md` (Sections 4.1, 5),
`conformance/vectors/worker-exit-disposition.json` and `conformance/README.md`.

Two sites beyond the Scope list. Section 13.1 gives `origin_run_id` its type in one clause,
the type step 1 says it has never been given; stating it only in Section 4.1.5 would leave
the two sites disagreeing about what the field holds. Section 14.3's `not closed` note
enumerates the Core state Section 4.1.8 does not list, and the process identity and
per-process counter join that enumeration rather than relying on the template's Section 5
prose alone — the note is what governs them, and an enumeration that omits them is the
stale-restatement shape `scripts/validate_spec_consistency.py` exists for.

Two `Implementation-defined` obligations were added, not one: the `run_id` derivation
(Section 4.1.5) and the process identity it composes from (Section 16.1). Both have template
rows, since step 11's check is per section. Section 16.1's is stated in prose beneath the
block, as Section 16.5's object-store obligation is, because the consistency script blanks
fenced content and an obligation stated only in a pseudocode comment is invisible to it.
Issue #106.
