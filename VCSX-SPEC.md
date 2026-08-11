# vcsx Engine Specification

Status: Draft v1 (language-agnostic)

Purpose: Specify `vcsx`, a reusable VCS-workflow engine that runs a repository-owned
`(trigger) → (action)` policy over version-control and forge operations behind two front-ends
(interactive `ship`/`land` and an embedded driver). This document is the **full engine specification**
that the contract surface (`VCSX-CONTRACT.md`) defers to: it defines the invocation protocol, the
field-level `repo.policy.toml` schema, the plugin API, the concrete reason-token registry, and the
reference algorithms. It is language-agnostic and names no implementation language normatively.

## Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, and
`OPTIONAL` in this document are to be interpreted as described in RFC 2119.

`Implementation-defined` means the behavior is part of the implementation contract, but this
specification does not prescribe one universal policy. Implementations MUST document the selected
behavior.

## 1. Overview

### 1.1 What vcsx Is

`vcsx` is an engine that automates a repository's Way of Working over version control: it runs
version-control and forge operations (commit, integrate, push, pull request, merge) and, around each,
evaluates a repository-owned policy that decides what happens next. The policy is one
`(trigger) → (action)` machine (Section 5) read from `repo.policy.toml` (Section 6). The engine ships
no Way of Working of its own — no commit convention, message format, hygiene rule, or merge policy;
it provides the operations, the policy machine, and the seams, and the repository provides the policy.

`vcsx` is an independent deliverable, consumed as a pinned tool and usable without any particular
consumer. It exposes two front-ends over one policy-graph executor:

- the interactive front-end, entered through `ship` and `land`;
- an embedded driver, which invokes the same executor programmatically and binds escalation to its own
  resolver (Section 7.3).

### 1.2 Relationship to the Contract Surface

`VCSX-CONTRACT.md` is the **surface** of this engine — the names and surface semantics that an
embedding consumer (for example the Symphony service) references so its own specification need not
restate the engine's schema. This document is the surface's own deferral target: everything
`VCSX-CONTRACT.md` §11 marks deferred is defined here. The two documents MUST keep identical names for
every shared token; Section 14 states the alignment rule. Where the surface and this document appear to
conflict on a *name*, the surface governs until reconciled; where they conflict on *schema or
algorithm*, this document governs.

### 1.3 Relationship to Consumers

`vcsx` is driven by a consumer that owns credentials and (when applicable) the agent boundary. A
consumer may be a human at an interactive prompt or an automation service. `vcsx` itself:

- holds no long-lived credentials of its own; the consumer supplies credentials to the forge/VCS
  plugins for the duration of an invocation (Section 9), or runs the engine in a context that already
  holds them.
- performs no repository *provisioning* (initial clone / object-store fetch). The engine operates on an
  already-provisioned worktree; provisioning is the consumer's responsibility.
- enforces no agent-secret boundary. When a consumer runs the engine on behalf of a sandboxed,
  credential-less agent, the consumer instantiates that boundary and mediates the engine's
  credentialed operations; `vcsx` distinguishes host-side from in-sandbox execution (Section 3.2) so a
  consumer can split a policy across such a boundary, but the boundary itself is the consumer's.

## 2. Goals and Non-Goals

### 2.1 Goals

- Run version-control and forge operations behind one policy-graph executor with deterministic,
  most-specific-wins matching and no silent drops.
- Let a repository express its whole Way of Working in one file (`repo.policy.toml`), consumed
  identically by the interactive and embedded front-ends.
- Keep the engine format-neutral: message formulation, hygiene, and merge policy are repository
  configuration and hooks, never engine built-ins.
- Provide a stable invocation contract (structured results, proto classes, exit codes, versioning) so
  a consumer can branch on outcomes without enumerating every reason token.
- Provide a plugin layer so the same policy runs across code hosts (for example GitHub, Forgejo) and
  checkout modes (for example git, jj) without policy changes.

### 2.2 Non-Goals

- Repository provisioning (clone / object-store fetch) and credential storage — the consumer's.
- Any agent-sandbox or secret-isolation mechanism — the consumer's.
- Prescribing a commit convention, message format, content-hygiene rule, or branch-protection policy —
  repository-owned Way of Working.
- A general-purpose workflow engine beyond the VCS/forge operation domain.

## 3. Architecture

### 3.1 Components

1. `Policy-Graph Executor`
   - Evaluates the action-policy machine (Section 5) against operation results and lifecycle positions,
     and dispatches actions. It is the single component both front-ends run.

2. `Front-Ends`
   - `ship` and `land` (interactive; Section 7) and the embedded-driver contract (Section 7.3). Each
     differs only in initiator and in how `escalate` binds (Section 5.5).

3. `Operation Layer`
   - The named operations (Section 4), each realized through the plugin layer and returning a typed
     result.

4. `Plugin Layer` (Section 9)
   - A `VCS backend` (git, jj, …) and a `Forge backend` (GitHub, Forgejo, …), each advertising a static
     capability descriptor. The policy is written against neutral operations; the plugin selects the
     backend.

5. `Policy Loader` (Section 6)
   - Reads and validates `repo.policy.toml` (with `vcsx.toml` merged in) and resolves each part from the
     execution context the consumer provides (Section 3.2).

6. `Scanner` and `Message Formulator` (Section 10)
   - The content-scan seam (`scan-content` at `before:commit`) and the composition/transform seams for
     commit, pull-request, and squash messages.

### 3.2 Execution Contexts (Trust)

The engine distinguishes two execution contexts, so a consumer that runs an agent inside a sandbox can
split one policy across the boundary:

- **Host-side** — operations and hooks that touch the remote or hold credentials (integrate, push,
  pull, create_pr, merge, host-side hooks). A consumer sources host-side policy from a trusted
  revision (for example a protected base branch) so an untrusted worktree cannot alter it.
- **In-sandbox** — operations and hooks that run in the working tree without credentials (the
  `before:commit` gate/scan, in-sandbox hooks). A consumer sources these from the worktree.

`vcsx` labels each policy edge and hook with its context (Section 6) but does not itself enforce the
sourcing rule; the consumer sources config by trust and mediates host-side operations. The engine
guarantees only that an edge declared in-sandbox never receives credentials.

### 3.3 Checkout Modes

The `VCS backend` detects and adapts to the checkout mode; policy is written mode-neutrally. At least:

- `git` — a plain git checkout.
- `jj` — a jj checkout, including a jj checkout colocated on git storage and a jj secondary workspace
  that has no colocated git storage. In a secondary workspace the backend derives the remote slug and
  branch from jj rather than from a colocated git remote.

The mode is reported by the `status` operation (Section 4.1) and is `Implementation-defined` in its
detection mechanism; the backend MUST document how it detects the mode.

## 4. Operations and the Operation Model

### 4.1 Operation Set

Operations are the unit `run_op` runs (Section 5.2). Each is realized through the plugin layer and
returns a typed result (Section 4.2). Read-only operations carry no lifecycle position.

- `status` — inspect working state. Outputs: `mode` (Section 3.3), `branch`, `dirty`, `conflicted`,
  `ahead`/`behind` versus the resolved base (Section 6.4), and the pull-request state when a forge
  is configured (number and open/closed/merged). Where the checkout holds no copy of the resolved
  base, `ahead`/`behind` are null and a `base_absent` output reports it; the operation still
  completes, because an inspection that cannot see the base states that rather than failing. An
  output the operation could not determine is reported the same way and means something else: the
  field is null and a `<field>_unavailable` output reports it — `pr_state_unavailable` where a
  configured forge could not be asked (Section 9.2). `base_absent` states what the checkout holds
  and `<field>_unavailable` states that the read did not establish it, which is the distinction
  Section 4.3 draws between a thing that is absent and a thing that is unavailable; a read reports
  no determinate value it did not establish. Read-only.
- `diff` — the branch delta against the resolved base. Read-only.
- `commit` — create a commit from the working tree, gated at `before:commit` (Section 10.1). The
  operation captures the working tree in full: every change the VCS does not ignore, including
  content the VCS has not yet recorded. The engine defines no staging operation and no way to commit
  a subset, so nothing selects the commit's content out of band.
- `integrate` — bring the resolved base into the work branch (a merge/update-branch), preserving
  recorded conflict resolutions where the backend supports them. The base is the branch as the
  configured remote holds it (Sections 6.2, 6.4), acquired rather than read from the checkout's
  copy. Gated at no fixed position; typically run in response to `push:non_fast_forward`.
- `push` — push the work branch to the remote with the refspec pinned to the work branch. Where a
  forge is configured, the operation first reads the work branch's pull-request state (Section 9.2
  `pr_state`) and refuses a push over a CLOSED/MERGED one (`push:pr_closed`). A state it could not
  determine is not the absence of a pull request: the operation does not push and reports
  `push:failed` (Sections 4.3, 9.2). Gated at `before:push`.
- `create_pr` — create or update the one pull request for the work branch against the resolved base,
  composing its title and body (Section 10.2). Gated at `before:create_pr`.
- `merge` — merge the pull request using the configured strategy (Section 6.8). Gated at
  `before:merge`; a squash strategy applies the `pr_to_squash` transform (Section 10.3).
- `pull` — update the local work branch from its remote counterpart, preserving the commits already on
  the branch: the counterpart is merged in, and no commit on the branch is rewritten, dropped, or
  re-parented (Section 11). `pull:conflict` is therefore a merge conflict, which the caller resolves and
  `commit` finalizes; the operation set has no step that resumes a sequential replay. Where the remote
  carries no counterpart the operation is a benign no-op and reports `pull:ok`: the work branch is
  engine-derived and need not exist on the remote before the first push (Sections 6.2, 6.3). An
  acquisition the engine could not complete is not that no-op and reports `pull:failed`
  (Sections 4.3, 9.1).

An engine MAY define additional operations and their `before:<op>` positions; the operations above are
the required set and the four positions `before:commit`, `before:push`, `before:create_pr`,
`before:merge` are the required lifecycle positions.

A gated operation's position runs as part of dispatching it. The engine runs `before:<op>` whenever
`<op>` is dispatched — by a front-end sequence (Sections 12.2, 12.3), by a `[policy]` `run_op` edge
(Section 5.2), or by a retry — so what reached the operation does not decide whether the operation is
gated. Gating is a property of the operation, as the entries above state it, rather than a step a
caller takes around it: Section 6.6 surfaces a block as the gated operation's own reason and Section
13.1 requires that surfacing at every gated operation, neither of which a caller could guarantee for a
dispatch it does not make. An operation gated at no fixed position — `integrate` and `pull` — enters
none wherever it is dispatched.

