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

## Re-evaluation — Superseded by 0029 (2026-06-28)

This decision is **Superseded by 0029** (the `Superseded` state per 0033). 0029 replaces this
decision's central organizing principle — its config/trust axis — so 0029, not this decision, is the
current model. Per the `Superseded` semantics, parts of this decision survive inside its successor:
the agent (which can write the worktree and commit) still must not be able to edit trust-sensitive
configuration; `WORKFLOW.md` stays repo-owned, untrusted, and in-sandbox-only (prompt + in-sandbox
build/test hooks); both surfaces still hot-reload last-known-good; and credential isolation is
untouched. Those rules are now expressed within 0029's framing rather than this decision's.

Decision 0029 changes **one facet**: where the Way of Working lives. 0005 placed the workflow
state-machine and host-side hooks in *operator-owned* policy config, reasoning that operator-ownership
was the only way to keep them out of the agent's reach. 0029 shows a second way — **source by trust**:
host-side-executed WoW is read from the protected **base revision** (which the agent cannot push to,
per the scope invariant, and which is review-gated), and in-sandbox parts from the **worktree**. So
the WoW moves into a *repo-owned* `repo.policy.toml` without becoming agent-tamperable, and the
trust axis this decision framed as "operator-located vs. sandbox-located" is reframed as
"**base-sourced vs. worktree-sourced**."

What 0029 overturns: the claim that the workflow state-machine, transitions, and host-side hooks must
live in *operator*-owned config — under 0029 they are repo-owned and base-sourced, and the operator
config shrinks to outward credentials, the sandbox profile, and a repo→policy pointer. What survives
(carried into 0029): the rules listed above. Because 0029 reframes this decision's load-bearing trust
axis rather than merely refining a detail, this decision is marked `Superseded`, not left Accepted;
see decision 0029 for the current model.
