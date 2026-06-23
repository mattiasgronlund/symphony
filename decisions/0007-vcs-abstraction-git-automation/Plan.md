# Plan — 0007 VCS abstraction and git automation

## Scope

Adds a VCS adapter and git-automation material; revises Workspace Management (Section 9) toward the
shared-store-plus-worktree model and host-side privileged git, and the worker flow (Sections 10, 16.5)
to reflect agent-local-commit plus Symphony-network-ops. Defines the broker CLI's git and PR verb
surface (the fixed neutral core plus extensions from 0003). Depends on 0003 (broker), 0004 (execution
model), and 0005 (policy config).

## Steps

1. Ensure a VCS adapter abstraction exists with at least GitHub and Forgejo, backing the broker's git
   and PR operations. Done when the adapter and its required operations are specified.
2. Ensure the git division of labor is stated: the agent does local git including `git commit`;
   Symphony performs clone/fetch/branch/back-merge/push/PR. Done when the worker flow (Section 16.5)
   and surrounding prose reflect it.
3. Ensure the work branch is Symphony-derived and deterministic via a policy template
   (`symphony/<identifier>`), with tracker `branch_name` as a non-authoritative hint. Done when branch
   derivation is specified and tied to push-scope enforcement.
4. Ensure back-merge is attempted at run start, postponed on non-clean apply, and that conflict
   resolution is required only on push-reject via a Symphony-stages / agent-resolves handoff. Done
   when the back-merge trigger and conflict handoff are specified.
5. Ensure the PR model is one-per-issue, created then updated and reused across runs. Done when the PR
   lifecycle is specified.
6. Ensure commit author/committer and push/PR actor are configurable per repo in policy, and that the
   broker git/PR verb set and its structured failure reason codes (`non_fast_forward`, `pr_conflict`,
   `scope_denied`) are defined. Done when authorship config and the verb/result contract appear.

## Cross-cutting sync

Workspace section (9): shared-store-plus-worktree provisioning and host-side privileged git. Config
cheat sheet (6.4): VCS and repo keys in policy config. Test matrix (17) and checklist (18): VCS-adapter,
git-automation, back-merge/conflict, and PR-lifecycle rows.

## Anchor changes

- Section 9.3 "OPTIONAL Workspace Population (Implementation-Defined)" — superseded for VCS by
  first-class Symphony-owned clone/fetch/worktree provisioning.
- New anchors: the VCS adapter, the work-branch template `symphony/<identifier>`, `back-merge` and
  `request-merge` (CLI verbs), the `non_fast_forward` and `pr_conflict` reason codes, and the
  one-PR-per-issue model.

## Status

Not started. Recorded as `Proposed`; `SPEC.md` not yet edited.