Note: a position runs where its operation runs and nowhere else. A `ship` over a working tree the
dirtiness guard reads as clean dispatches no `commit` (Section 12.2) and so enters no `before:commit`.
A position gates an operation, and where none is dispatched there is nothing to gate; a repository that
wants a unit to run whether or not a commit follows binds it to a result trigger rather than to a gate
(Section 5.1). What a unit could observe at the position is also nothing: a `before:commit` unit
inspects the working tree it runs in (Sections 6.6, 10.4), and a clean tree carries nothing for it to
find.

Note: the operations that reach the remote are exactly those Section 3.2 places host-side — among
the version-control operations, `integrate`, `push` and `pull`. `status` and `diff` are read-only
and report against the base ref the checkout already holds (Section 6.4), so their `ahead`/`behind`
counts and their delta MAY be stale where the remote has moved. The asymmetry follows from the trust
split rather than being an omission: acquiring the base is a host-side act, and marking a read-only
operation host-side would deny it to a consumer running the engine in-sandbox without credentials
(Section 3.2). A caller that needs current figures runs `integrate` first.

### 4.2 Operation Result Envelope and Proto Classes

Every operation completes with a typed result of the form `<op>:<reason>`. Every reason carries a proto
**outcome class** — one of `done`, `needs_caller`, `error` — which is part of the public contract
because policy branches on it through the `#class` fallback (Section 5.3):

- `done` — the operation reached its intended effect (including a benign no-op).
- `needs_caller` — the operation cannot proceed without a decision or action from the caller (the
  agent, the human, or the driver); it is not a failure of the engine.
- `error` — the operation failed.

A result also carries structured `outputs` (operation-specific; Section 8.2) and a human-readable
`message`.

### 4.3 Reason-Token Registry

The registry below is the concrete per-operation reason set and each reason's proto class. Consumers
SHOULD branch on the **class** rather than enumerate reasons; new reasons MAY be added in a compatible
release (Section 8.5) and existing consumers absorb them through the `#class` fallback. An engine MUST
document any reason it adds beyond this registry and MUST NOT change a listed reason's class within a
major version.

Three reasons are **universal**, carried in the table with `(any)` in place of an operation and listed
once rather than repeated per operation: `failed` and `unsupported` are defined for every operation,
and `blocked` for every operation gated at a lifecycle position (Section 4.1).

| Operation | Reason | Class | Meaning |
|-----------|--------|-------|---------|
| `(any)` | `failed` | `error` | The operation failed, including when a `before:<op>` hook blocked it with an `error` result (Section 6.6). |
| `(any gated)` | `blocked` | `needs_caller` | A `before:<op>` gate or scan blocked the operation (Section 6.6). |
| `(any)` | `unsupported` | `error` | The operation requires a plugin capability the backend does not declare (Section 9.3). |
| `commit` | `ok` | `done` | A commit was created. |
| `commit` | `nothing_to_commit` | `done` | No changes to commit; benign no-op. |
| `commit` | `identity_missing` | `needs_caller` | No caller-supplied commit identity is available (Sections 8.6, 10.1). |
| `integrate` | `ok` | `done` | The base was integrated. |
| `integrate` | `up_to_date` | `done` | Already current; no-op. |
| `integrate` | `merge_conflicts` | `needs_caller` | Integration stopped on conflicts to resolve. |
| `integrate` | `base_unresolved` | `error` | The base could not be resolved (Section 6.4). |
| `integrate` | `base_unavailable` | `error` | The base could not be acquired from the remote (Section 9.1 `fetch_base`). |
| `integrate` | `identity_missing` | `needs_caller` | No caller-supplied commit identity is available for the merge commit (Sections 8.6, 10.1). |
| `push` | `ok` | `done` | The work branch was pushed. |
| `push` | `up_to_date` | `done` | Remote already current; no-op. |
| `push` | `non_fast_forward` | `needs_caller` | Remote moved; integrate then retry. |
| `push` | `pr_closed` | `needs_caller` | The pull request is CLOSED/MERGED; refuse to push over it. |
| `push` | `rejected` | `error` | The remote rejected the push. |
| `create_pr` | `created` | `done` | A pull request was created. |
| `create_pr` | `updated` | `done` | The existing pull request was updated. |
| `create_pr` | `base_mismatch` | `error` | An existing pull request targets a different base. |
| `create_pr` | `conflict` | `needs_caller` | The pull request could not be created/updated cleanly. |
| `merge` | `ok` | `done` | The pull request was merged. |
| `merge` | `not_open` | `needs_caller` | The pull request is not open. |
| `merge` | `checks_pending` | `needs_caller` | Required checks have not completed. |
| `merge` | `checks_failed` | `error` | Required checks failed. |
| `merge` | `conflict` | `needs_caller` | The merge would conflict. |
| `merge` | `head_moved` | `needs_caller` | The pull request's head advanced after it was read; re-read then retry. |
| `merge` | `rejected` | `error` | Branch protection or forge policy refused the merge. |
| `pull` | `ok` | `done` | The local branch was updated. |
| `pull` | `conflict` | `needs_caller` | The merge of the remote counterpart stopped on conflicts. |
| `pull` | `identity_missing` | `needs_caller` | No caller-supplied commit identity is available for the merge commit (Sections 8.6, 10.1). |
| `status` / `diff` | `ok` | `done` | The read completed. |
| `diff` | `base_unavailable` | `error` | The checkout holds no copy of the resolved base, so no delta can be produced (Section 6.4). |

`base_unresolved` and `base_unavailable` are one word apart and name different failures, because base
resolution has two steps (Section 6.4) and each reason reports the one it stopped at.
**Unresolved is not knowing which branch** — the configured strategy selected none.
**Unavailable is not having its commit** — the branch it selected has no copy in the checkout, or
acquiring it failed. `status` reports the same absence in its outputs rather than as a reason
(Section 4.1), because a read that cannot see the base can still report everything else.

`pull` carries no counterpart reason of its own, and that follows from the operation rather than being
an omission. The conditions that leave `fetch_base` without a base ref are failures whatever their
cause, so one reason covers them. The conditions that leave `fetch_counterpart` without a counterpart
ref are a benign absence and a failure, and a reason carries one proto class (Sections 4.2, 8.5), so no
single reason can carry both; the acquiring capability distinguishes them instead (Section 9.1) and
each takes the reason it already has — an absent counterpart is `pull:ok`, a failed acquisition is the
universal `failed`. **A base is required to exist and a work branch's counterpart is not**, so what is
one condition for `integrate` is two for `pull`.

`merge:head_moved` and `push:non_fast_forward` name one condition on two operations — what was to be
written to moved between the decision to write and the write — and both are `needs_caller` with the
recovery in the gloss. Neither is a conflict: the branches merge cleanly, and a caller routed to
`merge:conflict` is sent to resolve something that does not exist. Neither is a refusal:
`merge:rejected` names branch protection or forge policy, and reporting a moved head under it sends
an operator to read a rule nobody wrote. The two differ only in the recovery each gloss names,
because a remote that moved requires an `integrate` before the write can succeed while a head that
moved requires only that the pull request be read again — which is why one routes through another
operation (Section 12.2) and the other re-dispatches its own, which re-runs its position
(Sections 4.1, 12.3). The
condition is not reported as the universal `failed` for the same reason `push:non_fast_forward` is
not: `failed` is class `error` and this is a state a caller acts on, so no wider token carries it
(Sections 4.2, 8.5).

`identity_missing` and Section 8.6's `identity_invalid` name one condition at two points, and the
first dispatch is the boundary between them. An entry the identity precondition covers is refused
before the policy runs and never reaches `identity_missing`; an entry it does not cover MAY reach an
operation that writes a commit through a `run_op` edge (Section 5.2), and that operation reports
`identity_missing` — a result the machine routes like any other, so a repository MAY bind it and the
built-in `needs_caller` default escalates it (Sections 5.3, 5.4). Only absence reaches a dispatch: a
supplied identity is judged for shape before the policy runs whatever the entry (Section 8.6), so a
malformed one is `identity_invalid` in every invocation.

Every operation therefore has at least one `done` reason and at least one `error` reason, so an
`error`-class result is expressible for every operation including the read-only ones; every gated
operation additionally has a `needs_caller` reason. `integrate` and `pull` are gated at no fixed
position and `status` and `diff` carry no lifecycle position (Section 4.1), so none of the four
carries `blocked`. An engine that defines an additional operation, and a `before:<op>` position for
it, defines the same universal reasons for that operation.

## 5. The Action-Policy Machine

### 5.1 Triggers

A trigger is one of:

- **Lifecycle positions** around an operation: `before:commit`, `before:push`, `before:create_pr`,
  `before:merge` (and any engine-defined `before:<op>`). A lifecycle position is matched exactly; it
  has no class form.
- **Typed operation results** `<op>:<reason>` (Section 4.3).
- **Signals** raised by the consumer, including agent milestone signals (`ready-for-review`, `blocked`,
  `done`) and **task-state events** (`tasks:all_closed`, `task:#needs_help`) when the consumer runs the
  task model (Section 7.3). A signal is matched exactly and has no class form: the consumer raises the
  token the policy binds. The `#` in `task:#needs_help` names a *condition across tasks* rather than a
  proto class — the consumer raises it when any task needs human help, not one event per task — so it
  is an ordinary signal token, not a fallback rung.

### 5.2 Actions

An action is one of:

- `run_op(op, args?)` — run an operation (Section 4). Its result is itself a trigger, so a policy is a
  graph, not a flat list; the number of dispatches in one invocation is bounded (Section 5.6).
  Dispatching a gated operation runs its `before:<op>` position first (Sections 4.1, 6.6), so an
  operation reached through an edge is gated exactly as one a front-end sequence dispatches.
- `run(hook, context)` — run a repository hook (Section 6.6) in the declared execution context
  (Section 3.2).
- `escalate(reason)` — raise a need whose resolver the front-end binds (Section 5.5).
- `create_task(spec)` — create a task through the consumer's task model (Section 7.3); a no-op when the
  consumer runs no task model.
- `set_state(target)` — apply a workflow-state transition through the consumer (Section 6.7).
- `notify(channel, payload)` — emit a notification through the consumer; a no-op when the consumer
  cannot deliver it.
- `park` — stop the flow and hold for intervention without failing it. The invocation ends at
  `needs_caller` carrying the `intervention` need (Sections 8.2, 8.4).
- `fail(reason)` — end the flow as failed.

`create_task`, `set_state`, and `notify` are effected by the consumer, because they touch systems
(a task model, an issue tracker, a notification channel) outside the VCS/forge domain; the engine
emits the intent and the consumer performs it. `run_op` and `run` are the engine's own.

A consumer need not be able to effect every such action. A consumer may be a human at an interactive
prompt (Section 1.3), with no task model, no tracker binding, and no notification channel, so a policy
using these actions MUST behave predictably against a consumer that cannot perform them. Each action's
disposition is fixed:

- `create_task` and `notify` are benign no-ops. The engine MUST surface each such intent in the result
  envelope (Section 8.2) rather than drop it, on the same principle that forbids silently dropping an
  unmatched operation outcome (Section 5.4): an intent the engine emitted and no consumer performed is
  reported, so a policy that degrades against a lesser consumer degrades visibly.
- `set_state` is a configuration error, caught before the policy runs (Section 6.10), because a
  workflow state that never advances strands the flow rather than merely losing information.

This is not a second point of front-end divergence. The engine's behavior is identical in either
front-end — it emits the intent and records whether a consumer performed it — and only the consumer's
capability varies; `escalate` remains the single point at which the engine itself branches
(Section 5.5).

### 5.3 Matching Algorithm and the `#class` Fallback

Given a trigger, the executor selects at most one edge by most-specific-wins over a fallback ladder:

- For a **lifecycle position** `before:X`: match an edge keyed exactly `before:X`. No class fallback.
- For a **typed result** `op:reason`: try, in order, `op:reason` → `op:#class` → `#class` → a built-in
  default, where `#class` is the reason's proto class (Section 4.2). Example ladder:
  `push:non_fast_forward` → `push:#needs_caller` → `#needs_caller` → default.
- For a **signal / task-state event** `s`: match an edge keyed exactly `s`, then the unmatched-signal
  default (Section 5.4). No class fallback — a signal carries no proto class, because it is a
  consumer-raised condition rather than an operation result (Section 5.1).

The `#class` fallback lets a policy branch on the three stable classes without enumerating every
reason, so a new reason token added in a compatible release routes to an existing class edge. It
applies to typed operation results alone: those are the only triggers with a proto class to fall back
on.

### 5.4 Unmatched Policy and Determinism

- An unmatched **lifecycle position** is a benign no-op: nothing runs at the position and the operation
  proceeds. A position is an offered interposition point, not a result requiring disposition — the
  required positions (Section 4.1) are available to every policy and most policies bind only some, so
  leaving one unbound is the ordinary case rather than an omission. This is also why a position has no
  class fallback (Section 5.3): there is no outcome to classify.
- An unmatched **signal** (including a task-state event) is a benign no-op.
- An unmatched **operation outcome** MUST be fail-safe: the executor parks or fails the flow with the
  operation's proto reason surfaced. It MUST NOT be silently dropped, because a dropped operation
  outcome would strand a flow. The built-in default for the `error` class is `fail`; for
  `needs_caller`, `escalate`; for `done` with no edge, continue.
- The policy graph MUST be deterministic: at most one edge per `(from-context, trigger)` key, where a
  duplicate is a configuration error (Section 6.10). "from-context" allows a repository to give the same
  trigger different edges at different lifecycle points where the engine models them (for example a
  transition graph keyed on a workflow-state `from`, Section 6.7); absent such a model the key is the
  trigger alone.
- An edge that carries no `from` is **unscoped**: it is a candidate in every from-context, including
  none. Scoping is opt-in per edge, so a repository that scopes some edges does not thereby scope
  the rest, and adding its first transition edge changes what one trigger does in one context rather
  than silencing every edge that carries no `from`. This is what keeps the same `repo.policy.toml`
  yielding one operation flow under a front-end that supplies a from-context and one that does not
  (Section 13.1).
- Where one trigger key has both an edge scoped to the current from-context and an unscoped edge,
  the scoped edge is selected. The two are not a duplicate `(from, on)` — they are distinct keys —
  but a default and its override in one context. The from-context is a tiebreak within one key
  rather than an outer loop: the ladder (Section 5.3) selects the key first, so an unscoped edge on
  `push:non_fast_forward` is selected over an edge scoped to the current context on
  `push:#needs_caller`. Naming a context does not make a broader trigger the more specific match.

### 5.5 Escalation Binding

`escalate(reason)` names a need and the front-end binds the resolver:

- Interactive (`ship`/`land`): `escalate` returns a `needs_caller` result (Section 8.2) to the human
  caller, carrying the escalation payload (Section 8.4). The human resolves and re-invokes.
- Embedded driver: the driver binds `escalate` to its own resolver — for example creating an
  agent-assigned task (Section 7.3) — and resumes the flow when the need is met.

Because both front-ends run the same executor over the same policy, `escalate` is the single point at
which their behavior legitimately differs.

`park` (Section 5.2) reaches the same `needs_caller` result and carries a need of its own, so the
envelope's escalation rule holds for it without exception (Section 8.2). It is not a second point of
divergence, because it names no resolver to bind: `intervention` names a hold rather than a request
(Section 8.4), so both front-ends surface it and neither resumes the flow. That is what separates the
two actions: an `escalate` need is one a front-end is expected to meet and `intervention` is one it is
not, and the difference is readable in the result rather than only in the policy that produced it.

### 5.6 Flow Bound and Termination

A policy is a graph rather than a flat list (Section 5.2), so an invocation traverses it instead of
walking a fixed sequence, and nothing in the graph itself guarantees the traversal ends. `run_op` is the
only action whose result re-enters the machine:

- `run` does not re-enter on its own. A `before:*` hook's block surfaces as the gated operation's own
  reason — `<op>:blocked` or `<op>:failed` (Section 6.6) — so it reaches the machine through that
  operation, and an `after`/result-triggered hook does not block.
- `create_task`, `set_state` and `notify` are consumer-effected intents, emitted once (Section 5.2).
- `escalate`, `park` and `fail` end the flow.

Every non-terminating flow is therefore an unbounded sequence of `run_op` dispatches, and a bound on
that count bounds every loop the schema can express — including one a lifecycle position introduces,
where an edge on `before:push` dispatches `integrate` and the retried `push` re-gates the position. A
`run_op` edge at `before:<op>` naming that same operation is such a loop, the dispatch running the
position that dispatches it (Section 4.1), and the bound ends it as it ends any other.

A conforming executor MUST bound one invocation's flow by a count of `run_op` dispatches. The bound's
value is `Implementation-defined` and MUST be documented (Section 13.3); it MUST admit at least 64
dispatches, and an engine that lets a deployment configure it MUST hold the configured value to the same
floor. The floor's exact value is arbitrary; that it is fixed is not, because it is what keeps two
engines with different bounds in agreement on every policy that terminates within it.

The bound is a count, not a cycle detector. A repeated `(trigger, edge)` pair is ordinary rather
than pathological: `push:non_fast_forward → integrate → push` is the built-in routing (Section
12.2), and a base branch that moved twice produces it twice; `merge:head_moved → before:merge →
merge` is the other (Section 12.3), and a pull request pushed to twice produces that twice. An
executor that refused a graph containing a cycle would refuse that routing, and one that stopped at
a repeated edge would abort a correct flow that was about to converge. What separates a converging
flow from a looping one is how many operations it takes, not whether it revisits an edge.

A flow that reaches the bound ends the invocation at `needs_caller` carrying the `flow_exhausted` need
(Sections 8.2, 8.4). The pending `run_op` is not dispatched; the operations already run stand. Like a
park this is a hold rather than a request: no automated party can move the flow, so no front-end
resolves it (Section 8.4), and it introduces no point of front-end divergence (Section 5.5) — both
front-ends do the same thing with it. It carries a need of its own because the policy did not ask for
the hold; an exhausted flow says either that the graph does not converge or that the remote is moving
faster than the engine can follow, neither of which a park would tell the caller.

An engine MAY impose further bounds on a running flow, a wall-clock deadline for example. A flow stopped
by any bound the engine imposes reaches the same result, so the envelope does not reveal which one
fired, and the engine MUST document each bound it imposes (Section 13.3).

## 6. `repo.policy.toml` Schema

### 6.1 File Discovery and `vcsx.toml` Merge

- `repo.policy.toml` is the repository-owned Way-of-Working file. Its path is resolved relative to the
  repository root; the discovery precedence (explicit override, then the repository default) is
  `Implementation-defined` and MUST be documented.
- An engine-native `vcsx.toml`, when present, is merged into the same surface; `repo.policy.toml` keys
  take precedence on conflict. A consumer MAY present the merged surface as one document.
- A discovered file that does not parse yields no policy to validate. The engine reads no policy
  from it and refuses to run, reporting a configuration error (Section 6.10).
- Unknown keys SHOULD be ignored for forward compatibility.

### 6.2 `[engine]`

- `version_floor` (string) — the minimum engine version the policy requires, stated as a
  `MAJOR.MINOR` version (Section 8.5). A value that is not one is a configuration error
  (Section 6.10) rather than a floor the engine compares.
- `vcs` (string) — the VCS backend selector (for example `git`, `jj`); MAY be `auto` for detection
  (Section 3.3).
- `forge` (string) — the forge backend selector (for example `github`, `forgejo`).
- `remote` (string, OPTIONAL) — the name of the remote the operations that touch one act against
  (`integrate`, `push`, `pull`; Sections 3.2, 9.1). It also names which of the checkout's copies of the
  base a read resolves against, which acquires nothing (Section 6.4).
  - Default: unset — the backend's default remote for the checkout mode, which is
    `Implementation-defined` and MUST be documented (Section 13.3).

The backend selection is read here in both standalone and embedded use. An embedding consumer supplies
the *credential* the selected backend uses (Section 9), not the selection — so which code host a
repository targets is repository-owned, while the credential for it is the consumer's.

The remote is repository-owned on the same reasoning: a repository that publishes its work branch to
a fork, or that carries more than one remote, states which one here rather than leaving two
conforming engines to push the same branch to different places. The engine resolves the remote once
per invocation and supplies it to each capability that takes one (Section 9.1); a backend does not
read it from the policy itself, and does not infer it from the work branch's own upstream binding,
which need not exist — the work branch is engine-derived (Section 6.3) and MAY be absent from the
checkout at the first push.

The engine performs no repository provisioning (Section 1.3), so the named remote is one the
provisioned checkout already carries. A name the checkout does not carry is not a configuration
error — Section 6.10's validation reads the policy alone, and whether a remote exists is a property
of the checkout — so it surfaces at first use as the operation's `failed` reason (Section 4.3).

### 6.3 `[scope]`

- `branch_pattern` (string, OPTIONAL) — the work-branch name pattern (for example
  `symphony/<identifier>` or `feature/<slug>`). The engine derives the work branch from this pattern
  and the caller-supplied identity; it does not accept an arbitrary caller-named branch. Only the
  branch *name* is configured here; any scope *enforcement* (restricting which branch may be pushed)
  is the consumer's, and the engine pins the push refspec to the derived work branch regardless.
  - Default: unset — the work branch is the checkout's current branch (Section 9.1
    `current_branch`). A checkout with no current branch then has no work branch to derive, which
    Section 8.6 reports.

### 6.4 `[base]` and Base Resolution

