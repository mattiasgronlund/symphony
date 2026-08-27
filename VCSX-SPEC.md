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

`vcsx` is driven by a consumer that owns the configuration, the credentials and (when applicable) the
agent boundary. A consumer may be a human at an interactive prompt or an automation service. `vcsx`
itself:

- holds no long-lived credentials of its own; the consumer supplies credentials to the forge/VCS
  plugins for the duration of an invocation (Sections 8.1, 9), or runs the engine in a context that
  already holds them, and the engine persists neither beyond the invocation.
- obtains and maintains the checkout it acts in, from the remote, the access parameters and the
  credentials the consumer supplies (Sections 4.1, 8.1). Which remote a repository is taken from,
  which code host it is published to, and where either is reached are the consumer's; acquiring and
  refreshing what they name is the engine's.
- enforces no agent-secret boundary. When a consumer runs the engine on behalf of a sandboxed,
  credential-less agent, the consumer instantiates that boundary and mediates the engine's
  credentialed operations; `vcsx` distinguishes host-side from in-sandbox execution (Section 3.2) so a
  consumer can split a policy across such a boundary, but the boundary itself is the consumer's.

## 2. Goals and Non-Goals

### 2.1 Goals

- Run version-control and forge operations behind one policy-graph executor with deterministic,
  most-specific-wins matching and no silent drops.
- Obtain and maintain the checkout those operations act in — creating it where none exists, refreshing
  it where one does (Section 4.1) — so a consumer managing a repository implements no version control
  of its own.
- Let a repository express its whole Way of Working in one file (`repo.policy.toml`), consumed
  identically by the interactive and embedded front-ends.
- Keep the engine format-neutral: message formulation, hygiene, and merge policy are repository
  configuration and hooks, never engine built-ins.
- Provide a stable invocation contract (structured results, proto classes, exit codes, versioning) so
  a consumer can branch on outcomes without enumerating every reason token.
- Provide a plugin layer so the same policy runs across code hosts (for example GitHub, Forgejo) and
  checkout modes (for example git, jj) without policy changes.

### 2.2 Non-Goals

- Credential storage — the consumer's. The engine takes a credential for the duration of an
  invocation (Sections 1.3, 8.1) and persists none beyond it.
- Any agent-sandbox or secret-isolation mechanism — the consumer's.
- Prescribing a commit convention, message format, content-hygiene rule, or branch-protection policy —
  repository-owned Way of Working.
- A general-purpose workflow engine beyond the VCS/forge operation domain.
- **Deciding when to retry, how long to back off, or what a budget is worth** — the consumer's. The
  engine reports what it observed and stops: an operation that failed is reported rather than
  re-attempted (Section 4.3), a network call that reached its bound is reported rather than re-made
  (Section 9), and a forge budget is reported rather than paced against (Section 9.2). Which of
  those to act on, and how, is a decision that depends on what else the consumer intends to spend
  its budget on and how many other holders of the same credential are spending concurrently —
  neither visible from inside one invocation.
  - The `await_checks` operation (Section 4.1) is the one bounded exception, and it is an exception
    to *waiting* rather than to *deciding*. It executes a wait the consumer parameterizes — the
    bound, the interval and the budget floor are all invocation arguments (Section 8.1) — and
    answers none of the three questions above for itself. Supplied no arguments it makes a single
    read and cannot loop.

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
   - The content-scan seam (`scan-content`, at the lifecycle position a policy edge binds it to) and
     the composition/transform seams for commit, pull-request, and squash messages.

### 3.2 Execution Contexts (Trust)

The engine distinguishes two execution contexts, so a consumer that runs an agent inside a sandbox can
split one policy across the boundary:

- **Host-side** — operations and hooks that touch the remote or hold credentials (provision,
  integrate, push, pull, create_pr, merge, host-side hooks). A consumer sources host-side policy from
  a trusted revision it names itself so an untrusted worktree cannot alter it. That revision is not
  derived from the policy: a branch named inside `repo.policy.toml` cannot select the revision
  `repo.policy.toml` is read from, and it MUST NOT be a branch the consumer's own merges reach, or
  the work the consumer lands could rewrite what it trusts.
- **In-sandbox** — operations and hooks that run in the working tree without credentials (the
  `before:commit` gate/scan, in-sandbox hooks). A consumer sources these from the worktree.

The two lists above say which **operations** reach the remote or hold credentials. An **edge's** or
a **hook's** context is a different question with a different answer: it is fixed by the artifact
the edge or hook was declared in (Sections 6.5, 6.6), never by the operation an edge names. The
consumer tags each while assembling the one merged surface it hands the engine, which is the same
act as sourcing it by trust.

The two meet at a dispatch. An in-sandbox edge whose `run_op` names an operation from the host-side
list receives no credential and reports that operation's own reason at the dispatch (Sections 4.3,
8.6) — the operation states what it needs, and the edge's context states what it may hold.

`vcsx` labels each policy edge and hook with its context (Section 6) but does not itself enforce the
sourcing rule; the consumer sources config by trust and mediates host-side operations. The engine
guarantees only that an in-sandbox edge never receives credentials.

### 3.3 Checkout Modes

The `VCS backend` detects and adapts to the checkout mode; policy is written mode-neutrally. At least:

- `git` — a plain git checkout.
- `jj` — a jj checkout, including a jj checkout colocated on git storage and a jj secondary workspace
  that has no colocated git storage. In a secondary workspace the backend resolves the remote
  (Section 8.1) and the work branch from jj rather than from a colocated git remote.

The mode is reported by the `status` operation (Section 4.1) and is `Implementation-defined` in its
detection mechanism; the backend MUST document how it detects the mode. No `repo.policy.toml` key
selects it. For a checkout the engine did not create, `detect_mode()` (Section 9.1) is what answers,
and a mode it could not determine is `checkout_unreadable` (Section 8.6). The one checkout for which
there is nothing yet to detect is one the engine creates, whose mode the consumer names with
`local_vcs` (Sections 4.1, 8.1), so exactly one of the two paths answers for any checkout.

Which **backend** does the detecting is a separate question, and `local_vcs` answers that one too:
it is the consumer's VCS backend selection (Section 8.1), REQUIRED on every invocation, because the
engine loads a backend before it can ask one anything — `detect_mode()` included. Naming the backend
is not naming the mode. A backend MAY declare several supported modes (Section 9.3), so a checkout
the engine did not create takes its backend from `local_vcs` and its mode from `detect_mode()`, and
neither answer is derived from the other.

A checkout mode's storage arrangement is likewise the backend's. This specification states only the
relationship the provisioning operation needs — one fetched copy of a repository, and the working
trees that share it (Section 4.1) — and names no mechanism for realizing it, because a mode whose
secondary working tree holds no storage of the kind another mode colocates realizes it differently. A
backend that cannot derive more than one working tree from one fetched copy declares so in its
capability descriptor (Sections 9.1, 9.3) rather than discovering it at first use.

No checkout mode carries the forge repository coordinate. Which repository on the code host the forge
operations act against is supplied by the consumer (Sections 8.1, 11) and is not derived from the
checkout in any mode, so a backend that resolves a remote from jj resolves the version-control remote
and nothing about the forge.

## 4. Operations and the Operation Model

### 4.1 Operation Set

Operations are the unit `run_op` runs (Section 5.2), less the two below that run outside the
action-policy machine. Each is realized through the plugin layer and returns a typed result
(Section 4.2). Read-only operations carry no lifecycle position.

An operation marked **Read-only** below changes none of three things: the content a `commit` would
capture, the commits reachable from the work branch or the resolved base (Sections 6.3, 6.4), and
what the remote holds. The term quantifies over those three and not over the bytes on disk or the
object store: a backend MAY answer a read by writing to its own staging or bookkeeping state, subject
to the allowance and the documentation obligation Section 9.1 states over its capability list. A
checkout mode that records the working tree as a commit of its own before it can inspect it
(Section 3.3) is therefore drivable, because a commit no branch the engine named reaches is not one
of the three — which is why Section 9.1 requires such a backend to keep that commit outside what the
work branch reaches, rather than leaving the arrangement to each backend.

- `load_policy` — obtain the merged host-side policy surface, once, for a unit of work. It reads
  `repo.policy.toml` from the policy source (Sections 6.1, 8.1), merges any `vcsx.toml`, and returns
  the surface for the consumer to inspect, together with the assurance that it validates. What the
  consumer holds between invocations is that surface and the `policy_pin` naming it (Sections 8.1,
  8.2): every invocation reads and validates the document itself, and the pin is how a later one
  claims that what it read is the surface this unit of work began under (Section 8.6). This is the
  operation that makes Section 3.2's "the consumer sources config by trust" literally true, and it
  is realized through the plugin layer as every other operation is: it reads each file at the
  revision through `read_at_source` (Section 9.1), once per invocation rather than once per unit of
  work, because what a unit of work fixes is the surface and not the read. Like `provision`, it has
  no lifecycle position and raises no `<op>:<reason>` trigger, and for the same reason no `run_op`
  edge may name it: the edges that would gate, route or dispatch it are in the document it exists to
  obtain. Its failures are the four Section 6.1 names, reported as configuration errors. Read-only.
- `provision` — ensure the repository is present and current: create the store where
  `store_location` holds none, refresh it where it holds one, and, where the invocation names a
  `tree_location`, derive the working tree there from that store (Section 8.1). An invocation naming
  no `tree_location` maintains the store alone, which is the half a consumer runs once per
  repository before deriving a tree per unit of work. Store and trees are stated as a relationship
  rather than a mechanism — one fetched copy of a repository, and the working trees that share it —
  and how a backend realizes it is the backend's (Sections 3.3, 9.1). The operation is host-side
  (Section 3.2): it reaches the remote at `git_access` under `git_credential` (Sections 8.1, 9.1).

  `provision` runs before everything the engine reads out of the repository, which places it outside
  three things every other operation sits inside. It has **no lifecycle position**, and its result
  does not re-enter the action-policy machine as an `<op>:<reason>` trigger (Section 5): both are
  matched against `[policy]` edges read from `repo.policy.toml`, which is inside the repository this
  operation exists to obtain, so a gate on it would be absent on the invocation that creates the
  checkout and present on one that refreshes it — a trigger that sometimes exists, which Section
  5.4's one-edge-per-trigger rule is written to prevent. No policy document is validated for it, for
  the same reason (Sections 6.1, 6.11). And no precondition that reads a checkout is established for
  it (Section 8.6), because the checkout is what it produces. The consumer classifies the result. No
  front-end sequence dispatches it (Sections 12.2, 12.3): a consumer obtains the checkout by
  dispatching the operation, so no entry named for something else acquires one as a side effect.
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
  no determinate value it did not establish. Where the invocation supplied a `pr_state_validator`
  (Section 8.1) and the forge answered that the pull request has not moved since that validator was
  issued, the pull-request fields are null and a `pr_state_unchanged` output reports it; the
  operation still completes, and the caller reads the state it already holds. Where the forge
  refused the read because a budget was exhausted, the pull-request fields are null and a
  `pr_state_throttled` output reports it; the operation still completes, and the exhausted bucket
  with its `resets_at` is in `outputs.forge_budget` (Sections 8.2, 9.2), so the output names the
  condition and the snapshot carries the figure, which keeps the figure in one place. Those are four
  distinguishable pull-request conditions, stated separately because each carries a different
  meaning: `pr_state_unavailable` is a read that established nothing, `pr_state_unchanged` is a read
  that established the caller's copy is current, `pr_state_throttled` is a read the forge refused
  for budget, and a reported state is a read that established a new one. The operation completes in
  all four, which is what places a refused forge call here rather than in a reason of its own
  (Section 4.3). Read-only.
- `diff` — the branch delta against the resolved base. Read-only.
- `commit` — create a commit from the working tree, gated at `before:commit` (Section 10.1). The
  operation captures the working tree in full: every change the VCS does not ignore, including
  content the VCS has not yet recorded. The engine defines no staging operation and no way to commit
  a subset, so nothing selects the commit's content out of band.
- `integrate` — bring the resolved base into the work branch (a merge/update-branch), preserving
  recorded conflict resolutions where the backend supports them. The base is the branch as the
  resolved remote holds it (Sections 6.4, 8.1), acquired rather than read from the checkout's
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
- `await_checks` — read the pull request's required-check state (Section 9.2 `checks_state`) until
  one of five conditions holds: the checks completed successfully, they completed and did not pass,
  the forge reports no required checks for the pull request, the invocation's read allowance ended,
  or a budget floor the invocation supplied was reached (Sections 4.3, 8.1). The read allowance is
  what the invocation's await parameters authorize, an invocation authorizing no loop having an
  allowance of one read, so the fourth condition covers a supplied bound that was reached and a
  single read that found the checks still running alike. The third is a determinate answer rather
  than a wait that ended, and it ends the wait on the first read: a pull request with no required
  checks has nothing to wait for (Section 9.2). Gated at no fixed position.
  Read-only: it changes none of the three
  things that term quantifies over, and in particular it does not merge — the state it reports is
  the state a subsequent `merge` would act on, not an action on it. Each read is conditional where
  the consumer carried a validator forward and the backend supports one (Sections 8.1, 9.2), so a
  loop that finds nothing changed costs a loop's worth of unchanged answers rather than of full
  reads. It exists because the alternative way to poll is to re-dispatch `merge` until it stops
  reporting `checks_pending`, which asks a cheap question with a mutating request — charged at a
  mutation's cost, and carrying whatever a refused merge request costs on a given forge.
- `pull` — update the local work branch from its remote counterpart, preserving the commits already on
  the branch: the counterpart is merged in, and no commit on the branch is rewritten, dropped, or
  re-parented (Section 11). `pull:conflict` is therefore a merge conflict, which the caller resolves and
  `commit` finalizes; the operation set has no step that resumes a sequential replay. Where the remote
  carries no counterpart the operation is a benign no-op and reports `pull:ok`: the work branch is
  engine-derived and need not exist on the remote before the first push (Sections 6.3, 8.1). An
  acquisition the engine could not complete is not that no-op and reports `pull:failed`
  (Sections 4.3, 9.1).

Two operations run **outside the action-policy machine**: an operation the machine cannot route,
because it runs before the document the machine is read from can itself be read. `load_policy`
and `provision` are the pair today — one produces that document and the other produces the repository the document
is in (Sections 6.1, 6.11) — and it is the property rather than the pair this specification fixes,
so an operation a `MINOR` release adds with it inherits what follows (Section 8.5). Two things
follow. Neither raises an `<op>:<reason>` trigger an `on` may name (Section 5.1). And no `run_op`
edge may name either: a policy carrying one is refused with `operation_not_dispatchable` before
anything runs (Section 6.11).

The argument is the one `provision`'s entry above already makes, and it reaches the edge as it
reaches the trigger. An edge dispatching one of the pair was read out of what that operation
produces, so it can fire only where the product was already there — absent on the invocation that
creates the checkout and present on one that refreshes it, a trigger that sometimes exists, which
Section 5.4's one-edge-per-trigger rule is written to prevent. What an accepted edge would do is
worse than dead. `load_policy` carries no reason token and therefore no proto class (Section 4.3),
so a `run_op` naming it **disposes of** the outcome that fired it (Section 5.4) with a result none
of the three built-in defaults can key on, and the flow carries on past an outcome nothing acted on.

This specification fixes the operation set and the lifecycle positions; an engine defines neither of
its own. The operations above are the set, and `before:commit`, `before:push`, `before:create_pr`,
`before:merge` are the lifecycle positions; both are extended only by a `MINOR` release (Section
8.5). `provision` has none, for the reason its entry states: the policy that would carry the gate is
not readable when the operation must first run. `await_checks` has none for a different reason: a
gate before a wait would run a unit that inspects nothing and blocks nothing worth blocking, the
operation acting on nothing and reading a state the repository's own units cannot influence.

A gated operation's position runs as part of dispatching it. The engine runs `before:<op>` whenever
`<op>` is dispatched — by a front-end sequence (Sections 12.2, 12.3), by a `[policy]` `run_op` edge
(Section 5.2), or by a retry — so what reached the operation does not decide whether the operation is
gated. Gating is a property of the operation, as the entries above state it, rather than a step a
caller takes around it: Section 6.6 surfaces a block as the gated operation's own reason and Section
13.1 requires that surfacing at every gated operation, neither of which a caller could guarantee for a
dispatch it does not make. An operation carrying no lifecycle position enters none wherever it is
dispatched. Because the dispatch runs the position and a position's `run_op` edge
makes a dispatch of its own, a set of `[policy]` edges that returns a position to itself describes
dispatches that reach no operation at all; Section 6.11 refuses a policy carrying one
(`position_cycle`).

Note: a position runs where its operation runs and nowhere else. A `ship` over a working tree the
dirtiness guard reads as clean dispatches no `commit` (Section 12.2) and so enters no `before:commit`.
A position gates an operation, and where none is dispatched there is nothing to gate; a repository that
wants a unit to run whether or not a commit follows binds it to a result trigger rather than to a gate
(Section 5.1). What a unit could observe at the position is also nothing: a `before:commit` unit
inspects the working tree it runs in (Sections 6.6, 10.4), and a clean tree carries nothing for it to
find.

Note: the operations that reach the remote are exactly those Section 3.2 places host-side — among
the version-control operations, `provision`, `integrate`, `push` and `pull`. `status` and `diff` are
read-only and report against the base ref the checkout already holds (Section 6.4), so their
`ahead`/`behind` counts and their delta MAY be stale where the remote has moved. The asymmetry
follows from the trust split rather than being an omission: acquiring the base is a host-side act, and
marking a read-only operation host-side would deny it to a consumer running the engine in-sandbox
without credentials (Section 3.2). A caller that needs current figures runs `integrate` first.

### 4.2 Operation Result Envelope and Proto Classes

Every operation the reason registry covers completes with a typed result of the form
`<op>:<reason>` (Section 4.3). Every reason carries a proto **outcome class** — one of `done`,
`needs_caller`, `error` — which is part of the public contract because policy branches on it
through the `#class` fallback (Section 5.3):

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

Four reasons are **universal**, carried in the table with `(any)` in place of an operation and listed
once rather than repeated per operation: `failed` and `unsupported` are defined for every operation
this registry covers, and `blocked` and `hook_unanswered` for every such operation gated at a
lifecycle position (Section 4.1).

What the registry covers is stated as an invariant rather than as the list of operations it happens
to reach: an operation whose every outcome this specification reports as a configuration error
carries no reason here, and no universal reason reaches it. `load_policy` is that operation today —
its four outcomes are the ones Section 6.1 names, and giving them operation reasons as well would
register one condition twice (Sections 4.1, 6.11) — and an operation a `MINOR` release adds on the
same footing needs no exception written for it (Section 8.5). Every other operation is covered,
`provision` included: its result does not re-enter the machine as a trigger, which is a fact about
routing rather than about reporting, and the consumer classifies a typed result like any other
(Section 4.1).

Two further reasons are carried with `(any forge)` in place of an operation: `rate_limited` and
`forge_unavailable` are defined for every operation that **acts** on a forge call the condition
prevented — `push`, whose `pr_state` read a forge answers (Section 4.1), `create_pr`, `merge`, and
`await_checks`, whose every read is one. `status` reads a forge and is not among them, because it
reports the answer rather than acting on it and completes whatever the forge said; a refusal reaches
its caller as an output (Sections 4.1, 9.2).

| Operation | Reason | Class | Default need | Meaning |
|-----------|--------|-------|--------------|---------|
| `(any)` | `failed` | `error` | — | The operation failed, including when a `before:<op>` hook blocked it with an `error` result (Section 6.6). |
| `(any gated)` | `blocked` | `needs_caller` | `human_review` | A `before:<op>` gate or scan blocked the operation (Section 6.6). |
| `(any gated)` | `hook_unanswered` | `error` | — | A unit the engine ran at a `before:<op>` position — a hook, or the `pr_to_squash` transform (Section 10.3) — gave the engine no usable answer: `bound_elapsed`, `not_started` or `answer_unreadable` (Section 6.6). |
| `(any)` | `unsupported` | `error` | — | The operation requires a plugin capability the backend does not declare (Section 9.3). |
| `(any forge)` | `rate_limited` | `needs_caller` | `retry_after` | The forge refused because a budget was exhausted. The bucket and its `resets_at` are in `outputs.forge_budget` (Sections 8.2, 9.2). |
| `(any forge)` | `forge_unavailable` | `needs_caller` | `retry_after` | The forge did not answer, or answered that it is temporarily unable. The condition is in `outputs` (Section 8.2). |
| `provision` | `ok` | `done` | — | The checkout is present and current. |
| `provision` | `unreachable` | `needs_caller` | `human_review` | The remote could not be reached at `git_access` (Sections 8.1, 9.1). |
| `provision` | `store_unsupported` | `error` | — | A working tree was to be derived from a store the backend cannot share (Sections 4.1, 9.3). |
| `commit` | `ok` | `done` | — | A commit was created. |
| `commit` | `nothing_to_commit` | `done` | — | No changes to commit; benign no-op. |
| `commit` | `worktree_moved` | `needs_caller` | `reread_then_retry` | The working tree is no longer the one read at `before:commit`; re-read then retry. |
| `commit` | `identity_missing` | `needs_caller` | `supply_identity` | No caller-supplied commit identity is available (Sections 8.6, 10.1). |
| `integrate` | `ok` | `done` | — | The base was integrated. |
| `integrate` | `up_to_date` | `done` | — | Already current; no-op. |
| `integrate` | `merge_conflicts` | `needs_caller` | `resolve_conflicts` | Integration stopped on conflicts to resolve. |
| `integrate` | `base_unresolved` | `error` | — | The base could not be resolved (Section 6.4). |
| `integrate` | `base_unavailable` | `error` | — | The base could not be acquired from the remote (Section 9.1 `fetch_base`). |
| `integrate` | `identity_missing` | `needs_caller` | `supply_identity` | No caller-supplied commit identity is available for the merge commit (Sections 8.6, 10.1). |
| `push` | `ok` | `done` | — | The work branch was pushed. |
| `push` | `up_to_date` | `done` | — | Remote already current; no-op. |
| `push` | `non_fast_forward` | `needs_caller` | `integrate_then_retry` | Remote moved; integrate then retry. |
| `push` | `pr_closed` | `needs_caller` | `human_review` | The pull request is CLOSED/MERGED; refuse to push over it. |
| `push` | `rejected` | `error` | — | The remote rejected the push. |
| `create_pr` | `created` | `done` | — | A pull request was created. |
| `create_pr` | `updated` | `done` | — | The existing pull request was updated. |
| `create_pr` | `base_mismatch` | `error` | — | An existing pull request targets a different base. |
| `create_pr` | `conflict` | `needs_caller` | `human_review` | The pull request could not be created/updated cleanly. |
| `merge` | `ok` | `done` | — | The pull request was merged. |
| `merge` | `not_open` | `needs_caller` | `human_review` | The pull request is not open. |
| `merge` | `checks_pending` | `needs_caller` | `await_checks` | Required checks have not completed. |
| `merge` | `checks_failed` | `error` | — | Required checks failed. |
| `merge` | `conflict` | `needs_caller` | `resolve_conflicts` | The merge would conflict. |
| `merge` | `head_moved` | `needs_caller` | `reread_then_retry` | The pull request's head advanced after it was read; re-read then retry. |
| `merge` | `rejected` | `error` | — | Branch protection or forge policy refused the merge. |
| `await_checks` | `ok` | `done` | — | The required checks completed successfully. |
| `await_checks` | `checks_failed` | `error` | — | The required checks completed and did not pass. |
| `await_checks` | `still_pending` | `needs_caller` | `await_checks` | The invocation's read allowance ended with checks still pending (Section 8.1). |
| `await_checks` | `budget_floor` | `needs_caller` | `retry_after` | A supplied budget floor was reached with checks still pending, or the observed snapshot could not answer it (Sections 8.1, 9.2). |
| `await_checks` | `no_checks` | `done` | — | The forge reports no required checks for the pull request, so there is nothing to wait for (Section 9.2). |
| `pull` | `ok` | `done` | — | The local branch was updated. |
| `pull` | `conflict` | `needs_caller` | `resolve_conflicts` | The merge of the remote counterpart stopped on conflicts. |
| `pull` | `identity_missing` | `needs_caller` | `supply_identity` | No caller-supplied commit identity is available for the merge commit (Sections 8.6, 10.1). |
| `status` / `diff` | `ok` | `done` | — | The read completed. |
| `diff` | `base_unavailable` | `error` | — | The checkout holds no copy of the resolved base, so no delta can be produced (Section 6.4). |

The `Default need` column names the need an escalation on that result carries where nothing in the
policy named one. It is REQUIRED for every `needs_caller` reason and is `—` for the rest, whose class
defaults continue or fail rather than escalate (Section 5.4). The column is stated here rather than in
Section 8.4 because it is keyed by the pair this registry is keyed by: the built-in default has no
`escalate(reason)` to take a need from, a front-end binds its resolvers by the `need` token
(Sections 5.5, 8.4), and a need each engine derived independently would offer one driver a different
resolver key on every engine. A policy edge naming its own `escalate(reason)` supplies the need
instead, so the column is a default rather than a bound on what a repository may raise; Section 8.4
remains the `need` vocabulary and the definition of which needs are holds.

`commit:worktree_moved` and `merge:head_moved` take `reread_then_retry` rather than `human_review`,
and the difference is who can act. The state moved between the read and the write, so the repair is to
read it again and retry — which is exactly the re-entry a resume performs (Section 5.5) — and routing
it to a person sends one to look at a condition that has already changed. Neither reaches the default
under a front-end sequence, which routes both internally (Sections 12.2, 12.3); both reach it through a
bare `commit` or `merge` entry point (Section 8.1), which is the case a driver composing its own
sequence runs.

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

`commit:worktree_moved` is that condition one operation earlier — the state a `before:<op>` position
inspected moved before the operation acted (Section 6.6) — and takes the same class for the same
reason: the caller re-reads and retries, which `ship` does built in (Section 12.2). It is not
`nothing_to_commit`, whose `done` class reports a `commit` that was owed nothing where this one was
owed a working tree that is no longer there, and it is not the universal `failed`, on the argument the
paragraph above makes for its two. The three are the registry's whole answer to a state that moved
between the read and the write.

`identity_missing` and Section 8.6's `identity_invalid` name one condition at two points, and the
first dispatch is the boundary between them. An entry the identity precondition covers is refused
before the policy runs and never reaches `identity_missing`; an entry it does not cover MAY reach an
operation that writes a commit through a `run_op` edge (Section 5.2), and that operation reports
`identity_missing` — a result the machine routes like any other, so a repository MAY bind it and the
built-in `needs_caller` default escalates it (Sections 5.3, 5.4). Only absence reaches a dispatch: a
supplied identity is judged for shape before the policy runs whatever the entry (Section 8.6), so a
malformed one is `identity_invalid` in every invocation.

`provision:unreachable` is `needs_caller` where every other way provisioning can fail is the universal
`failed`, and the difference is whether the invocation's own arguments name what to change. A remote
the engine could not reach at `git_access` is a condition the caller repairs — the endpoint, the
credential, or the network between them, the first two supplied with the invocation (Section 8.1)
— and reporting it under `failed` would send a caller to read a diagnostic for a state its own
arguments describe. The reason names no cause beyond that: which of the three it was is not something
the engine can establish from the far side of a transport, and a reason per cause would be a registry
of the ways a network fails.

`provision:store_unsupported` is a reason of its own rather than the universal `unsupported`, and
the descriptor is what separates them. Whether a backend can derive more than one working tree from
one store is a static declaration (Sections 9.1, 9.3), so a consumer that derives more than one
against a backend declaring it cannot is refused at validation with `capability_unsupported`, before
anything is fetched (Section 6.11). What the declaration does not settle is what `store_location`
already holds: a store arranged in a way the selected backend cannot extend is a fact about that
location rather than about the descriptor, and `provision` reports `store_unsupported` for it, as
`integrate` reports `base_unavailable` for a base the checkout does not hold.

`rate_limited` and `forge_unavailable` are `needs_caller` where a forge refusal would otherwise be
the universal `failed`, and the class is chosen for the disposition it produces rather than for how
the condition reads. An `error`-class result no edge disposes of reaches the built-in default, which
**fails the flow** (Section 5.4). Carrying a throttle under `failed` therefore ends a unit of work
for a condition that clears on its own, through the same path and with the same finality as a
validation error that never will — and a repository that wrote `#error → fail`, which is what the
built-in default already does, gets a run failed by throttling. `needs_caller` is what Section 4.2
defines for an operation that cannot proceed without an action from the caller, and waiting is one.
The converse defect is the same axis read the other way: a consumer that retries `error`-class
results because some of them clear also retries a malformed pull-request title, which does not
become well formed on the ninth attempt.

The two divide the transient conditions **by repair** rather than by cause, which is why a 429 takes
one token and a server error, an expired bound (Section 8.1) and a transport failure share the
other. `rate_limited`'s repair is informed: the bucket that ran out and the time it refills are
already in `outputs.forge_budget` (Sections 8.2, 9.2), so a caller knows how long to wait and which
kind of work to hold back. `forge_unavailable`'s repair is uninformed — back off and try again, with
no reset time to aim at. Which of its three conditions occurred is diagnosis rather than routing and
is reported in `outputs` (Section 8.2), on the same reasoning `hook_unanswered` is reported that way:
the repair is the same shape in each case, and the condition is spelled as a token so what routes and
what diagnoses are both branchable. A backend MUST NOT report a permanent refusal under either
reason; a forge that refuses a request it will refuse identically on every retry is that operation's
own `error`-class result.

