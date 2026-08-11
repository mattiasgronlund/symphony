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

## 0049 — Implement `vcsx` in Rust as a separate repository

**State:** Accepted
**Folder:** [decisions/0049-vcsx-rust-separate-repository/](decisions/0049-vcsx-rust-separate-repository/)

Fixes the three things 0042 deliberately left open when it made the engine a separate deliverable and
put `engine-direct` first: the implementation language, the repository that holds it, and where that
implementation's own decision log lives — the axes 0045 classified as contract-invisible. **Rust**, in
its **own repository**, `engine-direct` first (0042 confirmed, not re-opened; nothing in the language
or repository choice bears on sequencing). Language options: A Rust (chosen), B Go, C Python. The
engine's centre of gravity is a policy machine over a closed vocabulary whose proto classes are frozen
within a major version (`VCSX-SPEC.md` Sections 4.2, 4.3, 8.5) — three of Section 13.1's eight checks
are about that machine, and a mis-classified reason routes to a different `#class` edge with no build
or test failure anywhere. That is a type-system problem before it is a plumbing problem, and Rust's
exhaustive matching turns most of the cluster into compile errors; the forge plugins, where Rust is
weakest, are the part most insulated behind a neutral interface (Section 9.2) and least likely to be
where correctness is lost. Go was rejected for moving that same cluster from the compiler back into
tests despite the better forge ecosystem and the same static-binary property; Python for needing an
interpreter wherever the engine runs, against the pinned-external-tool model 0028 fixed. Repository
options: A separate (chosen), B beside the specification, C a monorepo with a future Symphony
implementation. Co-locating exactly one implementation with a contract meant to bind several makes
neutrality a matter of discipline rather than structure — the property 0045's whole model rests on —
and a separate repository gives idiomatic choices a home that does not dilute this log; the monorepo
buys nothing while only one codebase is in motion, which is 0042's own cross-repo-tax reasoning. The
embedding repository's `scripts/vcs/` wrapper layer — 0042's Option C seed — is recorded as a **design
seed, not liftable code**: the escalate-on-ambiguity bias, one JSON object on stdout, the `done` /
`needs_caller` / `error` proto classes, forge rate-limit ride-out, and jj secondary-workspace slug and
branch derivation all transfer, but its exit codes (`0`/`2`/`10`/`64`) collide with Section 8.3's
(`0`/`10`/`20`/`2`), reusing `2` and `10` with different meanings, so carried code would satisfy its
own tests while silently violating the invocation contract. Decision-log hygiene per 0045 is unchanged:
an engine-document change or a gap it exposes routes a decision back here, while crate layout, whether
the engine is async at all, the error idiom, and the HTTP client stay in the engine repository's log.
Reconsider if the forge plugin layer comes to dominate the work, or if the cross-repo cost dominates
while both codebases are in motion — the case 0042 anticipated, noting its Option B needs no
re-decision. Depends on 0042, 0045; relates to 0027, 0028. Accepted; no specification edit follows.
Leaves three follow-ons, taken up as 0050, 0051, and 0052.

## 0050 — Publish an engine Conformance Statement

**State:** Accepted
**Folder:** [decisions/0050-engine-conformance-statement/](decisions/0050-engine-conformance-statement/)

