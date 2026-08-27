# Plan — 0157 What a re-dispatch tests

## Scope

- `SPEC.md` — Section 7.1 Issue Orchestration States, Section 8.2 Candidate Selection Rules,
  Section 8.3 Concurrency Control, Section 8.4 Retry and Backoff, Section 8.5 Active Run
  Reconciliation, Section 16.2 Poll-and-Dispatch Tick, Section 16.7 Worker Exit and Retry Handling,
  Section 17.4 Orchestrator Dispatch, Reconciliation, and Retry, and Section 18.1.3 Daemon
  Conformance.
- `conformance/vectors/retry-fire-disposition.json` — widened from the generation match to the
  fire's whole disposition.
- `conformance/README.md` — the corpus-coverage row's *Derived from*, and a "Surfaced findings"
  entry.
- `SPEC.md` Section 14.5 Operator Intervention Points — added while applying the plan and recorded
  in `Background.md` under *Findings from applying the plan*: its label-and-assignee bullet answered
  only for a running session, and the same edit now has an effect on an issue in backoff too.
- `SPEC.md` Section 7.3 Transition Triggers — **unchanged**, cited only, and found while applying
  the plan. Its `Retry Timer Fired` trigger already reads "Re-fetch active candidates and attempt
  re-dispatch, or release claim if no longer eligible", so it is the second normative statement
  Section 16.7 contradicted and it becomes true without being edited.
- `SPEC.md` Section 16.4 Dispatch One Issue — **unchanged**, cited only. `dispatch_issue` is the
  single site both dispatch paths reach; its `ensure_object_store` early return is the branch the
  stranded claim escapes through, and it stops escaping because its caller no longer holds a claim,
  not because the function changes. Its `repo_of(issue)` is the routing evaluation step 1 states the
  fire does not duplicate.
- `SPEC.md` Section 8.7 Multiple Repositories and Shared Polling — **unchanged**, cited only.
  Routing is a standing condition of a run *in flight*, evaluated against the entry's recorded
  `repository`; a fire has no such entry, so nothing in Section 8.7 is owed a re-dispatch clause.
- `SPEC.md` Section 14.2 Recovery Behavior — **unchanged**, cited only. Its repository-provisioning
  bullet already states the recovery ("Keep the service alive and retry on a later tick") that the
  stranded claim made unreachable from one caller; step 5 restores the reachability rather than
  restating the rule.
- `SPEC.md` Section 5.3.1 `tracker` — **unchanged**, cited only. Its "to dispatch or continue"
  clause is what a fire violates today; this decision adds no obligation there.
- `conformance/vectors/candidate-eligibility.json` — **unchanged**. `should_dispatch` gains a second
  caller; its inputs, its nine conditions and its answers are untouched, and the file already pins
  them.
- `conformance/vectors/available-slots.json` and `conformance/vectors/per-state-concurrency.json` —
  **unchanged**. Step 2 names the pair those two files already compute the halves of; neither the
  global computation nor the per-state limit resolution changes.
- `conformance/vocabulary.json` — **unchanged**. No published token is added, renamed, or removed:
  the registry publishes no group for pseudocode function names or for retry dispositions, and the
  error string `no available orchestrator slots` keeps its spelling.
- Sites carrying the repository-provisioning recovery this decision makes reachable from the second
  caller, all **unchanged**: `SPEC.md` Section 9.7 Repository Provisioning and the VCS Engine
  ("retried on a later tick") and Section 18.1.2 Broker Core Conformance ("retry on a later tick").
  Step 5 changes the claim state `dispatch_issue` is entered with, not the recovery either site
  states; the disposition is Section 14.2's and it is untouched.
- `conformance/vectors/standing-conditions.json` — **unchanged**, named here because its
  `description` and `notes` carry the same "the `Todo` blocker rule" and four-condition wording this
  decision revisits. What they state is what a *reconciliation refresh* re-tests against a run in
  flight, where all four are false by construction; this decision is about a second *dispatch*,
  where they are not. Neither sentence becomes false, and neither is edited.
