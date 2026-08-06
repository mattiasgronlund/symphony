# Decision Log

This log records decisions that shape `SPEC.md` (and, later, the implementation). Its purpose is to
preserve the *reasoning* behind each decision so it can be re-evaluated later without re-deriving the
original context.

Each decision is one chapter below: a short heading, a **State**, a link to its folder, and a short
focused prose description. The folder holds the supporting detail:

- `Background.md` — why the decision was made (the reasoning, alternatives, trade-offs).
- `Plan.md` — how the decision is to be implemented in `SPEC.md`.
- `Sessions.md` — the Claude session name(s) and id(s) that worked on the decision.

**States:** `Proposed` (under consideration) · `Accepted` (decided; to be / being applied) ·
`Rejected` (decided against; kept for the record) · `Superseded` (replaced by a later decision; kept
for the record). A `Superseded` chapter names the decision that replaced it; unlike `Rejected`, a
superseded decision may have been sound and parts of it may survive in its successor (decision 0033).

New decisions get the next zero-padded number and a folder `decisions/NNNN-short-slug/`. Copy
`decisions/_template/` to start. See `CLAUDE.md` for the working conventions.

---

## 0001 — Adopt a decision log

**State:** Accepted
**Folder:** [decisions/0001-adopt-decision-log/](decisions/0001-adopt-decision-log/)

Keep a structured decision log so changes to `SPEC.md` are traceable to their reasoning. Each
decision is a chapter here plus a folder containing `Background.md`, `Plan.md`, and `Sessions.md`.
This lets us revisit a decision later with its original motivation intact, rather than guessing at
why the spec reads the way it does.

## 0002 — Stable addressing of SPEC.md from decision plans

**State:** Accepted
**Folder:** [decisions/0002-stable-spec-addressing/](decisions/0002-stable-spec-addressing/)

`Plan.md` files address `SPEC.md` by stable identity — code-token identifiers first, then section
titles, with section numbers only as a secondary hint — and phrase each step as a declarative,
idempotent post-condition rather than a positional diff. This keeps plans re-executable in any order
and after intervening edits, where line/column or paragraph addressing would degrade. Anchor renames
and removals are recorded append-only in the `Anchor changes` section of the decision that causes
them, rather than in a standalone registry that would duplicate `SPEC.md` and rot.

## 0003 — Responsibility inversion and the credential broker boundary

**State:** Accepted
**Folder:** [decisions/0003-responsibility-inversion-credential-broker/](decisions/0003-responsibility-inversion-credential-broker/)

Symphony inverts from a scheduler/tracker-reader where the agent holds credentials into a privileged
broker: it performs all outward side effects (VCS remote operations, pull-request creation, all
tracker interaction) while a sandboxed, credential-less agent supplies only operation content through
a semantic `symphony` CLI over a per-run socket. The boundary enforces scope as well as confidentiality
(push only to the work branch, write only to the assigned issue), brokered results are structured with
a run-fatal `scope_denied`, and secrets resolve through a provider interface and are scrubbed from the
environment before the sandbox forks. This is the keystone for decisions 0004–0009.

## 0004 — Sandbox isolation and the per-run broker socket

**State:** Accepted
**Folder:** [decisions/0004-sandbox-isolation-broker-socket/](decisions/0004-sandbox-isolation-broker-socket/)

Each agent run MUST be wrappable in a configurable sandbox, with a strict-by-default profile assumed
(reference baseline: `jai` `Strict`, https://jai.scs.stanford.edu, on Linux; an equivalent mechanism
elsewhere). A per-run socket is the only privileged channel into the sandbox and binds each connection
to one (repo, issue, branch) for scope enforcement; the working tree is bind-mounted from the host so
Symphony runs credentialed git host-side against it. Egress is configurable with a strict default plus
an allowlist. This drops the SSH Worker Extension (Appendix A) for now.

## 0005 — Config and trust split

**State:** Superseded (by 0029)
**Folder:** [decisions/0005-config-trust-split/](decisions/0005-config-trust-split/)

Configuration splits on the sandbox boundary: `WORKFLOW.md` (repo-owned, untrusted) holds only settings
used *inside* the sandbox — the prompt and in-sandbox build/test hooks — while a new operator-owned
policy config holds everything Symphony uses outside the sandbox (credentials, scope rules, sandbox
profile, repo map, the workflow state-machine, agent selection, privileged setup hooks). Both surfaces
hot-reload with last-known-good-on-invalid. This retires the "hooks are fully trusted configuration"
assumption. **Superseded by 0029** (`Superseded` state per 0033): 0029 reframes the config/trust axis
from operator-vs-sandbox to base-sourced-vs-worktree and relocates the WoW (state-machine, host-side
hooks) into repo-owned base-sourced `repo.policy.toml`. Carried forward into 0029: the
`WORKFLOW.md`/in-sandbox model, credential isolation, and hot-reload last-known-good.

## 0006 — Agent adapters (Codex, Claude Code)

**State:** Accepted
**Folder:** [decisions/0006-agent-adapters/](decisions/0006-agent-adapters/)

Section 10 generalizes into a neutral agent runner contract plus per-agent adapters (Codex, Claude
Code), each deferring to its own protocol; the existing Codex detail becomes the Codex adapter. Agent
selection is operator policy: a per-repo default agent and native (pass-through) effort, overridable
per issue via an explicit policy table mapping tracker labels to (agent, effort) pairs. Session identity
and token accounting are generalized off Codex-specific shapes.

## 0007 — VCS abstraction and git automation

**State:** Accepted
**Folder:** [decisions/0007-vcs-abstraction-git-automation/](decisions/0007-vcs-abstraction-git-automation/)

A VCS adapter (GitHub, Forgejo) backs the broker's git and PR verbs. The agent does local git including
`git commit`; Symphony performs clone/fetch/branch/back-merge/push/PR and maintains one PR per issue
(created then updated). The work branch is Symphony-derived and deterministic (`symphony/<identifier>`).
Back-merge is attempted at run start but postponed if it would conflict, with conflict resolution
required only on push-reject via a Symphony-stages / agent-resolves handoff. Commit author and push/PR
actor are configurable per repo.

## 0008 — Tracker abstraction and writes

**State:** Accepted
**Folder:** [decisions/0008-tracker-abstraction-writes/](decisions/0008-tracker-abstraction-writes/)
**Summary:** [Summary.md](decisions/0008-tracker-abstraction-writes/Summary.md) — the 22-fork deep dive and the decisions it produced (0017–0024)

A tracker adapter (Linear, Forgejo) supports reads *and* writes, reversing the spec's "tracker reader
only" boundary. Symphony drives ticket lifecycle via a policy-owned workflow state-machine; the agent
supplies free-text content and emits semantic milestone signals (`ready-for-review`, `blocked`, `done`)
that the state-machine maps to the actual tracker transitions.

## 0009 — Multi-repo and shared polling

**State:** Accepted
**Folder:** [decisions/0009-multi-repo-shared-polling/](decisions/0009-multi-repo-shared-polling/)

One Symphony instance manages multiple repositories. Issues are routed to exactly one repo by explicit,
tracker-implementation-specific mappings in policy config (Linear project/team/label/assignee → repo;
Forgejo repo/tags/state → repo), and a single tracker's polling is shared across its repos to minimize
background work. Workspace, concurrency, and the object store/worktrees become keyed by (repo, issue).

## 0010 — State recovery model and class taxonomy

**State:** Accepted
**Folder:** [decisions/0010-state-recovery-classification/](decisions/0010-state-recovery-classification/)

The spec's current recovery stance ("without a durable orchestrator DB", "intentionally in-memory") is
an implicit two-class model — every field is either reconstructable from an external source of truth or
reset-and-lossy at startup — with zero durable state. Planned spend-control extensions introduce state
that is neither safely reconstructable nor safely lossy, hinging on the distinction between *account
totals* (external, account-wide, intermittently reachable) and *Symphony-attributed totals* (internal,
must be correct). This decision makes the taxonomy explicit and adds a per-field classification
obligation over four classes: `Reconstructable` (R, never primary-persisted), `Ephemeral` (E, documents
its reset consequence), `Cached external signal` (C, last-known-good plus an explicit `UNKNOWN` sentinel
that is never `0`, with a configurable fail-open/closed policy), and `Durable` (D, idempotent
re-seed-before-enforcement accounting). It admits D as the narrow, OPTIONAL exception to the
no-durable-DB stance, reclassifies `codex_rate_limits` to C, and is the shared prerequisite for
decisions 0011–0013.

## 0011 — Per-execution durable ledger

**State:** Accepted
**Folder:** [decisions/0011-execution-ledger/](decisions/0011-execution-ledger/)

An append-only, per-execution usage ledger keyed by `(issue_identifier, session_id)`, recording absolute
token snapshots and summarized by a high-water mark per session (then summed) so repeated appends are
idempotent. It is both the per-execution history surface (audit, debugging expensive/looping runs, cost
attribution) and the RECOMMENDED realization of class-D durability from 0010 — while D's contract stays
abstract so a non-ledger durable counter still conforms. Observability-first (no cost/`model` field in
the core schema), with non-fatal I/O. OPTIONAL extension; realizes the existing Section 18.2 TODO on
persisting session metadata across restarts.

