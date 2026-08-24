# Plan — 0145 The claim nothing released

## Scope

- `SPEC.md` — Section 16.3 (`terminate_running_issue`), Section 16.7 (`schedule_retry`), Section
  16.4 (`dispatch_issue`), Section 7.1 (Issue Orchestration States), Section 8.5 (Reconciliation),
  Section 17.4 (test matrix), Section 18 (implementation checklist).
- `conformance/vectors/` — no new file. The property is over a sequence of state mutations rather
  than over one pure function, and the corpus is per-function over one input; Section 17.4 is where
  it is checkable.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. No `Implementation-defined` behaviour and no
  MUST-document obligation is added, so no row is owed (`CLAUDE.md`, decision 0128).

## Steps

1. **`SPEC.md` Section 16.3 — `terminate_running_issue` releases the claim.** Ensure the function
   removes the issue from `claimed` where it removed the running entry, placed with the runtime
   accounting the same function already owns, and that its comment says why: the claim was held for
   the run whose entry is being removed. Ensure the `if missing` early return still returns
   unchanged, so a second call releases nothing it did not hold. *Done when:* both branches of
   Section 8.5 Part B and Part A's stall path release the claim, and the function is idempotent on
   re-entry.
2. **`SPEC.md` Section 16.7 — `schedule_retry` takes the claim.** Ensure the function adds the issue
   to `claimed`, so a `RetryQueued` issue is claimed by construction rather than by inheritance from
   `dispatch_issue`. Ensure the existing comment in that function's body, quoted as "The issue is
   already in state.claimed from dispatch_issue and stays claimed while it is" (a pseudocode
   comment, so the tokens carry no backticks there), is replaced by one stating the taking, since it
   is that comment's claim that is false on Section 16.4's spawn-failure path. Ensure
   `on_retry_timer`'s existing `state.claimed.remove(issue_id)` on the not-a-candidate branch is
   unchanged. *Done when:* every path that arms a retry leaves the issue claimed, including the
   spawn-failure early return, and Part A's terminate-then-schedule is correct in either order.
3. **`SPEC.md` Section 16.4 — the two early returns are covered, and one needs nothing.** Ensure the
   spawn-failure early return's correctness now follows from step 2 rather than from
   `state.claimed.add(issue.id)` below it, and that the comment beside the `ensure_object_store`
   failure still states that the issue is left unclaimed so a later tick retries it — that path
   writes no entry and arms no retry, and is the reason the partition in step 4 is complete rather
   than an exception to it. *Done when:* no path through `dispatch_issue` leaves a retry armed for
   an unclaimed issue, and no path releases a claim it did not take.
4. **`SPEC.md` Section 8.5 or Section 7.1 — state the partition.** Ensure one passage states that
   every site removing a running entry either releases the claim or hands it to a retry entry, and
   that there is no third — naming the three sites (`terminate_running_issue`, `on_worker_exit`,
   `dispatch_issue`'s spawn failure) so a site added later has to say which side it is on. Place it
   where the reconciliation-ownership invariant is stated, which is the passage it completes. *Done
   when:* Section 7.1's `Released` state is derivable from Section 16 rather than asserted beside
   it, and a reader can check the coverage without enumerating call sites themselves.
5. **`SPEC.md` Section 7.1 — `Released` names its producers.** Ensure state 6's description is
   consistent with step 4: the claim is removed where the run it was held for ends without a retry
   taking it over, and where a retry path completes without re-dispatch. *Done when:* the state's
   four listed causes each have a site in Section 16 that produces them.
6. **`SPEC.md` Section 17.4 — two rows.** Ensure the matrix covers (a) an issue whose run was
   stopped for a terminal or non-active state being dispatchable again as soon as it is a candidate,
   with no backoff elapsing and no restart — the existing release row, now with a producer; and (b)
   a repeatedly failing worker spawn escalating its backoff toward `agent.max_retry_backoff_ms`
   rather than restarting at the first attempt every `polling.interval_ms`. *Done when:* (b) fails
   an implementation whose `dispatch_issue` arms a retry without claiming, and (a) fails one whose
   `terminate_running_issue` does not release.
7. **`SPEC.md` Section 18 — the checklist follows.** Ensure the implementation checklist covers the
   claim's lifetime as one item — taken at dispatch or at retry arming, released where the run ends
   without a retry — rather than as two. *Done when:* the line exists and does not restate Section
   17.4's wording.

## Cross-cutting sync

- `SPEC.md` Sections 17.4 and 18: steps 6 and 7.
- `SPEC.md` Section 6.4 (config cheat sheet): no change.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no row owed; stated rather than left silent (decision 0128).

## Ordering

- **After decision 0144.** The withdrawn slot consequence in this decision's `Background.md` rests
  on that decision's settlement, and step 6's row (b) is stated in terms of the backoff rather than
  of a slot.
- **Before decision 0146.** That decision's race needs Section 8.5 Part B reachable as a re-dispatch
  path, and Part B is not reachable while the issue it terminated is never unclaimed. Both land
  before the mutation sites exist in the `symphony-rs` build, which is the cheap order and a
  property of timing rather than of the design.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0145-claim-lifetime/Plan.md --rev 22b5194` reports
one reach finding and no quote findings: `SPEC.md:2920` (Section 11.8) carries the fragment "the
issue is already", which is stock phrasing rather than a twin of the `schedule_retry` comment step 2
edits. Section 11.8 is not touched.

Recorded from the same run: the comment step 2 edits is a **pseudocode** comment, so its tokens
carry no backticks in `SPEC.md`. An earlier draft of this plan quoted it with them and the quote
matched nothing — the check's Q finding, and the reason the step now says so explicitly.

## Anchor changes

- **Changed:** `terminate_running_issue` gains a claim release; `schedule_retry` gains a claim take
  and loses the comment asserting the claim is already held; Section 7.1 state 6's description gains
  its producers.
- **Added:** the partition statement (step 4). No new field, no new token, no new configuration key.
- **Removed:** nothing. `claimed` stays an explicit set rather than becoming a derived view — see
  `Background.md` for why the derivation loses.

## Status

Applied to `SPEC.md` (Sections 7.1, 8.5, 16.3, 16.4, 16.7, 17.4, 18.1.3). Step 3 needed no
edit of its own: `schedule_retry`'s new comment names the spawn-failure early return, and the
`ensure_object_store` comment already said what the step requires. No vector file, as the
Scope records. Issue #108.
