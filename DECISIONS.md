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
for the record). A `Superseded` chapter names the decision that replaced it, as
`Superseded (by NNNN)`; unlike `Rejected`, a superseded decision may have been sound and parts of it
may survive in its successor (decision 0033). A State MAY carry a parenthetical naming a later
decision that revisited *part* of it without replacing it — the State itself stays one of the four,
since a decision still standing is still `Accepted`.

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

**State:** Superseded (by 0092)
**Folder:** [decisions/0062-engine-remote-selection/](decisions/0062-engine-remote-selection/)

Superseded in *placement* only, and by an argument this decision could not have reached: decision
0092 shows that the values needed to obtain a repository cannot be configured inside it, which moves
`[engine] remote` to the consumer along with the backend selection whose repository-ownership 0062
cited as its own support. What survives intact is the invariant this decision was really about — the
capabilities that take a `remote` are exactly the version-control operations Section 3.2 places
host-side — and the conformance hole it closed, since two conforming engines given the same
configuration still push to the same place. What is lost is the fork case 0062 left explicitly out of
scope, which now needs a read/write remote pair rather than a repository-owned key.

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

**State:** Superseded (by 0129)
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
`match_edge` clarifications. Applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 12.1, 13.1,
13.2) and the corpus (`match-edge.json` gained `unscoped_edge_matches_inside_a_from_context`,
`scoped_edge_wins_over_unscoped_edge_in_its_context`, and `ladder_outranks_the_from_context`).
**Superseded by 0129** (`Superseded` state per 0033): 0129 removes the from-context from the engine's
matching entirely, so the mixed configuration this decision exists to adjudicate — a scoped edge and
an unscoped one over one trigger — can no longer arise in the executor. This was sound when made and
answered the question a real engine implementation posed; what makes it moot is that its motivating
scenario, "a repository running a transition graph", is the scenario 0122 moved out of the executor,
`tracker.transitions` being consumer-read and keeping its own `(from, on)` key. Its analysis survives
its ruling: the finding that the from-context sits *inside* the ladder rather than around it is what
0129's reconsideration trigger would need again.

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
**Revisited by 0080**: that edge is now refused at validation as `position_cycle`, and Section 5.6's
sentence naming the loop is replaced by the boundary. The static detection declined here was cycle
detection over the policy graph, which Section 5.6 does rule out; 0080's check is over a subgraph in
which no cycle can be conditional, so the argument this decision rested on does not reach it. The
chosen option above is untouched.

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

## 0080 — A cycle of lifecycle positions is refused at validation

**State:** Accepted
**Folder:** [decisions/0080-position-cycle/](decisions/0080-position-cycle/)

Resolves issue #33, filed against decision 0078's follow-through rather than against the
specification as it stood: an edge reading `on = "before:commit"`, `do = "run_op"`, `op = "commit"`
validates — every clause is a known token and the edge carries the argument its action needs — and
only becomes reachable once 0078 puts the position inside the dispatch. Then the dispatch runs the
position, the position dispatches the operation, and the filing engine measured **sixty-four
dispatches and zero operations**, ending at `needs_caller` with the `flow_exhausted` need, whose
gloss says the graph does not converge or the remote is moving faster than the engine can follow —
neither, since no remote was consulted and nothing was retried — and with `op`, `reason` and `class`
null (Section 8.2), so the envelope names neither the position nor the edge and the only field that
could is `Implementation-defined`. It is also **the migration hazard from the reading 0078
replaced**, where the same edge meant "commit now" and worked, so the population most likely to meet
it is the one upgrading. 0078 declined static detection on Section 5.6's "the bound is a count, not a
cycle detector"; that paragraph is right and is not weakened here, but **it also names a measure** —
"what separates a converging flow from a looping one is how many operations it takes" — and on this
shape the number is zero on every traversal, so the measure is not merely unsatisfied but undefined.
The discriminator that falls out is mechanical: every cycle Section 5.6 defends turns on a **typed
operation result**, a report about state outside the engine that may differ next traversal, while a
lifecycle position is matched exactly, has no class fallback and binds at most one edge, so a cycle
made only of positions turns on nothing and cannot converge on any checkout against any remote —
refusing it is a check over a subgraph in which no cycle can be conditional, not the detector that
section rules out. Two corrections to the report as filed, both from the same analysis: the
discriminator is not "the operation's own position", and **the defect is a family** — `before:commit`
→ `run_op push` with `before:push` → `run_op commit` has the same property while no edge names the
operation its own position gates, so a rule shaped around the one-edge spelling misses it. Options:
**A** validation refuses it, one Section 6.10 reason `position_cycle` (chosen); **B** the dispatch
refuses a re-entrant position with the universal `failed` (rejected, and the rejection was
*measured*: against `before:push` → `run_op integrate` with `integrate:ok` → `run_op push`, the
filing engine's guard reported `error`/`push:failed` after `[integrate]` where the unguarded run
completed `ok` at `create_pr:created` after `[integrate, integrate, push, push]` — the predicate
"this operation's own position is on the stack" is not the claim "this flow cannot terminate", and
Section 8.6 independently rules out routing a configuration defect through the result channel, since
the universal `failed` "names no condition" and a repository binding `#error` to `escalate` would
turn a typo into an escalation to a person); **C** absorb the edge as satisfied by the dispatch
already in flight, the only option preserving the upgrading repository (rejected — it makes `run_op`
name two things, which is the ground 0078 rejected its own option B on, it never tells an author the
edge was defective, and it covers only the one-edge form); **D** keep the bound and sharpen the
report (rejected as an answer — `detail` is `Implementation-defined`, and it still diagnoses
convergence for a policy that never had a chance to converge; worth doing separately); **E** skip the
position on re-entry (rejected by the reporter before filing — it is the in-sandbox bypass 0078
exists to close, against Sections 6.6 and 10.1). The split the specification now states is that a
flow which **cannot** converge because it reaches no operation is refused before anything runs, and
one which **does not** converge while running operations is held by the bound, which is what a count
is for; an engine carrying the runtime guard removes it rather than keeping both, since what remains
for a stack-shaped predicate to catch is a terminating flow it would wrongly refuse. Cost: one
configuration reason, permanent within a `MAJOR`, and cheaper than the report assumed — Section 8.5
admits a new configuration reason in a `MINOR` and Section 6.10 states it is absorbed by the
`usage_or_config` status without an existing class edge. **The migration cost is named rather than
mitigated**: the refusal is unconditional, so a repository carrying the edge on a branch that never
commits is refused on every invocation, including a `status` that would have completed — accepted
because the edge means nothing under 0078, the operator is told before any operation has run, and the
alternative that preserves those invocations preserves them by deciding what the author meant. The
boundary lands as four `policy-validation` vectors rather than as prose alone — a one-position cycle
and a two-position cycle refused, a position edge to an operation the cycle does not return from and
a cycle through a typed result accepted — which is what stops the next engine deriving the predicate
the filing engine derived. Reconsider if a position-only cycle is found that no invocation could
enter, making its unconditional refusal cost a working run; the narrower rule would refuse only a
cycle reachable from an entry point, at the cost of making validation depend on the entry, which
Section 6.10 never does today. Revisits 0078's incidental refusal of static detection, recorded there
append-only, leaving its chosen option untouched; relates to 0079, 0066, 0060 and 0056. Accepted and
applied to `VCSX-SPEC.md` (Sections 4.1, 5.6, 6.10, 13.1, 13.2),
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/policy-validation.json` and
`conformance/vcsx/README.md`.

## 0081 — A hook bound is a bound on a unit, not on the flow

**State:** Accepted
**Folder:** [decisions/0081-hook-bound/](decisions/0081-hook-bound/)

Resolves issue #35, and resolves the **corrected** report rather than the filed one: the reporter
withdrew the opening claim that the concept of a bound is absent, since Section 5.6 already admits
"further bounds on a running flow, a wall-clock deadline for example" and requires each published.
Two things survive the correction and are what this decision answers. **It is a `MAY`**, so an engine
that never bounds a hook conforms while a repository hook that never returns wedges it — issue 4's
argument one layer down, which Section 5.6 has already accepted for the flow. And **`flow_exhausted`
is the wrong diagnosis, which Section 5.6's "same result" sentence forces**: Section 8.4 defines that
need as the hold the executor imposed on a graph that does not converge, while a hook that never
returns is one named unit at one named position that stopped answering, and Section 8.2 nulls `op`,
`reason` and `class` for a flow the executor stopped, so the envelope names neither. The distinction
drawn is that Section 5.6's further bounds are bounds on **a running flow** — they stop the executor
and end the invocation — while a hook bound bounds **one unit at one position** inside a dispatch:
the flow is not stopped, and the gated operation's result re-enters the machine, which is what the
machine is for. So the answer is an operation reason rather than a `need`, and Section 5.6's sentence
is scoped rather than contradicted. Bounding becomes REQUIRED, the value `Implementation-defined` and
published (Section 13.3), with a floor of 600 seconds on Section 5.6's own gloss — the number is
arbitrary, that it is fixed is not, because it is what keeps two engines agreeing on every hook that
answers within it, and a repository's `before:commit` gate can be its whole test suite. Section 4.3
gains **one** universal reason for gated operations, `hook_unanswered`, class `error`, covering the
bound elapsing, a unit that could not be started, and an answer the engine could not read — one token
across this issue and #38 rather than one each, because **a block is something the hook did** and a
hook that never started decided nothing, so spelling it as a block puts a gate that ran and refused
and a gate that is broken on `<op>:failed` together and leaves a repository routing `commit:failed →
park` unable to tell them apart. Which of the three occurred is diagnosis and belongs in `outputs`.
`blocked` keeps a gate that answered `needs_caller`, `failed` a gate that answered with an `error`
result. Options: **A** a unit bound with a reason of its own (chosen); **B** reuse `<op>:failed`
(rejected on the conflation, though Symphony's own Section 9.4 folds failure and timeout
deliberately, which makes it defensible rather than merely cheap — Symphony's hooks are not routed
through a machine that can branch on the difference); **C** keep Section 5.6's uniformity and mint a
`need` (rejected: a hold routes nothing, Section 8.4 nulls `op` at a position whose operation has not
run, and it treats a bound on one unit as a bound on the flow); **D** a repository budget clamped to
an operator ceiling (not rejected on merit — it is right if one consumer-owned number proves wrong
for the spread between a web request and a test suite — but deferred, because Section 6.1's
forward-compatibility rule makes it addable in a `MINOR` without breaking a policy written today);
**E** leave it a `MAY` (rejected). The bound is the consumer's and `[hooks]` gains no key: the
in-sandbox half is worktree-sourced by design, so a bound written there is a bound the bounded thing
sets, and Section 3.2 denies the engine the one fact — which revision a value came from — that would
let it admit the key host-side and refuse it in-sandbox; a `timeout_ms` a repository writes is
ignored under Section 6.1. An `after` hook that exceeds the bound is killed, the flow continues
unchanged, and the fact is reported in `outputs` on Section 5.4's no-silent-drops principle. **The
limit is stated rather than glossed**: killing the unit does not end what the unit started, so a hook
that leaves a grandchild holding the pipes is read from until the bound elapses — the invocation is
bounded, the machine is not. A `[hooks.<name>]` declaring no `run` is judgeable from the document and
is `malformed_policy` at validation, minting no token, while whether the named unit exists is a
property of the worktree and stays `hook_unanswered`. Cost: one reason, permanent within a `MAJOR`,
absorbed by the `#class` fallback so no consumer changes; and a repository gains what B cannot give
it — "if the gate does not answer, park" is an edge somebody can write. Reconsider if one number
proves wrong for the real spread, or if the `outputs` report of a killed `after` hook proves to have
no consumer. Review on PR #40 found the `after` half covering **one** condition where the gate half
covered three — a result-triggered hook the engine could not start was neither `hook_unanswered`
(that reason is `(any gated)`) nor reportable under `unfinished_hooks` (scoped to hooks stopped at
the bound), so it was silently dropped, which is what Section 5.4 forbids and what that bullet cites
as its own reason for reporting the bound case; both are widened to "gave the engine no usable
answer", keeping the division by whether anything waits rather than by which condition occurred.
Relates to 0084 (which takes this token rather than minting its own), 0060, 0057, 0056
and 0066. Accepted and applied to `VCSX-SPEC.md` (Sections 4.3, 5.6, 6.6, 6.10, 8.2, 13.1, 13.2,
13.3), `conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/policy-validation.json`,
`conformance/vcsx/README.md` and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0082 — `[messages.squash] strategy` defaults to `merge`

**State:** Accepted
**Folder:** [decisions/0082-squash-strategy-default/](decisions/0082-squash-strategy-default/)

Resolves issue #36, which is two reports whose answers meet. Section 9.3 splits an undeclared
capability at "determinable before the policy runs", and enumerating the descriptor fields against
the policy keys yields **exactly one row** — `[messages.squash] strategy` against a forge's declared
merge strategies, Section 9.3's own worked example. Section 8.6 then says a configuration error is "a
property of `repo.policy.toml` alone, detectable before any argument or checkout is in hand", which
cannot be exactly true, because determining that row needs the selected backend's descriptor; two
operative sentences of the same two sections say "the invocation" and "before the policy runs"
instead, so one section says the thing twice and differently, and an engine taking the literal
reading determines nothing, satisfies "where determinable" vacuously and fails the only example given
— observably, since the same policy is exit `2` before anything runs on one engine and
`merge:unsupported` at exit `20` on the day someone lands on the other. Meanwhile Section 6.8 gives
`strategy` three tokens, an example value and no statement of what an absent key means, while
Section 13.3 enumerates the backend's default remote and carries nothing for Section 6.8 — the
evidence this is an omission rather than a delegation. **A correction the decision records against
its own first draft**: Section 11's "A `rebase` or `squash` merge strategy is not an exception: it
writes to the base branch" does *not* rank the strategies — it scopes the work-branch guarantee,
saying a merge strategy touches a different branch and so is not a counter-example to the promise —
so citing it for the default would leave the first implementer to read Section 11 finding it says the
reverse. The real asymmetry is one step further in: of the three, `merge` is the only one under which
the commits the engine wrote, each gated at `before:commit` and attributed to the caller-supplied
identity, survive into durable history as written, where `rebase` re-parents them and `squash`
collapses them into a commit the code host authors; defaulting to the strategy that preserves what
the engine gated is the posture the document states wherever it states one. That is an argument from
the document's temperament rather than from a sentence in it, and is written as such. Options: **A**
fix the default at `merge` and repair Section 8.6's sentence (chosen); **B** publish the default as
`Implementation-defined` with a Section 13.3 row, as 0062 did for `[engine] remote`, and move
`capability_unsupported` into Section 8.6's registry where it becomes entry-scoped as 0074 scoped the
identity precondition — genuinely attractive, since refusing a `ship` over a strategy only `land`
uses is real over-refusal, but rejected because 0074's scoping was right for a **per-invocation input
the caller supplies** while a merge strategy is a property of the repository's way of working, so B
moves a document error into the invocation registry and blurs the distinction 0056 leaned on, and
because its cost is the one least worth shipping: two conforming engines writing different durable
base-branch history from the same file, which publishing makes discoverable rather than
interoperable; **C** an absent key means the code host's default (rejected twice — it makes durable
history depend on forge settings outside the repository's file, inverting Section 6.8's premise, and
gives `request_merge` an "unspecified" strategy, a capability argument that cannot say what it means,
which is the shape 0076's answer-domain rule forbids one layer down). Section 8.6's boundary is
repaired rather than reversed: a configuration error is judged from the policy document together with
what the engine holds independently of the invocation — its configured backends' descriptors, its own
defaults, the actions a consumer can effect and the units it bound — while a precondition failure
needs the invocation's arguments and the checkout; and a descriptor field a backend can answer only
once it has opened the checkout is explicitly *not* such a fact, so a policy requiring it keeps
Section 9.3's first-use disposition. **The cost is conceded and fenced**: an absent `strategy`
becomes determinable, so among the required policy keys Section 9.3's first-use half loses its only
producer, undoing an asymmetry at least one implementation deliberately preserved so
`merge:unsupported` kept a real test — the asymmetry was always uncomfortable, since it is odd that
spelling out the default changes whether you are refused, and it goes. What follows is a
documentation obligation rather than a shrug: Section 13.1 states that a Conformance Statement
claiming that half **names the engine-added operation or optional capability it demonstrated it
against**, so the result is not the overclaim shape — a mechanism described by one true sentence and
read as a general guarantee. Cost: fixing a default is a behaviour change for an engine that chose
otherwise, inside a `MAJOR`, and `merge` is itself not guaranteed by a descriptor, so a forge that
cannot perform a plain merge fails on a default nobody wrote — which the repaired check catches at
validation rather than on the day someone lands. Reconsider if a required key is added whose
contradiction with a descriptor is genuinely undeterminable before the policy runs, or if the
wholesale refusal costs operators working invocations, which is B's argument arriving as evidence.
Relates to 0062, 0074, 0076, 0056 and 0070. Accepted and applied to `VCSX-SPEC.md` (Sections 6.8,
8.6, 9.3, 13.1), `conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0083 — The push guarantee is quantified over the effect

**State:** Accepted
**Folder:** [decisions/0083-push-effect-and-read-only/](decisions/0083-push-effect-and-read-only/)

Resolves issue #37. Section 3.3 requires `jj` as a checkout mode and Section 9.1 is the surface a
backend adapts through, so until a second backend exists nothing tests whether that surface is
VCS-neutral or is git's mechanics written down; writing one against jj 0.44.0 produced two absolutes
jj cannot satisfy literally. `jj git push` always leases —
`--force-with-lease=refs/heads/<branch>:<last fetched>` on the create and update paths alike,
observed on the argv — so the obvious mediation for Section 9.1's "never a force push" refuses
**every** push a jj backend makes, and the reading decides whether a conforming engine can drive a jj
repository at all, in the section (Section 11) a mediating consumer implements against. **The
report's own "satisfied in effect" verdict, and this decision's first draft, were wrong, and the
correction is the substance of the decision**: a plain push refuses when the update is not a
fast-forward — exactly when commits would be dropped — while a lease refuses when the remote ref is
not at the expected value — when the remote moved. They diverge in the case the guarantee exists for:
the engine observes the remote work branch at `X`, the local bookmark sits at `W`, an ancestor of
`X`, because something outside the engine rewound it (Section 11 guarantees the engine never does
this, not that nobody does), the remote is still at `X` so the lease matches, and the push
force-updates `X → W`, dropping every commit between. A plain push refuses that; the lease permits
it. So a specification blessing the lease would have blessed the destruction of remote history on the
work branch, and the filing implementation's own jj plugin has no ancestry guard. Options: **A**
quantify over the effect and say nothing about mechanism (chosen) — the engine MUST NOT cause a push
that drops, rewrites or re-parents a commit already on the remote work branch, and the phrase "force
push" leaves Sections 9.1 and 11 alike, so no backend can argue from flags; **A′** the same
requirement plus a sentence blessing leases (rejected on the counterexample, and it was the drafted
recommendation); **B** quantify over observation — a push MUST NOT succeed where the remote work
branch carries a commit the engine did not observe (rejected: it permits the same case, because the
engine *did* observe `X`; it is quantified over observation where the hazard is destruction, so it is
narrower than what consumers rely on rather than stronger); **C** keep the absolute and declare the
transport in the descriptor (rejected — an absolute in prose and a conditional in data, which is
issue #36's pattern one section over, and it relocates the burden onto every consumer, where the ones
that do not read the field are exactly the ones the guarantee existed for). **Who pays is stated**:
an unconditional lease becomes a genuine non-conformance rather than a concession, and the repair is
cheap and backend-side — before invoking `jj git push`, check the local bookmark is a descendant of
the observed remote bookmark and report `push:non_fast_forward` without spawning where it is not,
which routes to `integrate` and retries within the flow bound, so no machinery is added. The cost —
the guarantee is no longer readable off the argv — is real and small: Section 11 already directs the
guard at the pinned refspec, and a guarantee readable off the argv was never the guarantee but a
proxy that held while git was the only backend. The second ask is **one repair rather than a
choice**, because no alternative was offered and the wording exists already scoped one capability too
narrow: `worktree_revision()`'s allowance to derive an answer by writing to the backend's own staging
or bookkeeping state, without changing the content a `commit` would capture and with the effect
documented, is stated over the whole capability list, and Section 4.1's "Read-only" is defined as
quantifying over the history, the remote and the content a `commit` would capture — the shape issues
26 and 28 both had, where a rule holding for one capability and not its neighbour is the next report.
Reconsider if a backend appears whose transport can satisfy the effect requirement only by a
mechanism the document would have to name, or if the read-only definition proves too permissive for a
consumer mediating by filesystem observation. Review on PR #40 found the read allowance introducing a
**new undefined absolute in the place this decision had just removed one**: it said a backend writing
bookkeeping state MUST NOT write to "the history", a term nowhere defined here, and `jj status`
snapshots the working copy into the working-copy commit — writing a commit object and moving a ref —
so the literal reading defeats the very backend the allowance was written for. Both ends now quantify
over three named things: the content a `commit` would capture, the commits reachable from the work
branch or the resolved base, and what the remote holds; a commit no branch the engine named reaches
is not one of them, because what the reads report against and what a `push` publishes are branches. A
second round found that repair **conditional on an arrangement the document did not name**: measured
on jj 0.44.0, a work bookmark kept on the working-copy commit is carried along when a read re-records
it, so the commits reachable from the work branch change and the revision a `push` would publish
moves — the read-only test failing on a read, by the mechanism the allowance blesses — while a
bookmark one behind holds. Section 9.1 now requires a backend that records the working tree as a
commit to keep that commit outside what the work branch reaches, which is checkable and is a property
of the backend rather than of the VCS. Relates to 0073, 0079, 0076 and 0063. Accepted and
applied to `VCSX-SPEC.md` (Sections 4.1, 9.1, 11, 13.1, 13.2, 13.3), `conformance/vcsx/README.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0084 — Every condition gets a home, and one exit code names "no result"

**State:** Accepted
**Folder:** [decisions/0084-no-result-channel/](decisions/0084-no-result-channel/)

Resolves issue #38. Section 8.2 opens "Every invocation returns one structured result" and
Section 8.3 fixes four exit codes mirroring the four statuses, adding that the JSON result is emitted
regardless of exit code — which presumes a result. Several paths reach no envelope: a repository unit
that will not run or answers outside the shape the engine fixed (Section 6.6 makes that form
`Implementation-defined`, so a violation is outside every registry upstream owns by construction);
`body_source = "template"` with no template unit bound, which Section 4.3's `unsupported` does not
cover because a template is neither a plugin nor a capability; a command line the front-end cannot
read, since neither Section 6.10 nor Section 8.6 names a condition of the argument *encoding*; and a
hook that exceeded a bound. Section 8.3's stated purpose is a caller branching **without parsing**,
and it fails for exactly these, differently on each engine; decision 0065 already declined "these
belong to the invocation contract" and built Section 8.6 instead, reasoning about the code itself,
and that argument applies unchanged where nothing ran at all. **The strongest argument for absorbing
is not registry hygiene but where the refusal happens**: Section 12.2's `ship` runs `commit`, `push`,
then `create_pr`, so a `template` body source with nothing bound is not discovered until a body is
composed — today that misconfiguration **publishes a work branch and then dies with empty stdout** —
while `set_state_unbound` refuses before anything runs, and this is the same shape one seam over.
Options: **A** give the conditions homes and reserve one code for the residue (chosen); **B** the
channel rule alone — a code outside the four means no result, stdout empty (elegant and total for a
consumer, and the winner if the question were only the channel, but rejected on its own stated cost,
that each engine still decides which conditions are faults, which leaves a Conformance Statement
unable to say anything useful, and it keeps the published-then-abandoned branch); **C** reserve a
code and stop (B plus a number, rejected on the same ground plus an exit code spent on a distinction
whose repair is identical either way: read stderr). A lands in four parts. `template_unbound` joins
Section 6.10, **with Section 6.10's judgement input widened and stated** — `set_state_unbound` is
judged from the consumer-supplied Section 5.2 actions, while a template unit is a Section 10.2
repository unit, so validation is stated to be judged from the document, what the engine holds
independently of the invocation, the actions a consumer can effect **and the repository units it
bound**, without which implementations diverge on whether the condition is determinable at all, which
is issue #36's ambiguity one section over. The hook conditions take decision 0081's `hook_unanswered`
and this decision mints nothing for them, because reading a hook that never started as a *block*
reintroduces the conflation 0081 exists to undo — a block is something the hook did. An unreadable
command line produces a **real envelope**: `usage_or_config`, exit `2`, `op` and `class` null,
`reason` carrying `arguments_unreadable`, a Section 8.6 precondition reason under that section's
repaired boundary (0082) since it is judged from the invocation's arguments and nothing else, and the
one precondition established **before** validation rather than after it, because an engine that
cannot decode its arguments cannot locate the policy it would validate — a carve-out stated rather
than left to contradict the ordering rule silently. And Section 8.3 reserves exit `1` for an
invocation that produced no Section 8.2 result, stdout empty and the diagnostic on stderr, with **any
other code meaning the same** — the load-bearing half, since it covers a panic, a signal and an
out-of-memory kill without the specification predicting every way a process can die — plus the
property that makes the rest safe: on every path that produces a result, stdout carries exactly one
JSON object and nothing else, which was the filing engine's own rule and which nothing in
Sections 8.2 or 8.3 required. Deliberately not enumerated: the membership of the set of ways a
repository unit can violate the engine's contract stays the engine's, because Section 6.6 makes that
contract `Implementation-defined` — the ask was about the channel. Cost: one configuration reason,
one precondition reason and one exit code, all permanent within a `MAJOR`, and Section 8.5 admits the
two reasons in a `MINOR` with the `usage_or_config` status absorbing them. Reconsider if a runtime
makes exit `1` unreadable as a reserved meaning (the any-other-code clause still holds), or if
`template_unbound` proves to need a checkout to judge, which would mean the judgement input was
widened in the wrong direction. Review on PR #40 found four defects in the follow-through, none
changing the chosen option and all recorded append-only in `Background.md`: the judgement input was
stated as a **closed** list that excluded `version_floor_unmet`'s own input, the running engine
version — this decision's contribution reproducing, one section over, the failure 0082 diagnoses;
`policy-validation.json`'s `given` named a *different* four from Section 6.10's, so two authoritative
lists disagreed; Section 8.5 nowhere said a reserved exit code was permitted, though it fixes the
exit-code mapping as major-stable and enumerates what a `MINOR` may add; and Section 8.6's opening
sentence was false for `arguments_unreadable`, the one row it does not cover, with the carve-out
stated three paragraphs later. Relates to 0081, 0082, 0065, 0056 and 0075/0076. Accepted and applied
to `VCSX-SPEC.md` (Sections 6.10, 8.1, 8.3, 8.5, 8.6, 13.1, 13.2), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/policy-validation.json`, `conformance/vcsx/vectors/exit-codes.json` and
`conformance/vcsx/README.md`.

## 0085 — The forge repository coordinate is the consumer's

**State:** Accepted (re-evaluated in part by 0091; principle extended by 0092)
**Folder:** [decisions/0085-forge-repository-coordinate/](decisions/0085-forge-repository-coordinate/)

Resolves issue #39. Section 6.2 assigns the forge **selection** to the repository and the
**credential** to the consumer, and nothing between them says how the selected backend learns which
repository on the host it is talking about: Section 9.2's capabilities take a head, a base, a title,
a body, a pull request, a strategy and a head, and none takes a repository; Section 8.1's common
arguments name four things and a coordinate is not among them; deriving it from the checkout is
foreclosed twice (Section 1.3's no-provisioning and Section 6.2's refusal to infer from the upstream
binding); and Section 3.3's "remote slug" is the one place the document names the concept, a
requirement with no capability behind it. The **subprocess encoding** is where it stops being
theoretical: Section 8 says the contract is the same either way and only the encoding differs, an
embedded driver can be handed a coordinate through a constructor, and a subprocess front-end has
nothing to encode — so a repository setting `forge = "github"` cannot be run by a conforming
subprocess front-end at all, including `push` and `status`, because Section 4.1 has both read the
pull-request state where a forge is configured: six of ten entry points. The service root was settled
first and on a security argument — it is not derivable from a host name, and Section 3.2 leaves the
sourcing rule to the consumer, so a root read from a file a consumer sourced from the worktree is a
credential presented to a host the worktree named — and **that argument does not stop at the root**.
A coordinate derived from the resolved remote's URL reads the checkout's configuration rather than
tracked content, which is better protected than a tracked file, but in the sandboxed-agent topology
the boundary is the worktree, not the checkout: a consumer that exposes `.git` to the agent has
handed it `git remote set-url`, and the engine will then push and open a pull request against
whatever that names, with the consumer's credential attached. Pinning the root to the credential
bounds this to one host, and same-host redirection is still presenting a credential to a repository
its holder did not choose. The credential and its target are one decision; what makes the hazard
possible is letting the two be made by different parties. Options: **A** backend-derived from the
resolved remote with a consumer override (rejected on that argument, but two things in it are kept —
its Section 3.3 argument is textual and is settled here whichever option lands, since nothing says
whether a "slug" is a remote name, a URL or a forge coordinate; and were a capability ever to answer
this it answers the remote's **URL, opaquely**, leaving the forge backend to interpret it, because
parsing an owner and a name out of a URL is service-specific — SSH against HTTPS, ports, nested
namespaces — and a VCS backend has no business knowing a forge's URL grammar, which is the mixing
Sections 9.1 and 9.2 are separate to prevent); **B** consumer-supplied and named in Section 8.1
(chosen); **C** repository-owned as `[engine] remote` became in 0062 (rejected before the sourcing
hazard is even reached, on the fork objection — a remote *name* is checkout-local and identical in
every clone while an owner/name coordinate is not, so every fork and mirror carries a diff in the
file whose purpose is to be inherited unchanged, which is why the analogy to 0062 does not carry).
**B's stated cost is real and does not belong in the specification**: "a human at a prompt supplies
it every invocation" assumes the front-end cannot default it, and it can — from the resolved remote,
exactly as A would — which keeps the derivation on the credential-holding side of the boundary, since
Section 8.1 already makes encodings the front-end's business and an interactive front-end *is* a
consumer under Section 1.1. So this is B's contract with A's ergonomics, and the difference is only
who derives: under A the engine derives from a value the checkout carries and the consumer never
sees, under B the consumer derives and the engine is told — the whole of the security argument.
Section 3.3's sentence is settled as part of the answer: "remote slug" is replaced by the resolved
remote (Section 6.2) and the work branch, and the section states the coordinate is not derived from
the checkout in any mode. Absence where a forge is configured is refused before the policy runs with
`forge_coordinate_missing`, on Section 8.6's own boundary and on 0084's refuse-before-publishing
argument; the engine holds the coordinate **opaque** as it holds the commit identity and the base ref
opaque, so a coordinate a backend cannot use is that backend's first-use `failed` rather than a shape
the engine judged. The credential and the service root stay out of the argument list for the reason
the report gave for excluding the credential — Section 11 has the engine run where they are already
held. **Disclosure, recorded so it can be discounted**: B is also the cheapest outcome for the filing
implementation, whose forge plugin already receives the coordinate at construction, so the
recommendation and the convenience point the same way; the argument stands on the sandbox boundary
rather than on the cost, and the reporter raised the alignment rather than leaving it to be noticed.
Reconsider if front-ends diverge on how they default the argument from the remote — the divergence B
pushes into the front-end is the one thing A would have standardized, and the repair is then a
RECOMMENDED defaulting rule in Section 8.1, not moving the coordinate back across the boundary.
Relates to 0062, 0065, 0073 and 0084. Accepted and applied to `VCSX-SPEC.md` (Sections 3.3, 6.2, 7.3,
8.1, 8.6, 9.2, 11, 13.1, 13.2), `conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0086 — An unanswered gate's condition is named, and the three conditions are tokens

**State:** Accepted
**Folder:** [decisions/0086-unanswered-gate-diagnosis/](decisions/0086-unanswered-gate-diagnosis/)