The two reasons are defined for the operations that act on a forge answer and not for `status`, and
the split falls there because the two kinds of operation lose different things to a refusal. A
`push`, a `create_pr`, a `merge` or an `await_checks` that could not reach the forge did not do what
it was dispatched to do, so the outcome is the operation's and belongs in its reason. A `status` that
could not reach the forge established five of its six outputs and not the sixth, so the outcome
belongs to the field: `pr_state_throttled` for a refusal on budget and `pr_state_unavailable` for a
read that established nothing (Section 4.1). Reporting the refusal as a reason would end an
inspection over one field a caller may not have been asking for, and reporting it as the universal
`failed` would additionally carry a condition that clears on its own under a class whose default
fails the flow. The two outputs are spelled apart for the reason the two reasons are: the repair is
informed on one side and uninformed on the other, and one token for both would tell a caller which
repair it has only by accident.

`await_checks:no_checks` is not `ok`, and the two are separated for what a consumer can see rather
than for what it must do. Both are class `done` and both continue the flow, so a repository binding
neither behaves identically under either; what one token would cost is the ability to tell a
repository whose checks all passed from one that configures none. That is how a merge gate stops
existing without anyone deciding to remove it — a required check dropped from branch protection, or
a workflow file that stopped matching, turns every later merge into an unchecked one, and under a
shared `ok` nothing in the record marks the day it changed. It is class `done` because a wait for
checks that do not exist is the benign no-op Section 4.2's definition already covers, and it is not
`needs_caller` because "a repository must have required checks" is a Way of Working and the engine
holds none (Section 1.1): a repository that holds it binds the reason and gets the stop, and one
that does not is not made to escalate on every merge. It is not `still_pending`, which reports a
bound that was reached, where nothing here was waited for.

`await_checks:still_pending` and `await_checks:budget_floor` both end a wait that found the checks
still running, and they are two reasons because the repairs differ: one is met by waiting longer and
the other by waiting for a bucket to refill, and a consumer that could not tell them apart would
raise the wrong bound — extending a deadline that was never the constraint, or conserving a budget
that was never short. Neither is `rate_limited`: nothing refused anything, and the loop did what it
was told for as long as it was told to. `still_pending` is stated over the invocation's read
allowance rather than over a supplied bound, so it also covers the invocation that authorized no
loop: its allowance is one read, and a single read that found the checks running has reached the end
of it (Sections 4.1, 8.1). Where an allowance and a floor are reached on the same read the reason is
`budget_floor`, which is the same repair distinction applied to one read rather than to two
outcomes: the floor is a fact about the snapshot the read observed, the allowance a fact about
whether there is another read, and reporting the constraint the read already met is what tells the
consumer which bound to raise. A floor the observed snapshot cannot answer reports `budget_floor`
too, the engine having failed to establish there is room to keep spending rather than having
observed room (Section 8.1). `checks_failed` is `error` and mirrors `merge:checks_failed`
because there is nothing left to wait for, which is the one outcome of the four that no further
waiting changes.

The `await_checks` **need** and the `await_checks` **operation** share a spelling deliberately.
`merge:checks_pending` has carried that need since this registry was written, and the operation is
now the thing that meets it: a consumer reading `need: await_checks` previously had to build a loop
and can now dispatch the operation the need is named after. Needs and operations are separate
vocabularies (Sections 4.1, 8.4), so nothing is ambiguous, and the shared name is the contract
describing its own remedy at the one point where it used to send a caller away to write machinery.

The version-control transport gains no transient reason here. A git remote publishes no budget and
no reset time, so `rate_limited`'s informed repair would have nothing to be informed by, and
`provision:unreachable` already routes the caller-repairable condition on that side away from
`failed` — its gloss names the endpoint, the credential and the network between them, which are the
invocation's own arguments. A `push`, `integrate` or `pull` whose git remote times out therefore
reports the reason it reports today. That is a decided scope rather than an omission, and the
narrowness is the point: a second token one word from `unreachable` is the hazard
`base_unresolved` and `base_unavailable` already show costs care to keep straight.

`blocked`, `failed` and `hook_unanswered` divide a `before:<op>` position's outcomes by what the hook
did. A gate that answered and refused with a `needs_caller` result is `blocked`; one that answered
with an `error` result is `failed` (Section 6.6). A gate that gave the engine no usable answer at all
is `hook_unanswered`, because a block is something the hook did and a hook that never answered decided
nothing — the engine did. Collapsing the two would put a gate that ran and refused and a gate that is
broken on one token carrying different repairs, and a repository binding `<op>:failed` to an action
could not tell them apart. Which of the three conditions produced `hook_unanswered` is diagnosis
rather than routing, and is reported in `outputs` under `unanswered_gates` (Section 8.2) rather than
in a reason of its own, because the repair is the same shape in each case. The condition is a token
rather than prose (Section 6.6), so what routes and what diagnoses are both spellings a consumer can
branch on.

The reason is spelled for the hook because that is the unit at almost every position, and it covers
the `pr_to_squash` transform at `before:merge` on the same terms (Section 10.3). What the token
names is the engine getting no usable answer from a unit it ran at a position, and the two cases
carry the same disposition — the operation does not act — so one reason serves both rather than a
second token carrying an identical repair. Which unit it was is what `unanswered_gates` names
(Section 8.2), alongside the condition.

Every operation this registry covers therefore has at least one `done` reason and at least one
`error` reason, so an `error`-class result is expressible for every one of them including the
read-only ones; every gated operation additionally has a `needs_caller` reason. The converse is the
invariant rather than the list of operations it happens to cover: an operation with no
`before:<op>` position carries neither `blocked` nor `hook_unanswered` (Section 4.1). An operation a
`MINOR` release introduces takes the same universal reasons on the same terms, gated or not
(Section 8.5).

## 5. The Action-Policy Machine

### 5.1 Triggers

A trigger is one of two kinds:

- **Lifecycle positions** around an operation: `before:commit`, `before:push`, `before:create_pr`,
  `before:merge`. A lifecycle position is matched exactly; it has no class form. `load_policy` and
  `provision` have no position and raise no trigger, running outside the machine (Section 4.1).
- **Typed operation results** `<op>:<reason>` (Section 4.3).

There is no third kind, and an event that is neither of these does not enter the executor. An event
the consumer observes — an agent milestone, or every task closing under a task model it runs
(Section 7.3) — selects which **entry point** the consumer invokes, which is what the `[driver]`
table it reads is for (Sections 6.9, 8.1). The engine is told `ship`; it is not told what led the
consumer to dispatch one. A trigger the engine matches is therefore one the engine itself produced:
a position it entered, or a result an operation it ran returned. That is what keeps a trigger's
producer and its matcher inside one invocation, and it is why the two kinds above are the whole of
the list.

### 5.2 Actions

An action is one of:

- `run_op(op, args?)` — run an operation (Section 4). Its result is itself a trigger, so a policy is a
  graph, not a flat list; the number of dispatches in one invocation is bounded (Section 5.6).
  Dispatching a gated operation runs its `before:<op>` position first (Sections 4.1, 6.6), so an
  operation reached through an edge is gated exactly as one a front-end sequence dispatches.
- `run(hook, context)` — run a repository hook (Section 6.6) in the declared execution context
  (Section 3.2).
- `escalate(reason)` — raise a need whose resolver the front-end binds (Section 5.5). An edge naming
  no `reason` raises the trigger's default need where the trigger is a `needs_caller` result
  (Section 4.3), and `human_review` otherwise: an `error` or `done` result a policy chose to escalate
  names no remedy of its own, and a lifecycle position has no outcome to take one from (Section 5.1).
- `create_task(spec)` — create a task through the consumer's task model (Section 7.3); a no-op when the
  consumer runs no task model.
- `set_state(target)` — apply a workflow-state transition through the consumer (Section 6.7).
- `notify(channel, payload)` — emit a notification through the consumer; a no-op when the consumer
  cannot deliver it.
- `park` — stop the flow and hold for intervention without failing it. The invocation ends at
  `needs_caller` carrying the `intervention` need (Sections 8.2, 8.4).
- `fail(reason)` — end the flow as failed. The invocation ends at `error` (Section 8.2). The `reason`
  is a repository-authored token rather than one of this specification's, and is reported in `message`
  and in `outputs` (Section 8.2) rather than in the envelope's `reason` field.

`create_task`, `set_state`, and `notify` are effected by the consumer, because they touch systems
(a task model, an issue tracker, a notification channel) outside the VCS/forge domain; the engine
emits the intent and the consumer performs it. `run_op` and `run` are the engine's own.

A consumer need not be able to effect every such action. A consumer may be a human at an interactive
prompt (Section 1.3), with no task model, no tracker binding, and no notification channel, so a policy
using these actions MUST behave predictably against a consumer that cannot perform them. Which it can
is the consumer's own declaration, supplied as `effectable_actions` (Section 8.1) and judged before
the policy runs (Section 6.11), rather than something the engine infers from the entry point or the
front-end: a driver with no notification channel and an interactive front-end wired to a tracker are
both ordinary, so an inference either way would refuse a valid policy or admit a stranding one with
no argument the consumer could make to correct it. Each action's disposition against an action
outside that set is fixed:

- `create_task` and `notify` are benign no-ops. The engine MUST surface each such intent in the result
  envelope (Section 8.2) rather than drop it, on the same principle that forbids silently dropping an
  operation outcome no action disposed of (Section 5.4): an intent the engine emitted and no consumer
  performed is reported, so a policy that degrades against a lesser consumer degrades visibly.
- `set_state` is a configuration error, caught before the policy runs (`set_state_unbound`,
  Section 6.11), because a workflow state that never advances strands the flow rather than merely
  losing information.

The split is also why `effectable_actions` defaults to empty (Section 8.1). A default admitting every
action would validate a `set_state` policy against a consumer that cannot advance a state and strand
the flow at the first transition, which is the outcome the reason exists to refuse; a consumer that
can effect one says so.

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

The `#class` fallback lets a policy branch on the three stable classes without enumerating every
reason, so a new reason token added in a compatible release routes to an existing class edge. It
applies to typed operation results alone: a lifecycle position has no outcome to classify
(Section 5.4), which is the other of the two trigger kinds.

### 5.4 Unmatched Policy and Determinism

- An unmatched **lifecycle position** is a benign no-op: nothing runs at the position and the operation
  proceeds. A position is an offered interposition point, not a result requiring disposition — the
  required positions (Section 4.1) are available to every policy and most policies bind only some, so
  leaving one unbound is the ordinary case rather than an omission. This is also why a position has no
  class fallback (Section 5.3): there is no outcome to classify.
- An **operation outcome no action disposed of** MUST be fail-safe: the executor parks or fails the
  flow with the operation's proto reason surfaced. It MUST NOT be silently dropped, because a dropped
  operation outcome would strand a flow. The built-in default for the `error` class is `fail`; for
  `needs_caller`, `escalate` carrying the reason's default need (Section 4.3); for `done` with no
  edge, continue — which names where control goes: back to whatever made the dispatch, at the point
  it made it. That is a front-end sequence (Section 12) or, for a bare entry point, the driver
  (Sections 7.3, 8.1), and it is the same place a `run_op` edge's own result returns to when its
  chain of substitutions ends. `continue` is an outcome of the machine rather than an action a
  policy can bind (Section 5.2).
- An outcome is **disposed of** by an action that ends the flow — `escalate`, `park`, `fail`
  (Section 5.6) — or by a `run_op`, whose own result takes its place in the machine. The remaining
  actions emit a consumer-effected intent or run a hook and return (Section 5.2), leaving the
  traversal exactly where an unmatched outcome leaves it, so an outcome that matched one of them
  reaches the same built-in default an unmatched outcome reaches. A `push:non_fast_forward → notify`
  edge under a single-operation entry point therefore reports the push result and escalates
  `integrate_then_retry`, rather than ending a run that neither escalated, parked nor failed. The rule
  is stated over disposition rather than over matching because what strands a flow is a result nothing
  acted on, and whether an edge happened to match is not that.
- The policy graph MUST be deterministic: at most one edge per trigger, where a duplicate is a
  configuration error (Section 6.11). The trigger is the whole of the key: an edge is selected by
  the ladder (Section 5.3) and by nothing else, so the same `repo.policy.toml` yields one operation
  flow whichever front-end runs it (Section 13.1). The engine matches no scope alongside the
  trigger, and a repository that wants one trigger to mean different things at different points in
  its own workflow does that scoping in the table its consumer reads (Section 6.7), which is keyed
  on a `from` state and matched by the party that effects the action.

### 5.5 Escalation Binding

`escalate(reason)` names a need and the front-end binds the resolver:

- Interactive (`ship`/`land`): `escalate` returns a `needs_caller` result (Section 8.2) to the human
  caller, carrying the escalation payload (Section 8.4). The human resolves and re-invokes.
- Embedded driver: the driver binds `escalate` to its own resolver — for example creating an
  agent-assigned task (Section 7.3) — and resumes the flow when the need is met.

Because both front-ends run the same executor over the same policy, `escalate` is the single point at
which their behavior legitimately differs.

A resume re-enters **the point that raised the need**. Where an operation result raised it, the resume
re-dispatches that operation, which runs its `before:<op>` position first as any dispatch does
(Section 5.2); where an edge at a lifecycle position raised it — the case whose escalation carries a
null `op` (Section 8.4) — the resume re-enters that position. A gate is therefore re-run rather than
bypassed, and the answer is the same for `<op>:blocked` and `<op>:hook_unanswered`: a gate that
refused may now pass and a gate that gave no usable answer may now answer, and neither yields a pass
the hook did not give (Section 6.6). A resume that landed past the position would run an operation no
gate had inspected, which is what the position exists to prevent.

A resume **continues the flow** from the point it re-entered. The result the re-entry produces is
disposed of by Section 5.4 as any result is, and where that disposition returns control it returns
to whatever made the dispatch, at the point it made it: a front-end sequence resumes its own
traversal from where the re-entered dispatch sat (Sections 12.2, 12.3), and a re-entered lifecycle
position runs its edges and the operation it gates proceeds as it does under any dispatch. A `ship`
that escalated `resolve_conflicts`, whose caller resolved the conflicts, therefore retries its push
and reaches `create_pr` in the resuming invocation rather than reporting the re-dispatched
`integrate` and stopping. Section 5.4 already names that disposition and its name is `continue`, so
a resume that stopped at the re-entered result would need a fourth disposition the section does not
provide.

The single-operation case is a **consequence** of that rule rather than an exception to it: where
the entry point is a bare operation the remainder of the flow is empty, so the invocation reports
the result and ends. A driver composing its own sequence out of bare operations gets the same
behavior for the same reason — the sequence is the driver's and not the engine's, so there is
nothing for the engine to continue past the operation the driver invoked, and the driver resumes its
own composition as it drives it (Sections 7.3, 8.1).

A resume is carried by the invocation that resumes rather than held by the engine. An invocation that
ends at `needs_caller` with a **resolvable** need returns a `resume_token` in `outputs`, and an
invocation supplying it as the `resume` argument re-enters the point that token names
(Sections 8.1, 8.2). The engine holds nothing between invocations — it takes a credential for the
duration of one and persists none beyond it (Section 1.3) — so a resume that depended on engine-side
state would be expressible under an in-process API and not under a subprocess, and the contract is
the same under either (Section 8). A need that names a **hold** carries no token, `intervention` and
`flow_exhausted` being unresolvable (Section 8.4), so a front-end reads the prohibition against
resuming either off the envelope rather than off the policy that produced it.

Nothing a position established carries across a resume. The state a position inspected is read again,
so an operation conditioned on an inspected identity — `expected_worktree`, `expected_head`
(Section 6.6) — is conditioned on what the re-entered position saw. An engine that carried the earlier
expectation forward would hand an operation state no position had inspected since, which is the
condition Sections 4.3 and 6.6 exist to report rather than to produce. The token is held to that rule
and not excepted from it: it carries the point to re-enter, the root trigger the chain that point
belongs to descends from, and the flow bound already spent, and it MUST NOT carry
`expected_worktree`, `expected_head`, or anything else a position established. A value that already
carries three things is where a fourth looks harmless, which is why the prohibition is stated over
the token rather than left to follow from the paragraph above it. A trigger is admitted for the same
reason the count is: both are control-flow state — what the flow was doing — rather than something a
position inspected, so neither is what this rule refuses.

The **root trigger** is the result of the sequence's own `run_op` that the chain the point belongs
to descends from (Sections 12.1, 12.2). It is what selects the control transfer once the re-entry's
result is disposed of, the transfer being a property of the trigger rather than of the disposition
an edge replaced (Sections 12.2, 12.3) — so without it a resumed `integrate` has no landing,
`integrate` appearing in Section 12.2 only inside a `push:non_fast_forward` disposition. It is
stated as the **root** rather than as the trigger an edge substituted, because Section 12.2 routes
`push:non_fast_forward` to `integrate` built in and escalates `integrate:merge_conflicts` with no
edge involved: phrased over substitution the field would be absent exactly where the built-in path
needs it. It is not needed where the point is a lifecycle position, the gated operation's own result
being the root the sequence transfers on.

Each of the three parts is fixed-width, and none grows with the policy graph. Section 5.4 has a
`run_op`'s own result take the place of the outcome it disposed of rather than stack beside it, so a
substitution chain of any length still descends from one root and one root is what the token names:
naming a point in the flow is not licence to serialize a traversal. The trigger MUST be carried by
its **registry token** (Sections 4.3, 5.1) rather than by an ordinal into an enumeration the engine
generated, because an operation or a reason added by a MINOR release shifts such an enumeration, and
a token issued before it then decodes into a different trigger — silently, from a record that still
looks valid. What the token has to determine is fixed here; how it spells any of it stays the
engine's own (Sections 8.1, 13.3).

Any **re-entry** a resume causes counts against the flow bound (Section 5.6). The count is stated over
re-entry rather than over the dispatch it usually is, because a resume into a lifecycle position
re-enters a position inside a dispatch whose count is already spent: a resolver that always resolves
would otherwise loop there with nothing to stop it. Both shapes therefore reach `flow_exhausted`
rather than running indefinitely, which is the property Section 5.6 holds for every other loop the
schema can express. The count is what the `resume_token` carries alongside the point and the root
trigger, so it accumulates across a chain of resumed invocations as it does within one: a bound that
restarted at each re-invocation would hold for a driver whose resolver returns in-process and fail
for a front-end whose caller resolves and invokes again, and the property would then depend on an
encoding the consumer chose for unrelated reasons.

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
- `escalate`, `park` and `fail` end the flow. A front-end that resumes an `escalate` (Section 5.5)
  re-enters the flow at the point that raised the need, so an `escalate` a front-end resolves is the
  one ending an invocation can carry on from — and every such re-entry counts against the bound below,
  which is why it does not reopen the question this section answers.

Every non-terminating flow is therefore an unbounded sequence of `run_op` dispatches and resume
re-entries, and a bound on that count bounds every loop the schema can express — including one a
lifecycle position introduces, where an edge on `before:push` dispatches `integrate` and the retried
`push` re-gates the position.
One shape is refused before it runs rather than bounded: a cycle of lifecycle positions, each
position's `run_op` edge dispatching the operation the next position gates, reaches no operation on
any traversal and is a configuration error (`position_cycle`, Section 6.11). The bound holds every
loop that runs operations, which is every loop whose cycle passes through a typed operation result.

A conforming executor MUST bound one flow by a count of `run_op` dispatches and resume re-entries
(Section 5.5). The bound is over the **flow** rather than over one invocation of it: a flow an
`escalate` ended and a resume continued is one flow, and a resumed invocation continues from the
count its `resume_token` carries rather than starting a fresh budget (Sections 5.5, 8.1). Stated over
the invocation instead, the bound would hold for an embedded driver whose resolver returns inside one
run and not for a front-end that returns to its caller and is invoked again — so the answer this
section gives to non-termination would depend on which front-end asked. The bound's value is
`Implementation-defined` and MUST be documented (Section 13.3); it MUST admit at least 64 dispatches,
and an engine that lets a deployment configure it MUST hold the configured value to the same floor.
The floor's exact value is arbitrary; that it is
fixed is not, because it is what keeps two engines with different bounds in agreement on every policy
that terminates within it.

An `await_checks` dispatch counts **once**, however many reads it makes (Sections 4.1, 8.1). Its
reads are bounded by the await parameters the invocation supplied, so the two bounds measure
different things and neither substitutes for the other: this one counts how many operations a policy
traversal runs, and that one counts how long one operation waits. Counting each read here would make
a policy's flow budget depend on how long a CI run happened to take, so a policy that terminates on
a fast build and exhausts the bound on a slow one — which is the one thing this bound exists to keep
two engines agreeing about.

The bound is a count, not a cycle detector. A repeated `(trigger, edge)` pair is ordinary rather
than pathological: `push:non_fast_forward → integrate → push` is the built-in routing (Section
12.2), and a base branch that moved twice produces it twice; `merge:head_moved → before:merge →
merge` is another (Section 12.3), and a pull request pushed to twice produces that twice;
`commit:worktree_moved → before:commit → commit` is the third (Section 12.2), and a worktree written
to twice during the gate produces that twice. An
executor that refused a graph containing a cycle would refuse that routing, and one that stopped at
a repeated edge would abort a correct flow that was about to converge. What separates a converging
flow from a looping one is how many operations it takes, not whether it revisits an edge. That
measure is also what separates the three pairs above from the shape validation refuses: each pair
takes one operation per turn and ends when the state that operation reports settles, while a cycle
made only of positions takes none, so the count measures nothing that could converge.

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

The bound Section 6.6 requires on a hook is not one of those, and the difference is what each bound
stops. A bound on a running flow stops the **executor**: the pending `run_op` is not dispatched and
the invocation ends. A hook bound stops **one unit at one position** inside a dispatch that is already
under way; the flow is not stopped, the gated operation reports `hook_unanswered` (Section 4.3), and
that result re-enters the machine as any operation result does. Routing it to `flow_exhausted` would
say the graph does not converge for a flow whose graph was never in question, and would discard the
two facts a caller acts on — which position, and which unit.

## 6. `repo.policy.toml` Schema

### 6.1 File Discovery and `vcsx.toml` Merge

- `repo.policy.toml` is the repository-owned Way-of-Working file. Its path is resolved relative to the
  repository root; the discovery precedence (explicit override, then the repository default) is
  `Implementation-defined` and MUST be documented.
- An engine-native `vcsx.toml`, when present, is merged into the same surface; `repo.policy.toml`
  keys take precedence on conflict. A consumer MAY present the merged surface as one document. Its
  path is resolved relative to the repository root as `repo.policy.toml`'s is, and its discovery
  precedence is `Implementation-defined` and MUST be documented on the same terms. Both files the
  loader reads are addressed rather than only one because two engines taking the second from
  different places merge different documents from one revision and run different policies for one
  repository, which no value a consumer can read reports.
- **A policy that cannot be used yields one disposition and four diagnoses.** Four conditions leave
  the engine without a policy it can run:
  - the source it is read from could not be read — `policy_source_unreadable`;
  - no `repo.policy.toml` was discovered there — `policy_not_found`;
  - a discovered file, or a `vcsx.toml` merged into it, does not parse — `malformed_policy`;
  - a discovered file parses and is invalid — one of the remaining Section 6.11 reasons.

  In every one of the four the engine reads no policy, refuses to run, and reports
  `usage_or_config` with the reason naming the cause (Section 6.11). The disposition is one because
  a consumer's response is one — it cannot run this repository's policy — while the reasons stay
  four because the **repair** differs: make the source readable, commit the file, fix the syntax,
  fix the value. Diagnosis belongs in the reason and the log; it does not belong in the disposition.

  `policy_source_unreadable` names no cause beyond that. Whether the branch is absent, the remote
  unreachable, or the credential refused is not something the engine can establish from the far side
  of a transport, and a reason per cause would be a registry of the ways a network fails — which is
  the reading `provision:unreachable` already takes (Section 4.3).
- `provision` is the one entry point that runs where no policy could be read, whichever of the four
  conditions holds, because it is the operation that obtains the repository the file is in
  (Sections 4.1, 6.11). Its dispatch reads no policy and is validated from the Section 6.11 inputs
  that are not the document.
- Unknown keys SHOULD be ignored for forward compatibility.
- The consumer configuration (Section 8.1) is the loader's second input and carries no key this
  surface carries. What a clone inherits unchanged is `repo.policy.toml`'s and what is needed to
  obtain the clone is the consumer's (Section 6.2), so the two sets are disjoint and the precedence
  rule above governs the `vcsx.toml` merge alone, needing no exception for the consumer's half.

### 6.2 `[requires]`

- `version_floor` (string) — the minimum engine version the policy requires, stated as a
  `MAJOR.MINOR` version (Section 8.5). A value that is not one is a configuration error
  (Section 6.11) rather than a floor the engine compares.

The table states what the policy document requires of the engine reading it, and selects nothing. The
values needed to obtain a repository cannot be configured inside that repository: reading
`repo.policy.toml` needs the repository, obtaining the repository needs the forge selection, its
access parameters, its credentials and the remote, and reading those from the file needs the
repository again. Those values are therefore the consumer's and arrive with the invocation
(Section 8.1). What `repo.policy.toml` holds is what a clone inherits unchanged — the scope, the base,
the policy edges, the hooks, the transitions, the message configuration and the task tables — none of
which is consulted before the repository exists.

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

- `branch` (string, OPTIONAL) — the base branch the pull request targets and `integrate` pulls from.
  It is the repository's own contribution to a value the invocation and the consumer configuration
  may also supply, and the lowest of the three in precedence: the invocation's `base_branch` wins,
  then the consumer configuration's, then this (Section 8.1). That precedence holds under
  `policy_source = "policy_branch"`; under `target_branch` this section supplies nothing, for the
  reason stated below. Where no applicable source supplies one, the invocation is refused before the
  policy runs, in the scope Section 8.6 states for the mode.
  - Default: unset — the consumer supplies the base, or the entry does not need one.
- `resolve` (string, OPTIONAL) — a base-resolution strategy when a single `branch` is insufficient:
  - `fixed` (Default) — `branch` is the base.
  - `by_prefix` — the base is selected from a table mapping work-branch-name prefixes to base branches
    (longest-prefix-wins, with a required empty-prefix default). This models track-aware bases without
    naming a specific deployment's mapping.
- `prefixes` (table, OPTIONAL) — the prefix→base map used when `resolve = by_prefix`. A missing or
  malformed map is a configuration error (Section 6.11); the engine surfaces
  `integrate:base_unresolved` / `create_pr:base_mismatch` rather than guessing.

Under `policy_source = "target_branch"` (Section 8.1) this section contributes nothing to the base.
The base then resolves from the invocation's `base_branch`, then the consumer configuration's, and
from nothing else: the mode reads host-side policy from the pull-request target, so every key here —
`branch`, `resolve` and `prefixes` alike — sits in the document the base is what locates. That is
Section 8.1's rule for the policy branch applied to the argument playing its role under this mode,
and it holds for the same reason: a branch named inside the policy cannot select the revision the
policy is read from. Where neither source supplies one the invocation is refused before the policy
runs, whatever the entry (Section 8.6).

One invocation resolves one base. Under `target_branch` the base is fixed before the policy is read
and this section cannot move it afterwards; under the default mode the policy is read first and this
section is the lowest of the three sources, as above.

Base resolution runs before `[[branch]]` section selection and reads no section, the resolved base
being what selects one (Section 6.10). That is why a section MUST NOT carry `[base]` or `[scope]`:
either would supply the value that selects it. The order is stated in both places rather than in one,
because an implementer reading either section needs it and neither section is the obvious home for
it.

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
belonging to the resolved remote (Section 8.1), so `ahead_behind` and `diff` report against the base
`integrate` would bring in rather than against whichever copy a backend preferred.

Base resolution is configuration, not a hook. An operation reads the resolved base; it never accepts a
base from untrusted content.

### 6.5 `[policy]` Edges

The action-policy machine (Section 5) is expressed as a table of edges. Each edge binds a trigger to
an action. The trigger is the whole of an edge's key: the engine matches no scope alongside it, so
at most one edge is bound to any trigger (Section 5.4).

```toml
[[policy.edge]]
on = "push:non_fast_forward"   # trigger: lifecycle position | op:reason | op:#class | #class
do = "run_op"                  # action (Section 5.2)
op = "integrate"               # action argument
# then the resulting integrate:* outcome re-enters the machine

[[policy.edge]]
on = "before:commit"
do = "run"                     # run a hook
hook = "scan-content"          # a hook name (Section 6.6); its context
                               # follows the artifact that declares it

[[policy.edge]]
on = "#error"                  # class fallback: any error with no more-specific edge
do = "escalate"
```

An edge's `on` MUST be a trigger the engine recognizes: a known lifecycle position, or an `op:reason`
/ `op:#class` / `#class` form over a known operation (Section 5.1). A duplicate `on` is a
configuration error (Section 5.4). An edge MUST also carry the arguments the action its `do` names
needs in order to be dispatched — `op` for `run_op`, `hook` for `run` — and an edge that omits one
is a configuration error (Section 6.11).

`reason` is OPTIONAL on an `escalate` or a `fail` edge, and an edge omitting it is well formed:
neither action needs it to be dispatched. An `escalate` without one raises the trigger's default need
(Sections 4.3, 5.2), and a `fail` without one is reported by its trigger alone (Section 8.2).

**An edge does not declare its execution context.** Which context an edge carries is fixed by the
artifact it is declared in, as a hook's is (Section 6.6): one declared in `repo.policy.toml` is
host-side, one declared in the consumer's in-sandbox artifact is in-sandbox. The engine still
receives a context for every edge, because it is handed one merged surface and never sees two
artifacts (Section 3.2) — the consumer tags each edge while assembling that surface, which is the
same act as sourcing it by trust.

