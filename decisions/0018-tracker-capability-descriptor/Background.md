# Background — 0018 Tracker capability descriptor

## Context

Section 11.1 lists six tracker operations and says an implementation "MUST support" all of them. The
2026-06-25 tracker sweep (0008 `Background.md`; `adapter-layer-fork-evidence` memory) found this is the
single biggest mismatch with reality: the three reads are genuinely universal, but the writes are not.
Every non-Linear retarget drops or fakes a *different* write subset — `blocked_by` hardcoded empty
(Monday, Bitable), per-label writes lost to a CSV rewrite (`td`), comments synthesized into a long-text
field (Monday, Bitable), or no comment API at all on a plan tier (Todoist free). The mandate-everything
contract forces adapters to lie: silently no-op an unsupported write, or substitute a different write
(append a "comment" into a description field) so the call appears to succeed.

The honest forks instead *declare* capability. Todoist (kalepail) probes `TrackerCapabilities{comments,
reminders,activity_log}` once at startup and returns a typed `CommentsUnavailable` rather than a no-op;
JhihJian exposes `capabilities()` and downgrades at runtime (GitHub Issues vs Projects); Go ports use
optional sub-interfaces probed by type assertion (miyataka `Writeback`/`PullRequestMerger`/`IssueCreator`,
mattconzen `PullRequestSetter`/`SpecWriter`) plus sentinels (`ErrCreateUnsupported`). The standing
finding across both adapter sweeps is "capability is DATA, not a method".

The spec already acts on that finding for the *agent* side: decision 0015 / Section 10.9 give each agent
adapter a "static capability descriptor (data, not a runtime call)" the orchestrator reads to drive
behavior. The tracker side has no equivalent. This decision adds the mirror.

## Options considered

- **Optional callbacks with silent no-op fallback** (jialinyi94 shape: absence ⇒ a semantically-valid
  no-op). Cleanest to implement, but the sweep flagged silent no-ops as the anti-pattern — a no-oped
  `set_state` looks like a successful transition, so a workflow can wedge with no error.
- **Per-call sentinel errors only** (mattconzen `ErrCreateUnsupported`, no descriptor). Honest at call
  time, but the orchestrator only discovers a gap by attempting the write, so it cannot validate a
  configured workflow up front.
- **Static capability descriptor (data) + typed unsupported sentinel (chosen).** Mirrors the agent
  adapter (Section 10.9 / decision 0015): the orchestrator reads the descriptor before writing and at
  dispatch preflight, and an undeclared write that is invoked anyway returns
  `tracker_unsupported_operation`. Capability is knowable ahead of the call *and* enforced at the call.

## Decision and reasoning

- **Reads stay REQUIRED, writes become capability-gated.** `fetch_candidate_issues`,
  `fetch_issues_by_states`, and `fetch_issue_states_by_ids` are required of every adapter — without them
  there is no scheduling or reconciliation — and are not part of the descriptor. This is the read/write
  split the sweep recommended.
- **Each tracker adapter advertises a static capability descriptor** (data, not a runtime call) declaring
  which writes it supports: `add_comment`, `set_state`, `link_pull_request`. The descriptor MAY depend on
  resolved config and is fixed for the run (e.g. a plan tier without a comment API declares `add_comment`
  unsupported, probed once at initialization).
- **The orchestrator consults the descriptor before a write** and MUST NOT invoke an undeclared write; an
  optional unsupported write (e.g. `link_pull_request`) is skipped and logged, not failed. An undeclared
  write invoked anyway returns `tracker_unsupported_operation` (added to Section 11.4). An unsupported
  write MUST NOT be silently treated as success, no-oped, or replaced by a synthesized substitute.
- **The descriptor ties into the transition graph (0017).** A non-empty `tracker.transitions` requires
  the `set_state` capability; dispatch preflight (Section 6.3) treats configured transitions on a tracker
  that cannot `set_state` as a configuration error.

Reasoning: this keeps the contract honest (no faked successes), makes capability gaps preflightable
rather than discovered mid-run, and is consistent with the agent capability descriptor the spec already
defines — capability as static DATA, with a typed sentinel as the call-time backstop.

Boundary: this decision is about *operation* capability (which writes work). Two adjacent concerns are
deliberately out of scope. Normalized-Issue *field* population (marking `branch_name`/`blocked_by`
OPTIONAL, an Issue escape hatch for dropped provider fields) is the separate normalized-model fix.
*Representation* of a state (GitLab scoped label, Projects v2 option-id, Jira transition id) stays
adapter-internal — decision 0017 already defines the transition graph over neutral state names and leaves
representation to the adapter (Section 11.2).

Problems to watch: the descriptor must stay a small enumeration of the three writes, not grow into a
per-field/per-state capability matrix (that pull is real — JhihJian's runtime stage-contract downgrade is
finer-grained); and the preflight tie to `tracker.transitions` must be kept in sync if 0017's graph
config changes.