- `branch` (string) — the base branch the pull request targets and `integrate` pulls from.
- `resolve` (string, OPTIONAL) — a base-resolution strategy when a single `branch` is insufficient:
  - `fixed` (Default) — `branch` is the base.
  - `by_prefix` — the base is selected from a table mapping work-branch-name prefixes to base branches
    (longest-prefix-wins, with a required empty-prefix default). This models track-aware bases without
    naming a specific deployment's mapping.
- `prefixes` (table, OPTIONAL) — the prefix→base map used when `resolve = by_prefix`. A missing or
  malformed map is a configuration error (Section 6.10); the engine surfaces `integrate:base_unresolved`
  / `create_pr:base_mismatch` rather than guessing.

Resolving the base produces two values, because the two plugin layers need different things from it:

- the base **branch** — a name, which the pull-request operations take (Section 9.2);
- the base **ref** — a handle to the commit the checkout holds for that branch, which the
  version-control capabilities take (Section 9.1 `resolve_base_ref`).

The engine holds a base ref opaque, as it holds the commit identity opaque (Section 10.1): it resolves
one, supplies it to the capabilities that take one, and does not interpret it. A ref's validity ends
when an operation moves what it names, so the engine resolves again rather than reusing one across a
`fetch_base` or a `merge_base` (Section 9.1). Resolving a ref reads the checkout and acquires nothing;
where the checkout holds no copy of the selected branch, resolution answers that it holds none, which
`diff` reports as `base_unavailable` and `status` as a `base_absent` output (Sections 4.1, 4.3).

Naming the ref rather than the branch alone is what makes a read deterministic. A checkout MAY hold
several copies of one base branch — its own local branch, and a remote-tracking copy for each remote it
carries — which are the same commit only until one of them is updated. Resolution selects the copy
belonging to the resolved remote (Section 6.2), so `ahead_behind` and `diff` report against the base
`integrate` would bring in rather than against whichever copy a backend preferred.

Base resolution is configuration, not a hook. An operation reads the resolved base; it never accepts a
base from untrusted content.

### 6.5 `[policy]` Edges

The action-policy machine (Section 5) is expressed as a table of edges. Each edge binds a trigger to an
action, with an OPTIONAL `context` (`host_side` or `in_sandbox`, Section 3.2; defaulted per the
action) and OPTIONAL `from` (a workflow-state name, used only by transition edges, Section 6.7). An
edge omitting `from` is unscoped: it is a candidate in every from-context, and an edge scoped to the
current context takes precedence over it for the same trigger (Section 5.4).

```toml
[[policy.edge]]
on = "push:non_fast_forward"   # trigger: lifecycle position | op:reason | op:#class | #class | signal
do = "run_op"                  # action (Section 5.2)
op = "integrate"               # action argument
# then the resulting integrate:* outcome re-enters the machine

[[policy.edge]]
on = "before:commit"
do = "run"                     # run a hook
hook = "scan-content"          # a hook name (Section 6.6)
context = "in_sandbox"

[[policy.edge]]
on = "#error"                  # class fallback: any error with no more-specific edge
do = "escalate"
```

An edge's `on` MUST be a trigger the engine recognizes (a known lifecycle position, an `op:reason` /
`op:#class` / `#class` form over a known operation, or a known signal). A duplicate `(from, on)` is a
configuration error (Section 5.4). An edge MUST also carry the arguments the action its `do` names
needs in order to be dispatched — `op` for `run_op`, `hook` for `run` — and an edge that omits one
is a configuration error (Section 6.10).

### 6.6 `[hooks]`

A hook is a named unit `run` invokes. Each hook declares its execution context (Section 3.2):

```toml
[hooks.scan-content]
context = "in_sandbox"         # runs in the worktree, no credentials
run = "..."                    # engine-invoked unit; its form is Implementation-defined

[hooks.notify-release]
context = "host_side"          # runs with host access; MAY receive repo-internal integrity values
run = "..."
```

- A `before:*` (host-side or in-sandbox) hook MAY block by returning a `needs_caller` or `error` result
  with a stable reason. The engine surfaces the block as the gated operation's own reason, preserving
  the class: a `needs_caller` result surfaces as `<op>:blocked` and an `error` result as
  `<op>:failed`. Both are defined for every gated operation, including a `before:<op>` position an
  engine adds (Section 4.3), so the surfacing is defined at every position. The position runs wherever
  its operation is dispatched from (Section 4.1), so a block surfaces identically for a front-end
  sequence and for a `run_op` edge (Section 5.2).
- An `after`/result-triggered hook is best-effort and does not block.
- A host-side hook MAY receive repo-internal integrity values from the consumer's environment; an
  in-sandbox hook MUST NOT receive credentials or integrity values.

### 6.7 `tracker.transitions`

The workflow-state transition graph (`tracker.transitions`) is a set of `set_state` bindings keyed on a
`from` workflow-state name and a trigger:

```toml
[[tracker.transitions]]
from = "In Progress"
on   = "pull_request_opened"   # a consumer-supplied run outcome, or a milestone signal / op:reason
to   = "Human Review"          # set_state target
```

The graph is over neutral state names; mapping a state name to a tracker's representation is the
consumer's. An unmatched `(from, on)` transitions nothing (a benign no-op, Section 5.4). The graph MUST
be deterministic (at most one `to` per `(from, on)`).

### 6.8 `[messages]`

Message formulation is repository configuration; the engine bakes in no format (Section 10).

```toml
[messages.commit]
# identity (author/committer) is supplied by the consumer, distinct from content;
# the commit body is authored by the caller and validated at before:commit.

[messages.pr]
body_source = "auto"           # "auto" (compose) | "agent" (caller prose) | "template"
title_scan  = "strict"         # scan profile for the title
body_scan   = "relaxed"        # scan profile for the body (Section 10.4)

[messages.squash]
strategy   = "squash"          # merge strategy: "squash" | "merge" | "rebase"
transform  = "pr_to_squash"    # a repo-owned transform applied at before:merge (Section 10.3)
```

### 6.9 `[tasks]` and `[driver]`

When the consumer runs the OPTIONAL task model (Section 7.3), these tables configure it:

```toml
[tasks]
enabled        = true
write_through  = true          # materialize tasks into the tracker where the capability exists

[driver]
on  = "tasks:all_closed"       # the computed-completion trigger
run = "ship"                   # the front-end sequence completion runs
```

These tables are inert when the consumer runs no task model (for example the interactive front-end).

### 6.10 Validation

A policy is validated before use. Each configuration error carries a stable reason token, surfaced in
the result envelope (Section 8.2), so a caller can branch on the cause without parsing `message`:

| Condition | Reason |
|-----------|--------|
| A discovered `repo.policy.toml`, or a `vcsx.toml` merged into it, that does not parse (Section 6.1) | `malformed_policy` |
| A key whose value does not satisfy the constraints its section states — an `[engine] version_floor` that is not a `MAJOR.MINOR` version (Sections 6.2, 8.5), for example | `malformed_policy` |
| An edge whose action cannot be dispatched from the arguments it carries — a `run_op` with no `op`, a `run` with no `hook` (Sections 5.2, 6.5) | `malformed_policy` |
| An edge's `on` is not a trigger the engine recognizes (Section 6.5) | `unknown_trigger` |
| An edge's `do` is not a known action (Section 5.2) | `unknown_action` |
| A `run_op` names an operation the engine does not define (Section 4.1) | `unknown_operation` |
| A `run` names a hook the `[hooks]` table does not declare (Section 6.6) | `unknown_hook` |
| A duplicate `(from, on)` policy edge — non-determinism (Section 5.4) | `duplicate_edge` |
| A duplicate `(from, on)` transition (Section 6.7) | `duplicate_transition` |
| A `by_prefix` base resolution with no empty-prefix default, or a missing or malformed map (Section 6.4) | `base_unresolvable` |
| A `set_state`/transition binding without a consumer that can apply it (Section 5.2) | `set_state_unbound` |
| A policy requiring a capability no configured backend declares (Section 9.3) | `capability_unsupported` |
| A `version_floor` above the running engine version (Section 8.5) | `version_floor_unmet` |

The first three conditions are well-formedness failures and the rest are consistency failures, and
the order is not incidental: validation takes a document, and a policy that does not parse yields
none for the checks below it to run against. `malformed_policy` covers a well-formedness failure no
other condition in the table names; where another names the state — a missing or malformed
`prefixes` map is `base_unresolvable` (Section 6.4) — that condition's reason is reported.
Section 6.1's rule that an unknown key SHOULD be ignored for forward compatibility covers a key the
schema does not declare, not a declared key whose value the schema does not admit.

Two boundaries against neighbouring reasons follow. `version_floor_unmet` names a floor the engine
read and does not satisfy; a floor it cannot read is `malformed_policy`. The engine refuses either
way, running only where the floor is demonstrably satisfied (Section 8.5), but the two reasons name
different repairs — a newer engine, and a corrected file. `unknown_operation` and `unknown_hook`
likewise name an argument the engine resolved and did not recognize, while an argument that is
absent is `malformed_policy`; that condition is stated over the actions rather than per argument,
because `set_state` with no target has the same shape and no reason of its own.

Configuration reasons carry no proto class: a refused policy has no operation result to classify. They
are reported under the `usage_or_config` status (Section 8.2) rather than through the `#class` fallback,
which is why a new configuration reason does not need an existing class edge to absorb it. An engine
MUST document any configuration reason it adds beyond this registry (Section 13.3).

On a configuration error the engine refuses to run and returns a usage/config result (Section 8.3); it
does not run a partial policy. Where more than one condition holds, which reason is reported is
`Implementation-defined` and MUST be documented; an engine MAY report several.

## 7. Front-Ends

### 7.1 `ship`

`ship` drives the change from the current worktree up to and including opening or updating the pull
request, and **stops at the pull request** — it does not merge. Its sequence (Section 12.2) runs
`commit` (if the worktree is dirty), then `integrate`/`push` (routing `push:non_fast_forward` through
`integrate` and retry, per policy), then `create_pr`. Each step passes through its lifecycle position
and its result re-enters the machine, so repository policy governs the sequence.

### 7.2 `land`

`land` merges an already-open pull request. It runs `merge` at `before:merge`, applying the
configured strategy and, for a squash, the `pr_to_squash` transform (Section 10.3). `land`
**transforms** message content; it never authors a message. It refuses to merge a pull request that
is not open or whose required checks have not passed, surfacing the corresponding `merge:*` reason.
It merges the head it read: where the pull request's head advances between the read and the merge,
nothing is merged, and `land` re-reads and retries within the flow bound (Sections 5.6, 12.3).

### 7.3 The Embedded-Driver Contract

An embedded driver invokes the same executor programmatically. It:

- supplies the execution context (host-side vs in-sandbox sourcing, Section 3.2) and the credentials the
  plugins use;
- binds `escalate` to its own resolver (Section 5.5) — for example an automation service that turns an
  escalation into an agent-assigned task;
- MAY run a **task model**: tasks with an `id`, a `description`, a `status` (`open`/`closed`/`blocked`),
  an `assignee` (`agent`/`human`), an optional parent, and an optional tracker link — seeded from a
  work item or a planning step, closed by the caller, and yielding the `tasks:all_closed` /
  `task:#needs_help` task-state events that drive computed completion (the `[driver]` binding, Section
  6.9). The task model, its durability, and its materialization into an external tracker are the
  driver's; `vcsx` only consumes the resulting events.

The interactive and embedded front-ends run the identical executor over the identical policy; they
differ only in initiator and `escalate` binding.

## 8. The Engine Invocation Contract

The engine is invoked over a transport-neutral contract: an in-process API or a subprocess with
structured input and output. The contract is the same either way; only the encoding differs.

### 8.1 Entry Points and Arguments

The entry points are the front-end sequences and the individual operations:

- `ship`, `land` — the front-end sequences (Section 7).
- `status`, `diff`, `commit`, `integrate`, `push`, `create_pr`, `merge`, `pull` — individual operations
  (Section 4.1), for a driver that composes its own sequence.

Common arguments: the identity the work branch is derived from (Section 6.3), the commit identity
the commits an entry writes are attributed to (Section 10.1), a message input for
`commit`/`create_pr` (Section 10), and the execution context (Section 3.2). The two identities are
separate arguments: the first fills the work-branch pattern and the second names an author, and a
consumer supplies each where its capability takes one (Section 9.1). Exact argument encodings are
`Implementation-defined` and MUST be documented; argument *names* for shared concepts MUST match
this specification.

### 8.2 Result Envelope

Every invocation returns one structured result:

```json
{
  "vcsx_version": "1.0",
  "entry": "ship",
  "status": "needs_caller",
  "op": "push",
  "reason": "non_fast_forward",
  "class": "needs_caller",
  "escalation": { "need": "integrate_then_retry", "op": "push", "detail": "remote moved" },
  "outputs": { "branch": "symphony/ABC-123", "pr": { "number": 42, "state": "open" } },
  "message": "Push rejected: remote moved; integrate and retry."
}
```

- `status` is the invocation's outcome. For a run that executed the policy it is the overall proto
  class: `ok` (all steps `done`), `needs_caller`, or `error`. For a run in which the policy did not
  run it is `usage_or_config` (Sections 6.10, 8.6). A flow the policy stopped with `park`
  (Section 5.2) is `needs_caller`: it did not reach the entry's intended effect, so it is not `ok`,
  and `park` does not fail the flow, so it is not `error`. A flow the executor stopped at its bound
  (Section 5.6) is `needs_caller` on the same reasoning: the entry's intended effect was not
  reached, and no operation failed — the executor declined to dispatch the next one.
- `op` / `reason` / `class` describe the decisive operation result. Where they are non-null, `class`
  is the class `status` reports — `done` under `ok`, `needs_caller` under `needs_caller`, `error`
  under `error` — because the status of a run that executed the policy is that result's proto class.
  All three are null where the run has no decisive operation result: a clean `ok` with no operation;
  a parked flow, which the policy stopped rather than an operation; and a flow stopped at its bound,
  which the executor stopped. In neither of the last two did an operation ask the caller for
  anything, so there is nothing decisive to report. Under `usage_or_config` there is no operation
  result: `op` and `class` are null and `reason` carries the configuration reason (Section 6.10) or
  the precondition reason (Section 8.6).
- `escalation` is present exactly when `status == "needs_caller"` (Section 8.4), a parked flow and an
  exhausted one included.
- `outputs` carries entry-specific structured data (for example `status` fields, the pull-request
  number/state). It also carries `unperformed_intents`: the consumer-effected intents (Section 5.2)
  the engine emitted and no consumer performed, each naming its `action` and that action's arguments.
  The key is absent or empty when every emitted intent was performed.
- A consumer MAY add fields but SHOULD NOT break the fields above within a major version.

### 8.3 Exit Codes

For the subprocess encoding, exit codes mirror the invocation status (Section 8.2) so a caller can
branch without parsing:

- `0` — `ok` (all `done`).
- `10` — `needs_caller` (an escalation is present).
- `20` — `error`.
- `2` — `usage_or_config` (Sections 6.10, 8.6); the policy did not run.

The JSON result is emitted regardless of exit code so a caller MAY always read structured detail.

### 8.4 Escalation Payload

When `status == "needs_caller"`, `escalation` carries: the `need` (a stable token naming what is
required, for example `integrate_then_retry`, `resolve_conflicts`, `supply_identity`,
`await_checks`, `human_review`, `intervention`, `flow_exhausted`), the `op` that produced it, and an
`Implementation-defined` `detail`. The `op` is null where no operation produced the escalation — at a
signal, at a lifecycle position where the gated operation has not run (Section 5.1), and at a bound
the executor reached (Section 5.6). A front-end binds the resolver by the `need` token
(Section 5.5); the `need` vocabulary is part of the public contract and MUST be documented and
stable within a major version.

Two needs name a **hold** rather than a request, and neither is resolvable: a front-end MUST NOT bind a
resolver to either and MUST NOT resume the flow on either. Each hold is released out of band, by a new
invocation.

- `intervention` — the need a parked flow carries (Section 5.2). The policy asked for the hold.
- `flow_exhausted` — the need a flow stopped at a bound carries (Section 5.6). The executor imposed the
  hold, which is a condition to investigate rather than an outcome the policy chose, so it is a token of
  its own rather than a second use of `intervention`.

Every other need names something a caller can supply, which is what makes `park` and `escalate`
distinguishable in the result envelope.

### 8.5 Versioning and the Version Grammar

- The engine version is `MAJOR.MINOR`. The invocation envelope, the invocation status values, the
  proto classes, the exit-code mapping, the `need` vocabulary, the class of every listed reason
  (Section 4.3), the configuration reasons (Section 6.10), and the precondition reasons
  (Section 8.6) are the **major-stable surface**: they do not change within a `MAJOR`.
- New reason tokens, new `need` tokens, new configuration reasons, new precondition reasons, new
  operations, and new plugin backends MAY be introduced in a `MINOR` release; existing consumers
  absorb new operation reasons through the `#class` fallback (Section 5.3), and a new configuration
  or precondition reason through the `usage_or_config` status, which does not change.
- A consumer declares a `version_floor` (Section 6.2); an engine below the floor refuses to run
  (fail-closed) with a usage/config result rather than mis-executing a policy that assumes newer
  surface.

### 8.6 Invocation Preconditions

Between validating the policy (Section 6.10) and running it, the engine establishes the
preconditions the invoked entry point depends on, in order, reporting the first that fails. It
resolves the work branch (Section 6.3), which calls a VCS backend capability — `derive_work_branch`,
or `current_branch` where no `branch_pattern` is configured — and judges the name it resolved with
`accepts_branch_name`. Where the caller supplied a commit identity (Section 10.1) it accepts it with
`accepts_identity`, whose shape only the backend can judge, because the engine holds identity
opaque; the shape is judged whatever the entry, so no invocation carries a malformed identity into
the policy. For an entry that can write a commit — `commit`, `integrate`, `pull`, and a front-end
sequence that dispatches one — an identity is REQUIRED, and its absence is refused here. Each is a
capability the backend publishes (Section 9.1), so the order above is established through the plugin
API rather than inside a backend's own construction, where a refusal would carry no reason for this
registry to report. A capability consulted here that answers neither yes nor no — a backend that
could not read the checkout it was pointed at — establishes no precondition either way, and is
`checkout_unreadable` rather than the refusal its negative answer would have produced (Section 9).

The entry point alone fixes that scope: a front-end sequence that dispatches one means the
sequence's own dispatches (Sections 12.2, 12.3), so `ship` requires an identity and `land` does not,
and a policy's `run_op` edges do not widen the set. An entry outside the set MAY still reach an
operation that writes a commit, because a policy is a graph rather than a flat list (Section 5.2): a
`status` or a `push` run can route an outcome to `commit`, `integrate` or `pull`. That is not a
precondition the engine refuses in advance, because it is not judged from the invocation's arguments
and the checkout but from a path the policy might take. The dispatched operation reports
`identity_missing` (Section 4.3) instead, which is the disposition Section 9.3 already gives an
unsupported capability — refused before the policy runs where the invocation determines it, reported
at first use where only the run does. That dispatch runs the operation's `before:<op>` position as any
dispatch does (Section 4.1): the entry point fixes which invocations are refused in advance, not which
are gated.

A precondition the engine cannot establish is not an operation result. No operation ran, so the
Section 4.3 registry does not apply, no proto class is assigned, and there is no `<op>:<reason>` for
the policy machine to route — the entry points are the front-end sequences and the individual
operations (Section 8.1), and this is before the first of them. The engine refuses to run the policy
and returns the `usage_or_config` status (exit `2`, Section 8.3) with `op` and `class` null and
`reason` carrying one of the tokens below, which is the envelope Section 8.2 already defines for a
run in which the policy did not run.

| Condition | Reason |
|-----------|--------|
| The work branch is the checkout's current branch (Section 6.3) and the checkout has none | `no_current_branch` |
| The derived work branch name is not a legal branch name for the VCS backend | `work_branch_invalid` |
| The caller-supplied commit identity is absent where the entry requires one, or is malformed as the VCS backend judges it whatever the entry (Section 10.1) | `identity_invalid` |
| A VCS backend capability consulted before the first dispatch could not answer — the checkout could not be read (Sections 3.3, 9.1) | `checkout_unreadable` |

Precondition reasons carry no proto class, for the same reason configuration reasons do not
(Section 6.10), and they share the `usage_or_config` status, so a consumer already branching on that
status absorbs a new one without a class edge. An engine MUST document any precondition reason it
adds beyond this registry (Section 13.3). An engine MUST NOT report a precondition reason for a
condition an operation has a reason that names, and the first dispatch is the boundary: before it no
operation has run, and once one is dispatched its failure is that operation's own reason
(Section 4.3). The universal `failed` reason does not satisfy that test, because it names no
condition — reading it as one would make every precondition reportable as `<op>:failed` and leave
this registry nothing to name.

What separates this registry from Section 6.10's is what each is judged from. A configuration error
is a property of `repo.policy.toml` alone, detectable before any argument or checkout is in hand; a
precondition failure needs the invocation's arguments and the checkout the engine was pointed at.
Both refuse to run the policy and both report `usage_or_config`, which is why that status names
usage and configuration together. Validation precedes precondition establishment, so where a
configuration error and a precondition failure both hold, the configuration reason is reported.

