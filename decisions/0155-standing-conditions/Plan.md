# Plan — 0155 The conditions that keep holding, and the repository nothing recorded

## Scope

- `SPEC.md` — Section 4.1.8 Orchestrator Runtime State, Section 7.1 Issue Orchestration States,
  Section 7.3 Transition Triggers, Section 8.2 Candidate Selection Rules, Section 8.5 Active Run
  Reconciliation, Section 8.7 Multiple Repositories and Shared Polling, Section 9.11 Node-Scheduler
  Adapter (its `signal_done` bullet only), Section 11.2 Adapter Semantics, Section 14.4 Partial
  State Recovery (Restart), Section 14.5 Operator Intervention Points, Section 16.3 Reconcile Active
  Runs, Section 16.4 Dispatch One Issue, Section 17.3 Issue Tracker Client, Section 17.4
  Orchestrator Dispatch, Reconciliation, and Retry, and Section 18.1.3 Daemon Conformance.
- `conformance/vectors/standing-conditions.json` — new file.
- `conformance/README.md` — a new "Surfaced findings" entry.
- `SPEC.md` Section 5.3.1 `tracker` (object) — unchanged, cited only. It already requires
  `required_labels` and `assignee` "to dispatch or continue"; the gap this decision closes is that
  nothing evaluates that clause once a run is in flight, not that the clause is missing.
- `SPEC.md` Section 9.1 Workspace Layout — unchanged, cited only. Its `repo_key` keying is why a
  workspace a re-routed run leaves behind is an orphan rather than something reconciliation can find
  under the repository the mapping now selects (step 3).
- `SPEC.md` Section 6.2 Dynamic Reload Semantics — unchanged, cited only. Its requirement that the
  operator policy config reload without restart is why re-evaluating the routing mapping at refresh
  is a live check rather than a recomputation of the value dispatch already read (step 2).
- `SPEC.md` Section 6.4 Core Config Fields Summary (Cheat Sheet) — no change. It documents
  configuration fields; `repository` is a runtime-state member this decision adds to a `running`
  entry, not a configuration key, and no configuration key changes.
- `SPEC.md` Section 19 Conformance Statement — no change. The disposition this decision adds is a
  fixed, non-`Implementation-defined` behavior; it creates no new "MUST document" obligation for
  Section 19's enumeration to carry.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed. `running` stays `Reconstructable`, and a new
  member of a `running` entry's value is not a new top-level Section 4.1.8 field; see Cross-cutting
  sync.
- `conformance/vocabulary.json` — unchanged. Its `runtime_state_fields` group is over Section
  4.1.8's top-level fields; `repository` is a member of one of those fields' values, not a new
  field.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. Standing
  conditions, reconciliation and issue-to-repository routing are orchestrator-side scheduling
  concepts the engine has no notion of.

## Steps

1. **`SPEC.md` Section 8.2 Candidate Selection Rules — the record's conditions are standing; the
   run's own state is not.** Ensure the section gains a closing paragraph stating that the
   conditions Section 8.2 tests over the issue record are *standing*: re-evaluated on every
   issue-state refresh for as long as the run is in flight, not only once at dispatch. Ensure the
   same paragraph names the `running`-membership bullet, the `claimed`-membership bullet, and the
   two concurrency-slot bullets as dispatch-time only, and states why: a run already in flight holds
   the `running` entry and the `claimed` membership those two bullets test, and already occupies the
   slot the remaining two count, so re-tested against a run already dispatched every one of the four
   is false by construction, and an implementation that re-ran the whole predicate wholesale on
   every refresh would stop every run it checked. Ensure the paragraph carves out one exception to
   the record being standing: the `Todo` blocker bullet stays dispatch-time only, with its reason
   stated — making it standing would put the issue's dependency graph into every refresh, on every
   tick, for every running issue. Ensure the paragraph disposes of the two record bullets that are
   neither a filter nor the blocker rule, so nine bullets are accounted for rather than four named
   and the rest implied. Ensure the field-presence bullet — in `SPEC.md` Section 8.2, "It has `id`,
   `identifier`, `title`, and `state`." — is stated to be a well-formedness test on the record the
   adapter returns rather than a standing condition: a refresh that omits one of those fields is the
   adapter obligation step 7 adds, surfacing as a refresh failure, and it MUST NOT be read as a
   standing-condition loss that stops the run. Ensure the state-membership bullet is stated to be
   standing already, evaluated by Section 8.5 Part B today, so the new rule reads as extending an
   existing practice rather than introducing one. *Done when:* Section 8.2 states, for every bullet
   it lists, whether a reconciliation pass may re-test it, naming the four orchestrator-state
   bullets and the blocker bullet rather than leaving them to be inferred from the closing
   paragraph's general claim.

