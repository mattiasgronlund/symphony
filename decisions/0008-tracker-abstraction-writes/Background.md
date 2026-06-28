# Background — 0008 Tracker abstraction and writes

## Context

Points 4, 6: Symphony owns all issue-tracker interaction — reads *and* writes — across at least Linear
and Forgejo, with the agent supplying content. This deliberately reverses the spec's current
"scheduler and tracker reader" boundary (Sections 1, 2.2, 11.5), where ticket writes were the agent's
job via `linear_graphql` (now retired, 0003).

## Options considered

### Write initiative

- **Pure relay / relay + minimal lifecycle / Symphony-driven lifecycle (chosen).** Symphony owns state
  transitions via a workflow state-machine; the agent supplies free-text content only. This gives
  consistent process enforcement at the cost of agent flexibility and a state-machine to specify.

### Where the state-machine lives

- **`WORKFLOW.md` proposes / split / policy config (chosen).** Because transitions are privileged
  tracker writes executed outside the sandbox, the in-sandbox-only rule (0005) places the
  state-machine in operator policy config. Operators own process; repos do not.

### How the agent signals progress

- **Outcome-driven only / agent requests explicit states / milestone signals mapped (chosen).** The
  agent emits semantic milestone signals (`ready-for-review`, `blocked`, `done`, ...) via the CLI; the
  policy state-machine maps each to the actual tracker transition. The agent expresses intent;
  operators control the resulting states.

## Decision and reasoning

A tracker adapter (Linear, Forgejo) supports reads and writes. Symphony drives ticket lifecycle via a
policy-defined state-machine; the agent supplies content and emits milestone signals that the
state-machine maps to transitions.

Problems to watch: this reverses a load-bearing boundary repeated in several sections, so the inversion
must be applied consistently (Sections 1, 2.2, 11.5, and the failure/security material in 14–15); and
putting the state-machine in policy removes process control from repo authors, which is intended but a
real change in who owns workflow.

## Re-evaluation: fork evidence on tracker writes (2026-06-25)

A third, tracker-focused sweep of ~22 retargeting forks (the live set the user supplied: GitLab, GitHub
Issues, GitHub Projects v2, Jira, Monday, Feishu Bitable, Todoist, local SQLite `td`, bespoke Postgres,
plus two genuine Rust ports). This extends — does not overturn — the Accepted decision. Each claim below
was read against the actual repo (the inherited fork-label table was again partly wrong: `miyataka` and
`hawkymisc` were mislabelled; both turned out to be real ports, and several "GitHub Projects v2" forks
are independent designs, not duplicates). Detail lives in the `adapter-layer-fork-evidence` memory; the
load-bearing conclusions for this decision:

### What the forks confirm

- **The two core writes are the right irreducible set.** `add_comment` + `set_state` survive in every
  fork that kept a tracker behaviour at all; the canonical contract is the floor, not a starting point to
  expand. Richer writes were universally added *outside* the core behaviour — as optional callbacks
  (`block_issue`/`unblock_issue`/`mark_for_retry`, martinthommesen; `create_pull_request_for_issue`,
  kimjj81; `update_pull_request_status_label`, abhijith), a side tool surface (PitchAI's 14-op
  `tool_operation`), a separate finalizer, or agent-driven raw-API tools. This validates the spec's
  conformance/extension discipline: keep core writes minimal, everything else is an OPTIONAL extension.

- **`set_state(target_state)` is the right *altitude*** — caller names a target *state*, adapter resolves
  the mechanism. Jira is the proof: `update_issue_state("Done")` cannot set a field, so the adapter fetches
  the issue's available transitions, name-matches `to.name`, and POSTs a transition id (wagnersza). The
  transition id never reaches neutral code. Keep `set_state` as the verb; do **not** lift `apply_transition`
  into the contract.