Resolves issue #42. Decision 0081 split what exceeding a hook bound produces into a routing half —
`<op>:hook_unanswered`, a Section 4.3 reason with a fixed class — and a diagnosis half, which of three
conditions occurred, which Section 4.3 sends to `outputs` "rather than in a token, because the repair
is the same shape in each case". Section 8.2 then does that for one half of Section 6.6's division and
not the other: the non-gating half gets a name, a field list and an absent-or-empty rule
(`unfinished_hooks`), and the gating half gets a clause — "`outputs` carries which condition occurred
for it too" — that **names no key, no shape and no field while requiring the report**. It is the only
fact in Section 8.2 that is REQUIRED and unnamed, on a surface Section 8.5 calls major-stable, and the
failure is silent in the direction that matters: a consumer finds no key it recognizes, concludes no
gate failed, and reports a run whose diagnosis it never saw. There is a second level underneath, which
is the report's second ask: the three conditions are **prose** in both Section 6.6 and Section 8.2, so
`unfinished_hooks` — a named key with a named `condition` field — carries values every engine invents,
and naming the gating half's key alone would move the defect one field deeper rather than close it.
This is 0081's own argument one level below a token: that decision refused to let each engine mint its
own reason because "the token would be chosen independently by every engine", and a key in `outputs`
and the values inside it are in exactly that position. The asymmetry also reads as an unfinished edit
rather than a choice — the review that landed on issue #35 equalized *which* conditions each half
reports and left *where* asymmetric. Options: **A** name `outputs.unanswered_gates` (an array of
`hook`, `position`, `condition`, `Implementation-defined` `detail`, absent or empty where every gate
answered) and fix the conditions as three tokens — `bound_elapsed`, `not_started`, `answer_unreadable`
— defined once in Section 6.6 and used by both keys (chosen; an array because the result re-enters the
machine, so a repository binding `commit:hook_unanswered` to anything that does not end the flow can
reach `before:push` on the same traversal, which Section 5.6 defends rather than refuses); **B** widen
`unfinished_hooks` to both halves, distinguished by a field (rejected — the better shape for a consumer
asking "which hooks broke", and it loses on what the existing key means: it is today exactly the set
nothing else reports, Section 8.2's "non-gating half's mirror of `hook_unanswered`", and widening it
makes the gating members duplicate a reason the envelope already states in `reason`, so a consumer that
read it as "the failures that were not routed" starts filtering and the property that made it worth
naming is gone); **C** `Implementation-defined`, documented under Section 13.3 (rejected — the honest
minimum, and more than the document manages today, but it concedes at the `outputs` level what 0081
refused at the token level, and the Conformance Statement records a *choice* rather than defines a
shared fact, so a consumer reading two Statements to learn two spellings of one condition is doing the
work the registry exists to remove). Reconsider if a second `outputs` key overlapping
`unanswered_gates` appears — a report of every hook run, not only the failures — at which point B's
one-view argument starts costing a join and beats the mirror property; reconsider also if a fourth
condition appears, since the three are exhaustive over *how the engine failed to get an answer* and a
fourth would mean Section 6.6's division is over something else. Relates to 0081, 0051, 0071 and 0059.
Accepted and applied to `VCSX-SPEC.md` (Sections 6.6, 8.2, 13.1, 13.2, 13.3) and
`conformance/vcsx/vocabulary.json`.

## 0087 — A resume re-enters the point that raised the need, and re-reads

**State:** Accepted
**Folder:** [decisions/0087-resume-re-entry/](decisions/0087-resume-re-entry/)

Resolves issue #43. Section 5.5 has an embedded driver bind a resolver and "resume the flow when the
need is met", and Section 5.4 produces an escalation with no `escalate` action having run, since the
built-in default for `needs_caller` *is* `escalate` — so a `before:commit` gate blocks, Section 6.6
surfaces `commit:blocked`, no edge is bound, the default escalates, and a driver resolves. **Where the
flow carries on is written nowhere**, and not only for a gate: the same silence covers every
escalation, including the ones the document's own `ship` routing raises. The filing implementation
resumed by dispatching the operation **without re-entering the position**, so a resolved need ran a
commit a gate had refused and that no gate re-inspected — the failure Section 6.6 exists to prevent one
layer down, where an operation that acted on state no position inspected returns a `done`-class result
for a run nothing gated. One of the report's three candidates closed while it was in flight: decision
0078 put the position **inside** the dispatch, so "dispatch the operation" and "re-enter the position"
are one act, and the implementation's behavior is no longer expressible through a dispatch at all — it
would have to be a resume landing *past* the position, which nothing describes and which Section 6.6
forbids outright for `hook_unanswered`. Options: **A** a resume re-enters the point that raised the
need — re-dispatching the operation whose result escalated, which runs its `before:<op>` position
first, or re-entering the position where an edge there escalated (the null-`op` case, Section 8.4)
(chosen; one rule for every escalation, the same answer for `blocked` and `hook_unanswered`, and the
gate re-run rather than bypassed so neither yields a pass it did not give); **B** the escalation ends
the invocation and the repair is picked up by the next one (rejected — the strongest rejected option,
simplest to specify, removes suspended state and makes both front-ends identical, but it rewrites
Section 5.5 rather than completing it: a driver that can genuinely meet the need must re-invoke, and it
collapses Section 8.4's split between a need a front-end is expected to meet and a hold released out of
band, since under B every need is released out of band, which is Section 8.4's definition of a hold);
**C** the resume point is the driver's, bounded and documented (rejected — it widens front-end
divergence from *which resolver is bound* to *where the executor resumes*, so two drivers run one
`repo.policy.toml` through different operation flows, the property Section 13.1 tests and Section 5.5
claims). Two properties are stated with A and neither is optional. **The count is over re-entry, not
over dispatch**: "a resume's re-dispatch is a dispatch" covers the operation case and leaves the
position case unbounded, because a `before:commit → escalate` edge re-enters a position *inside a
dispatch whose count is already spent*, so a resolver that always resolves would loop there forever —
quantifying over any re-entry puts both shapes on Section 5.6's bound and converges both on
`flow_exhausted`, which is issue #4's property held in the one place this decision adds. **A resume
re-reads**: the value of re-entering is that the position's reads happen again, and an engine that
cached `expected_worktree` or `expected_head` across a resume would hand an operation a stale
expectation, producing the condition decisions 0077 and 0079 exist to report rather than to produce.
Reconsider if a front-end appears that cannot hold a suspended flow across a resolver call, at which
point B becomes the practical answer rather than the minimal one; reconsider also if a need is added
whose remedy is not re-running the raising point, since every need today is met at or before it.
Relates to 0078, 0059, 0060, 0077, 0079 and 0088. Accepted and applied to `VCSX-SPEC.md` (Sections 5.5,
5.6, 8.4, 13.1, 13.2).

## 0088 — An outcome no action disposed of takes the default, and the registry carries each need

**State:** Accepted
**Folder:** [decisions/0088-default-need-per-reason/](decisions/0088-default-need-per-reason/)

Resolves issue #44. Section 5.4 fixes what an **unmatched** operation outcome does, Section 5.6 names
what ends a flow, and Section 5.2 makes the consumer-effected actions emit once — leaving a third case
between them: a result that **matched** an edge whose action neither ends the flow nor re-enters the
machine. `push:non_fast_forward → notify` under a single-operation entry point emits the intent, and
the traversal has nowhere to go. Section 8.2 then requires three things that do not compose: the
decisive result's class is `needs_caller`, so the status is, so an escalation is REQUIRED — and no
`escalate` ran, so nothing named a `need`. The filing implementation's envelope constructor holds
"exactly when" as an invariant and **panicked**: fail-closed rather than wrong, and evidence that an
implementation taking Section 8.2 literally cannot represent a run the specification asks for. The
half that reaches further than the report is the mapping: Section 5.4's built-in default for
`needs_caller` is `escalate` and Section 8.4 says an escalation carries a `need`, and **nothing says
which need for which reason** — already true for the unmatched case, made reachable from a policy edge
by this one. Counted against the registry, there are **17** `needs_caller` results (13 reason-specific
rows plus the universal `blocked` at each of four gated operations); the document fixes 2 of them, in
Section 12.2's routing; the filing implementation invented 6 and defaulted 9 to `human_review`. So an
engine derives 15 of 17 with no guidance while Section 5.5 has a front-end **bind its resolvers by
exactly those tokens** — two engines offering one driver two resolver keys for one condition, which is
what the `need` vocabulary being "part of the public contract" is supposed to exclude. Options: **A**
extend the fail-safe rule from "unmatched" to "no action disposed of", where an outcome is disposed of
by an action that ends the flow or by a `run_op` whose result takes its place, and put the default's
need on Section 4.3's registry as a `Default need` column (chosen); **B** null the operation fields and
end at `intervention` (rejected — reuses `park`'s machinery and needs no mapping, but it drops the
decisive result, which Section 5.4 forbids in the neighbouring case for a reason that does not stop at
whether an edge happened to match, and 0059's ground for nulling a park — no operation asked the caller
for anything — is false here, so the envelope would report a hold the policy never asked for); **C**
refuse the policy at validation (rejected — statically judgeable, and this repository has accepted
static refusal where the refused policies were unrepresentable or nonsense, which these are not:
`push:rejected → notify` means notify then report the failure, and the rewrite is not writable, since
Section 5.4 allows at most one edge per `(from-context, trigger)`, so C removes a policy rather than
repairing its report). The column goes on the **registry** rather than in a Section 8.4 table because
the registry is already keyed by `(operation, reason)` and already generated from
(`conformance/vcsx/vocabulary.json`, decisions 0051 and 0071), so the mapping becomes a field on a
generated record and an upstream rename becomes a compile error — the same property 0086's tokens buy,
and the difference between a normative mapping and a normative suggestion; Section 8.4 stays the `need`
vocabulary. Two rows have no good answer in the existing vocabulary: `commit:worktree_moved` and
`merge:head_moved` fall to `human_review`, which is wrong for them, because the state moved between the
read and the write and the repair is to read it again, not to fetch a person. Both reach the default
only through a bare `commit` or `merge` entry point, which is why Section 12.3's "adds a reason token
and no `need` token" stops being true the moment a driver calls `merge` directly. They take a new
need, **`reread_then_retry`**, minted here rather than deferred because it is meetable **only through
0087** — a resume re-enters the raising point and the position re-reads — and a need no front-end can
meet is a hold, which this one would have become for want of the resume semantics landing in the same
change. One hole the repair exposes is recorded rather than fixed quietly: Section 6.5's own example is
`{on = "#error", do = "escalate"}` with no `reason`, and the corpus carries the same shape, so an
explicit `escalate` naming no reason needs an answer too — it raises the trigger's default need where
the trigger is a `needs_caller` result and `human_review` otherwise, since an `error` or `done` result
a policy chose to escalate names no remedy of its own and a position has no outcome to take one from.
Reconsider the column's *placement* if the registry gains a second per-reason policy field, at which
point it is carrying policy rather than identity and a separate table stops being a duplicate key;
reconsider a *mapping* wherever a front-end's built-in routing contradicts it, since the two must
agree. Relates to 0087, 0059, 0051, 0071, 0074, 0077 and 0079. Accepted and applied to `VCSX-SPEC.md`
(Sections 4.3, 5.2, 5.4, 8.4, 12.3, 13.1, 13.2), `VCSX-CONTRACT.md` (Section 5.4),
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/compose-envelope.json` and
`conformance/vcsx/README.md`.

## 0089 — `fail` gets the envelope `park` has, and `fail(reason)` is the repository's token

**State:** Accepted
**Folder:** [decisions/0089-fail-envelope/](decisions/0089-fail-envelope/)

Resolves issue #45. Section 5.2 gives `fail` one sentence and Section 8.2 has nowhere to put that
ending unless an `error`-class result is already in hand, because its two rules are exhaustive in
opposite directions: where `op`/`reason`/`class` are non-null, `class` is the class `status` reports;
and all three are null in exactly three enumerated cases, none of which is a failed flow. The report
enumerated every Section 5.2 disposition against every Section 4.2 class plus a lifecycle position — 32
combinations — and three broke, all of them `fail`, each differently: `#needs_caller → fail` and
`before:push → fail` **panicked**, and `push:ok → fail` composed an **`ok`** envelope, which is the
report on its own: the specification's rules, taken literally, produce a success envelope for a flow
the policy had just failed. The two failing shapes are not exotic — "never allow a commit in this
repository" is `before:commit → fail` and "this repository never holds for a human" is `#needs_caller →
fail` — and `park`, introduced in the same sentence of Section 5.2, composes on every one of them. This
was **predicted**: decision 0059 closed `park`'s envelope and recorded `fail`'s as left open "which
cannot be settled before what `fail(reason)`'s argument *is* has an answer", so this decision answers
both. Options: **A** a fourth null case, scoped by the class that already governs the field — a `fail`
reports the decisive result where the run has one whose class is `error`, and nulls all three otherwise
(chosen); **B** relax the class invariant, reporting the result whatever its class and letting `status`
be the policy's (rejected — the most information in the envelope and what a from-scratch design might
pick, since it separates what the run did from what the last operation reported, but 0059 called that
invariant "worth more than the case that motivated it — what a reviewer checks the next time a terminal
action is added", and this *is* that next time: every consumer reading `class` as the class of the
status breaks, and Section 8.5 makes it a `MAJOR` change to fix a case a `MINOR`-compatible clause
covers); **C** refuse the edge at validation (rejected — what the filing implementation does meanwhile,
and it names itself a meanwhile; as a normative answer it removes meaning rather than adding a report,
since `before:commit → fail` stops being expressible and the workaround is `park`, which reports
`needs_caller` for something the repository said was a failure). A's split is where it is for two
reasons: the classes agree in the `error` case so 0059's invariant holds **unchanged** rather than
gaining an exception, and an explicit `#error → fail` then reports what the built-in `error` default
reports for the same flow — which is itself a `fail` — where nulling unconditionally would make writing
the default down explicitly report strictly *less* than leaving it implicit. **The cost is stated**:
two shapes for `fail`, which is what 0059 rejected as its option E for `park`, on the ground that a
consumer must handle null regardless so it adds a case without removing one. The counter is that the
argument turns on a point where `fail` and `park` differ — for `park`, reporting the result would put a
`done`-class reason under a `needs_caller` status, the violation the null was introduced to avoid,
while for `fail` on an `error` result the classes agree, so option E added a case to avoid a null a
consumer needed anyway and this keeps a field that is already there. `fail(reason)`'s argument is a
**repository-authored token**, surfaced in `message` as prose and in `outputs.failed_by_policy` as
data, carrying the trigger the edge fired on and the reason it wrote — and **not** in `reason`, which
carries tokens from three engine-owned registries a consumer branches on, where a repository-invented
value would be indistinguishable from an engine one. The corpus already carries `{"do": "fail",
"reason": "push_failed"}`, so the argument existed as an unhomed string rather than as a hypothetical.
Reconsider if anything else is proposed for `reason`'s namespace, since the argument for keeping the
token out rests on that namespace being engine-owned; reconsider the two shapes if a consumer is found
branching on `op` being non-null as a proxy for "an operation was decisive", the check being whether
the non-null rule still states in one sentence. Relates to 0059, 0088 and 0060. Accepted and applied to
`VCSX-SPEC.md` (Sections 5.2, 6.5, 8.2, 13.1, 13.2), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/compose-envelope.json` and `conformance/vcsx/README.md`.

## 0090 — `entry` is a described field, null exactly where no entry point was read

**State:** Accepted
**Folder:** [decisions/0090-entry-nullable/](decisions/0090-entry-nullable/)

Resolves issue #46. Decision 0084 made every condition reportable: an invocation whose arguments the
engine cannot decode is refused with `arguments_unreadable`, `usage_or_config` and exit `2`, and
Section 8.3 requires exactly one JSON object on stdout on every path that produces a result, so a
caller parses one shape rather than branching on whether anything was written. Composing that envelope
needs a field the case may not have: `vcsx`, `vcsx --repo /srv/work` and `vcsx frobnicate` have no
first word, or a first word that is not one of Section 8.1's ten. Three engines will answer three ways
— a JSON `null`, a sentinel, the literal word the caller typed — and a consumer reading `entry` as a
Section 8.1 token gets a type error, a token no registry contains, or whatever a user mistyped. The
sharper half is **why the gap exists**: `entry` is not merely un-nulled, it is *undescribed*. Section
8.2's bullets cover `status`, `op`/`reason`/`class`, `escalation` and `outputs`; `vcsx_version`,
`entry` and `message` appear in the example JSON and in nothing normative, so their type, nullability
and meaning are inferred from one sample. Nobody wrote that `entry` is non-null because nobody wrote
`entry`. Options: **A** describe the three fields and make `entry` null **exactly where no Section 8.1
entry point was read** — `usage_or_config` carrying `arguments_unreadable`, and nowhere else (chosen);
**B** only a decodable invocation owes an envelope, stderr and exit `2` otherwise (rejected — what the
filing implementation does, and the right call *as a meanwhile* under the discipline of not minting
Section 8.2 surface locally, but as a normative answer it hands back exactly what 0084 bought,
reintroducing the parse-or-not branch at the one exit code where a caller has least idea what happened:
for the condition whose whole content is "your invocation was unreadable", a caller would have to test
stdout for emptiness first, and Section 8.3's "every path that produces a result" would hold only by
making this path produce none); **C** a reserved `unknown` entry token (rejected for a reason that only
shows up in an implementation — an engine generating its entry-point type from `vocabulary.json` gets
`unknown` as a variant, and Section 8.6's identity precondition is a **total function of the entry
point**, so every exhaustive match must answer for a variant where the question does not apply, which
is what an option type says and a sentinel cannot; it also makes "the entry points" ambiguous wherever
a section quantifies over Section 8.1's ten. A nullable field costs one option at one call site; a
sentinel costs a nonsense arm in every total function over the type). The "exactly where" is
load-bearing rather than stylistic: without it an engine may null the field wherever convenient,
including where the command line parsed and the entry is known, and it is the same shape — and
enforceable for the same reason — as the escalation rule Section 8.2 already states. Section 9's rule
that a non-answer MUST NOT be spelled as the value's absent case does not reach this, on that rule's
own terms: it requires the non-answer to map to a reason a caller can read, and the null travels with
`reason: "arguments_unreadable"`, so the reason token carries the condition and the null is the field
agreeing with it. `message` is described as prose **nothing parses**, stated now rather than later
because it is the only field with no schema and therefore where structure gets put when it has nowhere
else to go — the filing implementation reports being tempted to put a `fail` reason there, which is
exactly the token 0089 gives an `outputs` key. Section 8.3 needs no change: the code is `2`, as it
already is. Reconsider if a second condition is found where an envelope is owed and no entry point was
read, since the clause names one case by name and two makes it a list; reconsider if the contract gains
an encoding in which a null is not expressible, since the nullable-versus-sentinel argument is settled
here on the shape of a generated type. Relates to 0084, 0065, 0089, 0051 and 0071. Accepted and applied
to `VCSX-SPEC.md` (Sections 8.2, 13.1, 13.2), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/compose-envelope.json` and `conformance/vcsx/README.md`.

## 0091 — Forge access parameters, and the credential pair

**State:** Accepted
**Folder:** [decisions/0091-forge-access-parameters/](decisions/0091-forge-access-parameters/)

`VCSX-SPEC.md` cannot say *where* a forge is: `endpoint`, `URL`, `URI` and `instance` occur zero times
in the document, and the one relevant use of `service` is Section 11's "the service the credential is
presented to travels with the credential", which is ambient context rather than a parameter. So
`forge = "forgejo"` selects a kind of software and every Forgejo instance is the same value to the
engine — a self-hosted instance is reachable by Symphony for issues (`tracker.endpoint`) and
unreachable for pull requests, and two conforming engines given the same policy, coordinate and
credential can reach different instances and both report `create_pr:ok`, which is the conformance hole
0062 closed for the remote. Decision 0085 reasoned about the service root and settled it by leaving it
out of the argument list; that half is reversed here. The consumer supplies a **git-access parameter**
and a **forge-API-access parameter** — two rather than one because Section 9.1 has exactly three
network-touching capabilities and Section 9.2 has no local half, so the parameters map one-to-one onto
the plugins, and because git and API access are not one origin (GitHub serves `api.github.com` for the
public host and `<host>/api/v3` for an enterprise one) — plus an OPTIONAL per-backend extension bag,
all held opaque by the engine as the coordinate and the base ref are, which keeps URI grammar inside
the forge plugin. Credentials become a pair, git and forge, the forge one defaulting to the git one:
one credential is correct for a GitHub PAT and false wherever git access is a deploy key. The
defaulting rule's cost is recorded — a forgotten forge credential presents a git credential to an API
endpoint — and it is bounded to an authentication refusal because both the parameter and the
credential come from the same party. Options rejected: a single service root (cannot express an
endpoint pair differing by host on GitHub and by path on GitHub Enterprise); an opaque bag alone
(nothing portable, and a missing endpoint becomes a first-use failure after a push, the disposition
0084 argues against); a third core web-base parameter (speculation, and the bag covers it); one
credential and an undefaulted pair. Ownership is deliberately left to 0092 so the parameter shape
stays re-evaluable on its own. Reconsider by promoting a bag key to the core set when two independent
backends both require it. Relates to 0085, 0062, 0073 and 0084.

## 0092 — Backend, forge and tracker selection are the consumer's, read from a consumer config

**State:** Accepted
**Folder:** [decisions/0092-selection-ownership-and-consumer-config/](decisions/0092-selection-ownership-and-consumer-config/)

Section 6.2 puts `vcs`, `forge` and `remote` in `repo.policy.toml` and argues that "which code host a
repository targets is repository-owned"; Section 11 of the same document says "the service the
credential is presented to travels with the credential". The paragraph also uses "host" for the kind
of forge software and for the instance one clause apart. What decides it is neither contradiction but
a **bootstrap cycle**: reading `repo.policy.toml` requires the repository, obtaining the repository
requires the forge kind, its access parameters and a credential, and those were configured in
`repo.policy.toml`. No override escapes it — an override applied only after cloning does not help
anyone clone — and `SPEC.md` already contains the workaround in prose, at Section 9.7's "for
provisioning (which precedes reading the base revision)". `SPEC.md` Section 10.9 corroborates with the
right test applied one domain over: the agent is operator-selected "because agent choice carries model
credentials and sandbox shape". So the forge selection, the 0091 access parameters and credentials,
the remote and the tracker selection are the consumer's, with **no overrides**; the engine reads them
from a consumer-owned configuration file whose discovery is `Implementation-defined` and MUST be
documented. Because the keys leave `repo.policy.toml` entirely rather than being shadowed, Section
6.1's precedence rule needs no exception. `[engine]` keeps `version_floor` alone and is renamed
`[requires]`. The checkout mode is detected rather than declared, `detect_mode()` being authoritative
for any checkout the engine did not create; the creation-time choice is deferred to 0093. The remote is
the one the repository was provisioned from, which supersedes 0062's placement while keeping its
invariant and surviving its objection to derivation, since a provisioning remote exists before
anything else does — at the cost of 0062's out-of-scope fork case, which now needs a read/write pair.
The tracker selection does not move: the cycle reaches it and confirms the existing operator
ownership. Recorded as considered and *not* load-bearing: 0085's fork objection, which
repository-declares-operator-overrides would have defeated — so if the cycle is ever broken that
option becomes live again and the objection will not be available. A second review finding, on the
branch and before merge, repairs what deleting `[engine]` left behind: `vcs` was removed without a
counterpart, so nothing named the VCS backend for any checkout the engine did not create, while this
decision's own new validation input asserts that the consumer's selection "fixes which backends the
plugin layer loads". `local_vcs` is widened to be that selection — REQUIRED on every invocation,
naming the backend, and naming the created checkout's mode as before, with `detect_mode()` still
authoritative for the mode of a checkout the engine did not create — rather than adding a second key
that would land on `SPEC.md`'s side as `vcs.vcs`. Its absence is the precondition
`local_vcs_missing`, established before validation because the selection is what fixes whose
descriptor validation reads. Validation's boundary is redrawn at
the checkout: Section 6.10 is judged from five inputs including the consumer's selection, Section 8.6
from what needs the checkout, using the seam Section 8.6 already has in establishing
`arguments_unreadable` before validation. Assumption recorded: the consumer file MAY carry a
credential or a reference the consumer resolves, since `SPEC.md` Section 15.3 forbids materializing
secrets that way, and Section 11's "holds no long-lived credentials" narrows to not persisting one
beyond an invocation. Relates to 0091, 0093, 0062, 0085 and 0002.

## 0093 — The engine is the only VCS adapter, and the engine layer is required

**State:** Accepted
**Folder:** [decisions/0093-engine-owns-provisioning/](decisions/0093-engine-owns-provisioning/)

Two components implement version control, split at provisioning: `VCSX-SPEC.md` Section 2.2 makes
provisioning a Non-Goal and `SPEC.md` Section 9.7 makes it Broker Core work "never a VCS-engine
responsibility". `SPEC.md`'s reference algorithms carry four VCS-touching calls —
`vcs.clone_object_store`, `vcs.fetch_object_store`, `workspace_manager.provision_for_issue` and
`vcs.attempt_clean_backmerge`. The third is where the duplication bites: creating each issue's tree is
`git worktree add` against `jj workspace add`, so the checkout mode is fixed by a component with no
VCS backend abstraction, and moving only the clone leaves Symphony holding a VCS implementation. The
fourth is a defect independent of everything else — the back-merge is an operation Section 9.7 routes
to the engine, so the `vcs.` prefix manufactures the adapter Section 9.7 denies exists. After 0092 the
operator names the forge kind, parameters, credentials and remote once and two implementations consume
them, so every future backend is implemented twice or the two disagree. And `engine-direct` cannot
start: no orchestrator, no Symphony adapter, and Section 2.2 forbidding the engine to provision.
Provisioning therefore moves into the engine, which becomes the only component implementing version
control, with the contract naming a **store and trees derived from it** as a relationship rather than
a mechanism, since a jj secondary workspace is not a git worktree. The price is stated rather than
absorbed: `SPEC.md` Section 18.1.1 lists "the VCS engine and autonomous daemon are OPTIONAL layers" as
a REQUIRED conformance item, and that bullet is rewritten — Broker Core remains the only *enforced*
guarantee and remains satisfiable for a single agent session in an existing workspace, but it can no
longer obtain one. Options rejected: keeping the non-goal (bounded duplication that stops being
bounded at a third backend, and the checkout mode decided in the wrong component); an implicit
ensure-step or an OPTIONAL operation (both add a capability without removing one, leaving two paths
that must not race, and Symphony's adapter disappears only by a choice the specification cannot
require without re-opening Section 18.1.1 anyway); a store-blind engine; a post-condition with an
`Implementation-defined` mechanism (a consumer running many issues per repository chooses an engine
*for* its storage behaviour and would have no way to state a requirement). The engine's identity
changes and the specification says so: Sections 1.3, 2.2 and 11 are rewritten rather than amended. The
secret-isolation invariant is untouched — provisioning is host-side like `push` and `merge`, and no
provisioning verb joins the broker's verb set. A second review finding, on the branch and before
merge, repairs the seam the operation was given no way to stand on: `provision` was listed as an
entry point while Section 8.6 still validated a policy read out of the repository and resolved a work
branch against a checkout — both of which `provision` exists to produce, so the invocation that
creates a checkout was refused with `checkout_unreadable` before it ran. Its two locations were also
never arguments, though "the location" carried four claims including what separates
`provision:store_unsupported` from `capability_unsupported`. `store_location` (REQUIRED) and
`tree_location` (OPTIONAL) become arguments, which also makes `SPEC.md`'s store-only phase
expressible; and `provision` is stated as the one entry point validated against no policy document
and establishing no precondition that reads a checkout. `capability_unsupported` survives both cuts
because it turns on the consumer's configuration rather than the repository's — 0092's input, doing
the work here. The cost is recorded: a `version_floor` cannot bind the step that obtains the file
declaring it. This is the third register the bootstrap cycle reached — configuration, then control
flow, then the invocation pipeline — each found after the previous repair shipped. Reconsider if a
deployment needs Broker Core over repositories materialized some other way entirely, in which case
the repair is to restore optionality with an OPTIONAL provisioning operation, not a second VCS
adapter. Relates to 0092, 0091 and 0062.

## 0094 — The policy branch is not the base branch

**State:** Accepted
**Folder:** [decisions/0094-policy-branch-and-base-source/](decisions/0094-policy-branch-and-base-source/)

Opened from decision 0093's second review finding and reframed twice under review; the path is kept
in `Background.md` because it is the argument. `SPEC.md` Section 15.4, echoed in `VCSX-CONTRACT.md`
Section 10, makes host-side Way of Working readable only from "the resolved **base revision**" — the
whole security argument for anything the engine runs on the host — while `VCSX-SPEC.md` Section 6.4
puts `[base] branch` inside `repo.policy.toml`, the file that sentence reads from the base revision.
To read the policy you need the base; to know the base you need the policy, and no document says how
the first read resolves. Breaking it in place means reading the policy from whatever the checkout
holds, which lets an agent-editable revision decide which revision is trusted. That is the fourth
instance of the cycle 0092 and 0093 chased, and the sharpest, the other three costing availability
where this one costs a guarantee. Stating the argument in full then exposed a second and larger
defect: it stands on two legs, and only one holds. The agent cannot *push* to the base — guaranteed
already by Section 10.8's scope guard, "push only to the run's work branch", with no configuration
required. But the base is trusted because it is *review-gated*, and landing pull requests on the base
branch is Symphony's entire purpose, so the trust root is a branch the service routinely merges into
and the only thing between an agent-authored host-side hook and its execution with operator
credentials is a reviewer noticing. Section 9.8 already worries about the adjacent case, requiring
the actor differ from the approver so a pull request cannot be self-approved. Measured: all 32
vectors in `vectors/policy-validation.json` supply `base.branch`, including every vector whose
subject is something else, which is how both defects survived. The repair separates the two jobs the
one value was doing — trust root, needed *before* the policy is read, and pull-request target, needed
*after* — since only the first is circular. The operator names a **policy branch**, REQUIRED with no
default, and no pull request Symphony creates or merges targets it; the guarantee is stated over what
Symphony does rather than over a config file, so a consumer checks it through the operations. It MUST
be unwritable by the agent, with the establishing mechanism `Implementation-defined` and MUST
document, since the scope guard covers the push path but not the others. The **pull-request target**
then becomes an ordinary configuration question with three sources in precedence order — the
invocation, operator config, then `repo.policy.toml`, which keeps a legitimate say including its
`by_prefix` mapping because reading it no longer depends on the value. An operator MAY bound what an
invocation may name; the bound is deliberately weaker than the trust-root case because a badly chosen
target reaches only the in-sandbox parts, which run without credentials. How a ticket carries one is
`Implementation-defined` and MUST be documented. Where no source supplies one the refusal is a
**precondition** scoped to the entries that need a target — `ship`, `integrate`, `create_pr` — which
is what the reframing bought: under the original framing it was a configuration error and would have
forced validation to take the entry point as a sixth input, the change that left this decision
`Proposed` through two drafts. Refusing up front rather than at first use preserves 0084's guarantee,
`ship` reading the target only at `create_pr`, after it has pushed. Options rejected: leaving the
base in the policy and answering only the missing-value question (leaves both defects); moving the
single value to the consumer (fixes the cycle, leaves the trust root a merge target — the smaller
half of the repair). Cost accepted: two branch-shaped values where there was one, and a policy that
cannot be reviewed alongside the code change needing it — which is the cost of the guarantee, since a
trust root reviewable alongside a code change is one a code change can alter. Assumption recorded:
the policy branch is REQUIRED with no default, the sheet's question on defaulting having gone
unanswered while the primary answer chose "the trust root is never a merge target", which any default
resolving to the main branch would void. Reconsider if operators report policy branches drifting far
enough from the main line that host-side hooks no longer match the code they run against. Relates to
0092, 0093, 0084, 0085 and 0002.

## 0095 — A host-side hook's unit comes from the trusted source

**State:** Accepted
**Folder:** [decisions/0095-host-side-hook-unit-provenance/](decisions/0095-host-side-hook-unit-provenance/)

Found reviewing what decision 0094 actually secured: it secures the hook's **declaration** and not
the **program the declaration names**. Two sentences older than 0094 put the executable back in the
agent's hands. `SPEC.md` Section 15.4 said "Hooks run with the workspace directory as their working
directory" — all hooks, both contexts, so a host-side hook's working directory is the tree the agent
edits. And `VCSX-SPEC.md` Section 8.6 said whether a `run` unit "exists and can be started is **a
property of the worktree**". So the specification did not merely permit a host-side hook to execute
repository content; it located the unit in the worktree and pointed the hook's working directory at
it. The chain needs no cleverness: an operator writes `run = "./scripts/check.sh"` on the policy
branch, the agent writes that file, and it executes on the host in the operator's context — no branch
manipulated, no pull request merged, no reviewer fooled, and a relative path into the repository is
the obvious way to write a host-side hook. This outranks the other open findings because they need a
misconfiguration or a particular checkout arrangement to bite, while this needs only that a
deployment use a host-side hook, and it defeats the trust argument rather than weakening it. Repair
in four parts, because the hole has two halves and each needs a rule and a way to check it: the unit
resolves from the trusted source and never from the working tree; a host-side hook's working
directory is not the workspace; the workspace path is supplied to it as an argument or environment
value; and an implementation MUST document how it resolves a host-side unit. The third is what keeps
the category useful — a host-side hook MAY **read** the workspace and MUST NOT **execute** from it,
so a scan or a build check still inspects agent-written content as data. The second is what stops the
first being defeated by accident, since a lifecycle hook's body is an inline script and a relative
command inside it would otherwise reach the tree. Options rejected: forbidding a host-side hook the
repository entirely (cannot express read-as-data, and removes the reason to have the category);
leaving it to Section 15.5's hardening guidance (SHOULD-level advice about a deployment's own risk
appetite, where Section 15.4's "Way-of-Working trust equals policy-branch trust" is a conclusion this
property is load-bearing for). The context keeps its names: `policy_branch` was considered and
rejected because `VCSX-SPEC.md` Section 3.2 deliberately keeps branches out of the engine — the engine
labels context, the consumer sources by trust — and the name means nothing in `engine-direct`, which
has no sandbox. So the engine states the rule branch-free (a host-side unit resolves from the same
source the host-side policy came from) and `SPEC.md` names that source. Recorded as considered and
**not** done, with the measurement that defeated it: a rule forbidding a `[policy]` edge from
conditioning credentialed work on an in-sandbox gate's outcome. Section 10.8's broker verb set —
`push`, `back-merge`, `pr`, `request-merge` — already exposes every credentialed operation such an
edge could dispatch bar `pull`, so an agent steering a gate obtains almost nothing asking would not,
while the rule would forbid the ordinary `commit:ok → run_op push`. What survives is that neutering
an in-sandbox gate defeats a hygiene control rather than reaching credentialed work, which Section
15.4 already characterizes correctly. Reconsider if an engine defines a credentialed operation beyond
Section 4.1 that no broker verb covers, or if a deployment narrows its verb set below Section 10.8's
floor. Relates to 0094, 0093 and 0002.

