# Background — 0009 Multi-repo and shared polling

## Context

Points 11, 12: one Symphony instance should manage multiple VCS repositories, and multiple repos under
a single issue tracker should share that tracker's polling to avoid redundant background work. The
current spec implicitly assumes a single repo/tracker configuration.

## Options considered

### Issue → repo routing

- **Convention from issue metadata / one-tracker-one-repo / explicit mapping in policy (chosen,
  refined).** Operator policy config maps tracker scopes to repos, and the mapping is
  **tracker-implementation specific** — for example Linear project/team/label/assignee → repo, and
  Forgejo repo/tags/open-closed → repo. Predictable and auditable; the mapping vocabulary differs per
  tracker adapter.

### Cardinality

- **One issue → one repo (chosen, hard boundary).** Each dispatched run targets exactly one
  repo/workspace; cross-repo changes are separate issues. Keeps the workspace, branch, PR, and scope
  identity simple.

### Polling

Shared per-tracker polling: Symphony polls each tracker once and routes results to repos via the
mapping, rather than polling per repo — directly serving point 12's goal of minimizing background
polling.

## Decision and reasoning

One instance manages many repos. Issues are routed to repos by explicit, tracker-specific mappings in
policy config; one issue maps to exactly one repo. Polling is shared per tracker.

Problems to watch: per-tracker mapping vocabularies differ, so the policy schema must be defined per
tracker adapter rather than once; and shared polling plus per-(repo, issue) workspaces means
concurrency limits, the object store, and worktrees are now keyed by repo as well as issue (depends on
0007's provisioning model).