Deriving it rather than declaring it removes a combination the declared form admitted: an edge the
working tree supplied, declaring itself `host_side`, dispatching a credentialed operation. Under
derivation that is not a rule to enforce but a thing that cannot be written, because a host-side
edge is one the working tree did not declare.

What the context decides is the dispatch, and it decides it for one action. An edge's context is
what Section 11's credential guarantee is stated over, so an in-sandbox edge's `run_op` naming an
operation that reaches the remote receives no credential and reports that operation's own reason at
the dispatch (Sections 4.3, 8.6). For the other actions it decides nothing: a `run` edge's hook
carries its own context and resolves its unit by it (Section 6.6), and the remaining five receive
neither the working tree nor a credential. No context is derived from the operation an edge names —
what Section 3.2 says about which operations reach the remote states what a dispatch needs, not
where an edge came from.

A `context` key on an edge is ignored rather than refused, under Section 6.1's rule for unknown
keys: a policy written against the declared form stays valid, and the context it names is not
consulted.

A `from` key on an edge is ignored rather than refused, under the same rule: a policy written
against a version that scoped an edge by workflow state stays valid, and the state it names is not
consulted. Two edges differing only by `from` are therefore a duplicate `on` and are refused as one
(Section 6.11), which is the report that matches what the engine does with them.

### 6.6 `[hooks.engine]`

A hook is a named unit `run` invokes:

```toml
[hooks.engine.notify-release]
run = "..."                    # engine-invoked unit; its form is Implementation-defined
```

The table's keys:

- `run` (string) — the engine-invoked unit. REQUIRED for a declared hook; its form is
  `Implementation-defined` and MUST be documented (Section 13.3). A `[hooks.engine.<name>]` table
  declaring no `run` is a configuration error (Section 6.11).

The namespace is `hooks.engine` rather than `hooks` because a consumer MAY carry hooks of its own
under `hooks` — Symphony's workspace lifecycle hooks are one such set — and two schemas sharing one
table have no rule for a name they both want. Prefixing both is what makes each set's owner readable
where it is declared, rather than inferable from whether an entry is a table or a scalar. A
consumer's namespace is not this specification's to define; that it is disjoint from `hooks.engine`
is.

**A hook does not declare its execution context.** Which context a hook runs in is fixed by the
artifact it is declared in: one declared in `repo.policy.toml` is host-side, one declared in the
consumer's in-sandbox artifact is in-sandbox. The engine still receives a context for every hook,
because it is handed one merged surface and never sees two artifacts (Section 3.2) — the consumer
tags each hook while assembling that surface, which is the same act as sourcing it by trust.

Deriving it rather than declaring it removes a combination the declared form admitted: a hook marked
`host_side` whose unit the working tree supplies. Under derivation that is not a rule to enforce but
a thing that cannot be written, because a host-side hook is one the working tree did not declare.

Where the unit is resolved from follows the context, and follows it for the same reason the
declaration does:

- An `in_sandbox` unit resolves from the **working tree**, which is where it runs and where the
  consumer sources in-sandbox policy from (Section 3.2).
- A `host_side` unit resolves from the **same source the host-side policy was read from**, and MUST
  NOT resolve from the working tree. A consumer that sources host-side policy from a trusted
  revision so an untrusted working tree cannot alter it gains nothing if the program that policy
  names is one the working tree supplies. The engine MUST NOT run a `host_side` unit with the
  working tree as its working directory; it supplies the working tree's location to the unit
  instead, so a host-side hook can still inspect the tree — reading it as data is what a scan or a
  build check is for — without executing anything the tree carries.

This specification names no branch here, because the engine has none: which revision counts as
trusted is the consumer's (Section 3.2), and this rule says only that the unit and the declaration
come from the same one. Making that source available as a directory is the backend's, through
`export_source` (Section 9.1): a revision is not a directory, and getting a tree out of one is what
a backend knows rather than what an engine does. How a unit is addressed within that source, and
what working directory the engine gives it, remain `Implementation-defined` and MUST be documented
(Section 13.3).

Where the form the engine's `run` unit takes requires the source materialized and the selected VCS
backend declares no `export_source`, a merged surface declaring any `[hooks.engine]` unit is refused
at validation with `capability_unsupported` (Sections 6.11, 9.3). The condition is the engine's
declared unit form rather than the unit: a form that is a command line carries no statement of
whether it names a path in the source, so a per-unit condition could not be evaluated from the
configuration this specification specifies, while the engine's form and the backend's declaration
are both static and held before the policy runs. An engine whose form resolves a unit from the
declaration itself — a task the consumer registered under a name the policy writes — materializes
nothing and reaches neither the capability nor the refusal.

How the engine treats a hook:

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

A hook is the one place the engine hands control to a program this specification does not describe, so
an engine MUST bound the time it waits for a hook to answer. The bound's value is
`Implementation-defined` and MUST be documented (Section 13.3); it MUST admit a configured value of at
least 600 seconds, and an engine that lets a deployment configure it MUST hold the configured value to
the same floor. The floor's exact value is arbitrary in the way Section 5.6's is; that it is fixed is
not, because a repository whose `before:commit` gate is its own test suite otherwise runs on one
engine and not on another.

The bound is stated over the hook because that is the unit at almost every position, and it holds
for every unit the engine runs at a lifecycle position and waits on. The `pr_to_squash` transform
(Section 10.3) is the one such unit no `[hooks.engine]` table declares, and it is bounded on the
same terms and reports the same reason: what makes the bound necessary is that the program is one
this specification does not describe, not which key named it.

What exceeding the bound produces divides with the division the bullets above already draw, by whether
anything waits on the answer:

- A `before:*` hook that has not answered when the bound elapses is stopped, and the gated operation
  reports `hook_unanswered` (Section 4.3). The operation does not act: a gate that did not answer
  never yields a pass, and the result re-enters the machine, so a repository MAY bind it and the
  built-in `error` default fails the flow where none does (Sections 5.3, 5.4). A hook the engine could
  not start, and one whose answer the engine could not read in the form it fixed, reach the same
  reason — the engine got no usable answer, whichever way it failed to get one.
- An `after`/result-triggered hook that gives the engine no usable answer — the same three conditions,
  since a hook that could not be started answers nothing whichever half of the division it is on — is
  stopped where it is still running, and the flow continues unchanged, which is "best-effort and does
  not block" read literally. Stopping it costs the flow nothing, where waiting holds an invocation open
  indefinitely. The engine reports each such hook in `outputs` (Section 8.2) rather than dropping it, on
  the principle that forbids silently dropping an intent no consumer performed (Section 5.4).

The three conditions are named tokens, so the diagnosis a consumer reads is spelled the same on every
engine:

- `bound_elapsed` — the unit was still running when the bound elapsed, and was stopped.
- `not_started` — the engine could not start the unit.
- `answer_unreadable` — the unit answered, and the engine could not read the answer in the form it
  fixed.

The engine reports the condition for every hook that gave it no usable answer, on either side of the
division above (Section 8.2). The token diagnoses rather than routes: the repair is the same shape in
each case, which is why Section 4.3 spends one reason on all three, and which of the three occurred is
what separates a gate that hung from a unit that is not there. Both are repairs to the hook and
neither is a repair a consumer can guess from the reason alone.

The bound is the consumer's, and `[hooks]` carries no key for it. A `timeout_ms` a repository writes
here is an unknown key and is ignored (Section 6.1). The reason is Section 3.2: the in-sandbox half of
this table is worktree-sourced by design, so a bound declared here would be a bound the bounded thing
sets — a hook that hangs and a hook that raised its own ceiling to a day are the same hook — and the
engine labels contexts without enforcing the sourcing rule, so it never learns which revision a value
came from and cannot admit the key host-side while refusing it in-sandbox. The bound arrives the way
Section 11 has the credential arrive: the repository owns which unit runs, and the consumer owns how
long the machine will wait for it.

Note: the bound is on the engine's wait, not on the machine. Stopping a unit does not end what that
unit started, so a hook that answers and leaves a descendant process holding the channel the engine
reads is read from until the bound elapses. The invocation is bounded; the host is not, and a consumer
that needs the stronger property provides it around the engine.

A position gates the operation on the state it inspected. Where that state has an identity the
backend can name, the engine takes the identity from the read the position inspected the state
through, and the operation acts on that state or reports that it could not: `merge` conditions on
the pull request's head (`expected_head`, Section 9.2) and `commit` on the working tree's identity
(`expected_worktree`, Section 9.1), each reporting `merge:head_moved` or `commit:worktree_moved`
rather than acting on state no position inspected. The guarantee is not that the state holds still —
nothing the engine controls stops another writer — but that a state which moved is reported rather
than acted on, and the retry re-dispatches the operation, which re-runs the position (Sections 12.2,
12.3).

The other two positions carry no identity of their own, and what each guarantees is stated where it is
realized. `before:create_pr` inspects the title and body the engine composed, and the operation writes
those same values with nothing recomposing them in between (Sections 10.2, 10.4). `before:push`
inspects the work branch and the operation sends the branch as it stands, so a branch that gained a
commit in between sends one the position did not inspect — a commit this engine gated at
`before:commit`, a mechanical merge commit an `integrate` or a `pull` wrote whose content is the
resolved base or the branch's own remote counterpart (Section 10.1), or a commit from a writer outside
the engine, which is the consumer's boundary rather than the engine's (Section 11). What the window
admits is bounded by the position one operation earlier rather than by an identity of its own.

The requirement is stated over the positions rather than per position because a gate is only a gate if
what it inspected is what proceeds. An operation that acted on other state returns a `done`-class
result for a run nothing gated, and the envelope carries nothing that distinguishes it from a run that
was gated (Sections 4.2, 8.2) — the failure Section 9 forbids one layer down, where a capability MUST
NOT report a condition it could not resolve as the value's absent case.

### 6.7 `tracker.transitions`

The workflow-state transition graph (`tracker.transitions`) is a set of `set_state` bindings keyed on a
`from` workflow-state name and a trigger:

```toml
[[tracker.transitions]]
from = "In Progress"
on   = "pull_request_opened"   # a condition the consumer observes
to   = "Human Review"          # set_state target
```

The graph is over neutral state names; mapping a state name to a tracker's representation is the
consumer's. An unmatched `(from, on)` transitions nothing. The graph MUST be deterministic (at most
one `to` per `(from, on)`), which the engine validates as part of the document it loads
(`duplicate_transition`, Section 6.11).

This table is read by the **consumer**, not matched by the executor, and it travels in
`repo.policy.toml` for the reason `[tasks]` and `[driver]` do (Section 6.9): the repository owns the
wiring, and the party that effects the action owns the matching. `set_state` is a consumer-effected
action (Section 5.2) and a tracker is outside the VCS/forge domain, so the condition `on` names is
one the consumer observes in its own run — a milestone its agent signalled, an outcome it saw, or a
condition across the tasks it manages. This specification therefore fixes neither that vocabulary nor
its spellings; a consumer that runs a tracker publishes them, as Symphony does (`SPEC.md`
Section 11.6). What the engine matches is Section 5.1's two kinds, both of which it produces itself.

A repository MAY of course want a transition on something the engine reported, and nothing here
prevents it: the consumer receives every operation result in the envelope (Section 8.2) and is free
to admit `<op>:<reason>` spellings into the vocabulary it publishes. That is the consumer's choice
about its own table rather than the engine matching one.

### 6.8 `[messages]`

Message formulation is repository configuration; the engine bakes in no format (Section 10).

```toml
[messages.commit]
# identity (author/committer) is supplied by the consumer, distinct from content;
# the commit body is authored by the caller and validated at before:commit.

[messages.pr]
body_source = "auto"           # "auto" (compose) | "agent" (caller prose) | "template"

[messages.squash]
strategy   = "squash"          # merge strategy: "squash" | "merge" | "rebase"
transform  = "pr_to_squash"    # a repo-owned transform applied at before:merge (Section 10.3)
```

No table here binds a content scan. A scan is declared as a hook and run by a `[policy]` edge at a
lifecycle position (Sections 6.5, 6.6, 10.4), which is the binding a repository writes for every
other unit the engine hands control to at a position; a second surface for one unit family would
also make a position no edge binds run something, where Section 5.4 has such a position run nothing.

- `strategy` (string, OPTIONAL) — the merge strategy the `merge` operation requests of the forge
  (Sections 9.2, 10.3). One of `squash`, `merge` or `rebase`. A value the schema does not admit is a
  configuration error (Section 6.11) rather than a silently defaulted one, because Section 6.1's
  forward-compatibility rule covers a key the schema does not declare and not a declared key whose
  value it does not admit.
  - Default: `merge`.

The default is stated here rather than left to the engine because it decides what a `land` writes to a
repository's base branch where the policy says nothing, and two conforming engines choosing
differently write different durable history there — a difference visible only to someone reading the
log afterwards. `merge` is the default because it is the one strategy of the three under which the
commits the engine wrote survive into that history as written: each was gated at `before:commit`
(Section 4.1) and attributed to the caller-supplied commit identity (Section 10.1), where `rebase`
re-parents them and `squash` collapses them into a commit the code host authors. Preferring the
strategy that preserves what the engine gated is the posture this specification states wherever it
states one — no operation that updates the work branch rewrites, drops or re-parents a commit already
on it, and an update that reconciles a divergence merges (Sections 4.1, 11). A repository whose Way of
Working is to rewrite states that here.

Note: Section 11's statement that a `rebase` or `squash` strategy "is not an exception" scopes the
work-branch guarantee — such a strategy writes to the base branch, which is a different branch — and
does not rank the three against one another. The default above rests on what each strategy does to the
commits, not on that sentence.

- `transform` (string, OPTIONAL) — names the repository unit run at `before:merge` under a `squash`
  strategy, which derives the squash subject and body from the pull request (Section 10.3). The unit
  is the consumer's to bind, as a `template` body source's unit is (Sections 6.11, 10.2); a
  `transform` naming a unit the consumer bound nothing to is a configuration error
  (`transform_unbound`, Section 6.11).
  - Default: none. Where no transform is named nothing is unbound and none runs; the code host
    composes the squash message it writes (Section 9.2).

### 6.9 `[tasks]` and `[driver]`

When the consumer runs the OPTIONAL task model (Section 7.3), these tables configure it:

```toml
[tasks]
enabled        = true
write_through  = true          # materialize tasks into the tracker where the capability exists

[driver]
on  = "tasks:all_closed"       # the task-model condition the consumer watches for
run = "ship"                   # the entry point the consumer then invokes
```

These tables are read by the **consumer** running the task model, not matched by the executor. The
task model is the consumer's (Section 7.3), so the condition `on` names is one the consumer observes
in its own state, and `run` names the entry point it invokes when that condition holds
(Section 8.1). They travel in `repo.policy.toml` because the repository owns the wiring — which
condition completes a unit of work, and what completing it runs — and not because the engine matches
them; the triggers the engine matches are Section 5.1's two kinds, both of which the engine itself
produces.

These tables are inert when the consumer runs no task model (for example the interactive front-end).

### 6.10 `[[branch]]` Sections

A repository MAY vary its Way of Working by the branch a unit of work targets. One policy document
carries the variation, so the whole of it stays reviewable in one place:

```toml
[[branch]]
match = { prefix = "release/" }

[[branch.policy.edge]]
on   = "before:push"
do   = "run"
hook = "sign-artifacts"

[branch.messages.squash]
strategy = "merge"             # a release track keeps individual commits
```

- `match` (table) — REQUIRED, and it names **exactly one** matcher. `prefix` is the matcher this
  specification defines: the section applies where the resolved base branch (Section 6.4) starts
  with its value. A `match` naming no recognized matcher, or more than one, is a configuration error
  (Section 6.11).
- Any key the top level carries MAY appear under a section, and means for that branch what it means
  at the top level — **except `[base]` and `[scope]`**, which a section MUST NOT carry
  (`branch_section_selector_key`, Section 6.11).

The exception is what keeps selection from depending on the section selected. Base resolution runs
first and reads no `[[branch]]` section; the resolved base is then what selects one (Section 6.4). A
section carrying `[base]` would supply the value that decides whether it applies, and one carrying
`[scope]` would do it one step longer: `branch_pattern` fixes the work-branch name, which a
`[base] resolve = "by_prefix"` reads to select the base, which selects the section. A value named
inside a scope cannot select the scope it is read from — the rule Section 6.4 already states for
`policy_source = "target_branch"`, where every `[base]` key sits in the document the base is what
locates, applied here to the section the base is what selects.

Refusing the two keys rather than resolving a fixpoint keeps "is this policy valid" answerable by
looking at the policy. A repository that wants a different base per track states it at the top level
with `resolve = "by_prefix"`, which is the mechanism that exists for it and which resolves in one
pass. Everything else a section can carry is downstream of selection and is untouched: hooks, edges,
messages, transitions and the task tables, the worked example above among them.

Resolution is by **longest prefix**, and exactly one section applies. Where several match, the one
whose prefix is longest wins; where none matches, the top level applies alone. That is what makes
the feature safe to add: Section 5.4 refuses a policy in which two edges could match one trigger,
and a scheme in which two sections could both contribute an edge for one trigger would reintroduce
exactly that ambiguity one level up. Longest-prefix-wins settles it by construction rather than by a
precedence rule an implementation could read differently.

No empty-prefix default is required, which is where this differs from the `by_prefix` base
resolution (Section 6.4). There, the strategy must select *some* branch, so a default is the only
way to make resolution total. Here the top level is the default, and a section states only its
differences.

A section **merges over** the top level, key by key, which mirrors the rule the `vcsx.toml` merge
already uses (Section 6.1). So a release track adds a signing gate without restating every hook, and
a key it does not mention keeps whatever the top level said. Two sections with the same `match` are
refused (Section 6.11) rather than merged in file order: file order is not a property a repository
should have to reason about, and 5.4's refusal of non-determinism is the posture this specification
takes wherever two things could both apply.

The matcher is named inside `match` rather than being the bare string it is today's only kind, so a
later decision adding another — a glob, say, for a repository whose branches carry a suffix rather
than a prefix — adds a key beside `prefix` instead of changing every section already written.

Important nuance: under `policy_source = "target_branch"` (Section 8.1) these sections come from the
pull-request target, so whoever can land a change there can author one. That is a property of the
mode rather than of this feature, and `SPEC.md` Section 15.4 states it where the mode is chosen.

### 6.11 Validation

A policy is validated before use. Each configuration error carries a stable reason token, surfaced in
the result envelope (Section 8.2), so a caller can branch on the cause without parsing `message`:

| Condition | Reason |
|-----------|--------|
| The source host-side policy is read from could not be read — the branch absent, the remote unreachable, or the credential refused alike (Sections 6.1, 8.1) | `policy_source_unreadable` |
| No `repo.policy.toml` was discovered at the source (Section 6.1) | `policy_not_found` |
| A discovered `repo.policy.toml`, or a `vcsx.toml` merged into it, that does not parse (Section 6.1) | `malformed_policy` |
| A key whose value does not satisfy the constraints its section states — a `[requires] version_floor` that is not a `MAJOR.MINOR` version (Sections 6.2, 8.5), for example | `malformed_policy` |
| An edge whose action cannot be dispatched from the arguments it carries — a `run_op` with no `op`, a `run` with no `hook` (Sections 5.2, 6.5) | `malformed_policy` |
| A declared hook that names no unit to run — a `[hooks.engine.<name>]` table with no `run` (Section 6.6) | `malformed_policy` |
| An edge's `on` is not a trigger the engine recognizes (Section 6.5) | `unknown_trigger` |
| An edge's `do` is not a known action (Section 5.2) | `unknown_action` |
| A `run_op` names an operation the engine does not define (Section 4.1) | `unknown_operation` |
| A `run_op` names an operation that runs outside the action-policy machine (Section 4.1) | `operation_not_dispatchable` |
| A `run` names a hook the `[hooks]` table does not declare (Section 6.6) | `unknown_hook` |
| A duplicate policy edge — two edges bound to one trigger, non-determinism (Section 5.4) | `duplicate_edge` |
| Two `[[branch]]` sections with the same `match` — non-determinism one level up (Section 6.11) | `duplicate_branch_section` |
| A `[[branch]]` section carrying `[base]` or `[scope]`, either of which supplies the value that selects the section (Sections 6.4, 6.10) | `branch_section_selector_key` |
| A duplicate `(from, on)` transition (Section 6.7) | `duplicate_transition` |
| A cycle of lifecycle positions, each position's `run_op` edge dispatching the operation the next position gates, so no operation on the cycle can run (Sections 4.1, 5.6) | `position_cycle` |
| A `by_prefix` base resolution with no empty-prefix default, or a missing or malformed map (Section 6.4) | `base_unresolvable` |
| A `set_state`/transition binding without a consumer that can apply it (Section 5.2) | `set_state_unbound` |
| A `[messages.pr]` `body_source = "template"` with no template unit bound (Sections 5.2, 10.2) | `template_unbound` |
| A `[messages.squash]` `transform` naming a unit the consumer bound nothing to (Sections 6.8, 10.3) | `transform_unbound` |
| A policy, or the consumer configuration, requiring a capability no selected backend declares (Section 9.3) | `capability_unsupported` |
| A `policy_branch` equal to the branch the resolved base names (Sections 6.4, 8.1) | `policy_branch_is_target` |
| A `version_floor` above the running engine version (Section 8.5) | `version_floor_unmet` |

The first two conditions leave the engine without a document at all, the next four are
well-formedness failures, and the rest are consistency failures. The order is not incidental:
validation takes a document, a policy that could not be obtained yields none for the well-formedness
checks to run against, and one that does not parse yields none for the consistency checks below it.
`malformed_policy` covers a well-formedness failure no other condition in the table names; where
another names the state — a missing or malformed `prefixes` map is `base_unresolvable` (Section 6.4),
a `[[branch]]` section carrying a selector key is `branch_section_selector_key` (Section 6.10) — that
condition's reason is reported. Each of those has a repair a reader can act on where
`malformed_policy` would name only that something is wrong: supply the map, or move the key to the
top level and express the variation with `resolve = "by_prefix"`. Section 6.1's rule that an unknown
key SHOULD be ignored for
forward compatibility covers a key the schema does not declare, not a declared key whose value the
schema does not admit.

Validation is judged from five inputs and no others, and naming them is what makes "determinable
before the policy runs" a question with an answer (Sections 8.6, 9.3):

- the policy document, with `vcsx.toml` merged in (Section 6.1);
- what the engine holds independently of the invocation — its own version (Section 8.5), which is
  what `version_floor_unmet` turns on, together with its own defaults (Section 6.8);
- the consumer's selection and access configuration (Section 8.1), which fixes which backends the
  plugin layer loads and therefore which descriptors the engine reads (Section 9.3); the descriptors
  of the selected backends, together with the defaults above and, where the capability is
  `export_source`, with the form the engine's own `run` unit takes (Section 6.6), are what
  `capability_unsupported` turns on;
- the actions the consumer can effect, supplied as `effectable_actions` (Sections 5.2, 8.1), which is
  what `set_state_unbound` turns on;
- the repository units the consumer bound, supplied as `bound_units` (Section 8.1), which is what
  `template_unbound` and `transform_unbound` turn on.

The last is stated rather than left to inference because a template is a Section 10.2 repository
unit and not a Section 5.2 action, so an engine judging only the document and the action set would
find the condition undeterminable and defer it to first use — and first use of a `template` body
source is a `create_pr`, which a `ship` reaches only after it has pushed (Section 12.2). A policy
that cannot compose a body would then publish a work branch before saying so. A `pr_to_squash`
transform is the same kind of unit and is refused here for the same reason, with more of the flow
behind it: its first use is the `merge` a `land` reaches only once the pull request is open
(Sections 10.3, 12.3).

The third, fourth and fifth are inputs rather than things the engine holds because the consumer
supplies each with the invocation (Section 6.2), and nothing about the ordering changes to admit
them: Section 8.6 establishes `arguments_unreadable` and `local_vcs_missing` before validation, so
the invocation's arguments are decoded — the backend selection, `effectable_actions` and
`bound_units` among them — by the time the checks above run. Each of the three is a fact about the
consumer rather than about one unit of work, so each is readable from the consumer configuration
(Section 8.1); what makes them inputs is that the engine is told them, not where the consumer keeps
them.

`policy_branch_is_target` is judged from the consumer's configuration and the policy together, and
from no checkout, which is what places it here rather than among the preconditions. A trusted
revision that is also the branch pull requests target is one the work being landed can rewrite, so
the two values naming the same branch is a defect in the configuration rather than a state the
engine can work around. Refusing it at validation is what keeps the refusal ahead of `commit`: a
consumer that discovered the conflict when `create_pr` ran would already have published a work
branch, which is the disposition Section 6.11 exists to avoid.

`provision` is validated from those inputs **less the first**. The policy document is not among
them, because the operation exists to obtain the repository the document is in (Sections 4.1, 6.1),
so no condition judged from the document — every row above from `malformed_policy` through
`version_floor_unmet` — can be reported for it. `capability_unsupported` is what survives, and it
survives for a reason rather than by exception: it turns on the third input, which is the consumer's
rather than the repository's, so a backend that cannot derive more than one working tree from one
store is refused here, before anything is fetched, on the one operation that would fetch.

What that costs is worth naming rather than leaving to be discovered. A `version_floor` above the
running engine version does not stop a `provision`, so an engine below the floor obtains the
repository and refuses on the next invocation — the first that reads a floor declared inside it.
That is the ordering the operation exists to break rather than a hole in it: a requirement stated in
a repository cannot bind the step that obtains the repository. The refusal still arrives fail-closed
and before any policy runs (Section 8.5), and what precedes it wrote no branch and published
nothing.

What is *not* judged here is what only a checkout or a run can answer. Whether the unit a `run`
names exists and can be started is a property of wherever that unit resolves from — the working tree
for an `in_sandbox` hook, the host-side policy's own source for a `host_side` one (Section 6.6) —
rather than of the document, so a hook the engine could not start is `hook_unanswered` at first use
(Sections 4.3, 6.6) and not a configuration error; a `[hooks.engine.<name>]` that names no unit at
all is the document's own defect and is refused here. The disposition is the same for both contexts;
only where the engine looked differs.

Two boundaries against neighbouring reasons follow. `version_floor_unmet` names a floor the engine
read and does not satisfy; a floor it cannot read is `malformed_policy`. The engine refuses either
way, running only where the floor is demonstrably satisfied (Section 8.5), but the two reasons name
different repairs — a newer engine, and a corrected file. `unknown_operation` and `unknown_hook`
likewise name an argument the engine resolved and did not recognize, while an argument that is
absent is `malformed_policy`; that condition is stated over the actions rather than per argument,
because `set_state` with no target has the same shape and no reason of its own.
`operation_not_dispatchable` is the third of that group and is not `unknown_operation` widened: the
operation is one this specification defines, and the repairs differ — `unknown_operation` says
correct the spelling, and this one says dispatch the operation from its own entry point, which
Section 8.1 gives it.

`position_cycle` names a policy that cannot run rather than one that might not converge, which is the
boundary against Section 5.6's bound. A lifecycle position is matched exactly, has no class fallback
(Section 5.3), and binds at most one edge (Section 5.4), so a `run_op` edge bound to a position is
taken whenever the position runs; a cycle of such edges therefore dispatches without
reaching an operation on every traversal, whatever the checkout holds and however the remote has
moved. A cycle that passes through a typed operation result is not this condition and is not refused,
because a result reports state outside the engine and the next traversal may differ — that is the
routing Section 5.6 defends, and refusing it is the cycle detection that section rules out. The
condition is judged over the `before:<op>` positions Section 4.1 defines and the `run_op` edges
bound to them, which is one graph: the trigger is the whole of an edge's key (Section 5.4), so there
is a single traversal to judge rather than one per scope.

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
and its result re-enters the machine, so repository policy governs the sequence. It commits the tree
it read: where the working tree changes between the `before:commit` position and the capture, nothing
is committed, and `ship` re-reads and retries within the flow bound (Sections 5.6, 12.2). It also
makes each step's progress before it takes the next: where the guard read the working tree dirty,
the sequence dispatches no `push` step unless a `commit` in the flow returned a `done`-class result;
and it dispatches no `create_pr` step unless a `push` in the flow returned a `done`-class result. A
tree the guard read as clean dispatches no `commit` and owes none.

Both are stated over the **flow** (Section 5.6) rather than over the invocation, so a resumed `ship`
continuing a resolved `create_pr:blocked` is not refused by them — the `push` whose `done` the
second requires was made in the invocation the resume continues. Both are stated over the
**sequence's own steps** rather than over `ship` as a whole, so a repository edge whose `run_op`
dispatches `create_pr` is the repository's dispatch and falsifies neither: policy may end a
front-end early or reach past it, and what these fix is what the sequence itself does
(Sections 12.1, 12.2).

A step the sequence may not advance past ends the invocation rather than being skipped. Where a
repository edge disposed of a `commit` or a `push` result and the step did not report a `done`-class
result, the sequence dispatches nothing further and the invocation reports the result the machine
last handed back (`result_of`, Section 12.1) — the same ending a `return` transfer produces
(Section 12.2), and what makes the bare transfer out of Section 12.2's commit loop sound.

The first sentence states the **extent** of the sequence rather than a postcondition on every
invocation. The built-in sequence already ends `ship` without a pull request on five paths — the
flow bound twice, `integrate:merge_conflicts`, `push:pr_closed`, and a push whose class is not
`done` (Section 12.2) — so a repository edge that ends the flow early does nothing the built-in does
not. What a repository edge can add is an ending of class `done` before `create_pr`, which is why
the test a caller applies is the operation the result names rather than its class (Section 13.1).

### 7.2 `land`

