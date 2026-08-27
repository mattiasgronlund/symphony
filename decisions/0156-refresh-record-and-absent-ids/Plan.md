# Plan — 0156 The refresh that returns a state, and the ids it does not answer

## Scope

- `SPEC.md` — Section 11.1 REQUIRED Operations, Section 11.2 Adapter Semantics (its Refresh
  completeness block), Section 8.5 Active Run Reconciliation, Section 16.3 Reconcile Active Runs,
  Section 17.3 Issue Tracker Client, Section 17.4 Orchestrator Dispatch, Reconciliation, and Retry,
  and Section 18.1.3 Daemon Conformance. Section 14.5 Operator Intervention Points was added while
  applying the plan and is recorded in `Background.md` under *Findings from applying the plan*: the
  absent-id disposition makes deleting an issue the one intervention whose effect is nothing, and
  Section 14.5 is where an operator reads what an intervention does.
- `conformance/vectors/reconcile-disposition.json` — new file.
- `conformance/README.md` — a corpus-coverage row and a "Surfaced findings" entry.
- `SPEC.md` Section 16.6 Worker Attempt (Workspace + Prompt + Agent) — **unchanged**, cited only.
  Its `issue = refreshed_issue[0] or issue` and the `build_turn_prompt` call beneath it are the
  second consumer whose existence makes the record rather than a field subset the right obligation
  (step 1), and its `or issue` fallback is the shape step 4 mirrors for Part B.
- `SPEC.md` Section 12.2 Rendering Rules, Section 5.5 Workflow Validation and Error Surface, and
  Section 12.4 Failure Semantics — **unchanged**, cited only. Strict variable checking, the
  `template_render_error` class, and the fail-the-attempt gating are the failure path step 1 closes.
- `SPEC.md` Section 4.1.1 Issue — **unchanged**, cited only. It is the record step 1 names, and its
  membership is decision 0154's, not this decision's.
- `SPEC.md` Section 8.2 Candidate Selection Rules and Section 8.7 Multiple Repositories and Shared
  Polling — **unchanged**, cited only. The standing conditions are decision 0155's; this decision
  changes what the refresh must supply them with, not what they test. Section 8.2's field-presence
  bullet is worth naming rather than leaving to be rediscovered: it backstops `id`, `identifier`,
  `title` and `state` on the general normalization obligation every adapter owes on every read,
  because Section 11.2's Refresh completeness block names only `state` of the four. Step 1 makes the
  refresh's own obligation cover all sixteen fields, at which point the bullet could cite it
  instead; it is left on the general obligation, which stays the truer citation for a
  well-formedness test that is not a standing condition.
- `conformance/vectors/standing-conditions.json` — **unchanged**. Its predicate is over a record it
  is handed; widening what the adapter must return does not change what the predicate reads.
- `conformance/vocabulary.json` — **unchanged**. No token is added, renamed, or removed.

## Steps

1. **`SPEC.md` Section 11.1 REQUIRED Operations — `fetch_issue_states_by_ids` returns a record.**
   Ensure the entry for `fetch_issue_states_by_ids(issue_ids)`, which today carries the single line
   "Used for active-run reconciliation.", states that for every id it resolves the operation MUST
   return the complete normalized issue record Section 4.1.1 defines, not only that issue's `state`.
   Ensure the entry names both consumers rather than only the one its current line names: active-run
   reconciliation (Section 8.5) and the worker's post-turn re-check (Section 16.6), the second of
   which renders the next continuation prompt from the returned record. *Done when:* Section 11.1
   states the result's shape rather than only the operation's use, and an adapter author reading
   only Section 11.1 knows a `{id, state}` pair does not satisfy it.