## 9. Plugin API

The plugin layer isolates code-host and checkout-mode specifics behind neutral interfaces. Each plugin
advertises a static capability descriptor (data, not a runtime call).

Each capability answers in one of two shapes, fixed by its entry in Sections 9.1 and 9.2: it either
**answers the operation's typed result** `<op>:<reason>` (Section 4.2), or it **answers a value**
the engine composes an operation from. A capability that answers a typed result reports a condition
it could not resolve through the result itself. A capability that answers a value MUST be able to
answer that it could not determine one, and that answer MUST NOT be spelled as the value's absent or
negative case. An absent counterpart, a base the checkout does not hold, a checkout with no current
branch, a working tree that is not dirty, and a work branch with no pull request are each a
determinate fact about the remote or the checkout; none of them is "the backend could not find out".
Every such non-answer MUST map to a reason a caller can read — a Section 4.3 operation reason where
an operation has been dispatched, a Section 8.6 precondition reason where none has, the first
dispatch being the boundary between them (Section 8.6) — and the capability's own entry MUST state
which.

The rule is stated over the capability list rather than left to each capability because the failure
it prevents is silent by construction. A value-answering capability that reports its failure as the
absent answer raises nothing anywhere: the engine composes an operation from a determinate-looking
value and reports the outcome that value implies. What follows is a benign result for a run that did
nothing — a `pull:ok` for a fetch that failed, a `push` over a merged pull request, a `ship` that
reports success with the work still uncommitted — rather than the `error`-class result Section 4.3
defines for every operation. Where the two shapes are mixed without the rule, which capability can
report a failure is a property of how its signature happened to be written.

### 9.1 VCS Backend Plugin

Realizes the version-control operations. Required capabilities:

- `detect_mode()` → checkout mode (Section 3.3), or that the mode could not be determined. The
  engine consults the VCS backend before the first dispatch, when it resolves the work branch
  (Section 8.6), so a mode the backend could not determine is the precondition reason
  `checkout_unreadable` and never an operation result.
- `current_branch()`, `is_dirty()`, `is_conflicted()`, `ahead_behind(base_ref)`. Each answers its
  value or that it could not determine one. `current_branch()` answers the checkout's current branch
  or none, so a checkout with no current branch is a state the engine reports (Section 8.6
  `no_current_branch`) rather than a backend failure; a current branch it could not read is neither
  of those, and is `checkout_unreadable` (Section 8.6). `is_dirty()` is `commit`'s own predicate: it
  reports the working tree dirty exactly when a `commit` would capture something, so content the VCS
  has not yet recorded counts and ignored content does not (Section 4.1). A dirtiness it could not
  determine is not cleanliness: a caller that guards a `commit` on the predicate dispatches the
  operation rather than skipping it (Section 12.2), and the dispatched `commit` reports
  `commit:failed`. `is_conflicted()` and `ahead_behind(base_ref)` realize `status` outputs alone,
  and an output `status` could not determine is reported as undetermined rather than as a
  determinate value (Section 4.1).
- `accepts_branch_name(name)` → whether the name is a legal branch name for this backend, and
  `accepts_identity(identity)` → whether the commit identity is well formed as this backend judges
  it (Section 10.1). Both are questions with no side effect, asked before any operation is
  dispatched (Section 8.6). Both answer yes or no and neither has a third answer: a backend that
  cannot judge the name or the identity it was given answers no, and the engine refuses the
  invocation (`work_branch_invalid`, `identity_invalid`) rather than admitting one nothing judged.
  That is a choice rather than an omission — a predicate that fails closed refuses a legal name at
  worst, while one that fails open carries an unjudged name or identity into every operation that
  writes.
- `resolve_base_ref(remote, branch)` → the base ref for that branch as the checkout holds it for
  `remote`, none where the checkout holds no copy (Section 6.4), or that it could not be resolved.
  Reads the checkout; acquires nothing. The last two are distinct answers, though `diff` reports
  both as `base_unavailable`, whose meaning already covers a failure to have the base whatever its
  cause (Section 4.3): the distinction is `status`'s, which reports a checkout demonstrably holding
  no copy as `base_absent` and a resolution it could not complete as undetermined, rather than
  stating a fact about the checkout it did not establish (Section 4.1).
- `diff(base_ref)` → `diff:*`, the branch delta against the resolved base (Section 6.4). Read-only.
- `derive_work_branch(pattern, identity)` → the pinned work branch (Section 6.3).
- `commit(message, identity)` → `commit:*`.
- `fetch_base(remote, branch)` → the base ref, acquiring the base as `remote` holds it (Section 4.1). A
  base it cannot acquire leaves no ref to answer with, and the engine reports
  `integrate:base_unavailable` (Section 4.3).
- `merge_base(base_ref, identity)` → `integrate:*`, bringing the acquired base into the work branch and
  preserving recorded conflict resolutions where supported.
- `fetch_counterpart(remote, work_branch)` → the ref of the work branch's remote counterpart, none where
  the remote carries none (Section 6.2), or that the acquisition failed. The last two are distinct
  answers and an acquisition the backend could not complete — the remote unreachable, the credential
  refused, the configured remote name absent from the checkout — MUST NOT be answered as an absent
  counterpart, because the two carry different results: an absent counterpart is a benign `pull:ok` and
  a failed acquisition is `pull:failed` (Sections 4.1, 4.3).
- `merge_counterpart(ref, identity)` → `pull:*`, merging the counterpart into the local branch and
  rewriting none of its commits (Section 4.1).
- `push(remote, work_branch)` → `push:*`, with the refspec pinned to the work branch and never a
  force push.

The network-touching capabilities are exactly `fetch_base`, `fetch_counterpart` and `push`: they reach
the remote, need a credential, and realize the version-control operations Section 3.2 places host-side.
Every other capability above is local to the checkout — it reads or writes the worktree and the history
the checkout already holds, acquires nothing over the network, and needs no credential. That is an
enumeration rather than a property of a signature, so a capability's context is read off this list and
never inferred from its arguments: `resolve_base_ref` takes a `remote` and acquires nothing, because the
remote names which of the checkout's copies it answers with (Section 6.4), and `merge_base`,
`merge_counterpart` and `commit` write commits and are still local, because the distinction is
credentials rather than mutation.

An operation is realized through one capability or several. `integrate` is `fetch_base` then
`merge_base`; `pull` is `fetch_counterpart` then `merge_counterpart`; `status` reads through
`detect_mode`, `current_branch`, `is_dirty`, `is_conflicted` and `ahead_behind`, with the forge's
`pr_state` where one is configured (Section 9.2). `pr_state` has three readers rather than one, and
two of them act on the answer instead of reporting it: `push` refuses over a CLOSED/MERGED pull
request (Section 4.1) and `merge` takes the head it conditions on from the same read (Section 9.2),
which is why the state it could not determine is refused at each rather than read as an absence.
Separating the two that acquire from the two that merge is what makes the enumeration above
exhaustive, and it places the half that stops on conflicts — the outcome the caller resolves and
`commit` finalizes (Section 4.1) — on the local side of the boundary, where the caller that resolves
it runs.

`remote` is the resolved remote (Section 6.2) and `base_ref` is the resolved base ref (Section 6.4),
both supplied by the engine; a backend reads neither from the policy nor infers one from the checkout's
own bindings.

`identity` on `commit`, `merge_base` and `merge_counterpart` is the commit identity (Sections 8.1,
10.1), supplied by the engine as `remote` is; the three capabilities that take one are exactly those
that can write a commit, so a mechanical merge commit is attributed no differently from a commit
`commit` writes (Section 10.1). `derive_work_branch(pattern, identity)` takes the identity the work
branch is derived from (Section 6.3), which is a derivation input rather than an attribution, and
writes no commit.

The list is the minimum every backend MUST provide, not a maximum: every operation Section 4.1
requires of a VCS backend is realizable through it. An engine MAY define additional operations
(Section 4.1), and where it does it MUST document the capabilities they require of a backend
(Section 13.3), so a capability beyond this list is visible as the engine's own rather than as shared
surface.

Descriptor fields: supported modes, whether `merge_base` can reuse recorded conflict resolutions, and
whether the backend can operate in a workspace with no colocated remote (Section 3.3).

### 9.2 Forge Backend Plugin

Realizes the pull-request and review operations. Required:

- `create_or_update_pr(head, base, title, body)` → `create_pr:*`, maintaining one pull request per
  work branch and refusing a base mismatch (`create_pr:base_mismatch`). Maintaining one requires
  finding the one that exists, so a backend that could not determine whether the work branch already
  has a pull request MUST NOT create one; it reports `create_pr:failed`.
- `pr_state(work_branch)` → the work branch's pull request — its number, its state
  (open/closed/merged) and the head it currently carries — none where the forge carries no pull
  request for the work branch, or that the state could not be determined. The last two are distinct
  answers and a state the backend could not determine MUST NOT be answered as an absent pull
  request, because the two carry different results: an absent pull request lets `push` proceed and
  `create_or_update_pr` create, while an undetermined one refuses both (`push:failed`,
  `create_pr:failed`) and is a `pr_state_unavailable` output for `status` (Sections 4.1, 4.3). The
  lookup is keyed on the work branch as head **whatever base the pull request targets**, because
  `create_pr:base_mismatch` exists to find one opened against a different base (Section 13.1) and a
  caller's own base therefore MUST NOT be substituted for the key. A search the backend could not
  complete is a state it could not determine and not an absent pull request — including an
  enumeration that reached a bound the backend imposes, which it MUST document (Section 13.3),
  because an incomplete search answers nothing.
- `request_merge(pr, strategy, expected_head)` → `merge:*`, honoring required checks and branch
  protection (a forge refusal surfaces as `merge:rejected`). `expected_head` is the head `pr_state`
  answered when the pull request was read at `before:merge` (Sections 10.3, 12.3). The capability
  MUST NOT merge a pull request whose head is no longer `expected_head`; it reports
  `merge:head_moved` (Section 4.3). The mechanism is the backend's — a forge whose merge request
  takes the expected head as a parameter supplies it there — and a backend whose forge offers no
  means of conditioning the merge does not declare the capability (Section 9.3), because a merge
  that cannot be conditioned merges content no lifecycle position inspected. Where `pr_state` could
  not determine the pull request's head there is no `expected_head` to supply, and the operation
  reports `merge:failed` rather than merging blind.

Every capability above reaches the code host, needs a credential, and realizes an operation Section
3.2 places host-side; the forge plugin has no local half for an enumeration like Section 9.1's to
separate. What a consumer mediates is therefore Section 9.1's three network-touching capabilities
together with every capability of this section (Section 11).

OPTIONAL:

- Review-thread writes: `post_review`, `reply_review`, `resolve_thread`.
- `link_issue(pr, issue_ref)` where the forge does not link natively.