`land` merges an already-open pull request. It runs `merge` at `before:merge`, applying the
configured strategy and, for a squash, the `pr_to_squash` transform (Section 10.3). `land`
**transforms** message content; it never authors a message. It refuses to merge a pull request that
is not open or whose required checks have not passed, surfacing the corresponding `merge:*` reason.
It merges the head it read: where the pull request's head advances between the read and the merge,
nothing is merged, and `land` re-reads and retries within the flow bound (Sections 5.6, 12.3). And
it returns a `done`-class result only where a `merge` in the flow reported `merge:ok` — so a `land`
whose built-in re-read-and-retry an edge disabled cannot report success without having merged. The
reason test and the class test coincide here rather than by construction: Section 4.3 gives `merge`
exactly one `done` reason, so the rule needs no phrase an engine has to interpret. It is stated over
the flow, as Section 7.1's two are, so a resumed `land` is not refused by it.

`land` MAY be invoked to await first. Under `--await` — or whatever the front-end's encoding for it
is (Section 8.1) — it dispatches `await_checks` and then the `merge` it already runs, continuing
to the merge where the await's result is class `done` and ending on it otherwise. That is the
disposition Section 5.4 gives every operation result rather than a rule this composition adds: it is
a composition of two operations this specification already defines and introduces no sequencing rule
of its own, so a `land` that awaits and a `land` preceded by a separate `await_checks` invocation
reach `merge` in the same state, the difference being how many invocations the consumer made.

### 7.3 The Embedded-Driver Contract

An embedded driver invokes the same executor programmatically. It:

- supplies the execution context (host-side vs in-sandbox sourcing, Section 3.2), the backend
  selection, the access parameters and credentials the plugins use, and the forge repository
  coordinate where a forge is configured (Section 8.1);
- binds `escalate` to its own resolver (Section 5.5) — for example an automation service that turns an
  escalation into an agent-assigned task;
- MAY run a **task model**: tasks with an `id`, a `description`, a `status` (`open`/`closed`/`blocked`),
  an `assignee` (`agent`/`human`), an optional `parent`, and an optional `tracker_link` — seeded
  from a work item or a planning step, and closed by the caller. The driver watches its own task
  state for
  the conditions `[driver]` names — every implementation task closed, or a task needing human help —
  and invokes the entry point that table names when one holds (Sections 6.9, 8.1). The task model,
  its durability, its materialization into an external tracker, and the watching are all the
  driver's; `vcsx` receives an invocation, not an event.

The interactive and embedded front-ends run the identical executor over the identical policy; they
differ only in initiator and `escalate` binding.

## 8. The Engine Invocation Contract

The engine is invoked over a transport-neutral contract: an in-process API or a subprocess with
structured input and output. The contract is the same either way; only the encoding differs.

### 8.1 Entry Points and Arguments

The entry points are the front-end sequences and the individual operations:

- `ship`, `land` — the front-end sequences (Section 7).
- `load_policy`, `provision`, `status`, `diff`, `commit`, `integrate`, `push`, `create_pr`,
  `merge`, `pull`, `await_checks` — individual operations (Section 4.1), for a driver that composes
  its own sequence.

Common arguments: the identity the work branch is derived from (Section 6.3), the commit identity
the commits an entry writes are attributed to (Section 10.1), a message input for
`commit`/`create_pr` (Section 10), the backend selection, the forge repository coordinate where a
forge is configured, the `remote`, `provision`'s two locations, the access parameters, extension bag,
consumer-capability declarations and credentials described below, and the execution context
(Section 3.2). The two identities are
separate arguments: the first fills the work-branch pattern and the second names an author, and a
consumer supplies each where its capability takes one (Section 9.1). Exact argument encodings are
`Implementation-defined` and MUST be documented; argument *names* for shared concepts MUST match
this specification.

The **backend selection** names which VCS backend and which forge backend the plugin layer loads
(Section 9). It is the consumer's for the reason Section 6.2 states: the selection is what obtaining
the repository needs, and `repo.policy.toml` is inside the repository it would obtain.

- `local_vcs` — the VCS backend the plugin layer loads, and the checkout mode for a checkout the
  engine creates (Sections 3.3, 4.1). REQUIRED for every entry point, because the engine loads a
  backend before it can ask one anything; its absence is refused before the policy runs
  (Section 8.6). It does not name the mode of a checkout the engine did not create, where
  `detect_mode()` answers (Section 9.1) — a backend MAY declare several supported modes
  (Section 9.3), so the backend and the mode are two answers and this argument gives one of them.
- `forge` — the forge backend the plugin layer loads. OPTIONAL: a consumer that runs no forge
  operation supplies none, and "a forge is configured" throughout this specification means this
  argument is present.

The **remote** is the consumer's on the same reasoning: it names where the repository was obtained
from, which is settled before there is a repository to read a policy out of.

- `remote` (OPTIONAL) — the name of the remote the version-control operations that touch one act
  against (`provision`, `integrate`, `push`, `pull`; Sections 3.2, 9.1). It is the remote the
  repository was provisioned from, and it also names which of the checkout's copies of the base a read
  resolves against, which acquires nothing (Section 6.4).
  - Default: unset — the backend's default remote for the checkout mode, which is
    `Implementation-defined` and MUST be documented (Section 13.3).

The engine resolves the remote once per invocation and supplies it to each capability that takes one
(Section 9.1); a backend does not read it from the policy, and does not infer it from the work
branch's own upstream binding, which need not exist — the work branch is engine-derived
(Section 6.3) and MAY be absent from the checkout at the first push.

The **base branch** is the pull-request target and what `integrate` brings in, and the consumer may
supply it two ways:

- `base_branch` (OPTIONAL) — the base for this invocation. It wins over the consumer
  configuration's and over `[base] branch` (Section 6.4), most specific first.
- `base_branch_allowed` (OPTIONAL) — the set of bases an invocation may name, as names or patterns.
  A `base_branch` outside it is refused before the policy runs (Section 8.6). It belongs to the
  consumer configuration rather than to a single invocation, so the party bounding the choice is not
  the party making it. The `policy_branch` is excluded whatever this lists, and whether or not it is
  configured at all: a bound an operator must remember to set is a guarantee that fails by omission,
  and this one is the specification's rather than the operator's.

Where no source supplies a base, an entry that needs one is refused before the policy runs; an entry
that needs none runs (Section 8.6). That scoping is the default mode's: under `target_branch` the
base is what locates the policy, so every entry needs one and Section 8.6 states the refusal over
all of them. The engine holds a base branch opaque as it holds the coordinate
opaque: it resolves which of the three sources applies, supplies the result to the capabilities that
take one, and interprets nothing about the name.

The **policy source** names where host-side policy is read from:

- `policy_source` — `policy_branch` or `target_branch`.
  - Default: `policy_branch`. The revision is named separately from the pull-request target, so
    nothing the consumer merges reaches what it trusts.
  - `target_branch` reads host-side policy from the pull-request target itself. `policy_branch` is
    then neither required nor meaningful, and a `policy_branch` equal to the target is the
    configuration rather than an error in it, so `policy_branch_is_target` does not arise
    (Section 6.11).
  - Under `target_branch` a base is REQUIRED, from the invocation or from the consumer
    configuration, and its absence is refused before the policy runs whatever the entry
    (Section 8.6). The target is what the policy is read from, so the base is this mode's
    counterpart to `policy_branch` and cannot come from `[base]`, which sits in the document being
    located (Section 6.4). What the mode saves is naming a second branch, not naming a base.

It is a named mode rather than a flag because the trust properties Section 11 states are conditional
on it, and a conditional guarantee is worth stating only where a consumer can tell which state
holds. What `target_branch` gives up is stated where the guarantee is, not left to be derived.

The **policy branch** is the revision the engine reads the host-side parts of `repo.policy.toml`
from under the default mode (Sections 3.2, 6.1):

- `policy_branch` — REQUIRED under `policy_source = "policy_branch"`; its absence is then refused
  before the policy runs (Section 8.6). Which revision host-side policy is read from is the
  consumer's decision, because Section 3.2 makes sourcing by trust the consumer's, and this argument
  is that decision made explicit.
  - It resolves to the copy belonging to the resolved `remote`, and never to a local branch of the
    same name. This is Section 6.4's rule for the base ref applied to the trust root, and it carries
    more weight here: a checkout MAY hold several copies of one branch, and for the base the wrong
    one yields a stale number, while for the policy branch it yields host-side hooks chosen by
    whoever can write that checkout. A consumer running the engine against a checkout it did not
    create is exactly where that matters.

It is REQUIRED with no default, and specifically no default derived from `[base] branch`: a branch
named inside the policy cannot select the revision the policy is read from. Two properties are
required of whatever it names, and neither is one the engine can establish for itself — a consumer
that runs an agent MUST NOT let that agent write to it, and MUST NOT direct its own merges at it
(Section 11). The engine holds it opaque, as it holds the base branch and the coordinate opaque.

Two **locations** name where `provision` acts (Section 4.1):

- `store_location` — where the fetched copy of the repository is maintained. REQUIRED for
  `provision`, carrying no meaning for any other entry, and its absence there is refused before the
  policy runs (Section 8.6).
- `tree_location` (OPTIONAL) — where the working tree is derived from that store. Absent,
  `provision` maintains the store and derives no tree, which is how a consumer runs the acquiring
  half once per repository and the deriving half once per working tree.

The engine holds both opaque, as it holds the forge repository coordinate: it takes them, supplies
each to the VCS backend capabilities that act on them (Section 9.1), and interprets neither. A
location a backend cannot use is that backend's own `failed` at first use rather than a shape the
engine judged. They are the only arguments naming a place the engine acts on, because they are the
only ones a consumer supplies before the place exists.

The **forge repository coordinate** names which repository on the code host the forge operations act
against (Section 9.2). It is REQUIRED where a forge is configured and carries no meaning
where none is, and its absence where one is configured is refused before the policy runs
(Section 8.6). The engine holds it opaque, as it holds the commit identity (Section 10.1) and the base
ref (Section 6.4) opaque: it takes one, supplies it to the forge backend, and does not interpret it.
Its shape is therefore the backend's, and a coordinate a backend cannot use is that backend's own
`failed` at first use rather than a shape the engine judged.

A front-end MAY derive the coordinate from the resolved remote and supply it, rather than requiring a
caller to state it on every invocation; a front-end that does MUST document how. Encodings are the
front-end's, as above, and deriving it there keeps the derivation on the same side of the trust
boundary as the credential the coordinate will be used with (Section 11) — which is the whole of why
the coordinate is the consumer's rather than the checkout's.

Two **access parameters** name where the engine reaches, one per plugin layer:

- `git_access` — where the version-control operations reach the remote. REQUIRED for an entry that
  can reach one, and its absence there is refused before the policy runs (Section 8.6). Exactly the
  network-touching capabilities Section 9.1 enumerates act against it.
- `forge_access` — where the forge operations reach the code host. REQUIRED where a forge is
  configured, and its absence there is refused before the policy runs (Section 8.6). Every capability
  of Section 9.2 acts against it.

The engine holds both opaque, as it holds the forge repository coordinate, the commit identity and
the base ref opaque: it takes them, supplies each to the plugin that uses it, and interprets neither.
Their shape is service-specific — one code host serves its API from a different name than its
version-control transport and another from a different path under the same name — and a parameter the
engine parsed would put a backend's addressing grammar back in the engine, which is the mixing
Sections 9.1 and 9.2 are separate to prevent. A parameter a backend cannot use is therefore that
backend's own `failed` at first use rather than a shape the engine judged, as a coordinate it cannot
use is.

Four **await parameters** bound the `await_checks` operation (Section 4.1). All are OPTIONAL, and an
invocation supplying none makes a single read and cannot loop:

- `await_bound_ms` (OPTIONAL) — the overall wall-clock bound on the wait.
- `await_max_reads` (OPTIONAL) — the greatest number of reads the operation makes.
- `await_interval_ms` (OPTIONAL) — the least time between two reads.
- `await_budget_floor` (OPTIONAL) — a bucket name and a `min_remaining`, compared against the
  snapshot each read observes (Section 9.2). The bucket is named by the consumer because bucket
  identity is the forge's and the engine normalizes none.

The first two **authorize** a second read; the other two do not. `await_bound_ms` and
`await_max_reads` are what give an invocation a **read allowance** greater than one read:
`await_interval_ms` paces reads an allowance already authorized, and `await_budget_floor` can only
end a wait early. The two questions are separate: what lets a wait read again, and what stops it.
Stating only the second leaves a floor or an interval supplied alone reading against a forge that
may never answer, which is a wait no supplied argument ends, where Section 2.2 admits this operation
only as a **bounded** exception.

An invocation supplying `await_interval_ms` or `await_budget_floor` and neither `await_bound_ms` nor
`await_max_reads` is refused before the policy runs, as `await_bound_missing` (Section 8.6). It is
refused rather than read as the no-parameter case because an invocation naming a floor or an
interval is asking for a wait that repeats, and a single read reported as a wait that ended answers
a question the consumer did not ask. A consumer that wants one read and an early stop on a low
bucket supplies the floor together with `await_max_reads`.

Reaching the end of the read allowance ends the wait with `await_checks:still_pending`; reaching the
floor ends it with `await_checks:budget_floor` (Section 4.3). Where both are reached on the same
read the operation reports `budget_floor`. That order follows from the snapshot **each read**
observes: the floor judges the read just made, while the allowance decides whether to read again, so
a read whose snapshot is already below the floor has answered before the allowance is consulted.

A floor the observed snapshot **cannot answer** — the forge published no snapshot, or the snapshot
carries no bucket of the name the consumer supplied — ends the wait with `budget_floor`. An engine
that cannot establish there is room to keep spending does not keep spending, and the floor behaves
the same whichever forge is underneath, which is what a consumer that cannot see the backend can
check. The consequence is stated rather than left to be found: against a forge that publishes no
budget at all, a floor-carrying invocation makes one read and reports `budget_floor` whatever the
checks said. The floor is OPTIONAL and no default supplies one, so a consumer reaches this only by
naming a floor.

These are the consumer's on the same footing as the access parameters and the credential pair, and
for the same reason Section 2.2 states: the engine compares against numbers it was handed and
chooses none of them. How long a wait is worth, how often to ask, and how much remaining budget is
too little are decisions that depend on what else the consumer intends to spend and how many other
holders of the same credential are spending concurrently — neither of which is visible from inside
one invocation. Remove the arguments and there is no loop; supply different ones and the same engine
waits differently.

One further argument selects what a front-end sequence runs rather than bounding an operation:

- `await_first` (OPTIONAL) — supplied to `land`, it dispatches `await_checks` before the `merge`
  the sequence already runs, continuing to the merge where the await's result is class `done` and
  ending on it otherwise (Sections 7.2, 12.3). It carries no meaning at any other entry point.
  - Default: unset — `land` merges without awaiting.

It is named here because Section 7.2 cites this section for it — "`--await`, or whatever the
front-end's encoding for it is" — and because the encoding is the front-end's while the name is not.
It is not one of the four above: those bound a wait the operation makes, and this one decides
whether the sequence dispatches the operation at all.

A **network bound** names how long the engine waits for one network call (Section 9):

- `network_bound_ms` (OPTIONAL) — the bound applied to each network call an invocation makes. It
  bounds **one call**, not the sum of an operation's calls: an operation realized through two
  capabilities is not held to one deadline across both, since the second may be local and a bound
  covering it would be bounding something other than a wait on a server (Section 9.1).
  - Default: `Implementation-defined` and MUST be documented (Section 13.3). An engine MUST admit a
    configured value of at least 600 seconds, and an engine that lets a deployment configure it MUST
    hold the configured value to the same floor. An engine MAY apply different values to different
    capabilities and MUST document them where it does.

The floor accommodates the slowest network unit in the capability set rather than the typical one:
`ensure_store` fetches an entire repository, and a first provision of a large one over an ordinary
link takes minutes, so an engine capping the configurable value below that would make this
specification's own provisioning operation unusable at scale while remaining conformant. The exact
value is arbitrary in the way Sections 5.6 and 6.6 say theirs are; that it is fixed is not.

The bound is the consumer's and `repo.policy.toml` carries no key for it. The endpoint each call
reaches and the credential it presents are already the consumer's — `git_access`, `forge_access` and
the credential pair, above — and how long to wait for an endpoint is a fact about that endpoint and
the network to it, which is the consumer's environment rather than the repository's Way of Working.
A repository cannot know whether its policy is being run against a forge on a local network or
across a saturated link. This is the placement Section 6.6 gives the hook bound, reached from this
section's own reasoning rather than by analogy: the repository owns which unit runs, and the
consumer owns how long the machine will wait for it.

Two **read validators** name the state a consumer already holds, so a read answers only where that
state has moved (Sections 4.1, 9.2). There are two because Section 9.2 has two capabilities that
issue one, over two resources that move independently — a check run completing moves the check
aggregate and not the pull request, and a push moves both — and a validator issued for one is not an
answer about the other:

- `pr_state_validator` (OPTIONAL) — the validator a previous invocation's `pr_state` read returned in
  `outputs` (Section 8.2). Supplied, the engine presents it on the `status` read (Sections 4.1, 9.2),
  and the forge MAY answer `unchanged`; absent, the read is unconditional.
  - Default: unset — an unconditional first read.
- `checks_state_validator` (OPTIONAL) — the validator a previous invocation's `checks_state` read
  returned in `outputs`. Supplied, the engine presents it on the first `await_checks` read; absent,
  that read is unconditional. Within one `await_checks` the engine carries the validator forward from
  each read to the next, so a loop presents one after its first read whether or not the invocation
  supplied one.
  - Default: unset — an unconditional first read.

The engine MUST NOT present a validator to a capability that did not issue it. The obligation is the
engine's rather than the backend's because a backend holds an opaque value it was handed and cannot
check what resource it describes, where the engine knows which read returned it — and a backend given
the wrong one would satisfy Section 9.2's prohibition on answering `unchanged` without a conditional
read to the letter, having presented a validator and made a conditional read, while answering about
the wrong resource.

The engine holds each opaque, as it holds the forge repository coordinate and the two access
parameters opaque: it takes one, supplies it to the forge backend, and interprets nothing about it.
Parsing one would put a forge's cache-validation grammar back in the engine, which is the mixing
Sections 9.1 and 9.2 are separate to prevent. Their absence is no precondition failure and adds no
row to Section 8.6: an invocation supplying neither makes the reads every invocation made before
these arguments existed.

A validator round-trips through the consumer because the engine holds nothing between
invocations. Credentials reach the plugins for the duration of an invocation and the engine
persists none beyond it (Section 1.3), and each invocation is a bounded run that exits, so there is
no engine-side cache for a validator to live in: it leaves in the result envelope and comes back as
one of these arguments. They are therefore also the one pair of consumer-supplied values below that
is **not** readable from the consumer configuration — each changes with each read, and a configured
one would be stale by construction. That round trip is what makes the saving available across
invocations rather than only within one, which is the case that matters: a consumer that parks on
`still_pending` and resumes later reads again in a new invocation, and a validator it could not carry
forward would leave the conditional read serving only the loop that was already cheap.

A consumer MAY supply a per-backend **parameter set** the engine carries to the selected forge
backend uninterpreted:

- `forge_parameters` (OPTIONAL) — the parameter set, carried through untouched. A backend MUST
  document the keys it reads, which are `Implementation-defined` per backend (Section 13.3).
  - Default: unset — the engine carries none.

A key the backend does not recognize is that backend's own disposition rather than a shape the
engine judged, on the same ground: the engine reads no key of the set, so it holds nothing to
judge one against.

Two arguments declare **what the consumer can do**, which is what the last two of validation's five
inputs are (Section 6.11):

- `effectable_actions` (OPTIONAL) — which of the consumer-effected actions (`create_task`,
  `set_state`, `notify`; Section 5.2) this consumer can perform. A `set_state` edge or transition
  where the set does not name `set_state` is refused with `set_state_unbound` (Section 6.11); a
  `create_task` or `notify` outside it is well formed, and the intent is emitted and reported
  (Section 8.2).
  - Default: empty — the consumer effects none.
- `bound_units` (OPTIONAL) — the repository unit names the consumer bound, which a `[messages.pr]`
  `body_source = "template"` and a `[messages.squash]` `transform` are checked against
  (Sections 6.8, 10.2, 10.3). A unit named by either and absent from this set is refused with
  `template_unbound` or `transform_unbound` (Section 6.11).
  - Default: empty — the consumer bound none.

Both default empty because that is the direction a wrong guess is cheap in. A default naming every
action would validate a `set_state` policy against a consumer that cannot advance a state, which
strands the flow at the first transition; a default naming every unit would admit a `template` body
source whose unit does not exist, and its first use is a `create_pr` a `ship` reaches only after it
has pushed (Section 12.2), so the policy would publish a work branch before reporting the defect.
Refusing costs a consumer one declaration; admitting costs a published branch or a stranded flow.

A consumer MAY supply `resume`, an OPTIONAL token continuing a flow a previous invocation escalated
(Sections 5.5, 5.6):

- `resume` (OPTIONAL) — the `resume_token` a previous invocation returned in `outputs`
  (Section 8.2). Supplied, the invocation re-enters the point that raised the need rather than
  beginning at its entry point, continues the flow from there rather than ending at the re-entered
  result (Section 5.5), and the flow bound continues from the count the token carries.
  - Default: unset — the invocation begins at its entry point.

A resumed invocation therefore does not run the flow ahead of the point it re-enters — the prefix,
not the remainder, which it continues into (Section 5.5) — and an argument the flow reads only ahead
of that point has no effect on it. A resumed `land` consults no `await_first`: the await branch runs
once, before the merge loop a resume re-enters (Section 12.3). A resumed `ship` does consult
`message`, which the commit loop reads at every turn (Section 12.2). The property is where the flow
reads an argument and not what kind of argument it is, and a caller that wants the prefix dispatches
the operation itself, which is the composition Section 7.2 already describes.

The engine holds it opaque, as it holds the base ref and the forge repository coordinate opaque, and
here that is a choice rather than a necessity: the value is the engine's own rather than another
party's, and an engine that published its structure would owe a stable spelling for "the point that
raised the need" across every graph shape a policy can express — a schema for the executor's
traversal, in exchange for nothing a consumer does with it. It round-trips through the consumer for
the reason the read validators do: the engine holds nothing between invocations, so it is not
readable from the consumer configuration either.

An engine MUST refuse a `resume` it cannot establish as its own and current — one issued under a
different policy, against a different repository, by a different major version, or by an entry point
other than the one the resuming invocation names — before the policy runs (Section 8.6), rather than
re-entering a point that no longer means what it meant. The direction is deliberate: a refused
resume costs a re-invocation from the entry point, where an accepted stale one runs an operation
the policy no longer routes.

The fourth condition is the entry point and not the point the token names. A token names a point in
the flow its own entry point began, so the only way a point can be missing from the flow being
resumed is that a different entry began it: `ship` never runs `merge` and `land` never runs
`create_pr` (Sections 12.2, 12.3), and a `ship` token supplied to a `land` names a point that `land`
does not reach. Stated that way the condition is evaluable from the token alone, needing no
enumeration of the points a flow contains — and it is what makes this refusal decidable at the two
entry points that validate no policy to judge one against: neither `provision` nor `load_policy`
runs a policy, so neither issues a token, and every token supplied to either fails on this condition
and on nothing else (Sections 4.1, 6.1, 8.6). The converse crossing is not a refusal. A token naming
a point inside `land`'s merge loop is usable at a `land` whether or not that invocation names
`await_first`, because the resume re-enters the point rather than beginning at the entry point, so
the branch ahead of it is never run.

A consumer MAY supply `policy_pin`, an OPTIONAL handle naming the policy surface a unit of work
began under (Sections 4.1, 6.1):

- `policy_pin` (OPTIONAL) — the `policy_pin` a previous invocation returned in `outputs`
  (Section 8.2). Supplied, the invocation is refused where the surface it validated is not the one
  the pin names (Section 8.6).
  - Default: unset — the invocation makes no continuation claim and runs the surface it read.

It is what makes a unit of work a span a consumer can check rather than a span it describes. Every
invocation reads and validates the document itself (Section 4.1), so nothing else holds the surface
fixed across the invocations one unit of work is made of: a consumer that shipped, edited its
policy, and landed would otherwise have run two documents under one unit of work with nothing saying
so. A resumed invocation needs no pin — the refusal of a `resume` "issued under a different policy"
above is this same judgement, made along a chain the engine can see — so the argument is that check
standing alone for the case with no token.

The engine holds it opaque, as it holds the `resume` token opaque, and here that is a **necessity**
rather than the choice it is there. A pin specified as a value would oblige this specification to
fix a canonicalization of the effective surface — over a document Section 6.1 places nowhere,
stating no location and no discovery rule for `vcsx.toml` at all — where a handle inherits none
of that: the value is the issuing engine's own, no two engines compare pins, and the only party
that reads one is the engine that established it. A consumer that inspects a pin therefore has a
bug, which follows from the form rather than needing a rule of its own. It round-trips through the consumer for the
reason the read validators and `resume` do: the engine holds nothing between invocations
(Section 1.3), so it is not readable from the consumer configuration either.

No argument carries a policy surface the other way. The consumer holds the surface `load_policy`
returned for inspection and the pin for continuity, and the engine reads the document itself on
every invocation, which is what makes Section 3.2's "the consumer sources config by trust" literal
rather than a property of one operation. An argument accepting a surface back would let a caller
hand the engine a document no revision ever held, in the file that declares the host-side units
Section 11's trust model exists to keep outside the working tree's reach.

The consumer supplies two credentials:

- `git_credential` — the credential presented at `git_access`.
- `forge_credential` — the credential presented at `forge_access`.
  - Default: `git_credential`.

Each credential is supplied with the access parameter it is used against, both from the consumer, so
the credential and the endpoint it reaches are one decision made by one party (Section 11).
Credentials reach the plugins for the duration of an invocation (Section 1.3); the engine persists
neither beyond it.

The consumer-supplied values this section names — `local_vcs` and `forge`, the forge repository
coordinate, the `remote`, `policy_source` and `policy_branch`, `base_branch` and
`base_branch_allowed`, `provision`'s two locations, the two access parameters, `network_bound_ms`,
the four await parameters, `await_first`, `forge_parameters`, `effectable_actions`, `bound_units`
and the credential pair — the two read validators, `resume` and `policy_pin` excepted, for the
reason their entries state — MAY be read by the engine from a **consumer configuration**: a
consumer-owned file, distinct from `repo.policy.toml` and never sourced from the repository. The
excepted set is closed by the reason its members share rather than by enumeration: each is a value a
previous invocation returned, which the engine holds nothing to reissue and a configured copy of
which would be stale by construction (Section 1.3). Every other value this section names is
outside it. Its discovery precedence is `Implementation-defined` and MUST be documented
(Section 13.3). It carries no key `repo.policy.toml` carries, so the two are disjoint and neither
shadows the other (Section 6.1). It MAY carry a
credential directly or a reference the consumer resolves, so a consumer holding its secrets in a
provider of its own need not write one to disk to use this engine; under either form the engine
persists no credential beyond the invocation.

An invocation whose arguments the engine cannot decode in the encoding it published is refused with
the `usage_or_config` status and the `arguments_unreadable` reason (Section 8.6), so the surface this
section hands the engine carries a defined failure rather than one each engine invents.

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

- `vcsx_version` is the `MAJOR.MINOR` version of the engine that ran the invocation (Section 8.5).
- `entry` is the entry point the invocation ran (Section 8.1). It is null **exactly where no
  Section 8.1 entry point was read** — the `usage_or_config` status carrying the
  `arguments_unreadable` reason (Section 8.6), and nowhere else. An invocation the engine decoded far
  enough to name an entry point reports that entry point whatever failed after it, so a `ship` whose
  remaining arguments were unreadable carries `ship` and a first word that is no entry point carries
  null. The rule is stated as an "exactly where" for the reason the escalation rule below is stated as
  an "exactly when": a field a caller branches on before deciding anything else is enforceable only
  where both halves are fixed, and a nullable field with no stated case is one an engine may null
  wherever it finds it convenient.
- `status` is the invocation's outcome. For a run that executed the policy it is the overall proto
  class: `ok` (all steps `done`), `needs_caller`, or `error`. For a run in which the policy did not
  run it is `usage_or_config` (Sections 6.11, 8.6). A flow the policy stopped with `park`
  (Section 5.2) is `needs_caller`: it did not reach the entry's intended effect, so it is not `ok`,
  and `park` does not fail the flow, so it is not `error`. A flow the executor stopped at its bound
  (Section 5.6) is `needs_caller` on the same reasoning: the entry's intended effect was not
  reached, and no operation failed — the executor declined to dispatch the next one.
- `op` / `reason` / `class` describe the decisive operation result. Where they are non-null, `class`
  is the class `status` reports — `done` under `ok`, `needs_caller` under `needs_caller`, `error`
  under `error` — because the status of a run that executed the policy is that result's proto class.
  All three are null where the run has no decisive operation result: a clean `ok` with no operation;
  a parked flow, which the policy stopped rather than an operation; a flow stopped at its bound,
  which the executor stopped; and a flow the policy failed with `fail` (Section 5.2) on anything
  other than an `error`-class result. In neither of the middle two did an operation ask the caller for
  anything, so there is nothing decisive to report. Under `usage_or_config` there is no operation
  result: `op` and `class` are null and `reason` carries the configuration reason (Section 6.11) or
  the precondition reason (Section 8.6).