2. **`SPEC.md` Section 11.2 Adapter Semantics — Refresh completeness is over the record.** Ensure
   the Refresh completeness block decision 0155 added, which today requires "a normalized record
   carrying the fields the standing conditions read (Section 8.2): `state`, `labels`, `assignees`,
   and the routing fields the adapter populates (Section 11.7)", instead requires the complete
   record of Section 4.1.1 and cites Section 11.1 as where the obligation is stated. Ensure the
   block keeps the two properties 0155 gave it and does not restate Section 11.1's requirement in
   its own words: that a silently partial result is non-conformant, and that completeness here is
   over the fields of an id the caller supplied rather than over a result set the adapter pages
   through, so no hard-cap counterpart to the enumeration block's clause is owed. Ensure the reason
   given for non-conformance is widened past reconciliation to name the render path: a record
   missing a field a `WORKFLOW.md` names fails the next turn's prompt with `template_render_error`
   (Sections 5.5, 12.2) and so a run attempt (Section 12.4), against an adapter that broke no other
   rule. Ensure the Section 11.2 block's closing sentence, which today reads "The operation's name
   reflects the use Section 11.1 lists it for, not the shape of its result.", is repaired rather
   than left standing: it is true only while Section 11.1 says nothing about the result, and step 1
   makes
   Section 11.1 say exactly that. Ensure what replaces it keeps the reader-facing point the sentence
   was for — the name says `states` and the contract is over a record — without asserting that
   Section 11.1 is silent on it. *Done when:* no sentence in Section 11.2 still names a subset of
   Section 4.1.1's fields as what the refresh owes, no sentence in it claims Section 11.1 does not
   fix the result's shape, and the block reads as the guarantee over Section 11.1's obligation
   rather than as a second, narrower statement of it.

3. **`SPEC.md` Section 8.5 Active Run Reconciliation — Part B names its collection and disposes of
   an unanswered id.** Ensure Part B states that it iterates the running issues — the ids in
   `running` the refresh was asked about — rather than the records the refresh returned, so an id
   with no returned record is a case the pass is in rather than one it never reaches. Ensure a
   bullet disposes of that case: the run is left untouched — worker running, entry in place, claim
   held, no retry armed — and reconciled again on the next tick. Ensure the reason is stated in the
   terms Part B already uses for the whole-fetch failure one bullet away, "If state refresh fails,
   keep workers running and try again on the next tick": a refresh that did not answer for an id is
   not a tracker that revoked it, and the partial case is not treated more harshly than the total
   one. Ensure the cost is named rather than absorbed: an id that is permanently absent, a genuinely
   deleted issue, leaves a run reconciliation never stops, until the worker exits through
   `agent.max_turns` or Part A's stall detection — which is a weak backstop, a run making progress
   against a deleted issue not being stalled. Ensure the bullet states which side of Section 8.5's
   claim partition it is on, as Section 8.5 requires of a site added later: neither side, because it
   does not end a dispatched run — the partition is over sites that end one, and this is a site that
   declines to. *Done when:* Part B and Section 16.3 agree on which collection is iterated, the
   absent id has a stated disposition with a stated cost, and the new bullet answers the partition
   question rather than leaving a reader to infer that it is exempt.

4. **`SPEC.md` Section 16.3 Reconcile Active Runs — the same branch in pseudocode.** Ensure
   `reconcile_running_issues`, which today iterates `for issue in refreshed`, iterates the running
   ids and looks the refreshed record up by id within the loop, so the absent case is expressible.
   Ensure the absent branch continues without touching the entry, mirroring the shape Section 16.6
   already uses for the same condition, `issue = refreshed_issue[0] or issue`. Ensure a comment
   states why it is a continue rather than a termination, citing the whole-fetch disposition above
   it in the same function. *Done when:* the pseudocode has four cases where it had three, the
   fourth changes no state, and no reader has to reconcile the loop against Section 8.5's sentence.

5. **`SPEC.md` Section 17.3 Issue Tracker Client and Section 17.4 Orchestrator Dispatch,
   Reconciliation, and Retry — the refresh row widens and the absent case gains one.** Ensure
   Section 17.3's refresh row, which decision 0155 wrote as returning "the fields the standing
   conditions read", asserts the complete Section 4.1.1 record for every id resolved, and that a
   record satisfying reconciliation but not prompt rendering is non-conformant. Ensure Section 17.4
   gains a row for the absent id: an id in `running` for which the refresh returns no record leaves
   that run untouched — worker, entry, claim and retry state unchanged — and is reconciled again on
   the next tick. *Done when:* both sections check the record rather than a subset, and the absent
   case is a named row rather than a behaviour only the pseudocode implies.