- `SPEC.md` Section 11.6 Workflow State Machine and Transition Triggers — **unchanged**. Its "a
  retry path that ran out" names a transition trigger's condition, not this path's disposition.
- `conformance/README.md`'s existing "Surfaced findings" entry for decision 0155 — **unchanged**. It
  quotes Section 5.3.1's "to dispatch or continue" as that decision's premise, and records what was
  true when written.

## Steps

1. **`SPEC.md` Section 8.2 Candidate Selection Rules — both dispatch sites test these
   conditions.** Ensure a paragraph, placed before the paragraph beginning "Which of these
   conditions a reconciliation pass may re-test is fixed here", states that two sites reach
   `dispatch_issue` — a poll tick (Section 16.2) and a retry timer fire after its backoff elapses
   (Sections 8.4, 16.7) — and that both MUST evaluate every condition above, through one
   predicate, rather than each carrying its own subset. Ensure the paragraph does not name that
   predicate: Section 8.2 describes `should_dispatch` without naming it today, as decision 0155's
   paragraph beneath it describes `standing_conditions_hold` without naming it, and the two call
   sites in Section 16 carry the name. Ensure it states why a fire is a
   dispatch and not a resumption: no run is in flight, no workspace is held, and what it starts is a
   run attempt like any other, so an issue that stopped satisfying a condition while it sat in
   backoff MUST NOT be dispatched by the fire that was armed while it did. Ensure it states how the
   `claimed`-membership condition is satisfied at a fire — the claim is released with the retry
   entry the fire consumes (Sections 8.4, 16.7), not excepted — so no condition is tested at one
   site and not the other. Ensure it states that routing is not part of this: `dispatch_issue`
   evaluates `repo_of(issue)` for both callers, and Section 8.7's standing routing condition is over
   a run's recorded `repository`, which a fire has none of. *Done when:* Section 8.2 names both
   dispatch sites, the predicate both use, and the one condition whose satisfaction at a fire needs
   explaining; and the existing standing/dispatch-time paragraph beneath it still reads true, its
   four "false by construction" conditions being about re-testing against a run in flight rather
   than about a second dispatch.

2. **`SPEC.md` Section 8.3 Concurrency Control — a name for the two concurrency conditions.**
   Ensure the section defines `dispatch_slot_available(issue, state)`: an issue has a dispatch slot
   when both limits admit it — `available_slots > 0`, and the count of running issues whose current
   tracked state equals the issue's below the limit resolved for that state. Ensure it states that
   the pair is exactly Section 8.2's two concurrency conditions, that `available_slots` is the
   global half alone, and that a dispatch site testing only `available_slots` admits a run past
   `max_concurrent_agents_by_state`. Ensure no Section 16 function body is added for it, following
   `should_dispatch` and `standing_conditions_hold`, which are named at their call sites and defined
   in Section 8 prose. *Done when:* one name covers both limits, `available_slots` keeps its
   existing global definition and its existing formula unchanged, and Section 8.3 says which of the
   two a caller gets from each.

3. **`SPEC.md` Section 8.4 Retry and Backoff — the "Retry handling behavior" list describes what a
   fire does.** Ensure the numbered list states, in the order the fire performs them: the candidate
   fetch; the release of the claim taken when the retry was armed, the entry it was taken for having
   been consumed, with every step below either taking it back or leaving the issue `Released`
   (Section 7.1); the lookup by `issue_id` and that nothing further is owed when it is absent; the
   requeue with error `no available orchestrator slots` where no dispatch slot is available under
   either limit (Section 8.3); the dispatch at the entry's `attempt` where every Section 8.2
   condition holds; and doing nothing further where one does not, a later poll tick dispatching the
   issue when it is eligible again. Ensure Section 8.4's step reading "If found but no longer
   active, release claim." does not survive as a step of its own: state membership is one of Section
   8.2's conditions, and the step is unreachable as written because `fetch_candidate_issues` returns
   only issues in the configured active states (Section 11.1). *Done when:* every step of the list
   has a counterpart in `on_retry_timer` and every branch of `on_retry_timer` has a step, and
   Section 8.4's "still candidate-eligible" is no longer a requirement the reference algorithm does
   not perform.