Closes a gap 0043 opened and 0049 made live. 0043 *deferred* engine conformance rather than restating
it — `SPEC.md` Section 17 says "The VCS engine has no profile here" and the Symphony statement template
defers to `VCSX-SPEC.md` Section 13 — but Section 13 receives that deferral with a test matrix and an
implementation checklist and no place to *publish* what an engine chose. The engine specification
carries five `Implementation-defined` obligations of its own (checkout-mode detection, Section 3.3;
`repo.policy.toml` discovery precedence, Section 6.1; the form of a hook's engine-invoked `run` unit,
Section 6.6; entry-point argument encodings, Section 8.1; the escalation `detail`, Section 8.4) plus
three documentation duties phrased without the keyword — reasons added beyond the Section 4.3 registry,
the `need` vocabulary (Section 8.4), and the plugin capability descriptors (Section 9.3). The gap is
sharpest for what 0049 builds first: `SPEC.md` Section 3.4 gives `engine-direct` no Symphony profile,
so a pure engine has no publication surface at all. Introduce a per-engine Conformance Statement with a
minimal repo-owned template (`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`) and a `VCSX-SPEC.md` Section
13.3 clause requiring it — mirroring `SPEC.md` Section 19 in structure and register at the engine's
much smaller scale. Options: A the template (chosen); B the Section 13.2 checklist plus a
per-implementation README (rejected — a ticked checklist item cannot carry a filled-in value, which is
the reasoning 0045 already applied to Symphony); C an engine section inside the Symphony template
(rejected — wrong owner, since an engine is conformant independently of Symphony and this would make a
Symphony artifact a precondition for an engine that may never be embedded, re-coupling what 0043
decoupled); D defer until a second engine exists (rejected — 0045's deferral was justified by
over-committing to a *wire format*, which a human-readable statement does not have, and its stated
trigger has fired). Like 0045's, the Statement adds no obligation: it is a view over obligations that
already exist. Including the capability descriptors is the one addition beyond the
`Implementation-defined` clauses and earns its place, because Section 9.3 makes an undeclared
capability an `error`-class result and Section 6.10 makes a policy requiring an unsupported one a
configuration error, so what a build declares is load-bearing for anyone authoring `repo.policy.toml`
against it. The Statement is a published declaration, not a gate; Sections 13.1 and 13.2 keep their
roles. Reconsider if the engine ever ceases to be an independent deliverable (0042's Option B), since a
single embedded artifact would have a single owner again. Depends on 0043, 0045, 0049; relates to 0002.
Accepted and applied: `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is created and `VCSX-SPEC.md` gains
Section 13.3.

## 0051 — The engine token vocabulary as data

**State:** Accepted
**Folder:** [decisions/0051-engine-vocabulary-as-data/](decisions/0051-engine-vocabulary-as-data/)

Mechanizes `VCSX-SPEC.md` Section 14's alignment rule — every token shared between the engine
specification and its contract surface MUST be spelled identically in both — now that 0049 has made an
implementation in a separate repository a **third** spelling on its own cadence, with nothing
mechanical connecting it. The rule's enforcement has been review, and review across two repositories is
where this drift survives longest: the failure is silent, since a reason carrying the wrong proto class
routes to a different `#class` edge and changes which policy fires with no build or test failure
anywhere. The vocabulary is also unusually suited to being data — Section 4.3 is already a 26-row
table, Section 4.1 a closed list of eight operations and four positions, Section 4.2 three classes,
Section 5.2 eight actions, Section 8.3 four exit codes — enumerations typeset as prose whose
correctness properties are exactly what a machine checks well. Publish them as
`conformance/vcsx/vocabulary.json` with a `conformance/vcsx/README.md` defining the schema and the
precedence rule. Options: A the registry (chosen); B a script extracting and diffing the token sets out
of the two documents (rejected — a brittle parser over prose that does nothing for the third spelling,
which is the part 0049 actually made worse); C prose discipline plus a pinned specification revision in
the engine repository (rejected — leaves a silent failure mode enforced by cross-repository review).
**The prose governs; the artifact is derived**, exactly as `SPEC.md` governs the Symphony corpus under
0046: every entry is read from the sections its `spec_refs` cite, entries carry names and the
properties the specification fixes about them rather than the prose of the rules those properties feed,
and a disagreement is a bug in the registry. Two normalizations are recorded — the combined
`status` / `diff` registry row expands to two entries, so 26 table rows yield 27; and operations gated
at no fixed position carry an explicit null rather than omitting the field. The artifact sits in its
own `vcsx/` subtree rather than folded into the Symphony corpus: the two derive from different
specifications, have different schemas, and are consumed by different implementations — one is a set of
behavior vectors, this is a vocabulary registry. This is 0045's deferred Option D taken up on its own
stated trigger ("once a second implementation or a conformance harness creates demand"). Reconsider if
the registry begins accumulating properties the prose does not fix, the sign it has stopped being a
derived view; the remedy is then to move the concept into `VCSX-SPEC.md` and re-derive, not to let the
registry lead. An engine conformance *corpus* — vectors over the matching ladder and the Section
5.3–5.4 fail-safe rules, in 0046's shape — is the natural successor and is deliberately not taken here.
Depends on 0045, 0049; relates to 0046 and to `VCSX-SPEC.md` Section 14, whose rule it mechanizes
without changing. Accepted and applied: `conformance/vcsx/` is created; no specification edit follows.

## 0052 — `notify` with no consumer that can effect it

**State:** Accepted
**Folder:** [decisions/0052-no-consumer-notify-semantics/](decisions/0052-no-consumer-notify-semantics/)

Resolves a gap 0049 made live by scheduling `engine-direct` first. `VCSX-SPEC.md` Section 5.2 makes
`create_task`, `set_state`, and `notify` the consumer's to effect, and Section 1.3 admits a consumer
that is "a human at an interactive prompt" — with no task model, no tracker binding, and no
notification channel — so every policy using these actions can run through a consumer that cannot
perform them. The specification resolves that case for two of the three, inconsistently: `create_task`
is "a no-op when the consumer runs no task model" (Section 5.2), a `set_state` binding without a
consumer that can apply it is a configuration error caught at validation (Section 6.10), and `notify`
is unstated. The asymmetry is coherent rather than accidental — a dropped `set_state` strands control
flow while a missed notification costs only observability — so `notify` is classified with
`create_task` as a benign no-op, stating the existing logic rather than adding a rule. What is
genuinely added is the surfacing requirement, imported rather than invented: Section 5.4 already
forbids silently dropping an unmatched operation outcome because a dropped outcome strands a flow, and
an emitted intent no consumer performed is the same failure one level up. Surfacing is extended to
`create_task` as well, since special-casing `notify` would leave the identical silent-drop hazard for
the other no-op; `set_state` never reaches the path. The intents ride in the existing envelope under
`outputs.unperformed_intents` (Section 8.2), a named key rather than an `Implementation-defined`
representation — which avoids adding a sixth such site to a specification whose whole surface is five,
and makes the requirement mechanically checkable. Options: A the surfaced no-op (chosen); B uniform
intent emission in every front-end (rejected — a larger Section 8.2 change that alters what a *capable*
consumer receives and puts `set_state` on the emission path against Section 6.10's refusal to run at
all); C make every consumer-effected action without a consumer a configuration error (rejected —
contradicts Section 5.2's settled `create_task` clause and would make a policy that legitimately
degrades refuse to run). Section 5.5's "`escalate` is the single point at which their behavior
legitimately differs" is preserved, not weakened: the engine's behavior is identical in either
front-end and only the consumer's capability varies. Reconsider if a further consumer-effected action
arrives whose omission strands control flow the way `set_state`'s does — it belongs at validation, not
with the surfaced no-ops — or if a consumer emerges whose capability is dynamic rather than known
before the policy runs. Depends on 0049; relates to 0030 and 0042. Accepted and applied to
`VCSX-SPEC.md` (Sections 5.2, 8.2); no `VCSX-CONTRACT.md` edit is required, since its Section 11
defers the result envelope to `VCSX-SPEC.md` Section 8 and no shared token changes.

## 0053 — Engine conformance corpus, first slice

**State:** Accepted
**Folder:** [decisions/0053-engine-conformance-corpus-first-slice/](decisions/0053-engine-conformance-corpus-first-slice/)

Takes the successor 0051 named and deliberately did not take: vectors that exercise the machine *over*
the vocabulary that decision published. `VCSX-SPEC.md` Section 13.1's test matrix is prose — eight
bullets a conforming engine "SHOULD include tests covering" — and prose is neither pass/fail nor
transferable, since two engines can each believe they satisfy the matching bullet while disagreeing
about what an `op:#class` edge catches. 0046 solved this for `SPEC.md`; the reasoning carries over
unchanged to an engine that 0042 made an independently released deliverable consumed over a
version-pinned contract, and 0049 makes it timely by putting a Rust implementation about to be built
against the specification rather than against its own reading of it. Options: A a pure,
host-independent first slice authored from the specification (chosen); B wait for the engine and derive
vectors from its behavior (rejected — inverts the direction of derivation, encoding one
implementation's reading, bugs included, as the cross-implementation contract); C fold the vectors into
`vocabulary.json` (rejected — a registry and a vector set have different schemas and different jobs,
and merging them makes the registry's derivation rule unstatable); D rely on Section 13.1 plus each
implementation's own tests (rejected — the status quo whose weakness prompts the decision). Four
functions, 49 vectors, all pure over their inputs: `match_edge` (18) and `validate_policy` (18) carry
the slice because three of Section 13.1's eight bullets are about the action-policy machine;
`resolve_base` (9) because longest-prefix-wins with a required empty-prefix default reads simple, is
easy to implement as first-match, and fails as a silently wrong base branch; and
`exit_code_for_status` (4) because 0049 recorded a live hazard for exactly that mapping — the wrapper
layer offered as a design seed numbers `0`/`2`/`10`/`64` against Section 8.3's `0`/`10`/`20`/`2`,
colliding on `2` and `10` with different meanings. `proto_class` is **deliberately omitted**: it is a
lookup over the Section 4.3 registry that `vocabulary.json` already is, so a file would restate it with
no assertion added, and `match_edge` exercises it in composition by supplying a trigger token rather
than its class — as Section 12.1's algorithm does. Conventions are reused, not re-invented: 0048's
success-or-error union, and the Symphony corpus's "keys absent from `expect` are unconstrained" rule,
which earns its keep immediately by letting a vector pin what the specification fixes without pinning
what it leaves open. No `profile` field, because 0043 deferred engine conformance rather than defining
profiles. Authoring surfaced three gaps, all recorded rather than guessed: an unmatched **lifecycle
position** has no stated default (Section 5.4 fixes the unmatched-outcome and unmatched-signal cases
only); the **class form of a concrete task-state event** is undefined, `needs_help` not being a proto
class; and **configuration errors carry no reason token**, so a caller can tell that a policy was
refused but not why without parsing `message` — the most substantive of the three for an engine whose
contract is otherwise built on stable tokens. Reconsider the pure-only boundary once a fixture harness
is cheap, at which point the `ship`/`land` sequences, plugin and checkout-mode behavior, message
formulation, and hook execution become a second slice. Depends on 0049, 0051; relates to 0046 (the
discipline and shape it reuses), 0048 (the error-vector convention), 0043 (why there is no profile
field), and 0052 (whose `notify` disposition one validation vector pins). Accepted and applied:
`conformance/vcsx/vectors/` (4 files, 49 vectors) and an extended `conformance/vcsx/README.md` are
created, and `VCSX-SPEC.md` Section 13.1 gains the corpus pointer that mirrors what 0046 added to
`SPEC.md` Section 17.

## 0054 — An unmatched lifecycle position proceeds

**State:** Accepted
**Folder:** [decisions/0054-unmatched-lifecycle-position/](decisions/0054-unmatched-lifecycle-position/)

Resolves the first of three gaps 0053 surfaced. `VCSX-SPEC.md` Section 5.4 fixed the unmatched
behavior of two of the three trigger kinds — a signal is a benign no-op, an operation outcome MUST be
fail-safe with a built-in default per proto class — and said nothing about a lifecycle position with no
edge, while Section 5.3 established only the negative that a position takes no class fallback. The
silence sat on the ordinary case: Section 4.1 defines four required positions and a policy binds
whichever it needs, so under a reading that generalized the fail-safe rule the minimal policy in the
corpus, which binds `before:commit` alone, could not run. Options: A a benign no-op, the operation
proceeds (chosen); B fail-safe as for an operation outcome (rejected — makes every policy that does not
bind all four positions unrunnable, contradicting Section 6.5's own examples); C a configuration error
requiring every position to be bound (rejected — same objection moved earlier, converting an offered
interposition point into an obligation). The reasoning worth recording is the distinction rather than
the outcome, the outcome being the only workable one: **an operation outcome is a result that must be
disposed of**, and dropping it strands a flow, which is what that bullet already says; **a lifecycle
position is an offered interposition point**, and declining to interpose strands nothing because the
operation it gates still runs. The same distinction explains the negative Section 5.3 already stated —
a position has no class fallback because there is no outcome to classify — so the edit adds the rule
*and* its rationale, to keep a later reader from re-deriving the generalization and reaching Option B.
Reconsider if a position were ever introduced whose whole purpose is to force a decision, since such a
position would not be an interposition point in this sense and would belong with the fail-safe
outcomes. Depends on 0053; relates to 0030 and to 0055, its sibling clarification. Accepted and applied
to `VCSX-SPEC.md` (Section 5.4) and the corpus (`match-edge.json` asserts the outcome and gains
`unbound_lifecycle_position_proceeds`).

## 0055 — Signals are matched exactly; the `#class` fallback is result-only

**State:** Accepted
**Folder:** [decisions/0055-signals-matched-exactly/](decisions/0055-signals-matched-exactly/)

Resolves the second gap 0053 surfaced. `VCSX-SPEC.md` Section 5.3's signal ladder fell back to "(for a
`#class`-shaped event token such as `task:#needs_help`) its class form", which is not resolvable:
`needs_help` is not one of the three proto classes, so the token is not a `#class` form in the sense
the same section uses two bullets earlier, and if it is instead the class form of some concrete task
event, no concrete-to-class mapping is defined anywhere. Section 12.1's `ladder()` carried the same
undefined `class_form` step. Two facts bound the resolution: a proto class is a property of an
*operation result* (Section 4.2 defines it over `<op>:<reason>`), so a consumer-raised signal has none
and the machinery has nothing to compute over; and Section 7.3 assigns the task model to the driver —
"`vcsx` only consumes the resulting events" — so defining a class taxonomy for task events would have
the engine specifying a subsystem it explicitly does not own. Options: A drop the rung, signals match
exactly (chosen); B define an event-class vocabulary for task events (rejected — invents a second class
system and forces the engine to fix a concrete event vocabulary, the coupling Section 7.3 avoids);
C let the consumer declare each signal's class form (rejected — adds schema and a validation surface at
the consumer boundary for a mechanism with no current use, and makes matching depend on per-invocation
data rather than the policy). Choosing A makes Section 5.3's three bullets consistent for the first
time: a lifecycle position has no class form because there is no outcome to classify (0054), a signal
has none for the same reason, and a typed result has one because it is the only trigger kind carrying a
class — what read as an inconsistent special case was the ladder reaching for a property only one
trigger kind has. `task:#needs_help` keeps its spelling, so no anchor changes, but the `#` is now
documented as naming a *condition across tasks* — raised once when any task needs human help — matching
`VCSX-CONTRACT.md` Section 8, where the task surface's events are the two aggregate ones rather than a
per-task stream. The accepted cost is that a policy reacting to several task conditions binds each
token, which is the cost already accepted for the three agent milestone signals; and unlike operation
reasons, where Section 8.5 lets a `MINOR` add tokens an existing policy must absorb, the signal
vocabulary is raised by the consumer, so a consumer never surprises its own policy — the `#class`
fallback exists to absorb *upstream* additions, and signals have no upstream. Reconsider if a
consumer's signal vocabulary grew large enough that grouping became a real need, or if the engine
began raising signals of its own. Depends on 0053; relates to 0030, 0031, and 0054. Accepted and
applied to `VCSX-SPEC.md` (Sections 5.1, 5.3, 12.1), the vocabulary registry, and the corpus.

## 0056 — A configuration-error reason registry and the `usage_or_config` status

**State:** Accepted
**Folder:** [decisions/0056-configuration-error-reason-registry/](decisions/0056-configuration-error-reason-registry/)

Resolves the third and most substantive gap 0053 surfaced, and a second defect found while resolving
it. `VCSX-SPEC.md` Section 6.10 enumerated five refusal conditions and Section 8.3 mapped them to exit
`2` while naming no token for any of them, leaving the one error class a caller most needs to act on as
the only one requiring prose parsing — a sharp inconsistency in an engine whose contract is otherwise
built on stable tokens, Section 4.3 giving every operation outcome a registry reason and Section 8.3
stating the same goal of branching "without parsing". The second defect: Section 8.2 defined `status`
as three proto-class values while Section 8.3 defined four exit codes, so **no `status` corresponded to
exit `2`** — an engine following Section 8.2 literally must report a refused policy as `error`, which
Section 8.3 maps to `20`, and the two sections could not both be satisfied. Options for the cause:
A a configuration-reason registry carried in the existing `reason` field with null `op`/`class`
(chosen); B leave it in `message` (rejected — the status quo the gap describes); C a structured
`errors` array (rejected — a second, differently-shaped error channel in an envelope whose virtue is
one shape). Options for the status: D a fourth value `usage_or_config` (chosen — makes the mapping
total and keeps Section 8.3's mirror property literally true); E report `error` and derive exit `2`
from the reason (rejected — breaks branching on status alone, the property Section 8.3 exists for).
Nine tokens: `unknown_trigger`, `unknown_action`, `unknown_operation`, `unknown_hook`,
`duplicate_edge`, `duplicate_transition`, `base_unresolvable`, `set_state_unbound`,
`version_floor_unmet`. Section 6.10's compound first condition is split into four rather than one
`unknown_name`, because the four are found at different points and repaired differently; the subtle
boundary is stated explicitly, since Section 6.5 recognizes a trigger only as an `op:reason` form *over
a known operation*, making a bad operation in a trigger `unknown_trigger` while `unknown_operation` is
the `run_op` argument case. **Configuration reasons carry no proto class** — a refused policy has no
operation result to classify — which also settles absorption: a new configuration reason arrives in a
`MINOR` not through the `#class` fallback, which has nothing to fall back on, but through the
`usage_or_config` status, which does not change. The status fix is not scope creep: the tokens are
carried in an envelope whose `status` had no value for the case producing them, so defining them alone
would have yielded a registry no conforming engine could report — and Section 8.5 makes both surfaces
major-stable, so fixing it before 0049's engine exists costs nothing and later would not. Accepted
cost: one new `Implementation-defined` site, for which reason is reported when several conditions hold,
since no useful total order exists and inventing one would be worse than documenting the choice; the
corpus deliberately does not exercise it, every failing vector holding exactly one condition.
Reconsider Option C if one-reason-at-a-time repair loops proved the dominant cost of authoring a
policy. Depends on 0053; relates to 0044 (whose `Engine Invocation Failures` class covers the refusal
this makes legible) and 0051. Accepted and applied to `VCSX-SPEC.md` (Sections 6.10, 8.2, 8.3, 8.5,
13.3), the vocabulary registry, the corpus, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0057 — Universal operation reasons: `blocked`, `failed`, `unsupported`

**State:** Accepted
**Folder:** [decisions/0057-universal-operation-reasons/](decisions/0057-universal-operation-reasons/)

Resolves parts 1a and 1b of issue #2, which are one defect seen twice: `VCSX-SPEC.md` Section 4.3's
registry is enumerated per operation, while Sections 6.6 and 9.3 state rules quantified over
operations. Section 6.6 surfaces a blocking `before:*` hook "as the operation's `blocked`/`failed`
reason", but only `commit` had the pair — `create_pr` could express a gate block at neither class
though Section 10.4 scans its title and body *during* the operation, and `push` had to borrow
`push:rejected`, which says the remote refused. `merge:blocked` was worse than missing: the gate word
at class `error` where `commit:blocked` carries it at `needs_caller`, so one `#needs_caller → escalate`
edge escalated a blocked commit and failed a blocked merge, with nothing saying whether that was
deliberate. Section 9.3 has the same shape: an undeclared capability "yields an `error`-class result",
and neither Section 4.3 nor Section 6.10 named a token — unsatisfiable for `status`, `diff` and `pull`,
which had **no `error`-class reason at all**. The general form is what makes it a defect: Section 4.1
lets an engine define additional operations, so the operation set is open while the registry was
closed, and any rule stated over all operations was going to outrun an enumeration. Options: A three
reasons defined for **every** operation, stated once (chosen); B add the missing tokens one at a time,
as the issue proposed (rejected — closes today's gap and leaves the registry closed against an open
operation set, and does not reach `status`/`diff`/`pull`); C a separate `<op>:gate_blocked` namespace
(rejected — contradicts Section 6.6's own wording and forces a rename of `commit:blocked`, trading one
rename for another). For the `merge:blocked` collision: D the gate meaning wins and the forge refusal
is renamed `merge:rejected`, keeping class `error` under a name parallel to `push:rejected` (chosen);
E merge alone has no `needs_caller` gate reason (rejected — a `before:merge` gate returning
`needs_caller` would surface at `error`, contradicting Section 6.6's class-preserving surfacing at
precisely the position a repository is most likely to gate); F one token whose class varies with its
origin (rejected — destroys the `#class` fallback for that reason, the one property Section 8.5 freezes
for a whole `MAJOR`). So: `failed` (`error`) and `unsupported` (`error`) for every operation, `blocked`
(`needs_caller`) for every gated one, and the registry gains a property now stated outright — **every
operation has at least one `done` and at least one `error` reason**, so an `error`-class result is
always expressible, including for the read-only ones, whose omission was an artifact of enumerating
outcomes an engine had already thought of. The answer to the issue's question about `merge:blocked` is
that it was an accident *of naming*: the class was right for the meaning the token carried, and the
word was wrong. `capability_unsupported` joins Section 6.10's registry for the validation-time half of
Section 9.3, keeping 0056's boundary intact. Section 12.2's `ship` loop needed a matching fix, the kind
of defect that only shows once a class gains a member: it named the two `needs_caller` push reasons
that existed and broke out otherwise, so a gate-blocked push would have fallen through to `create_pr`;
it now returns any non-`done` result through `result_of`. Accepted costs: 45 normalized registry
entries where there were 27, and a redefinition of a major-stable token, affordable only because
decision 0049's engine is not written — the same reasoning 0056 used. Left open deliberately and
recorded: Section 6.6 requires a blocking hook to return "a stable reason" and the envelope's `reason`
carries the *operation's* token, so where the hook's own reason is exposed remains unspecified — a
question about the envelope, not the registry. Relates to 0051, 0056, and 0049; sibling of 0058.
Accepted and applied to `VCSX-SPEC.md` (Sections 4.3, 6.6, 6.10, 9.2, 9.3, 10.4, 12.2, 13.1), the
vocabulary registry, and the corpus.

## 0058 — `diff(base)` is a required VCS backend capability

**State:** Accepted
**Folder:** [decisions/0058-diff-required-vcs-capability/](decisions/0058-diff-required-vcs-capability/)

Resolves part 1c of issue #2. `VCSX-SPEC.md` Section 4.1 makes `diff` a required operation and Section
8.1 an entry point a driver may call directly, while Section 9.1's required VCS backend capabilities do
not include it; `ahead_behind(base)` returns counts, not content, so nothing in the specified plugin API
produces a branch delta and a conforming engine could not implement a required operation through the
required interface. Every other operation traces to a capability, which is what marks this an oversight
rather than a design. Options: A add `diff(base)` → `diff:*` to the required list (chosen); B read
"Required capabilities" as a minimum and let each engine add its own (rejected — the specification is
not literally wrong, but the capability's name, signature, and result token would then be chosen
independently by every engine, which Section 14 calls a contract change and requires to be spelled
identically); C widen `ahead_behind(base)` to return content (rejected — overloads a capability whose
value is that it is cheap and countable, and forces a diff whenever `status` asks for counts); D demote
`diff` to an OPTIONAL capability-gated operation (rejected — a backend that cannot produce a delta is
not one the engine could drive, and demoting a required operation would fix the wrong end). The
reasoning worth keeping is the invariant rather than the bullet: **every required operation MUST be
realizable through the required capabilities**, which is what Section 9.1 was already trying to say and
what a reviewer can check when the next operation is added. The issue's minimum-versus-maximum question
is answered outright rather than left to inference — the list is the minimum every backend MUST provide,
and an engine defining an additional operation MUST document the capabilities it requires in its
Conformance Statement, so an engine-specific capability is visible as engine-specific rather than
mistaken for shared surface. No reason-token consequence: 0057 gives `diff` its `error`-class reasons
along with every other operation. Reconsider if a checkout mode appeared whose delta could not be
expressed against a single resolved base, which would revisit the signature rather than the
requiredness. Relates to 0057 and 0040. Accepted and applied to `VCSX-SPEC.md` (Sections 9.1, 13.3) and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0059 — A parked flow is `needs_caller` with the `intervention` need

**State:** Accepted
**Folder:** [decisions/0059-park-invocation-outcome/](decisions/0059-park-invocation-outcome/)

Resolves issue #3. `VCSX-SPEC.md` Section 5.2 defines `park` as "stop the flow and hold for intervention
without failing it" and Section 6.5 lets a repository write `do = "park"` on any edge, but Section 8.2
offered four invocation statuses and mapped none of them to a parked flow. Elimination reached one — not
`ok` ("all steps `done`"), not `error` (`park` does not fail the flow), not `usage_or_config` (reserved
for a run in which the policy did not run) — but by argument rather than by anything stated, and Section
8.3 turns status into an exit code, so two conforming engines could return different exit codes for the
same run of the same correct policy. Implementing it surfaced the sharper half: Section 8.2 had no
*shape* for the parked envelope either. `op`/`reason`/`class` were "the decisive operation result",
nullable only "for a clean `ok` with no decisive operation", while a parked flow's last result is
typically `done`-class — a `push:ok` on the way to a park edge — so reporting it would claim an operation
asked the caller something when none did, and would put a `done`-class reason under a `needs_caller`
status. And since `escalation` is present *exactly* when the status is `needs_caller`, a parked flow must
carry a Section 8.4 `need`, of which three name a remedy a park does not have. Options: A `needs_caller`
with a new `intervention` need and a null `op`/`reason`/`class` (chosen); B `human_review` covers it
(rejected — it collapses a hold into the token Section 12.2 already emits for `push:pr_closed`, and
Section 5.5 would then have a conforming driver bind a resolver and *resume* a parked flow, so rescuing
it costs a carve-out in Section 5.5, trading a token for an exception); C `needs_caller` with no
escalation, relaxing "exactly when" (rejected — the reading the filing implementation took, and it adds
no token, but it makes a parked flow indistinguishable from an engine bug that dropped the escalation,
against the "reported, never silently dropped" property Section 5.4 rests on); D a fifth invocation
status (rejected — Section 8.5 freezes the status values and the exit-code mapping for a whole `MAJOR`,
which is a steep price to avoid a `MINOR`-compatible token); E report the parked-at trigger when its
class agrees with the status (rejected — a consumer must handle null regardless, since a park at a signal
or a lifecycle position has nothing to report, so it adds a case without removing one and gives two parks
different shapes). What makes the token load-bearing rather than cosmetic is that **`intervention` is the
one need no front-end resolves**: `park` names a hold, not a request, so Section 8.4 forbids binding a
resolver to it or resuming the flow on it, and that single restriction is what keeps Section 5.5's claim
that `escalate` is the *single* point of front-end divergence true — both front-ends do the same thing
with a park. The null envelope is then derived rather than asserted, because Section 8.2 gains the
invariant it only implied: where `op`/`reason`/`class` are non-null, `class` is the class `status`
reports. That invariant is worth more than the case that motivated it — it is what a reviewer checks the
next time a terminal action is added. Two adjacent holes are closed on the same path: escalation's `op`
is stated nullable, naming the two cases (at a signal, and at a lifecycle position where the gated
operation has not run), a defect `blocked → escalate("human_review")` already had before `park`. Left
open deliberately and recorded: `fail`'s mirror-image envelope — an explicit `do = "fail"` on a
`done`-class trigger yields `error` with no `error`-class result — which cannot be settled before what
`fail(reason)`'s argument *is* has an answer; and issue #4's bounded traversal, which lands on this
invariant but asks its own questions. Reconsider if a front-end appears with a legitimate automated
response to a park, at which point Option E's finer envelope would start to pay for itself. Relates to
0044, 0056 (the last invocation status found missing), and 0057 (the same
rule-outruns-its-enumeration shape, one section over). Accepted and applied to `VCSX-SPEC.md` (Sections
5.2, 5.5, 8.2, 8.4, 13.1), the vocabulary registry, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0060 — A conforming executor bounds the flow, and an exhausted bound is `needs_caller`

**State:** Accepted
**Folder:** [decisions/0060-bounded-flow-traversal/](decisions/0060-bounded-flow-traversal/)

Resolves issue #4. `VCSX-SPEC.md` Section 5.2 makes a `run_op` result itself a trigger — "a policy is a
graph, not a flat list" — and Section 12.2 writes `ship` with an unbounded `loop:` that retries `push`
after each `integrate`, with no iteration cap, no cycle detector and no deadline anywhere in the
document. The issue judged this the mildest of the three it filed, since "two engines with different
bounds agree on every policy that terminates". Working it narrowed one half of that framing and widened
the other. **Wider:** the hang is reachable without a bad policy. `push:non_fast_forward → integrate →
retry push` is the built-in routing Section 12.2 itself prescribes, so a base branch that receives a
push between every one of ours live-locks a correct policy over a correct backend. **Narrower:** a cycle
detector — the safeguard the issue names — is the wrong mechanism in either form, since the
`push`/`integrate` cycle *is* the built-in routing (so refusing a cyclic graph refuses Section 12.2) and
the second time the base moves is ordinary (so stopping at a repeated `(trigger, edge)` pair aborts a
flow about to converge). What separates a converging flow from a looping one is how many operations it
takes, not whether it revisits an edge. Options: **A** MUST bound by a `run_op` count with a stated
floor, exhaustion yielding `needs_caller` with a new `flow_exhausted` need (chosen); **B** leave
bounding to the engine and publish the choice in Section 13.3, the issue's stated minimum (rejected —
optional bounding leaves "the engine hangs" conforming, which an autonomous consumer cannot absorb, and
an `Implementation-defined` *outcome* documents the disagreement rather than removing it, since Section
8.3 turns status into an exit code and Section 8.5 freezes the mapping for a `MAJOR`); **C** reuse
`intervention` (rejected — decision 0059 nulls `op`/`reason`/`class` for a hold, so `need` is the only
structured field left and a consumer could not tell a policy that asked to hold from an engine that
stopped one, the same objection 0059 raised against `human_review` covering a park); **D** `error`
(rejected — Section 4.2's `error` is "the operation failed" and none did; it also drags in the `fail`
envelope 0059 left open and invites a consumer to retry a flow whose defining property is that
repeating it unchanged changes nothing); **E** `usage_or_config` (rejected — Section 8.2 reserves it for
a run in which the policy did not run, and non-termination is not statically detectable, so Section 6.10
cannot catch it either); **F** a wall-clock deadline as the required bound (rejected — not
deterministic, so no vector can assert it, and the run's wall clock already belongs to the consumer;
kept as a permitted *additional* bound with the same disposition); **G** a repository-configurable bound
(rejected for now — it answers a retry-policy question, not the termination question, and is recorded as
the surface it would land on). The unit carries the decision: **`run_op` is the only action whose result
re-enters the machine** — `run` reaches it through the gated operation's `<op>:blocked`/`<op>:failed`
reason and an `after` hook does not block, `create_task`/`set_state`/`notify` are consumer-effected
intents emitted once, and `escalate`/`park`/`fail` are terminal — so bounding that count is a
termination proof for every policy the schema can express rather than a heuristic that usually catches
loops, and the next action added can be checked against it by asking only whether its result re-enters.
The floor (at least 64 dispatches, roughly an order of magnitude above the built-in sequences' worst
case) is what makes the issue's own portability claim true rather than hoped-for: with no floor an
engine whose bound is three conforms and agrees with nobody. `flow_exhausted` and `intervention` are
both holds — no automated party can move the flow, so no front-end binds a resolver or resumes — and
Section 8.4 now states that as a property of the pair rather than of a single token; they stay distinct
because a park is the policy working as written while an exhausted flow says the graph does not converge
or the remote outruns the engine. The envelope needs no new rule: decision 0059's invariant already
nulls `op`/`reason`/`class` where nothing is decisive, and 0059's own record anticipated this case.
Left open: `fail`'s envelope, still, and the configurable bound. Reconsider if a consumer appears that
can legitimately resume an exhausted flow, at which point `flow_exhausted` would want a resume token
rather than a bare hold. Relates to 0059 (whose invariant this builds on and whose `intervention`
carve-out it widens), 0056, 0057, and 0044 (whose `Engine Invocation Failures` class covers only runs in
which the policy did not run). Accepted and applied to `VCSX-SPEC.md` (Sections 5.6, 8.2, 8.4, 12.2,
13.1, 13.2, 13.3), the vocabulary registry, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0061 — `pull` preserves the work branch's committed history

**State:** Accepted
**Folder:** [decisions/0061-pull-preserves-history/](decisions/0061-pull-preserves-history/)

Resolves issue #8. `VCSX-SPEC.md` Section 4.1 defines `pull` as "update the local work branch from its
remote counterpart" and Section 4.3 gives it `pull:ok` and `pull:conflict`; a `conflict` means the
update reconciles a divergence, and the document never says whether it merges or rewrites, so an engine
choosing either conformed. The issue routes the defect through Section 11's never-force rule: a
rebasing `pull` leaves the branch non-fast-forward, Section 12.2 retries through `integrate`, and the
flow runs to decision 0060's bound. Working it moved that argument both ways. **Narrower:** on git the
chain does not reach `push:non_fast_forward` at all — `git pull --rebase` replays onto the branch's own
remote counterpart, so the result descends from the remote tip and the next push is a fast-forward.
**Wider:** on jj, which the issue names in passing, the rewrite is a dead end rather than a loop, since
jj rewrites published commits as an ordinary operation and publishing one needs the force push
Sections 9.1 and 11 forbid without exception — the identical repository state ships on git and does not
ship on jj, which is Section 2.1's cross-checkout-mode goal failing. **Wider again, and decisive:** the
*required operation set cannot finish a rebase's conflict*. `pull:conflict` is `needs_caller`,
`resolve_conflicts` names the need, Section 5.5 has the caller resolve and re-invoke, and Section 12.2
then dispatches `commit` — which finalizes a merge, a single conflicted state resolved once, and not a
sequential replay that stops per commit and needs a resume step Section 4.1's required set does not
contain. So the answer follows from the operation list rather than from either VCS's behavior, the shape
decision 0060 used to pick its unit. A rewriting update also fights `integrate`, which Section 4.1
requires to preserve recorded conflict resolutions: linearizing drops the merge those resolutions were
recorded against. Options: **A** state that the counterpart is merged in and no commit already on the
branch is rewritten, dropped or re-parented, with the no-rewrite half stated once beside Section 11's
never-force rule (chosen); **B** forbid the rewrite without naming the reconciliation, the issue's
literal ask (rejected — it leaves fast-forward-only conforming, under which a divergence has no
reconciliation to attempt, so `pull:conflict`'s reachability still varies by engine); **C** a
repository-configurable `[engine] pull_strategy` (rejected — reconciliation is not a Way of Working, and
it would offer a mode whose conflict the operation set cannot finish); **D** `Implementation-defined`
with a Section 13.3 row (rejected on the line 0056, 0059 and 0060 hold — it covers mechanisms, never
what a caller branches on, and here it would leave what the repository *contains* engine-dependent);
**E** permit the rewrite and add `continue`/`abort` operations (rejected — it grows the required
operation set for a strategy nothing asks for and still collides with never-force on jj; recorded as the
surface a future rebase mode needs); **F** fast-forward-only `pull` (rejected — it makes `pull:conflict`
a dead token, and a work branch legitimately diverges when a forge commits a review suggestion or
presses "update branch"). The invariant is worth more than the clause it was written for: Section 11
offered never-force as a scope guarantee, which is only sound if nothing the engine does creates a state
requiring a force — stating that no operation rewrites a commit on the work branch makes the rule one
an engine can always keep, and an operation added later is checked against it by asking only whether it
can rewrite a published commit. It is scoped to updates of the *work branch*, and Section 11 says so:
a `rebase` or `squash` merge strategy (Section 6.8) rewrites commits but writes the result to the base,
so the invariant does not narrow the strategies a repository may configure. `integrate` needs no clause
of its own, agreeing with the issue: "a merge/update-branch" and its recorded-resolution requirement
already name a history-preserving update.
No token is added, removed or reclassed, so the vocabulary registry is unchanged. Left open: no built-in
sequence dispatches `pull` at all (`ship` reconciles through `integrate`), so its recovery path is
specified and exercised nowhere in the reference algorithms; and a `pull` whose remote counterpart does
not yet exist, which belongs with the questions issue #9 bundles. Reconsider if a backend appears whose
only update is a rewrite and which can publish one without a force, at which point the merge requirement
could relax to the weaker append-only-published-history invariant. Relates to 0060 (whose bound the
issue's argument routes through, and which this decision finds is not the failure mode), 0058 (which
last changed Section 9.1's capability list), and 0057 (whose argument for changing settled surface
before an implementation exists this reuses). Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3,
9.1, 11, 13.1, 13.2) and `conformance/vcsx/README.md`.

## 0062 — The remote is named in `[engine]` and supplied to the capabilities that touch it

**State:** Accepted
**Folder:** [decisions/0062-engine-remote-selection/](decisions/0062-engine-remote-selection/)

Resolves part 1 of issue #9. `VCSX-SPEC.md` Section 9.1 gave the VCS backend `push(work_branch)` and
`pull(work_branch)`, neither carrying a remote, and Section 6.2's `[engine]` configured `version_floor`,
`vcs` and `forge` and no remote name — so a backend that talks to a remote at all had to pick one and
nothing said which. The consequence is a conformance hole with side effects: two engines running the
same `repo.policy.toml` over the same checkout can push a repository's work branch to two different
places while both conform, and both report `push:ok`. Options: **A** an OPTIONAL `remote` in `[engine]`,
resolved once per invocation and passed to the capabilities that take one (chosen); **B** a sentence
saying the remote is the backend's to determine, published under Section 13.3 (the issue's second offer;
rejected — it costs nothing and leaves the remote *unconfigurable*, so a repository whose work branches
go to a fork cannot say so, and Section 6.2's own rationale that "which code host a repository targets
is repository-owned" applies with equal force to which remote at that host); **C** name `origin`
normatively (rejected — a git convention in a document that names no VCS's conventions normatively, and
Section 3.3 already admits a jj secondary workspace where it names nothing); **D** derive it from the
work branch's upstream binding (rejected on the filing implementation's own reasoning — the work branch
is engine-derived per Section 6.3 and MAY be absent at the first push, so the configuration read is
exactly the one that does not exist); **E** a per-invocation `remote` argument (rejected — it relocates
the divergence rather than closing it, and Section 6.2 puts backend *selection* on the repository's
side). The reasoning worth keeping is not the key but the invariant it makes checkable: **the
capabilities that take a `remote` are exactly the version-control operations Section 3.2 places
host-side, and every other Section 9.1 capability is local to the checkout** — it acquires nothing over
the network and needs no credential. That one sentence answers which operations need a remote, which
need a credential, and which a consumer may run in-sandbox, and it is what a reviewer applies to the
next operation added. It also forced a latent defect out: Section 3.2's host-side list omitted `pull`,
which Section 4.1 defines as updating "from its remote counterpart" — the invariant would have been
false the moment it was written, and nothing had depended on that list being complete until now.
Passing the remote rather than letting the backend read the policy follows the document's existing habit
with the other configuration-resolved value: the base is resolved by the engine and reaches the backend
as a parameter, so a `remote` key with no way to reach the backend would repeat this issue's own
complaint — the answer settled somewhere other than where the implementer is reading. That is decision
0058's correction restated: every value an operation needs, and that the engine resolves, MUST reach the
backend through a capability signature. A remote name the checkout does not carry is an operation
`failed` (Section 4.3) rather than a configuration error, because Section 6.10 is judged from the policy
file alone and a remote's existence is a property of the checkout. Left out of scope: separate read and
write remotes for a fork-and-upstream arrangement, which is the shape to reach for if the need appears.
Reconsider then. Relates to 0058 (the same correction one operation over), 0064 (which says what
`integrate` does with the remote it now receives), and 0061. Accepted and applied to `VCSX-SPEC.md`
(Sections 3.2, 6.2, 9.1, 13.1, 13.3) and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0063 — `commit` captures the working tree, and `is_dirty()` is its predicate

**State:** Accepted
**Folder:** [decisions/0063-commit-captures-working-tree/](decisions/0063-commit-captures-working-tree/)

Resolves part 2 of issue #9. `VCSX-SPEC.md` Section 4.1 defined `commit` as "create a commit from the
working tree" and offered no `stage` operation a driver could call first; Section 12.2 then guarded it
with `if worktree_dirty()`. Two things went unstated: whether `commit` is itself responsible for putting
working-tree content into the commit, and whether content the VCS has never recorded counts toward that
guard — the same question asked of Section 9.1's `is_dirty()`. The phrasing already pointed one way, and
the issue is right that pointing is not enough, because the failure is silent and asymmetric: an engine
reading "from the working tree" as "from whatever was selected out of band" conforms to the letter, and
an agent whose entire change is new files is then reported clean, skips the commit, and ships an empty
branch with every step `done`-class and `create_pr:created` at the end. The reverse mistake is loud — a
commit that captured too much fails review. Options: **A** `commit` captures the working tree in full
and `is_dirty()` is true exactly when a `commit` would capture something (chosen); **B** a `stage`
operation and a `before:stage` position (rejected — it models a two-step workflow the engine has no way
to drive, since nothing in Sections 4.1 or 5.2 could decide what to select, so the argument would come
from the caller, which Section 6.3 declines for branches on the same reasoning; and it inverts the
failure so the default becomes an empty commit); **C** leave it, the phrasing points that way (rejected
— Section 12.2 makes the predicate decide whether the commit runs *at all*, so a merely probable reading
is not enough for a branch that silently ships nothing); **D** `Implementation-defined` (rejected — two
engines would produce different commits from the same worktree and `commit:nothing_to_commit` would mean
something different on each, which is the one thing a reason registry cannot afford). The reasoning
worth keeping is the second half rather than the first. That `commit` commits the working tree is a
policy choice, defensible either way in isolation; that **the guard and the operation share one
predicate** is not — it is what makes `if worktree_dirty()` a correct guard rather than an independent
opinion about the same worktree. Stated separately they drift into skipped work; stated as one predicate
the skip is provably benign, because the only tree the guard declines to commit is one a commit would
have found empty. That framing also settles the ignored-content question with no second rule: ignored
content is not dirty because a commit would not capture it, so if a repository changes what its VCS
ignores, both halves move together. `commit:nothing_to_commit` keeps its `done` class and is now the
only way the flow reaches a commit with nothing to do. Reconsider if a consumer needs to commit a subset
of a worktree, which would need a selection argument the engine trusts — a larger change than relaxing
this predicate. Relates to 0057 and 0061 (whose `pull:conflict` is finalized by a `commit` that now
demonstrably captures the resolved tree, including any file the resolution added). Accepted and applied
to `VCSX-SPEC.md` (Sections 4.1, 9.1, 12.2, 13.1).

## 0064 — `integrate` resolves the base against the remote; the read-only operations do not

**State:** Accepted
**Folder:** [decisions/0064-integrate-base-from-remote/](decisions/0064-integrate-base-from-remote/)

Resolves part 3 of issue #9. `VCSX-SPEC.md` Section 4.1 defined `integrate` as bringing "the resolved
base" into the work branch and Section 6.4 resolves the base to a *branch name*; whether that name meant
the branch as the checkout holds it or as the remote holds it was not stated, and the same question
applied to `ahead_behind(base)` and `diff(base)`. The document already decided it, in two places that do
not mention each other: Section 12.2 routes `push:non_fast_forward` to `integrate` and retries, a loop
that converges only against the remote's copy; and Section 4.1 marks `status` and `diff` "Read-only",
which acquiring the base is not. Decision 0060 sharpened the stakes rather than creating them — before
the flow bound a stale-base `integrate` produced an engine that spun, after it the same engine
terminates and reports a plausible `flow_exhausted` ("the graph does not converge or the remote outruns
the engine") when the truth is that it never fetched. The failure got quieter, not louder. Options:
**A** remote for `integrate`, the checkout's copy for `ahead_behind` and `diff` (chosen); **B** the
checkout's copy for everything (rejected — Section 12.2's built-in routing cannot converge, so the
document's own default policy would be wrong for the case it exists to handle, and rescuing it means a
fetch step every policy must remember to route); **C** the remote for everything (rejected — it makes a
read-only operation credentialed, so a consumer running `status` in-sandbox could not run it at all, and
makes the cheapest operation in the set the one that touches the network); **D** make it configurable
(rejected — one answer makes the built-in routing converge and the other does not, so a key whose wrong
value is never correct is a defect surface, not a policy surface); **E** state it for `integrate` only
and leave the read side to "Read-only" (the issue's own position; rejected as insufficient — that word
settled it before the issue was filed and the issue was filed anyway, by someone who derived the answer
and still wanted it said). The reasoning worth keeping is that **the asymmetry is not a compromise
between freshness and cost — it follows from Section 3.2's trust split, and the operations divide
exactly along it**: an operation that acquires the base is host-side because it needs the network and a
credential, and one that does not can run in-sandbox. That is also what makes Option C's cost visible —
a fetching `status` does not merely add latency, it moves the operation across the boundary Section 3.2
exists to let a consumer split a policy along. The staleness this leaves on the read side is stated
rather than hidden (a caller needing current figures runs `integrate` first); it is the price Section
4.1 already pays by marking the operation read-only, so nothing an engine *does* changes — only whether
an implementer has to guess. `pull` needs no clause: Section 4.1 already says "from its remote
counterpart" and 0061 fixed how it applies what it finds. Reconsider for a checkout mode where the
local/remote distinction has no cost, or a consumer actively harmed by stale `ahead`/`behind`, which
would argue for an OPTIONAL fetching variant rather than for changing this one. Relates to 0062 (which
supplies the remote), 0060 (whose bound a stale-base `integrate` now trips), and 0061. Accepted and
applied to `VCSX-SPEC.md` (Sections 4.1, 9.1, 12.2, 13.1).

## 0065 — Invocation preconditions are `usage_or_config`, with a registry of their own

**State:** Accepted
**Folder:** [decisions/0065-invocation-preconditions/](decisions/0065-invocation-preconditions/)

Resolves part 4 of issue #9. Decision 0057 made `failed`, `blocked` and `unsupported` universal, closing
the case where a capability fails *during* an operation; it left the case where one fails *before any
operation runs*. Section 6.3 has the engine derive the work branch from the pattern and the caller's
identity, which means calling a Section 9.1 capability during setup, and three real states fail there: a
checkout with no current branch, a derived name that is not legal for the VCS, and a malformed commit
identity, which only the backend can judge because Section 10.1 keeps identity opaque to the engine.
There is no operation to attach `<op>:failed` to — Section 8.1's entry points are the front-ends and the
operations, and this is before the first of them. Answering it exposed two adjacent holes: the
`usage_or_config` status promises usage *and* configuration and only configuration ever had a registry
(a malformed caller identity is the plainest usage error the contract can have, and had no token); and
Section 6.3's `branch_pattern` was listed with no `OPTIONAL` marker and no default, so the configuration
state in which a detached HEAD is fatal is one the document did not admit exists. Options: **A**
`usage_or_config` (exit `2`) with a precondition registry in a new Section 8.6 (chosen); **B** `error`
(exit `20`) with a null `op` (rejected — it reports a failure with no operation that failed, which 0059
refused for exactly this shape, and `20` invites a retry against a state no retry changes, while `2`
says "the policy did not run; fix the invocation"); **C** fold the reasons into Section 6.10 (rejected —
6.10 is judged from `repo.policy.toml` alone and a detached HEAD is not a property of that file, so
filing it there reproduces this issue's own complaint and breaks 6.10's contract that its conditions are
statically determinable); **D** a fifth invocation status (rejected on 0059's reasoning — Section 8.5
freezes the statuses and the exit-code mapping for a whole `MAJOR`); **E** a `setup` pseudo-operation so
the existing registry covers them (rejected — it adds a trigger surface no repository could usefully
bind, since the failure happens before the policy is consulted); **F** leave it
`Implementation-defined` (rejected — the exit code is the contract's coarsest branch point and is
exactly what the issue asks about). The reasoning worth keeping is the dividing line rather than the
tokens: **a configuration error is a property of `repo.policy.toml` alone, detectable before any
argument or checkout is in hand; a precondition failure needs the invocation's arguments and the
checkout.** Both refuse to run the policy and both report `usage_or_config`, which is why that status
names usage and configuration together — it was always a two-part status with one part populated. The
line is what a reviewer applies to the next such condition: ask what it is judged from, not which table
has room. Nothing in the envelope needed inventing — 0059's invariant already nulls `op`/`reason`/`class`
where nothing is decisive, which is the check Option B fails and this one passes. One boundary is stated
because it is how this could rot: an engine MUST NOT report a precondition reason for a condition an
operation could have reported, or the new registry becomes a home for any awkward failure and the
`error` status empties out. Making `branch_pattern` OPTIONAL with a stated default goes beyond the
question asked and is included because `no_current_branch` describes a situation that, read strictly,
could not otherwise arise. Three tokens is the whole registry, deliberately: each corresponds to a
capability the engine calls before the policy runs, which bounds growth better than "anything that goes
wrong early". Left open: `fail`'s envelope, still, unchanged since 0059 and 0060. Reconsider if an entry
point wants preconditions that are optional — a `status` that succeeds on a detached HEAD and reports
the detachment — which would narrow the precondition to the entries that write. Relates to 0057 (which
made operation failure total and left this the residue), 0059 (whose null-triple invariant this reuses),
0056 (which created `usage_or_config` and filled its other half), and 0044. Accepted and applied to
`VCSX-SPEC.md` (Sections 6.3, 8.2, 8.3, 8.5, 8.6, 13.1, 13.2, 13.3), the vocabulary registry,
`conformance/vcsx/README.md`, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0066 — A policy that is not well formed is `malformed_policy`

**State:** Accepted
**Folder:** [decisions/0066-malformed-policy-reason/](decisions/0066-malformed-policy-reason/)

Resolves issue #12, which reports three configuration states `VCSX-SPEC.md` Section 6.10's reason
table has no row for: an `[engine] version_floor` that is not a parsable `MAJOR.MINOR`, a required
action argument (`run_op`'s `op`, `run`'s `hook`) that is *absent* rather than wrong, and a
`repo.policy.toml` that is not valid TOML at all. The issue's own diagnosis is the right one and is
what makes this one decision rather than three: **the table is complete for a policy that is
inconsistent and silent about a policy that is unreadable.** All nine reasons decision 0056
registered describe a document the engine read and found at odds with something, and each
presupposes that a document exists and that its keys hold values of the shape Section 6 declares —
so everything upstream of those checks fell out, including conditions the issue did not report
(`[base] resolve` outside its two values, `[hooks] context` naming neither execution context). The
third state is the one that changes what an implementation builds, and the document already settles
everything about it except the token: Section 3.1 puts the `Policy Loader` inside the engine,
Section 6.1 makes discovery an engine obligation it MUST document, and Section 8.2 fixes the
envelope for a run in which the policy did not run — so an engine that cannot read the file has a
status, an exit code and an empty `reason`. Options: **A** one token, `malformed_policy`, for the
whole well-formedness class (chosen); **B** the filing implementation's meanwhiles —
`version_floor_unmet` for an unreadable floor, the argument's kind for an absent argument, the parse
failure left as the loader's own typed fault (rejected, each on its own terms below); **C** a token
per state (rejected — three tokens on the major-stable surface and three Conformance Statement rows
for three states with one owner, one repair and no caller that branches between them); **D** reading
the file is the front-end's problem and out of scope for Section 6.10, the issue's own alternative
(rejected on the document's text — Section 3.1 assigns the read to the engine, and `ship`/`land`
have no envelope of their own to report it in); **E** leave it to Section 6.10's existing extension
clause (rejected — that is the status quo, whose outcome is that the one state every engine reaches
is the one no two engines report alike);
**F** file them under Section 8.6's precondition registry (rejected by 0065's own dividing line —
all three are judged from `repo.policy.toml` alone, with no argument and no checkout in hand, which
is the definition of a configuration error). The reasoning worth keeping is the line the registry was
missing:
**well-formedness versus consistency**, with the ordering stated, since validation takes a document
and a file that does not parse yields none — which also means no new `Implementation-defined` site,
because where the policy does not parse no other condition is determinable. One token rather than
three follows 0056's own splitting criterion read the other way: it split `unknown_*` into four
because they are "found at different points and repaired differently", and these three are found by
one pass and repaired by one act. The floor's meanwhile is overturned by separating behavior from
report: fail-closedness is kept and decides the refusal, which is identical under either answer, but
not the reason — `version_floor_unmet` asserts a comparison that did not happen, while
`malformed_policy` is true of `latest`, `1` and `1.2.3` alike under a `MAJOR.MINOR` grammar, and the
two name different repairs (a newer engine, a corrected file). The absent-argument meanwhile is
overturned because it does not generalize: it works only where the argument's kind happens to have a
token, leaving `set_state` with no target, `notify` with no channel and `create_task` with no spec
unanswerable — the shape decision 0057 already settled by preferring a rule quantified over a set to
an enumeration that will outrun it, so the row is keyed on whether the action can be dispatched from
the arguments the edge carries, which also keeps Section 6.5's own bare `do = "escalate"` valid. The
issue's objection to enlarging a major-stable vocabulary is sound and is why one token is added
rather than three; it is answered by sequencing — part 3 cannot be answered by reuse, so the
vocabulary grows by one whatever else is decided, and once it has, routing the other two through it
costs nothing and removes two false statements. Two boundaries are stated because they are how this
could rot: `malformed_policy` covers a well-formedness failure **no other row names**, so a
malformed `prefixes` map stays `base_unresolvable`; and Section 6.1's ignore-unknown-keys rule is
scoped to a key the schema does not declare, not a declared key whose value it does not admit. Left
out of scope deliberately: a repository with no `repo.policy.toml` at all, and an I/O failure
reading a discovered one — adjacent, but neither is needed for this registry entry to be coherent,
and the first is a decision about whether a policy-less repository is a valid input. Reconsider if a
future `MAJOR` extends the version grammar, which would make an older engine's `malformed_policy`
misleading where the truth is that the policy needs a newer engine. Relates to 0056 (which created
this registry and whose criterion decides the token count), 0065 (whose "what is it judged from"
line files all three here), 0057, 0051, and 0044 (whose `Engine Invocation Failures` class already
names "an invalid `repo.policy.toml`" and now has a token for it). Accepted and applied to
`VCSX-SPEC.md` (Sections 6.1, 6.2, 6.5, 6.10, 13.1, 13.2), the vocabulary registry, the corpus, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0067 — An edge with no `from` is unscoped