## 0096 — The three repairs decision 0094 needed

**State:** Accepted
**Folder:** [decisions/0096-policy-branch-repairs/](decisions/0096-policy-branch-repairs/)

Three defects in decision 0094's applied text, grouped because they are one omission at three levels:
0094 stated a guarantee and left the ways of establishing it unstated. **First**, Section 9.10's
"Symphony MUST NOT create or merge a pull request whose base is the policy branch" had no refusal
behind it, so an operator setting `vcs.policy_branch = "main"` with the target resolving to `main` —
the obvious first configuration — got `commit` ok, `push` ok, `create_pr` refused: the work branch on
the remote and no pull request. That is the publish-then-die shape 0084 moved a check to validation to
prevent and which 0094's own reasoning cites 0084 to avoid, appearing a third time on this branch and
a second time introduced by a repair. The conflict is visible in the consumer's configuration with no
checkout and no network, so `policy_branch_is_target` joins Section 6.10's table and the refusal lands
ahead of `commit`. **Second**, nothing said which copy of the policy branch is read. Section 6.4 gives
the base ref that discipline because a checkout may hold a local branch and a remote-tracking copy;
for the base the wrong one is a stale number, for the trust root it is host-side hooks chosen by
whoever can write the checkout — latent in `daemon`, real in `interactive-agent`, immediate in
`engine-direct`. The policy branch now resolves to the copy the resolved remote holds, never a local
branch of that name, which collapses the `engine-direct` exposure to `daemon`'s. **Third**,
`policy_branch` was REQUIRED with no failure mode while its five siblings all have one; that is the
fourth recurrence of the pattern 0092's review finding named, and the second committed after naming
it, so the count is recorded rather than the token alone — adding a REQUIRED argument and adding its
refusal are two edits and nothing couples them. `policy_branch_missing` joins Section 8.6, established
before validation as the third of three, because the policy document is the first of Section 6.10's
inputs and this argument says where to read it. Plus the runtime half of the first: 0094's
`base_branch_allowed` and `base_branch_not_permitted` already cover a target an issue supplies, so the
policy branch is excluded from permitted targets **implicitly**, whatever the bound lists and whether
or not it is configured — a bound an operator must remember to set is a guarantee that fails by
omission. A refused issue is logged on every occurrence, and where the tracker adapter supports the
capability commented once per (issue, target) and transitioned to a configured blocked state; the MUST
sits on the log because `add_comment` and `set_state` are OPTIONAL (Section 11.7) and a `none`-mode
adapter may have neither, and the comment is bounded per (issue, target) because the daemon
re-evaluates every candidate every 30 seconds by default. Deliberately not done here: scoping the
first refusal to a strict mode. As the specification stands there is one mode; the tunable model makes
`policy_branch == target` legitimate under an operator opt-out, and that scoping is its work, since
repairing applied text and introducing design in one record buries the first. Relates to 0094, 0084,
0092 and 0002.

## 0097 — Where the policy comes from, when it is read, and what happens when it cannot be

**State:** Accepted
**Folder:** [decisions/0097-policy-loading-and-unusability/](decisions/0097-policy-loading-and-unusability/)

Three consequences decision 0094 left unhandled once the host-side Way of Working moved to a remote
branch. **The reload machinery stopped being implementable.** Section 6.2 requires detecting changes
to all three configuration artifacts, written when `repo.policy.toml` was read from a revision the
checkout held; from a remote branch, "detect changes" means polling a remote ref on a cadence nothing
specifies. **The policy is read far more often than anyone intended** — validation runs per
invocation and every brokered verb is an invocation, so 3 at minimum and roughly 23 at the default
`agent.max_turns` ceiling, per issue. The cost is not the count, since every operation Symphony
invokes the engine for is remote-touching anyway; it is 23 places a load can fail mid-run, each
needing a disposition. **And four ways a policy can be unusable had four dispositions**, two of them
undefined: the source unreadable (a case that did not exist before 0094), no file discovered (the
original scope of 0094 before it was reframed, never closed), a file that does not parse
(`malformed_policy`), and one that parses invalidly (Section 6.10's reasons). So: `policy_source`
names where host-side policy is read from, `policy_branch` by default or `target_branch` as the
operator's opt-out — a named mode rather than a flag, because the trust guarantee is conditional on
it and a conditional guarantee is worth stating only where a consumer can tell which state holds; what
the opt-out gives up is stated rather than derived, the merge path to the trust root reopening and
per-branch sections becoming authorable by whoever lands a pull request. Policy and workflow load
**once at work start** through `load_policy`, an operation returning the merged surface that the
consumer holds and supplies onward, which resolves Section 3.2's "the consumer sources config by
trust" against Section 6.1's "the engine discovers and reads" in the former's favour and dissolves the
recorded finding that no Section 9.1 capability reads a file at a revision — one operation does it
once rather than a capability per read. `WORKFLOW.md` changes timing only and stays worktree-sourced,
since everything in it runs in-sandbox without credentials. Section 6.2 is restated: `repo.policy.toml`
is not watched, the policy in force for a run is the one read at its start, and a change takes effect
for work started after it. The four unusable conditions get **one resolution and four diagnoses** —
each refuses with `usage_or_config` and its own reason, `policy_source_unreadable` and
`policy_not_found` joining the two that existed, because a consumer's response is one ("I cannot run
this repository's policy") while the repair differs (make the source readable, commit the file, fix
the syntax, fix the value). `policy_source_unreadable` does not distinguish an absent branch from an
unreachable remote from a refused credential, on `provision:unreachable`'s reasoning that a reason per
cause is a registry of the ways a network fails. Symphony classifies all four as `Engine Invocation
Failures`, repo-scoped, and retries them with a **documented per-repository backoff** rather than every
`polling.interval_ms` — none of the four clears without a person acting — which is not the per-worker
backoff Section 14.2 forbids, the unit being the repository. Each is logged with its reason so the four
stay distinguishable in the record, at transitions rather than every evaluation. Last-known-good is
scoped to work in flight: a policy that was loaded and can no longer be read stays in force for runs
under way while new work is refused, and one never loaded has no fallback — the one axis on which the
shared disposition splits, and it splits on history rather than cause. Deferred as too complicated for
now: routing that report through `[policy]` edges, which would work via the last-known-good policy but
buys a repository a say in a response already fixed. Reconsider the cadence if an operator needs to
revoke a host-side hook and finds runs in flight keep it; reconsider the unified resolution if
`policy_not_found` turns out to deserve parking rather than retry, nothing about it being transient.
Relates to 0094, 0093, 0092 and 0002.

## 0098 — The `repo.policy.toml` hook namespace, and per-branch sections

**State:** Accepted
**Folder:** [decisions/0098-policy-schema-shape/](decisions/0098-policy-schema-shape/)

