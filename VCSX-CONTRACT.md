# vcsx Engine Contract (Surface)

Status: Draft — contract surface.

Purpose: Fix the shared vocabulary — names and surface semantics — of the `vcsx` VCS-workflow engine
that `SPEC.md` (Symphony) defers to, so the repo-owned Way-of-Working parts of `SPEC.md` reference
stable tokens that stay identical across both documents. This is the **surface**: it fixes names and
surface semantics and defers the invocation contract, the field-level `repo.policy.toml` schema, the
plugin API, and the engine's internal algorithms to the full engine specification, `VCSX-SPEC.md`
(Section 11).

## Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, and
`OPTIONAL` in this document are to be interpreted as described in RFC 2119.

`Implementation-defined` means the behavior is part of the implementation contract, but this document
does not prescribe one universal policy. Implementations MUST document the selected behavior.

## 1. Status and Deferral Boundary

`vcsx` is an independent, reusable VCS-workflow engine, usable on its own and consumed by Symphony
through the contract named here. Symphony's `SPEC.md` defers to this contract the way it already
defers to the coding-agent app-server protocol: the spec owns *orchestration semantics* — what the
engine is asked to do and when — and this document owns the engine's *entry points, policy vocabulary,
and result surface*. Neither document restates the other's schema.

This stub fixes:

- the executor and its two front-ends (Section 3),
- the repo-owned policy surface `repo.policy.toml` and the consumer configuration alongside it
  (Section 4),
- the action-policy machine — triggers, actions, matching, unmatched policy, and the reason-token
  class contract (Section 5),
- the engine operations and their typed results (Section 6),
- the lifecycle positions (Section 7),
- the task model and broker task verbs (Section 8),
- the message-formulation surfaces (Section 9),
- the trust-sourcing rule and the secret/integrity taxonomy (Section 10).

This stub does **not** fix — and defers to the full engine spec (Section 11): any engine wire/RPC
schema and its version grammar, the field-level `repo.policy.toml` schema, the field-level schema of
the consumer configuration and the rule that locates it, the plugin API for VCS and code-host
backends, how a backend realizes the store `provision` maintains and the working trees derived from
it, the concrete reason-token registry beyond the classes and named results below, and all internal
algorithms.

Names in this document and in `SPEC.md` MUST stay identical. A token added or renamed here is a change
to the shared contract and MUST be reflected in both documents (see Section 12).

## 2. Consumption Model

- `vcsx` is an independent deliverable, pinned and invoked as an external tool the way the surrounding
  ecosystem pins other engine tools, and released on its own cadence. Symphony does not vendor the
  engine's implementation.
- Conformance is to the **contract**, not to a specific binary, runtime, or implementation language.
  This document names no implementation language normatively.
- Symphony reaches the engine only through this contract; a code host (for example GitHub or Forgejo)
  is reached through the engine's plugin layer, not through parallel Symphony adapters.
- The engine obtains and maintains the repository it acts in: `provision` (Section 6) creates the
  checkout where none exists and refreshes one that does, so a consumer implements no version
  control alongside it. A checkout the engine did not create remains drivable.

## 3. Executor and Front-Ends

- There is **one policy-graph executor**. It reads one `repo.policy.toml` (Section 4) and runs the
  action-policy machine (Section 5) against engine operations (Section 6).