4. **`SPEC.md` Section 16.7 Worker Exit and Retry Handling — `on_retry_timer` tests what a
   dispatch tests.** Ensure `on_retry_timer`, after the candidate fetch has succeeded and before the
   lookup by id, releases the claim once — `state.claimed.remove(issue_id)` — with a comment giving
   the reason (the claim was taken for the entry this fire consumed, and comes off with it, the
   discipline `terminate_running_issue` follows for a running entry) and the placement's reason (it
   is released before the eligibility test because the test is Section 8.2's whole predicate, whose
   `claimed`-membership condition would otherwise refuse every issue a fire could ask about; and
   after the fetch rather than before it, so no network round trip runs with the issue unclaimed).
   Ensure the `issue is null` branch relies on that single release rather than carrying its own.
   Ensure the slot test is `dispatch_slot_available(issue, state)` rather than
   `available_slots(state) == 0`, with a comment stating that it is tested outside `should_dispatch`
   because its disposition differs — a slot is transient, so the fire re-arms and keeps counting
   attempts, while a condition over the record releases. Ensure `should_dispatch(issue, state)`
   gates the call to `dispatch_issue`, and that its failing branch returns with the issue released.
   *Done when:* `state.claimed.remove(issue_id)` occurs exactly once in `on_retry_timer`,
   `should_dispatch` has two call sites in `SPEC.md`, `available_slots` no longer occurs in Section
   16.7, and no branch of the function reaches `dispatch_issue` holding a claim.

4a. **`SPEC.md` Section 16.7 — `schedule_retry`'s comment describes the release that now happens.**
    Ensure the comment on `state.claimed.add(issue_id)` in `schedule_retry`, whose closing sentence
    today reads "`on_retry_timer` releases it if it is no longer a candidate.", instead states that
    `on_retry_timer` releases the claim with the entry it consumes and that only a re-arm or a
    dispatch takes it back. Ensure the rest of the comment stands: arming takes the claim, a
    `RetryQueued` issue is claimed by construction, and the add is idempotent because the issue may
    already be claimed from dispatch. *Done when:* no comment in Section 16.7 describes the release
    as conditional on the issue being absent from the candidate set.

5. **`SPEC.md` Section 8.5 Active Run Reconciliation — the claim partition's `dispatch_issue`
   bullet is true of both callers.** Ensure the bullet stating that `dispatch_issue`'s
   `ensure_object_store` failure "leaves the issue unclaimed so a later tick retries it — the case
   that makes the partition complete rather than an exception to it" also states what makes it true:
   `dispatch_issue` is entered unclaimed from both of its callers, the poll tick because
   `should_dispatch` refused a claimed issue and the retry fire because it released the claim with
   the entry it consumed (Sections 8.4, 16.7). Ensure the Section 8.5 requirement "A site added
   later MUST state which side of that partition it is on" is answered for the release step 4
   adds: neither side, because the partition is over sites that end a dispatched run, and a retry
   fire ends a retry entry with no run in flight. This is the answer decision 0156 gave for Part B's
   absent-id branch, for the same reason. *Done when:* the bullet's completeness claim is checkable
   against both callers rather than against one, a reader who follows the retry path into
   `dispatch_issue` finds the claim state the bullet assumes, and the new release is not left for a
   reader to classify against the partition.

6. **`SPEC.md` Section 7.1 Issue Orchestration States — the `Released` bullet's second cause gains
   a producer.** Ensure the bullet that today reads "Issue missing from the candidate set, or a
   retry path that completed without re-dispatch: `on_retry_timer` releases it on the branch where
   the fired retry's issue is no longer a candidate (Section 16.7)" names a producer for both
   causes: `on_retry_timer` releases the claim with the retry entry it consumes, and the two
   branches that do not re-dispatch — the issue absent from the candidate set, and the issue present
   but no longer dispatch-eligible under Section 8.2 — leave it released. *Done when:* neither cause
   named in the bullet is without a producer, and the bullet's citation set covers Sections 8.2 and
   8.4 alongside 16.7.