- A `fail` is scoped by the class the rule above already turns on. Where the run has a decisive
  result whose class is `error`, a `fail` reports it: the class agrees with the status, so the
  invariant holds unchanged, and an explicit `#error → fail` edge reports what the built-in `error`
  default reports for the same flow — which is itself a `fail` (Section 5.4). A `fail` reached on any
  other trigger — a `needs_caller` or `done` result, or a lifecycle position, which has no outcome at
  all (Section 5.1) — has no result whose class agrees, and nulls all three rather than putting a
  reason of one class under a status of another. That is the same disposition `park` takes and for the
  same reason: the policy stopped the flow, and the envelope reports what stopped it in `status`
  rather than borrowing an operation's result to say it.
- `escalation` is present exactly when `status == "needs_caller"` (Section 8.4), a parked flow and an
  exhausted one included.
- `outputs` carries entry-specific structured data (for example `status` fields, the pull-request
  number/state). Where a forge read answered, the data it answered about carries the `validator` a
  later invocation presents (Sections 8.1, 9.2) — the pull-request data carrying the one supplied
  back as `pr_state_validator` and the required-check data the one supplied back as
  `checks_state_validator`, each attached to the resource it describes. That is what makes the round
  trip readable from this section and Section 8.1 alone: the value this invocation returned is the
  value the next one supplies, and which resource it describes is readable from where it was
  returned. It also carries `unperformed_intents`: the consumer-effected intents (Section 5.2)
  the engine emitted and no consumer performed, each naming its `action` and that action's arguments.
  The key is absent or empty when every emitted intent was performed. An intent naming an action
  outside `effectable_actions` (Section 8.1) is unperformed by construction, so the key is composed
  from what the engine already holds rather than from an answer the consumer returns mid-invocation —
  which is what makes it readable under the subprocess encoding as under the in-process one
  (Section 8). It likewise carries
  `unfinished_hooks`: the result-triggered hooks that gave the engine no usable answer (Section 6.6),
  each naming the `hook`, the `trigger` that ran it, and the `condition` that occurred —
  `bound_elapsed`, `not_started` or `answer_unreadable` — absent or empty where every such hook
  answered. It is the non-gating half's mirror of `hook_unanswered`, which is why the two cover the
  same three conditions.
- `outputs` carries `unanswered_gates` for the gating half: the `before:*` units that gave the
  engine no usable answer, each naming the `hook`, the `position` that ran it, the `condition` — the
  same three tokens — and an `Implementation-defined` `detail`; absent or empty where every such
  unit answered. The key is named for the gate that is almost always the unit at a position, and the
  `pr_to_squash` transform (Section 10.3) is reported here too rather than in a key of its own,
  because it reaches the consumer through the same reason and carries the same three conditions; the
  `hook` field carries the unit's name in either case. A gate is not reported in `unfinished_hooks`,
  because the gated operation reports it as
  `hook_unanswered` (Section 4.3): the reason routes and the condition diagnoses, and both halves
  spell the condition the same way, so one consumer branch reads both. It is an array rather than
  one entry because the result re-enters the machine: a repository binding `<op>:hook_unanswered` to
  anything that does not end the flow can reach a second position on the same traversal, which
  Section 5.6 bounds rather than refuses.
- `outputs` carries `forge_unavailable_condition` where the decisive result is `forge_unavailable`
  (Section 4.3): the condition that occurred — `server_error`, `bound_elapsed` (Section 8.1) or
  `transport_failure` — absent for every other reason. The three are named tokens, so the diagnosis
  a consumer reads is spelled the same on every engine, as Section 6.6 fixes for its own three. It
  is the same arrangement `unanswered_gates` makes for its own three conditions, and for the same
  reason: the reason routes, the condition diagnoses, and both spell the condition as a token so one
  consumer branch reads both.
- `outputs` carries `forge_budget`: the most recent budget snapshot a forge capability observed
  during the invocation (Section 9.2), reported whether or not any limit was reached. The key is
  absent where the invocation reached no forge capability, and equally where it reached one and the
  forge reported no budget. Those are different events sharing one spelling, deliberately: in both
  the consumer learned nothing new and keeps whatever figure it last held, which is the disposition
  Section 4.3 gives three conditions carrying one repair. It is the one value in this contract not
  held to Section 9's rule that a non-answer be distinguishable from an absence, and the departure
  is stated rather than left to be noticed: that rule governs a value the engine composes an
  operation from, and no operation, reason or precondition branches on this one — it is observed
  and carried through untouched. The engine reports the snapshot and acts on none of it: nothing
  here paces a call, defers a dispatch or refuses an operation because a bucket is low, retry,
  back-off and budget being the consumer's (Section 2.2). What a low bucket is worth spending on
  depends on what else the consumer intends to spend it on and how many other holders of the same
  credential are spending concurrently, neither of which is visible from inside one invocation.
- `outputs` carries `failed_by_policy` where the policy ended the flow with `fail` (Section 5.2):
  the `trigger` the edge fired on, and the `reason` the edge wrote where it wrote one (Section 6.5).
  The key is absent where no `fail` ran. The token is reported here rather than in the envelope's
  `reason` field because that field carries an operation reason (Section 4.3), a configuration
  reason (Section 6.11) or a precondition reason (Section 8.6) — each from a registry a consumer
  branches on and an engine MUST document additions to — and a repository-authored value there would
  be indistinguishable from an engine one.
- `outputs` carries `resume_token` where the invocation ended at `needs_caller` with a
  **resolvable** need (Section 8.4): an opaque token naming the point that raised the need, the root
  trigger the chain that point belongs to descends from, and the flow bound already spent, which a
  later invocation supplies as `resume` (Sections 5.5, 5.6, 8.1). The key is absent where `status`
  is not `needs_caller`, and absent where the need is one of the two holds — `intervention` and
  `flow_exhausted` — which no front-end resolves and no resume continues. Its presence therefore
  agrees with the need's resolvability, so a front-end reads Section 8.4's prohibition off the
  envelope rather than off the policy that produced it. The token carries the point, the root
  trigger and the count, and nothing a lifecycle position established; supplying it continues the
  flow from that point rather than ending the invocation at it (Section 5.5).
- `outputs` carries `policy_pin` where the invocation **validated a policy surface**: an opaque
  handle naming that surface, which a later invocation supplies as `policy_pin` to claim the two are
  one unit of work (Sections 4.1, 8.1, 8.6). The key is absent where no surface was validated, which
  is the rule every key here is under rather than an entry-point list — and it leaves exactly one
  entry point where it is always absent, `provision`, "the one entry point that runs where no policy
  could be read" (Sections 6.1, 8.6), together with any run refused before validation. It is not
  scoped to `load_policy`: every other entry reads and validates the document in order to run it, so
  the pin names a surface the invocation had already established, and a consumer wanting continuity
  invokes nothing it did not otherwise need.
- `message` is human-readable prose. Nothing parses it: every fact a consumer branches on has a field
  or a token of its own, so a consumer reading `message` for structure reads a surface no engine holds
  stable, and an engine putting structure there is spending a field that has no schema on one that
  should have had its own.
- A consumer MAY add fields but SHOULD NOT break the fields above within a major version.

### 8.3 Exit Codes

For the subprocess encoding, exit codes mirror the invocation status (Section 8.2) so a caller can
branch without parsing:

- `0` — `ok` (all `done`).
- `10` — `needs_caller` (an escalation is present).
- `20` — `error`.
- `2` — `usage_or_config` (Sections 6.11, 8.6); the policy did not run.
- `1` — the invocation produced no result at all (below); this is not an invocation status.

The JSON result is emitted for each of the four status-bearing codes regardless of which, so a caller
MAY always read structured detail from an invocation that produced one.

An invocation can also end without reaching a Section 8.2 result — the engine's own fault, an abort
its runtime raised, a signal, an exhausted host. `1` is reserved for that condition: stdout carries
nothing and the diagnostic goes to stderr. **Any exit code other than the four status-bearing ones
means the same thing**, which is what makes a caller's mapping total without this specification
enumerating the ways a process can end. An engine MUST NOT report an invocation status through a code
outside the four, and MUST NOT exit `1` for an invocation that composed a result.

On every path that produces a result, stdout carries exactly one JSON object and nothing else. That is
what lets a caller separate "no result" from "result" without parsing, and what keeps a pipeline over
stdout from breaking on a fault: a consumer reads stdout where the code is one of the four and stderr
otherwise.

### 8.4 Escalation Payload

When `status == "needs_caller"`, `escalation` carries: the `need` (a stable token naming what is
required, for example `integrate_then_retry`, `reread_then_retry`, `resolve_conflicts`,
`supply_identity`, `await_checks`, `retry_after`, `human_review`, `intervention`, `flow_exhausted`),
whether the need is `retryable` (below), the `op` that
produced it, and an `Implementation-defined` `detail`. The `op` is null where no operation produced
the escalation — at a lifecycle position where the gated operation has not run
(Section 5.1), and at a bound the executor reached (Section 5.6). A front-end binds the resolver by
the `need` token (Section 5.5); the `need` vocabulary is part of the public contract and MUST be
documented and stable within a major version. Where the need is resolvable, `outputs` carries the
`resume_token` a front-end supplies back to continue the flow (Sections 5.5, 8.2); where it is one of
the two holds below, no token is carried, which is the prohibition against resuming either made
readable from the envelope.

`retry_after` is the need a transient forge condition raises (Section 4.3). It names a wait, and the
length of that wait is not carried here: where the forge reported one, the exhausted bucket's
`resets_at` is in `outputs.forge_budget` (Sections 8.2, 9.2), and duplicating it into the escalation
would give a consumer two places to read one figure from and two ways for them to disagree.

`retryable` is a property of the **need**: a need is retryable exactly when re-invoking the same
entry point with the same arguments, after a delay and with no further action by the caller, MAY
succeed. It is fixed per need and therefore follows from a reason's default need (Section 4.3),
which is REQUIRED for every `needs_caller` reason — so the two cannot disagree, as they could if
retryability were a column on the reason registry. The values:

- Retryable: `reread_then_retry` (the re-read is what a re-invocation does), `await_checks`, and
  `retry_after`.
- Not retryable: `integrate_then_retry` (an `integrate` must run first, so re-invoking unchanged
  reproduces the same result), `resolve_conflicts`, `supply_identity`, `human_review`, and both
  holds below, which are not resolvable at all.

The field is carried rather than left for a consumer to derive from the need, because Section 8.5
permits new `need` tokens in a `MINOR` release: a consumer holding its own need-to-retryability
mapping is correct until the release that adds one and then silently wrong in whichever direction
its default guessed. Carrying the bit makes a new need absorbable, which is the job the `#class`
fallback does for a new reason (Section 5.3).

Two needs name a **hold** rather than a request, and neither is resolvable: a front-end MUST NOT bind a
resolver to either and MUST NOT resume the flow on either. Each hold is released out of band, by a new
invocation.

- `intervention` — the need a parked flow carries (Section 5.2). The policy asked for the hold.
- `flow_exhausted` — the need a flow stopped at a bound carries (Section 5.6). The executor imposed the
  hold, which is a condition to investigate rather than an outcome the policy chose, so it is a token of
  its own rather than a second use of `intervention`.

Every other need names something a caller can supply or an action it can take, which is what makes
`park` and `escalate` distinguishable in the result envelope. `reread_then_retry` is the second kind:
it is met by reading the moved state again and retrying, which is the re-entry a resume already
performs (Section 5.5), so a driver meets it by resuming and nothing else.

A need the built-in default raised (Section 5.4) is resolvable exactly as one an `escalate` action
named, and carries the reason's default need (Section 4.3). Only the two holds above are
unresolvable, and neither is reachable through that default: `intervention` is raised by `park` and
`flow_exhausted` by the executor.

### 8.5 Versioning and the Version Grammar

- The engine version is `MAJOR.MINOR`. The invocation envelope, the invocation status values, the
  proto classes, the exit-code mapping, the `need` vocabulary with each need's `retryable` value
  (Section 8.4), the class of every listed reason (Section 4.3), the configuration reasons
  (Section 6.11), the precondition reasons (Section 8.6), and the trigger kinds together with what
  constitutes an edge's key (Sections 5.1, 5.4) are the **major-stable surface**: they do not change
  within a `MAJOR`.
- The last of those is on the list for the same reason as the others, reached from what a repository
  can observe rather than from what an engine holds: a `repo.policy.toml` is written against the
  kinds an edge may be keyed on and against what distinguishes two edges, so a `MINOR` that added a
  kind or a key component would change which edge fires for a policy whose text did not change, and
  one that removed either would leave an edge that validated and never fires. Both are the shape a
  version boundary exists to carry.
- New reason tokens, new `need` tokens, new configuration reasons, new precondition reasons, new
  operations, new lifecycle positions, and new plugin backends MAY be introduced in a `MINOR`
  release; existing consumers absorb new operation reasons through the `#class` fallback (Section
  5.3), and a new configuration or precondition reason through the `usage_or_config` status, which
  does not change.
- The operation set and the lifecycle positions are this specification's rather than an engine's
  (Section 4.1), so the two additions above are a release's and never an individual engine's: a
  token outside the running version's set is `unknown_trigger` on every conforming engine (Section
  6.11) rather than validating against one and being refused by another. A `MINOR` MAY add a
  position where it may not add a trigger kind or a key component, and the argument is the one this
  section's second bullet makes for an edge's key, run in the opposite direction: a policy keyed on
  a position the running version does not define was already refused at validation, so an addition
  cannot change which edge fires for a policy that previously validated. Removing a position or an
  operation is the other half of that bullet's shape — it leaves an edge that validated and never
  fires — and is a `MAJOR` change.
- Reserving an exit code for a condition that is **not** an invocation status (Section 8.3) MAY
  likewise be done in a `MINOR`, and is not a change to the exit-code mapping the bullet above fixes:
  the four status-bearing codes and the statuses they map from are untouched. What grows is the set of
  codes a caller may observe, which Section 8.3 already makes total by reading every code outside the
  four the same way — so a consumer written against any `MINOR` from the one that states that rule
  onward absorbs a later reservation without changing.
- A policy declares a `version_floor` (Section 6.2); an engine below the floor refuses to run
  (fail-closed) with a usage/config result rather than mis-executing a policy that assumes newer
  surface.

### 8.6 Invocation Preconditions

Between validating the policy (Section 6.11) and running it, the engine establishes the
preconditions the invoked entry point depends on, in order, reporting the first that fails — with
three exceptions, which this section establishes before validation for the reasons stated below.
Where a
forge is configured it requires the forge repository coordinate and the forge-API access parameter
`forge_access` (Section 8.1), whose absence it judges itself in each case, because the argument is
either present or is not. It
resolves the work branch (Section 6.3), which calls a VCS backend capability — `derive_work_branch`,
or `current_branch` where no `branch_pattern` is configured — and judges the name it resolved with
`accepts_branch_name`. Where the caller supplied a commit identity (Section 10.1) it accepts it with
`accepts_identity`, whose shape only the backend can judge, because the engine holds identity
opaque; the shape is judged whatever the entry, so no invocation carries a malformed identity into
the policy.

For an entry that can write a commit — `commit`, `integrate`, `pull`, and a front-end
sequence that dispatches one — an identity is REQUIRED, and its absence is refused here. Each is a
capability the backend publishes (Section 9.1), so the order above is established through the plugin
API rather than inside a backend's own construction, where a refusal would carry no reason for this
registry to report. A capability consulted here that answers neither yes nor no — a backend that
could not read the checkout it was pointed at — establishes no precondition either way, and is
`checkout_unreadable` rather than the refusal its negative answer would have produced (Section 9).

Three preconditions are established **before** validation rather than after it, and each for the
same shape of reason — validation cannot proceed without what the argument names.

- `arguments_unreadable` is judged first of everything: an engine that cannot decode the
  invocation's arguments cannot locate the policy it would validate.
- `local_vcs_missing` follows, because the selection is what fixes whose descriptor the engine reads
  (Section 6.11): a validation that reports `capability_unsupported` has already loaded a backend,
  and loading one is what this argument names.
- The argument that says where the policy is read from follows, because the policy document is the
  first of Section 6.11's five inputs. There is nothing to validate until it is known. Which
  argument that is depends on the policy source (Section 8.1): `policy_branch_missing` under the
  default mode, and `base_branch_missing` under `target_branch`, which reads the policy from the
  pull-request target and so is located by the base.

The third is therefore mode-dependent while the first two are not, and exactly one of the two
applies to any invocation: `policy_branch` is neither required nor consulted under `target_branch`,
and `[base]` supplies no base under it (Section 6.4). The ordering rule this section states below
holds for every other reason in this registry.

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

`git_access` is scoped by that same rule. For an entry that can reach a remote — `provision`,
`integrate`, `push`, `pull`, and a front-end sequence that dispatches one — it is REQUIRED and its
absence is refused here; an entry outside the set that reaches `integrate`, `push` or `pull` through
a `run_op` edge reports that operation's own `failed` (Section 4.3), which is the disposition this
section already gives an identity the precondition does not cover. Those three are the whole of what
an edge can reach here: `provision` runs outside the action-policy machine, so a policy naming it is
refused at validation (Sections 4.1, 6.11) rather than reaching a dispatch. Neither access
parameter is judged for shape, because the engine interprets neither (Section 8.1): a parameter a
backend cannot use is that backend's first-use `failed` rather than a precondition this registry
names, exactly as a coordinate it cannot use is.

Under `policy_source = "policy_branch"` the base is scoped by the same rule as `git_access`. For an
entry that needs one — `integrate`, `create_pr`, and a front-end sequence that dispatches one — a
base is REQUIRED and its absence from all three sources is refused here as `base_branch_missing`;
`commit`, `push`, `pull`, `merge`, `land` and `provision` need none and run without one, `land`
taking its base from the pull request it merges (Section 12.3). An entry outside the set that
reaches a base-needing operation through a `run_op` edge reports that operation's own reason at the
dispatch (Section 4.3), which is the disposition this section already gives an identity the
precondition does not cover.

Under `target_branch` the entry point does not fix that set, and the base is REQUIRED whatever the
entry — `provision` excepted, below. The scoping rule above is about what an entry needs to *do its
work*; under this mode the base is also what says where the policy governing it is read from
(Sections 6.4, 8.1), and an entry that needs no base for its work still needs one for that. So a
`status` or a `push` invocation supplying no base from either remaining source is refused with
`base_branch_missing`, and is refused before validation rather than after it, which is the placement
`policy_branch_missing` has under the default mode and for the same reason.

`base_branch_not_permitted` is judged wherever a `base_branch` was supplied, whatever the entry,
because the bound is about what the invocation may name rather than about what the entry needs — the
same shape as the commit identity, whose *malformedness* is judged whatever the entry while its
*absence* is judged only where one is required.

`resume_unusable` is judged the same way: wherever a `resume` was supplied, whatever the entry, and
from the invocation's arguments together with what the engine holds independently of them — the
policy it validated and its own major version (Section 8.5). The fourth condition is judged from
the arguments alone, the entry point being one of them, which is what makes this reason decidable
at the two entry points that validate no policy for the first condition to compare against:
Section 6.1 calls `provision` "the one entry point that runs where no policy could be read", and
neither it nor `load_policy` runs a policy or issues a token, so a `resume` supplied to either is
refused on the entry point alone (Sections 4.1, 8.1).
It is a precondition rather than a configuration error because the artifact at fault is the
invocation: the policy is well formed, and what is wrong is a value the caller carried forward
past the point it described anything. An absent
`resume` is no failure and reaches no row here, an invocation supplying none beginning at its entry
point as every invocation did before the argument existed.

`await_bound_missing` is judged the same way: wherever an await parameter was supplied, whatever the
entry, because what is wrong is the combination the invocation named rather than an argument the
entry point required. A parameter that can only end a wait — `await_interval_ms`,
`await_budget_floor` — supplied with neither `await_bound_ms` nor `await_max_reads` describes a
wait nothing authorized to read twice, and no entry point makes that combination coherent
(Section 8.1). It is not one of the rows naming a missing argument below: nothing here is required
and absent, and an invocation supplying no await parameter at all is refused by nothing, making the
single read Section 4.1 gives it.

`policy_pin_unmatched` is judged wherever a `policy_pin` was supplied, whatever the entry, from the
surface this invocation validated against the handle the caller carried forward. It carries a reason
of its own rather than `resume_unusable` because the repairs differ, which is Section 6.11's
separation rule read on this side: a `resume_unusable` says re-invoke from the entry point, and this
says re-read the policy and decide whether this is still one unit of work. An absent `policy_pin` is
no failure and reaches no row here, and a resumed invocation is not required to supply one, its
token carrying the same judgement (Section 8.1). Its input is the surface this invocation
validated, as `resume_unusable`'s policy condition is — and the absence of one is as determinate
as a mismatch, which is what makes the row decidable at `provision`: that entry validates no
surface (Sections 6.1, 6.11), so a pin supplied to it names one this invocation did not
establish, and every such invocation is refused. A consumer holds a pin from an invocation that read
a policy, and `provision` precedes every invocation in a unit of work that did.

`provision` needs no base under either mode, and the list below is exhaustive for it. It is the one
entry point that runs where no policy could be read, being the operation that obtains the repository
the policy file is in (Section 6.1), so the argument that says where the policy is read from is one
it establishes under neither mode: it performs no policy read to locate. That is the same sentence
the Section 6.1 exemption rests on, applied to this mode's argument rather than to the document.

`provision` establishes only the preconditions judged from the invocation's arguments. It resolves
no work branch, consults no `detect_mode()`, and accepts no commit identity, because each of those
reads a checkout this operation exists to produce — so `no_current_branch`, `work_branch_invalid`,
`identity_invalid` and `checkout_unreadable` are unreachable for it, and a `provision` into a
location holding no repository is refused by none of them. What remains is the set judged from the
arguments alone: `arguments_unreadable`, `local_vcs_missing`, `git_access_missing` and
`store_location_missing`, together with the forge pair where a forge is configured, and the four
judged wherever their argument is supplied whatever the entry — `base_branch_not_permitted`,
`resume_unusable`, `policy_pin_unmatched` and `await_bound_missing`. Those four reach `provision`
for the reason they reach every entry: what they judge is a value the invocation named, and the
scoping rule that exempts `provision` from needing a base does not license it to name one outside
the permitted set. This is the Section 6.11 exemption's counterpart on the precondition side and
rests on the same sentence: the engine cannot read a repository it has not yet obtained.

A precondition the engine cannot establish is not an operation result. No operation ran, so the
Section 4.3 registry does not apply, no proto class is assigned, and there is no `<op>:<reason>` for
the policy machine to route — the entry points are the front-end sequences and the individual
operations (Section 8.1), and this is before the first of them. The engine refuses to run the policy
and returns the `usage_or_config` status (exit `2`, Section 8.3) with `op` and `class` null and
`reason` carrying one of the tokens below, which is the envelope Section 8.2 already defines for a
run in which the policy did not run.

| Condition | Reason |
|-----------|--------|
| The invocation's arguments could not be decoded in the encoding the engine published (Section 8.1) | `arguments_unreadable` |
| No `local_vcs` was supplied, so no VCS backend is selected (Section 8.1) | `local_vcs_missing` |
| No `policy_branch` was supplied, so the policy cannot be located (Section 8.1) | `policy_branch_missing` |
| A forge is configured and no forge repository coordinate was supplied (Section 8.1) | `forge_coordinate_missing` |
| A forge is configured and no `forge_access` was supplied (Section 8.1) | `forge_access_missing` |
| An entry that can reach a remote was invoked and no `git_access` was supplied (Section 8.1) | `git_access_missing` |
| `provision` was invoked and no `store_location` was supplied (Section 8.1) | `store_location_missing` |
| Under `policy_source = "policy_branch"`, an entry that needs a base was invoked and no source supplied one; under `target_branch`, any entry but `provision` was invoked and neither the invocation nor the consumer configuration supplied one (Sections 6.4, 8.1) | `base_branch_missing` |
| A supplied `base_branch` is outside the consumer's `base_branch_allowed` (Section 8.1) | `base_branch_not_permitted` |
| The work branch is the checkout's current branch (Section 6.3) and the checkout has none | `no_current_branch` |
| The derived work branch name is not a legal branch name for the VCS backend | `work_branch_invalid` |
| The caller-supplied commit identity is absent where the entry requires one, or is malformed as the VCS backend judges it whatever the entry (Section 10.1) | `identity_invalid` |
| A VCS backend capability consulted before the first dispatch could not answer — the checkout could not be read (Sections 3.3, 9.1) | `checkout_unreadable` |
| A supplied `resume` the engine cannot establish as its own and current — issued under a different policy, against a different repository, by a different major version, or by an entry point other than the one this invocation names (Sections 5.5, 8.1) | `resume_unusable` |
| A supplied `policy_pin` the engine cannot establish as naming the policy surface it validated (Sections 4.1, 8.1) | `policy_pin_unmatched` |
| An await parameter that only ends a wait was supplied with neither `await_bound_ms` nor `await_max_reads` (Section 8.1) | `await_bound_missing` |

Precondition reasons carry no proto class, for the same reason configuration reasons do not
(Section 6.11), and they share the `usage_or_config` status, so a consumer already branching on that
status absorbs a new one without a class edge. An engine MUST document any precondition reason it
adds beyond this registry (Section 13.3). An engine MUST NOT report a precondition reason for a
condition an operation has a reason that names, and the first dispatch is the boundary: before it no
operation has run, and once one is dispatched its failure is that operation's own reason
(Section 4.3). The universal `failed` reason does not satisfy that test, because it names no
condition — reading it as one would make every precondition reportable as `<op>:failed` and leave
this registry nothing to name.

What separates this registry from Section 6.11's is stated in one direction only. **A configuration
error is judged without reading the checkout**, from the five inputs Section 6.11 enumerates — the
policy document, what the engine holds independently of the invocation, the consumer's selection and
access configuration, the actions a consumer can effect and the repository units it bound. The
converse does not hold and is not claimed: a precondition MAY need the checkout and MAY be judged
from the invocation's arguments alone, as `arguments_unreadable`, `local_vcs_missing`,
`policy_branch_missing`, `forge_coordinate_missing`, `git_access_missing`, `forge_access_missing`,
`store_location_missing`, `base_branch_missing`, `base_branch_not_permitted` and
`await_bound_missing` are. Each row above says what it is judged from.

`base_branch_missing` is the one row judged partly from the policy document, since `[base] branch`
is its lowest source under the default mode (Section 6.4), and it is still a precondition rather
than a configuration error. The policy is well formed either way: a document that omits an OPTIONAL
key carries no defect to repair, and what is absent is a value the invocation or the consumer
configuration was free to supply. That is the invocation's side of the line below. Under
`target_branch` the qualification falls away and the row is judged from the invocation's arguments
alone, the policy document contributing no base — which is also what lets it be established before
the document is read.

Where both sides are checkout-free, what separates them is the artifact at fault: **a configuration
error names a defect a consumer repairs by editing a document; a precondition failure names one it
repairs by changing the invocation.** That is a distinction a consumer can act on without knowing the
order in which an engine establishes either.

Both refuse to run the policy and both report `usage_or_config`, which is why that status names usage
and configuration together. Validation precedes precondition establishment, so where a configuration
error and a precondition failure both hold, the configuration reason is reported — the three
established before validation excepted, for the reason above.

Two boundaries follow from stating it that way. A descriptor field a backend can answer only once it
has opened the checkout is **not** on the configuration side, so a policy requiring it is not a
configuration error and keeps Section 9.3's first-use disposition. And a capability a backend declares
statically is one the engine holds from the consumer's selection alone (Section 8.1), which it holds
before it validates, so `capability_unsupported` is inside this definition rather than a
counterexample to it — which is what Section 9.3's "where determinable" refers to.

The six rows naming a missing argument — the VCS backend selection, the policy branch, the forge
repository coordinate, the two access parameters and `provision`'s store location — are judged with
no capability consulted and no checkout opened, and are preconditions rather than configuration
errors because an argument is not a document: the policy is well formed and what is absent is what
the invocation was to supply.

## 9. Plugin API

The plugin layer isolates code-host and checkout-mode specifics behind neutral interfaces. Each plugin
advertises a static capability descriptor (data, not a runtime call).

Each capability answers in one of two shapes, fixed by its entry in Sections 9.1 and 9.2: it either
**answers the operation's typed result** `<op>:<reason>` (Section 4.2), or it **answers a value**
the engine composes an operation from. A capability that answers a typed result reports a condition
it could not resolve through the result itself. A capability that answers a value MUST be able to
answer that it could not determine one, and that answer MUST NOT be spelled as the value's absent or
negative case. An absent counterpart, a base the checkout does not hold, a checkout with no current
branch, a working tree that is not dirty, a revision carrying no file at the path asked for, a work
branch with no pull request, and a pull request
that has not moved since a validator was issued for it (Section 9.2) are each a
determinate fact about the remote or the checkout; none of them is "the backend could not find out".
The last is worth naming beside the others because it is the cheapest answer a capability can give
and is therefore the one most easily mistaken for having asked nothing: a capability answers
`unchanged` because it asked and was told so, never because it declined to ask.
Every such non-answer MUST map to a reason a caller can read — a Section 4.3 operation reason where
an operation has been dispatched, a Section 8.6 precondition reason where none has, the first
dispatch being the boundary between them (Section 8.6) — and the capability's own entry MUST state
which.

The obligation holds over how a capability **derives** its answer and not only over the answer it
returns. That is worth stating separately because the way it is broken is not an answer anybody
composed: a response field read as its type's default yields a well-formed value the backend never
established, and the capability then returns something that satisfies every clause above to the
letter. Where a capability's answer is derived from a response, a shape the derivation depended on
and did not find is a value it could not determine.