- The executor has **two front-ends** over that one executor:
  - the interactive front-end, entered through `ship` and `land`;
  - the embedded driver (for example Symphony's autonomous daemon).
- The two front-ends differ **only** in their initiator and in how the abstract `escalate` action
  (Section 5.6) is bound. They MUST run the same executor over the same policy, so a given
  `repo.policy.toml` yields the same operation flow through either front-end.

Entry points:

- `ship` — drive the policy from the current change up to and including opening/updating the pull
  request; `ship` stops at the pull request and does not merge.
- `land` — drive the merge of an already-open pull request. `land` transforms message content
  (Section 9); it never authors a message. `land` MAY be invoked to await required checks first,
  which composes the two operations below and introduces no sequencing of its own.
- `await_checks` — wait for the pull request's required checks, bounded by parameters the consumer
  supplies. It is an operation (Section 6) and an entry point; the engine executes the wait and
  decides none of its bounds.

## 4. `repo.policy.toml` (Config Surface)

`repo.policy.toml` is the **repository-owned** Way-of-Working file. It holds:

- `[requires]` — what the policy document requires of the engine reading it, namely the engine
  `version_floor`,
- `scope.branch_pattern` — the branch-*name* pattern for the work branch (the scope invariant itself
  is not configurable; Section 10),
- the action-policy edges, and the named hook units `[hooks.engine.<name>]` a `run` edge invokes
  (Section 5). Neither an edge nor a hook declares an execution context: the artifact it is declared
  in fixes that, so one in `repo.policy.toml` is host-side and one in the consumer's in-sandbox
  artifact is not.
  The `hooks` namespace is shared with the consumer, whose own hooks sit under a disjoint prefix,
- `[[branch]]` sections, each matching a base-branch prefix and merging its keys over the top level
  so one policy document can differ by the branch a unit of work targets. A section carries no key
  that resolves the base or names the work branch, those being what select the section,
- `tracker.transitions` — the workflow state-machine, expressed as `set_state` bindings in the machine
  (Section 5),
- `[tasks]` and `[driver]` — the task model and computed-completion wiring (Section 8).

An engine-native configuration file (`vcsx.toml`) is merged into `repo.policy.toml` as the same
surface, so a repository expresses one policy consumed identically by the interactive front-end and the
daemon.

The engine's other configuration input is the **consumer configuration**: the consumer's own, and
never sourced from the repository. It holds what the engine needs before there is a repository to
read a policy from — which VCS and forge backends are selected, where each is reached and under
which credential, the remote the repository was provisioned from, where `provision` materializes the
store and the working tree, the **policy branch** the host-side parts of `repo.policy.toml` are read
from, which of the consumer-effected actions this consumer can perform and which repository units it
bound, and the pull-request target with any bound on what an invocation may name — none of which a
file inside the repository can supply to the step that obtains the repository or selects the
revision the file itself is read from, and the last of which the file MAY also supply as the
lowest-precedence source. The term
names the input, not a file: where the engine discovers it is `Implementation-defined` and MUST be
documented. The two surfaces carry disjoint keys, so neither shadows the other.

The field-level schema of both surfaces is deferred (Section 11). The **sourcing** of
`repo.policy.toml` — which revision each part is read from — is fixed in Section 10.

## 5. The Action-Policy Machine

One `(trigger) → (action)` machine governs the operation flow. It subsumes what were previously three
separate shapes: the tracker transition graph, positional lifecycle hooks, and ad-hoc VCS-outcome
handling.

### 5.1 Triggers

A trigger is one of two kinds:

- **Lifecycle positions** — points around an engine operation:
  - `before:commit`
  - `before:push`
  - `before:create_pr`
  - `before:merge`
- **Typed operation results** — the outcome of an engine operation (Section 6), of the form
  `<op>:<reason>`, for example:
  - `push:ok`
  - `push:non_fast_forward`
  - `integrate:merge_conflicts`

Both kinds are produced by the engine itself — a position it entered, a result an operation it ran
returned — so a trigger's producer and its matcher sit inside one invocation. An event the consumer
observes is not a trigger: it selects which **entry point** the consumer invokes, which is what the
task model's `[driver]` wiring is for (Section 8).

Hooks are edges: a lifecycle-position trigger is where a repo-owned hook runs, and a result trigger is
where a repo-owned reaction runs. There is no separate hook axis (see Section 7).

### 5.2 Actions

An action is one of:

- `run_op` — run an engine operation (Section 6).
- `run` — run a repo-owned hook.
- `escalate` — raise a need whose resolver the front-end binds (Section 5.6).
- `create_task` — create a task (Section 8); a no-op where no task model runs.
- `set_state` — apply a workflow-state transition.
- `notify` — emit an operator/human notification.
- `park` — stop the flow and hold for intervention, without failing it.
- `fail` — end the flow as failed.

### 5.3 Matching and the `#class` Fallback

Trigger matching is **most-specific-wins** over a fallback ladder, so a configuration need not
enumerate every reason token and can survive new reason tokens:

1. `op:reason` — an exact result token (for example `push:non_fast_forward`).
2. `op:#class` — the operation with a proto **outcome class** (for example `push:#needs_caller`,
   since `push:non_fast_forward` is class `needs_caller`).
3. `#class` — the proto outcome class alone (for example `#needs_caller`).
4. a built-in default.

The proto outcome classes are a closed set:

- `done`
- `needs_caller`
- `error`

### 5.4 Unmatched Policy

- An unmatched **lifecycle position** is a benign no-op: nothing runs there and the operation
  proceeds.
- An **operation outcome no action disposed of** MUST be **fail-safe**: it is parked or failed and its
  proto reason is surfaced. It MUST NOT be silently dropped, because a dropped operation outcome would
  strand a run. An outcome is disposed of by an action that ends the run or by a `run_op` whose own
  result takes its place, so an outcome that matched no edge and one whose edge merely emitted an
  intent are treated alike: matching is not disposal.

### 5.5 Reason-Token Class Contract

Every reason token carries a proto **class** (`done` / `needs_caller` / `error`). The class of each
reason token is part of the public contract, because configurations branch on it through the `#class`
fallback (Section 5.3). The concrete registry of reason tokens is deferred (Section 11); the three
classes are fixed here.

### 5.6 Abstract `escalate`

`escalate` names a *need* — a point where the flow cannot proceed autonomously — and the **front-end**
binds the *resolver*:

- under an embedded driver (for example the autonomous daemon), `escalate` binds to an agent-assigned
  task (Section 8);
- under the interactive front-end, `escalate` returns a typed result to the human.

`escalate` is what lets the same `repo.policy.toml` run under both front-ends (Section 3). It is the
one place the two front-ends legitimately differ.

A resume re-enters the point that raised the need, and it round-trips through the consumer: an
invocation that ends on a resolvable need returns a token, and the invocation that resumes supplies
it back. The engine holds nothing between invocations, so the flow bound accumulates across a resumed
chain rather than restarting — which is what keeps the bound a property of the flow under either
front-end. A need naming a **hold** rather than a request carries no token and is not resumed.

## 6. Engine Operations and Typed Results

`run_op` (Section 5.2) runs an engine operation. The engine's plugin layer realizes each operation
against the selected backends — the VCS backend, and a code host such as GitHub or Forgejo; the
operation set and its result classing are host-neutral. Named operations include:

- `load_policy` — obtain the merged host-side policy surface once for a unit of work, from the
  policy source the consumer names. The consumer holds the result and supplies it to subsequent
  invocations, so no other operation reads the repository's configuration. Like `provision` it has
  no lifecycle position and raises no trigger, the edges that would gate it being in the document it
  obtains. Four conditions leave it without a usable policy — the source unreadable, the file
  absent, unparseable, or invalid — and all four are configuration errors differing in reason
  rather than in disposition.
- `provision` — ensure the repository is present and current: create the store where absent, refresh
  it where present, and, where the invocation names a place for one, derive a working tree from it.
  The store and the tree are named by the consumer, as a store location and an OPTIONAL tree
  location; an invocation naming no tree location maintains the store alone. It is credentialed,
  like `push` and `merge`; the agent's broker verb set (Section 8) carries no provisioning verb. It
  runs before everything the engine reads out of the repository, so it has no lifecycle position,
  raises no `<op>:<reason>` trigger, is validated against no policy document, and establishes no
  precondition that reads a checkout: all four are matched, read, or judged against what is inside
  the repository this operation obtains. A consumer dispatches it and classifies its result rather
  than routing it through the machine.
- `commit`
- `integrate` — bring the base branch into the work branch (back-merge / update-branch).
- `push`
- `create_pr`
- `merge` — merge/request-merge the pull request.
- `await_checks` — read the pull request's required-check state until the checks pass, fail, the
  forge reports no required checks for the pull request, a bound the consumer supplied is reached, or
  a budget floor the consumer supplied is reached. The third is a determinate answer rather than a
  wait that ended, and ends the wait on the first read. Read-only,
  gated at no lifecycle position, and bounded only by parameters the consumer supplies: the engine
  does not decide how long to wait, how often to ask, or how much budget is too little to keep
  asking. It exists so that check state is readable without dispatching a `merge`, which would ask a
  cheap question with a mutating request.

Each operation completes with a typed result `<op>:<reason>` whose `reason` carries a proto class
(`done` / `needs_caller` / `error`, Section 5.3), which is itself a trigger (Section 5.1). For example,
`push:ok` is class `done`; `push:non_fast_forward` is class `needs_caller`; `integrate:merge_conflicts`
is class `needs_caller`. The exhaustive per-operation reason registry is deferred (Section 11).

## 7. Lifecycle Positions

The lifecycle-position triggers of Section 5.1 are the fixed points around the operations of
Section 6. `provision` has none, for the reason its entry in Section 6 states. Earlier positional hook
names map onto the machine as follows, so a repository expressing a policy in the older positional
form aligns to the same edges:

| Positional hook name | Machine trigger |
|----------------------|-----------------|
| `before_commit`      | `before:commit` |
| `before_push`        | `before:push`   |
| `after_push`         | `push:ok`       |
| `before_pull_request`| `before:create_pr` |

`before:merge` is a lifecycle position shared by the message-formulation transform (Section 9). Base
resolution for `integrate`/`create_pr` is configuration (`scope.branch_pattern` names the work branch;
the base branch is repo config), not a hook.

## 8. Task Model and Broker Task Verbs

The task model makes completion **computed** rather than asserted. It is used by the autonomous daemon
driver; the interactive front-end has no task manager and uses `ship`/`land`.

Task:

- `id`
- `description`
- `status` — `open` / `closed` / `blocked`
- `assignee` — `agent` / `human`
- `parent` — OPTIONAL; the task this one hangs from
- `tracker_link` — OPTIONAL; the tracker artifact this task corresponds to

Broker task verbs (exposed to the credential-less agent through the broker CLI; they carry no
credentials):

- `add`
- `split`
- `close`
- `need-help`
- `update`

Semantics fixed at the surface:

- **Seeding** — tasks seed from the ticket when the tracker exposes structured tasks (capability-gated;
  the `structured-task-write` tracker capability), otherwise from an opening planning turn.
- **Computed completion** — the consumer watches its own task state for the `[driver]` `on` condition
  (`tasks:all_closed`) and invokes the entry point `run` names, replacing an asserted completion flag.
  The tables travel in `repo.policy.toml` because the repository owns the wiring; the engine matches
  neither, its triggers being the two kinds Section 5.1 fixes.
- **Escalation as tasks** — a need bound by `escalate` (Section 5.6) becomes an agent-assigned task;
  `need-help` is an agent-created human-assigned task that parks for feedback.
- **Write-through materialization** — the agent's `add`/`split` cause the broker (credentialed; the
  agent stays secret-free) to create/maintain structured tracker artifacts (sub-issues / checklist
  items). This is gated by the `structured-task-write` tracker capability and is default on where that
  capability exists; a repository disables it in `repo.policy.toml`.