## 0012 — Token budget guards

**State:** Accepted
**Folder:** [decisions/0012-token-budget-guards/](decisions/0012-token-budget-guards/)

Token-unit budget enforcement as an OPTIONAL extension and an application of class D (0010). Per-session
and per-issue caps abort and requeue the single issue; a global cap pauses new dispatch while in-flight
runs continue (a dispatch gate composing with Section 8.3). Budget exhaustion is its own failure
category (`token_budget_exceeded`) routed to a park/blocked state and kept out of the Section 8.4
retry/backoff path. Counters are durable and re-seeded idempotently before enforcement (closing the
fresh-budget-on-restart gap), with an OPTIONAL soft warning threshold and an OPTIONAL constrained
one-shot recovery. A cost/currency pricing overlay is explicitly deferred.

## 0013 — Provider quota backpressure

**State:** Accepted
**Folder:** [decisions/0013-quota-backpressure/](decisions/0013-quota-backpressure/)

Activates the currently-inert `codex_rate_limits` tracking into a normalized provider-quota snapshot
(comparable `used_percent`, opaque buckets, staleness, optional error) governed by class C (0010), fed
by either an in-band rate-limit stream or an OPTIONAL out-of-band poller. A dispatch-only gate pauses new
work when any bucket crosses a threshold, leaving running agents untouched, with implicit resume and a
configurable fail-open/closed policy on `UNKNOWN` (unsupported defaults open; transient block MAY close).
Account-wide headroom is kept separate from Symphony-attributed spend (0012). OPTIONAL extension.

## 0014 — Turn and step terminology

**State:** Accepted
**Folder:** [decisions/0014-turn-step-terminology/](decisions/0014-turn-step-terminology/)

Disambiguates two things colloquially called a "turn". Keeps `turn` meaning the orchestration-
initiated prompt-to-completion cycle on the live agent thread (unchanged, aligned with the Codex
app-server protocol's turn unit and `turn_id`), and introduces `step` for the coding agent's
internal, autonomous tool-call iteration within a turn — agent-internal, neither initiated nor
counted by Symphony, so `max_turns` bounds turns, not steps. (An adapter MAY still cap steps with a
native limit such as `--max-turns`, distinct from `agent.max_turns`.) The outer tier remains the
`run` (Section 7.2): a run contains turns, a turn contains steps. Rejected the inverse (turn = inner loop,
rename the cycle) as a conflict with the protocol the spec defers to.

## 0015 — Neutral agent runner contract

**State:** Accepted
**Folder:** [decisions/0015-neutral-agent-runner-contract/](decisions/0015-neutral-agent-runner-contract/)

Elaborates decision 0006's thin agent contract into a turn-centric, transport-neutral one, informed by a
study of ~24 backend-swap forks. Replaces the implicit "keep the subprocess alive across continuation
turns" assumption with an explicit, opaque, adapter-owned `continuation_ref` (a persistent app-server
becomes one adapter whose ref is a warm handle; a per-invocation CLI another whose ref is a resume token
or declares non-resumable). Adds a REQUIRED `cancel` with RECOMMENDED interrupt-then-drain to a resumable
state (making timeouts and early stops clean boundaries, per 0014's Identione refinement); REQUIRES neutral
events and a neutral token-usage record `{input_tokens, output_tokens, total_tokens}` with opaque extras;
advertises adapter capability as a static descriptor (resume mode, native step cap, accepted effort) rather
than a method; and rules that an adapter encapsulates one (agent, transport) pairing and MUST NOT
impersonate another agent's protocol. Selection (0006) and the broker (0003/0004) are unchanged; the
`codex_*` observability-field rename is delegated to a follow-on sweep (0016).

## 0016 — Neutralize agent observability vocabulary

**State:** Accepted
**Folder:** [decisions/0016-neutralize-agent-vocabulary/](decisions/0016-neutralize-agent-vocabulary/)

The mechanical-but-cross-cutting sweep deferred by 0006 and enabled by 0015: renames the persisted and
emitted `codex_*` observability vocabulary to neutral names every adapter normalizes into — bare inside the agent-session struct (Section 4.1.6),
scope-qualified in the runtime map (Section 4.1.8). `codex_app_server_pid` -> `pid`, `last_codex_*` ->
`last_*`, `codex_{input,output,total}_tokens`
-> `{input,output,total}_tokens`, `codex_totals` -> `agent_totals`, `codex_rate_limits` ->
`provider_rate_limits`, `codex_update` / `Codex Update Event` -> `agent_update` / `Agent Update Event`,
`codex_session_logs` -> `agent_session_logs`, plus neutralizing Codex-worded hardening prose (Section
15.5). Genuinely Codex-adapter-specific anchors (the `codex` config block, the Sections 10.1-10.8 worked
example, `codex.command`) are intentionally left unchanged. The generic-timeouts-under-`codex.*` config
wart is left for a separate decision.

## 0017 — Workflow transition graph

**State:** Accepted
**Folder:** [decisions/0017-workflow-transition-graph/](decisions/0017-workflow-transition-graph/)

Refines decision 0008 after the 22-fork tracker sweep found its flat milestone map (`tracker.milestones`)
unattested and Section 11.6 over-claiming a state-machine it never specified. The workflow state-machine
becomes an explicit directed graph over tracker workflow-state names: transitions `{from, on, to}` keyed on
one closed trigger vocabulary that unifies agent-emitted milestone signals (`ready-for-review`, `blocked`,
`done`) and orchestrator-observed run outcomes (`dispatched`, `pull_request_opened`, `run_succeeded`,
`run_failed`, `retries_exhausted`, each tied to Section 7.2/7.3). The graph lives in `tracker.transitions`,
replacing `tracker.milestones`; an unmatched trigger transitions nothing and the graph MUST be
deterministic. Nodes reuse existing state names rather than introducing a `stage` noun; provider
representation of states and tracker write-capability are deferred to a later capability decision.

## 0018 — Tracker capability descriptor

**State:** Accepted
**Folder:** [decisions/0018-tracker-capability-descriptor/](decisions/0018-tracker-capability-descriptor/)

Acts on the 22-fork sweep's biggest finding: Section 11.1's "every adapter MUST support all six operations"
is false for writes. The three reads stay REQUIRED; the writes (`add_comment`, `set_state`,
`link_pull_request`) become capability-gated. Each tracker adapter advertises a static capability descriptor
(data, not a runtime call) mirroring the agent adapter (Section 10.9 / decision 0015); the orchestrator
reads it before a write and at preflight. An undeclared write yields `tracker_unsupported_operation` and an
unsupported write MUST NOT be silently no-oped or replaced by a synthesized substitute. A non-empty
`tracker.transitions` (decision 0017) requires the `set_state` capability. Normalized-Issue field
optionality and provider state representation are out of scope.

## 0019 — Neutralize tracker error vocabulary

**State:** Accepted
**Folder:** [decisions/0019-neutralize-tracker-error-vocabulary/](decisions/0019-neutralize-tracker-error-vocabulary/)

The tracker-side mirror of decision 0016 (agent `codex_*` neutralization): renames Section 11.4's
Linear-named error categories to transport-neutral `tracker_*` names — `linear_api_request` ->
`tracker_api_request`, `linear_api_status` -> `tracker_api_status`, `linear_graphql_errors` ->
`tracker_backend_errors`, `linear_unknown_payload` -> `tracker_payload_invalid`,
`linear_missing_end_cursor` -> `tracker_pagination_error` — and records the Linear GraphQL adapter's mapping
onto them as a `Note:`. The Section 17.3 error-mapping test row is neutralized to match. The retired
`linear_graphql` tool name and the `~/.linear_api_key` example path are genuinely Linear-specific and
unchanged.

## 0020 — Normalized issue metadata and optional fields

**State:** Accepted
**Folder:** [decisions/0020-normalized-issue-metadata/](decisions/0020-normalized-issue-metadata/)

Acts on the sweep's normalized-model findings: the flat `Issue` (Section 4.1.1) silently drops provider
fields the flat schema does not capture, and `branch_name`/`blocked_by` are Linear-isms that no-op on other
trackers. Adds an opaque, adapter-owned `metadata` map to `Issue` as the documented escape hatch (an adapter
MAY round-trip a provider write handle through it, e.g. a GitHub Projects v2 item id, instead of re-resolving
per write), and marks `branch_name` and `blocked_by` OPTIONAL/tracker-dependent — an adapter without a
dependency model leaves `blocked_by` empty and blocker-gated dispatch (Section 8.2) then does not gate.
Section 11.3 records the Linear-specific derivation and an `Implementation-defined` `metadata`. Stops short
of a WorkItem wrapper to stay surgical.

## 0021 — set_state write semantics

**State:** Accepted
**Folder:** [decisions/0021-set-state-write-semantics/](decisions/0021-set-state-write-semantics/)

Specifies the obligations `set_state` carries beyond a plain write, from the sweep's Jira/GitLab/GitHub
evidence. New Section 11.8 requires `set_state` to be idempotent (already-in-target is a successful no-op;
the adapter MUST NOT re-apply a transition some trackers reject), to fail with `tracker_state_unreachable`
when the target is unreachable and `tracker_state_conflict` when the state changed underneath the write, to
SHOULD-verify results applied through eventually-consistent writes, and to treat a required transition input
it cannot express as `Implementation-defined`. A `set_state` failure is logged and does not by itself fail
the run; a conflict triggers re-reconciliation. Adds the two error categories to Section 11.4. Keeps the
`set_state(target)` altitude (no `apply_transition` in the contract).

## 0022 — Forge adapter surface

**State:** Accepted
**Folder:** [decisions/0022-forge-adapter-surface/](decisions/0022-forge-adapter-surface/)

Splits decision 0007's single VCS adapter into two contracts on the same code host: a VCS adapter (git
remote: clone/fetch/branch/back-merge/push, broker git verbs `push`/`back-merge`) and a first-class Forge
adapter (new Section 9.10) owning pull-request/merge-request lifecycle and OPTIONAL review-thread writes
(post/reply/resolve), with broker forge verbs `pr`/`request-merge`/review writes. The Forge adapter reuses
`vcs.kind`/`vcs.api_key` and advertises a static capability descriptor mirroring the agent (Section 10.9)
and tracker (Section 11.7) adapters — PR create/update REQUIRED, review-thread writes OPTIONAL. Reconciles
`link_pull_request` (decision 0008): forge-native for a same-platform tracker (which MAY declare the write
unsupported), a tracker write for a separate-system tracker (Linear). Refines decisions 0007 and 0008.

