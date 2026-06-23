# Background — 0003 Responsibility inversion and the credential broker boundary

## Context

The current `SPEC.md` casts Symphony as a scheduler/runner and tracker *reader*: the coding agent
holds whatever credentials it needs and performs the side effects itself (ticket writes via the
`linear_graphql` tool, any VCS work via workspace hooks). The Section 1 "Important boundary" and
Section 11.5 "Tracker Writes (Important Boundary)" make this explicit. That posture pushes all trust
onto the agent's runtime: a prompt-injected or buggy agent runs with live credentials and
unconstrained reach.

We want the opposite default. Symphony should own every privileged, outward-facing side effect — VCS
remote operations, pull-request creation, and all issue-tracker interaction — while the agent supplies
only the *content* of those operations and never holds a credential. This single inversion is the
keystone the other re-architecture decisions hang off: sandboxing (0004), the config/trust split
(0005), and the agent/VCS/tracker adapters (0006–0008) and multi-repo work (0009) all assume the
broker boundary defined here.

## Options considered

### How the agent invokes a privileged operation

- **Thin credential proxy.** Agent runs native `git`/`gh`/`tea`; Symphony only injects credentials (a
  git credential helper, a forwarded ssh-agent) and validates nothing. Native and flexible, but the
  agent can do anything the credential allows, scoping is hard, and each backend tool's quirks leak
  back into the sandbox.
- **Hybrid.** Semantic interface for PRs/tracker writes, thin proxy for raw git network ops. Plays to
  each strength but doubles the mechanisms to secure and document.
- **Semantic CLI (chosen).** A high-level `symphony` CLI models each operation (push, open/update PR,
  comment, ...), so Symphony can validate and scope every call and present identical verbs across
  GitHub/Forgejo/Linear. Cost: Symphony must model every supported operation.

### What the boundary protects

- **Confidentiality only.** Hide the token; execute whatever the agent asks within the token's full
  scope. Simpler, but leans entirely on credentials being narrowly minted.
- **Scope + confidentiality (chosen).** Hide the credential *and* constrain each operation to the
  current run's (repo, issue, branch): push only to the work branch, write only to the assigned issue,
  PR only to the configured base. Defends against a compromised agent, not merely a leaked token.

### How the agent reaches the broker

- **In-protocol tools** (Codex client-side tools, Claude Code MCP). Native per agent, but reintroduces
  per-agent protocol coupling — working against multi-agent support (0006).
- **CLI over a per-run socket (chosen).** Brokered ops are plain CLI commands on `PATH`, reached over
  a per-run socket; identical for any agent. The socket's per-run identity is what makes scoped
  authorization enforceable (mechanics in 0004). This retires the in-protocol `linear_graphql` tool.

### How privileged Symphony obtains secrets (point 7)

Symphony MAY consume standard git/gh credential mechanisms (including environment variables) and reads
tracker HTTP auth from the operator policy config, but MUST scrub every secret-bearing environment
variable before forking the agent sandbox. Secrets resolve through a provider interface with a
required file provider; `$VAR` indirection survives only for non-secret path values. The rule that
matters: **no secret ever crosses into the agent sandbox** — not via the environment, not via the
broker.

## Decision and reasoning

Symphony becomes a privileged broker. The agent supplies operation content and requests every side
effect through a semantic `symphony` CLI over a per-run socket; Symphony executes with credentials the
agent never sees and enforces per-run scope on each call. Brokered-operation results are structured (a
machine-readable status plus a reason code) so the agent can adapt to ordinary failures; a
`scope_denied` result is treated as a policy violation and fails the run rather than letting the agent
probe the boundary (the full failure taxonomy is owned by 0007).

The chief residual risk we accept and flag for downstream decisions: because the agent works in a
bind-mounted working tree it shares with Symphony (0004), it can read and locally rewrite `.git`
config and refs. The broker therefore MUST derive and pin the pushed ref itself (the deterministic
work branch, 0007) and never trust agent-side ref state when performing a network operation.

We would reconsider the semantic-CLI granularity if the verb surface needed to model real workflows
grows unmanageable; the fallback is the hybrid model — keep the semantic CLI for trackers/PRs while
admitting a scoped git proxy.
