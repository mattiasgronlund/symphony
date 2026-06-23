# Background — 0007 VCS abstraction and git automation

## Context

Points 2, 3, 5: Symphony owns VCS remote operations (fetch, push, back-merge) and pull-request
creation across at least GitHub and Forgejo, while the agent supplies input. Within the broker
boundary (0003) and the shared-tree execution model (0004), this decision fixes the git division of
labor, the branch and PR model, and the VCS adapter.

## Options considered

### Git division of labor

- **Symphony owns all git / agent owns clone too / agent does local git, Symphony does network
  (chosen, refined).** The agent uses normal local git **including `git commit`**; Symphony performs
  everything touching the remote (clone/fetch/branch/back-merge/push/PR). The agent's high-value
  contributions are commit/PR *messages* and *conflict resolution*.

### Back-merge and conflicts

Back-merge is attempted at **run start** but **postponed if it would not apply cleanly** (the agent is
not interrupted up front); conflict resolution is required only **on push-reject** (non-fast-forward),
handed off via Symphony-stages → agent-resolves → Symphony-completes. Lazy integration keeps the agent
on its primary task and defers merge work to the moment it actually blocks integration.

### Work-branch identity

- **Tracker-provided / agent-proposed-then-validated / Symphony-derived deterministic (chosen).**
  Symphony computes the branch from issue identity via a policy template (`symphony/<identifier>`); the
  tracker `branch_name` is at most a hint. A deterministic, agent-independent branch is what makes
  "push only to the work branch" enforceable.

### PR lifecycle

- **One PR per issue, updated (chosen).** Created on first push, updated (new commits, refreshed body)
  on later runs, and reused across retries/continuations — matching one-issue-one-repo (0009).

### Identity and authorship

- **Configurable per repo (chosen).** Policy maps commit author/committer and the push/PR actor per
  repo (attribute to the agent, impersonate a service user, etc.).

### Failure semantics

Brokered git/PR ops return structured results with reason codes (`non_fast_forward`, `pr_conflict`,
`scope_denied`, ...); ordinary failures are returned for the agent to adapt to; `scope_denied` is
run-fatal (0003).

## Decision and reasoning

A VCS adapter (GitHub, Forgejo) backs the broker's git and PR verbs. The agent commits locally;
Symphony fetches/branches/back-merges/pushes and maintains one PR per issue. Conflict resolution is
lazy, triggered at push-reject. Authorship is configurable per repo.

Problems to watch: if author equals actor equals the same bot under branch protection,
self-approval/self-merge must be structurally prevented — the configurable mapping must make a distinct
approver possible; postponing back-merge until push can produce large late conflicts on fast-moving
bases; and the shared-tree model means Symphony pins the pushed refspec and ignores agent-side ref
manipulation.