- **`link_pull_request` is the weakest of the three core writes.** Few forks expose it as a tracker op;
  PR/MR/review writes were repeatedly pushed to a *separate* surface (Harmony's distinct `Forge` behaviour;
  miyataka's `PullRequestMerger`; finalizers; agent tools) or folded into a workpad note. The
  tracker-vs-forge write boundary is a real seam (touches decision 0007) and `link_pull_request` may belong
  on the forge side, not the tracker.

### Gaps the decision/spec did not anticipate

- **Capability variance is the biggest miss.** Section 11.1 mandates all operations on every adapter; the
  non-Linear targets each drop or fake a *different* subset — `blocked_by` hardcoded empty (Monday,
  Bitable), `priority` dead (Bitable), per-label add/remove lost to a CSV rewrite (`td`), comments
  synthesized into a long-text field (Monday, Bitable) or natively absent on a plan tier (Todoist free).
  The honest designs *declare* capability rather than silently no-op: Todoist's `TrackerCapabilities{
  comments,reminders,activity_log}` probed at startup returning a typed `CommentsUnavailable`; jialinyi94's
  `@optional_callbacks` + valid no-op fallbacks; Go optional sub-interfaces probed by type assertion
  (miyataka, mattconzen); JhihJian's `capabilities()` map with runtime downgrade (GitHub Issues vs
  Projects). This reconfirms the standing finding "capability is DATA, not a method" — now on the tracker
  side. The contract should split read vs write capability and let a tracker advertise its supported
  writes, with unsupported writes returning a typed `unsupported` sentinel (never a silent no-op).

- **The milestone-signal → transition mapping is almost unattested.** The decision's centrepiece — the
  agent emits `ready-for-review`/`blocked`/`done` and a policy map (`tracker.milestones`) turns each into a
  transition — was found in **no** fork by that shape. The dominant pattern is run-*outcome* → state mapped
  in orchestrator code (success→handoff, failure→`Human Review`), with state *names* in config
  (`active_states`/`terminal_states`) but the transition *graph* hardcoded. The one fork with a structured
  agent-signal pipeline is JhihJian: a runner tool `symphony_stage_outcome` emits a closed `outcome`
  vocabulary mapped through per-stage `transitions` to a target stage, then written via `write_issue_stage`.
  That validates the *direction* (structured, config-defined signal→transition) but uses outcome/stage
  vocabulary, not milestone names. Open tension for the user: keep milestone signals as deliberate forward
  design (ahead of the ecosystem), or reframe toward an outcome vocabulary closer to JhihJian. Either way,
  the spec should say transitions are driven by *signals or run outcomes*, since outcome-driven is the
  attested majority.

- **`set_state` carries unspecified obligations.** Re-applying a Jira transition is illegal, so the adapter
  treats "already in target state" as success — idempotency is an adapter obligation the spec never states.
  GitLab has no `If-Match`, so issuepilot built an optimistic-lock label transition (`requireCurrent`,
  re-read verify, `claim_conflict`). GitHub label writes are eventually consistent, so abhijith added
  read-after-write `verify_state_label`. The write contract should: (a) require idempotent `set_state`
  (no-op when already in the target state = success), (b) define a `transition_unreachable`/`state_not_found`
  outcome, and (c) name a `claim_conflict` outcome for concurrent state writes.

- **The normalized Issue is flat, has no `raw`, and is silently lossy — and the spec inherited exactly
  this.** Every fork uses a flat struct and drops non-promoted fields (Jira custom fields, Bitable cells,
  Monday columns, Todoist extras). No fork keeps a `raw` blob *on Issue*; the escape hatch, when present, is
  a structured wrapper one level up (jialinyi94 `WorkItem{tracker_kind,metadata,attached_pr}`; kimjj81
  `Issue.metadata`+`kind`). The schema-rich targets (board, spreadsheet) are where the absence hurts most.
  Two concrete corollaries: `branch_name` and `blocked_by` are Linear-isms that silently no-op elsewhere
  (odyssey's blocker gating breaks for Jira/GitHub) and should be marked OPTIONAL/adapter-synthesized; and
  GitHub Projects v2 needs a *second* opaque handle (the project-item-id distinct from the issue node-id),
  which forks either modelled as a field, re-resolved per write (costly), or keyed off `repo#number`.
  Recommendation: give Issue an opaque adapter-owned `metadata` carrier (or a WorkItem wrapper) and mark the
  Linear-specific fields optional.

- **Linear naming bled into the neutral layer — including this spec.** Section 11.4's error categories are
  still Linear-named (`linear_api_request`, `linear_api_status`, `linear_graphql_errors`,
  `linear_unknown_payload`, `linear_missing_end_cursor`). The clean forks neutralized these (jialinyi94,
  issuepilot, archelab, mattconzen-Go); the lazy ones kept `Linear.Issue` as the cross-layer type even on
  GitHub/Jira/SQL paths and resolved `LINEAR_API_KEY`. The two Rust ports show the better shape: a closed
  `TrackerError` enum with structured `RateLimited{reset_at}`. Recommend renaming the core error categories
  to transport-neutral `tracker_*` and demoting the Linear-specific codes to Linear-adapter examples.

- **Auth/transport is not universal.** Local `td` (SQLite) and PitchAI (self-owned Postgres) have no API
  key, endpoint, or network and collapse the broker/credential boundary, yet the shared config still
  defaults to the Linear GraphQL endpoint and `LINEAR_API_KEY`. Pagination is likewise not universal (Monday
  and Bitable select a cursor but never follow it). Auth and pagination are better modelled as
  adapter-declared properties than baked-in assumptions; the broker boundary (Section 11.5) should
  explicitly admit a degenerate local/no-auth adapter.

### Net effect on the decision

The Accepted decision stands: a read+write tracker adapter, Symphony-driven lifecycle, agent supplies
content. The refinements are additive and mostly belong in Section 11 and Section 4.1.1 rather than in the
decision's shape: a declared write-capability surface, idempotency/claim obligations on `set_state`,
neutralized error categories, an Issue escape-hatch with Linear-isms marked optional, and an honest
acknowledgement that milestone-signal mapping is forward design while outcome-driven transitions are the
attested norm. The tracker-vs-forge write split and the no-auth/local adapter are open boundary questions
that may warrant their own decisions.

The milestone/outcome point was acted on immediately: decision 0017 generalizes the flat `tracker.milestones`
map into an explicit `{from, on, to}` transition graph (`tracker.transitions`) keyed on both agent milestone
signals and orchestrator-observed run outcomes. The remaining refinements (write-capability declaration,
error-code neutralization, Issue escape hatch) are still open.

## Re-evaluation — completion model refined by 0031 (2026-06-28); stays Accepted

This decision **remains Accepted**. Decision 0031 (daemon-side autonomous task management) refines the
**completion** half of this decision for the autonomous case: the single agent-asserted `done` milestone
becomes **computed** `tasks:all_closed`, and `blocked` becomes a `need-help` task. The agent still
expresses intent and operators (now the repo, decision 0029) own the resulting transitions — this
decision's load-bearing principle is intact; 0031 only makes completion observable rather than an
unverifiable flag. 0031 also uses this decision's tracker writes in a new way: a **write-through**
materialization of the task list into the issue as structured artifacts (sub-issues / checklist items),
broker-mediated so the agent stays credential-free (decision 0003) — an additional *kind* of
broker-mediated tracker write, consistent with the boundary set here, gated by a new structured-task-write
capability (decision 0018). Interactive sessions keep the plain `ship`/`land` path with no task model.
See 0031.