## 9. Message Formulation

Message **content** is the agent's; message **formulation policy** is repo-owned Way of Working. The
three surfaces have distinct origins:

- **Commit message — authored.** The agent authors it in-sandbox (conventions conveyed by the prompt),
  validated by `scan-content` at the `before:commit` position. Author/committer identity is repository
  configuration, distinct from content. A mechanical merge commit uses the engine default *message*
  and carries that same configured identity; the engine attributes no commit to an identity it
  derives from the host it runs on.
- **Pull-request message — composed.** Title and body are composed from agent-supplied prose and/or
  durable inputs (the ticket, the closed task list from Section 8, commit subjects), and are what a
  `scan-content` check at the `before:create_pr` position inspects — strictly for the title, with
  the tracker-key relaxation the code host's integration needs for the body. Which rules apply to
  which is the repository's, as every scan rule is: the check is reached through a policy edge at
  the position, and no configuration key names a profile per field. One pull request is maintained
  per issue (created, then updated). The default body is auto-composed from the durable inputs;
  agent-supplied prose, when present, overrides (replaces) it.
- **Squash message — transformed.** The squash subject/body are mechanically derived from the pull
  request by a repo-owned `pr_to_squash` transform at the `before:merge` position (title verbatim,
  body laundered — for example stripping tracker keys). `land` runs this transform; it never authors
  a message. A transform that gives the engine no usable answer leaves the pull request unmerged
  rather than merging it under its own title and body.

