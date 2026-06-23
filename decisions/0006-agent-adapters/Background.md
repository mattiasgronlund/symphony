# Background — 0006 Agent adapters (Codex, Claude Code)

## Context

The spec is Codex-app-server-specific: Section 10, the `codex` config block, and the
`<thread_id>-<turn_id>` session model all assume Codex. Point 1 requires support for at least Codex and
Claude Code. The CLI-only broker (0003) already decouples side effects from the agent protocol, so
what remains is generalizing the *runner* contract and the per-agent specifics (session lifecycle,
events, token accounting, approval/sandbox mapping).

## Options considered

### Normativity of the agent interface

- **Thin contract, mostly deferred.** Least to maintain, weakest cross-agent conformance/observability
  guarantees.
- **Codex-shaped, others conform.** Least rework, but bakes Codex assumptions into the supposedly
  neutral layer.
- **Neutral contract + adapters (chosen).** A neutral runner contract (start session, run turn, stream
  events, normalized token usage, capability advertisement) plus per-agent adapter sections, each
  deferring to its own protocol as source of truth. Section 10's Codex detail becomes the Codex
  adapter.

### Agent selection

- **One agent per instance / agent in `WORKFLOW.md` / agent in policy (chosen).** Agent selection
  involves model credentials and sandbox shape, so it is policy config, set per repo. Each repo has a
  default agent plus effort, overridable per issue via tracker tags/labels through an explicit policy
  mapping table (label → (agent, effort)); only mapped labels take effect.

### Effort

- **Neutral scale, adapter-mapped / neutral + native override / pass-through native (chosen).**
  `effort` carries the agent's native value directly. This couples a label's effort to a specific
  agent, which the explicit mapping table absorbs cleanly: each label maps to an (agent, effort) pair
  together, so a label that switches the agent also supplies that agent's native effort.

## Decision and reasoning

Define a neutral agent runner contract with per-agent adapters (Codex, Claude Code). Select the agent
in policy config: a per-repo default agent plus native effort, overridable per issue via an explicit
policy table mapping tracker labels to (agent, effort) pairs. Pass effort through as the agent's native
value.

Problems to watch: a prompt authored in `WORKFLOW.md` should avoid agent-specific assumptions, since
the agent can vary per issue; and pass-through effort means the policy table, not the spec, is where
"what effort values are valid" lives — each adapter must document its accepted values.