Two changes to one schema, taken together because each would otherwise rewrite the other's work.
**The `hooks` namespace had two owners and no stated rule**: `SPEC.md` Section 5.3.4 wrote scalars
(`hooks.after_create`) and `VCSX-SPEC.md` Section 6.6 wrote subtables (`[hooks.scan-content]`), both
into `repo.policy.toml`. TOML permits both, so nothing broke — but a repository wanting an engine
hook named `after_create` could not have one, two timeout concepts sat adjacent with different
defaults (`60000` against a floor of 600 seconds), and Section 6.11's `malformed_policy` for "a
declared hook that names no unit to run" would refuse a valid Symphony config under any engine
reading every key under `hooks` as a hook. The disambiguation that saves it — scalars are the
consumer's, tables are the engine's — was real, load-bearing and written nowhere. **And context was
declared for one hook family and derived for the other**: Section 5.3.4 already lets the artifact fix
it ("when both define it, the `repo.policy.toml` hook runs on the host and the `WORKFLOW.md` hook
runs inside the sandbox"), while the engine's named hooks carried a `context` key — which admitted a
combination the derived form cannot express, a hook marked `host_side` whose unit the working tree
supplies, which 0095 had to forbid in prose. So hooks are prefixed **symmetrically**,
`[hooks.engine.<name>]` beside `[hooks.workspace]`, on the criterion that a fresh reader should see
the two-owners fact where it is declared rather than infer it from an entry's type; asymmetric
prefixing was the smaller diff, `[hooks.<name>]` being shared contract surface across four artifacts,
and lost on that criterion with nothing implemented yet to migrate. `context` is removed from hook
declarations and derived from the artifact — the engine still receives one per hook, since it is
handed one merged surface and never sees two artifacts, but the consumer tags it while assembling
that surface, which 0097's `load_policy` already has it doing. That makes 0095's unit rule structural
rather than stated, and collapses a genuine oddity: `repo.policy.toml` was read from **two
revisions**, host-side sections from the policy source and the in-sandbox `before:commit` gate from
the worktree. The gate's declaration moves to `WORKFLOW.md` and each artifact is now read from one
revision; the edge invoking the gate stays in `repo.policy.toml`, so the agent can change what the
gate does and not whether it runs. Edge `context` is untouched, participating in matching where a
hook's did not. **`[[branch]]` sections** restore what 0094 traded away without naming: before, the
policy came from the resolved base revision, so a release track could carry stricter host-side hooks;
afterwards one source governed every target and `by_prefix` did not replace it, mapping a work-branch
prefix to a base branch rather than to hooks. A section carries a `match` table naming exactly one
matcher, `prefix` being the one defined, and merges over the top level key by key as the `vcsx.toml`
merge already does. Longest prefix wins and exactly one section applies, which settles determinism by
construction rather than by a precedence rule — Section 5.4 refuses two edges matching one trigger,
and two sections both contributing an edge would reintroduce that one level up. No empty-prefix
default is needed, unlike `by_prefix`, because the top level is the default. Two sections with the
same `match` are `duplicate_branch_section`; a `match` naming no matcher or several is
`malformed_policy`. The matcher is named inside `match` rather than being a bare string so a later
glob adds a key beside `prefix` instead of changing every section written. Options rejected: glob now
(a precedence rule for two matching globs, and dialects differing across implementations) and filter
expressions (a grammar, an evaluation order and a failure mode). Under `policy_source =
"target_branch"` these sections come from the target, so whoever lands a pull request can author one
— a property of that mode, stated where the mode is chosen. Reconsider the matcher if a repository
must rename branches to be served by it, which would be the specification dictating naming rather
than describing it; reconsider derived context if a repository needs a host-side and an in-sandbox
hook of the same name in one artifact, the one capability this removes. Relates to 0095, 0097, 0094
and 0002.

## 0099 — The edge is the binding, and a unit at a position that says nothing

**State:** Accepted
**Folder:** [decisions/0099-scan-binding-and-unanswered-units/](decisions/0099-scan-binding-and-unanswered-units/)

Issue #49 reported two gaps in Section 10.4 — a commit diff that can be scanned with no key naming a
profile for it, and no disposition for a `scan-content` check or a `pr_to_squash` transform that gives
no usable answer. Tracing both produced three findings that do not line up with the two. **A scan was
bound to a unit two ways and reconciled nowhere**: Section 6.5's own worked edge example is
`on = "before:commit"`, `do = "run"`, `hook = "scan-content"` and Section 10.1 calls the scan a hook,
while Section 6.8 declares `title_scan`/`body_scan` and nothing says how `strict` resolves to a unit or
who dispatches it. Adding `diff_scan` would have closed the asymmetry without closing the hole. **The
scan half of the second gap was already covered** — the issue's premise, that Section 10.4 positions
title/body scanning "during `create_pr`" rather than at a `before:` hook, does not survive the next
paragraph of the same section, which says "at `before:create_pr`"; a scan is a `before:<op>` hook, so
the bound, `hook_unanswered` and `unanswered_gates` all reached it already, and the defect was one
loose sentence. **The transform was genuinely uncovered, and worse than filed**: it is named by
`[messages.squash]` `transform`, is never called a hook, and Section 6.6's bound is stated over hooks,
so nothing bounded it and an engine waiting forever was conforming. One supporting argument was also
wrong: a fallback would not publish where "Section 11 says no operation rewrites afterwards", that
guarantee being over the work branch, which Section 11 says a squash strategy is not an exception to
because it writes to the base branch. So: **the edge is the binding**. `title_scan` and `body_scan` are
removed, no key replaces them and none is added for the diff; a scan is declared as a hook and run by a
`[policy]` edge, the three contents bound alike, a position no edge binds running nothing as Section
5.4 already has it. What the engine supplies at each position is stated for the first time — the commit
message and the diff at `before:commit`, the composed title and body at `before:create_pr` — mirroring
Section 10.3's sentence for the transform. Rejected: completing the table, which keeps the per-field
declaration readable in configuration but gives one unit family two dispatch mechanisms and puts a
carve-out into Section 5.4; and passing the profile as an argument, which costs an argument-passing
surface Section 6.6 does not have. The capability survives the removal either way, in the unit rather
than the schema, which is where Section 10.4 already puts every scan rule. **The transform is a unit at
a position**: Section 6.6's bound is restated to reach every unit the engine runs at a lifecycle
position and waits on, `hook_unanswered`'s gloss widens from a hook to such a unit, and a transform
that gives no usable answer yields `merge:hook_unanswered` and the operation does not act. That is
stated as the effect a consumer can check — the pull request is not merged — rather than as "the forge
is never asked", which the `spec-guarantee` test rejects as a claim about a call readable only from the
engine's own trace, and which both the issue and the reporting implementation use. No separate MUST NOT
on falling back to the pull request's own body: an operation that does not act publishes nothing.
Minting `merge:transform_unanswered` was rejected on Section 4.3's own argument for spending one reason
where the repair is the same shape. **`transform_unbound` joins `template_unbound`** at validation,
judged from the fifth input that already exists; a `[messages.squash]` naming no transform is not the
condition, since it names no unit. Generalizing both to `unit_unbound` was rejected on cost across
three artifacts and because the token would stop saying which unit is missing. **Left open and verified
rather than assumed:** Section 9.2's `request_merge(pr, strategy, expected_head)` takes no message, and
nothing carries the transform's output to the forge, so the seam Section 10.3 describes has no route to
the operation that would use it — a plugin-API defect predating this issue, out of its scope, and not
affecting the disposition above. Reconsider the binding if an operator must read a repository program
to learn which content is guarded in a deployment where reading it is what the trust boundary avoids;
reconsider the single reason if a repository needs to route a broken transform differently from a
broken gate. Relates to 0081, 0086, 0098, 0057 and 0002.

## 0100 — An edge does not declare its execution context

**State:** Accepted
**Folder:** [decisions/0100-edge-context-provenance/](decisions/0100-edge-context-provenance/)

Issue #52 reported that Section 6.5 makes an edge's `context` OPTIONAL and "defaulted per the
action" and that no default is stated for any action, anywhere. The label is not descriptive:
Section 11 promises an in-sandbox edge receives no credentials, so an unlabelled `run_op` edge
dispatching `integrate` makes one conforming engine integrate and another fail for want of a
credential, on the same policy and the same repository, with the policy well formed because the key
is OPTIONAL. Section 13.3 does not list the choice either, so an engine has the obligation and
nowhere to publish how it met it, and Section 8.5 makes it a forward problem: an operation added in
a `MINOR` arrives with no context and no rule to derive one. **Decision 0098 stopped one object
short for a reason that does not survive checking.** It left edge `context` alone because "an edge's
context participates in matching, a hook's does not" — but an edge's *execution* context
participates in no matching. Section 5.3's ladder is over the trigger, Section 5.4's key is
`(from-context, trigger)` where its own text glosses that as "a transition graph keyed on a
workflow-state `from`, Section 6.7", and Section 12.1's `match_edge(policy, from_context, trigger)`
reads the `from` key and the ladder and nothing else. Two different things are called a context on
one schema object and the sentence collapsed them; the capability being preserved did not exist.
Measured, the execution context is written 13 times in `VCSX-SPEC.md` and exactly one occurrence
declares an edge's while exactly one consumes it — the other eleven are a hook's, already derived.
So: **an edge does not declare its execution context**. The key is removed; the artifact fixes it,
an edge in `repo.policy.toml` being host-side and one in the consumer's in-sandbox artifact
in-sandbox, with the consumer tagging each edge while assembling the one merged surface as 0097's
`load_policy` already does for hooks. The question stops being askable rather than being answered,
Section 11's guarantee stops resting on an author labelling truthfully — a working-tree edge
claiming `host_side` is now unwritable rather than forbidden — and the forward problem closes
outright, since no context is derived from an operation. A policy still carrying the key has it
ignored under Section 6.1's unknown-key rule; `malformed_policy` was rejected as a carve-out from
forward compatibility that also refuses documents that were conforming, and because the substituted
tag is the safe one where it matters. Rejected: a `context` field per operation in
`vocabulary.json`, which publishes data a consumer genuinely needs but answers what an operation
*needs* rather than what an edge *may cause*, keeps the mislabelling combination, and only defers
the `MINOR` problem; and deriving an operation's context from the capabilities it requires, which
Section 9.1's enumeration nearly supplies for free and which reproduces Section 3.2's list — but
labels the operation rather than the edge, and makes `status` host-side wherever a forge is
configured, since `status` reads `pr_state`. Declaring it `Implementation-defined` was rejected as
making the divergence visible without removing it. What this gives up is one artifact declaring both
contexts side by side, which is close to vacuous now that a hook carries its own context and the six
non-`run_op` actions receive neither worktree nor credential. Reconsider if a repository needs a
trusted-artifact edge to dispatch *without* the credentials the engine holds; the answer then is a
per-edge assertion about credentials, not a restored `context`. Relates to 0098, 0095, 0097 and
0002.

## 0101 — Under `target_branch` the base is an argument, not a policy key

**State:** Accepted
**Folder:** [decisions/0101-base-under-target-branch/](decisions/0101-base-under-target-branch/)

Issue #51 reported that under `policy_source = "target_branch"` the base resolves from a source
inside the document the mode is trying to locate — decision 0094's bootstrap cycle, one mode over.
Section 6.4 gives the base three sources with `[base] branch` lowest; Section 8.1 reads host-side
policy from the pull-request target, which is the base. An invocation supplying no `base_branch`
against a consumer configuration supplying none has no revision to read a policy from, and the only
remaining source is inside the unread policy. Nothing names the condition:
`policy_source_unreadable` says the source could not be read where here it was never named,
`base_branch_missing` is scoped to entries that need a base where this reaches every entry, and
`policy_not_found` presumes a source. **The sharper consequence is that Section 8.6's scoping is
mode-dependent and does not say so** — its sentence that `commit`, `push`, `pull`, `merge`, `land`
and `provision` "need none and run without one" is false under this mode for the first five, because
an entry that needs no base to do its work still needs one to locate the policy that governs it,
which is the argument that section already makes for `policy_branch_missing` and states as the
reason that reason precedes validation. **A third consequence the issue did not name:** Section
12.4's `resolve_base` also reads `resolve` and `prefixes`, so `by_prefix` reaches the same cycle by
a second route and the rule has to be stated over `[base]` rather than over one key of it — which
also settles that one invocation resolves one base, rather than the located policy re-resolving a
different operational one. Measured with 0094's own instrument, `policy_source` appears in 0 of 9
base-resolution vectors and 0 of 38 policy-validation vectors: the mode 0097 introduced and 0098
extended is exercised by no vector, which is what hid this. So: **under `target_branch`, `[base]`
contributes nothing to the base**, which resolves from the invocation then the consumer
configuration alone — Section 8.1's existing sentence about the policy branch applied to the
argument that plays its role under the other mode. Where neither supplies one, `base_branch_missing`
whatever the entry, established before validation, so the before-validation set becomes
mode-dependent — `arguments_unreadable`, `local_vcs_missing`, then `policy_branch_missing` under the
default mode and `base_branch_missing` under this one — while the ordering rule for every other
reason holds unchanged. `provision` keeps its exemption, restated rather than created: Section 6.1
already makes it the one entry that runs where no policy could be read, so it performs no policy
read to locate. Rejected: minting a precondition reason for the condition, because Section 6.1's
rule keeps reasons apart where the *repair* differs and the repair here is identical — supply
`base_branch` — so the token would spend major-stable surface to say what a consumer can read off
the `policy_source` it configured itself; and removing the mode, which closes the cycle by
construction and makes Section 11's guarantee unconditional, but puts a reader back to comparing two
strings to learn which trust regime holds, turns `policy_branch_is_target` from a refusal 0094 added
deliberately into an opt-in, and rewrites `SPEC.md` Section 15.4's statement of what the mode costs
as a property of a coincidence between two values. All four copies of the three-source list move
together (Sections 6.4 and 8.6, `SPEC.md` Sections 9.7 and 18.1) and Section 15.4 gains the third
thing the mode costs. Reconsider the token if a consumer must distinguish "this entry needs a base"
from "nothing says where to read the policy from" in automation; reconsider the mode if a deployment
supplies an operator-level base on every invocation anyway, since it is then paying for a
convenience it no longer uses. Relates to 0094, 0097, 0098 and 0002.

## 0102 — The enumerated error tokens as data, and a class that names its condition

**State:** Accepted
**Folder:** [decisions/0102-enumerated-error-tokens/](decisions/0102-enumerated-error-tokens/)

Resolves issue #54, which reports that Section 5.5's five workflow/template error classes have no
group in `conformance/vocabulary.json` while `vectors/prompt-rendering.json` already asserts one by
name. Three defects sit on that spot. **The corpus measures a spelling the specification does not
require**: the vector file calls `template_render_error` a MUST, Section 5.5 carries no RFC 2119
keyword at all, and Section 17.1's four checks say "returns typed error" — satisfied by any
spelling. **The registry could not have carried the group anyway**, because 0071 ruled that the
ruling belongs in the specification and deferred these tokens on a stated blocker — "several are
RECOMMENDED rather than REQUIRED spellings, which is a distinction the registry would have to carry
per entry" — so the registry gap is downstream of the level gap. Deriving it shows the blocker is
per **group**, not per entry: each section states one level for its whole set, so the distinction
costs one field and the slice is cheaper than the deferral assumed. **A class named by its condition
or by the pass that caught it** is the defect that breaks an implementation today: a strict template
engine resolves filter names against its own filter table and variable names against the render
context, so it may reject an unknown filter earlier than an unknown variable (measured, `liquid`
0.26.11 / rustc 1.97.1: filter at parse, variable at render), and the corpus expects
`template_render_error` for both — which holds only if the class names what was wrong rather than
which pass noticed. Section 5.5 annotates `template_parse_error` "(during prompt rendering)", a
phase, which is the sentence that invites the misreading; under it two of six vectors fail for an
implementation that is otherwise correct. **The five Section 5.5 classes become REQUIRED spellings;
Sections 11.4 and 10.6 stay RECOMMENDED, and the registry carries the level per group.** The split
is where the mechanism draws the line: whether a spelling can be required turns on **who owns the
condition**. Section 5.5's five are conditions on artifacts this specification defines, so every
implementation faces exactly those five; Sections 11.4 and 10.6 are categories an adapter maps a
foreign failure onto — "each adapter maps its transport's failures onto them" — and requiring a
spelling there requires a *distinction* the transport may not offer. Rejected: RECOMMENDED
throughout (it makes the corpus the overreaching party and would delete its two sharpest vectors,
leaving the one class a consumer branches on spelled per implementation); and REQUIRED throughout
(one rule for every enumerated error token, which would retire the level field, but imposes a
distinction an adapter over a transport that reports a bad status and a malformed payload
identically cannot compute). Rejected on scope: carving out Section 5.5 alone, which leaves the
deferral standing on a reason just shown wrong, so the next reader takes it on trust; and spec-only,
which is cheapest and fixes everything that breaks today, but leaves an implementation transcribing
five tokens by hand once the only remaining obstacle is the authoring. Section 5.5 also states that
the set is **open** — additional classes MAY be defined, MUST be documented, and MUST be assigned
one of the two gating behaviors — before the registry records `exhaustive: false`, because REQUIRED
plus an unflagged group reads as closed and closing it by omission is the Section 10.4 failure 0071
was created to fix. `gating` is carried per entry (Section 5.5 fixes the split; Sections 6.2 and
12.4 act on it), `requirement_level` per group. Section 10.8 stays deferred on its own and stronger
reason: its reason codes are introduced by "for example" with no enumeration, so there is nothing to
publish that would not be invented. Two findings recorded rather than fixed: Section 17.3 requires
four of Section 11.4's RECOMMENDED tokens by name in `Core Conformance` checks, the same asymmetry
one section over; and Sections 10.6 and 10.4 share three spellings (`turn_failed`, `turn_cancelled`,
`turn_input_required`), which is the useful naming rather than a collision, now stated in the group
note. **Review finding, recorded rather than folded in:** a comment on issue #54 reports the same
asymmetry three more times — Section 14.1's nine failure classes, Section 7.1's six orchestration
states, Section 7.2's eleven run-attempt phases — and the finding this decision answers for is its
own, because rewriting the deferral list's first bullet made the whole list read as re-derived when
only that bullet was. Section 7.1's states sit behind a reason that is about Section 7.3's triggers;
Section 14.1's reason ("not tokens an implementation emits") is true of emission and beside the
point, since Sections 17.2, 17.4, 18.1.4 and 19 name the classes in backticks; and Section 7.2 had
no bullet at all. That the defect this decision named recurred inside the same change is the more
useful half of the finding. The list now states how deep the audit went and carries both challenges;
the general rule the report asks for — one rule for prose enumerations, which must first fix whether
a token is Section 14.1's title or a slug, a question Section 14.1 already answers both ways since
`token_budget_exceeded` is a category and is not Title Case — is a successor decision's. That tenth
category also answers the report's direct question: a Section 14.1 group takes `exhaustive: false`,
while its own closed nine-value enum stays right, because openness is a property of the set and not
of the names (0071). Reconsider the Section 11.4 level when a second tracker adapter lands and
Section 17.3's four
are asserted against it; reconsider the level field when an entry needs a level its group does not
state; reconsider Section 10.8 when its reason codes are enumerated rather than illustrated. Depends
on 0071 and 0048; relates to 0056, 0045, 0046 and 0002. Accepted and applied to `SPEC.md` (Sections
5.5, 17, 17.1, 18.1), `conformance/vocabulary.json`, `conformance/README.md`,
`conformance/vectors/prompt-rendering.json`, and `CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0103 — Publish a prose enumeration when something outside the implementation spells it

**State:** Accepted
**Folder:** [decisions/0103-prose-enumerations/](decisions/0103-prose-enumerations/)

Takes up issue #54's follow-up comment on its own framing — one decision, not four — and names the
test decision 0071 had been applying without stating it. **The question for a candidate token set is
not whether it is an enumeration but what reads the spelling and what happens when the reading is
wrong**, so a prose enumeration is published when something outside the implementation's own source
spells it: a repository author writing configuration, a Conformance Statement author filling a
table, or a conformance check asserting a value. Under it the reported sets are not peers, and the
strongest is not among the three reported. **Section 11.6's five run outcomes** (`dispatched`,
`pull_request_opened`, `run_succeeded`, `run_failed`, `retries_exhausted`) are written by a *human
into `repo.policy.toml`*, and a misspelling was caught by **nothing** — established rather than
assumed: to the engine a bare token is a well-formed *signal*, and `VCSX-SPEC.md` Section 5.1 leaves
the signal set open because "the consumer raises the token the policy binds", so `unknown_trigger`
cannot fire on a typo; Section 6.3's enumerated preflight checks did not cover `on` values; and
Section 11.6's "a trigger that fires with no matching `from`-state transition performs no
transition" made the outcome indistinguishable from a real trigger nobody bound. The policy loaded,
validated, dispatched, and the transition silently never fired. **Section 14.1's nine failure
classes** have a reader too — `CONFORMANCE-STATEMENT-TEMPLATE.md` carries two rows named by class —
and go to 0104, because their token needs an anchor change across seven documents. **Sections 7.1,
7.2 and 7.3 have no reader**: Section 13.3's snapshot exposes no orchestration state as a value,
nothing outside Section 7.2 asserts a phase by name, and Section 7.3's seven prose-titled lifecycle
events reach no configuration, wire or conformance surface. Rejected: publishing all five (a reader
appearing later cannot be predicted, but a set nothing checks the registry against turns a derived
view into an inventory — 0071's reconsideration trigger one step away); a rule keyed on enumeration
*shape* (mechanical and dodges the token question, but gets the two important cases backwards,
Section 14.1 being Title Case *with* a reader and Section 7.2 identifier-shaped with none); and
publishing nothing further (the analysis is durable regardless, but leaves the silent failure
standing). **The whole Section 11.6 vocabulary is published**, all ten tokens, rather than only
Symphony's five: the set exists so one `on` field can be checked against one vocabulary the
specification calls closed, and splitting it by provenance would serve the ownership model over the
person writing the file. The five agent-emitted and task-state tokens are also carried by the engine
registry as `signals`, which stays their authority; `core: false` marks the two the OPTIONAL task
extension owns. Rejected: a per-entry origin field, as machinery for a property no generator uses.
**The spellings are REQUIRED**, on 0102's test — whether a spelling can be required turns on who
owns the condition, and these are Symphony's own run mechanics — and because a closed set whose
spellings are optional is not closed in any way a repository author can rely on. **One consequence
was added beyond what was asked**, because the level is otherwise unobservable: Section 6.3 now
rejects a `tracker.transitions` `on` outside the vocabulary, and **Symphony must be the one to catch
it**, since the engine's signal set is open by design and Section 5.1 gives the consumer the
vocabulary precisely so the consumer can fix it. The **ownership question the deferral bullet held
all of this behind was already answered** — decision 0055: "the signal vocabulary is raised by the
consumer … and signals have no upstream" — before the bullet was written, which with 0102's two
makes four stale deferral reasons, twice inside the decisions repairing them; nothing re-derives a
reason for *not* doing something, so the reader test replaces per-bullet reasons with one re-askable
question. The test lives in `conformance/README.md` rather than Section 17, departing from 0071's
placement of the *precedence* rule: precedence decides which artifact wins a disagreement, which an
implementation acts on, while a publication test decides only what the registry contains. Reconsider
Section 7.2 when the measurement in `Background.md` returns a conformance surface, Section 7.1 when
a monitoring surface exposes a state as a value, and the five duplicated signal tokens if they ever
drift between the two registries. Depends on 0071 and 0102; relates to 0055, 0051, 0056 and 0002.
Successor 0104. Accepted and applied to `SPEC.md` (Sections 6.3, 11.6, 17, 17.3),
`conformance/vocabulary.json` and `conformance/README.md`.

## 0104 — The failure classes get a token

**State:** Accepted
**Folder:** [decisions/0104-failure-class-tokens/](decisions/0104-failure-class-tokens/)

The half of issue #54's follow-up that 0103's reader test selects and 0103 could not publish.
Section 14.1's nine failure classes have a demanding reader: `CONFORMANCE-STATEMENT-TEMPLATE.md`
carries rows *named by class*, so a person transcribes `Repository Provisioning Failures` by hand
into a published document, and Sections 9.7, 17.2, 17.4, 18.1.2, 18.1.4 and 19 name classes in
backticks. What blocked the group was **what the token is**: the nine are Title Case titles while
`token_budget_exceeded` — which Section 14.1's own note calls a failure category and a Section 17.4
check asserts — is snake_case, so `SPEC.md` answered the shape question two ways and a derived view
could not pick between them (0071, restated by 0102). **Each of the nine gains an identifier-shaped
token beside its prose name**, which also makes the section self-consistent. Rejected: publishing
the titles verbatim and letting each implementation slugify (faithful, needs no spec change, but two
implementations slugifying `Workflow/Config Failures` independently yield
`workflow_config_failures`, `workflow/config_failures` or `WorkflowConfigFailures`, and nothing
catches it — the divergence the registry exists to remove, reintroduced with the registry's
authority behind the ambiguity); and letting the registry mint the slugs (cheapest, and exactly the
derived view leading its source that 0071 forbade). Three things application turned up. **The
`_failures` suffix is load-bearing**: the better-reading short form collides `workspace`, `tracker`
and `observability` exactly with `config_namespaces` entries, so every token is the prose name
transliterated rather than shortened. **Section 14.2 did not name the classes it disposes of, and
the mapping is not one-to-one** — its bullets carry their own headings ("Dispatch validation
failures", "Worker failures"), so the correspondence was inferable but unstated, and a registry
entry carrying a recovery disposition would have been inventing the mapping. Section 14.2's bullets
now name their classes, which made two facts visible: `workspace_failures` and
`agent_session_failures` **share** the worker disposition, and `tracker_failures` takes **two**,
because what a tracker failure costs depends on where it occurred. A nine-row mapping would have
hidden both, and the group therefore carries **no** recovery disposition — with the mapping stated
in the prose the entry would only restate it, and 0071's line is that entries carry properties the
specification fixes, not the prose of the rules those properties feed. The contrast with
`error_classes` carrying `gating` is deliberate: Section 5.5 states gating as a two-valued property,
Section 14.2 states paragraphs of behaviour. **The requirement level was not asked and had to be
settled**: REQUIRED, on 0102's test — the condition is Symphony's own, faced identically by every
implementation — because a token another implementation may spell differently is useless to the
Conformance Statement author who motivated the decision. `exhaustive: false` on evidence rather than
reading, `token_budget_exceeded` being a category outside the nine; this does not contradict a
consumer closing its own enum at nine, since openness is a property of the set and not of the names
(0071), and issue #54's reporter is right to have closed theirs for a build shipping no such
extension. Section 14.1 now also states *why* an extension-defined category is spelled differently:
the nine partition where a failure arose, while an extension elevates one condition it disposes of
differently. Reconsider if the nine tokens turn out to be used only by the registry and the
Conformance Statement and never by an implementation's own branching, which would mean Section
14.2's recovery mapping was the real consumer and the token should have been derived from that
table. Depends on 0103 (whose reader test selects this set) and 0071 (whose ordering rule it
follows). Relates to 0102 and 0002. Accepted and applied to `SPEC.md` (Sections 9.7, 14.1, 14.2, 17,
17.2, 17.4, 18.1.2, 18.1.4, 18.2, 19), `conformance/vocabulary.json`, `conformance/README.md` and
`CONFORMANCE-STATEMENT-TEMPLATE.md`.

## 0105 — One lowercase, named once and cited everywhere

**State:** Accepted
**Folder:** [decisions/0105-case-normalization/](decisions/0105-case-normalization/)

Issue #56: Section 4.2 said "Compare states after `lowercase`" and did not say which lowercase, over
a value that is a **comparison key, not a display string**. Three sites branch on it — dispatch
eligibility against `active_states`/`terminal_states` (Sections 8.2, 16.3), the
`max_concurrent_agents_by_state` lookup whose miss falls back to the global limit silently (Sections
5.3.5, 8.3, a `Core Conformance` check in 17.1), and Section 11.6's duplicate `(from, on)` rule,
where the reading decides whether a `repo.policy.toml` **loads at all**. Measured, `İ` (U+0130)
separates the readings: unchanged under ASCII-only, `i` + U+0307 under the Unicode default mapping
(identical in `rustc` 1.95.0, CPython 3.13.5 and Node v26.5.1), and bare `i` under a Turkish
tailoring, which also maps `In Progress` to `ın progress` and so makes the **host's environment** an
input to a conformance-checked comparison. Section 4.2 now names the rule once —
`Lowercase Normalization`, the Unicode Default Case Conversion with the full mappings, no
language-specific tailoring (MUST NOT), and no Unicode normalization form applied — and the state
rule, the three differently-worded label rules (Sections 4.1.1, 5.3.1, 11.3), the state-keyed
configuration sites and the Section 16.3 reference algorithm all cite it. Rejected: ASCII-only
lowercase (0047's byte-level philosophy, no Unicode library, no version drift — but 0047 governs a
*projection* into a directory name where any total function serves, while this is a *match* against
an operator-typed string, and ASCII-only makes case-insensitivity a property of the tracker's
alphabet, holding for `TODO` and silently not for `İNCELEME`); full case folding (what Unicode
specifies for caseless matching and it folds `Straße`/`STRASSE`, but `rustc` 1.97.1 has no
`to_casefold` at all and Go's `strings.EqualFold` is *simple* folding whose own package example
asserts `EqualFold("ß", "ss") == false` — the primitive whose appeal is that every standard library
has it, which folding is not); and requiring NFC (real — the tracker owns one side and
`symphony.toml` the other — but **not an interoperability defect**, since every implementation that
lowercases the code points as given agrees, so it is the operator's surprise and not the
specification's silence, and it is stated as *not applied* rather than left unsaid). Three findings
application turned up. The existing corpus does not merely fail to check the locale-sensitive
reading, it checks it **conditionally on the runner's host** — `In Progress` → `in progress` does
fail under a Turkish tailoring — so a green corpus on CI is not evidence about the deployment host.
Section 16.3's pseudocode compared raw states, reading as if the rule did not reach it. And the new
decomposed vector **arrived on disk composed**, silently normalized by the authoring tool: it still
passed, because a composed input lowercasing to a composed output is a case every reading agrees on,
so the vector had degraded into a tautology that two identical-looking spellings hid — caught by
re-parsing and comparing code points, not by reading. Non-ASCII vector values are now `\uXXXX`
escapes as a stated corpus convention, `workspace-key.json` (verified intact first) re-encoded to
match. Three vectors were added and no `normalize_label` function, deliberately: it would add a
harness entry point to re-check the same mapping. Reconsider on either of two reports — a state that
renders identically and never matches (the NFC axis, its own decision) or a `ß`/`ss`-shaped
near-miss (case folding, with the dependency cost then accepted). Relates to 0047, 0046 and 0002.
Accepted and applied to `SPEC.md` (Sections 4.1.1, 4.2, 5.3.1, 5.3.5, 8.2, 8.3, 11.3, 11.6, 16.3,
17.1, 17.3), `conformance/vectors/state-normalization.json`,
`conformance/vectors/per-state-concurrency.json`, `conformance/vectors/workspace-key.json` and
`conformance/README.md`.

## 0106 — A read that answers `unchanged`, and the validator that asks for it

**State:** Accepted
**Folder:** [decisions/0106-conditional-forge-reads/](decisions/0106-conditional-forge-reads/)

Issue #58's first engine primitive. The engine already tells a consumer to poll —
`merge:checks_pending` carries the default need `await_checks` (Section 4.3) — and provides no
affordable way to come back: `pr_state` reads the pull request's number, state and head in full on
every call, so a twenty-minute check run polled every thirty seconds is forty full reads per unit of
work, linear in concurrent units and charged against a budget the same consumer cannot see (0107).
No loop, cadence or budget policy moves into the engine, which Section 2.2 keeps outside it; what
moves is the primitive a consumer cannot build for itself, because the engine owns the forge call.
`pr_state(work_branch, known_validator)` gains a fourth answer, `unchanged`, and returns a
**validator** the consumer presents on the next read. Verified against the upstream documentation
rather than assumed: GitHub REST states that a conditional request "does not count against your
primary rate limit if a `304` response is returned", and recommends it for polling — but **GitHub
GraphQL documents no conditional request at all**, and the downstream `--watch` drain that prompted
the issue ran on GraphQL, so this primitive does not retire the failure it is filed under; what
protects a consumer there is the visible budget (0107) and a cadence paced against it. Forgejo's
coverage could not be established, which is the argument for the descriptor field rather than an
omission. `unchanged` is a **fourth** answer and not a spelling of the other three: read as `none` a
`304` would let `create_or_update_pr` open a second pull request, and read as undetermined the
cheapest answer would refuse what the expensive one permits — the failure Section 9's answer
discipline exists to prevent. The engine presents a validator only on the read whose answer it
**reports** (`status`) and on neither of the two an operation **conditions a write on**, because
`unchanged` carries no head and a `merge` resolving one against a consumer-remembered head would
defeat the `merge:head_moved` guarantee (0077). The validator round-trips through the consumer
because the engine holds nothing between invocations (Section 1.3), which is also why it is the one
consumer-supplied value not readable from the consumer configuration — a configured one is stale by
construction. Reported as a `pr_state_unchanged` output beside `base_absent` and
`pr_state_unavailable`, not as the `status:not_modified` reason the issue asks for: a reason token
is a trigger (Section 5.1), and binding policy to the freshness of the consumer's own cache puts a
condition the repository cannot see into the vocabulary a repository writes against — the argument
against being that a consumer branching on `reason` learns the read was cheap without descending
into `outputs`. A backend declaring no conditional-read support is presented no validator and
answers in full; that is not `unsupported` (Section 4.3), since the operation proceeds and what is
absent is a saving, which is what lets a consumer write one loop rather than one per forge.
Reconsider on a forge whose conditional read is keyed to a *query* rather than a resource, which
would make the per-`work_branch` granularity wrong, or on a `304` observed to cost budget, which
would leave 0107's cadence carrying the whole load. Relates to 0076, 0077, 0107 and 0108. Accepted
and applied to `VCSX-SPEC.md` (Sections 4.1, 8.1, 8.2, 9, 9.1, 9.2, 13.1, 13.2, 13.3).

## 0107 — The budget the call already saw

**State:** Accepted
**Folder:** [decisions/0107-forge-budget-snapshot/](decisions/0107-forge-budget-snapshot/)

Issue #58's second primitive, and the one that carries the load 0106 cannot. Exhaustion was
**discovered as a mid-`land` failure** — not as a warning or a threshold crossing, but as the
operation meant to merge the work reporting it could not. Today a consumer can learn nothing about
its own headroom except by failing: every Section 9.2 capability reaches the code host, every forge
reports what the credential has left on that call, and the engine discards it, so a
`create_pr:created` is a call that observed the budget and reported everything except the budget.
Every forge capability now answers the snapshot it observed, or that the forge reported none, and
the most recent lands in `outputs.forge_budget` — reported on a call that succeeded exactly as on
one that did not, since a budget visible only at exhaustion is visible only after the decision it
should have informed. Stated over the capability list rather than per capability, the shape Section
9.1 uses for its bookkeeping-write allowance, so a capability added later inherits it. Rejected: a
`budget()` probe of its own, which loses twice mechanically — it **costs the thing it measures**, so
a consumer polling headroom has built a second drain to monitor the first (GitHub exempts its
rate-limit endpoint, but a specification cannot rest a primitive on one forge's exemption), and its
answer is **stale before it is used**, the real question being what the last call left rather than
what was true a moment ago, with every concurrent holder of the credential spending in between.
Verified rather than assumed: GitHub GraphQL is accounted in **points** ("5,000 points per hour per
user"), and its own documentation states "The REST API also has a separate primary rate limit" — two
budgets, two units, one credential. So the snapshot carries **buckets**, not a number: pacing
request-based work against a query-based balance is not a conservative approximation but an
unrelated figure, and the observed drain emptied one while the other was untouched. Bucket identity
is opaque and the counts carry no unit this specification names, because a normalized bucket set
would be a mapping into a model the engine invented — whether a forge's second bucket is a narrower
window on the first or an unrelated pool is not establishable at a plugin boundary. The engine
reports and acts on nothing (Section 2.2): what a low bucket is worth spending on depends on what
else the consumer means to spend it on and how many other holders are spending concurrently, neither
visible from inside one invocation. One departure is stated rather than left to be noticed: the key
is absent both where no forge capability was reached and where one was and the forge reported
nothing, which Section 9's answer discipline would normally forbid — that rule governs a value the
engine composes an operation from, and no operation, reason or precondition branches on this one.
The Section 9.1 network capabilities are out of scope, a git transport publishing no quota.
Reconsider on a forge reporting budget **only** on a dedicated endpoint, which would force either
the rejected probe or a permanently absent key, or on a consumer pacing correctly and still
exhausting — which would mean the reported figure is not the enforced one and the snapshot is
advisory in a way this record does not claim. Relates to 0106, 0108 and 0112. Accepted and applied
to `VCSX-SPEC.md` (Sections 8.2, 9.2, 13.1, 13.2, 13.3).

## 0108 — A throttle is not a failure, and retryable is a property of the need

**State:** Accepted
**Folder:** [decisions/0108-transient-forge-reasons/](decisions/0108-transient-forge-reasons/)

Issue #58's third primitive. The defect is not that a consumer cannot tell a 429 from a 422: it is
that a throttled forge takes the universal `failed`, `failed` is class `error`, and an `error`-class
result no edge disposes of reaches the built-in default, which **fails the flow** (Section 5.4) — so
a condition that clears in sixty seconds **ends the unit of work**, through the same path and with
the same finality as a validation error that never clears. The mirror defect is the same missing
axis read the other way: a consumer that retries `error` because some of them clear also retries a
malformed pull-request title forever. The issue's own report of a 429 "landing as an unrelated
reason like `checks_pending`" is the sharpest form — `checks_pending` carries `await_checks`, so a
throttle misreported that way sends a consumer to poll a forge that just asked it to stop.
`rate_limited` and `forge_unavailable` join Section 4.3 as `(any forge)` rows over `push`,
`create_pr` and `merge`, both class **`needs_caller`** — chosen for the disposition it produces, not
for how the condition reads, since `needs_caller` escalates where `error` fails and Section 4.2
defines it as an operation awaiting a caller action, waiting being one. **Two reasons, not the four
the issue names**, split by repair rather than cause: `rate_limited`'s wait is informed, the
exhausted bucket and its `resets_at` already in `outputs.forge_budget` (0107), while a 503, an
expired bound and a TLS failure carry one uninformed repair and are therefore diagnosis rather than
routing — reported as `outputs.forge_unavailable_condition`, which is the arrangement 0104 recorded
for `hook_unanswered`'s three conditions and for the same stated reason. The argument for four is
that a consumer may alarm differently on a handshake failure than on a hiccup; it is served by the
diagnostic token without spending four registry entries a repository would bind with four identical
edges. **`retryable` is a property of the `need`, not of the reason** — it means re-invoking the
same entry with the same arguments, after a delay and with no further action, MAY succeed, which is
decided entirely by what the need asks for: `integrate_then_retry` is false because an `integrate`
must run first, `reread_then_retry` is true because the re-read is what a re-invocation does.
Placing it on the need rather than as a registry column means it follows from the reason's
`default_need`, already REQUIRED for every `needs_caller` reason, so the two cannot disagree. It is
carried rather than derived because Section 8.5 permits new `need` tokens in a `MINOR`, and a
consumer holding its own mapping is correct until that release and then silently wrong — the job the
`#class` fallback does for a new reason. It joins the major-stable surface on the same footing as a
reason's class. Scope limit recorded rather than left implied: **the version-control transport gains
no transient reason**, a git remote publishing no budget or reset time and `provision:unreachable`
already routing the caller-repairable git-side condition away from `failed`; so an `integrate` whose
fetch times out still fails the flow, and a report of that is the reconsideration trigger. Reconsider
also if `forge_unavailable`'s three conditions turn out to be routed on rather than logged, which
would mean two reasons was one too few. Relates to 0104, 0107 and 0109. Accepted and applied to
`VCSX-SPEC.md` (Sections 4.3, 8.2, 8.4, 8.5, 9.2, 13.1, 13.2), `conformance/vcsx/vocabulary.json`
and `conformance/vcsx/README.md`.

## 0109 — The other program the engine waits on

**State:** Accepted
**Folder:** [decisions/0109-network-call-bound/](decisions/0109-network-call-bound/)

Issue #58's fourth primitive. Section 6.6 bounds a hook on the ground that it is "the one place the
engine hands control to a program this specification does not describe" — and it is not the one
place. A network call is the second, with the same shape: the engine hands a request to a server it
does not describe and waits for an answer it does not control, and **nothing bounded that wait**.
What that costs is not a slow operation but the property the contract rests on. The engine runs a
bounded sequence and exits (Sections 1, 2.2, 5.6), which is the sentence a consumer's
escalate-and-exit loop is built against, and a host that accepts a connection and never answers holds
the invocation open indefinitely — so that sentence was conditional on every server the engine talks
to answering. `network_bound_ms` is a consumer-supplied bound on **one** network call, not on an
operation's total: an operation realized through two capabilities is not held to one deadline across
both, since the second may be local (`integrate` is `fetch_base` then `merge_base`) and a bound
covering it would be bounding something other than a wait on a server. Its value is
`Implementation-defined` and MUST be documented, and an engine MUST admit a configured value of at
least 600 seconds — the same floor Section 6.6 fixes, reached from this bound's own capability set
rather than by copying: it covers `ensure_store`, which fetches an entire repository, so the floor
accommodates the **slowest** network unit and an engine capping below it would make the
specification's own provisioning operation unusable at scale while staying conformant. A hardcoded
value settles nothing, for the reason Section 6.6 gives its floor — sixty seconds is generous for an
API call and far too short for a clone, so an engine picking one number picks it wrong for one of
the two. The bound is the consumer's and `repo.policy.toml` carries no key for it, argued from this
section's own placement rather than only from Section 6.6's sourcing rule: the endpoint and the
credential are already the consumer's, and how long to wait for an endpoint is a fact about the
consumer's environment — a repository cannot know whether its policy runs against a forge on a LAN
or across a saturated link. Expiry divides by transport, reusing what 0108 already built: a forge
call is `forge_unavailable` carrying `bound_elapsed`, deliberately the same spelling Section 6.6
fixes for a hook still running when its bound elapsed, since one event on two kinds of unit should
not diagnose differently by which program the engine happened to be waiting on; a version-control
call reports what it reports today, `provision:unreachable` or the universal `failed`. The engine
stops the call and does not retry — an engine retrying inside the bound would make it mean the total
wait multiplied by an attempt count the engine chose rather than the consumer (Section 2.2).
Reconsider if every conforming engine documents a per-capability table, which would mean the
per-call unit was wrong and the bound belongs per capability; or on an `ensure_store` reaching the
600-second floor in ordinary use, which would mean provisioning needs a bound distinct from the API
calls' rather than a shared one with a high ceiling. Relates to 0081, 0108 and 0112. Accepted and
applied to `VCSX-SPEC.md` (Sections 8.1, 9, 13.1, 13.2, 13.3).

## 0110 — A field that moved is not a field that is empty

**State:** Accepted
**Folder:** [decisions/0110-forge-parse-answer-domain/](decisions/0110-forge-parse-answer-domain/)

Issue #59's first half. The obligation already existed — Section 9 requires a value-answering
capability to be able to say it could not determine a value and forbids spelling that as the value's
absent case, and Section 4.1 puts it in one line: a read reports no determinate value it did not
establish. What this decision fixes is **where the rule is broken**, and the gap is that the rule is
written over what a capability *answers* while the defect lives in how the answer is *derived*. No
backend author decides to report a missing field as an empty one; a deserializer does it by default,
a field absent from the payload taking the type's zero value, and the capability then returns a
well-formed value that satisfies every existing clause to the letter. The failure path is fully
specified by text already present: a renamed number field yields a default, `pr_state` answers
**none**, and `create_or_update_pr` — required to maintain one pull request per work branch, which
Section 9.2 says requires finding the one that exists — **creates a second**, while `push` stops
refusing over a CLOSED/MERGED one and `status` reports no pull request where `pr_state_unavailable`
is the truth. Section 9's preamble now states that the obligation reaches the derivation, and Section
9.2 that a response not carrying a depended-on shape is a value the capability could not determine —
never a default, an empty value, or the absent case — with an unrecognized pull-request state the
same condition one level in, since reading it as `closed` off an enum's fallback arm is the same
defect with a different default. The boundary is stated in the other direction too, because the
conservative reading is unusable: a field the capability does **not** read is not drift, forge
payloads gaining keys continuously, and a backend refusing every unrecognized response would break on
the next upstream release with nothing wrong. This record does not overclaim: the clause adds no
requirement and is a redundancy placed where the failure actually occurs, which is its whole
justification — plus a Section 13.1 check, since a prose obligation on a parse step is verifiable
only by reading a backend's source, and an injected-response check is verifiable against a binary.
Reconsider if a backend is observed refusing on drift that did not matter, which would mean
"depended-on shape" is being read as "the shape the forge documented". Relates to 0076 and 0111;
adjacent to 0108, which covers a forge that did not answer where this covers one that answered
something unreadable. Accepted and applied to `VCSX-SPEC.md` (Sections 9, 9.2, 13.1, 13.2).

## 0111 — The corpus states the assertion; the harness holds the fixture

**State:** Accepted
**Folder:** [decisions/0111-fault-injection-vector-shape/](decisions/0111-fault-injection-vector-shape/)

Issue #59's second half, driven by the sharpest observation in the study behind issues #58–#62: **the
failures that bit us are exactly the ones with no test** — 99 vectors green, none of them in the
transient family. A fault-injection case cannot be an ordinary vector here, and the reason is
structural rather than a matter of effort: every file under `conformance/vcsx/vectors/` states a pure
function checkable by reading JSON and comparing two values, which is what makes the corpus
language-neutral, while asserting that a 429 yields `rate_limited` requires something to *be* a forge
and return a 429 on demand. That is a harness — a program in one implementation's language — and this
repository holds none and should not, the corpus deriving from a specification and being consumed by
every implementation. So the halves split where each can be stated authoritatively: **this repository
fixes the assertion**, read from `VCSX-SPEC.md` as every entry is, and **an implementation authors the
cases** against the twin it owns, the fixture being a property of a forge and a backend that reaches
two forges as two different responses. Six injected conditions are enumerated with the sections they
derive from, and five assertions are REQUIRED of each: the reason and its proto class, the need and
its `retryable` value, the `outputs` keys, undetermined-and-distinguishable for a drift case, and —
called out separately — that the operation **did not act**, because the other four are readable off an
envelope while that one is a statement about the forge afterwards, and a vector asserting only the
envelope would pass for an engine that reported `create_pr:failed` and created a pull request anyway.
A runner that cannot execute such a file MUST report it **not run**, never passed, so "the corpus is
green" keeps meaning one thing. Rejected: authoring the data here with the harness obligation
attached — it would make the first file in this tree that no reader here can execute, the same hazard
0105 found in a vector that had degraded into a tautology, a corpus whose green is conditional on
something the corpus does not state. The honest form of that alternative is that a specification
repository should be able to demand a test rather than describe one; that demand is met normatively by
the Section 13.1 checks the sibling decisions added, and what is not claimed is that this repository
verifies them. Reconsider if two implementations' suites disagree about what one injected condition
should yield, which would mean the schema underspecifies the assertion and the data must come back
here — at which point the language-neutrality cost is worth paying, a corpus nobody can run beating
two that disagree. The concurrency-stress tier is deliberately not covered: it asserts over N
concurrent sessions rather than one injected response, and is deferred to the Symphony-side work.
Relates to 0106–0110, 0053 and 0105. Accepted and applied to `conformance/vcsx/README.md` and
`VCSX-SPEC.md` (Section 13.1).

## 0112 — The wait becomes an operation, and the non-goal it tests gets written down

**State:** Accepted
**Folder:** [decisions/0112-bounded-await-checks/](decisions/0112-bounded-await-checks/)

Issue #60's engine half. The issue states its own fork — a shared consumer library, or a bounded
engine subcommand — and **(b)** was chosen by the maintainer. Applying it surfaced a finding that
reordered the decision: the boundary the objection to (b) rests on **was never written down**.
Section 2.2's Non-Goals are four — credential storage, agent-sandbox mechanism, commit conventions, a
general-purpose workflow engine — and retry, back-off and budget appear in none of them; the claim is
asserted only in text this slice itself added, since 0107 and 0109 were each drafted citing
"(Section 2.2)" for it. The downstream study says the same thing with the same confidence. So the
boundary everyone reasons from was folklore: substantively true of the design, never stated, never
checkable, never decided. A bounded exception cannot be stated against a rule that does not exist, so
Section 2.2 gains the non-goal first — deciding **when** to retry, **how long** to back off, and
**what a budget is worth** are the consumer's — and `await_checks` is then a stated exception to it.
The exception is to **waiting**, not to **deciding**: the bound, the read count, the interval and the
budget floor are all invocation arguments, the engine compares against numbers it was handed and
chooses none, and an invocation supplying none makes a single read and cannot loop. The usual
objection to (b) is weaker than it looks — 0081 already settled that a bound is a bound on a unit,
and the engine already waits on hooks and (since 0109) on network calls — and the real cost is that a
budget-aware cadence needs a budget policy, which this containment is designed to keep outside.
Building it required a read that did not exist: 0106 gave the conditional-read validator to
`pr_state` because that was the only forge read, while issue #58's VX-1 names two, so `checks_state`
joins Section 9.2 with the same four answers and reuses the validator machinery rather than
rebuilding it. Polling by re-dispatching `merge` was rejected outright — it asks a cheap question
with a **mutating** request, charged at a mutation's cost and carrying whatever a refused merge
costs on a given forge — and the new read has a benefit past the loop: check state stops being
reachable only by asking a question whose favourable answer merges the work. `await_checks` is an
operation and an entry point rather than a front-end sequence, which buys three things: `<op>:<reason>`
results a repository can bind, membership of the gated-at-no-position category (a gate before a wait
inspects nothing), and **one** dispatch against the flow bound however many reads it makes — counting
each read would make a policy's flow budget depend on how long a CI run took. Four reasons:
`still_pending` and `budget_floor` are separate because one is met by waiting longer and the other by
waiting for a bucket to refill, and a consumer that could not tell them apart would raise the wrong
bound. The `await_checks` **need** and the `await_checks` **operation** share a spelling
deliberately: needs and operations are separate vocabularies, and the need now names the operation
that meets it. Steelmanned and rejected: **(a)** a shared library keeps cadence policy with the party
owning the budget, but turns a skill's dependency-free shell invocation into a language-specific
build dependency, and a library nobody links is a governance layer that governs nothing — which is
how the drain happened; **(c)** stating the loop's obligations and leaving packaging
`Implementation-defined` is this repository's idiom and was the recommended option, but specifies
nothing a skill can *call*, so "written once" becomes written once per implementation — right if the
two consumers needed different loops, and they need the same one. Reconsider if the argument surface
grows: a fifth parameter — a back-off curve, a per-bucket policy, jitter — would mean the engine is
accumulating the budget policy this decision claims it does not hold, one argument at a time, and
that accumulation rather than the wait is what would make (b) the mistake its objectors expect. Also
reconsider on a forge whose check state is not aggregable. Relates to 0081, 0106, 0107, 0108 and
0109. Accepted and applied to `VCSX-SPEC.md` (Sections 2.2, 4.1, 4.3, 5.6, 7.2, 8.1, 9.2, 13.1,
13.2), `VCSX-CONTRACT.md` (Sections 3, 6) and `conformance/vcsx/vocabulary.json`.

## 0113 — The specification already knows how to do this, in one place and not the other

**State:** Accepted
**Folder:** [decisions/0113-liveness-by-result-token/](decisions/0113-liveness-by-result-token/)

Issue #61, which the study calls the sharpest Symphony-specific lesson: a backgrounded poller killed
by a sandbox seccomp filter exited `0`, and the parent read that as success and merged incomplete
work. The fix is **already written, for the engine**: `VCSX-SPEC.md` Section 8.3 evidences a result
by a composed envelope, reserves `1` for an invocation that produced none, and reads every code
outside its four status-bearing ones the same way — so a seccomp kill of a `vcsx` invocation yields
no envelope and a conforming consumer reads no result rather than a status. The Agent Runner
(Section 10.7) has no such rule: it says `run_turn` returns "a result with its outcome" and that "on
any error the Agent Runner fails the worker attempt", and nothing says what makes an outcome a
success. Section 10.4 already fixes `turn_completed` and requires an adapter to spell the condition
that way; it did not require one to have **occurred**. So an agent process killed by seccomp, the OOM
killer or `SIGKILL` ends with status `0`, no error is reported because the thing that would report
one is dead, and the turn is reported complete — the consequence being not a run that fails but a run
that **succeeds wrongly**, and a failed run retries where a wrongly successful one lands whatever was
in the working tree when the process died. Three clauses, each checkable without knowing the adapter:
success is reported only where the adapter **observed** the protocol's terminal success signal; a
process's **exit status is not a turn outcome** in either direction, being evidence a process ended
and none of what it accomplished; and an adapter MUST NOT report success on the evidence that a
backgrounded process did not report a failure — the general form of the reported failure rather than
the instance. Section 9.4's hooks get the narrower half, a hook terminated by a signal being a failed
hook, because a shell script carries no event vocabulary and what is checkable instead is the wait
status; without it a killed `after_create` is a passed hook and fatal to nothing. **Core**, on the
stance this slice uses — split by what a requirement costs a single-tenant deployment — because it
costs nothing: adapters already receive these events since Section 10.7 already requires them to be
emitted, and what changes is that the outcome must be derived from them; seccomp, the OOM killer and
`SIGKILL` are not properties of concurrency, so a one-session deployment gets the same protection. A
requirement that is free and prevents merging unfinished work has no business being optional.
Steelmanned: Symphony defers success and failure to the agent protocol on purpose, and a
specification adjudicating what a completed turn is reaches into a boundary it drew deliberately —
respected here, since the rule does not say what a successful turn *is*, only that the adapter must
have observed the protocol saying so; the boundary stands and the burden of proof moves. Reconsider
on an adapter for a protocol with **no** terminal signal, where the answer is a capability descriptor
declaring it and a statement of what selecting such an adapter gives up, not a weakening for
everyone. Relates to 0076, 0104 and 0110. Accepted and applied to `SPEC.md` (Sections 9.4, 10.6,
10.7, 14.1, 17.5, 18.1).

## 0114 — One pull request per issue is a rule about which one

**State:** Accepted
**Folder:** [decisions/0114-pr-identity-under-concurrency/](decisions/0114-pr-identity-under-concurrency/)

Issue #62's PR-identity item. Section 9.10 says Symphony "maintains one pull request per issue" and
that "the head is the work branch"; what neither it nor Section 8.3 says is **how an update finds the
pull request it updates**. The engine looks it up keyed on the work branch as head, so the identity
of the thing being written is derived at write time from a branch name — and a branch name is a
lookup key, not an identity: what it resolves to depends on the forge's state at the moment of the
lookup rather than on anything the run established. Observed: a concurrent session overwrote
another's title and body, and a later merge squashed the hijacked title into history — which
Section 9.10's own "title verbatim" squash rule makes permanent. The engine had already solved the
harder half and only the harder half: 0077 requires `request_merge` to refuse where the head moved,
and `VCSX-SPEC.md` Section 9.2 goes as far as saying a backend whose forge cannot condition the merge
does not declare the capability, "because a merge that cannot be conditioned merges content no
lifecycle position inspected". `expected_head` pins **what** is merged; nothing pinned **which** pull
request is written, and a hijacked title passes every head check because the head never moved.
Symphony now carries the forge's own pull-request identity into every mutating operation, re-reads it
immediately before the write — exists, carries this run's work branch as head, targets the resolved
base — and refuses on mismatch with `pr_identity_mismatch`, distinct from `pr_conflict` because one
is a write that could not be applied and the other a write that would have been applied to the wrong
thing. The refusal is **not retried**: a second writer is active, and a retry re-reads a state that
writer is still changing. The guarantee is stated honestly rather than overclaimed — "immediately
before" bounds the pair as the closest the forge's interface allows and **narrows** the window rather
than closing it, since Symphony cannot make the pair atomic; a forge offering a conditional update
closes it and a plugin whose host has one SHOULD use it, the shape `expected_head` already has.
**Core**, on this slice's cost test: a single-session deployment resolves once, re-reads, finds it
unchanged and writes, and after 0106 that read is conditional where the forge supports one — a `304`
on the common path. It is also not only a concurrency guard, which is the answer to the objection
that Section 8.3 already covers this: Section 8.3 bounds *Symphony's own workers* and none of the
reported writers were one — a second deployment, a developer's interactive invocation, a skill-driven
agent (the consumer issue #60 is actively specifying for) — and without concurrency at all, a pull
request a human closed or retargeted between two runs is the same mismatch, written to today. Issue
#62's cross-cutting stress tier lands as a `Concurrency Stress` validation profile and Section 17.9,
RECOMMENDED on the same ground `Real Integration Profile` is: it needs a live forge and real
concurrency, and making it REQUIRED would make conformance depend on a harness this specification
does not describe — the boundary 0111 drew for the engine's fault-injection vectors, reached again
for the same reason. Reconsider if refusals appear in normal operation with no competing writer,
which would mean the check is pinned to fields that legitimately change. Relates to 0077 and 0106.
Accepted and applied to `SPEC.md` (Sections 9.10, 17, 17.9, 18, 18.1).

## 0115 — Observing the budget is free; spending on it is not

**State:** Accepted
**Folder:** [decisions/0115-forge-budget-and-checks-wait/](decisions/0115-forge-budget-and-checks-wait/)

Issue #60's SY-1 and issue #62's SY-2, together because one is the other's input. Most of SY-1 is no
longer Symphony's: 0112 made the wait an engine operation, so what remains here is **when** to
dispatch it, **which bounds** to hand it, and **what to do** with each outcome — and explicitly not a
loop, since a second loop around one that already loops is two bounds with no defined relationship.
Two of the issue's four requirements were answered by the engine work (conditional reads by 0106, the
budget-respecting cadence by `await_budget_floor`), and one asked-for thing turns out to be
**unnecessary**: because 0112 made awaiting an *operation* rather than a front-end sequence, its
outcomes are already `<op>:<reason>` results the action-policy machine routes with the `#class`
fallback, so the `checks:*` trigger vocabulary the issue requests would be a second spelling for
outcomes already carried. SY-2 asks for a promotion to Core and gets neither a yes nor a no, because
the filed item bundles two things with very different costs — which is the conformance stance doing
work rather than being restated. **Recording** the snapshot is Core: after 0107 it arrives unbidden
in the envelope of a call Symphony already made, nothing is polled or configured to get it, and a
deployment that discards it has thrown away the only evidence that would afterwards explain where a
budget went, having paid nothing for it. **Acting** on it — a pre-emptive check before a mutating
call, a warn threshold, a floor — needs operator-chosen numbers and can wrongly withhold work, so it
stays an OPTIONAL extension under `forge_budget.*`, the shape Section 8.9's gate already has. It is a
**sibling section** rather than an extension of 8.9: that section governs the coding-agent provider's
account — different account, credential, operations and units — and states the rule this inherits,
that one account's quota is never summed into another's. The steelman for folding them is real
(8.9's snapshot is proven and general) and loses on the staleness machinery: half of 8.9's structure
exists because a provider quota is fetched out of band and can be old, while a forge budget arrives
attached to the call that just spent it, so reusing the shape would carry `fetched_at`,
`stale_after_ms` and an `UNKNOWN` that cannot occur — and an implementer reading it would build a
poller for a figure needing none. The guard checks before a **mutating** call rather than only
gating dispatch, because the expensive moment for this budget is the write: a run that has already
provisioned a workspace and spent an agent session fails differently from one never dispatched. The
one wholly-Symphony piece is the terminal disposition: `still_pending` and `budget_floor` **park**,
not retry and not fail — Section 8.4's backoff is for transient failures and a check run still
running is not failing, so a retry re-enters a wait that exhausts the same bound while holding a
worker slot, and a budget floor would be spent against by the retry meant to get past it. That is
`token_budget_exceeded`'s disposition, for the same reason: an operator bound, reached. Finally, a
successful await is **not** authority to merge — it reports checks passing for the head *it* read,
and a push into the gap between awaiting and merging is exactly `merge:head_moved`, so the merge
still conditions on its own read (0077) and re-verifies identity (0114); treating it otherwise would
undo that guarantee by way of a feature added to serve it. Reconsider if one set of await bounds is
wrong for every repository, which would put them in `repo.policy.toml` where a repository knows its
own CI, or if the Core-recorded snapshot turns out never to be read — which would mean the
justification was cost rather than value. Relates to 0077, 0106, 0107, 0112 and 0114. Accepted and
applied to `SPEC.md` (Sections 6.4, 8.11, 9.10, 13.5, 14.2, 17.4, 18.1, 18.2) and
`conformance/vocabulary.json`.

## 0116 — One credential is a scope decision nobody made

**State:** Accepted
**Folder:** [decisions/0116-credential-partitioning/](decisions/0116-credential-partitioning/)

Issue #62's credential item. Read carefully, the specification never chose a shared token and was
wrong: it never asked the question. `vcs.git_credential` and `vcs.forge_credential` are flat keys,
Section 8.7 routes many repositories through one orchestrator, and nothing states how the two
compose — which in practice means one, because a flat key has one value. So the fix is not to change
a policy but to make the scope an explicit decision. Two distinct failures motivate it and only one
is about security. **Budget contention**: a forge meters a *credential*, not a repository, so
repositories sharing one are a single spender to the code host and a runaway loop in one exhausts
every other's budget — 0107 makes that observable and 0115's guard can pause on it, but neither can
*separate* budgets that are not separate, and a guard pausing on a low bucket pauses the repositories
spending nothing too. **Blast radius**: a credential reaching every repository the orchestrator
serves is one whose compromise reaches every repository it serves. That second point is explicitly
orthogonal to the secret-isolation invariant (Sections 9.6, 15.3), which governs **where** a
credential goes and says nothing about **how much** one is worth; the invariant holding perfectly
does not bound what a leaked value unlocks. The rule: an operator MAY configure the pair per
repository, an implementation **MUST support** that configuration, the orchestrator-level value
applies where a repository configures none — so nothing that works today stops working — and a
deployment serving repositories under different ownership SHOULD partition. A `credential_scope` log
field records which scope a call was made under, naming the scope and never the credential. Pitched
as an extension rather than Core on this slice's cost test: an operator provisioning one token now
provisions several, each with its own creation, storage, rotation and revocation, and for a
single-repository deployment the partition is a partition of one. The split that makes the
recommendation usable is that **supporting** it is required of an implementation while **using** it
is the operator's — otherwise a multi-tenant operator would hold a `SHOULD` unsatisfiable on a
conforming implementation. Steelmanned: a bounded blast radius is a security property and security
properties are poor candidates for optionality — defeated because Core here would have to mean
*mandating* separate credentials, making a single-repository deployment provision per-repository
tokens it does not have and putting this specification into credential lifecycle. **The per-agent
half of the filed item is declined**, explicitly rather than by omission: the forge meters a
credential, the observed unit of contention is the repository, and minting one per run needs an
issuance/rotation/revocation mechanism this specification does not define. Reconsider if contention
is observed *within* one repository, which pacing rather than a finer partition would answer.
Relates to 0107 and 0115. Accepted and applied to `SPEC.md` (Sections 6.4, 8.7, 13.1, 15.3, 18.1, 19)
and `conformance/vocabulary.json`.

## 0117 — The sandbox is stated over secrets, and the damage came from something else

**State:** Accepted
**Folder:** [decisions/0117-env-isolation-guarantee/](decisions/0117-env-isolation-guarantee/)

Issue #62's environment item. Section 9.6 guarantees a great deal about secrets — "every
secret-bearing environment variable MUST be scrubbed before the sandbox starts" — and nothing about
anything else, so every other variable is inherited by default because nothing says otherwise. The
assumption does real work: a reader who believes the sandbox isolates the agent reasonably believes
it isolates the agent's environment, where what is required is isolation from credentials and the
host filesystem. The observed failures — an inherited `CARGO_TARGET_DIR` building into a sibling
worktree, a `.venv` shebang running another checkout's interpreter — are **not containment
failures**, which is what decides where the fix goes: the variable was legitimately inherited, the
path legitimately reachable, the agent legitimately used it, every component behaved as configured,
and the outcome was a session acting on a sibling's configuration. A stronger sandbox profile
addresses none of it. So the requirement is that the run's environment is **constructed** rather than
**inherited**: composed from what the run needs, with a variable naming a **location outside the
run's own workspace** — build output directory, cache root, toolchain or interpreter path, temporary
directory — kept out unless the deployment named it, and such a location resolving inside the run's
workspace where one is needed. The prohibition is stated over what a variable *names* rather than
over a list of names, because a list is per-ecosystem and would be incomplete before it was written;
what an implementer gets instead is a writable test — poison one such variable, assert the agent does
not see it. The composed set is `Implementation-defined` and documented, the disposition the sandbox
profile and egress policy already have. **Core**, and free: a deployment already filters the
environment to scrub secrets, so this changes the filter from a denylist to an explicit set. It is
also not concurrency-specific — a single-session deployment with an inherited build-output directory
writes somewhere it did not intend too and merely lacks a sibling to collide with, which is the
property this shares with 0113 and 0114: concurrency reveals these rather than causing them.
Steelmanned: the sandbox profile is already `Implementation-defined` with a documentation obligation,
so a deployment wanting this configures it — defeated because that delegation covers the *profile*,
implies nothing about environment construction, and a conforming implementation on the named baseline
inherits the environment; a knob nobody is told to turn for a property never claimed is a gap with an
`Implementation-defined` label nearby. Reconsider if implementations diverge on what "names a
location outside the workspace" covers, where the repair is a per-ecosystem baseline published beside
the specification as the token registry already is. Relates to 0113 and 0114. Accepted and applied to
`SPEC.md` (Sections 9.6, 17.2, 18.1, 19).

## 0118 — A tool that is not there yet is a tool the workspace cannot use

**State:** Accepted
**Folder:** [decisions/0118-provisioning-survivability/](decisions/0118-provisioning-survivability/)

Issue #62's provisioning item and the cross-cutting distribution item. One finding reframed it: the
issue's root cause — `after_create = git clone --depth 1` with no `--recurse-submodules` — is a
configuration **the current specification has already moved away from**. Section 9.3 makes repository
population "first-class Symphony behavior … not an implementation-defined hook concern", and Section
16.5 dispatches the engine's `provision`, so clone depth and submodule recursion are the engine's
(`VCSX-SPEC.md` Section 9.1 `ensure_store`), not a Symphony hook's. What Symphony owes is therefore
not a flag but a statement of **what a workspace is guaranteed to contain** when an agent starts in
it: a tool the workspace depends on MUST be usable from a workspace Symphony provisioned, with no
step the agent takes first. Stated over contents rather than mechanism, it is checkable the way a
repository author would check it — provision from scratch, run the tool — and it survives a backend
or checkout mode changing how acquisition works. The submodule answer then follows as a consequence
rather than a preference: a tool distributed as a submodule does not satisfy the guarantee, because
whether provisioning populates one is the engine's determination and not something a repository can
rely on, so a deployment needing one uses a pinned release the workspace resolves or vendors it into
the tree. Symphony owns exactly one part the engine cannot state, being the party that starts the
agent: no agent session begins against a workspace whose **working-tree derivation** has not
completed — provisioning has two halves (Section 16.5) and a repository's own tools exist only after
the second, so a current store is not a workspace an agent can be started against. Disk-full
introduces no class and no disposition: it is `repository_provisioning_failures` taking that class's
repo-scoped retry, with two additions that are the ways an implementation gets it wrong while looking
correct — a partially written store or tree MUST NOT be presented as usable (a directory that exists,
looks plausible, and is not what the next step expects), and the retry MUST NOT be converted to a
per-worker backoff, since a full filesystem is not a condition one issue's retry clears. Not an
extension: it adds no configuration and no mechanism, so there is nothing to enable and the cost test
does not arise. Steelmanned: clone depth and submodule recursion are the engine's and Symphony
restating them would duplicate a contract it defers to — right about the mechanism and wrong about
the guarantee, since the engine cannot know what a repository depends on, and stating the guarantee
while naming no flag is what keeps the deferral intact. Reconsider if the guarantee is satisfiable
only by vendoring large binaries into every repository, which would mean it is forcing a bad
distribution choice rather than describing a reachable one. Relates to 0093 and 0104. Accepted and
applied to `SPEC.md` (Sections 9.7, 16.5, 17.2, 18.1).

## 0119 — A drain was found by catching it live, which is the defect

**State:** Accepted
**Folder:** [decisions/0119-correlation-and-budget-record/](decisions/0119-correlation-and-budget-record/)

Issue #62's observability item, whose finding is its last clause: the GraphQL drain "was only found
by catching a live poll process". Everything needed to explain it afterwards was absent, so the
investigation depended on someone being present while it was still happening. The record answers
"what did this session do" and neither of the questions an after-the-fact investigation asks. **Which
run caused this one**: each retry attempt gets its own `session_id` and nothing links attempt 3 to
the attempt that produced it, so a retry sequence is a set of unrelated sessions against one issue —
the shape a retry storm and a coincidence share. **Who spent the budget**: after 0115 each session
records what its calls observed, but a shared credential (0116) means the question is answered by
comparing readings across sessions that each saw a different moment, and the aggregate that would
answer it does not exist. `origin_run_id` names the **origin** of a retry sequence rather than the
immediate predecessor, deliberately: every attempt then carries one value, so the sequence is a group
rather than a linked list, a record missing from the middle loses one member instead of severing the
tail, and "everything that came from this run" is a filter rather than a traversal. It is never null,
the first attempt being its own origin — a nullable field would invite branching on an absence naming
no condition. The cross-session aggregate is keyed by **credential scope** rather than by repository,
argued from what the forge meters: repositories sharing a credential exhaust one bucket, and a
per-repository view shows several small numbers where an operator needs one large one. Two
prohibitions are stated because both are the obvious mistake — buckets are never summed across
scopes, two credentials' remaining counts adding to a figure describing nothing; and a difference
between readings is never attributed as Symphony's consumption where the credential has other
holders, since the forge reports what the credential has left rather than what Symphony took, so a
person running a command-line tool against the same token appears as Symphony's spend. Requirement
levels split as 0115's did: the identifier is **Core**, being a value the orchestrator already holds
when it schedules a retry and a single-issue deployment still retries; the aggregate is an
**extension**, needing a store, a sink and a retention policy for a benefit that exists only where
sessions are concurrent. Steelmanned: `issue_identifier` plus timestamps already groups a retry
sequence — true for the simple case, and broken exactly where investigation matters, since an issue
that failed, retried, succeeded, then reopened and retried again yields two sequences under one
identifier separable only by inferring where the first ended, and inference is what fails at 2 a.m.
Reconsider if operators correlate across *repositories*, which nothing in the current model produces
and which would mean the identifier is scoped too narrowly. Relates to 0115 and 0116. Accepted and
applied to `SPEC.md` (Sections 13.1, 13.5, 17.6, 18.1, 18.2) and `conformance/vocabulary.json`.

## 0120 — A read that always completes still has to say which repair it needs

**State:** Accepted
**Folder:** [decisions/0120-status-forge-throttle-output/](decisions/0120-status-forge-throttle-output/)

Issue #69. `VCSX-SPEC.md` Section 4.3 defines `rate_limited` and `forge_unavailable` for "every
operation whose forge call the condition prevented" and then enumerates four operations, omitting
`status` — while Section 9.2 permits **any** forge capability to answer either reason and Section
9.1 routes `status` through `pr_state`. A throttled `status` therefore has no defined result. Both
readings available today lose something the document argues for elsewhere: `status:failed` is the
`error`-class disposition Section 4.3 rejects for a condition that clears on its own, and
`status:ok` with `pr_state_unavailable` collapses the by-repair division the registry draws between
an informed repair carrying a `resets_at` and an uninformed one carrying nothing — a distinction
`outputs.forge_budget` cannot recover, its absence being one spelling for two events. The repair is
a fourth pull-request output, `pr_state_throttled`, beside `pr_state_unavailable`,
`pr_state_unchanged` and a reported state. `status` keeps `ok`, which is the property Section 4.1
builds the operation around: a base it cannot see, a field it could not establish and a state that
has not moved are all outputs, and a forge that refused one field is not a reason to discard the
version-control answers a caller asked for. Steelmanned: widening the `(any forge)` set is smaller
and makes one rule govern all five forge-touching operations — it loses because the other four *act*
and a throttle stops them acting, where `status` reports and a throttle stops one field, so widening
converts the operation that always completes into one that sometimes does not. Reconsider if a forge
appears whose throttling is per-credential rather than per-call, making a refused `pr_state`
evidence about the next version-control operation. Relates to 0106–0112. Accepted and applied to
`VCSX-SPEC.md` (Sections 4.1, 4.3, 9.2, 13.1, 13.2) and `conformance/vcsx/vocabulary.json`.

## 0121 — A validation input with no carrier is a verdict each engine reaches on its own

**State:** Accepted
**Folder:** [decisions/0121-validation-input-carriers/](decisions/0121-validation-input-carriers/)

Issue #68. `VCSX-SPEC.md` Section 6.11 fixes validation as judged from "five inputs and no others"
and turns `set_state_unbound` on the fourth — the actions the consumer can effect — and
`template_unbound` and `transform_unbound` on the fifth, the repository units it bound. Section 8.1
enumerates the invocation surface twice and carries neither, so three tokens in the major-stable
surface have truth conditions the contract does not transmit and two engines may validate one
document differently. The cost is the one Section 6.11 already quantifies, arriving by the route it
was written to close: an engine that cannot read the input defers to first use, and first use of a
`template` body source is a `create_pr` a `ship` reaches only after it has pushed. The repair is two
consumer-supplied arguments — `effectable_actions` and `bound_units`, both defaulting empty, both
readable from the consumer configuration. Empty is the fail-closed direction Section 5.2 already
argues for the one action it treats as fatal, a `set_state` that never advances stranding the flow;
the asymmetry survives, with `create_task` and `notify` outside the set staying valid and reported.
The static set also makes `outputs.unperformed_intents` computable from what the engine holds rather
than from a report a subprocess consumer cannot return. Steelmanned: dropping the three reasons and
deferring everything to first use is a strictly smaller contract — it loses because deferring is not
smaller, it is a contract that publishes a work branch before reporting a defect the document could
have shown. Reconsider `bound_units`' shape if the set of consumer-bound units stops being two.
Relates to 0086–0090. Accepted and applied to `VCSX-SPEC.md` (Sections 5.2, 6.11, 8.1, 8.2, 13.1,
13.2) and `VCSX-CONTRACT.md` (Section 4).

## 0122 — A trigger kind nothing can raise is surface, not a feature

**State:** Accepted
**Folder:** [decisions/0122-remove-signal-triggers/](decisions/0122-remove-signal-triggers/)

Issue #70. `VCSX-SPEC.md` Section 5.1 makes signals one of three trigger kinds and six further
sections give them matching, disposition, a place in an edge's `on`, a validation reason, an
escalation nulling rule, a reference-algorithm arm and a conformance check — while Section 8.1's
entry points are the front-end sequences and the individual operations, and no argument carries a
token. A repository can write `on = "ready-for-review"`, have it validate, have it counted against
the determinism rule, and never see it fire; a policy can even be refused for a duplicate pair of
edges neither of which is reachable. Everywhere the one signal with a concrete producer is realized
it is realized outside the engine: `SPEC.md` Section 8.10 has the consumer observe
`tasks:all_closed` and invoke `ship` through `[driver]`, and Section 11.6 evaluates the milestones
as tracker transition triggers. The kind is therefore removed, and `[tasks]`, `[driver]` and
`tracker.transitions` are named for what they already are: tables that travel in `repo.policy.toml`
because the repository owns the wiring, and that the **consumer** reads, the party effecting an
action owning the matching. Sections 6.7, 6.9, 7.3 and `VCSX-CONTRACT.md` Sections 5.1, 5.4 and 8
are more surface than the issue lists, recorded rather than discovered mid-edit. A **review
finding** is recorded in the Background: the first execution re-grounded `tracker.transitions` on
the engine's typed results, which checking against `SPEC.md` Section 11.6 showed would narrow a
closed consumer vocabulary — milestone signals, five orchestrator- observed run outcomes, task
events — to the subset the engine happens to produce, `pull_request_opened` naming a broader
condition than `create_pr:created`. The mistake has this decision's own shape: signals were engine
surface with no engine producer, and the first repair made a table engine surface with no engine
matcher. Steelmanned: a signal entry point makes every existing clause true as written and buys a
real capability — it loses on what it would owe, a second entry-point shape needing its own `entry`
value, its own Section 8.6 precondition scope and its own answer for a run that matched nothing,
carried for a capability both consumers route around. Reconsider if a consumer appears that wants
the repository rather than the driver to decide what a milestone means. Relates to 0026–0032;
`SPEC.md`'s half is 0127. Accepted and applied to `VCSX-SPEC.md` (Sections 5.1, 5.3, 5.4, 6.5, 6.7,
6.9, 7.3, 8.4, 12.1, 13.1, 13.2), `VCSX-CONTRACT.md` (Sections 4, 5.1, 5.4, 8), the
`conformance/vcsx/` vocabulary and vectors, and the two conformance READMEs.

## 0123 — A termination guarantee that holds in one encoding is not a guarantee

**State:** Accepted
**Folder:** [decisions/0123-resume-carrier/](decisions/0123-resume-carrier/)

Issue #71. `VCSX-SPEC.md` Section 5.5 defines a resume as re-entering "the point that raised the
need" and requires every such re-entry to count against the flow bound, because "a resolver that
always resolves would otherwise loop there with nothing to stop it". Nothing carries either fact
across an invocation: no `outputs` key, no `escalation` field — its `op` is explicitly null in the
case the resume must re-enter — and no argument. Section 8.1 states the model that makes this fatal,
arguing for the validator round trip: "each invocation is a bounded run that exits, so there is no
engine-side cache". So the guarantee holds for an in-process embedded driver and fails for the
interactive front-end, whose resume is a re-invocation with a fresh bound at the entry point — and
Section 13.1 asserts it with no front-end qualification, while Section 8 claims the contract is the
same under either encoding and Section 5.5 claims `escalate` is the only place the front-ends
differ. The repair carries the resume: an opaque `resume_token` in `outputs` for a **resolvable**
need, supplied back as `resume`, with the bound continuing from the count it carries. Opaque by
choice rather than necessity — the value is the engine's own, and publishing the executor's
traversal position would owe a stable spelling for every graph shape a policy can express. Holds get
no token, which makes Section 8.4's prohibition readable off the envelope. The token carries the
point and the count and **not** what a position established, which is what keeps Section 5.5's
re-read guarantee intact. Steelmanned: scoping the guarantee to the in-process front-end is the
honest minimal move — it loses because Section 5.6's bound is written as unconditional and scoping
it leaves the interactive front-end with a resolver loop nothing stops. Bounding the resolver is
orthogonal rather than alternative and is the reconsideration trigger: revisit when an engine's wait
on a resolver is shown to hang an invocation. Relates to 0059 and 0060. Accepted and applied to
`VCSX-SPEC.md` (Sections 5.5, 5.6, 8.1, 8.2, 8.4, 8.6, 13.1, 13.2, 13.3), `VCSX-CONTRACT.md`
(Section 5.6) and `conformance/vcsx/vocabulary.json`.

## 0124 — One token for two resources is a conditional read against the wrong thing

**State:** Accepted
**Folder:** [decisions/0124-per-resource-validators/](decisions/0124-per-resource-validators/)

Issue #72. `VCSX-SPEC.md` Section 9.2 defines two capabilities that each take and issue a validator
— `pr_state` over the pull request and `checks_state` over its required-check aggregate — and
Section 8.1 defines one `pr_state_validator`, presented to both. The two resources move
independently, so a backend handed the other's token satisfies Section 9.2's "MUST NOT answer
`unchanged` where it presented no validator" to the letter while answering about the wrong resource:
harmless on a forge with per-resource entity tags, and on one deriving both from a single timestamp
an `unchanged` for a resource that did move, which Section 4.1 reports as `pr_state_unchanged` and a
caller reads as current. The saving is also absent where it was wanted — `checks_state`'s validator
has no `outputs` key, so it carries forward inside one `await_checks` and not across the
park-and-resume cycle `SPEC.md` Section 9.10 actually runs. Section 9.1's rule for which reads carry
a validator is derived from `pr_state`'s three readers and settles `pr_state` completely, leaving
`checks_state` covered only by the clause that hands it the wrong token. The repair is two arguments
and two returned values, each named for its resource, with the engine carrying the obligation not to
present one issued for the other — the engine being the party that knows which resource issued a
token and the backend holding an opaque value it cannot check. Steelmanned: one bag keyed by
resource is a single argument and makes a third read a key — it loses because the engine would parse
a structure to route its parts, which is the mixing Sections 9.1 and 9.2 are separate to prevent,
and because a bag missing a key and a bag not supplied are two spellings of one condition.
Reconsider the shape if a third conditional read is added. Relates to 0106–0112. Accepted and
applied to `VCSX-SPEC.md` (Sections 8.1, 8.2, 9.1, 9.2, 13.1, 13.2, 13.3).

## 0125 — A gate that stopped existing should not read as a gate that passed

**State:** Accepted
**Folder:** [decisions/0125-await-checks-no-checks/](decisions/0125-await-checks-no-checks/)

Issue #73. `VCSX-SPEC.md` Section 4.1 bounds `await_checks` by four terminal conditions and Section
9.2's `checks_state` has a fifth determinate answer — "none where the forge reports no required
checks for it" — that no reason covers. Section 9's catch-all does not reach it, that rule governing
a value a capability could not determine and this being the absent case the same entry treats as
determinate on purpose: "a pull request with no checks is mergeable and one whose checks could not
be read is not". The reachable paths are the two that do not run `merge` first — the bare
`await_checks` entry point, and Section 7.2's `land --await`, which for such a repository ends on an
undefined result instead of merging, the operation composed to make awaiting cheap defeating the
merge it was composed with. Read literally the operation burns a supplied bound and reports
`still_pending` for a pull request that was mergeable from the first read. The repair is
`await_checks:no_checks`, class `done` — the benign no-op Section 4.2's definition already covers,
so the flow continues and a `land --await` merges. A reason of its own rather than `ok` because a
shared token would leave a consumer unable to see a merge gate stop existing: a required check
removed from branch protection turns every subsequent merge into an unchecked one, and nothing in
the record would show the day it changed. Steelmanned: folding into `ok` adds no token and the
dispositions agree — it loses because the token is free where they agree and unrecoverable where a
deployment later wants to alert. `needs_caller` is rejected because "a repository must have required
checks" is a Way of Working, which Section 1.1 keeps out of the engine. Reconsider if `checks_state`
gains a way to distinguish a pull request with no checks from a forge whose check interface is not
configured. Relates to 0106–0112. Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.2,
13.1), `VCSX-CONTRACT.md` (Section 6), `SPEC.md` (Sections 6.4, 9.10, 17.4, 18.1) and
`conformance/vcsx/vocabulary.json`.