A credential-free content seam on the broker CLI lets the agent supply pull-request text across the
sandbox boundary without holding credentials.

## 10. Trust Sourcing and the Secret/Integrity Taxonomy

Sourcing (which revision each part of `repo.policy.toml` is read from):

- **Host-side-executed** Way of Working — host-side hooks, the operation flow, and the branch-name
  pattern — is read from a **trusted revision the consumer names**, which the agent cannot write to
  and which the consumer's own merges do not reach. WoW-config trust therefore equals trusted-branch
  trust. That revision is not the pull-request target and is not derived from `repo.policy.toml`: a
  branch named inside the file cannot select the revision the file is read from, and a branch the
  consumer merges into is one the work it lands could rewrite.
- **In-sandbox** parts — the `before:commit` gate/scan — are read from the **worktree**, where an
  agent's edit is harmless and where a pull request's own gate change is correctly exercised.
- A hook's **unit** — the program its declaration names — is sourced as its declaration is: from the
  trusted revision for a host-side hook, from the worktree for an in-sandbox one. A host-side
  declaration sourced from a revision the agent cannot write, naming a program the agent can, would
  carry no trust at all. A host-side hook does not run with the worktree as its working directory;
  it is given the worktree's location, so it can read the tree without executing from it.

The consumer configuration (Section 4) is sourced from no revision of the repository. The selections
and access values it carries are the consumer's, so which backend receives a credential and which
endpoint that credential is presented to are one decision made by one party.