7. **`SPEC.md` Section 16.2 Poll-and-Dispatch Tick — the loop break names the computation Section
   8.3 defines.** Ensure `on_tick`'s break condition is `available_slots(state) == 0` rather than
   `no_available_slots(state)`, a name no section defines and whose only other spelling this
   decision removes from Section 16.7. Ensure the global-only break is kept as the break — an
   exhausted global limit admits no issue, while the per-state limit is per-issue and stays inside
   `should_dispatch`. *Done when:* `no_available_slots` occurs nowhere in `SPEC.md`, and `on_tick`
   still breaks on the global limit rather than on `dispatch_slot_available`.

8. **`SPEC.md` Section 17.4 Orchestrator Dispatch, Reconciliation, and Retry — the fire's checks.**
   Ensure rows exist for: a retry fire whose issue has lost a `tracker.required_labels` label, lost
   the configured `tracker.assignee`, or gained a non-terminal blocker while in `Todo` during its
   backoff does not dispatch, and leaves the issue unclaimed rather than armed for another retry; a
   retry fire into a state already at `max_concurrent_agents_by_state` requeues with `no available
   orchestrator slots` rather than dispatching, the global limit having headroom; and a repository
   provisioning failure raised by a dispatch a retry fire started leaves the issue unclaimed, so a
   later tick retries it as Section 14.2 states. Ensure the existing Section 17.4 rows this decision
   relies on — "Slot exhaustion requeues retries with explicit error reason" and the
   backoff-escalation row — are left unchanged. *Done when:* each of the three behaviors has a row,
   and no row asserts a disposition Section 8.4's list and Section 16.7 do not agree on.

9. **`SPEC.md` Section 18.1.3 Daemon Conformance — the claim's lifetime and the fire's
   eligibility.** Ensure the item reading "The claim has one lifetime: taken at dispatch or at retry
   arming, released where the run it was held for ends without a retry taking it over (Sections 7.1,
   8.5)" also covers the release this decision adds: a retry fire releases it with the entry it
   consumes, and re-takes it only by dispatching or re-arming. Ensure an item states that both
   dispatch sites evaluate Section 8.2's conditions whole — a retry timer fire no less than a poll
   tick — so an issue that lost a condition during its backoff is not re-dispatched. *Done when:*
   the checklist does not license a fire that dispatches on membership in the candidate set alone,
   and its claim-lifetime item accounts for every `state.claimed.remove` in Section 16.

10. **`conformance/vectors/retry-fire-disposition.json` — the fire's whole disposition.** Ensure the
    file's `retry_fire_disposition` covers the branches Section 16.7 now has, not only the
    generation match, in the shape `conformance/vectors/reconcile-disposition.json` established: the
    predicate results are `given` inputs rather than re-derived, so this file pins what the fire
    does with an answer and not how the answer is computed. Ensure `given` carries the entry and the
    fire's `generation`, the candidate fetch's outcome, whether the issue is in the candidate set,
    whether `dispatch_slot_available` holds, and whether `should_dispatch` holds; and `expect` names
    the disposition (`dispatch`, `discard`, `rearm`, `release`), whether the retry entry present
    when the fire arrived survives it, whether the fire leaves the issue unclaimed, and the
    `attempt` the disposition carries. Ensure the three existing vectors keep their ids and their
    outcomes — `fire-generation-matches`, `fire-generation-stale`, `fire-with-no-entry` — with the
    stale one carrying downstream inputs that would otherwise dispatch, so the short-circuit is what
    the vector shows. Ensure new vectors cover: the fetch failing; the issue absent from the
    candidate set; no dispatch slot; dispatch-ineligible with a slot available; and a fire with
    neither a slot nor eligibility, which re-arms rather than releases because Section 16.7 tests
    the slot first. Ensure a note records that `slot_available: false` implies `dispatch_eligible:
    false`, the two concurrency conditions being among `should_dispatch`'s nine, so no vector holds
    the impossible pair; and that the eligibility predicate itself is
    `conformance/vectors/candidate-eligibility.json`'s subject and is not re-derived here. Ensure
    `spec_refs` cites the sections the file's values are read from, and that
    `conformance/README.md`'s row for the file carries an identical *Derived from*. *Done when:*
    every branch of `on_retry_timer` has at least one vector, no vector re-tests a condition
    `candidate-eligibility.json` covers, and the file's `expect` distinguishes re-arming from
    releasing rather than collapsing both into one not-dispatched outcome.