The rule is stated over the capability list rather than left to each capability because the failure
it prevents is silent by construction. A value-answering capability that reports its failure as the
absent answer raises nothing anywhere: the engine composes an operation from a determinate-looking
value and reports the outcome that value implies. What follows is a benign result for a run that did
nothing — a `pull:ok` for a fetch that failed, a `push` over a merged pull request, a `ship` that
reports success with the work still uncommitted — rather than the `error`-class result Section 4.3
defines for every operation. Where the two shapes are mixed without the rule, which capability can
report a failure is a property of how its signature happened to be written.

An engine MUST bound the time it waits for each network call, under `network_bound_ms`
(Section 8.1). The capabilities this covers are Section 9.1's four network-touching ones and every
capability of Section 9.2.

Section 6.6 bounds a hook because "a hook is the one place the engine hands control to a program
this specification does not describe". A network call is the second such place, and it has the same
shape: the engine hands a request to a server this specification does not describe and waits for an
answer it does not control. What an unbounded wait costs is not a slow operation but the property
the contract rests on — the engine runs a bounded sequence and exits (Sections 1, 2.2, 5.6), and a
connection a host accepts and never answers holds the invocation open indefinitely, so the exit a
consumer's escalate-and-exit loop is waiting for never arrives. Without the bound, that sentence is
conditional on every server the engine talks to answering.

What an expiry reports divides by transport. A **forge** call that reaches the bound is
`forge_unavailable`, carrying `bound_elapsed` in
`outputs.forge_unavailable_condition` (Sections 4.3, 8.2) — the same spelling Section 6.6 fixes for
a unit still running when its bound elapsed, reused deliberately, since one event on two kinds of
unit should not diagnose differently by which program the engine happened to be waiting on. A
**version-control** call that reaches it reports the reason that operation reports today:
`provision:unreachable`, whose gloss already names the network between the caller and the endpoint,
and the universal `failed` for `integrate`, `pull` and `push`. That asymmetry is the one Section 4.3
states over the transient reasons — a git remote publishes no budget and no reset time — rather than
a second one this bound introduces.

The engine stops the call and reports it; it does not retry. Whether to call again is the consumer's
(Section 2.2), and an engine retrying inside the bound would make the bound mean the total wait
multiplied by an attempt count the engine chose rather than the consumer.

### 9.1 VCS Backend Plugin

Realizes the version-control operations. Required capabilities:

- `ensure_store(store_location, remote, local_vcs)` → `provision:*`, creating the store where
  `store_location` holds none and refreshing it where it holds one, acquiring from the remote
  (Section 4.1). `local_vcs` names the checkout mode for a store this capability creates
  (Sections 3.3, 8.1); where one already exists it is refreshed in the mode it already holds, which
  the capability reads from the store rather than from this argument. A remote it could not reach is
  `provision:unreachable` and not the universal `failed`, because the endpoint and the credential it
  was given are the invocation's own arguments (Sections 4.3, 8.1).
- `derive_working_tree(store_location, tree_location)` → `provision:*`, deriving a working tree at
  `tree_location` from the store `ensure_store` maintains at `store_location`, so trees share one
  fetched copy of the repository rather than each carrying its own (Section 4.1). Reads and writes
  the checkout; acquires nothing. Invoked only where the invocation named a `tree_location`
  (Section 8.1). A backend that cannot share a store across working trees declares so in the
  descriptor below rather than discovering it here (Sections 4.3, 9.3).
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
- `read_at_source(remote, branch, path)` → the content of the file at `path` in the revision
  `branch` names for `remote`, none where that revision carries no such file, or that it could not
  be read. Reads the copy the checkout already holds; acquires nothing. The three are distinct
  answers because Section 6.1 diagnoses them apart: a source the engine could not read is
  `policy_source_unreadable` and a revision carrying no `repo.policy.toml` is `policy_not_found`,
  and the repair differs by which holds — make the source readable, or commit the file. This is what
  `load_policy` reads the policy source through, the merged `vcsx.toml` included (Sections 4.1, 6.1,
  8.1).
- `diff(base_ref)` → `diff:*`, the branch delta against the resolved base (Section 6.4). Read-only.
- `derive_work_branch(pattern, identity)` → the pinned work branch (Section 6.3).
- `worktree_revision()` → an identity for the working tree as `commit` would capture it, or that it
  could not determine one. The identity MUST differ whenever a `commit` would capture different
  content, so it distinguishes exactly what `is_dirty()` counts: every change the VCS does not
  ignore, including content the VCS has not yet recorded (Section 4.1). Its form, and how a backend
  derives it, are `Implementation-defined` and MUST be documented (Section 13.3) — this
  specification states the distinction the value MUST make and leaves the mechanism to the backend,
  as it does for an acquisition that failed (`fetch_counterpart`) and for a merge conditioned on a
  head (Section 9.2). The allowance to derive an answer by writing to the backend's own bookkeeping
  state is stated below over the whole list; it bites hardest at `before:commit`, because the
  working tree is read there on invocations the gate then blocks, and both this capability and
  `worktree_diff()` read it. That the diff and the identity come from one read is what holds the
  price to one such write rather than two: a position taking them separately writes the backend's
  bookkeeping state once for each.
- `worktree_diff()` → the diff a `commit` would record, together with the identity
  `worktree_revision()` answers for the tree it read, or that it could not determine them. The diff
  is `is_dirty()`'s question answered with content: every change the VCS does not ignore, including
  content the VCS has not yet recorded (Section 4.1), so a backend answering what it has staged
  alone hands a scan content the `commit` would not capture. Reads the checkout; acquires nothing.
  It answers two values from one call as `ahead_behind(base_ref)` does, and for the same reason:
  values taken against two reads are not a state anything held. The pairing is what binds the scan
  at `before:commit` to the capture it gates (Sections 6.6, 10.4) — an identity taken from a read of
  its own matches a tree that moved and moved back, `worktree_revision()`'s contract being stated
  over content rather than over the reads that observed it, so a `commit` conditioned on it would
  capture content no position inspected. A pair the backend could not determine is answered before
  the position runs, so no unit inspects content the operation will not use and the `commit` has no
  `expected_worktree` to supply (Section 12.2).
- `commit(message, identity, expected_worktree)` → `commit:*`. `expected_worktree` is the identity
  answered for the working tree read at `before:commit` — `worktree_diff()`'s, where the position
  scanned the tree's content, and `worktree_revision()`'s where nothing there read it (Sections 6.6,
  12.2). The capability MUST NOT create a commit from a working tree whose identity is no longer
  `expected_worktree`; it reports `commit:worktree_moved` (Section 4.3). Where that read could not
  determine an identity there is no `expected_worktree` to supply, and the operation reports
  `commit:failed` rather than capturing a tree no position inspected.
- `fetch_base(remote, branch)` → the base ref, acquiring the base as `remote` holds it (Section 4.1). A
  base it cannot acquire leaves no ref to answer with, and the engine reports
  `integrate:base_unavailable` (Section 4.3).
- `merge_base(base_ref, identity)` → `integrate:*`, bringing the acquired base into the work branch and
  preserving recorded conflict resolutions where supported.
- `fetch_counterpart(remote, work_branch)` → the ref of the work branch's remote counterpart, none where
  the remote carries none (Section 8.1), or that the acquisition failed. The last two are distinct
  answers and an acquisition the backend could not complete — the remote unreachable, the credential
  refused, the configured remote name absent from the checkout — MUST NOT be answered as an absent
  counterpart, because the two carry different results: an absent counterpart is a benign `pull:ok` and
  a failed acquisition is `pull:failed` (Sections 4.1, 4.3).
- `merge_counterpart(ref, identity)` → `pull:*`, merging the counterpart into the local branch and
  rewriting none of its commits (Section 4.1).
- `push(remote, work_branch)` → `push:*`, with the refspec pinned to the work branch. The capability
  MUST NOT cause a push that drops, rewrites or re-parents a commit already on the remote work branch;
  where the push it would make would do so, it sends nothing and reports `push:non_fast_forward`
  (Section 4.3). The requirement is stated over the effect and names no mechanism, so a backend
  satisfies it through whatever its transport provides — and a transport whose refusal is conditioned
  on something else, on the remote not having moved for example, does not satisfy it merely by
  refusing in the common case (Section 11).

OPTIONAL:

- `export_source(remote, branch, into)` → the revision `branch` names for `remote`, materialized as
  a directory at `into`, or that it could not be materialized. Reads the copy the checkout already
  holds; acquires nothing. It is what a `host_side` unit is resolved through where the form the
  engine's `run` unit takes needs a directory to resolve one from (Section 6.6): a revision is not a
  directory, and backends make one from a revision differently enough that the mechanism is not the
  engine's to own. `into` is supplied by the engine as `store_location` and `tree_location` are, so
  where the source is materialized is the consumer's decision rather than a location the backend
  chose (Section 8.1). A backend declares whether it provides this capability in the descriptor
  below, and a policy that needs one against a backend declaring none is refused at validation
  rather than reaching it (Sections 6.6, 6.11, 9.3). It is OPTIONAL because an engine whose unit
  form resolves a unit from the declaration itself materializes nothing, and a capability every
  backend must provide for an engine that never calls it is surface with no reader.

The network-touching capabilities are exactly `ensure_store`, `fetch_base`, `fetch_counterpart` and
`push`: they reach the remote at `git_access` under `git_credential` (Section 8.1) and realize the
version-control operations Section 3.2 places host-side. Every other capability above is local to
the checkout — it reads or writes the worktree and the history the checkout already holds, takes
neither the access parameter nor the credential, and acquires nothing over the network. That is an
enumeration rather than a property of a signature, so a capability's context is read off this list
and never inferred from its arguments: `resolve_base_ref` takes a `remote` and acquires nothing,
because the remote names which of the checkout's copies it answers with (Section 6.4), and
`merge_base`, `merge_counterpart`, `commit` and `derive_working_tree` write to the checkout and are
still local, because the distinction is credentials rather than mutation. `read_at_source` and
`export_source` take a `remote` and a `branch` and are local for a reason one step further out:
`provision` runs before everything the engine reads out of the repository (Section 4.1), and the
policy source resolves to the copy belonging to the resolved `remote` (Section 8.1), which that
`provision` has already placed in the store. The consequence is stated where it is already accepted
— a change to the policy source after that does not take effect until the next unit of work (Section
13.1).

An operation is realized through one capability or several. `provision` is `ensure_store`, then
`derive_working_tree` where the invocation named a `tree_location` (Sections 4.1, 8.1) — which is
what places the acquisition on the network side of the enumeration above and the tree derivation on
the local side, and what lets a consumer take the acquiring half alone without reaching a capability
that writes a checkout; `load_policy` is `read_at_source` at the policy source, once for
`repo.policy.toml` and once for a `vcsx.toml` beside it (Sections 4.1, 6.1); `integrate` is
`fetch_base` then `merge_base`; `pull` is `fetch_counterpart` then `merge_counterpart`; `commit` is
the read its position makes then `commit` — `worktree_diff` where the position scans the tree's
content and `worktree_revision` where nothing there reads it — which is what makes the tree the gate
inspected the tree captured (Section 6.6); `status` reads through `detect_mode`, `current_branch`,
`is_dirty`, `is_conflicted` and `ahead_behind`, with the forge's `pr_state` where one is configured
(Section 9.2). `pr_state` has three readers rather than one, and two of them act on the answer
instead of reporting it: `push` refuses over a CLOSED/MERGED pull request (Section 4.1) and `merge`
takes the head it conditions on from the same read (Section 9.2), which is why the state it could
not determine is refused at each rather than read as an absence. That split also fixes which reads
carry a validator (Sections 8.1, 9.2): the engine presents a `known_validator` on the read whose
answer it **reports** — `status`'s — and on neither of the two an operation **conditions a write
on**. An `unchanged` answer carries no state and so no head, and a `merge` that resolved one against
the head a consumer remembered would be conditioned on a value the engine did not read, which is the
guarantee `merge:head_moved` exists to make (Sections 4.3, 9.2). A conditional read makes a poll
cheap; it does not make a write conditional on consumer-held state.

`checks_state` is settled by the same rule reached from its own side rather than by `pr_state`'s
readers: it has one reader, `await_checks` reports its answer, and no operation conditions a write on
it, so it carries a validator — its own, `checks_state_validator` (Section 8.1). The two validators
are separate because the two capabilities read separate resources, and the engine presents each only
to the capability that issued it (Sections 8.1, 9.2).
Separating the two that acquire from the two that merge is what makes the enumeration above
exhaustive, and it places the half that stops on conflicts — the outcome the caller resolves and
`commit` finalizes (Section 4.1) — on the local side of the boundary, where the caller that resolves
it runs.

A backend MAY derive any capability's answer by writing to its own staging or bookkeeping state,
including by recording the working tree as a commit where its checkout mode requires one to inspect
it. It MUST NOT thereby change the content a `commit` would capture, the commits reachable from the
work branch or the resolved base (Sections 6.3, 6.4), or what the remote holds, and it MUST document
where it writes (Section 13.3). Those three are what Section 4.1's "Read-only" quantifies over, read
from the other end, so a capability and the operation it realizes are held to one test.

A backend that records the working tree as a commit MUST keep that commit outside what the work
branch reaches. The allowance and the prohibition above are consistent only under that arrangement:
where the work branch names the recorded commit instead, re-recording it to answer a read moves the
branch, so the commits reachable from the work branch change and the revision a subsequent `push`
would publish is not the one that existed before the read — a read failing the second of the three
by the mechanism the allowance permits. Which arrangement a mode uses is the backend's, and this
specification requires only that the recorded commit not be reachable from the branch, which a caller
can check.

The allowance is stated over the list rather than on the capabilities that happen to need it, because
which capabilities those are is a property of the checkout mode rather than of this specification: a
mode that records the working tree before it can inspect it cannot answer `is_dirty()`,
`is_conflicted()` or `worktree_revision()` without writing, and answering from a stale record instead
would report a determinate value the backend did not establish, which Section 9 forbids. The
prohibition is stated over the commits a branch reaches rather than over the object store, because a
commit no branch the engine named reaches is not something a caller can observe through this
specification's operations: what `status` and `diff` report against, and what a `push` publishes, are
branches (Sections 4.1, 9.1).

`remote` is the resolved remote (Section 8.1) and `base_ref` is the resolved base ref (Section 6.4),
both supplied by the engine; a backend reads neither from the policy nor infers one from the checkout's
own bindings. `git_access` and `git_credential` are supplied the same way, to the four capabilities
the enumeration above places on the network and to no other, so where a backend reaches and what it
presents there are the consumer's decisions rather than values the backend held (Sections 8.1, 11).
`store_location` and `tree_location` are supplied the same way to the two provisioning capabilities
and to no other, so where a backend materializes a store and a tree is the consumer's decision as
well; a backend derives neither from the checkout, which is the one it does not yet have.

`identity` on `commit`, `merge_base` and `merge_counterpart` is the commit identity (Sections 8.1,
10.1), supplied by the engine as `remote` is; the three capabilities that take one are exactly those
that can write a commit, so a mechanical merge commit is attributed no differently from a commit
`commit` writes (Section 10.1). `derive_work_branch(pattern, identity)` takes the identity the work
branch is derived from (Section 6.3), which is a derivation input rather than an attribution, and
writes no commit.

The required capabilities are the minimum every backend MUST provide, not a maximum: every operation
Section 4.1 defines is realizable through them — `load_policy` included, which reads its source
through `read_at_source` — and which operations there are is this specification's to say rather than
an engine's (Sections 4.1, 8.5), so no engine adds one that would require more. A capability a
backend provides beyond this list is visible as that backend's own rather than as shared surface.

Descriptor fields: supported modes, whether `merge_base` can reuse recorded conflict resolutions,
whether the backend can operate in a workspace with no colocated remote (Section 3.3), whether it
can derive more than one working tree from one store, and whether it provides `export_source`
(Sections 4.1, 6.6, 9.3).

### 9.2 Forge Backend Plugin

Realizes the pull-request and review operations. Required:

- `create_or_update_pr(head, base, title, body)` → `create_pr:*`, maintaining one pull request per
  work branch and refusing a base mismatch (`create_pr:base_mismatch`). Maintaining one requires
  finding the one that exists, so a backend that could not determine whether the work branch already
  has a pull request MUST NOT create one; it reports `create_pr:failed`.
- `pr_state(work_branch, known_validator)` → the work branch's pull request — its number, its state
  (open/closed/merged), the head it currently carries, and a **validator** a later read presents to
  ask for the state only if it has moved — none where the forge carries no pull
  request for the work branch, `unchanged` where `known_validator` was presented and the pull
  request has not moved since that validator was issued, or that the state could not be determined.
  Three of the four are distinct answers and a state the backend could not determine MUST NOT be
  answered as an absent pull
  request, because the two carry different results: an absent pull request lets `push` proceed and
  `create_or_update_pr` create, while an undetermined one refuses both (`push:failed`,
  `create_pr:failed`) and is a `pr_state_unavailable` output for `status` (Sections 4.1, 4.3).
  `unchanged` is the fourth and is neither of those two: it is a determinate fact about the
  resource — the state is the one the caller already holds — where an absent pull request is a
  determinate fact that there is none and an undetermined one is the backend stating neither. A
  backend MUST NOT answer `unchanged` where it presented no validator or made no conditional read,
  which is the same prohibition this section states over an undetermined answer and is stated over
  the backend's answer for the same reason: what the backend asked the forge is not something the
  engine can observe. The
  lookup is keyed on the work branch as head **whatever base the pull request targets**, because
  `create_pr:base_mismatch` exists to find one opened against a different base (Section 13.1) and a
  caller's own base therefore MUST NOT be substituted for the key. A search the backend could not
  complete is a state it could not determine and not an absent pull request — including an
  enumeration that reached a bound the backend imposes, which it MUST document (Section 13.3),
  because an incomplete search answers nothing.
- `checks_state(work_branch, known_validator)` → the aggregate state of the pull request's required
  checks — pending, passed, or failed — none where the forge reports no required checks for it,
  `unchanged` where `known_validator` was presented and the state has not moved since that validator
  was issued, or that the state could not be determined. The four answers and the prohibition on
  answering `unchanged` without having asked are `pr_state`'s, above, and hold here for the same
  reasons; a state the backend could not determine MUST NOT be answered as no required checks,
  because a pull request with no checks is mergeable and one whose checks could not be read is not.
  That answer is determinate and ends the wait: `await_checks` reports `no_checks` for it
  (Sections 4.1, 4.3). The validator this capability issues is its own — the required-check aggregate
  and the pull request move independently — and the engine presents it back only here, as
  `checks_state_validator` (Sections 8.1, 9.1). It realizes `await_checks` (Section 4.1) and exists
  so that check state is readable without dispatching a `merge`: before it, the only way to learn
  whether checks had passed was to ask a question whose favourable answer merged the work.
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

Every capability above acts against the forge repository coordinate the consumer supplied, at the
forge-API access parameter `forge_access` and under `forge_credential` (Section 8.1) — all three
supplied by the engine to the backend, as it supplies the resolved remote, `git_access` and
`git_credential` to the version-control capabilities (Section 9.1). No signature above takes a
repository, an endpoint or a credential and a backend infers none: which repository on the code host
is acted on, where the code host is reached, and what is presented there are neither read from the
policy nor derived from the checkout (Sections 3.3, 11).

Every capability above reaches the code host, needs a credential, and realizes an operation Section
3.2 places host-side; the forge plugin has no local half for an enumeration like Section 9.1's to
separate. What a consumer mediates is therefore Section 9.1's four network-touching capabilities
together with every capability of this section (Section 11).

Every capability above additionally answers, alongside its own result or value, the **budget
snapshot** the forge reported on the call it made, or that the forge reported none. The obligation
is stated over the list rather than on each capability, as Section 9.1 states its bookkeeping-write
allowance over its own list, so a capability added to this section carries it without further text.
It is answered on a call that succeeded exactly as on one that did not: a budget visible only at
exhaustion is visible only after the decision it should have informed, which is the condition
reported as a merge that could not proceed rather than as a figure that fell.

A snapshot is one or more named **buckets**, each carrying a `limit`, a `remaining` and an OPTIONAL
`resets_at`, together with the time the observation was made. It is several buckets and not one
number because one credential may hold several independent budgets — a forge accounting its
request-based and its query-based interfaces separately gives the same credential two, in two
different units — and a consumer pacing one kind of work against the other's balance is not
approximating conservatively but reading an unrelated figure. Bucket identity is opaque: the engine
carries the name the forge used, normalizes nothing, and compares nothing. A normalized bucket set
would be a mapping from each forge's accounting model into one the engine invented, and the engine
holds no basis for it — whether a forge's second bucket is a narrower window on the first or an
unrelated pool is not something a plugin boundary can establish. `limit` and `remaining` are
therefore counts in the bucket's **own** unit, which is the forge's, and this specification names
none; a consumer compares a bucket against itself over time, which is the only comparison the data
supports.

The version-control network capabilities (Section 9.1) answer no snapshot and are outside this: a
git transport publishes no quota, so there is nothing for a backend to observe and a counterpart
key there would be permanently absent.

Where a forge response does not carry the shape a capability depends on, that capability MUST answer
that it could not determine the value, and MUST NOT answer a default, an empty value, or the value's
absent case. A value found in the right place whose content the backend cannot interpret — a
pull-request state carrying a token it does not recognize — is the same condition one level in, and
reading it as `closed` because an enum's fallback arm says so is the same defect with a different
default. The consequences are the ones `pr_state`'s entry already states for an undetermined answer
misspelled as an absent one, and drift is simply the likeliest way to produce that misspelling and
the least visible in review: nothing in such a backend's source says it is assuming there is no pull
request.

A field the capability does not read is **not** this condition. A forge that adds a key, reorders an
object, or returns a member the backend ignores MUST NOT be treated as a response the capability
cannot answer from; forge payloads gain fields continuously, and a backend refusing every
unrecognized one would break on the next upstream release with nothing wrong.

Any capability above MAY answer `rate_limited` or `forge_unavailable` (Section 4.3), every one of
them reaching the code host; the obligation is stated over the list for the same reason the snapshot
is. A backend MUST NOT report a permanent refusal under either — a request the forge will refuse
identically on every retry is that operation's own `error`-class result — and MUST NOT report a
throttle under a reason naming an unrelated condition, a `merge` reporting `checks_pending` for a
refused call being the case that sends a caller to poll a forge that just asked it to stop.

What such an answer reaches a caller as is fixed by the **reader** rather than by the capability, on
the split Section 9.1 already draws for `pr_state`. Where the operation acts on the answer — `push`,
`create_pr`, `merge`, `await_checks` — it is that operation's own `rate_limited` or
`forge_unavailable` reason (Section 4.3). Where the operation reports the answer — `status`, whose
`pr_state` read is one of three — it is an output: `pr_state_throttled` for a refusal on budget and
`pr_state_unavailable` for a read that established nothing (Section 4.1), the operation completing
either way. So no capability answer is permitted that the operation reading it has no spelling for,
and the same forge condition is reported as a reason by an operation it stopped and as an output by
one it left a field short.

OPTIONAL:

- Review-thread writes: `post_review`, `reply_review`, `resolve_thread`.
- `link_issue(pr, issue_ref)` where the forge does not link natively.

Descriptor fields: PR create/update REQUIRED; the merge strategies supported; whether review-thread
writes and native issue linking are supported; whether the backend supports **conditional reads**.

A backend declaring no conditional-read support is supplied no `known_validator`, answers the full
state, and yields no `pr_state_unchanged` output (Sections 4.1, 8.1). That is not the `unsupported`
reason (Section 4.3), which names a capability an operation requires and cannot proceed without:
here the operation proceeds exactly as it would have, and what is absent is a saving. One consumer
loop is therefore correct against either backend and cheap against one of them, which is the
property that lets a consumer write one loop rather than one per forge. Which mechanism a
supporting backend realizes the validator with is `Implementation-defined` and MUST be documented
(Section 13.3) — an entity tag presented as `If-None-Match` is one, a modification timestamp is
another — as the form of `worktree_revision()` already is (Section 9.1). The engine holds the value
opaque and requires only the distinction it MUST make.

### 9.3 Capability Descriptors

The executor reads a descriptor before invoking a capability and MUST NOT invoke an undeclared one; an
undeclared capability yields an `error`-class result rather than a silent no-op. A repository policy that
requires an unsupported capability (for example a squash strategy a forge cannot perform) is a
configuration error surfaced at validation where determinable, carrying `capability_unsupported`
(Section 6.11); where it is not determinable before the policy runs, it surfaces at first use as the
operation's `unsupported` reason (Section 4.3).

What is determinable follows from what validation is judged from (Sections 6.11, 8.6). A capability
a backend declares statically follows from the consumer's selection alone (Section 8.1), which the
engine holds before it validates, so a `[messages.squash] strategy` no selected forge declares is
refused at validation — whether the policy states the strategy or takes the Section 6.8 default,
since the engine holds its own default. A consumer configuration that derives more than one working
tree from one store against a VCS backend declaring it cannot (Section 9.1) is refused the same way,
and for the same reason: the declaration is static and the consumer's requirement is held before the
policy runs. A `[hooks.engine]` unit declared against a VCS backend declaring no `export_source`,
under an engine whose `run` unit form needs the policy source materialized, is refused there too:
the backend's declaration and the engine's own form are both static, and the hook is declared in the
document validation reads (Sections 6.6, 9.1). What remains on the first-use side is an OPTIONAL
capability of Section 9.2 an operation reaches against a backend that does not declare it, and a
descriptor field a backend can answer only once it has opened the checkout. Section 9.1's OPTIONAL
capability is not on that side: what requires it is a declaration in the document together with the
engine's own unit form, neither of which an operation has to run to establish, so it falls on the
determinable half above. Neither is reachable through the operation set and the policy keys this
specification defines, so a Conformance Statement claiming the first-use half names the optional
capability or descriptor field it demonstrated the claim against (Section 13.1).

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

The composed title and body are what a scan at `before:create_pr` inspects (Section 10.4). One pull
request is maintained per work branch (created, then updated).

### 10.3 Squash (`pr_to_squash`)

For a squash merge, the squash subject and body are **mechanically transformed** from the pull request
by the repository-owned `pr_to_squash` transform at `before:merge`: by convention the title is taken
verbatim and the body is laundered per the transform (for example stripping integration-only keys), so
durable history can be stricter than the live pull-request surface. `land` runs the transform; it never
authors a message. The transform is a repository unit; the engine supplies only the position and the
pull-request content.

The unit is named by `[messages.squash]` `transform` and bound by the consumer, as a `template` body
source's unit is (Sections 6.8, 10.2); a `transform` naming a unit the consumer bound nothing to is
refused at validation (`transform_unbound`, Section 6.11). It is a unit the engine runs at a
lifecycle position and waits on, so Section 6.6's bound applies to it. A transform that gives the
engine no usable answer — it did not start, it was still running when the bound elapsed, or it
answered in a shape the engine could not read — yields `merge:hook_unanswered` (Section 4.3) and the
operation does not act: the pull request is not merged, and a caller reading its state finds the one
it had before (Section 9.2). No separate prohibition on merging with the pull request's own title
and body is needed — an operation that does not act publishes nothing, so a transform is not stepped
around by an engine that could not run it.

### 10.4 Content Scanning

A scan is a repository-owned check (`scan-content`) that inspects content — a commit diff, a title,
a body — and blocks by returning a `needs_caller`/`error` result with a stable reason, which the
engine surfaces as the scanned operation's `blocked` or `failed` reason (Section 6.6). The engine
ships no scan rules; a profile such as `strict` or `relaxed` is a repository's own name for one of
its checks, and which rules a profile applies — to a title as against a body — is the repository's
on the same terms.

A scan is bound the way every other unit the engine hands control to at a position is: it is
declared as a hook and a `[policy]` edge runs it at a lifecycle position (Sections 5.2, 6.5, 6.6).
No `[messages]` key binds one (Section 6.8), so the three contents are bound alike and a position no
edge binds runs no scan, which is what Section 5.4 has such a position do. An edge naming a hook the
document does not declare is `unknown_hook` and a hook the engine could not start is
`hook_unanswered` at first use, so a scan needs no configuration reason of its own (Section 6.11).

What the engine supplies at the position is the content and nothing else, as Section 10.3 supplies
the pull-request content to the transform: the commit message and the diff the commit would record
at `before:commit`, the composed title and body at `before:create_pr` (Sections 10.1, 10.2). A
scan's execution context follows the artifact that declares it, as every hook's does (Sections 3.2,
6.6): the `before:commit` scan is the in-sandbox one — the message was authored there and the tree
it inspects is there — where a scan the host-side policy declares over the composed title and body
runs in the consumer's context.

The diff scanned at `before:commit` is bound to the capture by the identity that came with it:
`worktree_diff()` answers the diff and the identity of the tree it read in one read, and the engine
supplies that identity as the `commit`'s `expected_worktree`, so a tree written to between the scan
and the capture is reported as `commit:worktree_moved` rather than committed (Sections 9.1, 12.2).

The title and body scanned at `before:create_pr` are the values the operation writes: the engine
composes them once (Section 10.2) and recomposes nothing between the scan and the write, so that
position needs no identity to condition on where the other two do (Sections 6.6, 9.1, 9.2).

## 11. Security and Trust Model

`vcsx` enforces no security invariant of its own; it provides the structure a consumer uses to enforce
one:

- The engine holds no long-lived credentials: it takes a credential for the duration of an invocation
  and persists none beyond it (Sections 1.3, 8.1). A consumer supplies credentials to the plugins for
  an invocation or runs the engine where they are already held.
