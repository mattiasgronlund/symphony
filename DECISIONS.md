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
and not closing the per-session CPU-governance question this decision leaves open. Proposed; finding
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
Accepted; reasoning recorded. The `SPEC.md` framing edits are deferred to be applied in step with
decisions 0028–0032, whose still-`Proposed` framing 0027's spec text forward-references.

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
Depends on 0027 (Accepted). Accepted; reasoning recorded. The `SPEC.md` edits are deferred and
applied in step with the companion `vcsx` spec (so contract names stay identical across both
documents) and decisions 0029–0030, which 0028's spec text forward-references.

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
0023/§15.3 and 0026. Depends on 0027 (Accepted). Accepted; reasoning recorded. The `SPEC.md` edits are deferred and applied with the companion `vcsx` spec (0028) and
decisions 0030–0031, which `repo.policy.toml` houses.

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
0028 (both Accepted). Accepted; reasoning recorded. The `SPEC.md` edits are deferred and applied in
step with the companion `vcsx` spec (0028) and decisions 0031–0032, which share its triggers/actions.

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
0030 (both Accepted). Accepted; `SPEC.md` edits deferred (batched with 0028's `vcsx` spec and 0029).

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
supplied. Relates to 0003/0007/0022/0030/0031. Depends on 0027, 0030 (both Accepted). Accepted;
`SPEC.md` edits deferred (batched with 0028's `vcsx` spec and 0029–0031).

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