**State:** Accepted
**Folder:** [decisions/0067-unscoped-policy-edges/](decisions/0067-unscoped-policy-edges/)

Resolves issue #13, raised by an engine implementation (`vcsx-policy`) built against `06a3bc19` that had
to pick a reading to compile. `VCSX-SPEC.md` Section 5.4 keys the policy graph on
`(from-context, trigger)` and closes with "absent such a model the key is the trigger alone", which
settles the two all-or-nothing configurations and not the **mixed** one — which is the only
configuration a repository running a transition graph is ever in, since Section 6.7's graph is keyed
`(from, on)` by construction while the edges that make a policy work (`push:non_fast_forward →
integrate`, the `#error` catch-all, the `before:commit` scan) carry no `from` at all. The two readings
differ by a whole policy rather than by one edge: under "an absent `from` is its own null context",
every ordinary edge stops firing the moment the consumer supplies a context, so adding the first
transition edge silently disables the routing that made the policy work. The corpus made the silence
visible rather than creating it — 22 of `match-edge.json`'s 24 vectors passed `"from_context": null`,
and the two that did not both exercised edges that *carry* `from`. Options: **A** an edge with no `from`
is unscoped, a scoped edge outranks an unscoped one for the same key, and the ladder selects the key
first (chosen); **B** an absent `from` is the null context (rejected); **C** mixing a scoped and an
unscoped edge over one trigger is a configuration error (rejected — it makes one added transition edge
retroactively invalidate a working policy, needs a tenth configuration reason for a condition that is
not a defect, and forbids the default-plus-override idiom); **D** unscoped, but resolve the from-context
before the ladder, so one scoped `#error` edge overrides everything while the context holds (rejected —
it lets a broader trigger beat a more specific one, which is the property Section 5.3's
most-specific-wins exists to prevent, and it reproduces B's failure mode in miniature); **E** answer in
the corpus alone and leave the prose (rejected — `conformance/vcsx/README.md` states the specification
governs and every value is read from the sections cited, so the vector would be authoring the answer,
which 0045's hygiene rule reserves for a decision, and a vector can pin which edge wins but not why).
Option B is not merely the less attractive reading but **unavailable**: Section 13.1 requires that the
same `repo.policy.toml` yield the same operation flow through `ship` and an embedded driver, and the
interactive front-end has no tracker binding and so supplies no from-context while a driver running the
consumer's workflow states supplies one — under B the unscoped `push:non_fast_forward → integrate` edge
fires under `ship` and not under the driver, two flows from one policy. Deriving the answer from a rule
the document already states is what makes it stable; the issue's argument from failure modes agrees but
does not have to carry it. B also cannot express "in every context", the contexts being the consumer's
tracker states rather than a closed set the policy can enumerate or the engine validate. The precedence
half is where the two dimensions meet, and the from-context sits *inside* the ladder rather than around
it: for one trigger key an edge naming the current context is the more specific statement and wins;
across keys nothing changes, because naming a context does not make a broader trigger the more specific
match. Accepted cost, stated rather than hidden: a per-context *mode* is not expressible in one edge — a
repository wanting every error escalated in one workflow state scopes the edges it wants overridden, at
the specificity they are written. Two things deliberately do not move: `duplicate_edge` (Section 6.10)
is unchanged, since a scoped and an unscoped edge are distinct `(from, on)` keys and were never a
duplicate, which Section 5.4 now says so a validator does not invent one; and Section 6.7's own
determinism rule is untouched, its rows having no unscoped form. Reconsider if a from-context vocabulary
were ever engine-owned and enumerable, which would make B's completeness checkable and C's validation
meaningful, or if per-context modes proved common enough that scoping each overridden edge dominated the
cost of authoring a policy — in which case the answer is an explicit mode construct rather than
inverting the ladder, since inverting it breaks the specificity guarantee for every policy that wants no
mode. Relates to 0030 (the machine this refines), 0053 (the corpus that made the gap visible), 0045 (the
hygiene rule making it a decision rather than a guessed-at vector), and 0054 and 0055, the two sibling
`match_edge` clarifications. Accepted and applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 12.1, 13.1,
13.2) and the corpus (`match-edge.json` gains `unscoped_edge_matches_inside_a_from_context`,
`scoped_edge_wins_over_unscoped_edge_in_its_context`, and `ladder_outranks_the_from_context`).

## 0068 — Every commit the engine writes carries the caller-supplied commit identity

**State:** Accepted
**Folder:** [decisions/0068-merge-commit-identity/](decisions/0068-merge-commit-identity/)

Resolves issue #14. `VCSX-SPEC.md` Section 10.1 splits a commit into content and identity and
assigns the second to the consumer; Section 9.1 carried that through for `commit(message, identity)`
and for neither of the two other capabilities that can write a commit — `integrate` writes a merge
commit whenever the base does not fast-forward, and decision 0061 made `pull` merge the remote
counterpart rather than replay over it. Section 10.1 answered this exact case for the *message*
("uses the backend's default message") and said nothing about who it is attributed to, so a backend
had to decide with nothing to decide from. Left to the environment, git auto-detects an identity
from username and hostname: the merge commit names whoever ran the engine, so the same repository
under the same policy produces different history on different machines, and where the hostname
carries no domain — a container, a CI runner — git refuses the address and aborts the merge, so
`integrate` returns `integrate:ok` on a laptop and `integrate:failed` on a runner with nothing in
the policy differing. The filing implementation shipped that and CI caught it. Options: **A** the
commit identity reaches `integrate` and `pull` through their Section 9.1 signatures (chosen); **B**
the consumer's identity supplied once when the backend is opened (the issue's meanwhile; rejected —
it routes an engine-resolved value through a channel that is not a capability signature, and the
channel does not exist, since Section 9.1 specifies capabilities and not a backend lifecycle, so it
must invent a plugin-instantiation step and make it the second place the engine hands a backend a
resolved value; it puts two identities in play with a precedence rule no result exposes when a
backend gets it wrong; and Section 8.6 already has the engine present the identity to the backend
and refuse the run on `identity_invalid`, so backend-scoping would have the engine validate a value
it does not supply); **C** an engine-defined identity published under Section 13.3 (the issue's
second offer; rejected — it closes the host-dependence but not the divergence, two engines writing
different authors into a repository's permanent history while both conform, and it inverts
Section 10.1 for one commit out of two while every consumer already holds an identity, since
`commit` requires one); **D** leave it to the environment as an `Implementation-defined` behavior
(rejected — the term names a behavior an engine chooses and documents so a consumer can plan around
it, and this one is not a property of the engine at all but of the host it happens to run on); **E**
a repository-owned author key in `repo.policy.toml` beside `remote` (rejected — Section 6.2's line
puts backend *selection* on the repository's side and the *credential* on the consumer's, and naming
the author in the repository would source attribution from one side and authorization from the
other); **F** reuse the identity `derive_work_branch` already takes (rejected — a branch derived
from `symphony/<identifier>` is filled from a work item, so reusing it would attribute commits to a
work item; what the option is good for is exposing that Section 8.1's common-argument list conflated
two identities, fixed here). The reasoning worth keeping is the invariant in the shape decision 0062
left it: **the capabilities that take the commit identity are exactly those that can write a
commit.** Section 9.1 now carries one sentence of that form per engine-resolved value — the
capabilities taking a `remote` are exactly the operations Section 3.2 places host-side, those taking
an `identity` are exactly the ones that write commits — and each is what a reviewer checks when the
next capability is added. The tension with 0062 had to be argued rather than assumed, because the
meanwhile resolves it the other way: 0062, inheriting from 0058, requires every value an operation
needs and the engine resolves to reach the backend through a capability signature, and a
backend-scoped identity is that rule's plainest counter-example. Its justification — the identity is
constant across an invocation — is true and beside the point, because **constancy is an argument
about where a value is supplied from, not about how it reaches the backend**; the remote is equally
constant and is passed anyway. Bending the rule for the first constant value would leave it stating
something about frequency rather than about provenance. The credential is the one value that does
travel outside a signature, and identity is not like it: Section 11 keeps credentials out of the
engine deliberately, while Sections 8.1 and 8.6 have the engine hold the identity and validate it.
Two consequences are stated rather than left to follow — a backend MUST NOT attribute a commit to an
identity it derives from its execution environment, and a merge the forge performs, the commit a
squash writes included, is attributed by the code host to the account the consumer's credential
names — the second because without it the invariant reads as a claim about every merge commit in a
repository's history and `land` looks like an omission rather than a boundary. Requiring the
identity for an `integrate` that may fast-forward is a deliberate small cost: the engine cannot know
in advance whether the update merges, and refusing up front at exit `2` beats discovering it after
the merge was attempted. `identity_invalid` widens to cover an absent identity rather than gaining a
fourth token, since 0065 bounded that registry deliberately and one failure of one argument should
not need two branches. Reconsider if a backend appears that cannot be constructed without an
identity — one signing through a key held in an agent socket — which would argue for a plugin
lifecycle with an explicit open step that the identity travels with. Relates to 0062 (whose
signatures this extends and whose invariant it applies a second time), 0058 (the source of that
invariant), 0065 (whose precondition this widens), 0061 (which made `pull` a commit-writing
capability), and 0032 (which authored the content/identity split). Accepted and applied to
`VCSX-SPEC.md` (Sections 8.1, 8.6, 9.1, 10.1, 13.1, 13.2), the vocabulary registry,
`VCSX-CONTRACT.md` (Section 9), and `SPEC.md` (Sections 9.8, 17.2).