11. **`conformance/README.md` — a "Surfaced findings" entry.** Ensure an entry records that
    `SPEC.md` Section 8.4's "Retry handling behavior" required a fire to dispatch an issue "found
    and still candidate-eligible" while `SPEC.md` Section 16.7's `on_retry_timer` tested membership
    in the candidate set and the global slot count alone, so a backoff of up to
    `agent.max_retry_backoff_ms` outlived the eligibility that armed it; that the same path tested
    `available_slots` rather than both limits, admitting a run past
    `max_concurrent_agents_by_state`; and that entering `dispatch_issue` with the claim still held
    stranded it permanently on the `ensure_object_store` branch, against `SPEC.md` Section 8.5's own
    statement that that branch "leaves the issue unclaimed so a later tick retries it". Ensure the
    entry names decision 0157 and the third site the answer to issue #120 identified. *Done when:*
    the entry names both sections that disagreed, all three defects, and the decision that resolved
    them.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — **no change.** No configuration key is added, removed
  or redefined. `agent.max_concurrent_agents_by_state` is already listed there with its default
  `{}`; this decision changes which dispatch sites consult it, not the key.
- `SPEC.md` Section 17 (test matrix) — covered by step 8 (Section 17.4).
- `SPEC.md` Section 18 (checklist) — covered by step 9 (Section 18.1.3).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no row owed.** This decision introduces no
  `Implementation-defined` behavior and no MUST-document clause: it closes a choice the document had
  left two answers for and fixes a disposition, both of which remove implementation latitude rather
  than delegate it. As decisions 0155 and 0156 recorded,
  `scripts/validate_spec_consistency.py` is not evidence either way — its obligation check collapses
  the template's `8.x` extension citation to `8` — so this is a checked judgement, not a green run.
- `conformance/vocabulary.json` — **unchanged.** `dispatch_slot_available` is a pseudocode predicate
  name, as `should_dispatch` and `standing_conditions_hold` are, and the registry publishes no group
  for those. The retry dispositions stay prose; no log context field, error class or state name is
  added.
- `conformance/vectors/` — covered by step 10 (`retry-fire-disposition.json` widened; no new file).
- `conformance/README.md` — covered by steps 10 and 11.
- `scripts/validate_spec_consistency.py` — **no check-7 row.** Check 7 covers vectors whose `expect`
  enumerates a set a section fixes; `retry_fire_disposition`'s `expect` is a computed disposition,
  which is the shape the file already had and keeps.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — **unchanged.**
  Dispatch, claims and retry are Symphony's; the engine's only appearance on this path is
  `ensure_object_store`, whose contract does not change.

## Ordering

Steps 1 and 2 introduce the anchors the rest cite — the two-dispatch-sites paragraph and
`dispatch_slot_available` — and step 4 is what makes steps 3, 5, 6 and 9 true rather than asserted.
Step 7 is independent of the others and could stand alone; it is here because removing
`available_slots` from Section 16.7 (step 4) would otherwise leave `no_available_slots` as the only
spelling of a computation Section 8.3 defines under another name.

**Depends on decision 0155 having landed.** Step 1's paragraph sits above 0155's standing/dispatch-
time paragraph and has to read consistently with it, and this decision's correction to 0155's
recorded finding presumes that finding exists. It does not depend on decision 0156: 0156 is about
what the *refresh* returns and which ids it does not answer for, and the retry path uses
`fetch_candidate_issues` rather than `fetch_issue_states_by_ids`.