2. **`SPEC.md` Section 8.7 Multiple Repositories and Shared Polling — routing gains a continue
   clause, stated over the run.** Ensure the "Issue-to-repository routing:" bullets gain a new
   bullet requiring that routing is a standing condition too: for a run already dispatched, the
   mapping is re-evaluated against the current normalized record on every issue-state refresh, and
   the result MUST still name the repository the run holds. Ensure the clause is stated over the
   *run* — testing the run's own recorded `repository` (Section 4.1.8, step 5) against a fresh
   evaluation of the mapping — rather than over the issue: an issue-side phrasing that asks only
   whether the issue still routes is circular at dispatch, where routing is what selects the
   repository in the first place, so there is nothing yet to compare it against. Ensure the clause
   cites Section 6.2 Dynamic Reload Semantics for why re-evaluating the mapping is a live check and
   not a recomputation of a value already known: Section 6.2 requires the operator policy config —
   the mapping's own artifact — to be re-read and re-applied without restart, so the mapping in
   force at refresh time may differ from the one in force at dispatch. *Done when:* Section 8.7
   states a continue condition for routing in the same terms Section 5.3.1 already states one for
   `tracker.required_labels` and `tracker.assignee`, addressed to the run rather than to the issue.

3. **`SPEC.md` Section 8.5 Active Run Reconciliation — Part B's active branch splits on the standing
   conditions, on the release side of the claim partition.** Ensure the bullet "If tracker state is
   still active: update the in-memory issue snapshot." is qualified to update the snapshot only
   where the standing conditions (Section 8.2's record conditions, Section 8.7's routing condition)
   still hold. Ensure a new bullet is added beside it for the case where tracker state is still
   active but a standing condition no longer holds, with disposition: terminate the worker, release
   the claim, arm no retry, leave the workspace. Ensure the step states which side of Section 8.5's
   claim partition the branch is on, since Section 8.5 itself requires it: "A site added later MUST
   state which side of that partition it is on." Ensure it names the release side —
   `terminate_running_issue` (Section 16.3), armed with no retry behind it, the same disposition
   Part B's other two terminating branches already carry. Ensure Section 8.5 gains the cleanup
   rationale it has never stated for its existing split between cleaning and leaving the workspace,
   and extends it to the new branch: cleanup means the work is finished, while a standing-condition
   loss is reversible and can be caused by an operator editing a mapping or a label, so removing the
   workspace would be an unrecoverable response to what may be a config typo. Ensure the cost of
   leaving the workspace is named honestly as a reconsideration trigger rather than left implicit:
   Section 9.1 Workspace Layout keys the per-issue workspace path by `repo_key`, so a workspace a
   re-routed run leaves behind is a permanent orphan under the repository the mapping now selects.
   Ensure Section 8.5's remote-executor bullet is widened past its current "a terminal or non-active
   decision" to also forward a standing-condition loss over the seam, on the same
   connected/disconnected split the bullet already draws. Ensure Section 9.11's `signal_done`
   bullet, which today enumerates the same two causes as reconciliation stopping a run "for a
   terminal or non-active issue (Sections 8.5, 8.6)", is widened the same way, so a run
   reconciliation stops for a standing-condition loss also gets its `signal_done`. Ensure the stop
   is made operator-visible, naming which condition failed, unlike the terminal and non-active
   branches beside it: the operator can read those off the tracker directly, but a
   standing-condition loss may trace to a third party's label edit or an operator's own mapping
   change, neither visible from the issue alone. Ensure Section 8.5's own consequence bullet in
   `SPEC.md`, which today reads "A run stopped because its issue reached a terminal or non-active
   state schedules no retry at all.", enumerates the standing-condition loss as a third such cause:
   that bullet is where Section 8.5 states what the no-retry disposition costs and why the invariant
   is stated in the section rather than left to Section 16, so a fourth branch that arms no retry
   belongs inside it rather than beside it. *Done when:* Part B disposes of an
   active-but-no-longer-standing issue on the release side of the partition, the branch's cleanup
   choice has a stated reason rather than sitting beside a rationale-free precedent, the consequence
   bullet enumerates three causes rather than two, and both the remote-executor bullet and Section
   9.11's `signal_done` bullet forward it too.