## 0069 — `observability.*` is the configuration namespace for observability settings

**State:** Accepted
**Folder:** [decisions/0069-observability-config-namespace/](decisions/0069-observability-config-namespace/)

Resolves part 2 of issue #15. Section 18.2 carried the specification's own TODO — "Make observability
settings configurable in workflow front matter without prescribing UI implementation details" — and
nothing in Section 5.3 or the Section 6.4 cheat sheet defined a namespace for one, while every other
extension owns one (`budget.*`, `quota.*`, `compute.*`, `server.*`, `[tasks]` / `[driver]`) stated in
the same sentence shape. Section 13.6 then required the ledger to own its configuration "under its own
namespace, documented with the extension" **without saying what that namespace is** — an obligation to
use a namespace with no namespace named. The cost is concrete: the first implementation to make a sink
or a ledger path configurable invents a top-level key and the second invents a different one, for the
same deployment. Options: **A** `observability.*` in the operator policy config with the ledger under
`observability.ledger.*` (chosen); **B** `logging.*` (rejected — the ledger, a status surface and
humanized summaries are not logging, and a namespace that must be widened later is worse than a wide
one now, because widening it is the rename a namespace exists to prevent); **C** one namespace per
Section 13 surface (rejected — it multiplies top-level keys for what an operator experiences as one
concern; `observability.ledger.*` satisfies Section 13.6 without a third top-level key); **D** follow
the TODO into `WORKFLOW.md` front matter (rejected — Section 5 makes `WORKFLOW.md` untrusted,
in-sandbox, and forbids any setting Symphony executes with host access, which a sink path and a ledger
location plainly are; the TODO predates the three-artifact split); **E** define the fields as well
(rejected, and drawn as the scope line — Sections 13.2 and 13.4 make the sink and the surface
implementation-defined, so there is no cross-implementation field to define, and naming one would
prescribe the UI details the TODO itself rules out); **F** leave the TODO (rejected — it has already
been read once by an implementation that then had to invent a key). **The specification owes the
place, not the settings**: a namespace is a cross-implementation contract because two implementations
reading the same configuration must agree where the keys live, while the settings are not, because the
specification made them implementation-defined in the first place. So naming the namespace discharges
the TODO rather than deferring it. Artifact placement follows trust rather than the TODO's wording, on
Section 5's dividing rules and `compute.*`'s precedent ("in the operator policy config"). Recorded as
noticed and not fixed: Section 13.8 places `server.*` in `WORKFLOW.md` front matter, in tension with
Section 5 for the same reason Option D is rejected — a defect in Section 13.8 rather than a precedent,
surfaced in `conformance/README.md`. Reconsider if a genuinely cross-implementation observability
field appears, which the specification should then define under this namespace. Relates to 0005 and
0029 (the trust split that decides the artifact), 0011 (the ledger whose namespace this names), 0045,
and 0070. Accepted and applied to `SPEC.md` (Sections 6.4, 13.6, 18.2).