## 0023 — Adapter-declared auth mode

**State:** Accepted
**Folder:** [decisions/0023-adapter-declared-auth-mode/](decisions/0023-adapter-declared-auth-mode/)

Removes the spec's hardwired assumption that every tracker is a remote, credentialed API (the sweep's local
`td`/SQLite and self-owned Postgres backends did not fit). Each tracker adapter declares an auth mode in its
capability descriptor (Section 11.7): `secret` (a credential resolved through the secret provider) or `none`
(no credential; a host-side store). `tracker.api_key`/`tracker.endpoint` and the dispatch-preflight key check
(Section 6.3) apply only to `secret`-mode; the secret provider is consulted only then. The broker still
mediates tracker writes for scope and isolation when the adapter has no credential, and a local adapter's
store MUST be host-side (outside the bind-mounted workspace) so the agent cannot bypass it. `linear`/`forgejo`
are `secret`-mode; a `none`-mode adapter is an OPTIONAL extension. Mirrors the adapter-declared-DATA approach
of decision 0018; relates to 0003/0005.

## 0024 — Candidate enumeration completeness

**State:** Accepted
**Folder:** [decisions/0024-candidate-enumeration-completeness/](decisions/0024-candidate-enumeration-completeness/)

Fixes a read-side correctness gap the sweep flagged (Monday/Bitable forks select a cursor but never follow
it, capping at one page). Pagination was specified only in the Linear-specific block, and the orchestrator's
client-side priority sort and dispatch (Section 8.2) assume the complete candidate set. States a neutral
requirement in Sections 11.1/11.2: `fetch_candidate_issues` MUST return the complete matching set, the
adapter paginating internally (mechanism/page size adapter-specific); a silently partial result is
non-conformant; a broken enumeration surfaces `tracker_pagination_error`; a hard-capped backend documents the
cap (`Implementation-defined`) and MUST NOT silently drop fetchable issues. The Linear page-size/cursor lines
stay as Linear specifics. Reframes pagination as a correctness requirement, not an optional capability; a
bounded server-side-ordered mode is noted as a deferred scale option. Continues the neutralization theme of
0019/0020/0023.

## 0025 — Session resource governance and the host-side launch seam

**State:** Proposed
**Folder:** [decisions/0025-session-resource-governance/](decisions/0025-session-resource-governance/)

Captures the analysis behind an operator request for per-session CPU *fairness* (work-conserving weights, not
quotas) under concurrent sessions whose build/test gate runs are CPU-bound. Finding 1: the agent's CPU-bound
work runs inside the sandbox, so the existing `Implementation-defined` sandbox-wrap (Section 9.6) is already
the per-session attach point for a cgroup / CPU weight — no new mechanism is needed agent-side. Finding 2: the
spec models host-side work — repository provisioning and git verbs (Sections 9.7–9.9), worktree provisioning
(Section 16.6), and policy-config hooks (Sections 9.4/15.4) — as behaviors, not launches, so it has no
wrapper/governance seam; those subprocesses are orchestrator children and inherit the orchestrator's cgroup,
not the session's, leaving the brief's "whole-subtree" goal unreachable for host-side ops (dominant host-side
CPU cost = concurrent `after_create`/`before_run` build hooks, which is real but secondary to the in-sandbox
gate). Records three options without choosing: A leave the spec silent; B an OPTIONAL note that the sandbox
launch is the per-session attach point and host-side ops are governed at the service/orchestrator level; C an
OPTIONAL host-side execution-wrapper ("session resource domain") that brings host-side per-session work into
the session's cgroup. No option is selected; the distinguishing evidence is whether host-side per-session CPU
is material once the agent subtree is governed. The brief's non-secret env-passthrough half (`ENTRY_CHECK_*`,
touching the Section 15.3 secret-scrubbing invariant) is out of scope and tracked as a separate future
decision. Decision 0034 (Accepted) later acted on one host-side op named in finding 2: it specified the
failure model (`Repository Provisioning Failures`, Section 14.1) and a reference algorithm
(`ensure_object_store`, Section 16.5) for repository provisioning — the error-handling half, distinct from
and not closing the per-session CPU-governance question this decision leaves open. Decision 0035
(Accepted) later realized Option C's "session resource domain" as a placed component — the execution
process behind an always-present orchestrator↔executor seam — closing the host-side *launch-seam* gap
along the placement axis while leaving this decision's per-session CPU-*governance* question open (its
mechanism, when chosen, should attach to the 0035 executor rather than be invented separately). Proposed; finding
recorded, no `SPEC.md` change.

## 0026 — VCS-operation lifecycle hooks aligned with `vcsx`

**State:** Superseded (by 0030)
**Folder:** [decisions/0026-vcs-lifecycle-hooks/](decisions/0026-vcs-lifecycle-hooks/)

Aligns Symphony's hook vocabulary with the external `vcsx` VCS-workflow engine so one repository can
express one VCS policy and have it honored identically whether it runs `vcsx` interactively or under
Symphony's broker. A companion `vcsx` proposal merges that tool's direct-sequence, role-named hooks
(`validate`, `scan-content`, `resolve-base`, `pr-body-transform`, `post-push`, `post-gate`) into one
hook per lifecycle position and renames them to positional `before_*`/`after_*` names; this decision
adds the matching set to Symphony. Introduces an OPTIONAL **VCS-operation** lifecycle hook axis —
`before_commit`, `before_push`, `after_push`, `before_pull_request` — fired around the broker's
commit/push (Sections 9.8–9.9) and forge `pr` (Section 9.10) verbs, sitting beside (not replacing) the
existing **workspace** lifecycle hooks (`after_create`/`before_run`/`after_run`/`before_remove`,
Section 9.4). Classifies them onto Symphony's existing two-trust-level model (Section 15.4):
`before_commit` is in-sandbox/untrusted (warms a worktree artifact, no secrets); `before_push`/
`after_push`/`before_pull_request` are host-side/operator-trusted, with `after_push` permitted a
declared secret (Section 15.3) and outward writes under operator credentials. `before_*` may block with
a stable reason code (Section 10.8); `after_*` is best-effort and never blocks. The bind-mounted
working tree (Section 9.6) is the only channel between an in-sandbox `before_commit` and a host-side
`after_push`, so a warmed artifact crosses the trust boundary as worktree state — the seam that lets
the same policy split across the sandbox boundary or fold into one process. Symphony ships no
cache/token/signing policy; whether such an artifact exists or is trusted lives entirely in the repo's
wired hook implementations. Base resolution stays `vcs.base_branch` config, not a hook. Marked OPTIONAL
so Core Conformance is unaffected. **Superseded by 0030** (`Superseded` state per 0033): the separate
`before_*`/`after_*` hook *axis* is folded into the one `(trigger) → (action)` machine, but the four
lifecycle positions survive as triggers (`after_push` ≡ `push:ok`) and the two-trust-level
classification is preserved and still referenced by 0029, so 0026's durable contribution lives on.
Reasoning recorded; no `SPEC.md` change was ever made.

## 0027 — Minimal enabler and the three-layer architecture

**State:** Accepted
**Folder:** [decisions/0027-minimal-enabler-three-layers/](decisions/0027-minimal-enabler-three-layers/)

