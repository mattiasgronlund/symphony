# Background — 0155 The conditions that keep holding, and the repository nothing recorded

## Context

Issue #121, filed from the `symphony-rs` build against `4d610da`, reports that reconciliation's
stop-on-attribute-loss rule is stated in Section 11.2 — the **Linear adapter's** own section — and
nowhere Section 8.5 Part B can be read from. Section 11.2's Linear bullet says it outright:

> Required-label, configured-assignee and routing filtering happens after normalization so refresh
> can observe a label removal, an assignment change, or an issue moved between projects or teams,
> and stop or release existing work.

Part B, the general reconciliation rule every adapter is dispatched through, carries no such branch.
Investigation widened the defect past the one report in three ways, each its own section below: the
rule this quote describes already exists as a MUST for two of the four attributes and Part B honors
neither; three independent passages agree reconciliation is state-only, so the omission is a design
position rather than an oversight; and nothing in the running entry ties a dispatched run to the
repository it was dispatched to, so a mapping edit mid-run is invisible by construction.

## The rule already exists for two of the four attributes, and three sites agree not to check it

Section 5.3.1 states, for `tracker.required_labels`, "An issue MUST contain every configured label
to dispatch or continue," and for `tracker.assignee`, "An issue MUST be assigned to the configured
assignee to dispatch or continue: its `assignees` (Section 4.1.1) contain the configured value."
"dispatch or continue" as a clause occurs exactly twice in `SPEC.md`, both in Section 5.3.1, and
nowhere else — `grep -c "or continue"` returns a third hit, but it is `continues` in an unrelated
sentence about an executor disconnected from the seam. That MUST is Core today, and nothing
downstream of dispatch reads it a second time: Section 8.2's eligibility bullets test
`required_labels` and `assignee` once, at candidate selection, while Section 8.5 Part B — which runs
every tick an issue is in flight — tests neither. Routing — `project`/`team` — never had a continue
clause to fail to honor, because decision 0148 stopped at making a mid-run routing move *visible* to
the refresh and never said what reconciliation does with it; Section 8.7's routing bullet, "Each
polled issue is routed to exactly one repository," is a dispatch-time statement over the candidate
set Section 8.1 fetches each tick, not over a run already under way.

This is not one oversight but three passages agreeing with each other. Section 8.5 Part B enumerates
terminal, active, and neither, no fourth branch; Section 16.3's `reconcile_running_issues`
pseudocode mirrors that exactly (`terminal_states`, `active_states`, else), unsurprising since one
is pseudocode for the other. The third site is load-bearing because it is not pseudocode: Section
17.3's Daemon Conformance row, "Issue state refresh by ID returns minimal normalized issues," is a
checklist row, the thing an implementer builds toward — it does not describe an oversight, it
describes a target, and an adapter returning the smallest issue satisfying that row is conformant.

Decisions 0140 and 0148 each added one of these per-issue attributes, each extended Section 11.2's
Linear clause to say the refresh can observe its loss, and neither touched Part B. The same omission
made twice by two different decisions means the gap is not a property of either attribute; nothing
tells a dispatch gate it owes a continuation counterpart, and a fifth eligibility condition added
the same way would extend Section 11.2 a third time and leave Part B untouched again.

## Nothing ties a run to the repository it was dispatched to

Section 8.7 states what a dispatch grants — "A dispatch grants an agent commit and pull-request
authority in the repository it routes to" — and Section 6.2 makes the mapping that decided that
routing a live artifact: the software "MUST detect changes to the two configuration artifacts it
holds locally," and the operator policy config is one of them. So the mapping a run was dispatched
under and the mapping in force during that run's reconciliation are not guaranteed to be the same
mapping, and Section 16.4's running-entry literal — eighteen members, `repo_of(issue)` called twice
in `dispatch_issue` and stored nowhere — has nothing to compare against.

Recomputing `repo_of(issue)` at reconciliation does not repair this: both sides of the comparison an
implementation would have to invent evaluate the same function against the same, already-reloaded
mapping, so they always agree with each other. There is no second value to compare against because
the run's original routing was never stored, and the recomputation is blind to a mapping edit by
construction. Left unrepaired, a run keeps commit and pull-request authority in a repository the
mapping no longer selects, with nothing able to observe that it has happened.