## 0070 — The Conformance Statement records the Section 13 resolutions

**State:** Accepted
**Folder:** [decisions/0070-conformance-statement-section-13-resolutions/](decisions/0070-conformance-statement-section-13-resolutions/)

Resolves part 1 of issue #15. Section 19 requires a resolution for every `Implementation-defined`
behavior and introduces its enumeration with "including:", so the list is open — yet three Section 13
behaviours appeared in neither it nor `CONFORMANCE-STATEMENT-TEMPLATE.md`: the log sink (13.2), the
human-readable status surface (13.4), and the presentation of rate-limit data (13.5). The template's
Section 4.2 also had no `<other>` escape row of the kind its Section 2 provides, so an implementation
had nowhere to write three resolutions Section 19 implies it owes — and a Statement that omits a
resolution because the form lacked a field is the failure Section 19 exists to prevent (0045). Its
Section 2 additionally cited a placeholder `13.x` in three rows, dating from the template's creation:
two resolve to 13.6 and 13.8, and the third (autonomous task management, `8.10 / 13.x`) resolves to
nothing, since Section 13 has no task-management subsection. Options: **A** resolve the obligation in
`SPEC.md` first, then add the rows (chosen); **B** add the rows to the template only (rejected — for
Section 13.2 the row would carry an obligation the specification does not state, inverting the
template from a view over `SPEC.md` into a second source of requirements, which its own preamble
forbids); **C** file all three under the template's Core table (rejected — Section 4.1 says a core row
MUST NOT be left blank, while Section 13.4's surface is explicitly OPTIONAL, so it would demand a
resolution from an implementation that ships none and blur the Core/extension boundary inherited from
Sections 17 and 18); **D** rely on `<other>` rows alone (rejected — 0045 chose a pre-enumerated
template over a checklist precisely because a generic slot does not tell an implementer an obligation
exists; an escape row catches what nobody anticipated, it does not substitute for what is known);
**E** drop the placeholder rows' Section column (rejected — it trades a wrong pointer for no pointer).
**The template may only point at what `SPEC.md` states**, which is why a defect reported as three
missing table rows is partly a specification change: Section 13.2's "The spec does not prescribe where
logs are written" is a disclaimer, while `Implementation-defined` is a contract term carrying a
MUST-document obligation, and Section 17.6 already makes sink-failure behavior a `Core Conformance`
check an auditor cannot verify without knowing what the sinks are. Core versus extension follows the
specification's own marking rather than the convenience of the form: 13.2 and 13.5 are core rows (13.5
resolvable as "none", which is a resolution and not a blank), 13.4 is extension-scoped and gains a
Section 2 row carrying 0069's `observability.*`. Section 4 gains a lead-in sentence mirroring Section
19's "including" and Section 4.2 gains the `<other>` row; Section 4.1 gets the sentence but no row,
because a permanent placeholder would contradict its own MUST-not-be-blank instruction. Reconsider if
Section 19 and the template drift a third time — the remedy is then to generate the template from
`SPEC.md`'s tokens rather than to keep patching both. Depends on 0045 and 0069; relates to 0050 and
0043. Accepted and applied to `SPEC.md` (Sections 13.2, 19) and `CONFORMANCE-STATEMENT-TEMPLATE.md`
(Sections 2, 4, 4.1, 4.2).