## 0126 — A section cannot supply the value that selects it

**State:** Accepted
**Folder:** [decisions/0126-branch-section-selector/](decisions/0126-branch-section-selector/)

Issue #74. `VCSX-SPEC.md` Section 6.10 selects a `[[branch]]` section by the resolved base branch
and admits every top-level key inside a section — including `[base]`, which resolves that branch,
and `[scope]`, whose `branch_pattern` fixes the work-branch name a `by_prefix` resolution reads. The
selector therefore depends on values the selected section may change, directly or one step longer
through the work branch, and nothing refuses it: `duplicate_branch_section` and `base_unresolvable`
name neither, Section 6.10's "exactly one section applies" is a property of the prefix comparison
rather than of the fixpoint, and Section 6.4 describes resolution without reference to `[[branch]]`
at all. Two conforming engines dispatch against different branches from one document, which is what
Section 6.10 closes by claiming longest-prefix-wins avoids. This is the recurrence of the defect
issue #51 and decision 0101 repaired — a value named inside a scope selecting the scope it is read
from — found in the construct that carves the document into scopes, the first repair having been
stated over the document rather than over the general form. The repair refuses a section carrying
`[base]` or `[scope]`, with `branch_section_selector_key`: total, checkable from the document alone,
and the posture Sections 5.4 and 6.11 take wherever two things could both apply. What it costs is
narrow and stated — a release track cannot take its own base or branch pattern from a section, which
is expressed at the top level with `resolve = "by_prefix"`, and every hook, edge, message and task
key is untouched. Steelmanned: an explicit two-phase resolution gives up nothing and refuses only
the documents that are actually circular — it loses because validity stops being answerable by
looking at the document, and a two-pass rule is one an implementation can get subtly wrong where a
one-pass rule cannot. Reconsider if a matcher is added that does not depend on the resolved base.
Relates to 0101. Accepted and applied to `VCSX-SPEC.md` (Sections 6.4, 6.10, 6.11, 13.1, 13.2),
`VCSX-CONTRACT.md` (Section 4) and `conformance/vcsx/vocabulary.json`.

## 0127 — The section whose job is the vocabulary is the one where a missing member is the failure

**State:** Accepted
**Folder:** [decisions/0127-spec-trigger-vocabulary/](decisions/0127-spec-trigger-vocabulary/)

Issue #75. `SPEC.md` Section 9.12 opens by fixing its job — naming the machine's vocabulary and
deferring the schema — and then names a vocabulary with members missing: five operations where the
engine defines eleven, and a trigger list carrying task-state events while its own unmatched-policy
bullet three lines below names agent milestones too. Section 9.10 four pages earlier instructs a
repository to bind `await_checks:*` "as it binds `merge:*`", so a reader following the
cross-reference lands on a list that does not contain what they were sent to find. Two omissions are
correct and must survive: `provision` and `load_policy` raise no `<op>:<reason>` trigger, the edges
that would route them being in the document they exist to obtain — which is why the repair is nine
names and a stated reason for the two exclusions, rather than eleven. The signal half is settled by
0122's removal rather than by reconciling the two bullets, and the milestone tokens are pointed at
Section 11.6, where they are evaluated. Steelmanned: replacing the enumeration with a
cross-reference cannot drift — it loses because naming the vocabulary is what this section exists to
do, Sections 9.10, 11.6 and 8.10 being unreadable without it, and because the two exclusions are
Symphony-visible facts a bare reference would hide. Reconsider if the engine's operation set starts
changing between releases. Depends on 0122. Accepted and applied to `SPEC.md` (Sections 8.10, 9.12,
11.6, 17.4, 18.1) and `conformance/vocabulary.json`.

## 0128 — A table that is complete against itself is where a missing obligation hides

**State:** Accepted
**Folder:** [decisions/0128-conformance-template-rows/](decisions/0128-conformance-template-rows/)

Issue #67, reported by a downstream implementation while re-pinning. Decisions 0106, 0107 and 0109
each added an `Implementation-defined` answer to `VCSX-SPEC.md` Section 13.3 and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 gained a row for none — verified against the
file, whose table carries sixteen rows and none of the three, while every other obligation on that
bullet list has one. The two documents have different readers, which is what makes the gap silent:
Section 13.3 is prose an implementer reads once, and the template's table is what a **generator**
parses, so an engine implementing conditional reads, the budget snapshot and the network bound
publishes a Statement silent about all three while every check designed to catch that silence
reports green — the table being complete against itself. Treating this as bookkeeping is wrong on
two counts: the conditional-read row carries a condition no other per-backend row does, and after
0123 and 0124 the same bullet list carries two more answers, one of which is that very row now
covering two validators rather than one. Five rows are added and a conditional row states its
condition in the resolution column, `not supported` reading correctly and a new column being a
schema change to a table other implementations already parse. The recurrence is the more useful
finding: three decisions each edited a normative list and not the artifact mirroring it, because
`CLAUDE.md`'s cross-cutting sync list is `SPEC.md`'s alone and names neither `VCSX-SPEC.md` Section
13.3 nor either template — so that list is extended here, the alternative being to fix the rows and
leave the mechanism that dropped them. Steelmanned: generating the template from Section 13.3 cannot
regress — it loses on ownership, the template being a RECOMMENDED shape downstream generators
already consume, and it is the reconsideration trigger should a fourth decision land an obligation
without its row. Repairs the release discipline of 0106, 0107 and 0109 rather than their content.
Accepted and applied to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 3), `VCSX-SPEC.md`
(Section 13.3) and `CLAUDE.md`.

## 0129 — A matching axis the contract cannot transmit

**State:** Accepted
**Folder:** [decisions/0129-remove-from-context/](decisions/0129-remove-from-context/)

Issue #77, which PR #76 predicted in its own "Follow-up this exposed and did not take". `VCSX-SPEC.md`
Section 5.4 keys the policy graph on `(from-context, trigger)`, Section 6.5 lets an edge carry an
OPTIONAL `from`, Section 12.1's `match_edge` takes one as a parameter, Section 6.11 refuses a
`duplicate_edge` on the composite key and judges `position_cycle` over every context, and Sections
13.1 and 13.2 require the scoping be tested and implemented — while Section 8.1 carries no argument
supplying one, in either of the two lists it enumerates. Nothing here is strictly false: Section 5.4's
*"where the engine models them … absent such a model the key is the trigger alone"* is a real hedge,
and an engine modelling no from-context is conforming. That is the defect. Two conforming engines
given one `repo.policy.toml` produce different operation flows — one where a `from`-scoped edge fires
and one where it is dead text — and a repository author cannot tell which they have, the difference
being a capability the contract never made declarable; it is the property Section 5.4's own
unscoped-edge bullet claims to guarantee, stated over a value the specification does not transmit. The
sole model Section 5.4 named as the engine's — Section 6.7's transition graph, which Section 6.5 still
cross-references for `from`'s meaning — is read by the consumer and not matched by the executor as
that section now reads. The measurement that decided it: every `from`-carrying policy edge in the
conformance corpus, all seven across two files, uses `do: "set_state"`, the consumer-effected action
whose own matching table is still keyed `(from, on)` for the consumer to walk, and `SPEC.md` writes no
scoped edge at all — so the capability at stake is scoping a **non-`set_state`** action by workflow
state, which nothing in the repository does. The executor now matches on the trigger alone; a
leftover `from` is ignored rather than refused under Section 6.1's unknown-key rule, the precedent
0100 set for an edge's `context`, so two edges differing only by `from` collide as a plain
`duplicate_edge`. Steelmanned: **carrying** it is the move 0121 made for `effectable_actions` and
`bound_units`, makes every clause true as written, leaves 0067 standing and preserves a promised
capability — it loses on the argument's shape (an opaque scope token the engine would *match* on
rather than hand to a plugin) and on re-opening at the argument level what is settled at the table
level, the party that effects the action owning the matching, bought for a capability with no
demonstrated user. **Neutering** it keeps a surface that validates and never fires, which is what 0122
removed a trigger kind over; the half worth keeping, the ignored-key rule, is kept. Reconsider if a
repository or the `vcsx-policy` engine wants a non-`set_state` action scoped by workflow state.
Supersedes 0067, whose motivating scenario — a repository running a transition graph — is the one 0122
moved out of the executor. A change to the major-stable surface (Section 8.5), landing in the next
`MAJOR`. Confirmed with the user through decision sheet `vcsx-from-context` (`13ce1d6b`). Accepted and
applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 6.11, 8.5, 12.1, 13.1, 13.2),
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 2, which also carried a stale "no-op on an unmatched
signal" 0122 left behind), and the conformance corpus.

## 0130 — The corpus names what an algorithm takes; the contract names what a caller sends

**State:** Accepted
**Folder:** [decisions/0130-corpus-argument-names/](decisions/0130-corpus-argument-names/)