The headline re-framing for consuming an external VCS-workflow engine (`vcsx`): Symphony *enables*
Ways of Working and *enforces* none beyond the **secret-isolation invariant** (the agent never needs
VCS/Forge credentials, the keystone of 0003). The monolithic service is factored into three layers —
a **broker core** (≈ 0003/0004: secret isolation, scope, the per-run socket, credentialed-op
mediation; the only Core-Conformance guarantee here and independently conformant), an optional
**`vcsx` engine**, and an **autonomous daemon** layered on the broker core. Three deployment
topologies fall out with sharp conformance boundaries: daemon, interactive-agent (broker core +
`ship`/`land`), and engine-direct. Parent of decisions 0028–0032; does not change 0003/0004.
Accepted and applied to `SPEC.md` (Sections 1, 2, 3.4, 18) in step with decisions 0028–0032 against
the `VCSX-CONTRACT.md` stub (0039): the enabler-not-enforcer principle, the three layers, and the
three deployment topologies.

## 0028 — `vcsx` as an independent deliverable; one shared policy executor

**State:** Accepted
**Folder:** [decisions/0028-vcsx-deliverable-shared-executor/](decisions/0028-vcsx-deliverable-shared-executor/)

`vcsx` is an independent, reusable engine consumed as a pinned mise tool (like `archdoc`) and usable
without Symphony; `SPEC.md` defers to its **contract** (not its implementation), mirroring the
existing Codex-app-server-protocol deferral so the spec stays language-agnostic. The policy-graph
**executor lives in `vcsx`**: interactive `ship`/`land` and the daemon are **two front-ends over one
executor reading one `repo.policy.toml`**, differing only in initiator and `escalate` binding — which
makes the three topologies provably consistent rather than coincidentally similar. `vcsx` is
therefore not tiny (it owns the executor); Symphony's *marginal* code over it stays tiny. Refines
0007 and 0022 (their VCS/forge adapter roles fold into the engine contract and its plugin layer).
Depends on 0027 (Accepted). Accepted and applied to `SPEC.md` (Sections 3.4, 5, 9.7–9.10, 18) against
the `VCSX-CONTRACT.md` stub (0039), so contract names stay identical across both documents: the engine
deferral boundary, the one-executor-two-front-ends invariant, and the recast of the broker verbs
through the engine contract. Realization and sequencing — a separate codebase from the start,
`engine-direct` built first — are decided in 0042.

## 0029 — Repo-owned WoW config, trust sourcing, and the secret/integrity taxonomy

**State:** Accepted
**Folder:** [decisions/0029-repo-owned-wow-config-trust-sourcing/](decisions/0029-repo-owned-wow-config-trust-sourcing/)

