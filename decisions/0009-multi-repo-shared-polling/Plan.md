# Plan — 0009 Multi-repo and shared polling

## Scope

Generalizes the orchestrator, workspace layout, and configuration from single-repo to multi-repo; adds
shared per-tracker polling and the issue→repo mapping. Touches Polling/Scheduling (Section 8), Workspace
Management (Section 9), and the config model (Sections 5–6). Depends on the VCS adapter (0007) and the
tracker adapter (0008).

## Steps

1. Ensure policy config can enumerate multiple repos in one instance, each with its own VCS, agent, and
   policy settings. Done when multi-repo policy config is specified.
2. Ensure an explicit, tracker-implementation-specific issue→repo mapping routes each issue to exactly
   one repo (Linear project/team/label/assignee → repo; Forgejo repo/tags/state → repo). Done when the
   mapping schema is specified per tracker adapter and one-issue-one-repo is stated as a boundary.
3. Ensure polling is shared per tracker (poll once, route to repos) rather than per repo. Done when the
   poll loop (Section 8) describes shared polling and routing.
4. Ensure workspace identity, concurrency limits, and the object store/worktrees are keyed by
   (repo, issue). Done when the Section 9 layout and the Section 8.3 concurrency control reflect
   repo-qualified keys.

## Cross-cutting sync

Config cheat sheet (6.4): multi-repo and mapping keys. Test matrix (17) and checklist (18): routing,
shared-polling, and repo-qualified concurrency/workspace rows.

## Anchor changes

- Per-issue workspace path `<workspace.root>/<sanitized_issue_identifier>` (Section 9.1) —
  repo-qualified to include the repo in the key.
- New anchors: the issue→repo mapping (per tracker adapter), shared per-tracker polling, and multi-repo
  policy config.

## Status

Not started. Recorded as `Proposed`; `SPEC.md` not yet edited.