Found by the sweep 0129 authorised, and its subject is the mechanism rather than any one name:
`conformance/vcsx/vectors/*.json` was written from what the Section 12 reference algorithms *take*,
`VCSX-SPEC.md` Section 8.1 was written from what a caller *sends*, and nothing reconciles the two
lists. `policy-validation.json` spells Section 8.1's `effectable_actions` as `consumer_capabilities`
in all 38 vectors and in the two notes that gloss it — the same three actions, the same semantics —
so the corpus violates Section 8.1's own rule that *argument names for shared concepts MUST match
this specification*, and a runner executing it against a real engine invents a channel by that name.
Decision 0121 gave the concept its argument name and renamed `bound_units` alongside it, but left
this one on the pre-0121 spelling. `base-resolution.json`'s `supplied_base` is the milder instance,
mirroring Section 12.4's `resolve_base` local rather than Section 8.1's `base_branch` in four vectors
whose own notes already call it "the invocation's". Both are renamed to Section 8.1's spelling: the
corpus is a derived view (`conformance/vcsx/README.md`, "`VCSX-SPEC.md` governs. This file is
derived."), and a derived view that renames what it derives is the drift the registry exists to
prevent. Section 8.1 is already correct and is not edited; the specification needed one repair rather
than none, and it is the more interesting half of the finding — `resolve_base` (Section 12.4) reads
`supplied_base` as a **free name its signature never binds**, glossed in a comment as "the
invocation's, else the consumer configuration's", which under Section 8.1 is `base_branch`. So the
corpus was not mirroring an algorithm's local but an algorithm's gap, and the signature now carries
the parameter it reads. This is the third instance of the pattern:
#68's `consumer_capabilities` for an input the contract did not carry, #77's `from_context` for
another, and now a field whose input the contract does carry under a different name — the first two
were missing arguments and this one is a missing *reconciliation*, which is why it needs its own
decision rather than a third repair. The standing check is a README rule rather than tooling: a
`given` field naming an invocation input MUST use Section 8.1's spelling, stated where a vector
author reads it, the way `CLAUDE.md`'s cross-cutting rule fixed the template misses 0128 found.
Steelmanned: **leaving the algorithm's own parameter names** is defensible for `supplied_base`, which
is genuinely `resolve_base`'s local rather than an invocation argument — it loses because the file's
own notes describe it as the invocation's, so the vector already claims to model the caller's input
and only the spelling disagrees, and because a rule with an exception a reader must judge is the rule
that produced this. Reconsider if a vector file legitimately needs to model an algorithm-internal
value the invocation contract has no name for; the answer then is a note saying so, not a second
spelling. Records one finding it deliberately does not repair: Section 12.4 models the base's
three-source precedence (Section 8.1) only under `target_branch`, its default-mode path reading
`base_config.branch` alone, so after this rename it takes a `base_branch` parameter that path never
reads — a defect in the reference algorithm rather than in a name, made more visible here and left
assignable. Depends on 0121; relates to 0129 and 0128. Accepted and applied to
`conformance/vcsx/vectors/policy-validation.json`, `conformance/vcsx/vectors/base-resolution.json`,
`conformance/vcsx/README.md` and `VCSX-SPEC.md` (Section 12.4).

## 0131 — A value set closed in prose, and the field that points at it

**State:** Accepted
**Folder:** [decisions/0131-condition-vocabulary/](decisions/0131-condition-vocabulary/)

Reported as issue #78 by an implementation building the slice for decisions 0107–0110.
`VCSX-SPEC.md` Section 8.2 fixes `outputs.forge_unavailable_condition` to `server_error`,
`bound_elapsed` or `transport_failure`, and `conformance/vcsx/vocabulary.json` carried the three only
inside that output key's English `meaning`, while their sibling set — the three ways a unit gives the
engine no usable answer — has had a group (`hook_conditions`) all along. The consequence is asymmetric
failure on one upstream event: a renamed hook condition breaks a generated type at build, a renamed
forge condition diverges in silence, and the mechanism built to catch exactly that reports green. The
reporter's own workaround is the measurement — its decision 0011 R63 parses the three backticked
tokens **out of the sentence** into a generated constant, an implementation preferring to parse
English over accepting the silent case. Published under decision 0103's reader test, with both
readers named (Section 13.1's network-bound row asserts `bound_elapsed` by name; the fault-injection
obligation in `conformance/vcsx/README.md` makes `forge_unavailable_condition` an assertion an
implementation's harness owes), though the argument that carries it is symmetry: Section 8.2 calls
the two sets "the same arrangement … and for the same reason", and only one was published. The file
was swept rather than the one report answered — every `meaning` and `note` scanned for a value set
closed in prose and spelled nowhere as data, five hits and exactly one unpublished — so this is the
**last** instance of its shape, and the instrument is in `Background.md` to be re-run. `bound_elapsed`
is knowingly carried in both groups, on 0103's Option E reasoning and on Section 9's own "reused
deliberately", with the sharing recorded in each note. The report's other half was found by asking
what a generator can do with the groups that already exist: `unfinished_hooks` and `unanswered_gates`
say "`condition` is a `hook_conditions` token" *in prose* over a flat-string `fields` array, so the
same defect sat one layer up on keys already thought fixed — `fields` is promoted to objects carrying
`values_from`, and `fields` itself, previously undocumented, is now described in the README. One
candidate link was **refused by its own verification**: `unanswered_gates.position` →
`lifecycle_positions` fails because Section 5.1 admits "any engine-defined `before:<op>`" and Section
4.1 lets an engine add operations and positions, so a generator told to close that enum would reject
a conforming engine's own gate — this decision's defect pointed the other way, a machine-readable
claim about closedness that is wrong. `unperformed_intents.action` is left unlinked and the reason
recorded: its space is the consumer-effected *subset* of `actions`, and a subset predicate is a
property `VCSX-SPEC.md` does not fix, which is the registry's own trigger for moving a concept into
the specification instead of letting the registry lead. Steelmanned: **publishing nothing further**,
on the ground that the values are already in the prose an implementer reads — it loses to the
generator, which is the reader the registry exists for and the one that cannot read prose. Section
8.2 gains the one sentence a REQUIRED spelling rests on, in Section 6.6's own words, because the
bullet's existing sentence claims *cross-key* uniformity where a shared generated type rests on
*cross-engine* portability; and, a consequence not on the sheet, Section 13.1's transient-forge row
now names the three, the new sentence being otherwise unobservable — the same move 0103 recorded
under the same heading. `schema_version` goes `1` → `2`: adding a group is additive as prior
additions were, but changing the shape of an existing field is this file's first non-additive change.
Adds no `Implementation-defined` and no "MUST document" clause, so `CLAUDE.md`'s template-row rule is
checked and not triggered — stated rather than inferred. Records one finding it does not repair:
`hook_conditions`' first `spec_ref` cites a stale section title, `Section 6.6 "[hooks]"` for a
heading that reads `[hooks.engine]`. Depends on 0103 and 0051; relates to 0107–0110 and 0128. Accepted
and applied to `VCSX-SPEC.md` (Sections 8.2, 13.1), `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/README.md`.


## 0132 — Nine derived artifacts, and the enumerations they drifted from

**State:** Accepted
**Folder:** [decisions/0132-derived-artifact-drift/](decisions/0132-derived-artifact-drift/)

Found by a review pass run when the issue queue emptied, and filed as issues #83, #84 and #85. Every
finding has one shape: a specification sentence enumerates something, a second artifact restates
that enumeration, the two disagree, and nothing notices because each artifact is complete against
itself. The shape is not new — 0128 exists because three decisions in a row added an obligation and
no template row, 0103 counted four bullets that went stale "twice inside the decisions repairing
it", and 0131 swept a file rather than answer its one report — so this decision repairs the
instances
**and** adds `scripts/validate_spec_consistency.py`, which is the part that is not another instance
of the same manual sweep. Section 17's registry enumeration named ten token sets where
`conformance/vocabulary.json` publishes thirteen; the direction of repair is settled by the
artifacts rather than by the derived-view rule, since all three unnamed groups are in
`conformance/README.md`'s coverage table and `runtime_state_fields` is named there as the group **a
Conformance Statement author reads for its recovery-class table** — so the prose list is what fell
behind, and the rule that would have deleted a documented group allocates authority rather than
direction. Three groups are added for sets Section 19 makes an implementation spell and no group
carried — `layer_profiles`, `validation_profiles`, `deployment_topologies` — the reader being the
one 0103's test names outright, "a Conformance Statement author filling a table", and the failure
being 0131's on a worse field: an implementation hand-writes the string that says what it claims
conformance to, and a rename diverges silently in the one field a consumer reads to learn what is
being asserted. The **layer** names (`Broker Core`, `VCS Engine`, `Autonomous Daemon`) were checked
against the same test and **declined** — Section 19 records the profile, not the layer, so no reader
outside an implementation's own source spells one; this is 0131's `unanswered_gates.position`
refusal run again. Seven obligations gained rows in the matching Conformance Statement template, two
of them provable against the templates' own closing sentence that each "enumerates each obligation
above as a row" — the composed environment set (Section 9.6) and the forge pull-request-search bound
(`VCSX-SPEC.md` Section 9.2) — and five missing at both layers, so Section 19 and Section 13.3
gained the clauses above their new rows. What went unanswered was not incidental: Section 15.4's
first obligation is the trust root of the host-side hook category, and a Statement that never asks
it cannot distinguish a protected policy branch from an unprotected one. `hooks.after_create` and
its three siblings, plus `hooks.timeout_ms` in Section 9.4 and in Section 18's checklist, are
prefixed to the `hooks.workspace` namespace Section 5.3.4 fixes and gives a reason for — the
collision being live, since `hooks.engine.<name>` is a sibling whose entries are tables where these
are scalars. Two citations are retargeted: Section 9.7's to `VCSX-SPEC.md` Sections 6.4 and 8.1,
from a `VCSX-CONTRACT.md` Section 15.4 that does not exist in a document where `policy_source` never
appears. `parent` and `tracker_link` become tokens in `VCSX-CONTRACT.md` Section 8 and
`VCSX-SPEC.md`, the registry having published two spellings **no document backed** — worse than a
disagreement, which the derived-view rule resolves, because there was nothing to disagree with and
the check built to catch divergence could report neither red nor green. **The checker found the
eighth and ninth defects before it was finished**: `SPEC.md` Section 5 cites `VCSX-CONTRACT.md`
Section 3.4, which that document has no subsection for, and Section 14.3's requirement that every
`Ephemeral` field's reset consequence be documented had nowhere in the template to be recorded — the
latter surfacing in the *warning* tier, the case a zero-row check cannot see and a reviewer's eye
slides over. That is the decision's measurement: two of nine instances were invisible to a careful
person reading for exactly this class, and both fell out of a check in under an hour. Steelmanned:
**three decisions grouped by artifact and no tooling**, the repository's established rhythm — it
loses
because three groupings record three symptoms and no disease, and the disease has now been diagnosed
four times by four people reading. The checker's two limits are written into its docstring rather
than left to be discovered, and its warning tier is kept rather than silenced, since dropping it for
noise would have left the ninth defect open. Records three findings it does not repair: Section 9.7
claims a parallel obligation Section 9.8 does not carry, seven registry groups carry no
`requirement_level` though the README says to read it first, and 0131's stale `hook_conditions`
`spec_ref` is still open. Depends on 0103, 0051 and 0128; relates to 0131 and 0002. Accepted and
applied to `SPEC.md` (Sections 5, 9.4, 9.7, 17, 18.1.2, 19), `VCSX-SPEC.md` (Sections 7.3, 13.3),
`VCSX-CONTRACT.md` (Section 8), both Conformance Statement templates, `conformance/vocabulary.json`,
`conformance/README.md`, and `scripts/validate_spec_consistency.py`.

## 0133 — A token that was the whole class, and a bound that was the only bound

**State:** Accepted
**Folder:** [decisions/0133-await-class-and-authorization/](decisions/0133-await-class-and-authorization/)

Issues #81 and #82, the whole open queue, both against `await_checks` and both the same defect twice:
an enumeration that was correct when it had one member, and a sentence reasoning over it that was not
revisited when a second member arrived. **#82** is document against document. Section 7.2 ends an
awaiting `land` on any await result "not `ok`"; Section 13.1 requires that same `land` to **merge**
when the await answered `no_checks`; Section 4.3 says of the pair that both are class `done` and
"both continue the flow"; `VCSX-CONTRACT.md` says the composition "introduces no sequencing of its
own". Of four artifacts carrying the behaviour, exactly one drifted — decision 0125 minted the second
`done` reason and never revisited the one sentence it had just falsified. The cost inverts 0125's own
argument: that decision split `no_checks` off `ok` so a merge gate that stops existing is *visible*,
and Section 7.2 unrepaired makes the same change *breaking* — the day branch protection loses its
last required check is the day every awaiting `land` parks. The repair states Section 7.2 over the
**class**, as the disposition Section 5.4 already gives every operation result, which also makes the
paragraph's own "introduces no sequencing rule of its own" claim true where a token-specific stop had
made it false. A separate policy-override clause was **declined**: Section 5.4's wording is already
conditional — "for `done` **with no edge**, continue" — so a repository binding
`await_checks:no_checks` still gets the stop 0125 promised, and restating it would state one rule
twice. Section 13.1's `land --await` sentence is left **verbatim**, being correct as written and the
observable assertion a test checks rather than a restatement of the rule it tests. Section 12.3's
`land` pseudocode gains the await branch it never had, in Section 12.2's existing idiom. **#81** is a
silence with a hang behind it: Section 8.1 says which await parameters **end** a wait and never says
which one authorizes a second read, and read as an authorization `await_budget_floor` alone is a loop
with no terminator against a forge publishing no budget — Forgejo publishes none, so it is the
ordinary case against one of the two backends the reporter carries, and two conforming engines
diverge into a hang and a single read from one sentence. Only `await_bound_ms` and `await_max_reads`
authorize a loop; `await_interval_ms` paces reads a bound already authorized and `await_budget_floor`
can only end one early; an invocation naming either of the latter and neither of the former is
**refused** before the policy runs as `await_bound_missing`, a new precondition reason. The silent
single read — the reporter's own behaviour and the minimal answer — loses because an invocation
naming a floor is asking for a bounded wait, and answering with one read that looks like a wait that
ran answers a question nobody asked; the accepted cost is that "read once, but stop if the bucket is
low" now needs `await_max_reads = 1` beside the floor. A bound and a floor reached on the same read
report **`budget_floor`**, the order falling out of Section 8.1's own "the snapshot **each read**
observes": the floor judges the read just made, the allowance decides whether to read again. A floor
the observed snapshot cannot answer — no snapshot, or no bucket of that name — **fires**, ending the
wait with `budget_floor`, which is the **opposite** of what #81 proposed and of what was recommended:
an engine that cannot establish there is room does not keep spending, and the behaviour stops
depending on which forge is underneath. The cost is stated rather than argued away — against Forgejo
every floor-carrying invocation reads once and Symphony parks on that reason — and is bounded by the
floor being OPTIONAL with `vcs.await_budget_floor` defaulting unset, so a deployment opts in. The
declined reading, that an unanswerable comparison is no comparison rather than a failed one, is
recorded in its own terms with the trigger that reopens it. Section 4.1's five terminal conditions are
re-framed to the invocation's **read allowance** ending, an invocation authorizing no loop having an
allowance of one read — which is what makes the enumeration true of a no-parameter invocation whose
checks are pending, a case that previously matched none of the five. Records a finding the repair
turned up: Section 8.6's `provision` sentence "What remains is…" was **already short by two**, omitting
`base_branch_not_permitted` and `resume_unusable`, both judged wherever their argument is supplied and
the former asserted so in the test matrix — adding `await_bound_missing` silently would have been the
third omission in a list already missing two, so the sentence is repaired. The fifth instance of
0132's enumeration-drift class, and the second found inside the decision repairing one;
`validate_spec_consistency.py` could not have caught it, comparing registries against prose where this
is prose against prose, so **check 5** is added for the await enumeration and the general case is
recorded as still open. Also recorded and not repaired: `await_max_reads` has no stated floor, so `0`
is a bound that authorizes a loop and permits no read. Reconsider on a fifth await parameter (0112's
own trigger), a forge that publishes a budget only sometimes, a consumer for which the two-parameter
spelling is a burden rather than a nuisance, or a budget snapshot that distinguishes a forge with no
budget interface from one reporting an empty budget. Depends on 0112 and 0125 as support; relates to
0132 and 0002. Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 7.2, 8.1, 8.6, 12.3, 13.1,
13.2), `VCSX-CONTRACT.md` (Section 6), `conformance/vcsx/vocabulary.json`, and
`scripts/validate_spec_consistency.py`.

## 0134 — A vocabulary two documents closed and one left the engine to extend

**State:** Accepted
**Folder:** [decisions/0134-spec-owned-trigger-vocabulary/](decisions/0134-spec-owned-trigger-vocabulary/)

No open issues to work from — all 54 closed, #81 and #82 having closed when PR #87 landed — so a
fresh consistency review was run against what the mechanical checks structurally cannot see: one
document against another, and prose against prose. Three defects and one derived-artifact omission,
filed as #88, #89 and #90. The **first is the one that matters**: the trigger vocabulary a
`repo.policy.toml` is keyed on was closed in `VCSX-CONTRACT.md` (Section 5.1's four positions,
Section 7's "the fixed points") and in `SPEC.md`, and open in `VCSX-SPEC.md`, which said an engine
"MAY define additional operations and their `before:<op>` positions", wrote "(and any engine-defined
`before:<op>`)" into the definition of a trigger, and judged `position_cycle` over "the positions
the engine defines". That is observable rather than academic, because Section 6.11 refuses an
unrecognized trigger with `unknown_trigger`: a policy keyed on an engine-defined position, or on an
engine-defined operation's result, **validates on one conforming engine and is refused by another**,
against `VCSX-CONTRACT.md` Section 2's promise that conformance is to the contract and not to a
binary. Nothing disclosed it either — Section 13.3 required only the *backend capabilities* an added
operation needs, never the operation's own name or its position — which made it the sole gap in an
otherwise complete pattern, added reason, configuration and precondition tokens each carrying a
MUST-document obligation *and* a template row. **The maximal reading wins**: the operation set and
the position set become **spec-owned and versioned**, extensible by a MINOR release of Section 8.5
and never by an individual engine, because the minimal repair — document the extension, row it in
the template — documents a divergence rather than removing it, and `unknown_trigger` is a refusal to
run rather than something a consumer routes around. That a MINOR may add a *position* where it may
not add a trigger **kind** or a key component is Section 8.5's own second-bullet argument run
backwards: a policy keyed on a position the running version does not define was already refused, so
there is no previously-firing edge for an addition to move, while a *removal* leaves an edge that
validated and never fires and stays MAJOR. Both halves close rather than the operation set alone,
since closing one would leave a consumer to know which half of its policy is portable. **#89**:
`VCSX-CONTRACT.md` Section 6 opened "Named operations **include**:" and listed eight where Section
4.1 defines eleven — `status`, `diff` and `pull` missing from the document whose Section 1 claims to
fix the operation names and whose Sections 1 and 12 require them identical with `SPEC.md`, which
names all eleven. `status` and `pull` were each reworked by #69 and #8 without the contract's list
moving; the word *include* is what let it happen quietly, and the contract's only occurrence of the
token `status` was the task model's field, so grepping for it found an unrelated concept. The three
are added at contract altitude and the list is closed. **#90**: Section 4.3's "none of the four" was
short by one, `await_checks` being gated at no fixed position and `provision` carrying none at all,
while the registry beside the sentence was already right — the third instance of this shape in as
many decisions and the fifth overall. Replaced by **the invariant** — an operation with no
`before:<op>` position carries neither `blocked` nor `hook_unanswered` — which covers both without
naming either and cannot drift; Section 4.1's own "`integrate` and `pull`" list is repaired the same
way. **The fourth finding**, noted inside #89: `conformance/vcsx/vocabulary.json` published ten
operations and omitted `load_policy`, invisible to every check because check 4 walks registry→prose
and never the reverse. Repaired, and the class made machine-detectable by **check 6**, deliberately
narrow — a table of two closed groups, `operations` and `lifecycle_positions` — because closedness
is a property of the prose no general rule reads off it, so a group the table does not name stays
unchecked in that direction. Adding `load_policy` to the registry needed a `read_only` answer the
marker had never given, so Section 4.1 now marks the operation **Read-only**, which is what the
registry derives from rather than inventing; the position set closing likewise made
`unanswered_gates`' `position` a `values_from` link the registry's own discipline had previously
forbidden. Two of the three standing validator warnings are fixed **in the checker rather than in
the documents**, both being correct as written: Section 14.2's obligation belongs to the extension
that defines it, so check 2 **re-homes** an obligation declared under an "OPTIONAL extension,
Section N.M" bullet instead of loosening `covers()`, and Section 6.6's fourth obligation is a TOML
example restating the prose beside it, so fenced regions are excluded. Records three things
unrepaired: Section 4.3's "every operation has at least one `done` and one `error` reason" does not
hold for `load_policy`, whose failures are configuration reasons — pre-existing, and a decision
about that operation rather than about this vocabulary; the registry's `reasons` note names three
forge-universal operations where Section 4.3 names four; and Section 8.4's residual
2-obligations-1-row warning, whose second obligation is the `need` vocabulary's own spec-level
stability clause, carried forward from 0132. A sweep for further counted enumerations is explicitly
**not** part of this decision, 0133 having already recorded the general case as open. `SPEC.md`
needs no change and gets none, so Sections 6.4, 17 and 18 are untouched. No token is renamed or
removed and no new `Implementation-defined` obligation is created, so no Conformance Statement row
is owed; three existing template rows are narrowed instead. Reconsider on an engine holding a real
operation the specification lacks, on a matching rule that made an unrecognized position a no-op
rather than a refusal, or on a third group wanting check 6. Relates to 0128, 0131, 0132, 0133 and
0002. Accepted and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 5.1, 6.11, 8.5, 9.1, 9.3, 13.1,
13.2, 13.3, 14), `VCSX-CONTRACT.md` (Sections 6, 7), `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`,
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`, and
`scripts/validate_spec_consistency.py`.

## 0135 — The map a template can iterate, and the order it never had

**State:** Accepted
**Folder:** [decisions/0135-map-iteration-order/](decisions/0135-map-iteration-order/)

Issue #93, the only one open, filed by the `symphony-rs` build against Section 12.2: the rendering
rules require the renderer to "Preserve nested arrays/maps (labels, blockers, metadata) so templates
can iterate", and nothing in the document fixes the order iterating one yields. `labels` and
`blocked_by` have an order because they are lists; `metadata` is a map and the `issue` object is
another, and a template may name either whole. Section 5.4 makes the rendered body the agent's whole
instruction for the run, so **one template and one issue produce two different instruction texts on
two conforming implementations** — and worse than that, on neither one reproducibly: Ruby Liquid
iterates a `Hash` in insertion order, which for a payload-decoded map is a property of the JSON
parser, and `liquid` 0.26.11 iterates a `HashMap` whose order is the randomizing hasher's, measured
by the reporter as three orders across six runs of one binary. Both are "Liquid-compatible", which
is why Section 5.4's sufficiency clause could not settle it, and `render_prompt` is a corpus
function whose `iterate-labels` vector already established iteration as in-contract — so the
observable output of a checked function was unspecified for an input the same corpus says must work.
**The order is fixed ascending by key, compared by Unicode code point**, with a `Note:` recording
that the result is independent of the host's locale, applies no Unicode normalization form, and is
reproduced by comparing the keys' UTF-8 bytes — the clause that makes the rule implementable rather
than aspirational, since an implementation whose engine hands it an unordered map can sort on the
way out. Section 12.2 also fixes **what one iteration yields** — a two-element key/value entry, key
first — because an order is only observable through a shape, and without one a vector can assert
that two runs agree but not what they render. **And it fixes the rule's reach**, which is the half
#93 did not ask for and the half that decides whether the rule is true as written: the maps a
template names by path, the `issue` object and `metadata`, and not a blocker ref's own fields. That
boundary is the engine's rather than a preference — verified in `liquid` 0.26.11 rather than taken
from the report, `StackFrame::get` materializes a variable through `ValueView::to_value()` before a
`{% for %}` sees it, so an implementation buys the order by writing `to_value()` by hand, and a
value that returns an ordered pair array is no longer an object, which `{{ b.identifier }}` after
`{% for b in issue.blocked_by %}` needs it to be. A rule over *every* map an implementation exposes
would therefore be unimplementable on a Liquid-compatible engine; the rule as written is
implementable on all of them, because path resolution walks `ObjectView::get` and materializes only
what the path ends at. One cost is recorded rather than discovered downstream: the same
materialization makes `{% assign i = issue %}` followed by a field read fail, on any implementation
buying the order that way. Two options are steelmanned and lose — **order alone**, exactly as #93
asked, which states a rule wider than any implementation can meet and leaves the next implementer to
rediscover the conflict; and **removing map iteration from the contract**, which owes no order at
all but takes away the only way a template can render adapter-owned `metadata` whose keys it cannot
name in advance, the case that field exists for. The fourth answer, `Implementation-defined` plus a
documented choice, is recorded as rejected: it documents the divergence rather than removing it
(0134's finding) and does not even buy reproducibility within one implementation. Three vectors pin
it — `iterate-metadata-map` (keys `zeta`, `mu`, `alpha` in, ascending out), `iterate-issue-object`
for the container, and `iterate-metadata-map-non-ascii`, whose three keys separate code-point order
from both an en_US and a Swedish collation and sort identically in NFC and NFD, so it tests the
comparison rather than the normalization form. No token is added, renamed or removed, and no
`Implementation-defined` or "MUST document" obligation is created, so no Conformance Statement row
is owed. Reconsider on a Liquid-compatible engine that can order an object without destroying it, on
a repository that genuinely needs to iterate a blocker's fields, or on a tracker adapter whose
metadata keys are not stable strings. Relates to 0048, 0102, 0105 and 0128. Accepted and applied to
`SPEC.md` (Sections 12.2, 17.1, 18.1.3), `conformance/vectors/prompt-rendering.json` and
`conformance/README.md`.

## 0136 — A timer fire that could not name the arming it came from

**State:** Accepted
**Folder:** [decisions/0136-retry-fire-identity/](decisions/0136-retry-fire-identity/)

Issue #95, filed by the `symphony-rs` build against phase D2 — planned rather than built, so nothing
downstream has to be unwound to adopt an answer. Section 8.4 requires retry entry creation to
"Cancel any existing retry timer for the same issue", which is what makes cancel-then-replace
in-contract rather than an implementation's invention; Section 16.7 then identifies an arriving fire
by `issue_id` alone and guards it with `if missing`. **That guard tests presence, and a replaced
entry is present** — so it catches the fire whose entry was popped and not the fire whose entry was
swapped. The reachable collision is a stall: Section 8.5 Part A terminates the worker and queues a
retry, the terminated worker's own abnormal exit reaches `on_worker_exit` and queues a second, the
second cancels the first's timer, and a fire already in flight then finds the *new* entry, pops it,
and dispatches at once. What ships broken is the backoff itself — the retry that Section 8.4 says
waits `min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)` runs immediately and its
`due_at_ms` is discarded unread, **collapsing backoff to zero on exactly the path that had just
produced two failure signals in a row**. The report's own worked example is *not* reachable and this
is recorded rather than dropped: it has reconciliation observing a stall for an issue whose worker
already exited, but `on_worker_exit` begins `state.running.remove(issue_id)` and Part A iterates
running issues only. **`RetryEntry` gains `generation`**, `schedule_retry` assigns it and arms the
timer with it, and the fire carries it back. The shape change matters as much as the field:
`on_retry_timer` becomes get-compare-remove rather than `pop`-then-test, because a comparison that
fails after the pop has already taken the entry the fire should not have touched. Two options are
steelmanned and lose. **Guarding on the due time** needs no new field, is robust to any number of
stale fires, and costs nothing to thread — a sans-io step reads no clock, so `now_ms` is already on
every input, and an earlier claim that it depends on the backoff constants is wrong and corrected in
the Background: re-arming for the remainder is correct at any delay. It loses because it decides "is
it time yet" rather than "is this the live arming", and Section 8.4's continuation delay is a fixed
`1000` ms, so two continuation schedules taken at the same instant are indistinguishable to it; it
would also owe a clock-slack value or an `Implementation-defined` row, which the generation does
not. **Treating the fire as a wakeup over a due-scan** removes identity entirely and is the shape
most real schedulers take, but it needs a dispatch order over the due set and a rule for
`available_slots` running out mid-scan — today one fire dispatches exactly one issue and requeues at
`attempt + 1` — so three due entries and one free slot would inflate two backoffs for issues that
never got a chance; its vector `entries_due(map, now_ms) -> [issue_id]` is not expressible until
that order is pinned, and all eight files in `conformance/vectors/` are one-shot pure functions.
#95's own alternative, **requiring the cancellation be observed before the entry is replaced**, is
recorded and loses for putting a liveness obligation on the host's timer facility, which a sans-io
core cannot check. One clause goes beyond the ask: **a generation value MUST NOT be reused for an
issue while the process lives.** Storing it only in the entry leaves nothing to derive the next
value from once `on_retry_timer` removes the entry, and the obvious reading restarts at 1. The reuse
turns out to be unreachable under first-in-first-out delivery — traced in the Background rather than
assumed — but the document states no ordering property for orchestrator messages and defines neither
`send` nor `event_loop`, so the guarantee would rest on a primitive it never wrote down. The counter
that satisfies the clause is itself Core-introduced state with no Section 4.1.8 field, which is
issue #96 arriving from the other direction; decision 0137's Section 14.3 widening is what admits
it, and this decision deliberately adds no field for it, since the container is one integer and
mandating one would over-specify a choice with no observable consequence.

## 0137 — A backoff kept per repository, and the state model with no repository in it

**State:** Accepted
**Folder:** [decisions/0137-repository-scoped-recovery-state/](decisions/0137-repository-scoped-recovery-state/)

Issue #96, filed alongside #95 and against the same unbuilt phase. Section 14.2 requires that where
an engine policy could not be used at all, "retry is **backed off per repository** rather than
attempted every tick"; Section 4.1.8 has eight fields and **not one is keyed by repository**; and
Section 14.3 closes its recovery-class obligation over "every field of the Orchestrator Runtime
State … and any state introduced by an OPTIONAL extension" — **exhaustive over the wrong set, since
it admits extensions and leaves Core's own additions outside**. An implementation has three ways to
comply and the document blesses none: a field Section 4.1.8 does not list, which Section 14.3's
"every field" then does not reach and `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 has no line for;
hanging it off `running` or `claimed`, both `Reconstructable` and "rebuilt from tracker state and
workspaces", from neither of which a backoff schedule is derivable — so a restart silently resumes
the per-tick hammering the clause exists to stop; or not holding it, which is not complying. What
ships broken is the Conformance Statement rather than the daemon: **the state whose restart
behaviour an operator most needs — does my failing repository come back backed off or come back
hammering — is the one a generated Statement has no row for**, complete against its own table and
silently missing the answer, which is decision 0128's failure mode arriving through the enumeration
instead of through a missed row. The drafting's claim that `repository_provisioning_failures` is
tick-local and holds nothing is **wrong**, and wrong in the direction that mattered: what needs a
home is one MUST and *two* Core MAYs — the mandatory per-repository backoff, plus a park MAY on each
of the two classes — whose shapes are not the same. Section 14.2 also SHOULDs logging "the first
failure, each backed-off retry, and recovery", and both "first" and "recovery" are predicates over
the previous tick's per-repository state, so the state has a consumer the issue never names. The
asymmetry that settles the shape: `node_provisioning_failures` carries the *identical* park MAY and
is an OPTIONAL extension, so Section 14.3 already admits its state, classes it, and gets it a
template row — the same construct blessed on one path and homeless on the other. **Both halves are
taken.** Section 4.1.8 gains `repository_backoff` (map `repository -> { due_at_ms, attempt }`,
`Ephemeral`), because the backoff is a MUST with one shape and the specification owes it a name the
way it owes one to `retry_attempts`; Section 14.3 gains a clause admitting state Core behavior
requires beyond Section 4.1.8, on the terms it already sets for an extension's, because the two
parks are `Implementation-defined` down to whether they happen at all and a mandatory `parked` flag
would force a representation for a choice an implementation may decline. **The field alone** loses
on the parks — a park that does not survive a restart quietly un-parks a repository a human decided
to stop retrying — and on leaving the class open for the next Core addition to rediscover, which is
the lesson Section 14.1 already learned and ends with. **The rule alone** is the smaller and more
general diff and loses on comparability, which is what #96 was about: "class and document whatever
you hold" makes each Statement internally complete and mutually incomparable, one reporting
`repo_backoff_until` and another `policy_retry_state` with no way to tell whether they agree.
**Reverting to a per-tick retry** is recorded as the obvious fourth answer and loses twice — against
its own clause's still-true reasoning, and because the two park MAYs survive the reversion and are
still homeless, so it pays a behavioural regression and closes nothing. The `Ephemeral` class is
argued rather than inherited: `Durable` would leave a restart unable to clear a backoff whose cause
a human has just fixed, and `Reconstructable` would be a lie, since nothing outside the process
records it.

## 0138 — The function five call sites named and no section defined

**State:** Accepted (magnitude corrected by 0144; a consequence it removed is repaired by 0145)
**Folder:** [decisions/0138-reference-algorithm-gaps/](decisions/0138-reference-algorithm-gaps/)

