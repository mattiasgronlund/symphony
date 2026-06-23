# Background — 0005 Config and trust split

## Context

The current spec keeps everything in `WORKFLOW.md`, including secrets via `$VAR`, and declares hooks
"fully trusted configuration" (Section 15.4). Once `WORKFLOW.md` is genuinely repo-owned and the agent
is sandboxed and credential-less (0003, 0004), that single trusted config file is untenable: anyone
who can commit to the repo — including the agent — can edit it, so it cannot also hold credentials,
scope rules, or the sandbox profile.

## Options considered

### The dividing principle

- **Split by file only, both still trusted.** Keeps today's model; leans entirely on repo access
  control (branch protection) for credential isolation.
- **Repo proposes, policy caps.** Flexible per-repo, but security-relevant keys in untrusted
  `WORKFLOW.md` need validation and capping logic.
- **In-sandbox-only rule (chosen).** `WORKFLOW.md` contains only settings actually used *inside* the
  sandbox (the per-issue prompt and in-sandbox build/test hooks); everything privileged — credentials,
  scope rules, sandbox profile, repo map, the workflow state-machine, agent selection, and privileged
  setup hooks — lives in operator-owned policy config the repo/agent cannot modify. The sandbox
  boundary (0004) *is* the trust boundary, which makes classification mechanical: if Symphony uses a
  setting outside the sandbox, it is policy config.

### Hooks

The in-sandbox rule resolves hooks directly: privileged setup (clone/fetch/bootstrap needing
credentials or host access) is policy-owned and runs outside the sandbox; build/test hooks stay in
`WORKFLOW.md` and run inside the sandbox without credentials.

### Reload

- **Restart for policy / additive-only / hot-reload both.** Chosen: **hot-reload both**, keeping
  `WORKFLOW.md`'s existing watch/reload (Section 6.2 "Dynamic Reload Semantics") and extending it to
  policy config, with the same last-known-good-on-invalid safety.

## Decision and reasoning

Two configuration surfaces split on the sandbox boundary. `WORKFLOW.md` (repo-owned, untrusted,
in-sandbox-only) holds the prompt and in-sandbox hooks. Policy config (operator-owned, privileged)
holds everything Symphony uses outside the sandbox. Both hot-reload.

We accept and flag the cost of hot-reloading the policy config: live changes to credentials, scope, or
the state-machine during active runs introduce races and an audit surface, and the security anchor now
changes without a restart gate. The mitigation (invalid reload keeps last-known-good; changes apply to
future operations) is inherited from Section 6.2 and must be extended to policy config carefully. A
second consequence to watch: moving the workflow state-machine into policy (0008) takes process
control away from repo authors — intended, but a shift teams will feel.