## Anchor changes

New:

- `dispatch_slot_available` — the predicate Section 8.3 defines for Section 8.2's two concurrency
  conditions, called in Section 16.7 (steps 2, 4). Defined in Section 8 prose with no Section 16
  body, following `should_dispatch` and `standing_conditions_hold`.

Changed:

- `SPEC.md` Section 8.2 Candidate Selection Rules — gains a paragraph naming both dispatch sites
  (step 1). The nine conditions themselves are unchanged in wording and in order.
- `SPEC.md` Section 8.3 Concurrency Control — gains `dispatch_slot_available` (step 2).
  `available_slots` keeps its name, its formula and its global-only meaning.
- `SPEC.md` Section 8.4 Retry and Backoff — the "Retry handling behavior" list is restated against
  what the fire does (step 3). Its step "If found but no longer active, release claim." is subsumed
  by the Section 8.2 condition it was a special case of, and is not replaced by a step of its own.
- `SPEC.md` Section 8.5 Active Run Reconciliation — the partition's `dispatch_issue` bullet states
  the claim state both callers hand it (step 5).
- `SPEC.md` Section 7.1 Issue Orchestration States — the `Released` bullet names a producer for both
  of its causes (step 6).
- `SPEC.md` Section 16.2 Poll-and-Dispatch Tick — `on_tick` breaks on `available_slots(state) == 0`
  (step 7).
- `SPEC.md` Section 16.7 Worker Exit and Retry Handling — `on_retry_timer` releases the claim once,
  tests `dispatch_slot_available` and then `should_dispatch` (step 4); `schedule_retry`'s comment
  describes that release rather than the conditional one it replaced (step 4a).
- `SPEC.md` Section 17.4, Section 18.1.3 — rows and items (steps 8, 9).
- `SPEC.md` Section 14.5 Operator Intervention Points — the label-and-assignee bullet answers for an
  issue in backoff as well as a running one (a finding from applying the plan).
- `conformance/vectors/retry-fire-disposition.json` — `given` and `expect` widen from the generation
  match to the whole disposition (step 10). The three existing vector ids are kept.

Removed:

- `no_available_slots` — the Section 16.2 spelling of `available_slots(state) == 0`, defined by no
  section (step 7). No other site uses it.

Not edited, and deliberately: `decisions/0155-standing-conditions/Background.md` states that
`on_retry_timer` owes "the record's conditions and the `Todo` blocker rule, but not the four
orchestrator-state ones". That classification is corrected in this decision's `Background.md` under
*A correction to decision 0155's record*, not in 0155's file. A decision record states what was true
when it was written.

## Status

Applied. Steps 1 to 9 are in `SPEC.md`; steps 10 and 11 are in
`conformance/vectors/retry-fire-disposition.json` and `conformance/README.md`. Issues #120, #121.

Reviewed with the `plan-review` skill before the first edit, against `cbc6507`. Four lenses:
`check_plan_anchors.py` went from 23 findings over 29 quoted spans to 2 over 27. Q repaired
seventeen — ten step headers quoting a section *title*, which the script reads as a span that must
occur in that section's body; four quotations attributed to a section named later in the same
sentence; two `SPEC.md` quotations attributed to the step's target file; and one phrase of the
plan's own in quotation marks. One Q finding is deliberate: the quotation from
`decisions/0155-standing-conditions/Background.md` is outside the script's corpus and was verified
by hand. R named four further sites as unchanged with reasons, and `conformance/README.md:502` is
named but still reported. P repaired three: `schedule_retry`'s comment describing the conditional
release this decision replaces, with no producer left for its premise; Section 8.5's "site added
later MUST state which side" requirement unanswered for the release step 4 adds; and step 1 naming
`should_dispatch` in Section 8.2 prose, where neither it nor `standing_conditions_hold` has ever
been named.