The repository owns its Way of Working in `repo.policy.toml` (engine selection, hooks, the operation
flow, transitions; `vcsx.toml` merged in), so configuring Symphony needs no WoW knowledge. The
agent-tamper problem is solved by **sourcing by trust**, not an immutability flag: Symphony reads
**host-side-executed** WoW from the protected **base revision** (the agent cannot push to base;
review-gated) and **in-sandbox** parts (the `before:commit` gate/scan) from the **worktree** (harmless
and correctly runs a PR's own gate change) — so WoW-config trust equals base-branch trust. The
operator config shrinks to outward credentials, sandbox profile, and a repo→policy pointer; the scope
invariant stays a broker-core built-in. The secret model splits into **outward credentials**
(broker-mediated) vs **repo-internal integrity values** (the gate-cache HMAC — repo-owned, not a
broker secret). Supersedes 0005 (now `Superseded by 0029` per 0033 — it reframes 0005's config/trust
axis; 0005's `WORKFLOW.md`/in-sandbox model and credential isolation are carried forward); refines
0023/§15.3 and 0026. Depends on 0027 (Accepted). Accepted and applied to `SPEC.md` (Sections 5, 5.6,
6.1–6.4, 9.6–9.8, 11.6, 15.3, 15.4) with decisions 0028–0031 against the `VCSX-CONTRACT.md` stub
(0039): `repo.policy.toml` as the three-artifact WoW surface, base-vs-worktree trust sourcing, and the
outward-credential vs integrity-value taxonomy.

## 0030 — The action-policy machine

**State:** Accepted
**Folder:** [decisions/0030-action-policy-machine/](decisions/0030-action-policy-machine/)

One `(trigger) → (action)` machine subsumes three previously separate shapes: the tracker transition
graph (0017), the positional lifecycle hooks (0026), and ad-hoc VCS-outcome handling. Triggers are
lifecycle positions, typed operation results, and task-state events; actions are `run_op`, `run`
(hook), `escalate` (abstract, bound per front-end), `create_task`, `set_state`, `notify`, `park`,
`fail`. Hooks become policy edges (`after_push` ≡ `push:ok`). Matching is most-specific-wins with a
**`#class` fallback** over the proto outcome classes (`done`/`needs_caller`/`error`), so configs need
not enumerate every code and the vocabulary can grow without breaking them; an unmatched **operation
outcome** is **fail-safe** (never a silent drop), while an unmatched signal stays a benign no-op.
Abstract `escalate` lets the same WoW run under both front-ends. The proto **class** of each reason
becomes part of the public contract. Generalizes 0017 (still Accepted; `tracker.transitions` becomes
a `set_state` binding); supersedes the positional-hook axis of 0026, which moves to `Superseded`
(0033) with its positions kept as triggers and its trust classification preserved. Depends on 0027,
0028 (both Accepted). Accepted and applied to `SPEC.md` (new Section 9.12 plus Sections 5.6, 11.6)
against the `VCSX-CONTRACT.md` stub (0039): the `(trigger) → (action)` machine, the `#class` fallback,
the fail-safe-on-unmatched-outcome rule, and abstract `escalate`, with `tracker.transitions` recast as
a `set_state` binding within it.

## 0031 — Autonomous task management and computed completion

**State:** Accepted
**Folder:** [decisions/0031-autonomous-task-management/](decisions/0031-autonomous-task-management/)

A daemon-side task model makes completion **computed** rather than asserted: tasks carry an id,
status, and an `agent`/`human` assignee; they seed from the ticket (capability-gated, 0018) or from an
opening planning turn; the agent manages them through broker-CLI verbs (`add`/`split`/`close`/
`need-help`/`update`, extending 0003/0004). `tasks:all_closed` runs `ship`; a conflict binds
`escalate` (0030) to an agent task; `need-help` is an agent-created human-assigned task that parks for
feedback. Daemon-only — interactive sessions use `ship`/`land`. Refines 0008 and 0017 (milestone
signals → computed task state). The durability fork is **resolved**: the agent's `add`/`split` cause
the broker to **materialize** the task list into the tracker as structured artifacts (write-through,
default on where 0018 declares a structured-task-write capability; disablable in `repo.policy.toml`),
making the list `Reconstructable` (0010) with faithful restart; the fallback where the tracker can't
hold structure (or write-through is off) is `Durable`, never `Ephemeral` by default. Depends on 0027,
0030 (both Accepted). Accepted and applied to `SPEC.md` (new Sections 4.1.9, 8.10 plus Sections 7.2,
10.8, 11.6, 14.3) against the `VCSX-CONTRACT.md` stub (0039): the `Task` entity, computed completion,
the broker task verbs, write-through materialization, and the `Reconstructable`/`Durable`
classification.

## 0032 — Message formulation: commit, pull request, squash

**State:** Accepted
**Folder:** [decisions/0032-message-formulation/](decisions/0032-message-formulation/)

Message **content** is the agent's; message **formulation policy** is repo-owned WoW; Symphony bakes
in no format. The three surfaces have distinct origins: the **commit** message is *authored* by the
agent in-sandbox (validated by `scan-content`; author/committer identity is repo config per 0007); the
**pull-request** message is *composed* from agent-supplied prose and/or durable inputs (ticket, the
closed task list from 0031, commit subjects), scanned title-strict / body-Linear-relaxed; the
**squash** message is *mechanically transformed* from the PR via a repo-owned `pr_to_squash` at the
`before:merge` position (0030) — title verbatim, body strip-linear — re-imposing on history the
strictness relaxed for the live PR surface, so `land` stays thin. Adds a credential-free broker-CLI
content seam for agent-supplied PR text. The PR-body-source fork is **resolved**: the default body is
auto-composed from ticket + closed task list (0031) + commit subjects, with agent prose overriding when
supplied. Relates to 0003/0007/0022/0030/0031. Depends on 0027, 0030 (both Accepted). Accepted and
applied to `SPEC.md` (Sections 9.8, 9.10) against the `VCSX-CONTRACT.md` stub (0039): the three
message surfaces (authored commit, composed PR, `pr_to_squash`-transformed squash), the auto-compose
PR-body default with agent-prose override, and the credential-free content seam.

## 0033 — A `Superseded` state in the decision-log lifecycle

**State:** Accepted
**Folder:** [decisions/0033-superseded-decision-state/](decisions/0033-superseded-decision-state/)

Adds a fourth state to the decision-log lifecycle (0001): `Superseded` — *replaced by a later
decision; kept for the record*. Decision 0030 exposed the gap: it supersedes the positional-hook axis
of 0026 while keeping 0026's durable parts (the lifecycle positions, now triggers; the trust
classification, still used by 0029), so 0026 is neither `Rejected` (its mechanism was not decided
against — parts survive) nor still `Proposed` (its framing is no longer under consideration). A
`Superseded` chapter names its successor; unlike `Rejected`, a superseded decision may have been sound
and may live on in that successor. Refines 0001; first applied to 0026 (superseded by 0030). Applied
immediately — edits only the `DECISIONS.md` legend and its `CLAUDE.md` mirror; no `SPEC.md`
dependency. Accepted and applied.

## 0034 — Repository provisioning failure class and clone reference algorithm

**State:** Accepted
**Folder:** [decisions/0034-repository-provisioning-failure-class/](decisions/0034-repository-provisioning-failure-class/)

Section 9.7 describes the *result* of repository provisioning ("one fetched object store per
repository on the host") and its credential boundary, but the spec has no failure class, no recovery
behavior, and no reference algorithm for the host-side clone/fetch that creates it — an asymmetry with
the fully-specified per-issue worktree path (algorithm in 9.2, `Workspace Failures` in 14.1, recovery
in 14.2). This decision closes that gap with **Option C**: a `Repository Provisioning Failures` class
in Section 14.1 (parallel to `Workspace Failures`), a **repo-scoped** recovery entry in Section 14.2
(skip the affected repository's dispatches and retry on a later tick, distinct from issue-scoped
worker backoff; persistent auth/config failure park-vs-retry is `Implementation-defined`), and an
`ensure_object_store(repo)` reference algorithm in Section 16 that runs before
`provision_for_issue`. The decision fixes a layer-ownership error: the clone is **broker-core/daemon**
work that uses the secret store (Section 15.3) and is **not** a `vcsx` responsibility — `vcsx` operates
on an already-provisioned worktree (0007 "Symphony performs … clone/fetch …", 0027 broker-core holds
credentials; 0028 defers only commit/push/pr/merge, not clone). No new config key (object-store path
stays `Implementation-defined`). Builds on 0025 (Proposed), which named repository provisioning as an
under-specified host-side op: this decision closes its failure-model half and leaves 0025's per-session
CPU-governance question open. Relates to 0007, 0009, 0028. Depends on 0027 (Accepted). Accepted and
applied to `SPEC.md`.

## 0035 — The execution process and the always-present orchestrator↔executor seam

**State:** Accepted
**Folder:** [decisions/0035-execution-process-and-seam/](decisions/0035-execution-process-and-seam/)

The head of a four-decision set (0035–0038) reintroducing remote execution — the "reworked
remote-execution extension" 0004 anticipated when it dropped the SSH Worker Extension for shipping the
agent without the sandbox/per-run-socket/credential boundary. Driver: run coding-agent sessions on
**Cloud Instances** billed per started hour, provisioned/reaped by an external system, variant chosen
per repo and/or issue label, work shared under a configurable policy — implementing *as little
cloud/scheduler logic as possible* in Symphony (which is *little logic*, not *no new surface*). This
decision gives Section 3.2's **Execution Layer** a component identity — the **execution process
(executor)** — that owns everything the in-process worker does today (Section 16.6: workspace, object
store, prompt build, turn loop, agent protocol, broker, hooks), and makes the orchestrator↔executor
seam **always present**: local execution is the degenerate **in-process transport**, remote execution
(0036/0037) is the same seam over a network transport. One execution model, so local and remote cannot
duplicate or drift; the node-scheduler is purely a placement + transport adapter behind the seam. The
executor instantiates the secret-isolation boundary (sandbox 9.6, per-run broker socket 10.8,
credential-less agent 15.3) *wherever it runs*, so carrying it to a node becomes a property of the
transport rather than a bolt-on. The unification is of the **execution process and the seam**, not the
wiring around them: 0036 (transport/secrets), 0037 (node-scheduler acquisition), and 0038 (executor
commits) are the **autonomous-daemon topology's** realization; the interactive-agent (`ship`/`land`)
and engine-direct (operator holds secrets) topologies reuse the same execution process with their own
initiator and secret-sourcing (0027). Options: A bolt remote on beside a single-host core (duplicates the
execution path); B a first-class executor behind an always-present seam (chosen); C reconsider for a
lighter mechanism (rejected — the lighter mechanisms are the ones 0004 already rejected). Realizes
0025's Option C "session resource domain" as a placed component (see 0025's 2026-07-03 update). Relates
to 0004, 0025, 0027 (its Execution Layer given a component identity, shared across the three
topologies with the daemon-topology wiring carried by 0036–0038), 0003. Parent of
0036–0038. Accepted and applied to `SPEC.md` (Sections 3.1, 3.2, 16.4, 16.6) in the spec's current
vocabulary; the three-topology framing and base-revision hook sourcing stay in the decision folder
pending the deferred 0027/0029 edits.

## 0036 — The orchestrator↔executor protocol and direct secret delivery

**State:** Accepted
**Folder:** [decisions/0036-orchestrator-executor-protocol/](decisions/0036-orchestrator-executor-protocol/)

Specifies the network transport of the 0035 seam. Following the deferral pattern of Section 10 (agent
app-server protocol) and 0028 (`vcsx` contract), the orchestrator↔executor wire protocol is its **own
versioned sub-spec** that `SPEC.md` defers to; the spec owns orchestration semantics, not schemas.
**The agent protocol terminates on the executor** — the orchestrator is never in agent communication;
it dispatches a **run-spec** (normalized issue data, workflow template, agent/effort, `max_turns`,
wall-clock bound, `continuation_ref`) plus secrets, and receives only normalized runtime events
(Section 10.4), usage (13.5), outcome, and committed-state notifications. The up-channel is **durably
buffered on the executor with a sequence cursor and replayed** from last-ack on reconnect, so an
orchestrator disconnect leaves no gap in the event log or token accounting. **Secrets are delivered
orchestrator→executor directly** (never through the scheduler) over a channel secured by
**scheduler-bootstrapped mutual auth** (mutual TLS; the scheduler provisions one-time trust material,
enabling trust without seeing the secret); Section 15.3's agent-side invariant is unchanged (the secret
reaches the executor's broker context, never its sandbox). Version is **negotiated with a documented
minimum floor** — a stale warm-node image fails closed at bring-up rather than mis-parsing mid-run.
Options: A inline the protocol (drops the spec below altitude); B a deferred versioned sub-spec
(chosen); C inline contract + external schema (splits the source of truth). Relates to 0004, 0035,
0037, 0038, 0028, 0003, Section 15.3. Depends on 0035. Accepted and applied to `SPEC.md` (Sections 10,
15.3); the versioned protocol sub-spec is referenced as a forward external document not yet authored.

## 0037 — The node-scheduler remote adapter, provisioning failures, and the run registry

**State:** Accepted
**Folder:** [decisions/0037-node-scheduler-remote-adapter/](decisions/0037-node-scheduler-remote-adapter/)

How the orchestrator obtains a remote executor, what happens when it cannot, and how it finds an
in-flight remote run after a restart. Symphony is *configured to connect to* an external
**node-scheduler** that owns node lifetimes end to end — provisioning/reaping, executor-software
deployment, mutual-auth bootstrap (0036), pooling/autoscaling/billing, the instance-variant catalog and
variant-selection logic, and teardown timing — and is deliberately **not** in the secret path (0036)
or agent communication. Symphony connects through a thin `compute`-kinded adapter (sibling of the
tracker/VCS/forge adapters) with a static capability descriptor and **four verbs**:
`request_node(selection, bound)` (selection = repo identity 8.7, normalized labels 11.3, agent/effort
10.9, sharing key+hint; bound = wall-clock/cost ceiling), `node_ready(endpoint, trust_material)`,
`lookup_by_run_id(run_id) → endpoint` (reattach, surviving node moves), `signal_done(run_id)` (the
scheduler decides keep-warm/reuse/destroy). Everything cloud-shaped stays `Implementation-defined`;
Symphony treats the node as opaque. **Boundary travel is a fail-closed conformance requirement** of
`remote` (sandbox 9.6, per-run socket 10.8, credential-less agent 15.3; `ensure_object_store` from 0034
runs fresh on the executor's node). Acquire is **async with a new `provisioning` orchestration
sub-state** (Section 7). **Two new failure classes** (with the existing agent-session class, three
surfaces total): `Node Provisioning Failures` → scope-scoped skip + retry, mirroring `Repository
Provisioning Failures` (0034); `Executor Bring-up Failures` (won't start / auth / boundary) →
fail-closed, fresh node; agent-session (14.1) unchanged. Restart uses a **required,
remote-mode-only durable run registry** (`run-id ↔ issue ↔ node`) reconciled via `lookup_by_run_id`
(local keeps 14.4 reconstruct). **Sharing** is a `sharing_key` + hint; the scheduler packs isolated
executor processes (each with its own sandbox/broker/secrets), so cross-credential co-tenancy risk
dissolves and Section 8.3 concurrency stays session-count-based/placement-opaque (no new knob).
Across-run retry is orchestrator-owned and **non-coercive** (it may re-dispatch but MUST NOT compel the
scheduler to supply a node — enabler-not-enforcer, 0027). New `compute.*` config (`kind` default
`local`, variant-by-repo/label pass-through, sharing hint/key, wall-clock bound, release disposition),
extension-owned, not Core Conformance. Relates to 0004, 0034, 0025, 0027, 0035, 0036, 0038. Depends on
0035, 0036. Accepted and applied to `SPEC.md` (Section 9.11 plus Sections 7.1, 8.3, 8.4, 14.1, 14.2,
14.4, 6.4, 16.4).

## 0038 — Executor-authoritative writes and the driver-local / reconciler-remote reframing

**State:** Accepted
**Folder:** [decisions/0038-executor-authoritative-state-writes/](decisions/0038-executor-authoritative-state-writes/)

Resolves who writes the authoritative record of a run once the executor (0035–0037) runs the whole
session on a node. The executor runs the turn loop autonomously and owns completion (turn count and
"has the work progressed" — computed completion, 0031), holds the repo (it cloned it) and the
credentials (0036), so the repo-owned WoW (0029, read from base) and the action-policy machine (0030)
execute **on the executor** — which therefore also **commits** the outcome: opens the PR through its
on-node broker and sets tracker state via the machine's `set_state`. Section 7 is reframed
**driver-local / reconciler-remote**: the orchestrator drives dispatch/candidate selection, but for an
in-flight run the executor is the authoritative writer and the orchestrator **reconciles from the
tracker** — which it already does (humans edit tickets; Section 8.5 reconciles every tick), so this
extends an existing reconciliation rather than inventing one. The **broker instance moves onto the
executor** (0003/0004 invariant preserved — the agent sandbox holds no credentials); **git/forge writes
are executor-exclusive** (only the executor holds those creds), while **tracker read/write is shared**
(the orchestrator already polls with tracker creds; the executor may read/write too). `escalate` (0030)
is resolved by an **executor tracker write** (comment / blocked state) the orchestrator observes — no
new up-channel message for the common case. Terminal-mid-run guard is **hybrid**: while connected the
orchestrator forwards terminal/cancel on the live down-channel (0036); while disconnected the executor
**re-checks tracker state before finalizing writes** so it never pushes for a closed issue. Options:
executor-commits / orchestrator-observes (chosen) vs. executor-proposes / orchestrator-commits vs.
orchestrator sole writer. Edits applied **in step with** the deferred 0029–0031 `SPEC.md` edits (so the
action-policy machine is never named before it exists, per 0034's deferral discipline). Relates to
0003/0004, 0017, 0021, 0029, 0030, 0031, 0035, 0036, 0037. Depends on 0035, 0036, 0037. Accepted and
applied to `SPEC.md` (Sections 7, 10.8, 11.5, 8.5) in current vocabulary; the action-policy machine
(0030) and repo-owned WoW (0029) are expressed via the existing transition graph, `set_state`, and
`blocked` signal pending the deferred 0029/0030 edits.

## 0039 — vcsx contract-surface stub to unblock the repo-owned-WoW batch

**State:** Accepted
**Folder:** [decisions/0039-vcsx-contract-surface-stub/](decisions/0039-vcsx-contract-surface-stub/)

Acts on decision 0028's own deferral. The 0027–0032 batch's `SPEC.md` edits are gated on the companion
`vcsx` spec ("contract names stay identical across both documents", 0028), which did not exist in this
repo and had no tracked owner — a hard external gate that could stall the largest re-framing of the
spec indefinitely. This decision authors `VCSX-CONTRACT.md`, a **contract-surface stub** that freezes
the shared vocabulary — the executor and its two front-ends (`ship`/`land` + the daemon driver) over
one policy-graph executor and one `repo.policy.toml`; the action-policy machine (triggers
`before:commit`/`before:push`/`before:create_pr`/`before:merge`, `<op>:<reason>` results, task-state
events; actions `run_op`/`run`/`escalate`/`create_task`/`set_state`/`notify`/`park`/`fail`; the
`#class` fallback over `done`/`needs_caller`/`error`; fail-safe on an unmatched operation outcome; the
reason-token class contract; abstract `escalate`); the engine operations and typed results
(`commit`/`integrate`/`push`/`create_pr`/`merge`); the lifecycle positions and the positional-name
mapping (`after_push` ≡ `push:ok`); the task model and broker verbs
(`add`/`split`/`close`/`need-help`/`update`, `tasks:all_closed` → `ship`, `structured-task-write`,
write-through materialization); the message-formulation surfaces (authored/composed/transformed,
`pr_to_squash` at `before:merge`, the content seam); and the trust-sourcing rule plus the
outward-credential vs integrity-value taxonomy. Every token is taken verbatim from decisions 0026–0032,
so freezing them creates no new design. It mirrors the app-server-protocol deferral: the stub owns
entry points and policy vocabulary, while the **wire/RPC schema, the field-level `repo.policy.toml`
schema, the plugin API, the concrete reason-token registry beyond its classes, and internal
algorithms** stay deferred to the full engine spec. Options: A leave the batch gated on the missing
external spec (stalls indefinitely); B a bare in-repo placeholder pointer (freezes nothing); C the
contract-surface stub (chosen). Keeps `SPEC.md` the single source of truth and shrinks the deferral
window: the 0027–0032 edits can now be written against a stable in-repo anchor, and the full `vcsx`
spec reconciles to these names rather than inventing them. Depends on 0028; relates to 0026–0032
(shaping) and 0035–0038 (which reuse the executor). Accepted; `VCSX-CONTRACT.md` authored, no `SPEC.md`
edit made.

## 0040 — Author the full vcsx engine specification

**State:** Accepted
**Folder:** [decisions/0040-vcsx-full-engine-spec/](decisions/0040-vcsx-full-engine-spec/)

Completes the forward artifact decision 0039 deferred. The contract surface (`VCSX-CONTRACT.md`, 0039)
fixes the `vcsx` vocabulary `SPEC.md` references but §11 defers the deep detail to a "full engine
specification" that did not exist; with the 0027–0032 batch applied against that surface, the deferral
target must resolve to a real document. This decision authors `VCSX-SPEC.md`, a full, standalone,
language-agnostic engine spec, and wires `VCSX-CONTRACT.md` (header, §11, §12) to name it. The layering
is now three clean levels — Symphony `SPEC.md` → the contract surface `VCSX-CONTRACT.md` → the full
engine spec `VCSX-SPEC.md` — each deferring the next's detail rather than restating it, mirroring how
`SPEC.md` defers to the Codex app-server protocol. `VCSX-SPEC.md` fixes the operation set and the
concrete reason-token registry with stable proto classes; the full action-policy machine (triggers,
actions, the `#class` matching ladder, unmatched policy, determinism, escalation binding); the
field-level `repo.policy.toml` schema (`[engine]`/`[scope]`/`[base]`/`[policy]`/`[hooks]`/
`tracker.transitions`/`[messages]`/`[tasks]`/`[driver]`, `vcsx.toml` merge, base resolution,
execution-context labeling); the `ship`/`land` front-ends and the embedded-driver contract; the
transport-neutral invocation contract (result envelope, exit codes, escalation payload, versioning with
a `version_floor` floor); the plugin API for VCS and forge backends with capability descriptors; the
message-formulation seams (`scan-content`, PR composition, `pr_to_squash`) with no built-in format; a
security/trust model that enforces nothing itself; and reference algorithms. Every shared token is
spelled identically to the surface. Options: A keep deferring to an unwritten spec (implementable from
nothing); B fold the detail into `VCSX-CONTRACT.md` (inflates the stable surface); C a separate
`VCSX-SPEC.md` the surface defers to (chosen). Builds on 0039; relates to 0026–0032. Accepted;
`VCSX-SPEC.md` authored and `VCSX-CONTRACT.md` wired to it, no `SPEC.md` edit made.

## 0041 — Integrate the phased-spec implementation workflow

**State:** Accepted
**Folder:** [decisions/0041-integrate-phased-spec-workflow/](decisions/0041-integrate-phased-spec-workflow/)

Installs a reusable phased-delivery workflow for the eventual `SPEC.md`→implementation transition: a
discovery / behavior-contract / verification / implementation / conformance-closure gate sequence
backed by seven skills (`spec-roadmap`, `phase-planner`, `phase-workflow`, `phase-behavior-contract`,
`phase-verification`, `phase-implementer`, `phase-closeout`), an ExecPlan standard (`.agent/PLANS.md`),
and a roadmap/traceability/template scaffold under `docs/implementation/`. The bundle shipped
Codex-oriented and written as though implementation were already underway; it was reconciled rather
than dropped in verbatim. Options: A install verbatim (its `AGENTS.md` misrepresents the current state
and its skills reach only Codex); B take only the skills (breaks their references to the planning docs
and the validator); C install the full bundle reconciled (chosen). The canonical skills live once under
`.agents/skills/` and are mirrored to Claude Code as `.claude/skills/` symlinks — one source of truth,
no drift; the same single-source principle governs the instruction files, so the governance lives in
`CLAUDE.md` and `AGENTS.md` is a symlink to it, letting Claude Code and Codex read one shared file. It
states the workflow is **dormant** until implementation is explicitly begun, so the near-term focus
stays on refining `SPEC.md`; no requirement IDs, roadmap, or traceability rows are generated yet.
`scripts/validate_workflow_bundle.py` passes. No `SPEC.md` edit made.

## 0042 — Realize `vcsx` as a separate deliverable, engine-direct first

**State:** Accepted
**Folder:** [decisions/0042-vcsx-realization-separate-deliverable/](decisions/0042-vcsx-realization-separate-deliverable/)

Fixes realization and sequencing for the VCS engine layer, whose shape decisions 0027, 0028, 0039 and
0040 already settled and applied. Two facts bound the space first: a Symphony-native VCS/forge
implementation is foreclosed by Section 9.7 ("there are no parallel Symphony VCS/forge adapters for
those operations"), so choosing one would re-open 0028 rather than answer this decision; and `OPTIONAL`
in Section 3.4 is topology-scoped, not build-scoped, since Section 18.1 requires a VCS engine and the
action-policy machine for Core Conformance — the engine is skippable only by not building the daemon.
Realization options: A a separate deliverable from the start (chosen) — its own codebase, pinned by
`version_floor`, reached over the `VCSX-SPEC.md` invocation contract; B an in-process module behind the
same contract, extracted later (sanctioned by `VCSX-SPEC.md` Section 8, "only the encoding differs", but
the boundary holds only while a dual-encoding conformance suite enforces it, and standalone reuse waits
on extraction); C generalize an existing wrapper layer into the engine (proven code, but shaped by one
repository's Way of Working — the pull 0027 rejected; admissible as a seed, not exclusive with A or B);
D a minimal fixed-policy subset with the policy machine deferred (rejected — the monolith 0027
rejected, expensive to retrofit). Sequencing options: `engine-direct` first (chosen), `interactive-agent`
first, `daemon` first. The two chosen axes compose: the cross-repo tax that argues against a separate
deliverable is only paid while both codebases are in motion, and `engine-direct` first means only one
is — while putting the artifact most likely to be wrong, the policy vocabulary and the
`repo.policy.toml` schema, in front of a real user before Symphony freezes it. Carried from the first
commit so later layers extend rather than retrofit: execution-context labeling (`host_side` /
`in_sandbox`, the seam the Broker Core later splits on) and the fail-closed `version_floor` pin.
Accepted residual risk: the secret-isolation invariant — Symphony's one enforced guarantee — stays
unproven longest, a deliberate trade since its design is already fixed by 0003/0004 and `engine-direct`
has no sandboxed agent to inform it. Reconsider if parallel Symphony/engine development makes the
cross-repo cost dominate (Option B needs no re-decision, the contract being identical across
encodings), if `engine-direct` usage warps the engine toward the human case, or if no second consumer
materializes. Depends on 0027, 0028, 0039, 0040. Accepted; no `SPEC.md` edit follows — Section 3.4
already states the engine is an independent deliverable pinned as an external tool, and Section 5.6
already defers the `repo.policy.toml` field schema. Leaves one follow-on, taken up by 0043:
conformance profiles, which are what reconciles Section 3.4's `OPTIONAL` with Section 18.1's REQUIRED.

## 0043 — Layer-keyed conformance profiles

**State:** Accepted
**Folder:** [decisions/0043-layer-keyed-conformance-profiles/](decisions/0043-layer-keyed-conformance-profiles/)

Closes the gap 0027 opened and 0042 named. Section 3.4 makes the Broker Core "independently
conformant … for a single interactive agent session with no polling daemon", but Section 18.1 requires
the polling orchestrator, the tracker client, complete candidate enumeration, multi-repo routing, the
retry queue, and reconciliation — so `Core Conformance` has meant *the `daemon` topology*, and the unit
0027 elevated to a standalone deliverable had no profile to claim, while `interactive-agent` and
`engine-direct` were described in Section 3.4 and unrepresented in Sections 17 and 18. **The layer, not
the topology, becomes the unit of conformance**: `Broker Core Conformance` and `Daemon Conformance` are
defined as the two components of `Core Conformance` (kept as the umbrella, so every existing "Core
conformance does not require these fields" clause stays true), engine conformance is *deferred* to
`VCSX-SPEC.md` Section 13 rather than restated, and the three topologies are declared compositions —
`engine-direct` = engine alone, `interactive-agent` = Broker Core + engine, `daemon` = Broker Core +
Daemon + engine. Section 18.1's flat list is regrouped under the layer that owns each bullet (none
added, none removed) and Sections 17.1–17.7 gain a per-subsection profile scope, with item-level
scoping only in the two mixed subsections — so each profile's subset is *derived from one list* rather
than restated. Two allocation calls are made rather than left to the editor: the tracker adapter splits
on the line the document already draws, its read surface (`fetch_candidate_issues`, state refresh,
terminal fetch) being `Daemon Conformance` and its broker-mediated write surface (`set_state`,
comments) `Broker Core Conformance`; and the Agent Runner with its adapters is `Broker Core
Conformance` while the prompt template and `WORKFLOW.md` loader are `Daemon Conformance`. The engine
layer is REQUIRED **conditionally** — of any deployment performing a remote VCS or forge operation
(push, back-merge, `create_pr`, merge) — which leaves Section 3.4's "optionally driving the VCS Engine"
intact and reads the way `Extension Conformance` already does. Options: A layer-keyed with structural
per-item scoping (chosen); B one profile per topology (rejected — the topologies nest, so each list
restates the previous and one change must land in three places); C per-item tags with no profile
definitions (rejected — nothing states what a claim requires); D relax Section 3.4 and accept
`Core Conformance` = daemon (rejected — re-opens 0027's headline as partly `Superseded`). Engine
coupling: B1 conditional on remote operations (chosen) over B2 unconditional for the daemon profile.
Depends on 0027, 0028, 0042; relates to 0040 (the deferral pattern it reuses for engine conformance).
Accepted and applied to `SPEC.md` (Sections 3.4, 17, 18.1, 18.2, and a profile declaration per
OPTIONAL extension); Section 18.1 gained a fourth `Both Layer Profiles` group for the five genuinely
shared items, and Section 17.2 proved mixed as well — both recorded in `Plan.md`.

## 0044 — Engine invocation failure class

**State:** Accepted
**Folder:** [decisions/0044-engine-invocation-failure-class/](decisions/0044-engine-invocation-failure-class/)

Supplies the consumer-side half of a contract whose engine side was already specified. `VCSX-SPEC.md`
Section 8.5 has an engine below the repository's `version_floor` refuse to run fail-closed "rather than
mis-executing a policy that assumes newer surface", and Section 8.3 makes that outcome distinct — exit
`2`, "usage or configuration error; the policy did not run" — but `SPEC.md` Section 14.1 had no class
for it, Section 14.2 no recovery behavior, and Section 18.1's engine group required a conforming engine
without saying what happens when the one present is not. A new core class `Engine Invocation Failures`
covers exactly the cases in which **the policy never ran**: the engine unavailable, not conforming to
the invocation contract, refusing below the floor, or returning a usage/configuration result. The
scoping is the substance — once the policy runs, the action-policy machine (Section 9.12) already owns
every operation outcome through the `#class` ladder and its unmatched-outcome fail-safe, so drawing the
boundary at *did the policy run* keeps the two mechanisms disjoint and makes the class decidable
straight from the result envelope. Recovery mirrors `Repository Provisioning Failures` (0034) because
the blast radius is identical — the floor and the operation flow are declared in that repository's
`repo.policy.toml` — so it is repository-scoped: skip that repository's dispatches, keep the service
alive, retry on a later tick, never convert to a per-worker backoff, and park persistent cases under a
documented `Implementation-defined` policy. Options: A the scoped class (chosen); B extend
`Workflow/Config Failures`, whose "Missing coding-agent executable" is a real precedent but whose
instance-wide disposition mis-scopes a repository-owned floor; C rely on the policy machine's
unmatched-outcome fail-safe, which by construction cannot fire when no operation ran; D per-worker
backoff retry, which never converges on a configuration defect. Surfaced while verifying 0042's
post-conditions and predates it. Depends on 0028, 0040; relates to 0034 (the recovery shape it
mirrors) and 0030 (the boundary it stops at). Accepted and applied to `SPEC.md` (Sections 14.1, 14.2,
17.4, 18.1.4): the class is core class 7, shifting the two OPTIONAL remote classes to 8 and 9.

## 0045 — Multi-implementation conformance: the Conformance Statement

**State:** Accepted
**Folder:** [decisions/0045-multi-implementation-conformance-statement/](decisions/0045-multi-implementation-conformance-statement/)

Answers how to run several implementations of `SPEC.md`, potentially in different languages, without
fragmenting the contract. "Language-specific choice" is two things: **contract-visible variation** an
implementation makes and a consumer can observe — the 26 `Implementation-defined` / `MUST document`
obligations, the profile and topology claimed (0043), the OPTIONAL extensions shipped (Section 18.2),
the engine `version_floor` and agent protocol floor pinned (Sections 8.5, 10.2), the recovery class
assigned each Orchestrator Runtime State field (Section 14.3) — and **idiomatic realization**
(concurrency model, error idiom, libraries, layout) the contract cannot see and the spec is silent
on. Each is already required to be documented *somewhere*, but nothing says *where* or gathers them,
so implementations cannot be compared and a silently-skipped obligation stays invisible. Introduce a
normative, human-readable **Conformance Statement** — a per-implementation published artifact that
consolidates exactly the contract-visible choices — with a repo-owned template
(`CONFORMANCE-STATEMENT-TEMPLATE.md`) that pre-enumerates every obligation and every runtime-state
field. The Statement adds no obligation: it is a *view* over 0043's profiles, Section 18.2's
extensions, the version floors, the `Implementation-defined` clauses, and Section 14.3's recovery
classes — the same single-source derivation 0043 used so a checklist cannot drift into three, and it
keeps `SPEC.md` language-agnostic because the choices are recorded *outside* the normative text.
Options: A the human-readable Statement with template (chosen); B leave the obligations scattered
(rejected — defeats the comparability that is the point of multiple implementations); C fold into the
Section 18 checklist only (rejected — a definition-of-done bullet is not a published declaration and
cannot carry a filled-in value); D a machine-readable manifest schema (deferred — over-commits to a
wire format before an implementation exists to shape it, against 0040's defer-schema discipline;
the natural successor once a second implementation or a conformance harness creates demand). Around
the Statement, three positions are recorded rather than built: a shared, language-neutral
**conformance corpus** (data-driven vectors turning Sections 17–18's prose into objective pass/fail
in every language) as the follow-on authored when implementation begins; **decision-log hygiene**
(this log binds all implementations, idiomatic choices live in each implementation's own log, and a
language that exposes a genuine `SPEC.md` gap routes a decision back *here*); and **live-state
interoperability** as an explicit non-goal (Sections 14.3–14.4 give containment, not handoff of a
running issue between implementations — its own decision if ever wanted). Depends on 0027, 0040,
0042, 0043; relates to 0002 (the stable-addressing discipline the Statement and template follow).
Accepted and applied: `CONFORMANCE-STATEMENT-TEMPLATE.md` is created, and `SPEC.md` gains Section 19
`Conformance Statement`, a `Both Layer Profiles` checklist item (Section 18.1.1), and pointers to it
from the Section 1, 9.6, and 14.3 documentation clauses.

## 0046 — Conformance corpus, first slice

**State:** Accepted
**Folder:** [decisions/0046-conformance-corpus-first-slice/](decisions/0046-conformance-corpus-first-slice/)

Drafts the shared, language-neutral conformance corpus 0045 named as the mechanism that turns
Sections 17–18's prose into an objective pass/fail identical in every implementation language, and
fixes the choices later slices inherit. Format is JSON (every language parses it dependency-free;
`SPEC.md` already uses it for payloads; YAML rejected for its non-uniform implicit typing, a
per-language test file rejected as not being data). The corpus lives in a spec-adjacent
`conformance/` tree — a `README.md` plus one `vectors/*.json` file per behavior. The first slice
covers only pure, host-independent functions — `sanitize_workspace_key`, `normalize_state`,
`resolve_config_defaults`, `retry_backoff_delay_ms`, `available_slots`,
`per_state_concurrency_limit`, `sort_for_dispatch` (31 vectors) — so it runs identically on day one
with a few-line harness and no sandbox, tracker, engine, filesystem, or network; integration
behaviors are deferred to a later slice tied to the `Real Integration Profile` (Section 17.8). The
corpus specifies a harness *contract* (invoke the named `function` with `given`, assert it equals
`expect`), not a harness in any language, and stays RECOMMENDED shared evidence feeding the
Conformance Statement's Section 7 evidence row rather than a new REQUIRED gate. Every expected value
is derived verbatim from the cited `SPEC.md` section; where the spec is silent no vector is authored
— non-ASCII workspace-key sanitization (Section 9.5 Invariant 3) does not fix whether "character" is
a byte, a code point, or a grapheme, so that gap is surfaced as a spec-clarification follow-on rather
than guessed at, the corpus doing its second job of exercising the spec. Depends on 0045; relates to
0002 (stable addressing) and 0044 (the Section 17.8 profile boundary it defers integration vectors
to). Accepted and applied: the `conformance/` tree (README + 7 vector files, 31 vectors) is created,
and `SPEC.md` Section 17's intro points at it as the RECOMMENDED machine-readable realization of its
deterministic checks; the non-ASCII sanitization clarification is resolved by decision 0047.

## 0047 — Workspace-key sanitization operates on UTF-8 bytes

**State:** Accepted
**Folder:** [decisions/0047-workspace-key-utf8-byte-sanitization/](decisions/0047-workspace-key-utf8-byte-sanitization/)

Resolves the gap 0046 surfaced. Section 9.5 Invariant 3 and Section 4.2 replaced "any character not
in `[A-Za-z0-9._-]`" with `_` but never fixed what a "character" is; the allowed set is all ASCII, so
the ambiguity bites only on non-ASCII input, where byte, code point, and grapheme readings diverge
and precomposed vs. decomposed accents would differ. Fix the unit to the **UTF-8 byte**: replace
every byte of the identifier's UTF-8 encoding not in `[A-Za-z0-9._-]` with `_`, so a non-ASCII code
point yields one `_` per byte. It is the only reading trivially identical in every language
(UTF-8-encode, scan bytes) with no UTF-16 surrogate handling and no Unicode library, and it always
yields pure-ASCII output — serving both the invariant (Section 9.5, "the most important portability
constraint") and the corpus's cross-language determinism. Options: A UTF-8 byte (chosen); B code
point (rejected — `codePointAt` surrogate care in UTF-16 languages, still normalization-sensitive);
C grapheme (rejected — needs a UAX-29 library and shifts across Unicode versions, breaking
cross-version determinism). Accepted costs: a non-ASCII code point expands to several underscores,
and the rule stays normalization-sensitive because it does not normalize first — tolerable since
sanitization is already lossy and non-reversible (Section 4.2 makes no round-trip claim), identifiers
are ASCII in practice, and normalizing would reintroduce the very Unicode dependency this avoids.
Reconsider if a tracker issues non-ASCII identifiers at scale where key collision or readability
matters, or if the key ever must round-trip to an identifier (it does not today). Depends on 0046;
relates to 0002. Accepted and applied to `SPEC.md` (Sections 4.2, 9.5) and the corpus
(`workspace-key.json` gains precomposed and decomposed non-ASCII vectors; the README finding is
marked resolved).

## 0048 — Conformance corpus, prompt-rendering slice

**State:** Accepted
**Folder:** [decisions/0048-conformance-corpus-prompt-rendering-slice/](decisions/0048-conformance-corpus-prompt-rendering-slice/)

Adds the corpus's second pure slice, the one 0046's README named next: `render_prompt`, pure over
(template, issue, attempt) → string (Section 12.1). Six vectors in
`conformance/vectors/prompt-rendering.json` cover known-variable substitution, multi-field
substitution, nested-list iteration (Section 12.2), `attempt` as a present integer, and the two
strict-mode MUST failures — an unknown variable and an unknown filter, each raising
`template_render_error` (Sections 5.4, 5.5). Authoring it forces two choices the first slice avoided.
The vector `expect` is extended to a **success-or-error union**: either the successful result or
`{ error: <class> }` asserting a raised error class — chosen over a separate `expect_error` field or a
sentinel value, because a vector is either a success or a failure and this is the convention every
later error-path vector (config validation, tracker errors) will reuse. And the templates are written
in **Liquid-compatible reference syntax**: a template needs a syntax, Section 5.4 names Liquid, and
because `WORKFLOW.md` is repository-owned and must render on every implementation a repository
targets, the syntax is effectively a cross-implementation contract; templates are single-line and
delimiter-based so no expected string depends on whitespace control. No `SPEC.md` change. Two gaps are
surfaced rather than guessed: Section 5.4's "Liquid-compatible semantics are sufficient" is a floor
not a mandate (tightening it to a shared syntax is a candidate), and `attempt` being "null or absent"
on the first run collides with strict unknown-variable failure (so only a present-integer `attempt`
is tested) — both open spec-clarification candidates. Depends on 0046; relates to 0044 (the failure
class its error vectors name) and 0047 (the finding-to-decision path it reuses). Accepted and applied
to the corpus (now 8 files / 39 vectors); no `SPEC.md` change follows.