- The engine labels every policy edge and hook with its execution context (Section 3.2) so a
  consumer can source host-side policy from a trusted revision and in-sandbox policy from the
  worktree, and can mediate the credentialed operations. An in-sandbox edge or hook MUST NOT receive
  credentials. Neither declares that context: it is fixed by the artifact each was declared in
  (Sections 6.5, 6.6), so an edge or hook the working tree supplied cannot claim the credentialed
  side by saying so, and the guarantee rests on where the text was sourced from rather than on what
  it asserts about itself. The capabilities that touch the network are named and enumerable — four
  of the VCS backend's and every required capability of the forge backend (Sections 9.1, 9.2) — so
  what a consumer mediates is a fixed list rather than something inferred from an operation's
  description.
- Provisioning is host-side (Sections 3.2, 4.1). `provision` reaches the remote at `git_access` under
  `git_credential`, so it sits with `integrate`, `push`, `pull` and every forge operation on the side
  of the boundary the consumer mediates; the in-sandbox half of a split policy receives no credentials
  and so reaches nothing the operation needs. Adding the operation therefore completes the fixed list
  above rather than adding a mechanism a consumer must enforce.
- The engine pins every push refspec to the derived work branch, so a consumer's scope guard has a
  fixed target, and no push the engine causes drops, rewrites or re-parents a commit already on the
  remote work branch (Section 9.1). The second is a property of the effect and not of the transport: a
  guard written against the presence or absence of a flag tests the mechanism a backend happens to use
  rather than the guarantee, and a transport that refuses on a different condition — that the remote
  has not moved, for example — meets the guarantee only where it also refuses a push that would drop a
  commit the remote already carries. No operation that updates the work branch rewrites, drops, or
  re-parents a commit already on it — an update that reconciles a divergence merges (Section 4.1) — so
  the branch remains publishable without rewriting it. A `rebase` or `squash` merge strategy
  (Section 6.8) is not an exception: it writes to the base branch.
- The revision host-side policy is read from is the consumer's `policy_branch` (Section 8.1), and
  the engine derives no default for it from the policy, because a branch named inside
  `repo.policy.toml` cannot select the revision `repo.policy.toml` is read from. Two properties of
  it are the consumer's to establish, stated as obligations on the consumer rather than as
  guarantees of the engine: an agent the consumer sandboxes MUST NOT be able to write to it, and the
  consumer MUST NOT direct its own merges at it. The second is the one a consumer that lands pull
  requests has to act on — a trusted revision that is also a merge target is one the work being
  landed can rewrite, which makes host-side trust a property of review rather than of sourcing.
- Everything that decides which system is reached, and with what, comes from the consumer: the
  backend selection, the forge repository coordinate, the `remote`, the two access parameters,
  `forge_parameters` and the two credentials (Section 8.1). Where the engine materializes a store
  and a working tree comes from the consumer on the same terms — `store_location` and
  `tree_location`. The engine derives none of them from the checkout or from `repo.policy.toml`.
  Which backend receives a credential, where that credential is presented, and which repository it
  acts on are therefore one decision made by one party. A selection, a coordinate or an access
  parameter read from the checkout or from the policy would let a writer with access to either
  redirect a credentialed operation to a system the credential's holder did not choose, and Section
  3.2 leaves the sourcing boundary to the consumer rather than enforcing one that would prevent it.
- Each credential is supplied with the access parameter it is used against: `git_credential` with
  `git_access` and `forge_credential` with `forge_access` (Section 8.1). Where `forge_credential` is
  unset it defaults to `git_credential`, and what that rule admits is bounded by the same one party: a
  defaulted credential is presented at the consumer's own `forge_access`, so a mismatch is an
  authentication refusal from a system the consumer chose rather than a credential reaching an
  unchosen host.
- The engine obtains the repository it acts in from those same consumer-supplied values
  (Sections 4.1, 8.1), and reads no base or branch from untrusted content; base resolution is
  configuration (Section 6.4).

A consumer that runs a sandboxed, credential-less agent (for example the Symphony service) instantiates
the agent boundary and the secret isolation; those are the consumer's, not the engine's.

## 12. Reference Algorithms

### 12.1 Match a Trigger

```text
function match_edge(policy, trigger):
  candidates = ladder(trigger)          # most-specific first
  for key in candidates:
    edge = policy.lookup(key)
    if edge exists:
      return edge
  return builtin_default(trigger)

function ladder(trigger):
  if trigger is a lifecycle position:        # before:X
    return [trigger]                          # exact only
  if trigger is a typed result op:reason:
    class = proto_class(op, reason)
    return [ "op:reason", "op:#class", "#class" ]  # substituting op/reason/class
```

The front-end sequences in Sections 12.2 and 12.3 dispatch through three names, defined here so one
spelling is used at every call site and no site reads as one where policy is not consulted:

- `run_op(op, arguments…)` runs the operation's `before:<op>` lifecycle position, performs the
  operation, and hands the operation's result to the machine, which applies the matched edge or the
  built-in default (Sections 5.3, 5.4). Policy is consulted at every dispatch. What it returns to
  the sequence is the result of **the operation the sequence dispatched** — `push`'s own result for
  `run_op("push")` — so every substitution the machine made inside that dispatch is invisible to
  the sequence, which is what pins the control transfer to the root rather than to the last link of
  a substitution chain.
- `result_of(r)` is the result the machine last handed back within the dispatch `r` came from: `r`
  itself where no repository edge substituted, and the substituted operation's result where one did.
  It is what a `return` transfer reports.
- `disposed_by_policy(r)` is true where a repository `[policy]` edge matched the trigger `r` names
  (Section 5.3), so the machine applied that edge's action in place of the built-in disposition the
  sequence writes out. It is false where the built-in default applied.

### 12.2 `ship` Sequence

```text
function ship(identity, message):
  loop:
    if flow_bound_reached():                # Section 5.6; counts every run_op, not this loop's turns
      return flow_exhausted()               # needs_caller, need = flow_exhausted
    if worktree_dirty() is clean:           # neither dirty nor undetermined (Section 9.1)
      break
    c = run_op("commit", message)         # runs before:commit, then commits the tree that
                                            # position read; commit:* re-enters the machine
    if c is commit:worktree_moved:
      continue                              # transfer: continue - re-read, re-gate, retry
    break                                   # transfer: break
  loop:
    if flow_bound_reached():
      return flow_exhausted()
    r = run_op("push")                      # runs before:push, then pushes
    if r is push:non_fast_forward:
      if not disposed_by_policy(r):         # built-in disposition; an edge replaces this block
        i = run_op("integrate")
        if i is integrate:merge_conflicts:
          return escalate("resolve_conflicts")
      continue                              # transfer: continue - retry the push, edge or no edge
    if r is push:pr_closed:
      if not disposed_by_policy(r):
        return escalate("human_review")     # built-in disposition, which ends the flow
      return result_of(r)                   # transfer: return - reports what the edge produced
    if r.class != done:
      return result_of(r)                   # e.g. push:blocked; class default (Section 5.4)
    break                                   # transfer: break - push:ok / up_to_date
  p = run_op("create_pr")                   # runs before:create_pr, then composes (Section 10.2)
  return result_of(p)                       # transfer: return - stops at the pull request
```

The routing above is the built-in default; a repository's `[policy]` edges override each step. `ship`
never runs `merge`. The sequence runs no position of its own: each `run_op` above runs its operation's
`before:<op>` position (Section 4.1), so a working tree the guard reads as clean enters no
`before:commit`.

**What an edge replaces, and what it does not.** A repository edge replaces the built-in
**disposition** of the trigger — what is done with the result. It does not replace the sequence's
**control transfer** — where the sequence goes next:

- Where the disposition returns control to the sequence, the transfer is a property of the trigger
  and is unchanged. A policy-bound `push:non_fast_forward` therefore retries the push rather than
  breaking to `create_pr`, and its `integrate` runs once rather than twice: the edge replaced the
  built-in disposition written out above, and `continue` is what the trigger transfers to either
  way. A policy-bound `commit:worktree_moved` re-reads `worktree_dirty()` and re-dispatches `commit`
  rather than falling through to the push loop.
- Where the disposition ends the flow — `escalate`, `park`, `fail` (Section 5.6), or a substituted
  result whose own default is one of those — the invocation ends inside the dispatch and no transfer
  applies. Without this clause the rule above would say a `push:non_fast_forward → escalate` edge
  continues the push loop, which is the one thing an `escalate` does not do.
- Where the transfer is `return`, the sequence reports the result the machine last handed back:
  `result_of` (Section 12.1), not the operation the sequence dispatched. A
  `push:pr_closed → run_op status` edge raises no escalation, transfers `return`, and `ship` reports
  `status:ok` — an odd policy with a determinate outcome, and the edge is honoured. Section 13.1
  states the test a caller applies to tell that ending from a completed one.

The transfer is selected by the result of the sequence's own `run_op` and by nothing else
(Section 12.1). Pinning it to that root is what keeps it determinate where a repository binds
`integrate:ok` as well as `push:non_fast_forward`: the substituted result then replaced
`integrate:ok`, which replaced `push:non_fast_forward`, and "the trigger it replaced" would name two
different things. This is the same "the trigger is the whole of the key" discipline Section 5.4
already states for matching.

**Where a resume re-enters, and what follows it.** A resumed invocation enters this sequence at the
point its token names rather than at the top (Sections 5.5, 8.1), so a token naming a point in the
push loop does not re-run the commit loop's guard, and `identity` and `message` are consulted only
where the flow ahead of that point reads them (Section 8.1). What happens after the re-entry is this
section's ordinary rule and not a second one: the re-entered dispatch's result is disposed of, and
the transfer is selected by the token's root trigger — the result of this sequence's own `run_op`
the chain descends from — which is what the un-resumed case selects on too (Section 12.1).

A `ship` that escalated `resolve_conflicts` carries `push:non_fast_forward` as that root, so the
resumed `integrate`'s result transfers `continue` and the push is retried, exactly as it is where
the `integrate` ran in the escalating invocation; the loop then breaks on `push:ok` and the sequence
reaches `create_pr`. Without the root the resumed `integrate` would be a dispatch with no landing,
since `integrate` appears in this sequence only inside that disposition and never as a step of its
own. Every `run_op` the re-entry and the continuation dispatch counts against the flow bound from
the count the token carries (Sections 5.5, 5.6), so both loops' convergence argument holds across a
resumed chain as it does within one invocation.

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

The commit loop is Section 12.3's one operation earlier. `commit` is conditioned on the working-tree
identity its position read (Sections 6.6, 9.1), so a tree that changed in between is reported as
`commit:worktree_moved` and the retry re-dispatches the operation, which re-runs `before:commit` and
reads the tree again. Routing it built in keeps this sequence from surfacing the reason at all, as it
does for `merge:head_moved`. Both reasons still carry a `need` — `reread_then_retry` (Sections 4.3,
8.4) — because a bare `commit` or `merge` entry point reaches the built-in default without a sequence
to route it (Sections 5.4, 8.1). A working tree that changes between every attempt ends the
invocation at the flow bound rather than committing a tree no position inspected, which for a caller
still writing in the worktree is the correct report.

Both loops are bounded by the flow bound (Section 5.6) rather than by a step count of their own: every
`run_op` counts against it wherever it is dispatched, so a `push`/`integrate` pair that never converges —
against a base branch that moves between every attempt, or through a repository's own edges routing back
to an earlier operation — ends the invocation at `needs_caller` with the `flow_exhausted` need instead of
running indefinitely.

### 12.3 `land` Sequence

```text
function land(await_first):
  if await_first:                            # --await, or the front-end's encoding for it
    if flow_bound_reached():                 # Section 5.6; counts every run_op
      return flow_exhausted()                # needs_caller, need = flow_exhausted
    a = run_op("await_checks")               # one dispatch, however many reads (Sections 4.1, 8.1)
    if a.class != done:
      return result_of(a)                    # transfer: return; class default (Section 5.4);
                                             # every done reason merges
  loop:
    if flow_bound_reached():                 # Section 5.6; counts every run_op
      return flow_exhausted()                # needs_caller, need = flow_exhausted
    m = run_op("merge", strategy = configured_strategy())
                                             # runs before:merge — reads the pull request, applies
                                             # pr_to_squash for a squash strategy — then merges the
                                             # head that position read (Sections 9.2, 10.3)
    if m is merge:head_moved:
      continue                               # transfer: continue - re-dispatch: re-read, re-gate
    return result_of(m)                      # transfer: return - merge:not_open / checks_pending
```

The routing above is the built-in default, as Section 12.2's is; a repository's `[policy]` edges
override it.

**What an edge replaces here is the same as in Section 12.2**, and the split matters for one branch.
A repository edge replaces the built-in **disposition** of the trigger and not this sequence's
**control transfer**: where the disposition returns control, the transfer is a property of the
trigger and is unchanged; where it ends the flow, the invocation ends inside the dispatch and no
transfer applies; and where the transfer is `return`, the sequence reports the result the machine
last handed back (`result_of`, Section 12.1). So a policy-bound `merge:head_moved` keeps its
`continue` and the merge is retried — the built-in re-read-and-retry below is not silently disabled
by an edge that only meant to observe. The transfer is selected by the result of this sequence's own
`run_op` and by nothing else, so a substitution chain inside the machine cannot move it.

**Where a resume re-enters, and what follows it.** A resumed invocation enters at the point its
token names and continues from there (Sections 5.5, 8.1): a token naming a point inside the merge
loop re-enters that loop whether or not the invocation names `await_first`, the await branch lying
ahead of it. What follows is this section's ordinary rule — the re-entered dispatch's result is
disposed of and the transfer is selected by the token's root trigger (Section 12.1) — so a root of
`merge:head_moved` transfers `continue` and the loop re-dispatches, while a root in the await branch
transfers on the class default that branch tests: a resumed `await_checks` whose result is class
`done` falls through into the merge loop rather than reporting, which is the answer the un-resumed
case gives. Every `run_op` the re-entry and the continuation dispatch counts against the flow bound
from the count the token carries (Sections 5.5, 5.6), so the loop's convergence argument holds
across a resumed chain as it does within one invocation.

The await branch is Section 7.2's composition written out, and it adds no rule: it dispatches the
operation and applies the class default Section 5.4 gives every operation result, which is why the
branch tests the class rather than a reason. Every class `done` reason therefore reaches the merge
loop below it, and a repository that wants one of them to stop the flow binds it as it binds any
other outcome. The dispatch counts **once** against the flow bound however many reads the wait made
(Sections 5.6, 8.1), so an awaiting `land` and a `land` preceded by a separate `await_checks`
invocation spend the same budget on the wait; only the loop below re-dispatches, and only its
retries count again.

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
routing is built in, `merge:head_moved` reaches a caller through this sequence only where a repository
binds it to an edge that ends the flow — but it reaches one directly through a bare `merge` entry
point, where the built-in default escalates it (Section 5.4), so the condition carries the
`reread_then_retry` need as well as its reason token (Sections 4.3, 8.4).

### 12.4 Resolve Base

```text
function resolve_base(work_branch, base_config, remote, policy_source, base_branch):
  if policy_source == "target_branch":
    return { branch: base_branch,            # the invocation's, else the consumer
                                             # configuration's (Section 8.1); base_config is
                                             # not read, because the policy it belongs to was
                                             # located by this value (Sections 6.4, 8.1)
             ref:    resolve_base_ref(remote, base_branch) }
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

The corpus additionally publishes the **shape** of a fault-injection vector without publishing its
cases. Asserting what an engine produces when a forge refuses, stalls or answers a payload missing a
field requires something to stand in for a forge and behave that way on demand, which is a harness
in an implementation's language rather than data derived from this specification; the fixture also
differs per backend, one condition reaching two forges as two different responses. The corpus
therefore fixes what such a vector MUST assert and leaves the cases to the implementation that owns
the harness. A runner that cannot execute one reports it as not run rather than as passed, so the
host-independence claim above stays true of the vectors it is made about.

A conforming engine SHOULD include tests covering:

- Matching: an `op:#class` edge catches an unnamed reason of that class; a `#class` edge catches an
  otherwise-unmatched result; a lifecycle position matches exactly with no class fallback; and the
  ladder is the whole of the selection, an edge being bound to a trigger and to nothing alongside it
  (Section 5.4).
- Undisposed policy: an unmatched operation outcome is fail-safe (parked/failed, reason surfaced,
  never dropped); an outcome whose matched edge neither ends the flow nor dispatches an operation
  reaches the same built-in default, so a `push:non_fast_forward → notify` edge under a
  single-operation entry point emits the intent and then yields `needs_caller` with the decisive
  result reported and the reason's default need, rather than an `ok` envelope, a dropped result or a
  park (Sections 4.3, 5.4); an escalation the built-in default raised carries that default need, and a
  `merge:head_moved` reached through a bare `merge` entry point escalates `reread_then_retry` rather
  than `human_review`; an `escalate` edge naming no `reason` raises the trigger's default need, and
  `human_review` where the trigger carries none; an unmatched lifecycle position runs nothing and the
  operation proceeds.
- Trigger kinds: an edge keyed on a token that is neither a known lifecycle position nor an
  `op:reason` / `op:#class` / `#class` form over a known operation is refused at validation with
  `unknown_trigger` — so a policy written against a vocabulary the engine no longer matches fails
  loudly rather than validating and never firing; the vocabulary a token is judged against is the
  running version's rather than the engine's, so two conforming engines at one version accept and
  refuse the same tokens (Sections 4.1, 8.5); `tracker.transitions`, `[tasks]` and `[driver]` are
  carried in the merged surface and validated for determinism without the executor matching their
  `on` (Sections 5.1, 6.7, 6.9, 6.11).
- Determinism: two policy edges bound to one trigger are a configuration error, as is a duplicate
  `(from, on)` transition — the two tables carrying different keys, the transition graph being the
  consumer's and scoped by a `from` state (Sections 5.4, 6.7) — and the engine refuses to run on
  either.
- Termination: a policy whose `run_op` results route back to an earlier operation stops at the flow
  bound (Section 5.6), yielding `needs_caller` with the `flow_exhausted` need and null
  `op`/`reason`/`class`; a flow that converges within the bound is unaffected; a repeated
  `(trigger, edge)` pair does not by itself stop a flow; a policy whose lifecycle positions dispatch
  one another in a cycle is refused at validation with `position_cycle` rather than reaching the
  bound, and reaching no operation is what distinguishes it — a policy whose cycle passes through a
  typed operation result, an edge on `before:push` dispatching `integrate` and an `integrate:ok` edge
  dispatching `push`, is accepted and bounded (Sections 5.6, 6.11).
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
  an unconditioned merge (Sections 4.3, 9.2); a `commit` whose working tree changed after
  `before:commit` read it creates no commit and yields `worktree_moved` rather than `ok` or
  `nothing_to_commit`, while a `worktree_revision()` that could not determine an identity yields
  `commit:failed` rather than a commit conditioned on nothing (Sections 4.3, 6.6, 9.1).
- The bounded wait: an `await_checks` exits at each of its five terminal conditions and reports the
  matching reason — checks passed, checks failed, no required checks (`no_checks`), the read
  allowance ended (`still_pending`), a supplied budget floor reached (`budget_floor`) — and the
  last two are distinguishable, so a consumer can tell which bound to raise (Sections 4.1, 4.3,
  8.1); an
  invocation supplying no await parameter makes exactly one read and does not loop, and where that
  read finds the checks still running it yields `still_pending`, its allowance being one read; an
  invocation supplying only `await_budget_floor`, or only `await_interval_ms`, is refused with
  `await_bound_missing` whatever the entry and runs nothing, while the same invocation carrying
  `await_bound_ms` or `await_max_reads` alongside runs (Sections 8.1, 8.6); a floor naming a bucket
  the observed snapshot does not carry, and a floor against a forge that publishes no snapshot at
  all, each end the wait with `budget_floor` on the first read rather than reading on; a read that
  reaches the end of the allowance and the floor together yields `budget_floor` rather than
  `still_pending`; reads honour `await_interval_ms`; each read after the first presents the
  validator the previous read returned, whether or not the invocation supplied one (Sections 8.1,
  9.2); a
  `checks_state` that could not be determined is not answered as no required checks, since a pull
  request with none is mergeable and one whose checks could not be read is not (Section 9.2); a pull
  request the forge reports no required checks for yields `no_checks` on the first read rather than
  `ok`, rather than `still_pending` after burning a supplied bound, and rather than `failed`, and a
  `land --await` against such a repository merges rather than ending on the await's result (Sections
  4.1, 4.3, 7.2); an awaiting `land` continues to the merge on every class `done` await reason and
  ends on every other class, the decision being the class rather than the reason, so a repository
  binding no edge merges under either `done` reason and one binding an edge that ends the flow stops
  under it (Sections 5.4, 7.2, 12.3); and the whole dispatch counts once against the flow bound
  however many reads it made (Section 5.6).
- Response drift: a forge response missing a field a capability depends on yields an undetermined
  answer and the refusing result, distinguishable from the response that legitimately carries no
  pull request — so a renamed field does not let `create_or_update_pr` open a second pull request,
  does not let `push` proceed over a CLOSED/MERGED one, and reaches `status` as
  `pr_state_unavailable` rather than as an absent one; an unrecognized pull-request state is
  likewise undetermined and not read as `closed`; and a response carrying an **extra** field the
  capability does not read is answered normally (Sections 9, 9.2).
- The network bound: a forge call that exceeds `network_bound_ms` yields `forge_unavailable` with
  `bound_elapsed` in `outputs` rather than the universal `failed`, and the invocation ends rather
  than waiting on a connection the far side never answers (Sections 8.1, 9); a configured value at
  the 600-second floor is accepted; the bound applies to one call rather than across an operation's
  capabilities, so an `integrate` is not held to one deadline over `fetch_base` and `merge_base`;
  and no engine-internal retry occurs inside it (Sections 2.2, 9.1).
- Transient forge conditions: a throttled forge call an operation **acts** on yields `rate_limited`
  and not `failed`, and the run escalates rather than failing, so a condition that clears on its own
  does not end a unit of work (Sections 4.3, 5.4); the same throttle reached through `status`, which
  reports rather than acts, yields `ok` with null pull-request fields and a `pr_state_throttled`
  output rather than a reason or an escalation, and is distinguishable there from a
  `forge_unavailable`, which stays `pr_state_unavailable` — so the operation that reports both keeps
  the informed repair and the uninformed one apart (Sections 4.1, 4.3, 9.2); a permanent refusal —
  a validation error the forge will refuse
  identically on retry — still yields an `error`-class result and is not reported under either
  transient reason; a `forge_unavailable` result carries `outputs.forge_unavailable_condition`
  naming which of `server_error`, `bound_elapsed` and `transport_failure` occurred, and a result of
  any other reason carries none (Section 8.2); every `needs_caller` escalation carries `retryable`,
  and its value matches the need's — `retry_after`, `await_checks` and `reread_then_retry` true,
  `integrate_then_retry` and both holds false (Section 8.4).
- Budget visibility: a forge-touching operation that **succeeded** carries a `forge_budget` output,
  so the figure is available before the decision it informs rather than only at exhaustion; a forge
  reporting several buckets yields several, each under the name the forge used and none normalized
  or summed (Sections 8.2, 9.2); an invocation reaching no forge capability carries no
  `forge_budget` key; and no engine behavior differs between a low bucket and a full one
  (Section 2.2).
- Conditional reads: a `status` supplying a `pr_state_validator` the forge reports unmoved yields
  `ok` with null pull-request fields and a `pr_state_unchanged` output, and is distinguishable from
  both a branch with no pull request and a state that could not be determined (Sections 4.1, 8.1,
  9.2); the `validator` a `status` returned in `outputs` is the value a later invocation presents,
  so the round trip closes without engine-held state (Section 8.2); a forge backend declaring no
  conditional-read support is presented no validator, answers the full state, and yields no
  `pr_state_unchanged` output rather than an `unsupported` result (Sections 4.3, 9.2); `push`
  and `merge` read `pr_state` with no validator whatever the invocation supplied, so no write is
  conditioned on a head the engine did not read (Sections 9.1, 9.2); and each capability is presented
  only the validator it issued — an `await_checks` presents `checks_state_validator` and never
  `pr_state_validator`, the validator an `await_checks` returned is the value a later invocation
  presents, so a wait that parked and resumed stays cheap across invocations, and a `status` and an
  `await_checks` in one consumer loop each carry their own (Sections 8.1, 8.2, 9.2).
- Resuming: a resolvable `needs_caller` carries a `resume_token` in `outputs` and a hold —
  `intervention`, `flow_exhausted` — carries none, so the prohibition on resuming a hold is readable
  from the envelope; supplying the token re-enters the point that raised the need rather than the
  entry point, so a resolved `commit:blocked` re-runs the gate rather than committing past it; the
  re-entered position reads the working tree and the pull-request head again rather than reusing
  what the token was issued beside; the flow then **continues** from that point rather than ending
  at the re-entered result, so a `ship` whose caller resolved a `resolve_conflicts` escalation
  retries its push and reaches `create_pr` in the resuming invocation, the transfer selected by the
  root trigger the token carries and the answer the same as the un-resumed case gives; the
  accumulated count survives into that continuation, so a resolver that resolves every time reaches
  `flow_exhausted` **across invocations** and not only within one, the bound being over the flow; a
  token the engine cannot establish as its own and current is refused with `resume_unusable` before
  the policy runs on any of the four conditions — a different policy, a different repository, a
  different major version, or an entry point other than the one the resuming invocation names — so a
  `ship` token supplied to a `land` is refused, and a token supplied to an entry that issues none,
  `provision` or `load_policy`, is refused on the entry point alone and with no policy consulted;
  and a resumed invocation does not run the flow ahead of the point it re-enters, so a `land`
  resuming into its merge loop consults no `await_first` whether or not the invocation names one,
  while a resumed `ship` consults `message` at every turn of the commit loop it re-enters (Sections
  5.5, 5.6, 7.2, 8.1, 8.2, 8.6, 12.2, 12.3).
- Consumer capability declarations: a `set_state` edge against a consumer whose `effectable_actions`
  omits `set_state` is refused with `set_state_unbound` before any operation runs, while a
  `create_task` edge against the same consumer validates, emits, and is reported in
  `unperformed_intents`; a `template` body source and a `[messages.squash]` `transform` naming a unit
  outside `bound_units` are refused with their own reasons before a push and before a merge
  respectively; and a consumer supplying neither argument is refused for all three rather than
  deferring to first use (Sections 5.2, 6.11, 8.1, 8.2).
- Per-branch selector keys: a `[[branch]]` section carrying `[base]` and one carrying `[scope]` are
  each refused with `branch_section_selector_key` before any operation runs, while a section carrying
  `[branch.messages.squash]`, a hook or an edge still applies and merges over the top level, and a
  top-level `[base] resolve = "by_prefix"` still resolves — so the mechanism that replaces the refused
  one is exercised (Sections 6.4, 6.10, 6.11).
- Provisioning: a `provision` naming a `store_location` holding no repository and a `tree_location`
  yields a checkout the remaining operations run against; a `provision` where one exists refreshes
  it and fetches no second copy, the store the first left being the one the second used; a
  `provision` naming no `tree_location` maintains the store and derives no working tree, so the
  location the omitted argument would have named holds nothing afterwards; two working trees derived
  from one store resolve the same base ref and reach the same commits, so neither carries a copy of
  its own; a VCS backend that does not declare it can derive more than one working tree from one
  store is refused at validation with `capability_unsupported` rather than at first use, while a
  `store_location` already holding a store the selected backend cannot extend yields
  `provision:store_unsupported` (Sections 4.3, 9.3); a remote the engine could not reach yields
  `provision:unreachable` rather than the universal `failed`; `provision` has no lifecycle position
  and no `[policy]` edge can gate it or route its result, so a policy that names one is refused with
  `unknown_trigger`; an in-sandbox edge receives no credential whatever it dispatches, `provision`
  included, so the operation set gains no in-sandbox path to a credentialed acquisition
  (Sections 3.2, 11); no front-end sequence dispatches `provision`, so a `ship` in a location
  holding no repository refuses on the checkout rather than acquiring one as a side effect (Sections
  4.1, 8.6, 12.2).
- The base branch and its three sources: an invocation-supplied `base_branch` beats the consumer
  configuration's, which beats `[base] branch`, and `status` reports against whichever applied; a
  policy omitting `[base] branch` is well formed and validates (Section 6.4); an `integrate` or a
  `create_pr` with no base from any source yields `base_branch_missing` and runs nothing, while a
  `commit`, a `push`, a `pull`, a `merge`, a `land` and a `provision` all run without one, `land`
  taking its base from the pull request it merges; a `base_branch` outside the consumer's
  `base_branch_allowed` yields `base_branch_not_permitted` whatever the entry, including entries
  that need no base; an entry outside the base-needing set that routes to `integrate` through a
  `run_op` edge reports that operation's own reason rather than a precondition (Sections 6.4, 8.1,
  8.6).
- The base under `target_branch`: a `status` invocation supplying no `base_branch`, against a
  consumer configuration supplying none, yields `base_branch_missing` and reads no policy —
  reported before any configuration reason the document would also have yielded, since the document
  is what the missing value locates; the same invocation with a base supplied runs, and a
  `[base] branch` present in the located document does not become the base, `status` reporting
  against the supplied one; a `[base] resolve = "by_prefix"` in that document likewise does not
  re-resolve it; and a `provision` with no base from any source runs, being the entry that performs
  no policy read (Sections 6.1, 6.4, 8.1, 8.6).