4. **`SPEC.md` Section 16.3 Reconcile Active Runs — `standing_conditions_hold` gates the active
   branch, tested first.** Ensure `reconcile_running_issues`'s active branch — today
   `state.running[issue.id].issue = issue` reached whenever `issue_state` is in `active_states` —
   tests `standing_conditions_hold` first, before writing the snapshot: where it holds, the snapshot
   update proceeds unchanged; where it does not, the branch stops the run through
   `terminate_running_issue` the same way the terminal branch does, and the snapshot is not updated.
   Ensure the predicate is named `standing_conditions_hold` — the shared name for what Section 8.2
   and Section 8.7 both define as standing (step 1, step 2) — rather than a fresh name coined for
   this call site alone. Ensure Section 16.3's `terminate_running_issue` trailing comment is
   corrected: it currently reads "for either of its two branches", true only while Part B has
   exactly two branches that release without arming a retry; ensure it instead states that Part B
   queues no retry for any of its branches, so the comment does not fall out of date the next time
   Part B grows one. *Done when:* the active branch reads as a two-way test with
   `standing_conditions_hold` evaluated before the snapshot is touched, and the
   `terminate_running_issue` comment is accurate for the branch count Part B has after step 3.

5. **`SPEC.md` Section 16.4 Dispatch One Issue and Section 4.1.8 Orchestrator Runtime State — the
   running entry gains `repository`, recorded once at dispatch.** Ensure the running-entry literal
   `dispatch_issue` writes gains a `repository` member, valued from `repo_of(issue)` — the same
   expression the function already evaluates twice, once for `ensure_object_store` and once for the
   provisioning-failure log call, and stores nowhere today. Ensure Section 4.1.8's `running` bullet
   describes the new member in the shape it already uses for `run_id`: today the bullet states "each
   entry carries the `run_id` of the run attempt it holds (Sections 4.1.5, 16.4), so the key and the
   entry's identity are different things and a message can be decided against the entry rather than
   against the key"; ensure a parallel sentence states that each entry also carries the `repository`
   it was dispatched to, recorded once at dispatch rather than recomputed, so a later re-evaluation
   of the routing mapping (step 2) has something fixed to compare against. Ensure `running` keeps
   its `Reconstructable` recovery class, and ensure the reason covers both workspace layouts Section
   9.1 defines rather than only the first: where one instance manages several repositories the path
   carries `repo_key` and the member is read back from it, and where it manages one the single
   managed repository is the only value the member can hold. The member therefore changes nothing
   about how the field recovers, in either layout. *Done when:* every entry `dispatch_issue` writes
   carries `repository`, and Section 4.1.8's bullet documents it beside `run_id` rather than leaving
   it to be inferred from the pseudocode.

6. **`SPEC.md` Section 7.1 Issue Orchestration States and Section 7.3 Transition Triggers — the
   state machine names the new cause and widens two triggers.** Ensure Section 7.1's `Released`
   cause list gains a third item beside "Terminal or non-active issue: reconciliation terminates the
   run and `terminate_running_issue` releases the claim with the running entry (Sections 8.5,
   16.3)." and the retry-path cause that follows it: a standing condition no longer holding,
   releasing the claim the same way through `terminate_running_issue`, with no retry taking it over.
   Ensure the `Reconciliation State Refresh` trigger in Section 7.3, which today reads "Stop runs
   whose issue states are terminal or no longer active." and "Schedule no retry for a run stopped
   this way.", is widened to also stop a run whose standing conditions no longer hold, scheduling no
   retry for that case either. Ensure Section 7.1's worker post-turn re-check — today "After each
   normal turn completion, the worker re-checks the tracker issue state." and, also in Section 7.1,
   "If the issue is still in an active state, the worker SHOULD start another turn on the same live
   coding-agent thread in the same workspace, up to `agent.max_turns`." — widens with the two
   conditions a worker can evaluate from the record it already re-fetches for the state check:
   `tracker.required_labels` and `tracker.assignee`, Section 5.3.1's two filters. Ensure the
   worker's check does not widen to routing: routing needs the full mapping re-evaluated over the
   run's recorded `repository` (step 2), which is reconciliation's standing-condition check rather
   than a test the worker's own post-turn loop repeats. *Done when:* `Released`'s cause list, the
   `Reconciliation State Refresh` trigger, and the worker's post-turn condition each name the
   standing conditions they now cover, and the worker's post-turn scope stops at the two filters
   rather than silently including routing.

