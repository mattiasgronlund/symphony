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
`Rejected` (decided against; kept for the record).

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

**State:** Accepted
**Folder:** [decisions/0005-config-trust-split/](decisions/0005-config-trust-split/)

Configuration splits on the sandbox boundary: `WORKFLOW.md` (repo-owned, untrusted) holds only settings
used *inside* the sandbox — the prompt and in-sandbox build/test hooks — while a new operator-owned
policy config holds everything Symphony uses outside the sandbox (credentials, scope rules, sandbox
profile, repo map, the workflow state-machine, agent selection, privileged setup hooks). Both surfaces
hot-reload with last-known-good-on-invalid. This retires the "hooks are fully trusted configuration"
assumption.

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