## Standing versus dispatch-time, and why each condition keeps one home

Section 8.2's eligibility bullets divide along a line the document has never drawn explicitly.
`required_labels`, `assignee`, and, after this decision, routing are conditions over the issue
*record* — changeable independently of anything the orchestrator does, by a third party editing a
label or an operator editing a mapping — and re-evaluating them on every issue-state refresh is both
possible and the property Section 5.3.1's "or continue" already asks for. These are standing
conditions: true for as long as the run is in flight, checked again each time the refresh has fresh
data to check them against.

The other four of Section 8.2's bullets cannot be made standing without breaking the run they would
be checked against. "It is not already in `running`," "It is not already in `claimed`," and both
concurrency-slot tests are true exactly once, at the moment before dispatch, and false by
construction for any run already in flight, since such a run is by definition already in `running`
and already in `claimed`. An implementation that re-ran `should_dispatch` wholesale at
reconciliation would stop every run it checked — not a stricter reading of the rule but a different
rule. The `Todo`-state blocker rule could in principle be made standing but is deliberately kept
dispatch-time-only: making it standing would put the issue's dependency graph in every
reconciliation refresh, on every tick, for every running issue, for no correcting benefit, since a
run already under way has already cleared that gate once.

Routing is standing too, but it is not phrased as a condition over the issue: Section 8.2 tests
properties of the record, while routing tests where the run's authority lives, and phrasing that
over the issue during reconciliation would be circular, since routing is the computation that
decides which repository "the issue's repository" means. Section 8.7, which already states routing
over the run rather than the issue, is where the continuation clause belongs, citing Section 6.2 for
the reload that can move the answer mid-run.

Each rule therefore keeps exactly one home — Section 5.3.1 for the two record filters, Section 8.7
for routing — and Part B does not restate any of them; it *evaluates* them, the relationship it
already has with `active_states` and `terminal_states`, which Section 5.3.1 also defines and Part B
only tests. Standing is written as plain prose, "a standing condition," not a backticked defined
term the way `Reconstructable` is; the vocabulary a conformance suite needs is the predicate name,
`standing_conditions_hold`, which is what a reader checks a build against.

## The disposition: stop the worker, release the claim, arm no retry, leave the workspace

Two of these four are not choices this decision makes; they follow from decisions already in the
log. Decision 0145 makes claim release a partition rather than a rule per site — "every site that
ends a dispatched run either releases the claim or hands it to a retry entry, and there is no third"
— and Section 8.5 states that partition's obligation on whoever adds a site to it: "A site added
later MUST state which side of that partition it is on." A standing-condition loss is such a site,
so this decision's job is to say which side out loud: the claim is released, following
`terminate_running_issue`'s existing shape; no retry is armed, matching Part B's two existing
branches, decision 0138's repair of the function that would otherwise self-cancel one, and decision
0144's settlement of what a claim without a run costs.

Cleanup is the genuinely open question. Part B's existing split — a terminal state cleans the
workspace, a non-active-but-not-terminal state does not — has no stated rationale anywhere, and this
decision supplies one rather than inheriting the terminal branch's answer by proximity: a terminal
issue's work is finished and deleting its workspace discards nothing wanted, while a standing-
condition loss is not finished and is reversible — a label re-added, a mapping edit corrected.
Cleanup on that loss would be deleting live work in response to an event that, in the routing case,
may be an operator's own typo, which is worse than leaving the workspace in place. The cost is named
rather than absorbed: Section 9.1 keys the workspace path by `<repo_key>`, so a workspace left
behind by a routing change sits under the *old* repository's key while a subsequent, correctly
routed run for the same issue is provisioned at a different path — a permanent orphan unless
something else sweeps it.

## The state: the running entry gains a `repository`, and it costs no new field