7. **`SPEC.md` Section 11.2 Adapter Semantics — a new Refresh completeness block, and the Linear
   bullet loses its behavioral half.** Ensure Section 11.2 gains a block titled *Refresh
   completeness* beside the existing "Candidate enumeration" block, in the same shape: today that
   block states "`fetch_candidate_issues` (Section 11.1) MUST return the complete set of matching
   issues.", and Section 11.2 goes on to state "A silently partial result is non-conformant, because
   the orchestrator's priority sort and dispatch (Section 8.2) assume the complete candidate set."
   Ensure the new block states the parallel guarantee for `fetch_issue_states_by_ids` — for every id
   it was given, it MUST return a normalized record carrying the fields the standing conditions read
   (state, labels, assignees, and the routing fields the adapter populates), and a silently partial
   result is non-conformant, because Section 8.5 Part B and the standing-condition check (step 3,
   step 4) assume the refresh is complete. Ensure the Linear-specific bullet Section 11.2 lists
   under "Linear-specific requirements", which today reads "Candidate and issue-state refresh
   queries include issue labels and assignees, and the routing fields the adapter populates
   (`project`, `team`). Required-label, configured-assignee and routing filtering happens after
   normalization so refresh can observe a label removal, an assignment change, or an issue moved
   between projects or teams, and stop or release existing work.", keeps only its first sentence —
   the GraphQL specifics of which fields the query includes — and loses the second: the behavior it
   states is now Section 11.2's general completeness guarantee and Section 8.5 Part B's evaluation
   of it, not a Linear-specific claim. Ensure the new block does **not** carry a counterpart to the
   hard-cap clause the enumeration block ends with — in `SPEC.md` Section 11.2, "Where a backend API
   hard-caps results with no way to page further, the cap is an `Implementation-defined` limitation
   the adapter MUST document" — because a refresh is over a caller-supplied id list rather than an
   open result set, so there is no cap to document. Ensure this is checked rather than assumed while
   applying: if the block is written with any `Implementation-defined` or MUST-document clause after
   all, its row goes into `CONFORMANCE-STATEMENT-TEMPLATE.md` in the same commit (decision 0128),
   and the Cross-cutting sync entry below stops being true. Ensure `fetch_issue_states_by_ids`
   (Section 11.1) keeps its name even though the new guarantee asks it for a record rather than only
   a state, and ensure the tension is recorded rather than silently resolved: a rename was
   considered and declined. In `SPEC.md` the operation is named at three sites — its
   REQUIRED-operations entry in Section 11.1, `reconcile_running_issues` in Section 16.3, and the
   worker's post-turn re-check in Section 16.6 — and Sections 17.3 and 17.4 describe the same
   operation in prose as the issue-state refresh, so a rename is five edits to the adapter
   contract's surface for a readability gain with no behavioral content. Ensure the record states
   the reach as it is rather than overstating it: the behavior corpus does not name the operation at
   all, so a rename is `SPEC.md`-local, and it is declined here because a contract-surface rename
   decided as a side effect of a reconciliation repair is a decision of its own rather than because
   it would be expensive. *Done when:* Section 11.2 states a completeness guarantee for the refresh
   in the same terms it already states one for enumeration, and the Linear bullet asserts only the
   GraphQL specifics.