6. **`SPEC.md` Section 18.1.3 Daemon Conformance — the enumeration item names the record.** Ensure
   the item decision 0155 widened, which today reads that `fetch_issue_states_by_ids` "returns the
   standing conditions' fields for every id it resolves", names the complete normalized record
   instead. *Done when:* the daemon checklist does not license a refresh Section 11.1 forbids.

7. **`conformance/vectors/reconcile-disposition.json` (new) — Part B's disposition as a function.**
   Ensure a new vector file exercises `reconcile_disposition` over `spec_refs` Section 4.2, Section
   8.2, Section 8.5, Section 16.3, in the shape `conformance/vectors/worker-exit-disposition.json`
   and `conformance/vectors/retry-fire-disposition.json` already establish for a one-shot
   disposition
   decision: a `given` carrying one running entry and the refreshed record for its id, or the
   absence of one, and an `expect` naming the disposition and its two observable consequences.
   Ensure the outcomes cover: a terminal state (stop, clean the workspace); a state that is neither
   active nor terminal (stop, leave the workspace); an active state whose standing conditions hold
   (continue, snapshot updated); an active state that has lost a record filter (stop, leave the
   workspace, claim released); an active state that no longer routes to the run's recorded
   repository (the same); and an id the refresh returned no record for (continue, nothing touched).
   Ensure the file states that the standing-condition predicate itself is
   `conformance/vectors/standing-conditions.json`'s subject and is not re-derived here — this file
   pins what Part B does with the predicate's answer, not how the answer is computed. Ensure
   `conformance/README.md` gains a row for the file in the corpus-coverage table. *Done when:* the
   file exists with six outcomes, its `expect` distinguishes workspace cleanup from claim release
   rather than collapsing them into one "stopped", and no vector in it re-tests a condition
   `standing-conditions.json` already covers.

8. **`conformance/README.md` — a "Surfaced findings" entry for the gap two decisions cited.**
   Ensure an entry records that Section 8.5 Part B and Section 16.3 disagreed on which collection
   Part B iterates, leaving an id absent from the refresh with no branch and two readings; that
   `decisions/0140-assignee-routing-condition/Background.md` and
   `decisions/0148-issue-routing-substrate/Background.md` each cited the same wording — Part B
   having no absent branch at all — as an argument, and neither repaired it, because in both the
   absent case was a consequence of a design being rejected rather than of the one accepted; and
   that Section 11.1 constrained the refresh's use and not its result, so an
   adapter returning `{id, state}` was conformant and Section 16.6's next continuation prompt failed
   strict variable checking. *Done when:* the entry names decision 0156, both prior citations, and
   the two sections that disagreed.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change. No configuration key is added, removed, or
  redefined; the refresh's contract is an adapter obligation, not a setting.
- `SPEC.md` Section 17 (test matrix) — covered by step 5 (Sections 17.3, 17.4).
- `SPEC.md` Section 18 (checklist) — covered by step 6 (Section 18.1.3).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no row owed.** This decision adds no `Implementation-
  defined` behaviour and no MUST-document clause: it replaces an adapter obligation with a wider one
  and fixes a disposition the document left open, both of which close choices rather than delegate
  them. As decision 0155 recorded, `scripts/validate_spec_consistency.py` is not evidence either way
  here — its obligation check collapses the template's `8.x` extension citation to `8` — so this is
  a checked judgement, not a green run.
- `conformance/vocabulary.json` — unchanged. The absent case introduces no token: it is a branch
  that changes no state, and its cause reaches no log field. The stop causes stay prose, as Section
  8.5's existing ones are.