Descriptor fields: PR create/update REQUIRED; the merge strategies supported; whether review-thread
writes and native issue linking are supported.

### 9.3 Capability Descriptors

The executor reads a descriptor before invoking a capability and MUST NOT invoke an undeclared one; an
undeclared capability yields an `error`-class result rather than a silent no-op. A repository policy that
requires an unsupported capability (for example a squash strategy a forge cannot perform) is a
configuration error surfaced at validation where determinable, carrying `capability_unsupported`
(Section 6.10); where it is not determinable before the policy runs, it surfaces at first use as the
operation's `unsupported` reason (Section 4.3).

## 10. Message Formulation

The engine provides the seams; the repository provides the format. `vcsx` bakes in no commit
convention, hygiene rule, or trailer.

### 10.1 Commit

The commit message is **authored** by the caller (in the consumer's context — for an agent-driven
consumer, in-sandbox). It is validated at `before:commit` by the repository's `scan-content` hook
(Section 6.6). The commit author/committer **identity** is supplied by the consumer, distinct from
content. A mechanical merge commit — one `integrate` or `pull` writes where the update it performs
is a merge (Section 4.1) — uses the backend's default message and carries that same identity, which
the engine supplies to those capabilities as it does to `commit` (Section 9.1).

A backend MUST NOT attribute a commit to an identity it derives from its execution environment.
Attribution is therefore a property of the invocation rather than of the host the engine runs on:
the same policy over the same checkout writes the same author on any machine, and an `integrate`
does not depend for its outcome on what identity the host happens to offer.

Note: a merge the forge performs (`merge`, Section 9.2), including the commit a squash strategy
writes (Section 10.3), is attributed by the code host to the account the consumer's credential
names. The engine writes no commit for it and supplies no identity.

### 10.2 Pull-Request Composition

The pull-request title and body are **composed** per `[messages.pr]` (Section 6.8):

- `body_source = "auto"` — compose the body from durable inputs the consumer supplies: the work item
  (title and link), a closed task list when the consumer runs the task model (Section 7.3), and the
  commit subjects. Caller-supplied prose, when present, overrides (replaces) the composed body.
- `body_source = "agent"` — use caller-supplied prose only.
- `body_source = "template"` — use a repository template over the durable inputs.

The title is scanned with the `title_scan` profile and the body with the `body_scan` profile (Section
10.4). One pull request is maintained per work branch (created, then updated).

### 10.3 Squash (`pr_to_squash`)

For a squash merge, the squash subject and body are **mechanically transformed** from the pull request
by the repository-owned `pr_to_squash` transform at `before:merge`: by convention the title is taken
verbatim and the body is laundered per the transform (for example stripping integration-only keys), so
durable history can be stricter than the live pull-request surface. `land` runs the transform; it never
authors a message. The transform is a repository unit; the engine supplies only the position and the
pull-request content.

### 10.4 Content Scanning

A scan profile is a repository-owned check (`scan-content`) that inspects content — a commit diff, a
title, a body — and blocks by returning a `needs_caller`/`error` result with a stable reason, which
the engine surfaces as the scanned operation's `blocked` or `failed` reason (Section 6.6). The
engine ships no scan rules; profiles such as `strict` and `relaxed` are names a repository binds to its
own checks. Scanning at `before:commit` runs in-sandbox; scanning title/body during `create_pr` runs in
the consumer's context.

## 11. Security and Trust Model

`vcsx` enforces no security invariant of its own; it provides the structure a consumer uses to enforce
one:

- The engine holds no long-lived credentials. A consumer supplies credentials to the plugins for an
  invocation or runs the engine where they are already held.
- The engine labels every policy edge and hook with its execution context (Section 3.2) so a
  consumer can source host-side policy from a trusted revision and in-sandbox policy from the
  worktree, and can mediate the credentialed operations. An in-sandbox edge or hook MUST NOT receive
  credentials. The capabilities that touch the network are named and enumerable — three of the VCS
  backend's and every required capability of the forge backend (Sections 9.1, 9.2) — so what a
  consumer mediates is a fixed list rather than something inferred from an operation's description.
- The engine pins every push refspec to the derived work branch and never force-pushes, so a consumer's
  scope guard has a fixed target. No operation that updates the work branch rewrites, drops, or
  re-parents a commit already on it — an update that reconciles a divergence merges (Section 4.1) — so
  the branch remains publishable without a force push. A `rebase` or `squash` merge strategy
  (Section 6.8) is not an exception: it writes to the base branch.
- The engine performs no repository provisioning and reads no base or branch from untrusted content;
  base resolution is configuration (Section 6.4).

A consumer that runs a sandboxed, credential-less agent (for example the Symphony service) instantiates
the agent boundary and the secret isolation; those are the consumer's, not the engine's.

## 12. Reference Algorithms

### 12.1 Match a Trigger

```text
function match_edge(policy, from_context, trigger):
  candidates = ladder(trigger)          # most-specific first
  for key in candidates:
    edge = policy.lookup(from_context, key)   # an edge scoped to this from-context
    if edge does not exist:
      edge = policy.lookup(null, key)         # else the unscoped edge, if the policy has one
    if edge exists:
      return edge
  return builtin_default(trigger)

function ladder(trigger):
  if trigger is a lifecycle position:        # before:X
    return [trigger]                          # exact only
  if trigger is a typed result op:reason:
    class = proto_class(op, reason)
    return [ "op:reason", "op:#class", "#class" ]  # substituting op/reason/class
  if trigger is a signal or task event s:
    return [ s ]                              # exact only; signals carry no proto class
```

### 12.2 `ship` Sequence

```text
function ship(identity, message):
  if worktree_dirty() is not clean:         # dirty, or undetermined (Section 9.1)
    dispatch(run_op("commit", message))     # runs before:commit, then commits;
                                            # commit:* re-enters the machine
  loop:
    if flow_bound_reached():                # Section 5.6; counts every run_op, not this loop's turns
      return flow_exhausted()               # needs_caller, need = flow_exhausted
    r = run_op("push")                      # runs before:push, then pushes
    if r is push:non_fast_forward:
      # policy typically routes this to integrate
      i = run_op("integrate")
      if i is integrate:merge_conflicts:
        return escalate("resolve_conflicts")
      continue                              # retry push
    if r is push:pr_closed:
      return escalate("human_review")
    if r.class != done:
      return result_of(r)                    # e.g. push:blocked; class default (Section 5.4)
    break                                    # push:ok / up_to_date
  p = run_op("create_pr")                    # runs before:create_pr, then composes (Section 10.2)
  return result_of(p)                        # stops at the pull request
```

The routing above is the built-in default; a repository's `[policy]` edges override each step. `ship`
never runs `merge`. The sequence runs no position of its own: each `run_op` above runs its operation's
`before:<op>` position (Section 4.1), so a working tree the guard reads as clean enters no
`before:commit`.

`worktree_dirty()` is the `is_dirty()` capability (Section 9.1), so the guard and the operation
share one predicate: a change made only of content the VCS has not yet recorded is dirty, and `ship`
commits it rather than reporting the branch clean and pushing nothing. Where the capability cannot
determine whether the working tree is dirty, the guard does not read as clean: `ship` dispatches
`commit`, which reports `commit:failed` (Sections 4.3, 9.1). The guard exists to skip a `commit`
that would report `nothing_to_commit`, not to decide whether a commit is owed, so an undetermined
predicate dispatches rather than skips — a guard that read it as clean would produce a `ship`
reporting success with the work still uncommitted, which is a branch on a capability's absent answer
rather than a report of it (Section 9). The retry converges because `integrate` acquires the base
from the configured remote (Section 4.1) rather than re-reading the checkout's copy; against a stale
copy the push would stay non-fast-forward until the flow bound ended the invocation.

The loop is bounded by the flow bound (Section 5.6) rather than by a step count of its own: every
`run_op` counts against it wherever it is dispatched, so a `push`/`integrate` pair that never converges —
against a base branch that moves between every attempt, or through a repository's own edges routing back
to an earlier operation — ends the invocation at `needs_caller` with the `flow_exhausted` need instead of
running indefinitely.

### 12.3 `land` Sequence

```text
function land():
  loop:
    if flow_bound_reached():                 # Section 5.6; counts every run_op
      return flow_exhausted()                # needs_caller, need = flow_exhausted
    m = run_op("merge", strategy = configured_strategy())
                                             # runs before:merge — reads the pull request, applies
                                             # pr_to_squash for a squash strategy — then merges the
                                             # head that position read (Sections 9.2, 10.3)
    if m is merge:head_moved:
      continue                               # re-dispatch: re-read, re-gate, retry
    return result_of(m)                      # merge:not_open / checks_pending -> needs_caller
```

The routing above is the built-in default, as Section 12.2's is; a repository's `[policy]` edges
override it.

The retry re-dispatches the operation, which re-runs the position (Section 4.1), and that is what
makes it sound. `before:merge` is where the pull request is read and where a squash strategy's
`pr_to_squash` transform runs (Section 10.3), so a retry that merged again without re-gating would
merge a head no position inspected and write a squash message describing a revision that is not the
one squashed. The re-dispatch also re-runs a repository's own gate edges there, which is the
property Section 12.2's loop has at `before:push`. `expected_head` is not an argument the sequence
threads: the dispatch supplies the head its own position read (Section 9.2).

The loop terminates on the flow bound (Section 5.6): every `run_op` counts against it wherever it is
dispatched, so a pull request whose head moves between every attempt ends the invocation at
`needs_caller` with the `flow_exhausted` need rather than retrying indefinitely — the same
convergence argument Section 12.2 makes, with the re-read in place of the `integrate`. Because the
routing is built in, `merge:head_moved` reaches a caller only where a repository binds it to an edge
that ends the flow, so the condition adds a reason token and no `need` token (Sections 4.3, 8.4).

### 12.4 Resolve Base

```text
function resolve_base(work_branch, base_config, remote):
  if base_config.resolve == "fixed" or unset:
    branch = base_config.branch
  else if base_config.resolve == "by_prefix":
    match = longest_prefix_match(work_branch, base_config.prefixes)
    if no match and no empty-prefix default:
      return error(base_unresolved)          # config error caught at validation
    branch = match or empty_prefix_default
  return { branch: branch,                   # the name the forge takes (Section 9.2)
           ref:    resolve_base_ref(remote, branch) }   # the commit the VCS takes; none
                                                        # where the checkout holds no copy
```

### 12.5 Compose the Pull-Request Body

```text
function compose_pr_body(inputs, agent_prose, source):
  if source == "agent" and agent_prose present:
    return agent_prose
  composed = join([
    inputs.work_item_title_and_link,
    inputs.closed_task_list,                 # empty when no task model
    inputs.commit_subjects
  ])
  if source == "auto" and agent_prose present:
    return agent_prose                        # override replaces
  return composed
```

