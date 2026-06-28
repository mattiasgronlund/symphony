# Plan — 0029 Repo-owned WoW config, trust sourcing, and the secret/integrity taxonomy

## Scope

Affected anchors in `SPEC.md`:

- Section 5 config model and the config/trust split (decision 0005) — introduce `repo.policy.toml` as
  the repo-owned WoW surface and shrink the operator-owned policy config.
- Section 9.6 "Agent Sandbox and Execution Isolation" and Section 15.4 "Hook Script Safety" — the
  **base-vs-worktree sourcing** rule for host-side vs in-sandbox config.
- Section 15.3 (secret provider) — the **outward-credential vs repo-internal-integrity-value**
  taxonomy.
- Section 9.7 `vcs.base_branch` — base resolution stays config, now expressed inside
  `repo.policy.toml`.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Introduce `repo.policy.toml`.** Ensure the spec defines a repo-owned WoW file holding engine
   selection, `scope.branch_pattern`, the policy edges/hooks (decision 0030), `[tasks]` (decision
   0031), and `tracker.transitions` (decision 0017), with `vcsx.toml` merged in (decision 0028). Done
   when the file and its sections are defined as repo-owned.

2. **Base-vs-worktree sourcing.** Ensure the spec states that Symphony reads **host-side-executed**
   WoW (engine selection, host-side hooks, the operation flow, branch-name pattern) from the resolved
   **base revision**, and **in-sandbox** parts (the `before:commit` gate/scan) from the **worktree**.
   Done when the sourcing rule is stated for each class and justified by the scope invariant +
   branch protection (WoW-trust = base-branch trust).

3. **Shrink the operator config.** Ensure operator-owned config holds only `[secrets]` (outward
   credentials), `[sandbox]`, and a repo→`repo.policy.toml` pointer — no WoW. Done when the operator
   surface no longer contains the workflow state-machine or hooks.

4. **Scope invariant stays built-in.** Ensure the work-branch-only / assigned-issue-only scope
   invariant remains broker-core behavior, enforced regardless of any config (only the branch-*name*
   pattern is repo config). Done when scope enforcement is described as built-in, not configurable.

5. **Secret vs integrity-value taxonomy.** Ensure Section 15.3 distinguishes **outward credentials**
   (broker-mediated; the isolation invariant) from **repo-internal integrity values** (repo-owned
   host-side hook environment; not broker-mediated), and reclassifies the gate-cache HMAC as the
   latter. Done when the two classes are defined and the HMAC is an integrity value, with the
   no-secret-in-sandbox invariant cited as preserved.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** restructure the config surfaces into `repo.policy.toml` (repo-owned)
  vs operator config (credentials/sandbox/pointer), and note base-vs-worktree sourcing.
- **Section 17 (test matrix):** add cases — an agent worktree edit to a host-side hook does not change
  the host-side behavior (it is read from base); an in-sandbox `before:commit` change *is* honored;
  the gate-cache HMAC never enters the sandbox.
- **Section 18 (checklist):** note the operator-config-needs-no-WoW property.

## Anchor changes

New tokens/terms: `repo.policy.toml`, **base-sourced** / **worktree-sourced**, **integrity value**
(vs **outward credential**). Supersedes decision 0005 (now `Superseded by 0029`; extend its
`Background.md` append-only). Refines decisions 0023 and 0026. Depends on decision 0027.

## Status

Accepted; `SPEC.md` application not started. Dependency 0027 is Accepted. The re-evaluations are
recorded: decision 0005 moves to `Superseded by 0029` with an append-only `Background.md` note (0029
reframes its trust axis; its `WORKFLOW.md`/in-sandbox model and credential isolation carry forward),
and decisions 0023 and 0026 are annotated for the secret/integrity-taxonomy and trust-classification
refinements respectively. `SPEC.md` application is deferred and batched with
the companion `vcsx` spec (0028) and decisions 0030–0031, since `repo.policy.toml` houses their
surfaces (policy edges, `[tasks]`, `tracker.transitions`).