- `conformance/vectors/` — covered by step 7 (new file `reconcile-disposition.json`).
- `conformance/README.md` — covered by steps 7 and 8.
- `scripts/validate_spec_consistency.py` — no check-7 row. Check 7 covers vectors whose `expect`
  enumerates a set a section fixes; `reconcile-disposition.json`'s `expect` is a computed
  disposition, which is the shape decision 0154 surveyed and found the corpus otherwise made of.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. The
  tracker adapter and reconciliation are Symphony's; the engine has no part in either.

## Ordering

**Depends on decision 0155 having landed**, and its `Plan.md` having been applied. Step 2 edits the
Refresh completeness block 0155 introduced, and step 6 edits the Section 18.1.3 item 0155 widened;
neither anchor exists before 0155 is applied. Step 3's absent branch sits beside the
standing-condition branch 0155 added, and step 7's vector pins that branch's disposition alongside
the other five.

The premise step 1 rests on is Section 11.1's silence about the result's shape, which 0155 left
untouched: its Refresh completeness block is stated in Section 11.2, over the fields one caller
reads. That is the sentence this decision widens, and it is why the two are separable — 0155 is
complete and consistent without this one, and this one is not statable without it.

## Anchor changes

New:

- `reconcile_disposition` — the function `conformance/vectors/reconcile-disposition.json` names for
  Part B's per-issue decision (step 7). `SPEC.md` states the behaviour in Section 8.5 and Section
  16.3 and does not name the function; the vector file's `function` is the corpus's own dispatch
  name, as `worker_exit_disposition` and `retry_fire_disposition` already are.
- `conformance/vectors/reconcile-disposition.json` — new vector file (step 7).

Changed:

- `SPEC.md` Section 11.1 REQUIRED Operations — the `fetch_issue_states_by_ids` entry gains the
  result's shape (step 1).
- `SPEC.md` Section 11.2 Adapter Semantics — the Refresh completeness block's field list is replaced
  by the complete record (step 2). A plan quoting decision 0155's field-subset wording records what
  was true when written and is not edited.
- `SPEC.md` Section 8.5 Active Run Reconciliation — Part B names the collection it iterates and
  gains a fourth case (step 3).
- `SPEC.md` Section 16.3 Reconcile Active Runs — `reconcile_running_issues` iterates the running ids
  and looks records up by id (step 4).
- `SPEC.md` Section 17.3 Issue Tracker Client — the refresh row asserts the record (step 5).
- `SPEC.md` Section 18.1.3 Daemon Conformance — the enumeration item names the record (step 6).
- `SPEC.md` Section 14.5 Operator Intervention Points — a bullet for deleting an issue, which this
  decision's disposition leaves the run running through (a finding from applying the plan).

Removed: nothing. `fetch_issue_states_by_ids` keeps its name, declined here on decision 0155's own
ground; no field, error class, state name, or section title is renamed or removed.

Not edited, and deliberately: `decisions/0140-assignee-routing-condition/Background.md` and
`decisions/0148-issue-routing-substrate/Background.md` both describe Section 8.5 Part B as having no
absent branch, and `decisions/0155-standing-conditions/Background.md` describes the Refresh
completeness obligation as being over the fields the standing conditions read. All three record what
was true when written; a decision record is not re-derived when a later decision moves the text it
cites.

## Status

Applied. Steps 1 to 6 are in `SPEC.md`; steps 7 and 8 are in
`conformance/vectors/reconcile-disposition.json` and `conformance/README.md`. Issue #121.

Reviewed with the `plan-review` skill before the first edit, against `b9f62c7`. Four lenses:
`check_plan_anchors.py` reports 0 findings from 10 quoted spans; two Q findings were repaired in the
plan (a quotation attributed to `conformance/README.md` that belongs to two decision records, and
one attributed to Section 12.4 that belongs to Section 11.2); one P finding was repaired (step 1
falsifies Section 11.2's own closing sentence asserting Section 11.1 is silent about the result, and
the plan had kept that sentence with no producer for its premise — step 2 now requires it repaired);
and one C deviation is recorded, that decision 0155's application was committed on a branch in the
primary worktree rather than a sibling one. This decision lands in
`../symphony-0156-refresh-record-and-absent-ids`.