## 13. Conformance

### 13.1 Test Matrix

The deterministic, host-independent subset of these checks is also published as a machine-readable,
language-neutral vector corpus under `conformance/vcsx/` (RECOMMENDED); an engine runs it against its
own binary and records the result in its Conformance Statement (Section 13.3). The corpus does not
restate or replace the checks below.

A conforming engine SHOULD include tests covering:

- Matching: an `op:#class` edge catches an unnamed reason of that class; a `#class` edge catches an
  otherwise-unmatched result; a lifecycle position matches exactly with no class fallback; an edge
  carrying no `from` matches inside a from-context, an edge scoped to that context is selected over
  it for the same trigger key, and the ladder selects the key before the from-context selects among
  the edges bound to it (Section 5.4).
- Unmatched policy: an unmatched operation outcome is fail-safe (parked/failed, reason surfaced, never
  dropped); an unmatched signal is a no-op.
- Determinism: a duplicate `(from, on)` edge or transition is a configuration error and the engine
  refuses to run.
- Termination: a policy whose `run_op` results route back to an earlier operation stops at the flow
  bound (Section 5.6), yielding `needs_caller` with the `flow_exhausted` need and null
  `op`/`reason`/`class`; a flow that converges within the bound is unaffected; a repeated
  `(trigger, edge)` pair does not by itself stop a flow.
- Operations and reasons: each operation returns a registry reason (Section 4.3) with its documented
  proto class; `push:non_fast_forward` is `needs_caller` and routes to `integrate`; `push:pr_closed`
  refuses a push over a CLOSED/MERGED pull request; `create_pr:base_mismatch` is surfaced, not
  overwritten; a divergent `pull` merges rather than rewrites, and the `pull:conflict` it leaves is
  finalized by `commit`; a working tree whose only change is content the VCS has not recorded is
  dirty and is committed, not skipped or reported `commit:nothing_to_commit`; `integrate` brings in
  the base as the remote holds it, so a `push:non_fast_forward` retry converges against a base that
  moved, while `status` and `diff` report against the resolved base ref and acquire nothing; a read
  in a checkout carrying more than one remote reports against the copy belonging to the configured
  remote (Section 6.4); an `integrate` whose acquisition fails yields `base_unavailable` rather than
  retrying to the flow bound; a `pull` whose acquisition fails yields `failed` while a `pull`
  against a remote carrying no counterpart yields `ok`, so a fetch the engine could not complete is
  not reported as the benign absence (Sections 4.1, 9.1); a `diff` in a checkout holding no copy of
  the base yields `base_unavailable`, while `status` yields `ok` with null `ahead`/`behind` and a
  `base_absent` output; a `push` whose pull-request state could not be determined does not push and
  yields `failed` rather than proceeding as it would over a branch that has no pull request, a
  `create_pr` in that condition creates nothing and yields `failed` rather than a second pull
  request, and `status` in it yields `ok` with a null pull-request output and a
  `pr_state_unavailable` output rather than reporting no pull request (Sections 4.1, 9.2); a `ship`
  whose `is_dirty()` cannot answer dispatches `commit` and yields `commit:failed` rather than
  pushing an uncommitted worktree (Sections 9.1, 12.2); a `merge` whose pull request's head advanced
  after it was read merges nothing and yields `head_moved` rather than `conflict`, `rejected` or
  `failed`, while a `pr_state` that could not determine the head yields `merge:failed` rather than
  an unconditioned merge (Sections 4.3, 9.2).
- Gate blocking: a `before:<op>` hook blocking with a `needs_caller` result surfaces as
  `<op>:blocked` and with an `error` result as `<op>:failed`, at every gated operation (Section 6.6);
  a gated operation dispatched by a `[policy]` `run_op` edge rather than by a front-end sequence — a
  `status` entry routing `status:ok` to `run_op` `commit` — runs `before:commit` and is blocked there
  identically, the position travelling with the dispatch rather than with the caller
  (Sections 4.1, 5.2).
- Front-ends: `ship` stops at the pull request, and over a working tree its guard reads as clean
  dispatches no `commit` and so enters no `before:commit` (Sections 4.1, 12.2); `land` merges an
  open, checks-passed pull request, applies `pr_to_squash` for a squash, and never authors a message;
  `land` retries a `merge:head_moved` by re-dispatching the operation, which re-reads and re-runs
  `before:merge`, so the squash message is transformed from the revision actually merged, and a head
  that moves between every attempt ends at the flow bound rather than merging a head no position
  inspected (Sections 5.6, 12.3); the same `repo.policy.toml` yields the same operation flow through
  `ship` and an embedded driver.
- Invocation contract: exit codes mirror proto classes; `escalation` is present exactly for
  `needs_caller`; a parked flow is `needs_caller` with the `intervention` need and null
  `op`/`reason`/`class`; a `version_floor` above the running version refuses fail-closed, while one
  that is not a `MAJOR.MINOR` version is refused as `malformed_policy` rather than compared; a
  policy file that does not parse and an edge omitting the argument its action requires are refused
  with the same reason and null `op`/`class` (Section 6.10); a checkout with no current branch where
  no `branch_pattern` is configured, an illegal derived work-branch name, and a commit identity that
  is absent where the entry requires one or malformed each refuse to run the policy and yield
  `usage_or_config` with the precondition reason and null `op`/`class`, the last two judged through
  `accepts_branch_name` and `accepts_identity`, while a backend that cannot read the checkout at all
  yields `checkout_unreadable` rather than `no_current_branch` (Sections 8.6, 9.1); an entry the
  identity precondition does not cover — a `status` whose policy routes `status:ok` to `run_op`
  `commit` — runs the policy and reports `commit:identity_missing`, class `needs_caller`, rather
  than a precondition reason, while a malformed identity supplied to that same entry is refused
  before the policy runs (Sections 4.3, 8.6).
- Message formulation: the `auto` PR body composes from durable inputs and agent prose replaces it; the
  squash body is the `pr_to_squash` transform of the pull-request body; every commit the engine
  writes carries the supplied commit identity — the mechanical merge commit an `integrate` or a
  `pull` writes included — on a host whose environment supplies no usable identity of its own
  (Section 10.1).
- Plugins: an undeclared capability yields `capability_unsupported` at validation where determinable
  and the operation's `unsupported` reason at first use otherwise, never a silent no-op; git and jj
  checkout modes (including a jj secondary workspace) are handled; the remote-touching operations
  act against the resolved remote, a configured `[engine] remote` overriding the backend's default
  (Section 6.2); the capabilities that reach the network are exactly `fetch_base`,
  `fetch_counterpart` and `push` among the VCS backend's and every required capability of the forge
  backend, and no other VCS capability is invoked with a credential (Sections 9.1, 9.2); every
  value-answering capability can report that it could not determine its answer, and no such report
  is spelled as the value's absent case (Section 9).

### 13.2 Implementation Checklist

- One policy-graph executor run by both front-ends; `ship`/`land` and the embedded-driver contract.
- The action-policy machine: triggers, actions, the `#class` fallback, from-context scoping with
  unscoped edges, fail-safe-on-unmatched-outcome, no-op-on-unmatched-signal, determinism, and a
  bounded flow.
- The operation set and the reason-token registry with stable proto classes, each gated operation
  running its `before:<op>` position as part of every dispatch.
- `repo.policy.toml` loader and validation (with `vcsx.toml` merge), including the refusal of a
  policy that is not well formed, base resolution to a branch and a base ref, and the
  execution-context labeling.
- The invocation contract: result envelope, exit codes, escalation payload, invocation
  preconditions, and versioning with a `version_floor` floor.
- The plugin API with VCS and forge backends and their capability descriptors, the VCS backend
  separating the capabilities that acquire from the local ones that use what they acquired, and
  every value-answering capability able to report that it could not determine its answer.
- Message formulation seams (`scan-content`, PR composition, `pr_to_squash`) with no built-in
  format, and every commit the engine writes attributed to the supplied commit identity.
- Checkout-mode handling (git, jj, jj secondary workspace), a pinned, never-forced push refspec, a
  history-preserving work-branch update, and a merge conditioned on the head the `before:merge`
  position inspected.

### 13.3 Conformance Statement

A conforming engine MUST publish a Conformance Statement: a single document recording the choices this
specification leaves to the engine, so a consumer, auditor, or peer engine can determine what the
engine does without reading its source. It is the home for the `Implementation-defined` and "MUST
document" obligations dispersed through this specification, gathering those choices in one place
rather than restating their requirements.

The Statement MUST record:

- The engine version and the major-stable surface it claims (Section 8.5), including the lowest
  `version_floor` the build satisfies.
- A resolution for every `Implementation-defined` behavior in this specification: checkout-mode
  detection (Section 3.3), the flow bound's value and any further bound the engine imposes
  (Section 5.6), `repo.policy.toml` discovery precedence (Section 6.1), the backend's default remote
  where `[engine] remote` is unset (Section 6.2), the form of a hook's engine-invoked `run` unit
  (Section 6.6), which reason is reported when several configuration conditions hold (Section 6.10),
  the entry-point argument encodings (Section 8.1), and the escalation `detail` field (Section 8.4).
- Any reason token the engine adds beyond a registry: an operation reason with its proto class
  (Section 4.3), a configuration reason (Section 6.10), or a precondition reason (Section 8.6).
- The `need` vocabulary the engine emits (Section 8.4).
- The capability descriptors its VCS and forge plugins advertise (Section 9.3), the capabilities any
  operation it defines beyond Section 4.1 requires of a backend (Section 9.1), and any bound a forge
  backend imposes on its search for a work branch's pull request (Section 9.2).

The Statement is a published declaration, not a precondition for running the engine: Section 13.1 and
Section 13.2 keep their roles as the test matrix and the definition of done. Its format is
`Implementation-defined`. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` in the specification repository is
the RECOMMENDED shape: it enumerates each obligation above as a row an engine fills.

A deployment that embeds this engine declares it from the consumer's side as a version pin, in the
consumer's own statement; an `engine-direct` deployment publishes this Statement alone.

## 14. Alignment with `VCSX-CONTRACT.md`

`VCSX-CONTRACT.md` is the surface an embedding consumer references; this document is its full
realization. Every token shared between the two — the operations, the lifecycle positions, the trigger
and action names, the proto classes, the reason and `need` vocabularies, the `repo.policy.toml`
sections, the task and message-formulation surfaces — MUST be spelled identically in both. Changing a
name is a contract change: update both documents in step, and record it where the owning consumer tracks
its anchors. This engine spec was shaped by the surface it realizes and by the Symphony decision record
(0026–0032) that motivated the surface; those hold the reasoning, this document holds the schema and
algorithms.