Reported by neither issue; found checking #95's claims against the corpus, and kept as its own
decision because the repair is not what either issue asked for and because the `symphony-rs` build
implements Section 16.7 directly at phase D2d, where every function that section calls and does not
define is a resolution that build has to invent. Section 16 defines eight functions and calls
forty-two it does not — most deliberately, since `log_debug` and `spawn_worker` are primitives and
`available_slots`, `sort_for_dispatch` and `normalize_state` are pinned by `conformance/vectors/`.
Three are gaps. **`schedule_retry` has five call sites and no body** — `dispatch_issue` once,
`on_worker_exit` twice, `on_retry_timer` twice — its only definition anywhere being Section 8.4's
two prose bullets, which is plausibly why #95's defect went unnoticed: the function whose body
decides what a fire means has no body to look at. **`terminate_running_issue` is called twice by
`reconcile_running_issues` and defined nowhere**, and it turns out to be the seam;
`reconcile_stalled_runs` is the third, and a gap this decision creates as much as inherits — see its
recorded review finding. The sharper
defect is that **`on_worker_exit` has no `if missing` guard where its sibling `on_retry_timer`,
eleven lines away, has one**, and two paths reach it with the entry already gone. Section 8.5 Part A
terminates a stalled worker and queues a retry, and that worker's own exit still arrives: if
reconciliation removed the running entry, `add_runtime_seconds_to_totals` and `next_attempt_from`
read fields off nothing; if it did not, `on_worker_exit` queues a **second** retry, which is the
double-schedule decision 0136's race needs. The document says neither, so both defects are live and
an implementation picks one by accident. Part B is worse in kind: a worker terminated *because its
issue went terminal* reaches `on_worker_exit` with an abnormal reason and unconditionally schedules
a retry for a closed issue. It self-cancels one backoff later via `find_by_id -> null ->
claimed.remove`, so the cost is a wasted timer and a held claim rather than corruption — **and the
claim is what it costs: the issue is skipped by every tick until the retry fires, up to
`agent.max_retry_backoff_ms`, while other issues' dispatch is unaffected, `available_slots` counting
running sessions rather than claims** (corrected by decision 0144; this chapter previously recorded
the cost as a concurrency slot per closure, following a Section 8.5 sentence that decision strikes —
see this decision's `Background.md`, "Logged finding"). Both
are #95's shape: a message arriving for state that has moved. **One rule fixes both**: reconciliation
that terminates a worker removes the running entry and accounts for that run's runtime at the point
of termination, and `on_worker_exit` is authoritative only for exits the orchestrator did not cause,
returning unchanged when the entry is gone — so the guard stops being defensive and becomes the
mechanism, while Part A keeps queueing its one retry and Part B keeps queueing none. The cost is
stated rather than discovered: the runtime-seconds accounting moves to `terminate_running_issue`, or
every terminated run drops out of `agent_totals`. **Guarding and stopping there** is what a reviewer
writes first and loses because it does not settle the race it hides — whether the entry is missing
still depends on what reconciliation did, so the guard converts a crash into a coin flip between one
retry and two, and a failure made quieter without being made determinate is worse than the crash,
which at least gets reported. **Suppressing by exit reason** keeps accounting in one place and loses
on trust: a worker killed hard reports what the operating system says rather than what the
orchestrator meant, and a reason-based branch still reads `running_entry` before it branches — state
the orchestrator wrote is checkable, a reason handed back across a process boundary is not.
**Defining every function Section 16 calls** loses on altitude; the test used instead — can a reader
supply the body without changing behaviour stated elsewhere — is written into the `Plan.md` with the
inventory command, so a later reader can re-run the classification rather than take it on trust. One
review finding is recorded rather than fixed quietly, and it is the sharpest thing here: **the first
draft of the repair kept Part A's retry while removing its only producer.** Stopping `on_worker_exit`
from queueing for a terminated run left the stall retry to `reconcile_stalled_runs`, which Section 16
calls and does not define — so as drafted a stalled run would have been terminated and never retried.
That is worse than the double-schedule being repaired: two retries is a wasted timer, none is a
dropped issue. `scripts/check_plan_anchors.py` reported nothing on this plan (0 findings from 4
quoted spans); the premise-and-consequence lens caught it, and the observation that a plan written in
pseudocode rather than prose is quietly under-checked by the mechanical lenses is recorded with it.

## 0139 — An obligation answered in full, and the heading that did not say so

**State:** Accepted
**Folder:** [decisions/0139-need-vocabulary-obligation-citation/](decisions/0139-need-vocabulary-obligation-citation/)

`scripts/validate_spec_consistency.py` warned for three decisions running that `VCSX-SPEC.md`
Section 8.4 has two obligations and one row in `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. Decisions
0132 and 0134 both examined it and left it: 0132 diagnosed the cause exactly — the template answers
with a whole section whose heading "carries no section citation for the validator to count" — and
0134 carried that forward with a second reason, that the obligation is "the `need` vocabulary's own
spec-level stability clause rather than a choice an engine makes", concluding "no detector is worth
writing". **The added reason is half wrong, and it is the half the disposition rested on.** Section
8.4's clause carries two obligations in one sentence: the `need` vocabulary "MUST be documented
**and** stable within a major version". Stability is spec-level exactly as 0134 says — Section 8.5
fixes it as major-stable and no engine chooses it. Documentation is not: it is an engine's
obligation, and the template already reads it that way and already discharges it, its Section 5
saying "List every `need` **this engine** can emit" and tabulating the eight registry needs plus an
`<other>` row. So the obligation was answered twice and neither answer was countable — the
documentation half by a section whose heading cites nothing, the stability half by the template's
Section 1, whose prose cites Section 8.5 rather than 8.4. **The answering heading now names the
section it answers**, which is the shape the validator's whole-subsection rule exists for and the
shape five sibling headings in the same file already use; the validator reports 0 errors and 0
warnings, against 0 and 1 at `211d515`. Three options lose. **Leaving it**, as 0132 and 0134 did,
has the real case that a standing warning is a standing marker — but a checker that always prints
one line trains a reader to skip it, and the next genuine warning arrives underneath: during
decisions 0136–0138 two new obligation miscounts appeared and had to be told from the standing one
by memory, which is a marker being remembered rather than read. **Exempting the section in the
checker** is what 0134's reasoning points at and asserts something false — that no Statement owes
anything for Section 8.4, when the `Implementation-defined` `detail` field is rowed and the needs are
tabulated — and would suppress the first obligation with the second, exemption being per section
rather than per sentence. **Splitting the sentence in `VCSX-SPEC.md`** is the most honest repair of
the underlying conflation and loses on direction: it edits a normative document to satisfy a
counting tool, where the template is the derived artifact and the right place to absorb it. One
process finding is recorded: the first draft of the plan's step quoted five sibling headings that
each embed a section citation, so `check_plan_anchors.py` read them as the plan's own attributions
and returned eleven findings that were all one artifact. A plan quoting a title that contains a
citation is unparseable to the checker and misleading to a reader; the step now describes the
convention instead of quoting it.

## 0140 — A dispatch condition no configuration and no record could supply

**State:** Accepted
**Folder:** [decisions/0140-assignee-routing-condition/](decisions/0140-assignee-routing-condition/)

Issue #100, filed by the `symphony-rs` build. Section 8.2's third eligibility bullet is two
conditions in one sentence — "routed to this worker by the configured assignee and contains every
label in `tracker.required_labels`" — and only the second is specified. **There is no configured
assignee anywhere in the document**: Section 5.3.1's `tracker` object has eight fields and none
names one, Section 6.4's cheat sheet has no row, Section 4.1.1's record has no field, and `metadata`
cannot be the channel because that section says "the orchestrator core does not interpret it". The
word occurs three times in `SPEC.md` and the only field among them is Section 4.1.9's **task**
assignee, which belongs to an OPTIONAL extension and is a different entity. Section 8.2 is `Daemon
Conformance` and nothing pins it — `should_dispatch` is called at `SPEC.md:3946` and defined nowhere
(one of decision 0138's forty-two), and `conformance/vectors/` holds nine files and no
candidate-eligibility file — so three faithful readings ship: always-true, an invented key whose
name and comparison two implementations will disagree about, or `metadata`. The reporting build
carries the condition as `Eligibility::routed_here: bool`, **supplied evidence rather than a
computed value, because nothing in the record or the config can compute it** — a bullet that looks
implemented and is not. The bullet is wrong twice: Section 8.2 is evaluated at candidate selection,
before dispatch, and a `worker` in this document is the per-issue task `dispatch_issue` spawns, so
**the subject of "this worker" does not exist yet** — it was a query-scope statement written at
record altitude. The repair specifies it parallel to `required_labels` at every step: `assignees` on
Section 4.1.1 (OPTIONAL, tracker-dependent, normalized, a list because Forgejo's is plural),
`tracker.assignee` on Section 5.3.1 with `Default: null`, the bullet split, Section 11.2's Linear
clause extended, and Section 11.7's descriptor declaring whether the adapter populates the field —
with a configured filter against an adapter that does not being a Section 6.3 preflight error, the
shape that section already carries for `tracker.transitions` and `set_state`. **The recommendation
was first the opposite and was reversed**, which is the part worth preserving: moving the routing
half adapter-side is what the reviewer argued from `project_slug` and Section 8.7, and it loses
because Section 11.2 answers the same question for the *sibling half of the same bullet* and answers
it against query scope — "Required label filtering happens after normalization so refresh can
observe label removal and stop or release existing work" — because Section 5.3's extension mechanism
admits "additional **top-level** keys" so a scope key under `tracker` is one a reader SHOULD ignore,
and because query scope would **foreclose** the continue side rather than defer it: Section 16.3
iterates `for issue in refreshed` and Section 8.5 Part B has three branches and no absent one, so an
issue that vanished from a scoped enumeration reaches none of them. One review finding is recorded
against this decision's own draft and it is the sharpest thing here: **the first design said
`assignees` is normalized as `labels` are *and* that which identifier the adapter publishes is
`Implementation-defined`**, which re-imports the hazard it was avoiding — Section 4.2's
normalization is not opt-in ("Every case-insensitive comparison in this specification is defined
over this operation"), so a case-significant opaque id gets lowercased, two principals merge, and a
configured filter matches an issue assigned to someone else with a dispatched issue as the symptom
rather than an error. The clause therefore lands on the **publication**, not the comparison —
phrased over the operation rather than over case, because Section 4.2 supplies the counterexample
itself: the mapping "is not one-to-one, so `İ` (U+0130) normalizes to `i` followed by U+0307", which
a case-worded clause does not catch. The reverse direction — one principal spelled two ways, Section
4.2 applying no Unicode normalization form — is recorded as inherited from `required_labels` rather
than introduced here, and closing it would be a decision about Section 4.2. The report's own premise
is recorded as out of scope **and false**: Section 8.7 routes issues to repositories rather than to
workers, and `running` and `claimed` are `Reconstructable` in-memory fields of one orchestrator, so
two instances share no claim and the bullet coordinated nothing. Eight conditions, one per vector,
`expect` naming the refusing condition — Section 8.2 fixes no precedence, so a two-condition vector
would pin an order the document does not state.

## 0141 — The operation no entry point named and no policy could dispatch

**State:** Accepted
**Folder:** [decisions/0141-load-policy-entry-and-pin/](decisions/0141-load-policy-entry-and-pin/)

Issue #101. Decision 0134 closed the operation set and put `load_policy` in it, which removed the
ground `VCSX-SPEC.md` Section 6.11's `unknown_operation` stood on — "an operation the engine does
not define" — and put nothing in its place. `load_policy` is the one member of the set that raises
no `<op>:<reason>` trigger and has no Section 4.3 entry, so a `[policy]` edge naming it **validates,
fires, and disposes of an outcome with a result that cannot take its place**: no edge matches it,
and it carries no proto class, so none of Section 5.4's three built-in defaults has anything to key
on and the flow carries on past a push that did not land. Three implementations are faithful and
incompatible, which is the divergence 0134 closed the set to prevent. The second finding is what
changes the answer's shape: **`load_policy` is not an entry point in the prose** — Section 8.1 names
ten operations where Section 4.1 defines eleven — so refusing the edge alone makes the operation
unreachable while Section 4.1 says a consumer holds its product. Two artifacts already disagree with
that enumeration: `VCSX-CONTRACT.md` Section 6 lists `load_policy` first, and
`conformance/vcsx/vocabulary.json`'s `entry_points` group carries thirteen tokens **while citing
Section 8.1 as its source** — a registry citing the prose it contradicts, against that corpus's own
"nothing here is invented". The decision is six-sided plus a seventh: Section 8.1 enumerates the
operation; a `run_op` naming an operation that **runs outside the action-policy machine** is refused
with a new `operation_not_dispatchable`; Section 5.1's `provision` parenthetical extends to both so
the trigger side needs no second token; Section 4.3's "every operation has at least one `done` and
one `error` reason" is scoped to what the machine can dispatch, closing 0134's own
recorded-not-repaired finding; and Section 8.6's `git_access` paragraph narrows to `integrate`,
`push` and `pull` once no edge may name `provision`. The property is stated over the bootstrap pair
rather than over the two names, and it reaches `provision` by the document's own argument — an edge
read out of the repository `provision` obtains can only fire on the refresh path, "a trigger that
sometimes exists, which Section 5.4's one-edge-per-trigger rule is written to prevent". **The
load-bearing correction came from the implementation side**: the property cannot be derived from the
reason table (that engine refuses today by reading it, and `provision` has three class-bearing
reasons), so a marker living only in prose makes every engine hardcode two names and makes the
MINOR-inheritance claim **false for exactly the engines that generate from the corpus** — a MINOR
adding a third such operation would pass their gate green. The registry therefore carries
`policy_dispatchable` beside `read_only` and `lifecycle_position`: one flag, two refusals, no second
prose list. The seventh part settles what the entry-point blessing was blocked on — Section 4.1's
"the consumer holds it and supplies it to every subsequent invocation, which therefore read no
repository", a sentence with no invocation shape, since Section 8.1 names no supply-back argument
and closes the consumer-configuration route. Supply-back is refused on trust: it would let a caller
hand the engine a document no revision ever held, in the file that declares the host-side hooks. A
**plain re-read** is coherent and is what ships, and its cost is Section 13.1's Policy-loading row —
false not everywhere but on the *unresumed continuation*, a `ship`, an edit, a fresh `land`, since
along a resumed chain the token's own policy fingerprint already refuses. A **revision pin** is what
the row literally promises and loses three times: a revision does not name the effective surface
(Section 6.1 states no location and no discovery rule for `vcsx.toml` at all, and a `[[branch]]`
section is selected by the resolved base), a second notion of "same policy" beside Section 8.1's is
issue #100's defect, and — the argument neither party made first — **a revision pin lets a caller
run a policy the repository has withdrawn**, an operator who removes a host-side hook having not
removed it for anyone holding an older pin. The **fingerprint pin** wins: OPTIONAL, default unset,
needed by no resumed invocation, refused with its own precondition reason rather than
`resume_unusable` because the repairs differ. It is reported by **every invocation that validated a
surface** rather than by `load_policy` alone — a first draft had that entry issue it, on the ground
that it "finally gives that entry point a purpose beyond inspection", which is a reason to want it
and not a reason for it: the gap the pin exists for is the unresumed continuation, and
`load_policy`-only issuance would make a consumer invoke an entry it did not need in order to obtain
a value the invocation it did make had already computed. `provision` is the one entry where the key
is absent, being "the one entry point that runs where no policy could be read", which is
`output_keys`'s own absent-where-the-condition-did-not-occur rule. The pin is an **opaque handle**,
and here that is a necessity where Section 8.1 calls the resume token's opacity "a choice": a value
form would oblige this specification to fix a canonicalization of the effective surface, over a
document Section 6.1 does not place on disk. That last gap — `vcsx.toml` has no stated location or
discovery rule — is recorded as **not** the pin's defect, since two engines never compare pins; what
it costs is that two conforming engines merge different documents from one revision, and it is
repaired with issue #110's capability decision. Section 13.1's row states the mechanism instead of
being lowered — the surface a unit of work executes is fixed when the unit of work begins, and an
invocation continuing one whose surface changed is refused rather than run under either document,
which is falsifiable where the caching phrasing was not. The cost is stated: the fingerprint refuses
where the revision pin would have proceeded, the same trade Section 8.1 already made for the resume.
`entry_points` also joins `validate_spec_consistency.py`'s closed groups, or the repair holds only
until the next edit.

## 0142 — A resume token that named a point and not the invocation it belongs to

**State:** Accepted
**Folder:** [decisions/0142-resume-bound-to-entry-point/](decisions/0142-resume-bound-to-entry-point/)

Issue #104. `VCSX-SPEC.md` Sections 8.1 and 8.6 fix three things a `resume` is established against —
a different policy, a different repository, a different major version — and say nothing about the
entry point that issued it, while Section 13.1's Resuming row names one of the three. So a token a
`ship` returned may be supplied to `land`, and **a `ship` token can name a point `land` never
reaches**: `ship` never runs `merge`, `land` never runs `create_pr`. Both readings are faithful, so
the divergence is *documented rather than prevented* — the Conformance Statement template's
`resume_token` row is where two conforming engines legitimately disagree about whether a crossed
token is refused, which is the shape decision 0134 closed for the trigger vocabulary. The decision
binds, and the argument that decides it is one neither the report nor the first recommendation made:
binding gives `resume_unusable` a **decidable** judgement where its stated inputs do not exist.
Section 8.6 judges it "from the invocation's arguments together with what the engine holds
independently of them — the policy it validated and its own major version", while Section 6.1 calls
`provision` "the one entry point that runs where no policy could be read" and Section 8.6
nonetheless places `resume_unusable` inside `provision`'s otherwise-exhaustive list. The entry-point
field settles it without reaching for the policy: `provision` issues no token, so every token
supplied to it mismatches on that field alone — and so does every token supplied to `load_policy`
once decision 0141 makes it an entry point. It costs no new token, no Section 13.3 obligation and no
Statement row; it **narrows** the existing row to the form question, the move 0134 made three times.
The condition was first stated over the flow the token names being **expressible in the invocation
being resumed**, to reach a crossing entry-point equality misses — an await-branch token supplied to
a bare `land`. **That general form is withdrawn and the condition is the entry point alone**, for
the reason below. The converse crossing was raised and **withdrawn**: a merge-loop token under `land
--await` is not refused, because Section 5.5 re-enters the point "rather than beginning at its entry
point", so the prefix is never run and refusing would make legality depend on a flag that changes
nothing. What that case needs is a sentence, and **the sentence took four attempts, of which the
first three are the useful record**. First: "sequence-selecting arguments are not consulted on a
resumed invocation" quantifies over a class Section 8.1 does not define — issue #100's defect one
document over, in the same batch, inside the repair for a different one. Second: deriving that class
from Section 12's signatures marks `message`, because `VCSX-SPEC.md:2969` is `function
ship(identity, message)` and not `ship()`, so the derivation says a resumed invocation does not
consult the commit message — false in the same code block, where the commit loop reads it at every
turn. Third: narrowing the test to a parameter appearing in a *condition* in the body is syntactic
where the property is positional, and a future `land(squash_mode)` branched on inside the merge loop
would satisfy it while being consulted on every resume that re-enters that loop. Fourth, and taken:
**the property is not needed at all.** Section 5.5 re-enters the point "rather than beginning at its
entry point", so a resumed invocation does not run the flow ahead of that point and an argument the
flow reads only ahead of it has no effect — `await_first` read once before `land`'s first dispatch,
`message` read at every turn of a loop a resume can re-enter. Both crossings fall out with nothing
classified, the await-branch one **reclassified as not a refusal** rather than uncovered, and the
fourth condition reduces to the entry point: a token names a point in the flow its entry point
began, and the only way a point can be missing from the flow being resumed is that a different entry
began it. Along the way the step-zero finding stands: **`await_first` is not in Section 8.1 at
all.** That section enumerates four await parameters and no sequence selector, so Section 7.2 cites
Section 8.1 for an argument it does not carry while Section 8.1 requires argument names for shared
concepts to match this specification. Enumerating the argument is owed regardless, and the registry
group survives the property that prompted it, costing a **new group**: `vocabulary.json` has
twenty-one entry-bearing groups plus `task_model` and **no `arguments` group**, so it must be
authored against the longest enumeration in the document. It is owed anyway, and this is its second
demand rather than its first: Section 8.1's argument names are normative, the section already keeps
per-argument properties as hand-maintained prose lists, and decision 0141's pin makes the
consumer-configuration exception set four. The group is closed from the start, or it inherits the
`entry_points` blind spot 0141 found — and it carries optionality, the consumer-configuration
exception and requiredness rather than a `selects_sequence` flag, which goes with the property.
**Requiredness is neither a boolean nor a list of entries**: Section 8.1 states it as every entry
point (`local_vcs`), one named entry (`store_location`), and a condition (`git_access` for "an entry
that can reach one"; the forge coordinate and `forge_access` "where a forge is configured"), so the
field admits three shapes. The dependency on issue #103 recorded as firm is **withdrawn with the
general form**: the entry point is carried by the token, no enumeration is consulted, and nothing
here waits on that decision. One coupling the capture did not name is recorded on the implementation
reply to PR #114: decision 0153 adds a part to the resume token outright and this decision requires
the token to answer which entry point issued it — a part in any engine whose point encoding does not
already determine that — so the two are one format revision landed together and two landed apart,
with a window in which a token issued between them decodes on neither build. This decision plausibly
lands first, ordering itself after 0141 while 0153 waits on 0143, so both records now carry the
coupling rather than only the one applied second.

## 0143 — Where a substituted result lands in a front-end sequence

**State:** Accepted
**Folder:** [decisions/0143-front-end-landing-rule/](decisions/0143-front-end-landing-rule/)

Issue #107, split out of #103 and reachable without a resume. `VCSX-SPEC.md` Sections 12.2 and 12.3
write the front-end sequences as pseudocode that tests each operation's result itself, and Section
5.4 says a result a `run_op` edge disposed of is replaced by that edge's own result — "in the
machine", with nothing said about what the **sequence** is handed. The report offered three readings
and the review narrowed the field to one, which makes the finding worse rather than better: "edges
override each step" refuses the both-fire reading, and Section 12.3:3078 — `merge:head_moved`
"reaches a caller through this sequence only where a repository binds it to an edge that ends the
flow" — refuses the edges-never-fire reading by presupposing exactly what it denies. **What survives
is the reading that produces a wrong write, so an implementer does not resolve this by coin flip:
they resolve it correctly and ship the bug.** Two wrong writes, both under the specification's own
example edge (`push:non_fast_forward → run_op integrate`, which `match-edge.json`'s first vector is
also built on): the push loop takes `integrate:ok`, falls through every test, breaks, and **opens a
pull request on the head the remote already held while reporting success**; and the commit loop
takes any `done` substitute for `commit:worktree_moved`, falls through, and **pushes a worktree
nothing committed**. The second reaches the state Section 13.1 says the `is_dirty()` guard prevents
*without falsifying that row* — the row is scoped to a predicate that cannot answer, and here it
answered fine — which is worth more than a falsified row: the document asserts the property only
where the guard is the mechanism and nowhere in general, which is issue #111. Two of the
pseudocode's names are undefined and inconsistent — `dispatch(` once at 2975, `result_of(` four
times, all on `return` paths — and under decision 0138's own test they are the only two of Section
12's dozen called-and-undefined names that fail it. The one-word statement of the gap is that
Section 5.4 ends "for `done` with no edge, continue" and **nothing says what `continue` continues**;
the corpus already noticed, inventing the distinction "`continue` and `no_op` are Section 5.4
outcomes, not Section 5.2 actions". The decision splits what the pseudocode fuses: a repository edge
replaces the built-in **disposition**; where the disposition returns control the **control
transfer** is the trigger's and is unchanged; where it ends the flow the invocation ends; where the
transfer is `return` the sequence reports the result the machine last handed back — with the
transfer selected by the sequence's own `run_op`, pinned to the root so substitutions inside the
machine are invisible. That is determinate for all ten branches where the report's own rule ("land
where the built-in disposition would have landed") is determinate for the three `continue`-shaped
ones and silent for the five `return`-shaped ones. The middle clause is a review finding against the
split's first draft, which had the transfer unconditional — **false where the edge ends the flow**,
since a `push:non_fast_forward → escalate` edge would then continue the push loop, the one thing
Section 5.6 says an `escalate` does not do: the repair for an under-specified landing point had
briefly specified one that contradicts an action's own definition. The `done`-class consequence is
granted rather than merely recorded, and on the built-in's own behaviour rather than on the two
sentences first put in tension: Section 12.2 **already** ends `ship` without a pull request on five
paths, so Section 7.1's "up to and including opening or updating the pull request" states the extent
of the sequence and never was a postcondition. What a repository edge introduces is a `done`-class
early return, and **that** is the unwritten invariant — `ship` returns `done` today only from
`create_pr` and `land` only from `merge`, which is what a caller reads to know the pull request
exists — so `push:pr_closed → run_op status` violates no rule and silently repurposes the only
completion signal the envelope has. The replacement test is **the operation the result names**, not
its class, stated in Section 13.1: the `output_keys` group carries the keys Section 8.2 fixes and
says the rest of `outputs` is entry-specific, so a pull-request identifier there is not portably
testable. **No count of that group is stated**, and the drafts that stated one are the finding: this
chapter's first draft said three, its correction said ten, and decision 0141 — same batch — adds an
eleventh, so a number written into Section 13.1 would be falsified by a decision already in the log
while the conclusion turns on the group's note either way. Raised on the implementation reply to PR
#114, against this decision and 0152 together. It is merged behaviour rather than a hypothetical —
the reporting engine returns `status:ok` for that edge today — and the answer leaves that build
correct, the repair being a row telling callers what to read. The vectors need a **new corpus
function**, since `match_edge` stops at edge selection by construction, and its `expect` names three
things: the disposition, the transfer, and what the invocation reports, the third being what tells
`status:ok` from the built-in escalation.

## 0144 — What a concurrency slot counts, and when a run starts occupying one

**State:** Accepted
**Folder:** [decisions/0144-slot-accounting-and-provisioning-phase/](decisions/0144-slot-accounting-and-provisioning-phase/)

Issue #109, split out of #108 because that issue's severity could not be stated without picking one
of two sentences. Section 8.3 computes headroom from `running_count` and
`conformance/vectors/available-slots.json` pins that signature — two inputs, four vectors, `claimed`
nowhere in the file; Section 8.5's rationale says "because `claimed` counts against
`available_slots`", 107 lines away in the same document. **The reading that loses livelocks a
deployment, and Section 16.7 shows it**: `on_retry_timer` removes the retry entry *before* it tests
headroom while the claim is still held, so a `max_concurrent_agents: 1` deployment with one issue in
backoff computes `1 - |{X}| = 0`, requeues X at `attempt + 1`, and repeats until the backoff saturates
at `agent.max_retry_backoff_ms` — X blocking its own re-dispatch forever with nothing running. The
general form is worse and is reached by ordinary operation rather than by a failure: claims are held
across backoff, and a **normal** exit schedules a continuation retry and keeps its claim, so a
deployment at its limit stays there after every run completes. It also contradicts what Section 8.3
says the limit is *for* ("it counts agent sessions, not where they run" — a `RetryQueued` issue is
none), and it collapses two conditions Section 8.2 lists separately, making each claimed issue spend
global capacity to prevent its own duplicate dispatch. So the formula and the vector stand, Section
8.5's clause is struck and its **conclusion survives** — Part B still schedules no retry — with the
cost restated as the one that follows: the issue holds its own claim and is skipped by every tick
until the retry fires, other issues unaffected. **Decision 0138's chapter records the same
magnitude**, so it is corrected there as a logged review finding rather than quietly, its repair being
correct on its other grounds; the finding's shape is one 0138 itself recorded one step over — a
consequence correct in the reasoning that reached it and false against an artifact that mechanizes
what it quantifies over. The settlement exposes a second edge that fails the *other* way and is
unbounded: Section 9.11 says a `Provisioning` dispatch "holds a dispatch slot but is not yet
`Running`", which under `running_count` is true only if it is in the `running` map, while Section
7.1 state 4 reads as a membership test — so the natural implementation is a second collection the
formula does not count, and since acquisition is asynchronous every tick sees the same headroom and
requests another node. Section 16.4 already writes the entry immediately after `spawn_worker`, so
what is missing is the sentence: **a dispatched run occupies `running` from dispatch until it ends,
and `Provisioning` and `Running` are phases of one entry rather than membership tests.** That is a
data-structure decision rather than a wording one, which is why it is stated in those terms; it also
removes a special case from 0145, since a provisioning run that never reached an agent then has an
entry `terminate_running_issue` releases. Stating the formula over `claimed` instead is steelmanned
— one set answering both of Section 8.2's questions is a simpler object, and bounding commitments
rather than sessions is a real want — and loses on the livelock, on Section 8.3's own statement of
purpose, and on requiring a pinned vector to be regenerated to buy a property the document does not
claim; if that want returns it returns as a **second** bound, not a redefinition of this one.

## 0145 — The claim nothing released

**State:** Accepted
**Folder:** [decisions/0145-claim-lifetime/](decisions/0145-claim-lifetime/)

Issue #108. Section 7.1 defines a `Released` claim state and Section 17.4 requires the release to
happen "without waiting for a backoff to elapse", while Section 16 removes an issue from `claimed` in
exactly one place — `on_retry_timer`'s not-a-candidate branch — and Section 8.5 Part B schedules no
retry. `terminate_running_issue`, the function both Part B branches and Part A's stall path call,
removes the running entry, accounts for the runtime, terminates the worker and never touches
`claimed`. **The release was a side effect of the retry decision 0138 correctly removed**: that
decision records the old retry self-cancelling "via `find_by_id -> null -> claimed.remove`", which was
the release's only producer, and `git log -S` puts the removal and the Section 17.4 row asserting the
release in one commit, `87abf10`. It is 0138's own recorded review finding one step over — that one
kept Part A's retry while removing its only producer, this one keeps a release whose only producer it
removed. What it costs: the issue is **permanently un-dispatchable**, since Section 8.2 tests
`claimed`, so a ticket closed while its worker ran and later reopened is fetched every tick and
skipped every tick until a restart clears the `Reconstructable` set — a symptom that reads as a
tracker-adapter problem rather than a scheduler one — and `claimed` grows monotonically. It costs
**no** concurrency slot; the earlier claim that it did is withdrawn on decision 0144's settlement. A
second edge sits in the same place: Section 16.4's spawn-failure early return arms a retry *above*
`state.claimed.add(issue.id)`, so the next tick re-dispatches with `attempt=null` and a repeatedly
failing spawn retries every `polling.interval_ms` (default `30000`) instead of escalating toward
`agent.max_retry_backoff_ms` — no double dispatch, but the backoff lost on the path whose whole
purpose is to back off. The repair is two clauses — `terminate_running_issue` releases the claim it is
removing the running entry for, `schedule_retry` takes it so `RetryQueued` is claimed by construction
— **stated as a partition rather than as two edits**: after them, every site that removes a running
entry either releases the claim or hands it to a retry entry, and there is no third, with the three
sites named so a site added later has to say which side it is on. Stated as two rules, a third removal
site added later is a new leak with no rule against it, which is the shape this defect has. The
derived view `claimed = keys(running) ∪ keys(retry_attempts)` — which Section 4.1.8 already describes
for restart — is the first thing a reader reaches for and would make the release unfalsifiable rather
than merely required; it loses because it makes duplicate-dispatch prevention a consequence of two
other collections' contents, so any future path writing a run without a `running` entry silently
reopens duplicate dispatch with no rule violated. The explicit set is load-bearing for remote mode.

## 0146 — Run-attempt identity and the messages a replaced run keeps sending

**State:** Accepted
**Folder:** [decisions/0146-run-attempt-identity/](decisions/0146-run-attempt-identity/)

Issue #106. `on_worker_exit` decides whether an exit is owed a retry by testing whether the running
entry is **present** — and Section 8.4 says, of the sibling function eleven lines below it in the
same code block, that "Testing only whether an entry is present does not satisfy this: the entry
that a discarded fire must not consume is present by construction". The same construction produces a
present-but-wrong entry here: reconciliation terminates run A and removes its entry, a later tick
dispatches run B under the same key, run A's in-flight exit arrives, the guard does not fire, and
the orchestrator **converts a live run into a queued retry and loses it** — run B's own exit then
arriving with no entry and correctly doing nothing. The window is not sub-millisecond: on the stall
path the re-dispatch happens after a backoff, so the guard fails whenever a killed worker takes
longer than one backoff to die, and in remote mode the exit crosses a seam whose events are buffered
and replayed *by design*. **The guard belongs on the channel rather than on the exit callback**,
because Section 16.6 sends agent events keyed by issue alone and a late one from run A lands on run
B's entry: it writes `last_timestamp`, which is Part A's own stall reference, so a dead run's
trailing events keep a genuinely stalled replacement alive — the one consequence with no second line
of defence, because the mechanism that would clean it up is the one the stale events defeat; it
overwrites `session_id`; and it computes Section 13.5's deltas between two unrelated cumulative
series, which Section 8.8's `Durable` idempotency is keyed on. The asymmetry is the argument for the
channel over the fields: in the reporting engine one field on the entry is idempotent under mixing
(rate limits order by `fetched_at`) and the other is silently wrong (a high-water mark across two
series is a value neither produced). **The identifier is one already owed in four places, not a
fourth identity**: Section 13.1 REQUIREs `origin_run_id` and states it is never null, Section 9.11
calls `lookup_by_run_id` and `signal_done`, Section 14.4 keys the remote run registry by run — and
Section 4.1.5 defines no id, so an emitter carrying `origin_run_id` as non-optional cannot construct
a session reference at all and a runtime snapshot's running row reports no session. That is true of
the **definition** and says nothing about the **comparison**, so Section 4.1.5 states both, on the
implementation reply to PR #114: a retried attempt carries its own `run_id` and its origin's,
`origin_run_id` being the `run_id` of the attempt the sequence began at — which is also the type
that field has never been given. Every attempt in a retry sequence carries one `origin_run_id`,
Section 13.1's own reason being that the sequence is a group rather than a linked list, so a guard
comparing against *it* fails in exactly the case this decision is about, where the retry that
dispatched run B belongs to run A's sequence. Its uniqueness is **wider** than Section 8.4's
generation, which is compared only in memory: a `run_id` is written to durable logs and handed to an
external scheduler, where a per-process counter restarting at 1 collides with the previous process's
records. That requirement needs a stated source, because it is not a function of state — and the
answer is not "the host supplies it", `SPEC.md` having no host in it: **Section 16.1 is already the
function that touches the world before the loop starts**, so it establishes a process identity,
`Implementation-defined` and documented on the `worktree_revision()` precedent, and `dispatch_issue`
composes `run_id` from it and a counter. The guarantee is stated over the distinction the value MUST
make — no two run attempts in one deployment share a `run_id` — because "non-reuse across restarts,
scheme `Implementation-defined`" reads as satisfiable by a constant until the first test that needs
it to differ, and a build whose simulated restart reuses the identity has a guard that is never
exercised and a suite that is green. The **shape** changes with the field: decision 0136 gave
`on_retry_timer` get-compare-remove "because a comparison that fails after the pop has already taken
the entry the fire should not have touched", and `on_worker_exit` inherited neither the field nor
the shape. Costs stated rather than discovered: a Core entity and the worker→orchestrator message
shape, plus one `Implementation-defined` obligation owing a Section 19 line and a Conformance
Statement row — decision 0128's trap, named from the start.

## 0147 — What a restart restores, and which class the Core field is

**State:** Accepted
**Folder:** [decisions/0147-cached-signal-restart/](decisions/0147-cached-signal-restart/)

Issue #105. Section 14.3's `Cached external signal` bullet says the last-known-good "MUST be carried
across both a failed refresh and a process restart"; Section 14.4 says "Only `Durable` state
introduced by an OPTIONAL extension is restored across a restart"; `provider_rate_limits` is Core
and carries the class, so it is inside both. **The rest of the corpus already answers it three
times, the same way** — Section 16.1's `restore_cached_and_durable_state` overlays both classes
"when an OPTIONAL extension configures one; otherwise the zero/null defaults above stand", Section
17.4's row is conditioned on the extension being implemented, and Section 14.3's own closing
paragraph says the class "is introduced by an OPTIONAL provider-quota extension". So the contract is
settled and the two sentences are the outliers. Neither half of the issue's ask reaches it alone,
which is why this is three edits: **reclass `provider_rate_limits`** on the `agent_totals` precedent
— `Ephemeral` for observability in Core, becoming `Cached external signal` when Section 8.9 enforces
on it, which is where its staleness bound and `UNKNOWN` policy come from; **scope Section 14.3's
restart half to a store**, mirroring the `Durable` bullet's existing degradation clause; and **say
both restorable classes in Section 14.4**, whose "only `Durable`" is false for a quota extension
with a store independently of the Core-field question. Section 8.9's own Recovery-semantics bullet
restates the unconditional promise and was not in the ask, so it moves too. The reclass is more than
re-labelling for a reason that has nothing to do with tidiness: **`Ephemeral` is the one class whose
reset consequence is a required part of the class**, so reclassing is what makes "the status surface
reports no rate-limit reading until the next agent update refreshes it" get written down somewhere a
consumer reads — where the minimal fallback (keep it `C`, say Core has no store) leaves the
obligation stated in Section 14.3 and reaching no artifact that publishes it, and where a build
carrying the class as a wrapper type has its compiler demand the sentence. It also closes the
issue's second edge as a side effect: a Core-only build has no value it is told to age against a
bound no Core section defines. The third edge is the one the section turns on and **the clause took
four drafts, of which the three discarded are the record**. Conditioning on the *configuration*
cannot see a store configured and empty, or unreachable. Conditioning on the *value* — "a restored
value is a reading; a restore that produced none is not" — covers all four startup shapes and leaves
two holes with no store involved: a restore whose `fetched_at` is already older than
`stale_after_ms` (default `180000`) arrives `UNKNOWN` and *is* a reading, and the drained idle needs
no restart at all, since Section 8.9's gate leaves running workers alone so in-band readings arrive
only while a worker runs — three minutes of quiet between tickets deadlocks a deployment that held a
reading and replaced it in this process. So the rule is conditioned on whether a reading can
**arrive** — and, on the implementation reply to PR #114, on releasing no more than that: where no
out-of-band refresh path is configured an `UNKNOWN` MUST NOT pause dispatch outright, and the gate
clamps headroom to **one run in flight** until a reading arrives. The third draft released the whole
limit, which takes a fail-closed deployment at `max_concurrent_agents: 20` from paused to twenty on
a missing reading, at every startup and after every idle drain; one run is what makes an agent
update arrive, so the deadlock argument reaches no further, and Section 8.9's existing SHOULD for a
provider exposing no quota interface is the exit that keeps the clamp from being permanent. The
condition is the class's and the quantity is the gate's, so they land in Sections 14.3 and 8.9
rather than together. Fail-closed stays intact for the deployment that configured a poller in order
to have it, including the startup window, and a poller reaching nothing pauses a deployment that
asked to be paused and says why in the snapshot's `error`. The value-conditioning survives with a
different job: it is what decides whether a startup `UNKNOWN` is Section 8.9's permanently-unknown
arm or its transient one — the pair that carries a SHOULD and a MAY today with nothing to decide
between them. **This is the one clause the issue thread had not converged on when the decision was
captured**, recorded with its full derivation so a reversal has something to argue against — which
is what the reply did, on the derivation rather than on a preference, and the third draft is kept in
the record because the difference between the two is the question. The dual-valued "Spec default"
cell gets a clause on the template's **column header** rather than in either row — it states which
of the two the implementation ships, not "both" — covering `agent_totals`, which has carried the
same ambiguity unread only because no generator has read it.

## 0148 — Routing keys and the record they route over

**State:** Accepted
**Folder:** [decisions/0148-issue-routing-substrate/](decisions/0148-issue-routing-substrate/)

Issue #113, the sibling of #100 rather than a restatement: that one is about one dispatch bullet's
computability, this is about whether a whole section's mechanism has a substrate. Section 8.7 routes
each polled issue through "an explicit, tracker-implementation-specific mapping in the policy config"
and names the keys by example — the `linear` adapter by project, team, label or assignee, the
`forgejo` adapter by repository and issue tags/state — while Section 4.1.1 declares its record "the
only issue the orchestrator, the prompt renderer and the observability output ever see" and carries
`labels`, `state`, and (after decision 0140) `assignees`. **`project`, `team` and the `forgejo`
adapter's `repository` are in no field at all**, and `metadata` is what Section 8.7's own last sentence
rules out — an opaque adapter-owned map *is* untrusted free-form content, and Section 4.1.1 says the
core does not interpret it. The two readings put the mapping in different components and only one is a
policy-config mapping: after normalization it is a pure function of the config and the record, and
Section 8.7's own example is unimplementable; before normalization the mapping is adapter-private,
"tracker-implementation-specific" becomes "tracker-implementation-*private*", and Section 17.4's two
checks assert a property of a mapping the orchestrator never sees. The `linear` example's first key is
**unreachable twice over**, which says the two sections were written against different pictures:
Section 5.3.1 carries a single `project_slug` and Section 11.1 fetches "for a configured project", so
every polled Linear issue is in one project and routing by project selects everything or nothing. The
decision routes **after** normalization, adds `project` and `team` to Section 4.1.1 as OPTIONAL,
tracker-dependent and normalized like `labels` — `project` being the tracker's container, which for
`forgejo` is the owning repository, named once rather than twice — has Section 11.7's descriptor
declare which the adapter populates so a mapping keyed on an unpopulated field is a Section 6.3
preflight error rather than a deployment that silently routes nothing, restates Section 8.7's bullet
over the record's fields, and **refuses an issue two rules claim** rather than picking, stated over
the issue because two rules can be disjoint over every issue that exists today: a dispatch grants an
agent commit and pull-request authority, and picking the first match sends it into a codebase the
operator did not point it at. 0140's publication clause is inherited rather than re-derived, since
Section 4.2's normalization is not something an adapter opts into. Routing before normalization is
steelmanned — every key exists in the raw payload, identity semantics stay where the knowledge is, and
Section 11.1's `project_slug` is the existing precedent — and loses on four counts, of which the
fourth is the one 0140 already paid for: a routing attribute can change while a run is in flight, and
Section 16.3 iterates `for issue in refreshed` while Section 8.5 Part B has **no absent branch**, so an
issue moved between projects mid-run reaches none of the three cases and its run continues against a
repository the mapping no longer selects. **What this decision does not fix is named rather than
missed**: the mapping has no configuration key and neither does the managed-repository list — Section
5.3's six top-level keys include neither while Section 6.4 and Section 8.7 assert both, and Section
8.1 says "each tracker" where Section 5.3.1 defines one. That schema is its own decision, nothing here
depends on it, and a single-repository deployment is fully expressible today.

## 0149 — The column that said who provides and not who requires

**State:** Accepted
**Folder:** [decisions/0149-capability-required-by-column/](decisions/0149-capability-required-by-column/)

Issue #102. Decision 0134 rewrote `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1 to infer, from
the operation set being closed, that "a capability beyond the list is a backend's own rather than an
engine's", and moved the columns from `Capability | Required by (operation) | Signature and result` to
`Capability beyond Section 9.1 | Provided by (backend) | Signature and result`. The premise is right
and **the inference fails structurally rather than because two capabilities happen to be missing**:
the premise licenses only "not an engine-added operation's", because `Required by` and `Provided by`
answer different questions — the engine requires, the backend provides, and a floor being met says
nothing about who wanted what sits above it. That holds even with Section 9.1 complete, since Section
6.6 leaves host-side unit resolution `Implementation-defined` and an engine may need a capability for
whichever mechanism it documents. So 0134 removed the column that carried the fact and added one that
does not, where it should have added — and the section's original question now has **no row anywhere
in the template**, while every engine that implements Section 4.1 has an answer to it. The harm is
concrete: Section 13.3's tables are a declaration a consumer relies on, and the reader the row serves
is a backend author deciding whether a capability above the floor is optional (drop it and the engine
still conforms) or load-bearing (drop it and the engine cannot implement Section 4.1 or Section 6.6).
Field-verified rather than hypothetical — the reporting engine's Statement already carries the
four-column form with a paragraph above the table naming which template inference it is contradicting
and why, because filling it as directed would publish three engine requirements as backend extras.
The repair rewords the inference and restores `Required by` at position two, **unqualified** rather
than as 0134's `Required by (operation)`: the three real requirers are an operation (`load_policy`), a
lifecycle position (`before:commit`) and a declaration in the document (a `[hooks.engine]` unit), and
the qualified form excludes two of them. It is owed **independently of decisions 0150 and 0151**,
whose additions should eventually empty this table — an argument for it rather than against, since
until then the reworded row is the only artifact saying *this engine requires them of every backend*
rather than *some backend happened to bring them*, and the rows do not disappear when those land, they
move from prose into a declared descriptor field with a test behind it. Two mechanical facts checked
rather than assumed: `check_obligations` scans only the **second** cell for section numbers and this
table's number lives in the first, so the insert is invisible to the parser; and the reword adds no
`Implementation-defined` behaviour, so 0128's trap does not fire — stated rather than left silent,
because three decisions in a row missed the case where it does.

## 0150 — The diff a commit would record, and the identity that comes with it

**State:** Accepted
**Folder:** [decisions/0150-worktree-diff-capability/](decisions/0150-worktree-diff-capability/)

Issue #110, first of two, split from #102. **The strongest form of the finding is not the derivation
— it is that an engine has already had to invent all three capabilities**, under the report's own
names and shapes, months before the report, with two backends behind them and published under
Section 13.3 as that engine's own. So the specification is not being asked whether it might need
them. This decision takes the one blocked by nothing: Section 10.4 supplies "the commit message and
**the diff the commit would record** at `before:commit`", Section 9.1's `diff(base_ref)` is the
branch delta against the resolved base and `worktree_revision()` answers an identity, and nothing in
Section 9.1 or 9.2 answers the question. Section 9.1's own closing paragraph is the better citation
than Section 4.1's "realized through the plugin layer", because it makes the claim rather than
implying it — "every operation Section 4.1 defines is realizable through it" — and it is false in
the section the repair edits. This one is **on the documented happy path**: Section 6.5's example
policy binds `before:commit` → `run` → `scan-content`, so the list is short of something every
engine supporting the canonical example needs. The load-bearing half was not in the report and is a
**live defect**: Section 10.4 closes by asserting that `before:create_pr` "needs no identity to
condition on where the other two do", which stops being true the moment the diff is a second read of
the tree — an engine reading the diff at T₁ and the identity at T₂ matches `expected_worktree` for a
tree that moved in between and then held still, and commits content the scan never saw, violating
Section 6.6's "a gate is only a gate if what it inspected is what proceeds" with every rule
satisfied. The reporting engine has exactly that pair, its diff read before the position and its
identity inside the operation after it — **field-confirmed after capture and repaired there in this
decision's shape**, the window having made `commit:worktree_moved` unreachable and left a
conformance test bound to Section 6.5's own `scan-content` shape passing because of it. Two findings
came back from that build and are carried into the edit: the pairing spends Section 9.1's
bookkeeping allowance **less**, not more — one staging write at the position where two reads made
two, which is the price decision 0079 weighed — and the undetermined case moves with the read,
failing from the composition before the position runs rather than at the capture after it, so a gate
no longer runs over content the operation will not use. **A sequencing rule is one hole short of
enough**: take the identity first and a tree that moves to B and back to A matches exactly, because
`worktree_revision()`'s contract is stated over *content* — an editor writing a file and reverting
it reaches it, and no ordering can see it. So the capability answers a **pair** — the diff, and the
identity for the tree it read, which the engine supplies as `expected_worktree` — making the wrong
shape unwritable rather than writing a rule against it. The honest objection, that Section 9.1 has
no precedent for a capability answering two things, does not hold: `ahead_behind(base_ref)` is that
precedent and is there for the same reason, and Section 9.1's `commit` bullet **already** binds the
identity to "when the working tree was read at `before:commit`", so the pair is that sentence's own
reading made true by construction. `worktree_diff()` inherits `is_dirty()`'s set rather than stating
its own — a backend answering a *staged* diff would satisfy a loose reading and hand the scan the
wrong content, which the pairing does not catch — and `worktree_revision()`'s write-to-bookkeeping
note is restated over the position, since both are consulted there on invocations the gate then
blocks. The network enumeration stays at four, checked against Section 9.1's list rather than
inferred from the signature, which that section forbids.

## 0151 — Reading and materializing the policy source

**State:** Accepted
**Folder:** [decisions/0151-policy-source-capabilities/](decisions/0151-policy-source-capabilities/)

Issue #110, second of two: the capabilities that turn on `load_policy`. Section 9.1's realization
paragraph maps five operations onto capabilities and **`load_policy` maps onto none**, in Section 9.1
or 9.2, while Section 4.1 says each operation "is realized through the plugin layer" and Section 9.1's
closing paragraph claims every one is realizable through the list. Section 4.1's excuse — "it is why
no capability of Section 9.1 reads a file at a revision — one operation does it once, rather than a
capability doing it per read" — explains the absence of a *per-read* capability and does not supply
the one read the operation makes; and **decision 0141 removes its premise**, since under the
fingerprint pin every entry point reads and validates the document, making it the read every entry
point makes once per invocation, which is exactly the per-read shape that sentence denies. So
`read_at_source(remote, branch, path)` joins the list, with three answers rather than two because
Section 6.1 distinguishes `policy_source_unreadable` from `policy_not_found`. The second half of the
same read is that **`vcsx.toml` has no address**: Section 6.1 fixes `repo.policy.toml`'s path and its
`Implementation-defined` discovery precedence, and states neither for the file it says is "merged into
the same surface" — a build put it at the repository root beside the first, "one constant next to
another, decided by nobody, documented nowhere". The harm is not a differing fingerprint (two engines
never compare pins; the value is opaque and only its issuer reads it) but that **two conforming
engines merge different documents from one revision and execute different policies**, of which a
differing pin is a symptom nobody can see — so the repair is owed on Section 6.1's own terms, on the
sibling's precedent. `export_source(remote, branch, into)` realizes Section 6.6's host-side unit
resolution, a revision not being a directory, with `into` earning its place because backends
materialize differently enough that the engine cannot own the mechanism but each can be handed a
location. It is **OPTIONAL with a descriptor field**, parallel to "derives more than one working tree
from one store", because an engine whose unit form is a registered task materializes nothing and a
required capability a conforming engine never calls is worse surface than none — and the condition is
stated **per engine rather than per unit**, because a command-line unit form carries no statement of
whether it names a path in the source, so a per-unit condition is not evaluable from the specified
configuration, which is issue #100's test one document over. That keeps the `capability_unsupported`
refusal on Section 9.3's determinable half with both halves static, widening its "What remains on the
first-use side is an OPTIONAL capability (Section 9.2)" sentence, this being the first OPTIONAL
capability in Section 9.1. The ordering that makes both credential-free is written down rather than
implied, since Section 9.1 says a capability's context is "read off this list and never inferred from
its arguments": a read of the policy branch acquires nothing **only because `provision` precedes it**,
placing the copy in the store, a consequence Section 13.1 already accepts. What the addition buys is
Section 9.3's descriptor discipline and a reported refusal at validation instead of three engines
naming one requirement three ways.

## 0152 — What a front-end sequence must reach, not only where it stops

**State:** Accepted
**Folder:** [decisions/0152-front-end-progress-invariants/](decisions/0152-front-end-progress-invariants/)

Issue #111, split from #107 and independent by design. Section 13.1's Front-ends row states an upper
bound, a guard property and two convergence properties, and **no lower bound**: nothing says the
sequence must *reach* anything. The nearest thing to one is in a different row and is scoped to the
predicate failing to answer — "a `ship` whose `is_dirty()` cannot answer dispatches `commit` and
yields `commit:failed`" — which makes the omission harder to see rather than easier, because a
reader hunting the invariant finds a sentence that reads like it and stops. So decision 0143's
reading 2 passes the **whole matrix**: `is_dirty()` answered, `ship` stopped at the pull request, no
retry misbehaved, and a pull request opened over a tree nothing committed. The plainest exhibit
needs no repository policy at all — Section 12.2's commit loop ends in a bare `break` while the push
loop below tests `if r.class != done`, so the block as printed walks from **any**
non-`worktree_moved` commit result into the push loop, and the invariant is exactly what makes that
`break` sound. Three invariants, with three corrections to the issue's phrasing, each load-bearing.
**Section 13.1 alone is not a home**: its lead-in is "A conforming engine SHOULD include tests
covering:", so an invariant living only there is a test recommendation an engine can decline while
conforming — and Sections 7.1 and 7.2 already carry the same shape one operation over ("It commits
the tree it read", "It merges the head it read"), which "it pushes what it committed" completes.
**Quantify over the flow, not the invocation**: a resumed `ship` continuing a resolved
`create_pr:blocked` dispatches `create_pr` in an invocation containing no push, so the
invocation-scoped row would refuse the resume the row above it requires, and Section 5.6 supplies
the unit. **State it over the sequence's step, not over `ship`**: an edge whose `run_op` dispatches
`create_pr` is the repository's dispatch, and a row falsifying it would take back what 0143 grants.
The third invariant is the one the pair pays for: Section 12.2's built-in ends `ship` without a pull
request on five paths and **every one is non-`done`**, so `ship` returns `done` today only from
`create_pr` and `land` only from `merge` — what a caller reads to know the pull request exists,
stated nowhere, and exactly what 0143's permitted `done`-class early return spends. The replacement
test is **the operation the result names**, not its class, readable from the envelope with no new
field, because the `output_keys` group carries the keys Section 8.2 fixes and notes the rest of
`outputs` is entry-specific, so a pull-request identifier there is not portably testable. **The
count is no part of that and is not stated**: an earlier statement said the group fixes three, this
decision's draft corrected it to ten, and the correction reproduced the failure it was repairing —
decision 0141 adds an eleventh entry, neither this plan nor 0143's orders itself against it, and
step 3 puts the sentence in Section 13.1. Raised on the implementation reply to PR #114; the repair
is to cite the group rather than count it, which is what both earlier statements already said the
conclusion turns on. The row leans on one clause: `op` is present exactly where a result was
decisive and null only for the two escalation shapes Section 8.4 nulls, so a caller reading it has
an answer on every ending. Under 0143's transfer split the first two are **derivable rather than
additional** — only `push:ok` and `push:up_to_date` reach the push loop's `break` whatever a
repository binds — which makes them a regression test on the landing rule and is an argument for
stating them. The issue argued this should precede 0143; that argument was good and its premise is
gone, since the rule is chosen. Its mechanical half stands: the two edit **one anchor set**, so two
decisions, one editing pass.

## 0153 — A resume continues the flow, and the token carries the root trigger

**State:** Accepted
**Folder:** [decisions/0153-resume-continues-the-flow/](decisions/0153-resume-continues-the-flow/)

Issue #103. Section 5.5 says what a resume re-enters and stops there; **no section says what happens
after that re-entry produces a result**. For a single-operation entry point the question does not
arise; for a front-end sequence a `ship` that escalated at `push` either reports the re-dispatched
`push` and stops or carries on to `create_pr`, and two conforming engines then give one caller two
different results from one token. **The argument that decides it is Section 5.6's accumulation.**
Under the narrow reading a resumed invocation that re-dispatches successfully ends `done`, so no
token is issued (Section 8.2 puts `resume_token` in `outputs` only at `needs_caller`), the count is
discarded, and the caller re-invokes from the top with a fresh budget — so a resolve-and-resume loop
never exhausts for the interactive front-end while it does for a driver whose resolver returns in
process. That is precisely the divergence Section 5.6 is written to prevent, and it makes Section
13.1's "reaches `flow_exhausted` **across invocations** and not only within one" false for one of
the two. Verified against a build implementing the narrow reading, which changed position on this
argument having weighed and not found it. Two supporting arguments: **Section 5.4 already names the
disposition and its name is "continue"**, so the narrow reading is the one needing a fourth
disposition the section does not provide, and Section 7.1 states `ship`'s contract over what it
drives. What the narrow reading would have cost is recorded rather than left implicit — Section
5.6's paragraph and Section 13.1's row would both have to be weakened — and it was **not
unreasonable**: it is what Sections 5.5 and 8.2 literally describe, both enumerating a two-element
token, so this decision changes those sentences rather than correcting a misreading. Section 8.1's
opacity paragraph, read on the issue as support for the narrow reading, argues the engine will not
**publish** a spelling, which cuts the other way; what it still argues against is a token whose
*size* grows with the graph. The token carries three fields: the point, the count, and **the
sequence's own `run_op` result the chain descends from** — decision 0143's root — where the point is
not that dispatch itself. Two sharpenings, both 0143's doing. **It is a trigger, not a sequence
position**: under 0143 the transfer is a property of the trigger and the trigger has exactly one
position because the sequence tested it, so the position is derived — a token carrying a position
would owe the traversal schema Section 8.1 says an engine should not publish, while one carrying a
trigger owes the trigger vocabulary Section 5.1 and the registry already publish, and Section 5.4's
tail-replacement keeps it fixed-width. **It is the root, not "the trigger an edge replaced"**:
Section 12.2 routes `push:non_fast_forward` to `integrate` built in, so phrased over substitution
the field would be absent exactly where a resumed `integrate` needs it. And the trigger is spelled
by its **registry token** rather than by an ordinal into a generated enumeration, which after a
MINOR insert decodes into a different trigger, silently, from a record that still looks valid. The
`MUST NOT` over position-established state is untouched: a trigger is control-flow state of the same
kind as the count. Easy to miss: `conformance/vcsx/vocabulary.json`'s `resume_token` note restates
the two-element description **in its own words**, so it moves with the sections — decision 0132's
drift class — and the format revision is shared with decision 0142, separable in substance and not
in encoding: 0142 will plausibly land first, so both records now state the coupling rather than only
whichever is applied second.

## 0154 — The record grew three fields and the vector that enumerates it did not

**State:** Accepted
**Folder:** [decisions/0154-issue-record-drift/](decisions/0154-issue-record-drift/)

Issue #120, filed by the `symphony-rs` build. Section 12.2 fixes the maps a template may name whole
as "the `issue` object, whose members are the fields Section 4.1.1 defines, and `metadata`", Section
4.1.1 defines sixteen fields, and `conformance/vectors/prompt-rendering.json`'s
`iterate-issue-object` expects thirteen — the three absent being `assignees` (decision 0140),
`project` and `team` (decision 0148), both landing after decision 0135 authored the vector. **No
implementation satisfies both**: a build following Section 12.2 renders sixteen keys and fails the
vector, a build passing the vector withholds three fields from the template context, and the
reporter chose the latter and said why — turning a green vector red would make "red" mean both work
owed and a vector believed wrong, and those have to stay distinguishable. **The corpus is what
moves, and its own decision says so**: 0135's `Plan.md` requires that the vector's "`given.issue`
carries every Section 4.1.1 field and no other", so this is a done-condition the artifact stopped
meeting rather than a second rule to reconcile. **The half the issue does not ask for is `given`**,
which carried thirteen too. `conformance/README.md`'s harness contract is one line — "Invoke the
implementation's realization of `function` with `given`" — and a harness that maps the input into
its own record type and one that renders the decoded object verbatim disagree on this vector and on
no other, `iterate-issue-object` being the only one in the corpus that iterates the container rather
than naming fields by path; repairing `expect` alone would fix one harness and break the other. Both
halves now carry the sixteen fields, `branch_name` still null so a null-valued member stays pinned
and the three new ones populated so a context carrying `project` only where routing consumed it is
caught. **The subset reading is steelmanned and loses**: `project` and `team` entered as routing
keys with no evident use in a prompt, but strict variable checking makes a hidden field a
`template_render_error` and so a failed run attempt (Sections 5.5, 12.4) rather than a blank, and
the subset would owe a membership rule, a dispatch-preflight check, and a reason a template may read
adapter-owned `metadata` and not the name of the project the issue sits in — for no confidentiality
gain over fields already rendered. **The larger half is that nothing was going to catch this.** Two
decisions added three fields and neither re-derived the vector, because the cross-cutting sync rules
name Sections 6.4, 17 and 18 and the Conformance Statement template and nothing names the corpus.
`scripts/validate_spec_consistency.py` exists for that exact shape — "a specification sentence
enumerates something, a second artifact restates that enumeration, the two disagree, and nothing
notices because each artifact is complete against itself" — and missed it, its six checks reading
registries, templates and prose and never `conformance/vectors/`. Check 7 adds the corpus as the
third derived artifact, comparing three spellings of one set (the section's fields, the keys `given`
supplies, the keys `expect` renders) plus the ascending code-point order Section 12.2 fixes, and it
is table-driven in check 6's shape with **one row**: all twelve vector files were surveyed and one
carries an enumeration-shaped expectation, every other expecting a computed value and
`config-defaults.json` declaring unlisted paths unconstrained. A `CLAUDE.md` bullet in place of the
check was rejected on measured grounds — decision 0128 records three consecutive decisions missing a
Conformance Statement row that `CLAUDE.md` already demanded in writing — so the rule lives in the
script's docstring instead. No `SPEC.md` change, no token added, renamed or removed, and no
`Implementation-defined` or "MUST document" obligation, so no Conformance Statement row is owed.
Reconsider on a second enumeration-shaped vector, which pays for the table's shape; on Section 4.1.1
gaining a field an implementation must not put in a prompt, which reopens the subset question on a
ground today's fields do not supply; or on a harness contract fixing whether `given` is mapped into
an implementation's types or fed verbatim, which would make pinning `given` belt-and-braces rather
than the thing that makes the vector well-defined. Relates to 0128, 0135, 0140 and 0148. Accepted
and applied to `conformance/vectors/prompt-rendering.json`, `scripts/validate_spec_consistency.py`
and `conformance/README.md`.

## 0155 — The conditions that keep holding, and the repository nothing recorded

**State:** Accepted
**Folder:** [decisions/0155-standing-conditions/](decisions/0155-standing-conditions/)

Issue #121, filed by the `symphony-rs` build against `4d610da`: reconciliation's
stop-on-attribute-loss rule is stated in Section 11.2 — the **Linear adapter's** section — and
nowhere Section 8.5 Part B can be read from. Investigation widened it three ways. **The rule already
exists for two of the four attributes.** Section 5.3.1 requires an issue to satisfy
`tracker.required_labels` and `tracker.assignee` "to dispatch or continue", the only two such
clauses in the document and Core today, and Part B honours neither; routing never had one at all,
decision 0148 having stopped at making a mid-run move *visible* to the refresh without saying what
reconciliation does with it. **Three sites agree reconciliation is state-only**, and #121 reported
one of the three: Part B, Section 16.3's pseudocode, and Section 17.3's row "Issue state refresh by
ID returns minimal normalized issues", which actively licenses an adapter to return the least it
can. **Nothing ties a run to a repository**: Section 16.4's entry literal has eighteen members and
no repository, `repo_of(issue)` being computed twice there and stored nowhere, while Section 8.7
keys workspace, object store and concurrency by `(repository, issue)` and states that "A dispatch
grants an agent commit and pull-request authority in the repository it routes to" — so a mapping
edit under Section 6.2's live reload leaves a run holding that authority in a repository the mapping
no longer selects, and recomputing `repo_of` catches nothing, both sides evaluating the new mapping
and agreeing with each other. **The class rather than the instance**: 0140 and 0148 each added an
attribute, each extended Section 11.2, and neither touched Part B, because nothing tells a dispatch
gate it owes a continue arm. **The rule.** Section 8.2's conditions over the issue record are
*standing* — re-evaluated on every issue-state refresh for as long as the run is in flight — while
its four orchestrator-state conditions are dispatch-time only and **false by construction** for a
run already in flight, stated explicitly because an implementation that re-ran `should_dispatch`
wholesale would stop every run it checked; the `Todo` blocker rule stays dispatch-time only rather
than put an issue's dependency graph in every refresh, on every tick, for every running issue; and
field presence is a well-formedness test on what the adapter returned, not a stop. Routing is
standing too but stated in Section 8.7 over the **run**, an issue-side phrasing being circular at
dispatch, where routing is what selects the repository. Each rule keeps one home and Part B
*evaluates* them, the relationship it already has with `active_states` and `terminal_states`.
**The disposition** — stop the worker, release the claim, arm no retry, leave the workspace — has
its claim and retry halves forced by 0145, 0138 and 0144, and Section 8.5's "A site added later MUST
state which side of that partition it is on." makes saying so an obligation rather than a courtesy.
Cleanup is the open half, and Part B's existing split has **no stated rationale anywhere**: the
decision supplies one, that cleanup means the work is finished while a standing-condition loss is
reversible and may be an operator's own mapping typo, where deleting a workspace is an unrecoverable
answer to a mistake about to be corrected. The cost is named rather than absorbed — Section 9.1 keys
the workspace by `repo_key`, so a re-routed issue's workspace is a permanent orphan. **The state**:
the running entry gains a `repository` recorded at dispatch, and Section 14.4's remote-mode run
registry gains it too, or a reattached run has no left-hand side. `running` stays `Reconstructable`,
and **no `runtime_state_fields` token and no Conformance Statement row are owed** — both
enumerations are over Section 4.1.8's nine top-level fields and a member of a field's value is not a
field — which is a judgement rather than a checker result, since an extension row citing `8.x`
collapses to `8` and a green `scripts/validate_spec_consistency.py` answers a different question.
**The stop is operator-visible**, naming which condition failed: the two branches beside it are
self-explaining, and this one is not, the issue still being `In Progress` while the cause may be a
third party's label edit or an operator's mapping change. **The adapter obligation**: Section 11.2
gains a "Refresh completeness" block beside "Candidate enumeration" — the refresh returns the fields
the standing conditions read, for every id it was given, and a silently partial result is
non-conformant — and the Linear bullet loses its behavioural half and keeps the GraphQL specifics.
`fetch_issue_states_by_ids` **keeps its name**, the rename declined not on cost, the behavior corpus
not naming it at all, but on standing: renaming the adapter contract's surface is not settled in
passing by a decision whose subject is a missing branch. Left open and named rather than closed
quietly: genuine absence from the refresh, which the completeness MUST does not cover, and decision
0140's match-field trigger, unfired because routing's predicate compares against the run's recorded
repository rather than against a configured value — a different left-hand side. Reconsider on a
workspace-orphan sweep landing elsewhere in the document, on a tracker adapter that cannot
distinguish a missing field from an incomplete fetch, on genuine tracker-side deletion becoming a
live failure mode, or on a decision already touching Sections 11.1, 16.3 or 16.6 that can fold the
rename in. Relates to 0128, 0137, 0138, 0140, 0144, 0145, 0148. Accepted and applied to `SPEC.md`,
`conformance/vectors/standing-conditions.json` and `conformance/README.md`.