Secret/integrity taxonomy:

- **Outward credentials** (VCS/forge/tracker credentials) are broker-mediated and never enter the agent
  sandbox. This is the one enforced invariant: the agent never holds a VCS/Forge credential.
- **Repo-internal integrity values** (for example a gate-cache HMAC) are repo-owned, supplied to a
  host-side hook's environment, and are **not** broker-mediated. They are not outward credentials.

The engine enforces no Way of Working beyond this secret-isolation invariant; whether any cached or
signed artifact exists or is trusted lives entirely in the repository's wired hooks.

## 11. Deferred to the Full Engine Spec

This surface deliberately does not fix, deferring them to the full engine specification
(`VCSX-SPEC.md`):

- the engine invocation contract (result envelope, exit codes, escalation payload) and the version
  grammar (`VCSX-SPEC.md` Section 8);
- the field-level schema of `repo.policy.toml` and its sections (`VCSX-SPEC.md` Section 6);
- the field-level schema of the consumer configuration (Section 4) and the rule by which the engine
  locates it (`VCSX-SPEC.md` Section 8.1);
- the plugin API for VCS and code-host backends (`VCSX-SPEC.md` Section 9);
- the mechanism by which a backend realizes the store `provision` maintains and the working trees
  derived from it (`VCSX-SPEC.md` Sections 3.3, 9.1);
- the concrete per-operation reason-token registry beyond the classes (Section 5.5) and the named
  results (Section 6) here (`VCSX-SPEC.md` Section 4.3);
- the engine's internal algorithms (`VCSX-SPEC.md` Section 12).

An implementation MUST consult `VCSX-SPEC.md` for these. Where this surface and the full spec appear to
conflict on a *name*, the name here governs until the two are reconciled (Section 12); where they
conflict on *schema or algorithm*, `VCSX-SPEC.md` governs.

## 12. Provenance and Alignment

- Symphony's `SPEC.md` defers to this contract. The deferred repo-owned Way-of-Working edits to
  `SPEC.md` reference the tokens fixed here, and the two documents MUST keep identical names.
- This surface is shaped by Symphony decisions 0026–0032 (the repo-owned WoW re-framing) and reused by
  the execution-process decisions 0035–0038 (the executor embeds this policy-graph executor). Those
  decision records hold the reasoning; this document holds the frozen names.
- Changing a name here is a contract change: update `SPEC.md` in step, and record the change in the
  owning decision's `Anchor changes`.