8. **`SPEC.md` Section 14.4 Partial State Recovery (Restart) and Section 14.5 Operator Intervention
   Points — the run registry carries the repository, and the operator table gains two causes.**
   Ensure Section 14.4's sentence "In remote mode the orchestrator maintains a *run registry* — a
   `Durable`-class mapping (Section 14.3) from each in-flight run to its issue and its node." is
   extended to carry the repository as well, so a run reattached after a restart or a moved node
   (Section 14.4's own `lookup_by_run_id` reattachment) has the same left-hand side to test standing
   conditions against that step 5 gives a run dispatched without a restart in between. Ensure
   Section 14.5's bulleted operator-intervention table gains two cases in the shape of its existing
   "terminal state -> running session is stopped and workspace cleaned when reconciled" and
   "non-active state -> running session is stopped without cleanup" bullets: removing a required
   label or changing the assignee on the tracker, and editing the routing mapping so the issue no
   longer routes to the run's repository, both -> running session is stopped, the claim released, no
   retry armed, and the workspace left. *Done when:* Section 14.4's run registry sentence names the
   repository, and Section 14.5's table lets an operator predict the standing-condition disposition
   from the same table that already answers the terminal and non-active cases.

9. **`SPEC.md` Section 17.3 Issue Tracker Client and Section 17.4 Orchestrator Dispatch,
   Reconciliation, and Retry — the refresh-completeness row replaces the minimal-issues row, and
   three rows in 17.4 follow.** Ensure Section 17.3's row "Issue state refresh by ID returns minimal
   normalized issues" is replaced — not extended beside it — with a row requiring the refresh to
   return the fields the standing conditions read (Section 11.2's new completeness guarantee, step
   7): the replaced row licensed exactly the silently-partial result the new guarantee forbids, so
   the two cannot stand together. Ensure Section 17.4's row "An assignment removed while a run is in
   flight is observed on the issue-state refresh and stops or releases that run, as a removed
   required label is" is rewritten as a first-class check in its own right — both the required-label
   loss and the assignee loss stop or release the run, each on its own row or the same row stated
   symmetrically — dropping the trailing "as a removed required label is" comparison now that both
   are stated directly rather than one borrowing the other's justification. Ensure a new row is
   added for the routing outcome: a routing mapping edit that no longer selects the run's recorded
   `repository` (step 2, step 5) stops or releases that run the same way. Ensure the row "If a
   remote node-scheduler is implemented, an in-flight remote run reattaches via `lookup_by_run_id`
   after an orchestrator restart or a moved node, and the buffered event stream replays with no gap
   in token accounting" is widened to assert that the reattached entry carries the repository the
   run registry recorded (step 8), so reconciliation's standing-condition check has a run-side
   repository to compare the freshly evaluated mapping against. Ensure Section 17.4's row in
   `SPEC.md` reading "A run stopped because its issue reached a terminal or non-active state
   schedules no retry, and its claim is released without waiting for a backoff to elapse" names the
   standing-condition stop as a third cause carrying the same disposition, this row being the
   matrix's twin of the Section 8.5 consequence bullet step 3 widens. Ensure Section 17.4's
   remote-executor row in `SPEC.md`, which today asserts that "a terminal issue stops a connected
   run via the forwarded signal and a disconnected run via the executor's pre-finalize re-check, and
   `signal_done` is emitted on completion and on terminal/cancel", widens with the seam bullet and
   the `signal_done` bullet step 3 addresses, so the matrix does not check a narrower set of
   forwarded causes than the sections it is derived from require. *Done when:* Section 17.3 no
   longer licenses a partial refresh, and Section 17.4 checks the assignee loss, the label loss, the
   routing loss, and the reattached repository each as named rows rather than folding one into
   another's justification, and no row in either section still enumerates the terminal and
   non-active causes as the whole set.

10. **`SPEC.md` Section 18.1.3 Daemon Conformance — three checklist items widen.** Ensure Section
    18.1.3's eligibility item — today "Candidate eligibility evaluated over the normalized record
    and the resolved configuration: every label in `tracker.required_labels` present, and the issue
    assigned to a configured `tracker.assignee`, both compared under `Lowercase Normalization`; a
    null configured assignee does not gate (Sections 4.2, 8.2)" — gains its continue arm: the same
    two conditions apply for as long as the run is in flight, not only at dispatch. Ensure Section
    18.1.3's reconciliation item — today "Reconciliation that stops runs on terminal/non-active
    tracker states, owning the removal and runtime accounting for the runs it terminates so a worker
    exit it caused queues no retry (Section 8.5)" — names the standing-condition case as a third
    stop condition beside terminal and non-active tracker states. Ensure Section 18.1.3's
    enumeration-completeness item — today "`fetch_candidate_issues` enumerates the complete matching
    set (adapter paginates internally); a silent partial result is non-conformant" — gains the
    refresh half: `fetch_issue_states_by_ids` returns the standing conditions' fields for every id
    given, and a silent partial result there is non-conformant too (Section 11.2, step 7). *Done
    when:* all three items name the continue/standing-condition half beside the dispatch/enumeration
    half they already state, rather than leaving the daemon checklist silent on the case decision
    0155 introduces.

11. **`conformance/vectors/standing-conditions.json` (new) and `conformance/README.md` — a vector
    file and its Surfaced-findings entry.** Ensure a new vector file exercises
    `standing_conditions_hold` (Section 16.3, step 4) over `spec_refs` Section 5.3.1, Section 8.2,
    Section 8.7, Section 16.3, in the shape `conformance/vectors/candidate-eligibility.json` and
    `conformance/vectors/issue-routing.json` already establish for `should_dispatch` and
    `route_issue`: a `given` carrying a running issue's original `repository` and a current
    normalized record and routing rules, and an `expect` of `{ holds: boolean, failed: <condition> |
    null }`. Ensure the vectors cover three routing outcomes — the mapping still selects the run's
    recorded `repository`; the mapping now selects a different single repository; the mapping now
    selects zero or more than one — plus a required-label-removed case and an assignee-changed case,
    so every standing condition step 1 and step 2 name has at least one vector. Ensure
    `conformance/README.md` gains a "Surfaced findings" entry recording the gap this decision
    closes: Section 8.5 Part B and Section 16.3's `reconcile_running_issues` evaluated tracker state
    alone, never `tracker.required_labels`, `tracker.assignee`, or routing, despite `SPEC.md`
    Section 5.3.1 already requiring the first two "to dispatch or continue" — a second instance of
    the state-gap class decision 0137 named, this time a condition Core behavior already required
    going unevaluated at the one site meant to keep re-evaluating it, rather than state the class
    0137 repaired. *Done when:* the vector file exists with the three routing outcomes and the two
    filter cases, and `conformance/README.md` names decision 0155, the vector file, and the gap in
    the same terms the existing 0137 and 0154 entries use.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change. `repository` is a runtime-state member
  (step 5), not a configuration field, and the routing mapping's own configuration schema is
  unchanged by this decision (it was already unpinned by `SPEC.md`, per
  `conformance/vectors/issue-routing.json`'s notes).
- `SPEC.md` Section 17 (test matrix) — covered by step 9 (Sections 17.3, 17.4).
- `SPEC.md` Section 18 (checklist) — covered by step 10 (Section 18.1.3).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed, on two counts. This decision introduces no
  `Implementation-defined` behavior and no MUST-document obligation: the disposition is fixed, the
  operator report is stated in the shape `SPEC.md` Section 8.7 already uses for a reported routing
  ambiguity, and the Refresh completeness block deliberately carries no hard-cap clause (step 7).
  And `running` stays `Reconstructable` (step 5), and
  both `conformance/vocabulary.json`'s `runtime_state_fields` group and the template's
  recovery-class rows are over `SPEC.md` Section 4.1.8's top-level fields; a new member of a
  `running` entry's value is not a new top-level field. This is a judgement rather than a checker
  result: `scripts/validate_spec_consistency.py`'s obligation check will not catch a missing
  template row for `SPEC.md` Section 8.5 even if one were owed: `CONFORMANCE-STATEMENT-TEMPLATE.md`
  already carries a Cost extension row citing `8.x`, and the check collapses that citation to `8`,
  treating it as covering every Section 8 subsection. A green run from that script is therefore not
  evidence for this row; the absence of an owed obligation is.
- `conformance/vocabulary.json` — unchanged, for the same top-level-field reason. No token is added,
  renamed, or removed.
- `conformance/vectors/` — covered by step 11 (new file `standing-conditions.json`).
- `conformance/README.md` — covered by step 11 ("Surfaced findings" entry).
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. This
  decision is entirely orchestrator-side scheduling and reconciliation; it introduces no
  engine-facing concept, operation, or obligation.

## Ordering

Independent. Decision 0154 has merged (PR #125), and there are no in-flight sibling decisions this
plan needs to sequence against.

This decision builds on six earlier ones rather than revising any of them:

- **Decision 0140**, *A dispatch condition no configuration and no record could supply*, and
  **decision 0148**, *Routing keys and the record they route over*, established the two record
  attributes and the routing keys step 1 and step 2 make standing — required_labels/assignee's
  dispatch-time gating and the routing mapping's key space respectively — without touching Part B.
  This decision is what makes both continue rather than only dispatch.
- **Decisions 0138** (*The function five call sites named and no section defined*), **0144** (*What
  a concurrency slot counts, and when a run starts occupying one*) and **0145** (*The claim nothing
  released*) established `terminate_running_issue` as the shared termination function and the
  exhaustive three-way claim partition step 3's fourth branch declares its side of. This decision
  adds a caller to that partition; it does not change the partition's shape.
- **Decision 0137**, *A backoff kept per repository, and the state model with no repository in it*,
  named the class step 11's `conformance/README.md` entry cites: Core behavior requiring state
  `SPEC.md` Section 4.1.8 had no room for. This decision's `repository` member (step 5) is a second
  instance of that class, not a new one, and follows 0137's repair shape — a field named and given a
  recovery class rather than left implicit.
- **Decision 0128**, *A table that is complete against itself is where a missing obligation hides*,
  is why the Cross-cutting sync entry for `CONFORMANCE-STATEMENT-TEMPLATE.md` states its no-row
  judgement explicitly rather than silently omitting the row: decision 0128's rule is that an
  obligation with no row is invisible to every check, so its absence here is recorded as a checked
  judgement rather than an oversight.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0155-standing-conditions/Plan.md --rev 85cb892`,
run from the worktree root against the revision this plan targets.

The first pass reported 57 findings — all Q (quote fidelity), caused by this plan's own mistakes
rather than anything in `SPEC.md`: section titles and decision titles written in straight double
quotes, which the checker reads as a claim that the title occurs as body prose, and several steps
citing a section number inside a quoted span that then leaked into the next quote's attribution
without being restated. Both classes were fixed at the plan level — titles unquoted or italicized,
section numbers restated immediately before each quote that follows another — never by loosening a
quotation to make it pass. One genuine R (reach) finding surfaced once the Q findings cleared:
Section 9.11's `signal_done` bullet enumerates the same "terminal or non-active issue" causes
Section 8.5's remote-executor bullet does, and needed the same widening; it is now folded into
step 3, and Section 9.11 is named in Scope.

Three further sites were found by reading for the premise this plan removes rather than by the
checker, which could not report them because the plan did not yet quote the wording they share.
Section 8.5's consequence bullet, Section 17.4's row on a run stopped for a terminal or non-active
state, and Section 17.4's remote-executor row each enumerate the two causes reconciliation stops a
run for, as the whole set. A fourth branch that arms no retry and is forwarded over the seam makes
all three under-state what the document requires while every one of them stays literally true, which
is why no mechanical check reaches them: nothing they say becomes false. Steps 3 and 9 now name
them. The lesson is recorded rather than left to the next such decision — an enumeration widened in
one section has twins wherever the matrix restates it, and R finds them only once the plan quotes
the enumeration itself.

The current run reports no finding from 47 quoted spans. That silence is this section working
rather than the sites having gone away: R asks whether the plan names a reached site's anchor, and
naming the six below is what answers it. Each was read at `85cb892` and judged benign, and the
judgement is recorded here so a later editor sees an assessment rather than an absence:

- `conformance/vectors/worker-exit-disposition.json:5` (`description`) carries "the run_id of the",
  reached from step 5's quote of Section 4.1.8's `run_id` sentence. Benign, and checked past the
  shared phrase: the vector decides what an arriving worker-lifecycle message does, and its premise
  is that a run was terminated by reconciliation and replaced — which a standing-condition
  termination instantiates rather than contradicts. Every expectation in the file holds unchanged
  with a fourth branch reaching `terminate_running_issue`, and the new `repository` member is not
  among the inputs it reads.
- `SPEC.md:3085` (Section 11.8) carries "if the issue is", reached from step 6's quote of Section
  7.1's worker post-turn condition. Benign: Section 11.8 states `set_state`'s idempotency condition
  ("if the issue is already in `target_state`"), a different subject sharing the connective phrase.
- `SPEC.md:3519` (Section 13.8.2) carries "if the issue is", reached the same way. Benign: this is
  the HTTP status API's `404` condition ("if the issue is unknown to the current in-memory state"),
  unrelated to standing conditions or the worker's turn loop.
- `SPEC.md:2481` (Section 10.2) carries "on the same live", reached from step 6's quote of Section
  7.1's "same live coding-agent thread" phrase. Benign: Section 10.2 states the app-server mechanics
  of starting a continuation turn on the same thread once a continuation has been decided on; it
  does not restate the *condition* under which a continuation happens, which is what step 6 widens,
  so it stays accurate unchanged.
- `SPEC.md:3055` (Section 11.7) carries "the adapter populates project", reached from step 7's
  retained first sentence of the Linear bullet. Benign: Section 11.7 declares the tracker adapter's
  static, once-per-run capability (whether it populates `project`/`team` at all), which step 7 does
  not touch; the new completeness guarantee is about a given refresh call returning those fields for
  an issue the adapter already declares it populates, not about the declaration itself.
- `conformance/README.md:461` carries "the runs it terminates", reached from step 10's quote of
  Section 18.1.3's reconciliation item. Benign: that sentence is decision 0138's own historical
  entry describing the `terminate_running_issue` no-op-guard fix; it is decision-log prose about a
  past repair, not a live site this decision's reconciliation-ownership language needs to touch.

`python3 scripts/validate_spec_consistency.py` reports 0 errors, 0 warnings, unchanged before and
after this plan was written — expected, since this plan does not itself edit `SPEC.md` or any
conformance artifact.

## Anchor changes

New:

- `repository` — a member `SPEC.md` Section 4.1.8 and Section 16.4 add to the `running` map's
  per-issue entry, recorded once at dispatch from `repo_of(issue)`. Not a new Section 4.1.8
  top-level field and not a new `runtime_state_fields` token (step 5).
- `standing_conditions_hold` — the predicate `SPEC.md` Section 16.3 names in
  `reconcile_running_issues`, testing Section 8.2's record conditions and Section 8.7's routing
  condition together (step 4).
- `conformance/vectors/standing-conditions.json` — new vector file for `standing_conditions_hold`
  (step 11).

Changed:

- `SPEC.md` Section 8.5 Active Run Reconciliation — Part B's still-active bullet is qualified on the
  standing conditions holding, and a new bullet disposes of the case where they do not (step 3).
- `SPEC.md` Section 16.3 Reconcile Active Runs — `reconcile_running_issues`'s active branch gains
  the `standing_conditions_hold` test, and `terminate_running_issue`'s trailing comment is corrected
  for the new branch count (step 4).
- `SPEC.md` Section 11.2 Adapter Semantics — the Linear-specific bullet loses its second sentence;
  the behavior it stated moves to the new Refresh completeness block and to Section 8.5 Part B's
  evaluation of it (step 7).
- `SPEC.md` Section 17.3 Issue Tracker Client — its row on minimal normalized issues, quoted in step
  9, is replaced by a completeness row (step 9).
- `SPEC.md` Section 17.4 Orchestrator Dispatch, Reconciliation, and Retry — the assignment row is
  rewritten to drop its trailing comparison to the required-label row; the reattach row is widened
  to assert the reattached entry carries `repository` (step 9).

Removed: nothing. Every changed sentence above is qualified, widened, or replaced by a statement of
the same behavior in a fuller form; no rule this decision touches is dropped without a successor
stating what happens instead. A plan quoting `SPEC.md` Section 11.2's pre-0155 Linear bullet in
full, or `SPEC.md` Section 17.3's pre-0155 "minimal normalized issues" row, is not edited; it
records what was true when written.

## Status

Not started. This PR carries the decision record only; `SPEC.md` is untouched by it.