- Provisioning precedes the policy and the checkout: a `provision` into a `store_location` holding
  no repository, with no `repo.policy.toml` anywhere to discover, runs and reports `provision:ok`
  rather than any configuration reason, while the same invocation of any other entry point is not
  required to (Sections 4.1, 6.1); a `provision` against a policy carrying a `version_floor` above
  the running engine version still runs, and the next invocation of another entry against the
  repository it obtained is refused with `version_floor_unmet` (Sections 6.11, 8.5); a `provision`
  establishes `arguments_unreadable`, `local_vcs_missing`, `git_access_missing` and
  `store_location_missing` and none of `no_current_branch`, `work_branch_invalid`,
  `identity_invalid` or `checkout_unreadable`, so an empty location refuses on a missing argument or
  not at all (Sections 8.1, 8.6); a `capability_unsupported` turning on the selected VCS backend's
  descriptor is still reported at validation for a `provision`, the selection being an input the
  consumer supplied rather than one read from the repository (Sections 6.11, 9.3).
- Policy loading and unusability: the surface a unit of work executes is fixed when the unit of work
  begins — every invocation reads and validates the document itself, and one continuing a unit of
  work whose surface has since changed is refused with `policy_pin_unmatched` before the policy runs
  rather than run under either document; a `ship`, an edit to the policy source, then a `land`
  supplying the `ship`'s pin is that case, and the pin the `ship` returned is what makes it visible,
  no token having been issued; an invocation supplying no pin makes no continuation claim and runs
  the surface it read; each of the four unusable conditions — source unreadable, file absent,
  unparseable, invalid — refuses with `usage_or_config` and its own reason, so a consumer branching
  on the status handles all four alike while the reason distinguishes the repair;
  `policy_source_unreadable` covers an absent branch, an unreachable remote and a refused credential
  without distinguishing them, and a revision carrying no `repo.policy.toml` yields
  `policy_not_found` where a source the engine could not read yields `policy_source_unreadable`, the
  two being distinct answers of the capability the read is realized through rather than one absence
  read two ways; a `vcsx.toml` at the path relative to the repository root is merged and one
  elsewhere is not, so two engines reading one revision merge one document; under
  `policy_source = "target_branch"` a `policy_branch` equal to the target is not an error and
  `policy_branch` is not required (Sections 6.1, 6.11, 8.1, 8.2, 8.6, 9.1).
- The bootstrap pair: a `[policy]` edge whose `run_op` names `load_policy` and one whose `run_op`
  names `provision` are each refused with `operation_not_dispatchable` before anything runs, while
  the same edge naming `integrate` validates; an edge keyed `on = "load_policy:#error"` and one
  keyed `on = "provision:ok"` are each refused with `unknown_trigger`, the trigger side taking no
  reason of its own; `load_policy` invoked as an entry point returns the merged surface and a
  `policy_pin`; a pin returned by an entry other than `load_policy` — a `ship` — is accepted by a
  later invocation, so a consumer obtains one without invoking an entry it did not need; and a
  `provision` returns none, being the one entry point that validates no surface (Sections 4.1, 5.1,
  6.1, 6.11, 8.1, 8.2).
- The policy branch: a `policy_branch` naming the same branch as the resolved base is refused with
  `policy_branch_is_target` and runs no operation, in particular no `commit` and no `push`; an
  invocation supplying no `policy_branch` yields `policy_branch_missing`, and yields it in
  preference to any configuration reason, since the policy cannot be located to validate; a checkout
  holding a local branch named as the policy branch reads the copy the resolved remote holds and not
  the local one; a supplied `base_branch` naming the policy branch yields
  `base_branch_not_permitted` whatever `base_branch_allowed` lists and whether or not it is
  configured (Sections 6.11, 8.1, 8.6).
- Hook namespace and derived context: a hook declared in `repo.policy.toml` is host-side and one
  declared in the consumer's in-sandbox artifact is in-sandbox, with no key in either saying so; a
  `[hooks.engine.<name>]` and a consumer lifecycle key of the same name coexist without collision;
  a `[hooks.engine.<name>]` declaring no `run` is refused with `malformed_policy` while a
  consumer-namespaced key is not read as a hook at all (Sections 3.2, 6.6, 6.11).
- Derived edge context: a `[policy]` edge takes its context from the artifact it is declared in on
  the same rule as a hook, so an edge in `repo.policy.toml` is host-side and one in the consumer's
  in-sandbox artifact is in-sandbox whatever operation its `run_op` names; an edge carrying a
  `context` key is matched and dispatched with the key ignored rather than refused, so a policy
  written against the declared form stays valid and the context it names is not consulted; and the
  same policy assembled from a different artifact split yields a different context for the same edge
  (Sections 3.2, 6.1, 6.5).
- Per-branch sections: the longest matching `prefix` applies and merges over the top level key by
  key, a key the section does not mention keeping the top level's value; where no section matches,
  the top level applies alone; two sections with the same `match` are refused with
  `duplicate_branch_section`; a `match` naming no recognized matcher, or more than one, is
  `malformed_policy` (Sections 6.10, 6.11).
- Hook unit resolution: a `host_side` hook whose `run` names a unit present both in the host-side
  policy's source and in the working tree runs the former, and a working-tree unit of that name with
  no counterpart in the policy source is not started at all; a `host_side` hook does not run with
  the working tree as its working directory and is given the tree's location instead, so a host-side
  scan over working-tree content still completes; an `in_sandbox` hook resolves its unit from the
  working tree and runs there; a unit the engine could not start yields `hook_unanswered` in either
  context, so only where the engine looked differs; a merged surface declaring a `[hooks.engine]`
  unit, under an engine whose `run` unit form needs the policy source materialized and a VCS backend
  declaring no `export_source`, is refused at validation with `capability_unsupported` before the
  policy runs rather than failing where the hook is first reached (Sections 6.6, 6.11, 8.6, 9.1,
  9.3).
- Gate blocking: a `before:<op>` hook blocking with a `needs_caller` result surfaces as
  `<op>:blocked` and with an `error` result as `<op>:failed`, at every gated operation (Section 6.6);
  a gated operation dispatched by a `[policy]` `run_op` edge rather than by a front-end sequence — a
  `status` entry routing `status:ok` to `run_op` `commit` — runs `before:commit` and is blocked there
  identically, the position travelling with the dispatch rather than with the caller
  (Sections 4.1, 5.2).
- Hook bounding: a `before:<op>` hook that has not answered when the engine's bound elapses yields
  `<op>:hook_unanswered` and no operation effect, rather than `<op>:blocked`, `<op>:failed` or a
  `flow_exhausted` hold, and the result re-enters the machine so a repository edge on it is taken; a
  hook the engine could not start and one whose answer it could not read yield the same reason, with
  `outputs.unanswered_gates` naming which of `bound_elapsed`, `not_started` and `answer_unreadable`
  occurred, and a traversal that routes past one unanswered gate into a second reports both entries
  rather than the last; a gate that answered with an `error` result still
  yields `<op>:failed`, so a broken gate and a refusing gate are distinguishable; a result-triggered
  hook that has not answered when the bound elapses is stopped, leaves the flow unchanged, and is
  reported in `outputs.unfinished_hooks` under the same three condition tokens, so one consumer branch
  reads both halves; a `[hooks.engine.<name>]` declaring no `run` is refused at validation with
  `malformed_policy` while a `run` naming a unit that does not exist is `hook_unanswered` at first use
  (Sections 4.3, 6.6, 6.11).
- Front-ends: `ship` stops at the pull request, and over a working tree its guard reads as clean
  dispatches no `commit` and so enters no `before:commit` (Sections 4.1, 12.2); `ship` retries a
  `commit:worktree_moved` by re-dispatching the operation, which re-runs `before:commit` and reads the
  tree again, and a working tree written to between every attempt ends at the flow bound rather than
  committing a tree no position inspected (Sections 5.6, 12.2); `land` merges an
  open, checks-passed pull request, applies `pr_to_squash` for a squash, and never authors a message;
  `land` retries a `merge:head_moved` by re-dispatching the operation, which re-reads and re-runs
  `before:merge`, so the squash message is transformed from the revision actually merged, and a head
  that moves between every attempt ends at the flow bound rather than merging a head no position
  inspected (Sections 5.6, 12.3); the same `repo.policy.toml` yields the same operation flow through
  `ship` and an embedded driver; a driver that resolves a need and resumes re-enters the point that
  raised it — re-dispatching the operation whose result escalated, which re-runs that operation's
  position, or re-entering the position where an edge there escalated — so a resolved
  `commit:blocked` re-runs the gate rather than committing past it, the re-entered position reads the
  working tree and the pull-request head again rather than reusing the identity taken before the
  escalation, and a resolver that resolves every time ends at `needs_caller` with the
  `flow_exhausted` need because every re-entry counts against the bound (Sections 5.5, 5.6, 6.6); a
  repository edge replaces a step's built-in disposition and not the sequence's control transfer, so
  a policy-bound `push:non_fast_forward` retries the push rather than reaching `create_pr` on the
  remote's prior head and a policy-bound `commit:worktree_moved` re-reads the working tree rather
  than pushing one it did not commit, while a policy-bound `merge:head_moved` keeps its retry
  (Sections 5.4, 12.1, 12.2, 12.3); a front-end that completed its sequence reports the result of
  the operation the sequence ends at — `create_pr` for `ship`, `merge` for `land` — so a caller
  tests **the operation the result names** rather than its proto class, a repository edge being
  permitted to end a front-end early with a `done`-class result and `outputs` carrying no portable
  pull-request identifier to test instead, the keys Section 8.2 fixes being the `output_keys` group
  and the rest of `outputs` being entry-specific (Sections 7.1, 7.2, 8.2, 12.2, 12.3); the operation
  the caller reads is `op` in the envelope, which is null only where the run had no decisive
  operation result — a parked flow, one stopped at the flow bound, a `fail` on anything other than
  an `error`-class result, and an `ok` with no operation at all (Section 8.2) — so a sequence that
  dispatched anything leaves the caller an answer; and, mirroring the normative statements in
  Sections 7.1 and 7.2 rather than stating them here, a `ship` dispatches no `push` step unless a
  `commit` in the flow returned a `done`-class result where its guard read the working tree dirty,
  dispatches no `create_pr` step unless a `push` in the flow returned one, and a `land` returns a
  `done`-class result only where a `merge` in the flow reported `merge:ok` — the two statements
  about classes here being about different classes, the one a sequence tests of its own step's
  result and the one a caller would wrongly read the invocation's ending by (Sections 4.3, 5.6, 7.1,
  7.2).
- Invocation contract: exit codes mirror proto classes; `escalation` is present exactly for
  `needs_caller`; a parked flow is `needs_caller` with the `intervention` need and null
  `op`/`reason`/`class`; a `version_floor` above the running version refuses fail-closed, while one
  that is not a `MAJOR.MINOR` version is refused as `malformed_policy` rather than compared; a
  policy file that does not parse and an edge omitting the argument its action requires are refused
  with the same reason and null `op`/`class` (Section 6.11); a checkout with no current branch where
  no `branch_pattern` is configured, an illegal derived work-branch name, and a commit identity that
  is absent where the entry requires one or malformed each refuse to run the policy and yield
  `usage_or_config` with the precondition reason and null `op`/`class`, the last two judged through
  `accepts_branch_name` and `accepts_identity`, while a backend that cannot read the checkout at all
  yields `checkout_unreadable` rather than `no_current_branch` (Sections 8.6, 9.1); an entry the
  identity precondition does not cover — a `status` whose policy routes `status:ok` to `run_op`
  `commit` — runs the policy and reports `commit:identity_missing`, class `needs_caller`, rather
  than a precondition reason, while a malformed identity supplied to that same entry is refused
  before the policy runs (Sections 4.3, 8.6); a policy binding `body_source = "template"` with no
  template unit bound is refused at validation with `template_unbound` and publishes nothing, rather
  than reaching `create_pr` after a `push` has already run, and one naming a `[messages.squash]`
  `transform` with no unit bound is refused with `transform_unbound` on the same terms, rather than
  reaching `merge` after a pull request is open (Sections 6.11, 12.2, 12.3); an invocation
  whose arguments cannot be decoded yields `usage_or_config` with `arguments_unreadable`, exit `2`,
  and an envelope on stdout whose `entry` is null, while an invocation decoded far enough to name an
  entry point reports that entry point whatever failed after it and `entry` is non-null on every
  other path, including every other `usage_or_config` reason (Sections 8.1, 8.2, 8.6); an invocation
  against a configured forge with no forge repository coordinate supplied yields `usage_or_config`
  with `forge_coordinate_missing` and runs no operation, while the same invocation with one supplied
  runs; an invocation against a configured forge with no `forge_access` supplied likewise yields
  `usage_or_config` with `forge_access_missing` and runs no operation, and an entry that can reach a
  remote invoked with no `git_access` yields `git_access_missing`, while an access parameter the
  backend cannot use runs the policy and is that backend's own `failed` at first use rather than
  either precondition (Sections 8.1, 8.6); an invocation supplying no `local_vcs` yields
  `local_vcs_missing` whatever the entry point, and yields it in preference to any configuration
  reason, since the selection is what fixes whose descriptor validation reads; a `provision`
  supplying no `store_location` yields `store_location_missing`, while another entry supplying none
  runs, the argument carrying no meaning there (Sections 6.11, 8.1, 8.6); a `fail` on an
  `error`-class result reports that result under `status` `error`, while a `fail` on a
  `needs_caller` result, on a `done` result and at a lifecycle position each yield `status` `error`
  with null `op`/`reason`/`class` and report the edge's trigger and reason in
  `outputs.failed_by_policy` — so a `push:ok → fail` edge yields a failure rather than an `ok`
  envelope, and a `fail` edge carrying no `reason` is well formed and reports its trigger alone
  (Sections 5.2, 6.5, 8.2); an invocation that produces no result at all exits `1` with stdout
  empty, a code outside the four status-bearing ones is read the same way, and every result-bearing
  path emits exactly one JSON object on stdout and nothing else (Section 8.3).
- Message formulation: the `auto` PR body composes from durable inputs and agent prose replaces it; the
  squash body is the `pr_to_squash` transform of the pull-request body; every commit the engine
  writes carries the supplied commit identity — the mechanical merge commit an `integrate` or a
  `pull` writes included — on a host whose environment supplies no usable identity of its own
  (Section 10.1).
- Content scanning: a scan is reached through a `[policy]` edge at a lifecycle position and through
  no `[messages]` key, so a `before:create_pr` scan blocking with a `needs_caller` result yields
  `create_pr:blocked` while the same repository with no edge at that position publishes the composed
  title and body unscanned, the position running nothing (Sections 5.4, 6.5, 10.4); the same policy
  scans a commit diff at `before:commit` with no key naming a profile for it; the content a
  `before:commit` scan inspected is the content the `commit` captures — a working tree written to
  while the scan runs yields `commit:worktree_moved` rather than a commit of content no scan saw,
  and a tree written to and restored around the engine's reads yields no `commit:ok` over a diff the
  scan was not handed, the window an engine taking the identity in a read of its own leaves open and
  one answering the diff and the identity from `worktree_diff()` closes; a backend whose
  `worktree_diff()` answers only what it has staged is non-conforming, the diff being `is_dirty()`'s
  set and counting content the VCS has not yet recorded (Sections 4.1, 6.6, 9.1); a scan is handed
  the content of its position and a `run` edge naming a hook the document does not declare is
  refused at validation with `unknown_hook` (Sections 6.6, 6.11).
- The squash transform: a `pr_to_squash` that gives the engine no usable answer yields
  `merge:hook_unanswered` and leaves the pull request unmerged at the head it had, rather than
  merging it under its own title and body, with `outputs.unanswered_gates` naming which of
  `bound_elapsed`, `not_started` and `answer_unreadable` occurred as it does for a gate; a
  `[messages.squash]` `transform` naming a unit the consumer bound nothing to is refused at
  validation with `transform_unbound` before any operation runs, while a `[messages.squash]` naming
  no transform is valid and merges (Sections 4.3, 6.6, 6.8, 6.11, 10.3).
- Configuration ownership: a `repo.policy.toml` carrying a key this specification no longer declares —
  a `vcs`, `forge` or `remote` left over from the table `[requires]` replaced — is ignored under
  Section 6.1's forward-compatibility rule rather than refused, so a policy written against an earlier
  surface still runs; two consumers with the same consumer configuration and the same policy reach the
  same backend and the same remote, whatever each repository's file says; a `[messages.squash]
  strategy` no selected forge declares is refused at validation with `capability_unsupported`, the
  consumer's selection being what fixes whose descriptor is read (Sections 6.1, 6.2, 6.11, 8.1).
- Plugins: an undeclared capability yields `capability_unsupported` at validation where determinable
  and the operation's `unsupported` reason at first use otherwise, never a silent no-op; a
  `[messages.squash] strategy` no selected forge declares is refused at validation whether the
  policy states it or takes the Section 6.8 default, and a Conformance Statement claiming
  Section 9.3's first-use half names the optional capability or descriptor field it demonstrated the
  claim against, because that half has no producer among the operation set and policy keys this
  specification defines (Sections 6.8, 9.3); git and jj
  checkout modes (including a jj secondary workspace) are handled; the remote-touching operations
  act against the resolved remote, a consumer-supplied `remote` overriding the backend's default
  (Section 8.1); no forge capability infers a repository from the checkout or the policy, and a
  front-end that defaults the forge repository coordinate from the resolved remote and one given it
  explicitly reach the same repository (Sections 8.1, 9.2); two engines given the same policy, the
  same coordinate and the same access parameters reach the same instance of the code host, so no
  engine supplies an endpoint of its own; a `forge_credential` left unset is presented at
  `forge_access` as `git_credential`; a `forge_parameters` key no backend declares reaches the
  selected backend uninterpreted and its disposition is that backend's, the engine neither refusing
  the invocation nor reporting a configuration reason for it (Sections 8.1, 9.2); the capabilities
  that reach the network
  are exactly `ensure_store`, `fetch_base`,
  `fetch_counterpart` and `push` among the VCS backend's and every required capability of the forge
  backend, and no other VCS capability is invoked with a credential or an access parameter
  (Sections 9.1, 9.2); a push that
  would drop, rewrite or re-parent a commit already on the remote work branch sends nothing and
  yields `push:non_fast_forward` whatever the transport, including where the local work branch has
  been moved to an ancestor of the remote's tip by a writer outside the engine (Sections 9.1, 11); a
  backend that answers a read by writing its own bookkeeping state — recording the working tree as a
  commit of its own where the checkout mode requires one — leaves the content a `commit` would
  capture, the commits reachable from the work branch and the resolved base, and what the remote
  holds all unchanged, the recorded commit being one the work branch does not reach, so a repeated
  read against a modified working tree does not move the revision a `push` would publish
  (Sections 4.1, 9.1); every
  value-answering capability can report that it could not determine its answer, and no such report
  is spelled as the value's absent case (Section 9).

### 13.2 Implementation Checklist

- One policy-graph executor run by both front-ends; `ship`/`land` and the embedded-driver contract.
- The disposition/transfer split in the front-end sequences: a repository edge replaces what is done
  with a step's result, while where the sequence goes next is selected by the result of the
  sequence's own dispatch — except where the disposition ended the flow, in which case there is
  nothing to transfer. Report a completed front-end as the result of the operation its sequence ends
  at, so a consumer can tell it from one an edge ended early.
- Advance a front-end sequence only on progress it made: dispatch `push` only after a `commit` in
  the flow returned `done` where the guard read the tree dirty, dispatch `create_pr` only after a
  `push` in the flow returned `done`, and return `done` from `land` only after a `merge` in the flow
  reported `merge:ok`. Hold each over the flow, so a resume is not refused, and over the sequence's
  own steps, so a repository edge is not.
- The action-policy machine: triggers, actions, the `#class` fallback,
  fail-safe-on-undisposed-outcome, no-op-on-unmatched-position, determinism, and a flow bounded over
  `run_op` dispatches and resume re-entries — the bound over the flow, so a resumed
  invocation continues from the count its token carries rather than starting a fresh budget. Two
  trigger kinds, both engine-produced; the tables a consumer reads (`tracker.transitions`, `[tasks]`,
  `[driver]`) carried and validated without being matched.
- The operation set and the lifecycle positions as this specification fixes them, neither extended
  by the engine, and the reason-token registry with stable proto classes and a default `need` per
  `needs_caller` reason, each gated operation running its `before:<op>` position as part of every
  dispatch, and a bounded wait on every hook the engine invokes with the three conditions named.
- The provisioning operation: a store created where `store_location` holds none and refreshed where
  it holds one, a working tree derived from that store at `tree_location` where the invocation names
  one, and the store/tree relationship stated as one fetched copy with the trees that share it — the
  mechanism the backend's, the inability to share it declared in the descriptor. It is validated
  without a policy document and establishes no precondition that reads a checkout, being the
  operation that obtains both.
- Base resolution from three sources — the invocation, the consumer configuration, then
  `[base] branch` — with the bound on what an invocation may name, and the refusal scoped to the
  entries that need a base. Resolution runs before `[[branch]]` section selection and reads no
  section, and a section carrying `[base]` or `[scope]` — the keys that select it — is refused.
  Under `target_branch` the third source drops out and the refusal reaches
  every entry but `provision`, before validation, the base being what locates the policy there.
- `repo.policy.toml` loader and validation (with `vcsx.toml` merge), both files addressed relative
  to the repository root and read at the policy source through the backend, the consumer
  configuration as a second and disjoint input, including the refusal of a policy that is not well
  formed, of one declaring a hook with no unit to run, of one binding a template body source with no
  template unit bound, and of one whose lifecycle positions dispatch one another in a cycle, base
  resolution to a branch and a base ref, and the execution-context labeling — an edge's and a hook's
  alike taken from the artifact each was declared in rather than from a key, including that a hook's
  unit resolves by its context, a `host_side` one from the host-side policy's own source rather than
  from the working tree.
- The invocation contract: result envelope with every field described and `entry` nullable only where
  no entry point was read, the `outputs` keys that report what the engine emitted and nobody
  performed, what a hook left unanswered on either side of the division, and what the policy failed
  with `fail`, exit codes including the reserved code for an invocation that produced no result and
  one JSON object on stdout for every one that did, escalation payload, invocation preconditions, the
  backend selection, the forge repository coordinate, the remote, `provision`'s store and tree
  locations, the base branch with its three-source precedence and its bound, the two access
  parameters, the per-backend extension bag, the credential pair with its default, and versioning
  with a `version_floor` floor.
- The plugin API with VCS and forge backends and their capability descriptors, the VCS backend
  separating the capabilities that acquire from the local ones that use what they acquired, the
  policy source read at its revision through one of those and materialized through the OPTIONAL
  capability a backend declares, with a policy needing one no selected backend declares refused at
  validation, the engine supplying each plugin the parameter
  and credential it uses — the forge backend its repository coordinate, `forge_access` and
  `forge_credential`, the VCS backend its resolved remote, `git_access` and `git_credential` — and
  every value-answering capability able to report that it could not determine its answer, in how it
  derives that answer from a response as well as in what it returns.
- Conditional forge reads where the backend declares them: one validator per resource, each returned
  in `outputs` beside the data it describes and presented back as `pr_state_validator` or
  `checks_state_validator`, never to the capability that did not issue it; an unmoved pull request
  reported as `pr_state_unchanged` rather than as an absent or an undetermined one — with no validator
  presented on the reads `push` and `merge` condition a write on.
- The consumer's own declarations as validation inputs: which actions it can effect and which
  repository units it bound, both defaulting empty, both readable from the consumer configuration, and
  the three `*_unbound` reasons judged from them before the policy runs.
- A resume carried across the invocation boundary: an opaque token returned for a resolvable need and
  withheld for a hold, supplied back to re-enter the point that raised the need, carrying the root
  trigger and the spent flow-bound count and nothing a lifecycle position established, and
  established against four conditions — the policy, the repository, the major version and the entry
  point that issued it — the last of which an engine judges from the token and the invocation alone,
  and which is therefore the one available where no policy was validated. A resumed invocation runs
  none of the flow ahead of the point it re-enters, so an argument the flow reads only ahead of it
  is not consulted and no class of arguments has to be recognized to know that.
- A resumed invocation that **continues** the flow past the point it re-entered rather than
  reporting the re-entered result: the front-end sequence resumes its own traversal, the transfer
  selected by the token's root trigger as it is un-resumed, and the bare-operation case falling out
  of an empty remainder rather than being cased. Each of the token's three parts fixed-width, and
  the trigger carried by its registry token rather than by an ordinal into a generated enumeration.
- The two operations that run outside the action-policy machine, marked by the property rather than
  by name: no `run_op` edge naming either, no trigger an `on` may name, both reached as entry points
  instead, and the reason registry scoped to what it covers — so an operation whose every outcome is
  a configuration error sits outside the universal reasons rather than standing as a counterexample
  to them.
- The policy-surface pin carried across the invocation boundary: an opaque handle returned by every
  invocation that validated a surface and by no other, supplied back to claim that a later
  invocation continues one unit of work, and refused where the surface this invocation validated is
  not the one the pin names — the surface being read and validated on every invocation rather than
  held by the engine or handed back by the caller.
- The forge budget snapshot on every forge-touching operation, reported on success as on failure,
  carrying each bucket under the forge's own name and in the forge's own unit, with no engine
  behavior conditioned on it.
- The transient forge reasons `rate_limited` and `forge_unavailable`, both `needs_caller` so a
  throttle escalates rather than failing the flow, with `forge_unavailable`'s condition in `outputs`
  and `retryable` carried on every escalation.
- A bound on every network call, configurable to at least 600 seconds, so no unit the engine waits
  on is unbounded and the invocation exits whatever the far side does.
- The `await_checks` operation and its `checks_state` capability, bounded entirely by
  consumer-supplied parameters, counting once against the flow bound, and reading conditionally
  where the backend supports it — with check state readable without dispatching a `merge`; only
  `await_bound_ms` and `await_max_reads` authorize a second read, and an invocation supplying a
  parameter that can only end a wait without one of them is refused with `await_bound_missing`.
- Message formulation seams (`scan-content`, PR composition, `pr_to_squash`) with no built-in
  format, every commit the engine writes attributed to the supplied commit identity, a scan reached
  through a policy edge at a lifecycle position rather than through a key of its own, and a
  transform that gives no usable answer leaving the pull request unmerged.
- Checkout-mode handling (git, jj, jj secondary workspace), a pinned push refspec whose push never
  drops, rewrites or re-parents a commit already on the remote work branch, a history-preserving
  work-branch update, and the two operations conditioned on the state their position inspected — the
  merge on the pull request's head and the commit on the working tree's identity, the latter
  supplied from the read that produced the diff the position scanned rather than from a read of the
  engine's own.

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
  detection (Section 3.3), the flow bound's value and any further bound the engine imposes (Section
  5.6), `repo.policy.toml` and `vcsx.toml` discovery precedence (Section 6.1), the form of a hook's
  engine-invoked `run` unit, how a `host_side` unit is addressed within the host-side policy's
  source and what working directory it is given, and the bound the engine waits for one under
  (Section 6.6), which reason is reported when several configuration conditions hold (Section 6.11),
  the consumer configuration's discovery precedence, the backend's default remote where the consumer
  supplies none, the entry-point argument encodings and how a front-end derives the forge repository
  coordinate where it does, the default `network_bound_ms` and any per-capability values the engine
  applies (Sections 8.1, 9), the form of the `resume_token` — how it spells the three parts Section
  5.5 fixes, whether it is signed, and the mechanism by which the four conditions Section 8.1 fixes
  are judged, those parts and those conditions themselves being specified rather than declared — the
  form of the `policy_pin` and how the engine establishes that one it is handed names the surface it
  validated (Sections 8.1, 8.2, 8.6), the `detail` field of an `unanswered_gates` entry (Section
  8.2), and the escalation `detail` field
  (Section 8.4).
- Any reason token the engine adds beyond a registry: an operation reason with its proto class and,
  where that class is `needs_caller`, its default `need` (Section 4.3), a configuration reason
  (Section 6.11), or a precondition reason (Section 8.6).
- The `need` vocabulary the engine emits (Section 8.4).
- The capability descriptors its VCS and forge plugins advertise (Section 9.3), the
  `forge_parameters` keys each forge backend reads, which are `Implementation-defined` per backend
  (Section 8.1), any bound a forge
  backend imposes on its search for a work branch's pull request (Section 9.2), the form of
  `worktree_revision()`'s value and how a backend derives it (Section 9.1), where a backend
  writes its own bookkeeping state to answer a capability (Section 9.1), — where a forge backend
  declares conditional-read support — the mechanism it realizes the `pr_state` and `checks_state`
  validators with, and which budget buckets each forge backend observes and where it reads them from,
  both `Implementation-defined` per backend (Section 9.2).

The Statement is a published declaration, not a precondition for running the engine: Section 13.1 and
Section 13.2 keep their roles as the test matrix and the definition of done. Its format is
`Implementation-defined`. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` in the specification repository is
the RECOMMENDED shape: it enumerates each obligation above as a row an engine fills.

A deployment that embeds this engine declares it from the consumer's side as a version pin, in the
consumer's own statement; an `engine-direct` deployment publishes this Statement alone.

## 14. Alignment with `VCSX-CONTRACT.md`

`VCSX-CONTRACT.md` is the surface an embedding consumer references; this document is its full
realization. Every token shared between the two — the operations, the lifecycle positions, the
trigger and action names, the proto classes, the reason and `need` vocabularies, the
`repo.policy.toml` sections, the task and message-formulation surfaces — MUST be spelled identically
in both. The operations and the lifecycle positions are additionally fixed as **sets** by this
specification (Sections 4.1, 8.5), so `VCSX-CONTRACT.md`'s closed lists are the whole of each at a
version rather than a core an engine extends. Changing a name is a contract change: update both
documents in step, and record it where the owning consumer tracks its anchors. This engine spec was
shaped by the surface it realizes and by the Symphony decision record (0026–0032) that motivated the
surface; those hold the reasoning, this document holds the schema and algorithms.