## 0071 — The Symphony token vocabulary as data

**State:** Accepted
**Folder:** [decisions/0071-symphony-vocabulary-as-data/](decisions/0071-symphony-vocabulary-as-data/)

Resolves part 3 of issue #15, and does for `SPEC.md` what 0051 did for the engine. Four of Symphony's
token sets were prose an implementation had no choice but to re-spell by hand — the emitted runtime
events (10.4), the REQUIRED log context fields (13.1), the usage-ledger entry fields (13.6), and the
state recovery classes (14.3) — so the drift `VCSX-SPEC.md` Section 14 closes for the engine was open
for Symphony, and silent in the same way: an event renamed upstream changes nothing downstream until
someone reads a re-pin diff. Symphony's exposure is the larger one, because `SPEC.md` is written for
multiple implementations in multiple languages (0045) and every one of them spells these tokens
independently. Section 10.4 carried a second defect on top: it introduced its list with "for example"
while Section 10.7 states that each adapter MUST emit that vocabulary, so the two could not both be
read literally, and a generator could not tell whether to close the enum. Options: **A** a registry in
the engine's shape (chosen); **B** a pinned-spec hash check (rejected — it converts a silent failure
into a diff someone has to read, which is the mechanism that already failed, and does nothing for the
second implementation); **C** transcribe the tokens into each Conformance Statement (rejected — a
human-readable declaration catches divergence at audit time, not at compile time). On the exhaustiveness
question: **D** not exhaustive, but the listed names are fixed (chosen); **E** exhaustive (rejected —
it makes any adapter-specific event non-conformant, contradicting the neutral-adapter model, and would
be a substantive new restriction adopted to make codegen convenient); **F** leave it open (rejected —
it leaves Section 10.7's MUST pointing at a list the document calls illustrative, so an adapter could
rename `turn_failed` and claim conformance). **The ruling belongs in the specification, not in the
registry**, since a derived view cannot decide whether its source's list is closed — so Section 10.4
gains the `Note:` first and the registry records `exhaustive: false` after. **Openness is a property
of the set, not of the names**: a generated type admits an unknown token while every known token is
still checked, the same shape the engine registry already uses for its operations. The file is
`conformance/vocabulary.json`, beside the Symphony corpus that occupies `conformance/` directly, since
`conformance/symphony/` would move an existing tree and break the paths cited in 0046, 0048, 0051 and
0053 to buy a symmetry no consumer needs. The slice carries the four sets plus three that make them
usable rather than readable — the neutral token-usage record both the event `usage` map and the ledger
entry are defined in terms of, the per-field recovery-class assignments a Conformance Statement is
compared against, and the configuration namespaces its extensions table draws from. `SPEC.md` Section
17 gains the precedence rule in its own text rather than only in a README, because Symphony has no
Section 14 to lean on: **the prose governs; the artifact is derived**, and a disagreement is a defect
in the registry. Authoring surfaced two findings recorded rather than fixed: Section 5.3's top-level
key list omits `vcs`, which Section 6.4 documents; and Section 13.8 places `server.*` in `WORKFLOW.md`
front matter against Section 5's host-access rule. Reconsider on 0051's trigger — a registry
accumulating properties the prose does not fix has stopped being derived — or if `SPEC.md` ever gains
a Section 14-style alignment rule, which the registry should then serve rather than stand beside.
Depends on 0051 and 0046; relates to 0045, 0010, 0011, and 0069. Accepted and applied:
`conformance/vocabulary.json` is created, `conformance/README.md` and `conformance/vcsx/README.md`
document it, and `SPEC.md` Sections 10.4 and 17 carry the ruling and the precedence rule.

## 0072 — Captured subprocess text is redacted where it enters the process

**State:** Accepted
**Folder:** [decisions/0072-redact-captured-subprocess-text/](decisions/0072-redact-captured-subprocess-text/)

Resolves issue #16. Section 15.3 is unambiguous — "Do not log API tokens or secret values", "Validate
presence of secrets without printing them" — and Section 13.8.2 describes a JSON API whose per-issue
response carries `last_message` and `recent_events[].message`, agent-produced free text served over
HTTP with no redaction requirement; Section 13.1's only nearby rule is about large raw payloads, which
is a size rule and not a content one. So an implementation can ship Section 13.8 faithfully, honour
Section 15.3 everywhere the specification names it, and still serve a token to anyone who can reach the
port. The defence that would ordinarily close this — a secret type that cannot be printed or serialized
— carries none of it: an agent that echoes a credential into its own message produces an ordinary
string, and there is no type to attach a rule to because the value did not come from the secret
provider, it came back out of a subprocess as prose. Options: **A** state the obligation in Section 15.3
over captured subprocess text, discharged where the text enters the process, and point at it from
Sections 10.4, 13.1 and 13.8.2 (chosen); **B** one sentence in Section 13.8.2 requiring redaction before
serving, the issue's first ask (rejected — by the time the handler runs the value is already in
orchestrator state, so the identical string stays in the log sink, the snapshot, the status surface, the
humanized summary and the session transcript that response itself links; it also puts the only statement
of a security requirement inside an OPTIONAL extension, leaving a non-HTTP deployment with nothing, and
sets the precedent that each new surface restates the sentence — which is how one gets missed); **C**
declare that Section 15.3 already governs the fields, the issue's second ask (rejected *as written* and
adopted as a consequence of A — read against today's Section 15.3 it is false, since those bullets bind
values Symphony resolved and printed rather than a string that arrived from a subprocess, and telling a
reader the case is covered when no clause covers it is worse than silence; once A puts the rule in
Section 15.3 the sentence becomes true, and it is what Section 13.8.2 now says); **D** require pattern
or entropy matching over agent output (rejected as *the* requirement — false positives corrupt
legitimate output and false negatives are unbounded, so an implementation cannot state what it
guarantees, and prescribing a matcher is the implementation detail this document keeps out of normative
text; retained as permitted, forbidden as a substitute); **E** leave the mechanism fully
`Implementation-defined` with no floor (rejected — the term still needs a behavior to bind, and with no
floor an implementation that logs a warning and serves the token conforms); **F** drop the two fields
from the response shape (rejected — they are what makes a per-issue debug endpoint worth having, and the
value stays in the log either way); **G** bind the rule to the orchestrator↔executor seam (rejected —
one hop too late where it matters, since with a remote executor the seam is a network boundary and a raw
value would already have crossed it and been written to whatever that node logs). The reasoning worth
keeping is the placement rule rather than the mechanism: **a redaction obligation belongs at the
boundary where untrusted text is first captured, not at each boundary where it is published, because
the set of publishers is open and the set of capture points is closed.** Symphony captures agent text in
one place and host-side hook output in one other; it publishes that text through logs, a snapshot, a
status surface, humanized summaries, a transcript and an OPTIONAL API, and the next release adds a
seventh. The floor is what makes this a MUST: the values are the finite set this run resolved and is
holding, the failure mode is publishing a credential to whoever can reach the port, and the fields are
observability-only (Sections 13.4, 13.7, 13.8) so nothing can break by complying — none of the usual
reasons to soften a requirement apply. Above the floor the mechanism and its marker are
`Implementation-defined` and published in the Conformance Statement, which is how a language-agnostic
document declines to prescribe a matcher while still letting an auditor see the choice. The residual is
stated in the specification rather than glossed, because a mitigation described as complete is worse
than one described accurately: known-value replacement does not reach a derived form — an encoding, or
a paraphrase — and cannot reach a secret Symphony never resolved, such as one the agent reads out of
repository or tracker content, since no value exists to match against. Those belong to the trust
boundary and harness hardening (Sections 15.1, 15.5), and their existence is why the secret-isolation
invariant stays the primary control and redaction its backstop. Two boundaries are drawn deliberately:
host-side hook output is inside the rule (captured the same way, a hook MAY hold a repo-internal
integrity value, and Section 15.4's "truncated in logs" is a size rule with the same gap Section 13.1
had), while commit messages and pull-request bodies are outside it (agent prose the repository publishes
deliberately, already gated by its own `before:commit` gate / `scan-content`, which refuses rather than
rewrites — the right shape where a title is used verbatim). No configuration key is added: an
operator-weakenable security floor is a floor an operator can remove. Reconsider if agent free text
becomes an orchestration input, which would make redaction order-sensitive and argue for a structured
channel for the signal; or if a secret provider rotates a credential mid-run, which makes "the values
this run resolved" time-varying and would need the floor to name the union. Relates to 0003 (the
credential broker and the secret-isolation invariant this backstops), 0004, 0032 (agent prose crossing
into commit and pull-request messages, left to the repository's gate), 0035 and 0036 (the executor and
the seam Option G would have used), and 0011. Accepted and applied to `SPEC.md` (Sections 10.4, 13.1,
13.8.2, 15.3, 17.5, 17.6, 18.1.2, 19) and `CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0073 — The network-touching capabilities are named, and base resolution yields a commit

**State:** Accepted
**Folder:** [decisions/0073-network-touching-capabilities-named/](decisions/0073-network-touching-capabilities-named/)

Resolves issue #22, which reports three things `VCSX-SPEC.md` Section 8.6 and Section 6.2 require a VCS
backend to answer and Section 9.1 — the document that says what a backend must be able to answer — does
not list: a judgement of whether a derived work-branch name is legal, a judgement of whether a commit
identity is well formed, and, once `[engine] remote` exists, which of a checkout's several copies of the
base a non-fetching read consults. The report's own defence-and-refutation is sound: a backend that
judges the identity when it is constructed judges it before the engine exists, and a `derive_work_branch`
that merely refuses produces a refusal with no token, so in both cases Section 8.6 never reaches its own
registry and a precondition step that cannot run is not a precondition step. Two things sharpen the third
gap beyond the report's framing — it is not only a fork problem, since even a single-remote checkout
offers `refs/heads/<base>` and `refs/remotes/<remote>/<base>`, and the report's fallback offer of "a
sentence saying which copy" is not available, because the only non-arbitrary answer is the copy belonging
to the resolved remote and Section 6.2 forbids a backend to read that remote from the policy. Options:
**A** the two predicates plus the resolved remote on `ahead_behind` and `diff`, exactly as asked
(rejected as insufficient — passing a `remote` to a capability that acquires nothing falsifies decision
0062's invariant while leaving its consequence true, and it leaves the name-to-commit step unspecified,
so two base-taking capabilities could still disagree inside one invocation); **B** a compound base
carrying the *remote* plus one combined `check_preconditions` (rejected — the compound narrows the
ambiguity without removing it, a local remote name is meaningless to the forge that also takes a base,
and the combined check makes Section 8.6's registry a plugin capability's return domain); **C** narrow
Section 8.6 instead — a typed `work_branch_invalid` refusal from `derive_work_branch` and a
presence-only identity precondition (rejected — it reopens 0065 one day after acceptance and reinstates
that decision's own rejected option, where a malformed identity arrives as `error`/exit `20` and invites
a retry against a state no retry changes); **D** resolve the base to a commit (rejected only as a
stopping point — it fixes the base and leaves `integrate` and `pull` acquiring without being named for
it); **D-strong** option D, and acquisition separates from use (chosen). The reasoning worth keeping is
the replacement of a proxy with the thing it stood for. 0062 wanted one sentence a reviewer applies to
the next capability and chose an argument-shaped equivalence — takes a `remote` ⟺ host-side ⟺ needs a
credential — and this issue is that proxy failing, because a read must know *which* remote's copy it
compares against while acquiring nothing at all. **The network-touching capabilities are exactly
`fetch_base`, `fetch_counterpart` and `push`; every other Section 9.1 capability is local to the
checkout, whatever arguments it takes.** That is an enumeration rather than an inference, so no argument
list can falsify it, and it makes Section 3.2's split checkable at the capability boundary instead of
read out of an operation's prose. The base half is the root cause: Sections 6.4 and 12.4 resolved the
base to a *name* and stopped, and the step from name to commit happened privately inside `ahead_behind`,
`diff` and `integrate`, three times per invocation with nothing requiring agreement — so resolution now
yields a record, `branch` for the forge which wants a name and `ref` for the VCS which wants a commit,
and one capability, `resolve_base_ref`, performs that step once. Decomposing the two acquiring operations
costs two capabilities beyond option D and buys three things: the enumeration becomes exhaustive; the
halves land where they belong for a consumer that sandboxes its caller, since the merging half is the
one that stops on conflicts and hands the worktree to whoever can resolve them; and a failure the engine
can now distinguish becomes reportable. That earns the one new reason, `base_unavailable` (`error`, for
`integrate` and for `diff`), operationally rather than as bookkeeping — Section 12.2 retries `push`
through `integrate`, and an acquisition that failed cannot converge, so today the run burns the flow
bound and reports `flow_exhausted`, which is 0064's own "the failure got quieter, not louder". It is one
word from `base_unresolved` and means something else, so the difference is stated: **unresolved is not
knowing which branch; unavailable is not having its commit.** Splitting `pull` buys only symmetry and is
included anyway, because a naming rule that holds for `integrate` and not `pull` is the next report; it
gains no token, since no built-in sequence retries `pull` and an absent counterpart is a normal state
before the first push. Three consequences are stated rather than inferred: a `base_ref` is opaque to the
engine as the commit identity is, its validity ends when an operation moves what it names, and
resolution MAY answer *absent* — which `diff` reports as `base_unavailable` and `status` reports as
`status:ok` with null `ahead`/`behind` and a `base_absent` output, because an inspection that cannot see
the base states a fact rather than raising a failure. `merge_base`, `merge_counterpart` and `commit` are
local although they write: Section 9.1's local set has always meant reads *or writes* the checkout, and
local is about credentials rather than mutation. The cost is recorded honestly because most of it is not
transitional: the change impact rounds to nothing while no `MAJOR` is published (Section 8.5) and is
now-or-never cheap, but two required methods beyond option D, a foreclosed fused acquire-and-merge, and
an enumeration that must be maintained all outlive it — while the handle and its lifetime, the likeliest
source of the next report, belong to option D and would have been paid either way. Reconsider for a
backend whose VCS makes acquire-and-merge genuinely atomic, which would argue for an OPTIONAL fused
capability in the descriptor rather than recombining the required two; or for a consumer that needs the
merge half in the sandbox in practice, which would argue for Section 3.2 labelling capabilities rather
than operations. Relates to 0062 (whose invariant this replaces with the enumeration it approximated),
0064 (whose asymmetry survives and whose quieter failure the new reason answers), 0058 (whose "every
required operation MUST be realizable through the required capabilities" licenses a one-to-many split,
as `status`'s six calls already show), 0065 (whose three precondition rows now each name a capability),
0068, 0060 and 0061. Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 6.2, 6.4, 8.6, 9.1,
11, 12.4, 13.1, 13.2), `conformance/vcsx/vocabulary.json`, and `conformance/vcsx/README.md`.

## 0074 — The commit-identity precondition is scoped to the entry point

**State:** Accepted
**Folder:** [decisions/0074-commit-identity-scope/](decisions/0074-commit-identity-scope/)

Resolves issue #23. Section 8.6 requires the commit identity "for an entry that can write a commit —
`commit`, `integrate`, `pull`, and a front-end sequence that dispatches one", and Section 5.2 makes a
policy a graph, so the last clause admits two readings: the sequence's own dispatches, or anything the
invocation can dispatch. Under the first, a `status` entry whose policy routes `status:ok` to `run_op`
`commit` reaches an identity-taking operation with no identity, and Section 4.3 has no reason naming the
condition — the engine is left with a fault at exactly the point Section 8.6 exists to refuse before.
Three things sharpen the report. The gap is the document's *own* example policy, not a contrived one:
Section 6.5 prints `push:non_fast_forward → run_op integrate` as its illustration and Section 12.2 builds
the same routing in, so the most ordinary policy in the document, invoked at the `push` entry point,
reaches an operation that writes a merge commit. A channel does exist and is the wrong one — `failed` is
universal (0057), so `commit:failed` is expressible; it reports exit `20`, an invitation to retry a run
no retry changes, so the operation cannot answer *truthfully*, which is narrower than "cannot answer".
And Section 8.6's closing rule is itself ambiguous in a load-bearing way: read counterfactually, "a
condition an operation could have reported" yields the issue's conclusion, but applied consistently it
also empties Section 8.6's own table, because `failed` makes every precondition one some operation could
have reported. Options: **A** scope the precondition to the entry *and* the policy's `run_op` edges
(rejected — the canonical `integrate` edge is in essentially every real policy, so it collapses to
"every invocation of every entry requires an identity", and it adds the policy file to what a
precondition is judged from, blurring 0065's dividing line); **B** keep the entry scope, say so, and add
the missing operation reason (chosen); **C** state the invariant and permit a reachability narrowing
(rejected — the argument set becomes engine-dependent, and the permissive direction means a consumer
developed against one conforming engine breaks on another); **D** require the identity unconditionally
(rejected — it charges a credential-free `status`/`diff` an attribution argument they never use);
**E** a fourth Section 8.6 token for the dispatch case (rejected — that registry is for conditions judged
before the policy runs); **F** `Implementation-defined` (rejected on 0065's reasoning). The reasoning
worth keeping is that **the document had already answered this shape once**: Section 9.3 refuses an
unsupported capability at validation "where determinable" and otherwise lets it surface "at first use as
the operation's `unsupported` reason". Identity is the same shape — at entry the engine knows a
commit-writing dispatch *may* occur, not that it will — so the entries that certainly write stay a
precondition and the residual becomes `identity_missing` (`needs_caller`, for `commit`, `integrate` and
`pull`). The test that generalizes is: ask whether the invocation determines the condition or only the
run does. `needs_caller` is the honest class rather than `error`: Section 4.2 defines it as an operation
that cannot proceed without a decision or action from the caller, a missing caller argument is that
literally, the built-in default already escalates it (5.4), and it gives the condition a resolver seam
(5.5) — `supply_identity` — where exit `20` would invite a retry that cannot succeed. Two boundaries are
stated because they are how this rots: the closing rule becomes "a condition an operation **has a reason
that names**" with the first dispatch as the line, plus an explicit note that the universal `failed` does
not satisfy it; and a supplied identity is judged for shape *whatever* the entry, which costs nothing
(`accepts_identity` has no side effect, 0073) and leaves only absence reachable at a dispatch — so
`identity_missing` names one condition rather than two, and a malformed identity handed to a `status` run
stops being unjudged. The cost is recorded rather than glossed: a `land` whose policy routes `merge:ok`
to `pull` merges the pull request and then stops at `pull:identity_missing`, and re-invoking `land`
answers `merge:not_open` — prior effects stand, as they already do at a flow bound (5.6), and the
escalation names what to supply. Option A avoids that one case and pays for it on every invocation of
every entry, which is the trade this declines. Twelve vectors pin the scope, since it is a pure function
of the entry point even though the judgement is not, on the rule issue #13 established that "no vector
pins whether X" is itself a defect. Reconsider for a driver that cannot tolerate discovering a missing
argument mid-flow after a forge merge has landed (which argues for A), or a consumer with no identity to
give that legitimately runs write-capable policies read-only (which argues the other way); if both
appear, C is the repair, and the clause is phrased as a scope over entry points rather than as an
analysis so that narrowing it later adds no token and changes no status. Relates to 0065 (whose
precondition registry and closing rule this repairs), 0068 (which made `integrate` and `pull` carry the
identity, and so made them reachable here), 0057 (whose universal `failed` is what makes the old rule
ambiguous), 0073 (whose `accepts_identity` the "judged whatever the entry" rule needs), and 0053.
Accepted and applied to `VCSX-SPEC.md` (Sections 4.3, 8.4, 8.6, 13.1),
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/identity-precondition.json`, and
`conformance/vcsx/README.md`.