The repair for the third gap is to record the repository at dispatch rather than keep recomputing
it. `dispatch_issue` already computes `repo_of(issue)` before the entry is written; the entry gains
a `repository` member holding that value, described the way `run_id` already is in Section 4.1.8's
`running` bullet — a member of the entry, not a new top-level state field. That distinction keeps
the addition from requiring a new `runtime_state_fields` vocabulary token or a Conformance Statement
row: `conformance/vocabulary.json`'s `runtime_state_fields` group carries nine entries, one per top-
level field Section 4.1.8 enumerates, and `running` is already one of them with class
`Reconstructable`. That class is unaffected — the workspace path already carries `repo_key`, so a
restart still rebuilds the entry, repository included, from the filesystem and the tracker. A new
member of an existing field's value is not a new field; Section 4.1.8's vocabulary is over fields,
not over what a field's value contains.

Section 14.4's remote-mode run registry needs the same addition for a different reason: it is
described today as "a `Durable`-class mapping (Section 14.3) from each in-flight run to its issue
and its node," no repository. A reattached remote run has to be checked against the standing
conditions the same as a local one, and the registry is the only left-hand side that comparison has.

## The stop is operator-visible, and it names the condition that failed

Section 14.5's two existing operator-facing outcomes are self-explaining without further annotation
— a terminal-state stop is visible because the operator sees the issue closed, and a non-active-
state stop the same way. A standing-condition-loss stop has no such mirror: the issue is still `In
Progress`, and the cause — a third party's label or assignment change, or an operator's mapping edit
— is not visible by looking at the issue the way a state change is. The stop is therefore reported
naming which condition failed, the shape a configuration error already takes (Section 6.3), rather
than left to be inferred from an issue that simply stopped making progress.

## The adapter obligation: refresh completeness beside candidate enumeration

Section 11.2 already states an obligation of this shape for the other read path —
"`fetch_candidate_issues` (Section 11.1) MUST return the complete set of matching issues. … A
silently partial result is non-conformant, because the orchestrator's priority sort and dispatch
(Section 8.2) assume the complete candidate set." The refresh path needs the same obligation over
its own axis: not every issue, but every *field* the standing conditions read, for every id the
refresh was asked about — a refresh that silently narrows its own response is the adapter-side
version of the same failure.

That obligation replaces, rather than duplicates, the Linear bullet quoted in Context: its
behavioral half is not a Linear-specific fact, it is the general adapter obligation stated once
under the adapter that needed it written down first. It moves up to Section 11.2's general part,
beside Candidate enumeration, and the Linear bullet keeps only the GraphQL query shape that
satisfies it. `fetch_issue_states_by_ids` keeps its name: the name says "states," the contract now
needs a record, and renaming would touch the three sections that name the operation — 11.1, 16.3 and
16.6 — plus Sections 17.3 and 17.4, which describe it in prose as the issue-state refresh. The reach
is stated as it is rather than inflated: the behavior corpus does not name the operation at all, so
a rename is `SPEC.md`-local and cheap to execute. It is declined on a different ground — a rename of
the adapter contract's surface, decided as a side effect of repairing a missing reconciliation
branch, is a decision of its own — and the tension is recorded rather than resolved.

Two things are left open rather than closed quietly. An issue genuinely absent from the refresh —
deleted from the tracker rather than merely changed — is not the same failure as a narrowed field
set, and the completeness MUST does not cover it: completeness is about what the refresh returns for
an id it was given, not whether the tracker still has that id to give. And decision 0140's general
match-field trigger — its reconsideration condition that "a third per-issue attribute arriving with
the same shape" is where a general "tracker-dependent match field" becomes cheaper than a fourth
copy of the `required_labels` pattern — stays unfired here. Routing is a third standing condition
but not a third copy of that pattern: its continuation predicate compares the record's current
routing outcome against the run's own recorded `repository`, not against a configured value the way
the label and assignee conditions do — a different left-hand side.

## Options considered

### Fix only what issue #121 reported

Move the Linear bullet's behavioral half up into Part B and stop there — the smallest edit, closing
the report. It loses on the class argument: routing still has no continue clause, Section 17.3 still
licenses a minimal refresh, and Section 16.4's missing `repository` is untouched, leaving routing's
half of the very defect unstatable.

### Re-run the whole dispatch predicate on every refresh

One rule, `should_dispatch`, evaluated again at reconciliation, rather than a second predicate. It
loses because `running`, `claimed`, and both slot tests are false by construction for a run already
in flight, so this stops every run it checks; it also puts the `Todo` blocker graph in every
refresh, the cost the standing/dispatch-time split exists to avoid.

