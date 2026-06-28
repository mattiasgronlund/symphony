# Background — 0029 Repo-owned WoW config, trust sourcing, and the secret/integrity taxonomy

## Context

Decision 0005 placed the workflow state-machine in the **operator-owned** policy config because it is
trust-sensitive and the sandboxed agent must not be able to change it. That works, but it forces an
operator to understand a repository's Way of Working in order to configure Symphony. We want the
opposite separation of concerns: the **repository** owns its WoW (engine selection, hooks, the
operation flow, transitions), so configuring Symphony needs **no** WoW knowledge — while still
preventing a sandboxed agent from escalating by editing the WoW.

Two related issues:

- **The agent-tamper problem.** If the WoW lives in the repo, the agent (which can write the worktree
  and *commit*) could rewrite a host-side hook to run arbitrary code under the operator's credentials.
- **A mis-classified secret.** The gate-cache HMAC was modeled as a broker secret. It is not an
  outward credential — per decision 0026's own reasoning the gate-cache is not an enforcement
  boundary; the HMAC only makes it marginally harder to forge a "passed the gate" record. Treating it
  as an isolation-invariant secret over-couples the broker core.

## Options considered

- **Option A — Mark the repo policy file "not editable" / block it in the sandbox.** Trade-offs:
  stops the agent editing the worktree copy, but **not** the agent *committing* a malicious WoW change
  that Symphony would then read. Necessary but insufficient. Rejected as the sole mechanism.

- **Option B — Source by trust: base revision vs. worktree (chosen).** Symphony reads the
  **host-side-executed** WoW (engine selection, host-side hooks, the policy/flow, the branch-name
  pattern) from the protected **base revision** — which the agent cannot push to (the scope
  invariant) and which is review-gated by branch protection. It reads the **in-sandbox** parts (the
  `before:commit` gate/scan) from the **worktree**, where agent edits are harmless (they only affect
  the sandbox) and correctly run a PR's own gate change. The result: **WoW-config trust equals
  base-branch trust** — the level the repo already trusts — with no new immutability mechanism. The
  operator config shrinks to outward credentials, the sandbox profile, and a repo→policy pointer; the
  scope *invariant* (work-branch-only, assigned-issue-only) stays a broker-core built-in.

The secret/integrity taxonomy is decided alongside: the broker secret store holds **only outward
credentials** (the isolation invariant — VCS/forge/tracker tokens). **Repo-internal integrity
values** (the gate-cache HMAC) are repo-owned, supplied to a host-side hook's environment, and are
**not** broker-mediated.

## Decision and reasoning

Choose **Option B** plus the taxonomy. The repository owns the WoW in one file (`repo.policy.toml`,
into which `vcsx.toml` is merged per decision 0028); Symphony reads host-side-executed parts from the
base revision and in-sandbox parts from the worktree. This **supersedes decision 0005**: its trust
axis is no longer "operator-located vs. sandbox-located" but **"base-sourced vs. worktree-sourced,"**
and the repo — not the operator — owns the WoW (0005's `WORKFLOW.md`/in-sandbox model and credential
isolation are carried forward). It refines decision 0023 / Section 15.3 (the secret model now
distinguishes outward credentials from repo-internal integrity values) and decision 0026 (the
`after_push` "declared secret" is reclassified; the host-side/in-sandbox hook classification now also
determines base-vs-worktree sourcing).

We would reconsider if a repository legitimately needs host-side WoW that does not live on the base
branch (e.g. a per-run computed policy), which the base-sourcing rule would not accommodate.

The decision is **Accepted** (dependency 0027 is Accepted); the corresponding `SPEC.md` change is
**not** made yet — application is deferred (see `Plan.md` Status). Supersedes 0005 (now `Superseded by
0029`); refines 0023 and 0026.