## 0075 — A failed counterpart acquisition is `pull:failed`

**State:** Accepted
**Folder:** [decisions/0075-counterpart-acquisition-failure/](decisions/0075-counterpart-acquisition-failure/)

Resolves issue #26. Decision 0073 split `pull` into `fetch_counterpart` and `merge_counterpart` and
concluded in as many words that the operation gains no reason token — "no built-in sequence retries it,
so `pull:failed` remains sufficient, and an absent counterpart stays a benign `pull:ok`" — but Section
9.1's realization did not carry that conclusion through: `fetch_counterpart` answers "the ref … or none
where the remote carries none", two answers for three conditions. A fetch that failed is not "the remote
carries none" and has no answer of its own, so an engine composing `pull` as Section 9.1 describes reads
the absent answer as "nothing to merge" and **reports `pull:ok`, class `done`, exit `0`, for a run that
pulled nothing.** What was missing was not a reason: `pull:failed` has been in the registry since 0057
made `failed` universal, and was merely unreachable — the specification had the word and no path to it.
Two things sharpen the report. Section 6.2 promises that a configured remote the checkout does not carry
"surfaces at first use as the operation's `failed` reason", and for `pull` first use *is*
`fetch_counterpart`, so two normative sections disagreed rather than one being silent. And Section 13.1
asked for the failed-acquisition check on the `integrate` side of the same split and nothing on the
`pull` side, which is why the filing implementation shipped the bug green through a full gate. The
issue's own preferred shape — one combined counterpart token, leaving the two-valued answer as it is,
"as `base_unavailable` covers both for `integrate`" — is unsound and was withdrawn by the reporter: a
reason carries exactly one proto class (4.2), frozen within a `MAJOR` (8.5), and `base_unavailable`
combines two conditions that are **both failures**, while the counterpart's two straddle the boundary,
"the remote carries none" being the ordinary state before the first push whose correct result is
success. A combined token at `error` fails every first push; at `done` it is the defect renamed. So the
three-valued answer is the floor under every option and the only live question was how to name the third
condition. Options: **A** the capability distinguishes and the failure is `pull:failed` (chosen); **B**
A plus a registered `pull:counterpart_unavailable`, class `error` (rejected — the sound version of the
ask, and the only one worth weighing); **C** the combined token (rejected as unsound, recorded because
the issue proposes it); **D** an answer-domain invariant over all of Section 9.1 (not taken — the
observation behind it is real, that Section 9.1 silently mixes capabilities answering `<op>:*` with
capabilities answering a bare value, and that of the three network-touching ones `push` answers a result
while both fetches answer a value, which is exactly where a transport failure has nowhere to go; but an
invariant quantified over the capability list sits at a different altitude than the section's prose, and
it is the repair to reach for if a second capability repeats this). B is rejected on 0073's own test
rather than on size. That decision earned `base_unavailable` operationally: Section 12.2 routes
`push:non_fast_forward` to `integrate` and retries the push, so a failed acquisition could not converge,
burned the flow bound (0060) and surfaced as `flow_exhausted` — "the graph does not converge or the
remote is moving", not "your remote is down". **The token exists because a built-in loop was
misdiagnosing.** Neither Section 12.2 nor 12.3 dispatches `pull`, so there is no loop to misdiagnose,
and the universal `failed` is doing precisely the job Section 4.3 defines it for — "defined for every
operation" is the specified answer, not a fallback. Section 8.5 makes every token permanent shared
surface and 0066 already ruled against reaching for a narrow token where a wider one fits, so minting
`counterpart_unavailable` would be that ruling inverted. The symmetry argument that carried 0073's split
does not carry a token either: the two operations differ because **a base is required to exist and a
work branch's counterpart is not**, so the base's non-ref answers collapse to one class and the
counterpart's do not — the asymmetry is in the subject rather than in the naming, which is why Section
4.3 gains a sentence and not a row. The cost is recorded rather than argued away: `pull:failed` covers
both halves of the split, so a policy cannot bind a failed acquisition apart from a failed merge, and a
consumer handling one real-world condition across both operations writes two shapes. Reconsider for a
consumer that must tell an unreachable remote from a failed merge *in order to act differently* — retry
later versus escalate to a person; Section 8.5 admits the token in a `MINOR` release, landing on the
`error` edge a consumer already has, so deferring costs a later minor bump and nothing else, while
adding it now is permanent. Relates to 0073 (whose conclusion this carries into Section 9.1, and whose
realization it repairs without disturbing the decision), 0057 (whose universal `failed` is the answer),
0066 (whose "the wider token where it fits" ruling this follows), 0062 and 0064, 0060, and 0074.
Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.1, 13.1) and `conformance/vcsx/README.md`;
`conformance/vcsx/vocabulary.json` verified unchanged.

## 0076 — A capability that cannot determine its answer says so

**State:** Accepted
**Folder:** [decisions/0076-capability-answer-domain/](decisions/0076-capability-answer-domain/)

Resolves issue #28. Decision 0075 considered and deferred an answer-domain invariant over the plugin
API, naming its own trigger: "**It is the repair to reach for if a second capability repeats this.**"
`pr_state(work_branch)` is that second capability — it answered `open`/`closed`/`merged`, three answers
for five states, since a work branch with no pull request was unstated and a forge that could not be
asked had nothing left to answer with. The consequences are worse than #26's because two of its three
readers *act* on the answer rather than report it: `push` proceeds over a **merged** pull request, the
exact act `push:pr_closed` exists to refuse, and `create_or_update_pr` opens a **second** pull request
for a work branch that already has one, the one thing Section 9.2 says a forge backend maintains
against; `status` merely lies, reporting no pull request for a repository that has one where Section
4.1 already carries the honest shape for the base (`base_absent`). The report also establishes that the
lookup cannot be narrowed — `create_pr:base_mismatch` requires finding a pull request opened against a
*different* base, so a forge with no head-keyed index enumerates, and **an enumeration that reached its
bound is an incomplete search rather than a negative answer**, a way of being unable to answer that is
not transport at all. What made this a decision about the class rather than about `pr_state` is the
audit: of the value-answering capabilities, `is_conflicted()`, `current_branch()`,
`resolve_base_ref()`, `accepts_*` and `is_dirty()` all have an absent answer that already means
something, and **`is_dirty()` fails open**. Section 12.2 does not report on it, it *branches* on it, so
a false reading produces no `commit:nothing_to_commit` but no commit result at all: `ship` goes
straight to `push` and reports success with the work still uncommitted — a green run that did nothing
it was asked to do, worse than the report that prompted the decision and never itself reported. An
implementation avoids it only through a channel of its own outside the Section 8.2 envelope, which is
the very objection #26 raised about its meanwhile, so every other engine must invent that channel and
choose its own mapping. Options: **A** widen `pr_state` alone, no token (contained in the choice, but
leaves the rule that would have caught `is_dirty()` unwritten); **B** A plus a registered `push` reason
for the refusal (rejected on 0066's and 0075's shared ruling — same class as `failed`, so the wider
token fits, and 8.5 admits it in any `MINOR` if a consumer must act differently); **C** A inside the
invariant, with the Section 9.1 audit it implies (chosen); **D** a `Result`-shaped plugin return
(rejected — a language-level mechanism in a document that names no language; the specification's
business is which reason a caller reads). So Section 9 now states it over both plugin sections: a
capability either answers its operation's typed result or answers a value; a value-answering capability
MUST be able to answer that it could not determine one; **that answer MUST NOT be spelled as the
value's absent or negative case**; and every such non-answer maps to a Section 4.3 reason where an
operation has been dispatched or a Section 8.6 precondition reason where none has — **the first
dispatch is the boundary**, which is 8.6's existing rule reused rather than a second one. The mappings
land almost entirely on reasons that already exist: `push:failed` / `create_pr:failed` / a
`pr_state_unavailable` output; a dispatched `commit` reporting `commit:failed` where `is_dirty()` cannot
answer, because the guard exists to skip a commit that would report `nothing_to_commit`, not to decide
whether a commit is owed; `diff:base_unavailable`, whose definition already covers "no copy in the
checkout, **or** acquiring it failed"; and a stated fail-closed answer for `accepts_branch_name` /
`accepts_identity`, a predicate that cannot judge answering no, since one failing closed refuses a legal
name at worst while one failing open carries an unjudged identity into every operation that writes. One
token is added, the precondition reason `checkout_unreadable`, for `detect_mode` and `current_branch` —
a backend that cannot read the checkout establishes no precondition either way, and reporting it as
`no_current_branch` would name a state the backend never established. The output name is
`pr_state_unavailable` on Section 4.3's own distinction — the engine knows exactly which branch and
cannot get the answer, so it is the unavailable half; `base_absent` is the model for the form and not
for the word, absence being a fact about the checkout and this a failure to establish one, and `unknown`
invites "to whom". Section 11 is repaired in the same change and not as tidying: it is the section
telling a consumer what it may rely on, it said the network-touching capabilities are "named and
enumerable (Section 9.1)", and **all three required Section 9.2 capabilities take a credential**, so a
consumer mediating exactly Section 9.1's three does not mediate the forge — an absence in the security
model. Cost recorded: the invariant is quantified over a list, the altitude objection 0075 raised, which
this overrides rather than answers; and `push:failed` still covers an unreachable forge alongside every
other push failure. Relates to 0075 (whose Option D this takes, on the trigger it named), 0073, 0066,
0065 (whose dividing line places the new token), 0057 and 0051. Sibling of 0077. Accepted and applied to
`VCSX-SPEC.md` (Sections 4.1, 8.6, 9, 9.1, 9.2, 11, 12.2, 13.1, 13.2, 13.3), `conformance/vcsx/vocabulary.json`
and `conformance/vcsx/README.md`.