### Make the `Todo` blocker rule standing too, for uniformity

Keeps Section 8.2's rules undivided rather than split by an unstated distinction. It loses on the
same cost: the dependency graph in every tick's refresh for every running issue, for no benefit,
since a run already under way has already cleared that gate once.

### Clean the workspace on a standing-condition loss, matching the terminal branch

Symmetric with Part B's terminal branch, no split to justify. It loses on reversibility: the causes
include an operator's own mapping typo, and deleting a workspace over a typo destroys live work in
response to a mistake likely to be corrected by the next reload.

### Derive the repository by recomputing `repo_of(issue)` at reconciliation

Adds no member to the running entry. It loses to Section 6.2's reload: both sides of the comparison
an implementation would build re-evaluate under the same, already-changed mapping and agree with
each other, blind to the edit it exists to catch.

### Rename `fetch_issue_states_by_ids`

A name matching its contract is easier to read cold, and the reach is small: `SPEC.md` names the
operation in Sections 11.1, 16.3 and 16.6, Sections 17.3 and 17.4 describe it in prose, and the
behavior corpus does not name it at all, so the rename is five edits in one document. It loses not
on cost but on standing: renaming the adapter contract's surface is a change to what every
implementation already builds against, and a decision whose subject is a missing reconciliation
branch is not where that gets settled in passing. The tension is recorded instead.

## What was checked

At `85cb892`, against the working tree:

- `grep -c "or continue"` returns three hits; the third is `continues` in Section 10's opening
  bullets, in a sentence about an executor disconnected from the seam. "dispatch or continue" as a
  clause occurs exactly twice, both in Section 5.3.1, and nowhere else.
- Section 8.5's partition sentence, "A site added later MUST state which side of that partition it
  is on," is verbatim as quoted, as is Section 8.7's "A dispatch grants an agent commit and pull-
  request authority in the repository it routes to."
- Section 16.4's running-entry literal has eighteen members and no `repository`; `repo_of(issue)` is
  called twice in `dispatch_issue` and its result is stored nowhere.
- `conformance/vocabulary.json`'s `runtime_state_fields` group has nine entries, one per top-level
  field Section 4.1.8 enumerates; Section 14.4 describes the remote-mode run registry as "a
  `Durable`-class mapping (Section 14.3) from each in-flight run to its issue and its node," with no
  repository named.
- Section 17.3 carries "Issue state refresh by ID returns minimal normalized issues," verbatim, and
  Section 11.2's Linear bullet carries the behavioral sentence quoted in Context, verbatim. Section
  9.1's per-issue workspace path is `<workspace.root>/<repo_key>/<sanitized_issue_identifier>` for a
  multi-repository instance, verbatim.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings. This is not
  evidence about a Conformance Statement row: an extension row citing a range such as `8.x`
  collapses to `8` and reports the section covered whether or not the subsection changed, so a green
  run answers a different question than the one that matters.

## Reconsideration triggers

- **A workspace-orphan sweep is added elsewhere in the document.** This decision accepts a re-routed
  issue's old workspace as a permanent orphan under `<repo_key>` keying, on the ground that deleting
  it is the worse failure; a general reclamation mechanism should be checked against this cleanup
  rationale rather than assumed to already cover it.
- **A tracker adapter that cannot report a partial refresh as a failure.** The completeness
  obligation assumes an adapter can distinguish "this id has no such field" from "the fetch did not
  complete"; a transport that conflates the two needs its own resolution, not Section 11.2's shape
  by analogy.
- **Genuine tracker-side deletion becoming a live failure mode**, the case the completeness MUST
  does not cover; a live occurrence needs a disposition of its own.
- **A Core consumer of the routing fields beyond routing itself** — decision 0148's own trigger —
  which would change what "the run's recorded repository" means here, since routing's continuation
  predicate is defined against exactly that value.
- **`fetch_issue_states_by_ids` gaining a second reason to change.** The naming tension is recorded
  rather than paid for alone; a decision already touching Sections 11.1, 16.3 or 16.6 should fold
  the rename in rather than this one reopening the question by itself.