## 0077 — A merge lands the head it read, or reports `merge:head_moved`

**State:** Accepted
**Folder:** [decisions/0077-merge-head-moved/](decisions/0077-merge-head-moved/)

Resolves issue #29. Section 12.3 had `land` read the pull request and then merge it — two calls, so a
window — and Section 4.3's six `merge` rows had no token for a head that advanced inside it, while the
two nearest each routed the caller somewhere wrong: `merge:conflict` sends them to resolve a conflict
that does not exist, the branches having merged cleanly a second ago, and `merge:rejected` blames a
branch-protection rule nobody configured. GitHub names the condition separately (`409`, "Head branch was
modified", with `405` for a pull request that is not mergeable); Forgejo conflates them, which is itself
evidence the condition had no agreed name. The report asked the general question — what does an
operation report when the state it was asked about moved underneath it — and noted that `push` answers
`non_fast_forward` with a class, a gloss naming the recovery, a routing pinned by 13.1 and a bound from
5.6, while `merge` answered nothing. **The argument that decided it is one the report does not make:
the dangerous case is not the merge that gets refused but the merge that succeeds.** GitHub's endpoint
merges whatever the head currently is; its `409` is opportunistic race detection rather than a
guarantee, and the proof is the `sha` parameter's own existence — if the endpoint reliably refused on
any head change, `sha` would be redundant. A decision that only mints a token therefore names a symptom
the forge reports at its discretion and leaves untouched the path where `land` merges content no
lifecycle position inspected — not hypothetical, since for a squash strategy `before:merge` is where the
pull request is read *and* where `pr_to_squash` transforms it (10.3), and 6.6 lets a repository put a
blocking scan there. Options: **A** no token, the condition under `merge:failed` with both misroutes
forbidden (rejected — it passes 0073's built-in-loop test, but that test asks whether the wider token
*fits*, and `failed` is class `error` where this is a state a caller acts on, which is 4.2's definition
of `needs_caller`: a class argument, the bar 0075 said would carry); **B** mint the token and leave the
window (rejected on the argument above); **C** B plus a merge conditioned on the head that was read
(chosen); **D** C softened to best-effort-and-document for a forge without the parameter (rejected —
it converts a correctness property into a documentation obligation, and 9.3 already has the honest
disposition for a capability a backend cannot provide); **E** route the retry through policy rather than
12.3 (rejected on token economy). Both parameters were verified rather than assumed: GitHub's `sha`,
"SHA that pull request head must match to allow merge", and Forgejo/Gitea's `head_commit_id`, confirmed
against Codeberg's live `swagger.v1.json`. So `request_merge` takes `expected_head` and MUST NOT merge a
pull request whose head is no longer that, the mechanism staying the backend's exactly as 0075 stated a
required distinction and left `git ls-remote --exit-code` to the backend; a backend whose forge cannot
condition the merge does not declare the capability (9.3), reusing existing machinery rather than adding
an escape hatch; and where `pr_state` could not determine the head there is no `expected_head` and the
operation reports `merge:failed` rather than merging blind — the interlock with 0076, which lands first
and is where `pr_state`'s value gains the head. **Section 12.3 loops, and that choice is what keeps the
token count at one.** Routed built in, `merge:head_moved` never terminates an invocation, so no `need`
is required and a repository that overrides the routing supplies its own `escalate` reason; left to
policy, 5.4's `needs_caller` default escalates it, 8.2 requires an escalation exactly then, and none of
8.4's needs fits — `integrate_then_retry` names `integrate` — so the engine would have minted two
permanent tokens instead of one. The retry re-enters the *position* rather than the operation, because
that is where the pull request is read and where `pr_to_squash` runs, so a retry that re-merged without
re-gating would reintroduce the defect the conditional merge closes. Surfaced and deliberately not
settled: whether a policy edge's `run_op("merge")` runs `before:merge` at all is ambiguous — 12.2's
pseudocode reads as the sequence owning the gate, while 4.1, 13.1 and 8.6 read as the operation owning
it — which is a Section 5.2 dispatch question over every gated operation rather than a `merge` question,
filed as issue #30; the built-in loop is correct under either reading, and a policy-only routing would
have been correct only under one. The conditional merge also closes the `before:merge` gate window as a
consequence, but that window exists at every position and `before:commit` has no cheap identity for the
state it inspected, which is a `§6.6` correctness claim rather than a registry one and is issue #31. Cost recorded: a capability signature changes, which no reason
addition would have, affordable now and never cheaper — 0073 restructured 9.1 with five new capability
names and an opaque ref handle and the realizing implementation absorbed it in one slice, and the
document is Draft v1. Reconsider for a forge in real use whose merge cannot be conditioned on the head;
Option D is then the fallback, and relaxing a MUST in a `MINOR` is cheaper than a correctness property
nobody could rely on having been true. Relates to 0075, 0076 (which lands first), 0057, 0060 and 0051.
Accepted and applied to `VCSX-SPEC.md` (Sections 4.3, 5.6, 7.2, 9.2, 12.3, 13.1, 13.2) and
`conformance/vcsx/vocabulary.json`.

## 0078 — A dispatch runs the operation's `before:<op>` position

**State:** Accepted
**Folder:** [decisions/0078-dispatch-runs-the-position/](decisions/0078-dispatch-runs-the-position/)

Resolves issue #30, which decision 0077 filed rather than folded in. Two passages described the
relation between a lifecycle position and its operation and did not agree: Section 12.2 wrote
`run_lifecycle("before:push")` and `run_op("push")` as two statements — redundant unless the sequence
owns the position, and Section 12.3 sharpened it by retrying "the lifecycle position rather than the
operation alone" — while Section 4.1 states gating as a property of the operation ("gated at
`before:commit`"), Section 6.6 surfaces a block as "the gated operation's own reason", Section 13.1
asks for that "at every gated operation", and Section 5.6 says "the retried `push` re-gates the
position". The two readings are different engines wherever an operation is reached outside a front-end
sequence, which Section 5.2 makes ordinary and **Section 8.6 already uses as its worked example** — a
`status` entry routing `status:ok` to `run_op` `commit` — without saying whether the gate travels with
it. Under the first reading that `commit` runs with no `scan-content`: not defeated, just never run,
and `before:commit` is the one position Section 3.2 labels in-sandbox precisely because its job is to
inspect content the consumer does not trust. **The filing engine is the argument for calling it an
interoperability defect rather than a wording nit**: it implements the first reading and got there by
where `gate()` happened to be called rather than by deciding, so an implementer who had read all four
passages closely enough to cite them still inherited the reading from whichever sentence the sequence
was built from. One correction to the report: `push`'s `pr_state` guard sits *inside* the operation
(Section 4.1, decision 0076), not at `before:push`, so it travels under either reading and only a
repository's own edges are skipped. Options: **A** the dispatch carries the position (chosen); **B**
the `run_op` *action* carries it while the sequences keep theirs — same observable result, preserves
`ship`'s unconditional `before:commit`, rejected because it makes `run_op` name two things and makes
gating a property of each dispatch path rather than of the operation, which is the shape decision 0076
rejected one layer down when it stated the answer-domain rule over the whole capability list rather
than per capability; **C** state the first reading and report a policy binding both a `before:<op>`
hook and a `run_op` edge to that operation (rejected — Section 6.6's surfacing then has to be realized
for a position no operation ran, and a documented bypass is still a bypass); **D** A plus a per-edge
`gated = false` (rejected — permanent schema for the exact condition being removed). **The consequence
is recorded rather than left to be discovered**: Section 12.2 ran `before:commit` above its dirtiness
guard, so under A a clean working tree enters no position at all. That is principled — a position
gates an operation, and where none is dispatched there is nothing to gate — and empirically empty: the
gate is a Section 6.6 hook that reads the working tree by running in it, so on a clean tree an
inspecting hook can only pass, and the run that disappears is observable only to a hook doing something
Sections 6.6 and 10.4 do not sanction. The filing engine pins the old behavior in
`flow::ship_runs_the_commit_gate_even_when_there_is_nothing_to_commit` with a comment naming exactly
this, and it pins the letter of Section 12.2 against three normative passages that say the opposite. A
`run_op` edge at `before:<op>` naming that same operation now loops; Section 5.6's bound ends it and
gains a sentence saying so, static detection being refused on Section 5.6's own "the bound is a count,
not a cycle detector". No token, no `need`, no configuration key: `conformance/vcsx/vocabulary.json` is
verified unchanged. Lands before 0079, which needs a position every dispatch runs for its invariant to
attach to. Relates to 0077, 0076, 0067, 0060 and 0053. Accepted and applied to `VCSX-SPEC.md` (Sections
4.1, 5.2, 5.6, 6.6, 8.6, 12.2, 12.3, 13.1, 13.2) and `conformance/vcsx/README.md`.

## 0079 — An operation acts on the state its position inspected

**State:** Accepted
**Folder:** [decisions/0079-gate-inspects-what-proceeds/](decisions/0079-gate-inspects-what-proceeds/)

Resolves issue #31, which decision 0077 filed alongside #29 and kept separate: #29 was a Section 4.3
registry claim and this is a Section 6.6 correctness claim. Section 6.6 makes a `before:*` hook a
**gate**, and a gate is only a gate if what it inspected is what proceeds — yet at every position the
gate inspected a read and the operation performed its own afterwards. 0077 closed one row, for `merge`
alone, and closed it by adding an argument rather than by stating a rule, which worked because a pull
request has a head: a cheap, forge-native identity for the thing inspected. Two corrections to the
report's table came out of the analysis: `before:create_pr` is **already closed by construction**,
since the engine composes the title and body once and hands the scanned values to the capability, so
it needs one sentence in Section 10.4 rather than a mechanism; and `before:push`'s window is the
branch tip, not the pull-request state, decision 0076 having put that read inside the operation. What
made merely documenting the window insufficient is an argument from the filing engine: **the gate is a
hook the engine runs, so the engine cannot know what it inspected** — there is nothing to compare
after the fact, and a worktree identity taken at the position is the only thing that can close the
window from inside the engine, which is also why handing the burden to the consumer would not
discharge it. Ruled out before the options: scanning the created commit and blocking by discarding it,
which Section 11's no-drop rule forbids. Options: **A** state the invariant and close every closeable
position, adding a second token and a `push` signature (rejected — the largest permanent surface any
of these issues has asked for, buying a residue the argument below already bounds); **B** state the
invariant, close `before:commit`, argue the residue (chosen); **C** state the limit and close nothing,
which is Section 11's own stance and which the report explicitly allows (rejected — the failure stays
invisible in the envelope, which is exactly what 0076 refused one layer down). **A claim was corrected
in the drafting and is worth keeping**: the first draft said both checkout modes supply the identity
naturally, true for `jj`, whose working copy is itself a commit, and false for `git`, where
`write-tree` needs the index to match and excludes untracked files that Section 4.1 requires a
`commit` to capture. `git` can still close it, because `commit` there is `add -A` then `commit` and
`git commit` commits *the index* — so the index is the atomicity boundary — but the two sub-shapes
available trade a side effect against closure: `add -A; write-tree` yields an immutable tree object at
the cost of mutating the index on invocations the gate may then block, while a digest over status,
diff and untracked hashes has no side effect and leaves a narrow window. **The specification does not
choose**, stating the required distinction and leaving the mechanism to the backend as 0075 did with
`git ls-remote --exit-code` and 0077 with `sha`, and Section 9.1 claims nothing about the value being
naturally available, because an implementer who believed that would look for something that is not
there. What it does fix is the boundary: a backend MAY write to its own staging or bookkeeping state
to derive the identity, MUST NOT thereby change what a `commit` would capture, and MUST document the
effect where it writes. The residue is argued rather than shrugged at: once `before:commit` is
binding, a `push` whose tip advanced sends commits this engine gated, plus the mechanical merge
commits `integrate` and `pull` write from the resolved base and the branch's own counterpart, so what
the window admits is bounded by the position one operation earlier, and what is left is a writer
outside the engine, which is the consumer's boundary. Section 12.2 loops on 0077's argument, keeping
the count at one token: routed built in, `commit:worktree_moved` never terminates an invocation and
needs no `need`, and a worktree written to between every attempt ends at the flow bound, which for a
caller still writing is the correct report. Cost: one reason token, one capability, one signature —
half of option A and the same shape 0077 paid. Reconsider if `before:push`'s residue is shown to admit
content the commit gate did not see; option A is then the fallback. Relates to 0077 (whose
`expected_head` this generalizes), 0078 (which lands first), 0076, 0075, 0063 and 0057. Accepted and
applied to `VCSX-SPEC.md` (Sections 4.3, 5.6, 6.6, 7.1, 9.1, 10.4, 12.2, 13.1, 13.2),
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.
